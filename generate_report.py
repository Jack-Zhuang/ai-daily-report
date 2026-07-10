#!/usr/bin/env python3
"""
AI推荐日报 - 日报生成脚本
生成移动端优化的HTML日报，包含顶会论文和多来源内容
"""

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import sys
from jinja2 import Environment, FileSystemLoader, select_autoescape

class ReportGenerator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.environ.get("BASE_DIR", str(Path(__file__).parent))
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "daily_data"
        self.archive_dir = self.base_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)
        
        self.today = os.environ.get("REPORT_DATE", datetime.now().strftime("%Y-%m-%d"))
        
        # 检查今日数据是否存在，如果不存在则使用昨天的
        data_file = self.data_dir / f"{self.today}.json"
        if not data_file.exists():
            from datetime import timedelta
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            data_file_yesterday = self.data_dir / f"{yesterday}.json"
            if data_file_yesterday.exists():
                self.today = yesterday
                print(f"⚠️ 使用前一天的数据: {yesterday}")
    
    def load_today_data(self) -> dict:
        """加载今日数据"""
        file_path = self.data_dir / f"{self.today}.json"
        print(f"📂 加载数据: {file_path}")
        if not file_path.exists():
            print(f"❌ 未找到今日数据: {file_path}")
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _ensure_daily_pick_summaries(self, daily_pick: list, data: dict):
        """从已有数据同步摘要到每日精选（LLM生成已在step2完成，此处不调API）"""
        # 建立映射
        arxiv_map = {p.get('arxiv_id', p.get('id', '')): p for p in data.get('arxiv_papers', []) if p.get('cn_summary')}
        github_map = {p.get('name', ''): p for p in data.get('github_projects', []) if p.get('cn_description')}
        article_map = {a.get('id', ''): a for a in data.get('articles', data.get('hot_articles', [])) if a.get('cn_summary')}
        
        for item in daily_pick:
            if item.get('cn_summary') and len(item['cn_summary']) > 30:
                continue  # 已有摘要且质量不错，跳过
            
            arxiv_id = item.get('arxiv_id', item.get('id', ''))
            if arxiv_id in arxiv_map:
                item['cn_summary'] = arxiv_map[arxiv_id].get('cn_summary', '')
                print(f"  ✅ 同步论文摘要: {str(item.get('title',''))[:30]}")
                continue
            
            name = item.get('name', '')
            if name in github_map:
                item['cn_summary'] = github_map[name].get('cn_description', '')
                print(f"  ✅ 同步GitHub简介: {str(name)[:30]}")
                continue
            
            item_id = item.get('id', '')
            if item_id in article_map:
                item['cn_summary'] = article_map[item_id].get('cn_summary', '')
                print(f"  ✅ 同步文章摘要: {str(item.get('title',''))[:30]}")
                continue
    
    def get_conference_papers(self, data: dict) -> dict:
        """获取顶会论文数据（从all_conferences.json加载，按技术分类）"""
        import os
        all_conf_file = self.base_dir / "conference_papers" / "all_conferences.json"
        if all_conf_file.exists():
            try:
                with open(all_conf_file, "r", encoding="utf-8") as f:
                    conf_data = json.load(f)
                conferences = conf_data.get('conferences', {})
                # 检查是否有解读文件
                insights_dir = self.base_dir / "docs" / "insights"
                existing_insights = set()
                if insights_dir.exists():
                    existing_insights = {f for f in os.listdir(str(insights_dir)) if f.endswith('.html')}
                
                result = {}
                for conf_name, papers in conferences.items():
                    if not isinstance(papers, list):
                        continue
                    # 给每个论文检查是否有解读
                    has_any_insight = 0
                    for p in papers:
                        pid = str(p.get('arxiv_id', p.get('id', '')))
                        pid_clean = pid.replace('.', '_')
                        p['has_insight'] = any(pid_clean in ef for ef in existing_insights)
                        if p['has_insight']:
                            has_any_insight += 1
                            # 设置解读URL（使用实际的insight文件名）
                            for ef in existing_insights:
                                if pid_clean in ef:
                                    p['insight_url'] = f'insights/{ef}'
                                    break
                    
                    result[conf_name] = {
                        "name": conf_name,
                        "papers": papers,
                        "total": len(papers),
                        "has_insight_count": has_any_insight
                    }
                if result:
                    print(f"📚 从 all_conferences.json 加载顶会论文，共 {len(result)} 个会议，{sum(r['has_insight_count'] for r in result.values())} 篇有解读")
                    return result
            except Exception as e:
                print(f"⚠️ 加载 all_conferences.json 失败: {e}")
        
        # 备用数据（当all_conferences.json不可用时）
        if 'conference_papers' in data and data['conference_papers']:
            return data['conference_papers']
        return {}
    
    def generate_html(self, data: dict) -> str:
        """生成HTML日报"""
        
        # 获取日期
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # ========== 强约束验证 ==========
        # 1. 每日精选必须是5项，顺序为：3文章+1论文+1GitHub
        daily_pick = data.get('daily_pick', [])
        
        # 过滤每日精选中的广告
        daily_pick = self._filter_daily_pick_ads(daily_pick)
        
        # 如果过滤后不足5项，从热门文章中补充
        if len(daily_pick) < 5:
            print(f"\n📌 补充每日精选（当前{len(daily_pick)}项，需要5项）...")
            hot_articles = data.get('articles', data.get('hot_articles', []))
            daily_pick = self._supplement_daily_pick(daily_pick, hot_articles, data)
        
        # 验证每日精选中的论文是否有解读（使用论文发布日期）
        insights_dir = self.base_dir / "docs" / "insights"
        for i, item in enumerate(daily_pick):
            if item.get('type') == 'paper' or item.get('pick_type') == 'paper':
                paper_id = str(item.get('id', item.get('arxiv_id', ''))).replace('.', '_')
                # 使用论文发布日期查找解读文件
                paper_date = item.get('published', item.get('date', date))
                if paper_date and len(str(paper_date)) >= 10:
                    paper_date_str = str(paper_date)[:10]
                else:
                    paper_date_str = date
                insight_file = insights_dir / f"{paper_date_str}_{paper_id}.html"
                if not insight_file.exists():
                    print(f"⚠️ 每日精选第{i+1}项论文缺少解读: {item.get('title', '')[:30]}")
        
        if len(daily_pick) != 5:
            print(f"⚠️ 每日精选数量错误: {len(daily_pick)}项，应为5项")
        
        # 2. GitHub Trending必须是5项，按增长排序，排除近期已发布的
        github_projects = data.get('github_projects', data.get('github_trending', []))

        # 检查是否有增长数据
        has_growth_data = any(p.get('growth_rate', 0) > 0 for p in github_projects)
        
        if has_growth_data:
            # 按 growth_rate 降序排序（增长最快的在前）
            github_projects = sorted(github_projects, key=lambda x: x.get('growth_rate', 0), reverse=True)
            print(f"📊 GitHub项目按增长排序完成")
        else:
            # 没有增长数据时，按 stars 排序
            github_projects = sorted(github_projects, key=lambda x: x.get('stars', 0), reverse=True)
            print(f"📊 GitHub项目按 Stars 排序完成（无增长数据）")

        # 加载历史记录，排除近期已发布的项目（排除今天已发布的）
        history_file = self.base_dir / "history" / "published.json"
        published_github = set()
        if history_file.exists():
            try:
                history = json.loads(history_file.read_text(encoding='utf-8'))
                # 只排除今天之前发布的项目
                for pid, pub_date in history.get('github_projects', {}).items():
                    if pub_date != date:  # 不排除今天发布的
                        published_github.add(pid)
                print(f"📚 历史已发布GitHub项目（不含今天）: {len(published_github)} 个")
            except:
                pass

        # 过滤已发布的项目
        original_count = len(github_projects)
        github_projects = [p for p in github_projects if str(p.get('id', p.get('name', ''))) not in published_github]
        if len(github_projects) < original_count:
            print(f"✅ 过滤已发布GitHub项目: {original_count} -> {len(github_projects)}")

        # 过滤掉没有增长的项目（高星但不活跃的旧项目）
        # 注意：如果数据来自 API 搜索（非 Trending 页面），可能没有 growth 数据，此时保留有 star 的项目
        has_growth_data = any(p.get('growth', 0) > 0 or p.get('growth_rate', 0) > 0 for p in github_projects)
        if has_growth_data:
            active_projects = [p for p in github_projects if p.get('growth', 0) > 0 or p.get('growth_rate', 0) > 0]
            if len(active_projects) < len(github_projects):
                print(f"📊 过滤零增长项目: {len(github_projects)} -> {len(active_projects)}")
                github_projects = active_projects
        else:
            # 无增长数据时（如 API 搜索获取），保留按 stars 排序的项目
            print(f"📊 无增长数据，保留按 Stars 排序的 {len(github_projects)} 个项目")
        
        if len(github_projects) > 3:
            github_projects = github_projects[:3]
            print(f"⚠️ GitHub项目截取为3项")

        # 记录今天发布的项目
        if github_projects:
            self._update_github_history(github_projects, history_file)
        
        # 3. arXiv论文：只展示有解读文件的论文
        insights_dir = self.base_dir / "docs" / "insights"
        arxiv_papers = data.get('arxiv_papers', [])
        
        # 检查每篇论文是否有解读文件（使用论文发布日期）
        for paper in arxiv_papers:
            paper_id = str(paper.get('id', paper.get('arxiv_id', ''))).replace('.', '_')
            # 使用论文发布日期查找解读文件
            paper_date = paper.get('published', paper.get('date', date))
            if paper_date and len(str(paper_date)) >= 10:
                paper_date_str = str(paper_date)[:10]
            else:
                paper_date_str = date
            
            insight_file = insights_dir / f"{paper_date_str}_{paper_id}.html"
            if insight_file.exists():
                paper['has_insight'] = True
            elif paper.get('has_insight'):
                pass  # 保持 True
            else:
                paper['has_insight'] = False
        
        # 展示论文：优先有解读的，其次有中文摘要的，最多5篇
        # 有解读的论文排在前面
        papers_with_insight = [p for p in arxiv_papers if p.get('has_insight')]
        papers_with_summary = [p for p in arxiv_papers if not p.get('has_insight') and p.get('cn_summary') and len(p.get('cn_summary', '')) > 50]
        
        arxiv_papers = (papers_with_insight + papers_with_summary)[:5]
        
        papers_with_insight_count = len(papers_with_insight)
        print(f"📖 arXiv论文: 有解读 {papers_with_insight_count} 篇，有摘要 {len(papers_with_summary)} 篇（展示 {len(arxiv_papers)} 篇）")
        
        # 4. 热门文章去重（移除与每日精选重复的）
        pick_titles = set()
        for item in daily_pick:
            title = item.get('cn_title', item.get('title', item.get('name', '')))
            pick_titles.add(title)
        
        # 使用 articles 字段（30篇），而不是 hot_articles
        hot_articles = data.get('articles', data.get('hot_articles', []))
        hot_articles = [item for item in hot_articles if item.get('cn_title', item.get('title', '')) not in pick_titles]
        
        # 智能分类和过滤文章
        hot_articles = self.classify_and_filter_articles(hot_articles)
        
        # 5. 安全网：对摘要质量差的内容即时用LLM补充
        self._ensure_daily_pick_summaries(daily_pick, data)
        
        # 6. 添加封面图
        self.add_cover_images(daily_pick, hot_articles, github_projects, arxiv_papers)
        
        # ========== 生成JavaScript数据 ==========
        daily_pick_json = json.dumps(daily_pick, ensure_ascii=False)
        hot_articles_json = json.dumps(hot_articles, ensure_ascii=False)
        github_projects_json = json.dumps(github_projects, ensure_ascii=False)
        arxiv_papers_json = json.dumps(arxiv_papers, ensure_ascii=False)
        conference_data = self.get_conference_papers(data)
        conference_json = json.dumps(conference_data, ensure_ascii=False)
        
        # 统计数据
        total_papers = len(data.get('arxiv_papers', []))
        total_projects = len(data.get('github_projects', []))
        total_articles = len(data.get('articles', data.get('hot_articles', [])))
        total_conference = sum(c.get('total', 0) for c in conference_data.values())
        
        # 构建模板上下文
        context = {
            'date': data['date'],
            'total_papers': total_papers,
            'total_projects': total_projects,
            'total_articles': total_articles,
            'total_conference': total_conference,
            'daily_pick_count': len(data.get('daily_pick', [])),
            'daily_pick_json': daily_pick_json,
            'hot_articles_json': hot_articles_json,
            'github_projects_json': github_projects_json,
            'arxiv_papers_json': arxiv_papers_json,
            'conference_json': conference_json,
        }
        
        # 使用 Jinja2 模板渲染
        html = self._render_template(context)
        
        return html
    
    def _render_template(self, context: dict) -> str:
        """使用 Jinja2 渲染 HTML 模板"""
        env = Environment(
            loader=FileSystemLoader(self.base_dir / 'templates'),
            autoescape=select_autoescape(['html'])
        )
        template = env.get_template('default/base.html')
        return template.render(**context)
    
    def classify_and_filter_articles(self, articles: list) -> list:
        """智能分类和过滤文章"""
        # 广告关键词（标题中出现直接过滤）
        ad_keywords_title = ["招聘", "内推", "求职", "简历", "面试", "课程", "培训", "报名",
                             "优惠", "促销", "购买", "订阅", "会员", "付费", "广告", "限时",
                             "免费领取", "扫码", "关注公众号", "实习", "校招", "社招", 
                             "急聘", "诚聘", "高薪", "待遇", "薪资", "福利"]
        
        # 广告关键词（摘要中出现需要综合判断）
        ad_keywords_content = ["投递简历", "发送简历", "联系邮箱", "应聘", "岗位要求",
                               "岗位职责", "工作地点", "薪资范围", "福利待遇"]
        
        # AI 相关关键词
        ai_keywords = ["AI", "人工智能", "大模型", "LLM", "GPT", "Claude", "OpenAI", "DeepSeek",
                       "Agent", "智能体", "推荐系统", "机器学习", "深度学习", "神经网络",
                       "Transformer", "RAG", "多模态", "计算机视觉", "NLP", "自然语言",
                       "强化学习", "知识图谱", "向量数据库", "Embedding", "微调", "训练",
                       "推理", "模型", "算法", "论文", "arXiv", "GitHub", "开源",
                       "机器人", "自动化", "自动驾驶", "AIGC", "生成式", "ChatGPT",
                       "diffusion", "stable", "midjourney", "huggingface"]
        
        filtered = []
        ad_count = 0
        no_summary_count = 0
        for article in articles:
            title = article.get("title", "") or article.get("cn_title", "")
            summary = article.get("summary", "") or article.get("cn_summary", "")
            text = (title + " " + summary).lower()
            
            # 检查标题是否包含广告关键词
            is_ad = any(kw in title for kw in ad_keywords_title)
            if is_ad:
                ad_count += 1
                print(f"  🚫 过滤广告: {title[:40]}...")
                continue
            
            # 检查摘要是否包含多个广告关键词（可能是招聘启事）
            ad_keyword_count = sum(1 for kw in ad_keywords_content if kw in summary)
            if ad_keyword_count >= 3:
                ad_count += 1
                print(f"  🚫 过滤招聘启事: {title[:40]}...")
                continue
            
            # 检查中文摘要是否有效（LLM 拒绝/为空的内容不展示）
            cn_summary = article.get('cn_summary', '')
            if not cn_summary or len(cn_summary) < 30:
                no_summary_count += 1
                print(f"  🚫 过滤无摘要内容: {title[:40]}...")
                continue
            
            # 检查是否 AI 相关
            is_ai = any(kw.lower() in text for kw in ai_keywords)
            if not is_ai:
                continue
            
            # 分类（强制覆盖旧分类）
            if any(kw in text for kw in ["agent", "智能体", "多智能体", "autonomous", "自主"]):
                article["category"] = "agent"
            elif any(kw in text for kw in ["llm", "大模型", "gpt", "claude", "llama", 
                                            "transformer", "语言模型", "chat", "对话", "prompt", "rag"]):
                article["category"] = "llm"
            else:
                article["category"] = "rec"
            
            filtered.append(article)
        
        if ad_count > 0:
            print(f"📊 过滤了 {ad_count} 篇广告/招聘内容")
        if no_summary_count > 0:
            print(f"📊 过滤了 {no_summary_count} 篇无有效摘要的内容")
        
        return filtered
    
    def _filter_daily_pick_ads(self, daily_pick: list) -> list:
        """过滤每日精选中的广告内容"""
        # 广告关键词
        ad_keywords = ["招聘", "内推", "求职", "简历", "面试", "课程", "培训", "报名",
                       "优惠", "促销", "购买", "订阅", "会员", "付费", "广告", "限时",
                       "免费领取", "扫码", "关注公众号", "实习", "校招", "社招",
                       "急聘", "诚聘", "高薪", "待遇", "薪资", "福利"]
        
        filtered = []
        removed = []
        
        for item in daily_pick:
            title = item.get("title", "") or item.get("cn_title", "") or item.get("name", "")
            
            # 检查是否为广告
            is_ad = any(kw in title for kw in ad_keywords)
            if is_ad:
                removed.append(title[:40])
                continue
            
            filtered.append(item)
        
        if removed:
            print(f"\n🚫 从每日精选中移除广告内容:")
            for title in removed:
                print(f"   - {title}...")
            print(f"   ⚠️ 每日精选数量减少: {len(daily_pick)} -> {len(filtered)}")
        
        return filtered
    
    def _supplement_daily_pick(self, daily_pick: list, hot_articles: list, data: dict) -> list:
        """从热门文章中补充每日精选"""
        # 广告关键词
        ad_keywords = ["招聘", "内推", "求职", "简历", "面试", "课程", "培训", "报名",
                       "优惠", "促销", "购买", "订阅", "会员", "付费", "广告", "限时",
                       "免费领取", "扫码", "关注公众号", "实习", "校招", "社招"]
        
        # 获取已在每日精选中的标题
        pick_titles = set()
        for item in daily_pick:
            title = item.get("title", "") or item.get("cn_title", "") or item.get("name", "")
            pick_titles.add(title)
        
        # 统计当前类型数量
        article_count = sum(1 for item in daily_pick if item.get('pick_type') == 'article' or item.get('type') == 'article')
        paper_count = sum(1 for item in daily_pick if item.get('pick_type') == 'paper' or item.get('type') == 'paper')
        github_count = sum(1 for item in daily_pick if item.get('pick_type') == 'github' or item.get('type') == 'github')
        
        # 目标：3文章 + 1论文 + 1GitHub
        need_articles = max(0, 3 - article_count)
        need_papers = max(0, 1 - paper_count)
        need_githubs = max(0, 1 - github_count)
        
        print(f"   需要补充: {need_articles}篇文章 + {need_papers}篇论文 + {need_githubs}个GitHub项目")
        
        # 从热门文章中筛选
        for item in hot_articles:
            if len(daily_pick) >= 5:
                break
            
            title = item.get("title", "") or item.get("cn_title", "")
            
            # 跳过已在每日精选中的
            if title in pick_titles:
                continue
            
            # 跳过广告
            if any(kw in title for kw in ad_keywords):
                continue
            
            # 根据类型补充
            item_type = item.get('type', 'article')
            
            if item_type == 'article' and need_articles > 0:
                item['pick_type'] = 'article'
                daily_pick.append(item)
                pick_titles.add(title)
                need_articles -= 1
                print(f"   ✅ 补充文章: {title[:40]}...")
            
            elif item_type == 'paper' and need_papers > 0:
                item['pick_type'] = 'paper'
                daily_pick.append(item)
                pick_titles.add(title)
                need_papers -= 1
                print(f"   ✅ 补充论文: {title[:40]}...")
        
        # 如果还不够，从 arXiv 论文中补充
        if need_papers > 0:
            arxiv_papers = data.get('arxiv_papers', [])
            for item in arxiv_papers:
                if need_papers <= 0 or len(daily_pick) >= 5:
                    break
                title = item.get("title", "") or item.get("cn_title", "")
                if title not in pick_titles:
                    item['pick_type'] = 'paper'
                    daily_pick.append(item)
                    pick_titles.add(title)
                    need_papers -= 1
                    print(f"   ✅ 补充论文: {title[:40]}...")
        
        # 如果还不够，从 GitHub 项目中补充
        if need_githubs > 0:
            github_projects = data.get('github_projects', data.get('github_trending', []))
            for item in github_projects:
                if need_githubs <= 0 or len(daily_pick) >= 5:
                    break
                title = item.get("name", "")
                if title not in pick_titles:
                    item['pick_type'] = 'github'
                    daily_pick.append(item)
                    pick_titles.add(title)
                    need_githubs -= 1
                    print(f"   ✅ 补充GitHub: {title[:40]}...")
        
        # 重新排序：3文章 + 1论文 + 1GitHub
        daily_pick = self._reorder_daily_pick(daily_pick)
        
        print(f"   补充后每日精选: {len(daily_pick)}项")
        return daily_pick
    
    def _reorder_daily_pick(self, daily_pick: list) -> list:
        """重新排序每日精选，确保顺序为：3文章 + 1论文 + 1GitHub"""
        articles = []
        papers = []
        githubs = []
        seen_titles = set()
        
        for item in daily_pick:
            # 获取标题用于去重
            title = item.get('title', item.get('cn_title', item.get('name', '')))
            if title in seen_titles:
                continue
            seen_titles.add(title)
            
            # 获取类型
            item_type = item.get('pick_type') or item.get('type', 'article')
            
            if item_type == 'article':
                articles.append(item)
            elif item_type == 'paper':
                papers.append(item)
            elif item_type == 'github':
                githubs.append(item)
            else:
                # 默认当作文章
                articles.append(item)
        
        # 按顺序组合：3文章 + 1论文 + 1GitHub
        result = []
        result.extend(articles[:3])
        result.extend(papers[:1])
        result.extend(githubs[:1])
        
        # 如果不够5项，用剩余的文章填充
        remaining = 5 - len(result)
        if remaining > 0 and len(articles) > 3:
            for item in articles[3:]:
                if remaining <= 0:
                    break
                result.append(item)
                remaining -= 1
        
        return result[:5]
    
    def add_cover_images(self, daily_pick, articles, github_projects, arxiv_papers):
        """为内容添加封面图"""
        covers_dir = self.base_dir / "covers"
        # GitHub Pages 以 docs/ 为根，所以还检查 docs/covers/
        docs_covers_dir = self.base_dir / "docs" / "covers"
        
        # 收集所有封面图：优先 docs/covers/，其次 covers/
        cover_files = set()
        if docs_covers_dir.exists():
            cover_files.update(f.name for f in docs_covers_dir.glob("*.jpg"))
        if covers_dir.exists():
            cover_files.update(f.name for f in covers_dir.glob("*.jpg"))
        
        if not cover_files:
            return
        
        # 每日精选
        for i, item in enumerate(daily_pick):
            cover_name = f"article_{i+1}.jpg"
            if cover_name in cover_files:
                item["cover_image"] = f"covers/{cover_name}"
        
        # 热门文章
        for i, item in enumerate(articles):
            item_type = item.get("type", "article")
            cover_name = f"{item_type}_{i+1}.jpg"
            if cover_name in cover_files:
                item["cover_image"] = f"covers/{cover_name}"
        
        # GitHub 项目
        for i, item in enumerate(github_projects):
            cover_name = f"github_{i+1}.jpg"
            if cover_name in cover_files:
                item["cover_image"] = f"covers/{cover_name}"
        
        # arXiv 论文
        for i, item in enumerate(arxiv_papers):
            arxiv_id = item.get("arxiv_id", item.get("id", "")).replace("/", "_").replace(".", "_")
            cover_name = f"paper_{arxiv_id}.jpg"
            if cover_name in cover_files:
                item["cover_image"] = f"covers/{cover_name}"
    
    def save_to_archive(self, data: dict, html: str):
        """保存到归档"""
        archive_path = self.archive_dir / self.today
        archive_path.mkdir(exist_ok=True)
        
        # 保存HTML
        (archive_path / "index.html").write_text(html, encoding="utf-8")
        
        # 保存JSON数据
        (archive_path / "data.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        # 更新索引
        self._update_archive_index(data)
        
        print(f"📁 已归档: {archive_path}")
    
    def _update_archive_index(self, data: dict):
        """更新归档索引"""
        index_file = self.archive_dir / "index.json"
        
        if index_file.exists():
            index = json.loads(index_file.read_text(encoding="utf-8"))
        else:
            index = {"archives": [], "reports": []}
        
        # 确保 reports 字段存在
        if "reports" not in index:
            index["reports"] = []
        
        # 添加新条目
        index["reports"].insert(0, {
            "date": self.today,
            "total_papers": data.get("stats", {}).get("total_papers", 0),
            "total_projects": data.get("stats", {}).get("total_projects", 0),
            "total_articles": data.get("stats", {}).get("total_articles", 0)
        })
        
        # 保留最近90天
        index["reports"] = index["reports"][:90]
        
        index_file.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def run(self) -> str:
        """执行日报生成"""
        print(f"\n{'='*50}")
        print(f"📝 生成AI推荐日报 - {self.today}")
        print(f"{'='*50}\n")
        
        # 加载数据
        data = self.load_today_data()
        if not data:
            return None
        
        # 生成 LLM 摘要（如果需要）
        self._ensure_summaries(data)
        
        # 生成HTML
        html = self.generate_html(data)
        
        # 保存到归档
        self.save_to_archive(data, html)
        
        # 保存到主目录
        main_path = self.base_dir / "index.html"
        main_path.write_text(html, encoding="utf-8")
        
        # 同时保存到 docs 目录（GitHub Pages 需要）
        docs_path = self.base_dir / "docs" / "index.html"
        docs_path.parent.mkdir(exist_ok=True)
        docs_path.write_text(html, encoding="utf-8")
        
        print(f"\n{'='*50}")
        print(f"✅ 日报生成完成！")
        print(f"   📄 主文件: {main_path}")
        print(f"   📄 Docs文件: {docs_path}")
        print(f"   📁 归档: {self.archive_dir / self.today}")
        print(f"{'='*50}\n")
        
        return str(main_path)
    
    def _ensure_summaries(self, data: dict):
        """确保所有内容都有摘要，并同步到每日精选"""
        from llm_summarizer import sync_daily_pick_summaries, generate_all_summaries, needs_llm_summary
        
        # 检查是否需要生成摘要
        need_generate = False
        
        # 检查论文
        for paper in data.get('arxiv_papers', []):
            if needs_llm_summary(paper.get('cn_summary', ''), paper.get('summary', '')):
                need_generate = True
                break
        
        # 检查文章
        if not need_generate:
            for article in data.get('articles', data.get('hot_articles', [])):
                if needs_llm_summary(article.get('cn_summary', ''), article.get('summary', '')):
                    need_generate = True
                    break
        
        # 如果需要生成，调用 LLM 生成摘要
        if need_generate:
            print("\n" + "=" * 50)
            print("🤖 生成 LLM 摘要...")
            print("=" * 50)
            data_file = self.data_dir / f"{self.today}.json"
            generate_all_summaries(data_file, force=False)
            # 重新加载数据
            data.clear()
            data.update(json.loads(data_file.read_text(encoding='utf-8')))
        
        # 同步每日精选摘要（无论是否生成了新摘要都要同步）
        sync_daily_pick_summaries(data)
        
        # 保存更新后的数据
        data_file = self.data_dir / f"{self.today}.json"
        data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def _update_github_history(self, projects: list, history_file: Path):
        """更新 GitHub 项目发布历史"""
        history_file.parent.mkdir(exist_ok=True)
        
        try:
            if history_file.exists():
                history = json.loads(history_file.read_text(encoding='utf-8'))
            else:
                history = {'daily_pick': {}, 'hot_articles': {}, 'arxiv_papers': {}, 'github_projects': {}, 'conference_papers': {}}
            
            today = self.today
            for p in projects:
                project_id = str(p.get('id', p.get('name', '')))
                history['github_projects'][project_id] = today
            
            # 只保留最近30天的记录
            from datetime import datetime, timedelta
            cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            for key in list(history['github_projects'].keys()):
                if history['github_projects'][key] < cutoff:
                    del history['github_projects'][key]
            
            history_file.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"📝 已记录 {len(projects)} 个GitHub项目到历史")
        except Exception as e:
            print(f"⚠️ 更新历史记录失败: {e}")


if __name__ == "__main__":
    generator = ReportGenerator()
    html_path = generator.run()
    if html_path:
        print(f"日报已生成: {html_path}")
        
        # 复制辅助页面到 docs/（GitHub Pages 从 docs/ 服务）
        base_dir = Path(__file__).parent.parent
        docs_dir = base_dir / "docs"
        for page_file in ["articles.html", "papers.html"]:
            src = base_dir / page_file
            dst = docs_dir / page_file
            if src.exists():
                shutil.copy2(str(src), str(dst))
                print(f"  ✅ 复制 {page_file} 到 docs/")
        
        # 自动部署
        deploy_script = base_dir / "scripts" / "auto_deploy.sh"
        if deploy_script.exists():
            print("\n🚀 自动部署中...")
            subprocess.run(["bash", str(deploy_script)], cwd=str(base_dir))

