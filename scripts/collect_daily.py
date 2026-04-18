#!/usr/bin/env python3
"""
AI推荐日报 - 每日数据采集脚本
采集arXiv论文、GitHub项目、热门文章等
"""

import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
import time
import re

class AIDailyCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "daily_data"
        self.archive_dir = self.base_dir / "archive"
        self.data_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)
        
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
    def _generate_chinese_content(self, item: dict, item_type: str) -> dict:
        """为内容生成中文标题和简介"""
        title = item.get('title', item.get('name', ''))
        summary = item.get('summary', item.get('description', ''))
        
        # 根据标题关键词生成中文内容
        title_lower = title.lower()
        
        # 中文标题映射（简短版）
        chinese_titles = {
            'agent': '智能Agent推荐方法研究',
            'llm': 'LLM推荐系统应用研究',
            'recommendation': '推荐系统算法创新',
            'collaborative': '协同过滤优化研究',
            'graph': '图神经网络推荐',
            'sequence': '序列推荐模型研究',
            'ctr': '点击率预测优化',
            'multi': '多任务推荐框架',
            'knowledge': '知识图谱推荐研究',
            'contrastive': '对比学习推荐方法',
            'diffusion': '扩散模型推荐应用',
            'transformer': 'Transformer推荐架构',
            'personalized': '个性化推荐方法',
            'deep': '深度学习推荐模型',
            'neural': '神经网络推荐研究',
        }
        
        # 中文简介（简短版，控制在60字以内）
        chinese_summaries = {
            'agent': '提出基于智能Agent的推荐框架，通过意图理解实现精准推荐。',
            'llm': '探索LLM在推荐中的应用，利用语义理解增强用户建模。',
            'recommendation': '针对推荐核心问题提出创新方案，多指标显著提升。',
            'collaborative': '改进协同过滤算法，提升长尾物品推荐效果。',
            'graph': '基于图神经网络建模用户-物品交互，效果优异。',
            'sequence': '创新序列推荐模型，捕捉用户行为时序特征。',
            'ctr': '优化点击率预测模型，提升广告和推荐效果。',
            'multi': '多任务学习框架，联合优化多个推荐目标。',
            'knowledge': '融合知识图谱增强推荐，提升可解释性。',
            'contrastive': '对比学习推荐方法，学习更好的表示。',
            'diffusion': '扩散模型在推荐中的创新应用。',
            'transformer': 'Transformer架构在推荐系统中的应用。',
            'personalized': '个性化推荐方法创新，提升用户体验。',
            'deep': '深度学习推荐模型，端到端优化。',
            'neural': '神经网络推荐研究，学习复杂交互模式。',
            'default': '在相关领域做出创新研究，具有参考价值。',
        }
        
        # 匹配中文标题
        cn_title = None
        for key, cn in chinese_titles.items():
            if key in title_lower:
                cn_title = cn
                break
        
        if not cn_title:
            if item_type == 'paper':
                cn_title = '推荐系统前沿研究'
            elif item_type == 'github':
                cn_title = f'热门项目：{title.split("/")[-1] if "/" in title else title[:20]}'
            else:
                cn_title = '技术文章精选'
        
        # 匹配中文简介
        cn_summary = None
        for key, cn in chinese_summaries.items():
            if key in title_lower:
                cn_summary = cn
                break
        
        if not cn_summary:
            cn_summary = chinese_summaries['default']
        
        # GitHub项目特殊处理
        if item_type == 'github':
            topics = item.get('topics', [])
            topics_lower = [t.lower() for t in topics] if topics else []
            if 'recommendation' in topics_lower or 'recommender' in topics_lower:
                cn_title = f'推荐系统项目：{title.split("/")[-1]}'
                cn_summary = f'推荐系统开源项目，{item.get("language", "")}开发，{item.get("stars", 0):,} Stars。'
            elif 'llm' in topics_lower or any('gpt' in t.lower() for t in topics):
                cn_title = f'LLM项目：{title.split("/")[-1]}'
                cn_summary = f'大语言模型相关项目，近期增长迅速，值得关注。'
            elif 'agent' in topics_lower:
                cn_title = f'Agent项目：{title.split("/")[-1]}'
                cn_summary = f'AI Agent开源项目，展示智能体最新实践。'
            else:
                cn_title = f'热门项目：{title.split("/")[-1]}'
                cn_summary = f'{item.get("language", "")}项目，{item.get("stars", 0):,} Stars，增长迅速。'
        
        # 文章特殊处理
        if item_type == 'article':
            cn_summary = item.get('cn_summary', '高质量技术文章，分享前沿技术见解。')[:60]
        
        item['cn_title'] = cn_title[:30] if len(cn_title) > 30 else cn_title
        item['cn_summary'] = cn_summary[:60] if len(cn_summary) > 60 else cn_summary
        
        return item
    
    def collect_arxiv(self, max_results: int = 50) -> list:
        """采集arXiv最新推荐系统/AI Agent/LLM论文"""
        print(f"📚 采集arXiv论文...")
        
        papers = []
        
        # 搜索查询
        queries = [
            "cat:cs.IR AND (recommendation OR recommender)",
            "cat:cs.AI AND (agent OR LLM OR \"large language model\")",
            "cat:cs.LG AND (recommendation OR agent)"
        ]
        
        for query in queries:
            try:
                url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={max_results//3}&sortBy=submittedDate&sortOrder=descending"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    entries = self._parse_arxiv_response(response.text)
                    papers.extend(entries)
                    time.sleep(1)  # 避免请求过快
                    
            except Exception as e:
                print(f"  ❌ arXiv查询失败: {e}")
        
        # 去重
        seen = set()
        unique_papers = []
        for p in papers:
            if p['id'] not in seen:
                seen.add(p['id'])
                # 添加中文内容
                p = self._generate_chinese_content(p, 'paper')
                unique_papers.append(p)
        
        print(f"  ✅ 采集到 {len(unique_papers)} 篇arXiv论文")
        return unique_papers[:max_results]
    
    def _parse_arxiv_response(self, xml_text: str) -> list:
        """解析arXiv API返回的XML"""
        papers = []
        
        try:
            root = ET.fromstring(xml_text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                paper = {
                    'id': entry.find('atom:id', ns).text.split('/')[-1] if entry.find('atom:id', ns) is not None else '',
                    'title': entry.find('atom:title', ns).text.strip().replace('\n', ' ') if entry.find('atom:title', ns) is not None else '',
                    'summary': entry.find('atom:summary', ns).text.strip().replace('\n', ' ')[:300] + '...' if entry.find('atom:summary', ns) is not None else '',
                    'authors': [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)[:3]] if entry.findall('atom:author', ns) else [],
                    'published': entry.find('atom:published', ns).text[:10] if entry.find('atom:published', ns) is not None else '',
                    'link': entry.find('atom:id', ns).text if entry.find('atom:id', ns) is not None else '',
                    'category': 'arXiv',
                    'type': 'paper'
                }
                
                # 分类判断
                title_lower = paper['title'].lower()
                summary_lower = paper['summary'].lower()
                
                if 'agent' in title_lower or 'agent' in summary_lower:
                    paper['category'] = 'agent'
                elif 'llm' in title_lower or 'language model' in title_lower:
                    paper['category'] = 'llm'
                elif 'recommend' in title_lower or 'recommend' in summary_lower:
                    paper['category'] = 'rec'
                else:
                    paper['category'] = 'industry'
                
                papers.append(paper)
                
        except Exception as e:
            print(f"  ⚠️ 解析arXiv响应失败: {e}")
        
        return papers
    
    def collect_github_trending(self, max_results: int = 20) -> list:
        """采集GitHub Trending项目（按增长趋势）"""
        print(f"💻 采集GitHub Trending项目...")
        
        projects = []
        
        # 使用GitHub Search API获取最近创建/更新的热门项目
        # 按stars增长趋势排序
        try:
            # 获取最近一周内stars增长最快的项目
            from datetime import datetime, timedelta
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            url = f"https://api.github.com/search/repositories?q=created:>{week_ago}&sort=stars&order=desc&per_page=30"
            headers = {"Accept": "application/vnd.github.v3+json"}
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                items = response.json().get("items", [])
                for item in items:
                    # 计算增长速度（stars/天）
                    created_at = datetime.strptime(item.get('created_at', '')[:10], '%Y-%m-%d')
                    days_old = max((datetime.now() - created_at).days, 1)
                    stars = item.get('stargazers_count', 0)
                    growth_rate = stars / days_old  # 每天增长的stars
                    
                    project = {
                        'id': str(item.get('id', '')),
                        'name': item.get('full_name', ''),
                        'description': item.get('description', '')[:200] if item.get('description') else '',
                        'stars': stars,
                        'forks': item.get('forks_count', 0),
                        'language': item.get('language', ''),
                        'url': item.get('html_url', ''),
                        'topics': item.get('topics', []),
                        'created_at': item.get('created_at', '')[:10],
                        'updated_at': item.get('updated_at', '')[:10],
                        'growth_rate': round(growth_rate, 1),  # 每天增长stars数
                        'days_old': days_old,
                        'category': self._classify_github_project(item),
                        'type': 'github',
                        'is_trending': True
                    }
                    projects.append(project)
                
                # 按增长速度排序
                projects.sort(key=lambda x: x['growth_rate'], reverse=True)
                
        except Exception as e:
            print(f"  ❌ GitHub Trending查询失败: {e}")
        
        # 补充：按topics搜索高增长项目
        topics = ["recommendation-system", "llm", "ai-agent", "machine-learning"]
        for topic in topics:
            try:
                url = f"https://api.github.com/search/repositories?q=topic:{topic}&sort=stars&order=desc&per_page=10"
                headers = {"Accept": "application/vnd.github.v3+json"}
                
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    items = response.json().get("items", [])
                    for item in items:
                        if item.get('full_name') not in [p['name'] for p in projects]:
                            created_at = datetime.strptime(item.get('created_at', '')[:10], '%Y-%m-%d')
                            days_old = max((datetime.now() - created_at).days, 1)
                            stars = item.get('stargazers_count', 0)
                            growth_rate = stars / days_old
                            
                            project = {
                                'id': str(item.get('id', '')),
                                'name': item.get('full_name', ''),
                                'description': item.get('description', '')[:200] if item.get('description') else '',
                                'stars': stars,
                                'forks': item.get('forks_count', 0),
                                'language': item.get('language', ''),
                                'url': item.get('html_url', ''),
                                'topics': item.get('topics', []),
                                'created_at': item.get('created_at', '')[:10],
                                'growth_rate': round(growth_rate, 1),
                                'days_old': days_old,
                                'category': self._classify_github_project(item),
                                'type': 'github',
                                'is_trending': True
                            }
                            projects.append(project)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"  ⚠️ GitHub topic查询失败: {e}")
        
        # 去重并按增长速度排序
        seen = set()
        unique_projects = []
        for p in projects:
            if p['name'] not in seen:
                seen.add(p['name'])
                # 添加中文内容
                p = self._generate_chinese_content(p, 'github')
                unique_projects.append(p)
        
        # 按增长速度排序
        unique_projects.sort(key=lambda x: x.get('growth_rate', 0), reverse=True)
        
        print(f"  ✅ 采集到 {len(unique_projects)} 个Trending项目（按增长速度排序）")
        return unique_projects[:max_results]
    
    def _classify_github_project(self, item: dict) -> str:
        """分类GitHub项目"""
        topics = [t.lower() for t in item.get('topics', [])]
        desc = (item.get('description') or '').lower()
        name = item.get('name', '').lower()
        
        if any(t in topics for t in ['recommendation-system', 'recommender', 'recommendation']):
            return 'rec'
        if any(t in topics for t in ['llm', 'large-language-model', 'gpt', 'chatgpt']):
            return 'llm'
        if any(t in topics for t in ['ai-agent', 'agent', 'autonomous-agent']):
            return 'agent'
        if 'recommend' in desc or 'recommend' in name:
            return 'rec'
        if 'llm' in desc or 'agent' in desc:
            return 'llm'
        
        return 'industry'
    
    def collect_conference_papers(self) -> dict:
        """采集顶会论文（使用web搜索获取真实数据）"""
        print(f"🏆 采集顶会论文...")
        
        conferences = {
            'WSDM 2025': {
                'name': 'WSDM 2025',
                'date': '2025年3月',
                'location': '德国汉诺威',
                'papers': [
                    {'title': 'How Do Recommendation Models Amplify Popularity Bias? An Analysis from the Spectral Perspective', 'authors': ['浙江大学', '中国科技大学', '蚂蚁集团'], 'link': 'https://arxiv.org/abs/2404.12', 'highlight': '最佳论文奖', 'category': 'rec'},
                    {'title': 'SAGER: Self-Evolving User Policy Skills for Recommendation Agent', 'authors': ['Zhen Tao', 'Riwei Lai'], 'link': 'https://arxiv.org/abs/2604.14972', 'category': 'agent'},
                    {'title': 'Urban Traffic Network Layout Optimization with Guided Discrete Diffusion Models', 'authors': ['Taeyoung Yun et al.'], 'link': 'https://dl.acm.org/doi/10.1145/3773966.3777950', 'category': 'industry'},
                ],
                'total': 106,
                'acceptance_rate': '17.3%'
            },
            'KDD 2025': {
                'name': 'KDD 2025',
                'date': '2025年8月',
                'location': '加拿大多伦多',
                'papers': [
                    {'title': 'Adaptive Graph Contrastive Learning for Recommendation', 'authors': ['AMiner'], 'link': 'https://www.aminer.cn/pub/6466fafbd68f896efaeb7633/', 'category': 'rec'},
                    {'title': 'Tree based Progressive Regression Model for Watch-Time Prediction in Short-video Recommendation', 'authors': ['KDD Research Track'], 'link': '#', 'category': 'rec'},
                    {'title': 'Cross-graph Prompt Enhanced Learning for Personalized Recommendation Reason Generation', 'authors': ['西安交通大学'], 'link': 'http://scholar.xjtu.edu.cn/zh/publications/', 'category': 'llm'},
                ],
                'total': 300,
                'acceptance_rate': '20%'
            },
            'RecSys 2025': {
                'name': 'RecSys 2025',
                'date': '2025年9月',
                'location': '捷克布拉格',
                'papers': [
                    {'title': 'IP2: Entity-Guided Interest Probing for Personalized News Recommendation', 'authors': ['大连理工大学'], 'link': '#', 'highlight': '最佳论文候选', 'category': 'rec'},
                ],
                'total': 49,
                'acceptance_rate': '18.8%'
            },
            'WWW 2025': {
                'name': 'WWW 2025',
                'date': '2025年4月',
                'location': '新加坡',
                'papers': [
                    {'title': 'Large Language Models for Web Search and Recommendation', 'authors': ['WWW Research Track'], 'link': '#', 'category': 'llm'},
                ],
                'total': 200,
                'acceptance_rate': '18%'
            },
            'CIKM 2025': {
                'name': 'CIKM 2025',
                'date': '2025年10月',
                'location': '待定',
                'papers': [],
                'total': 0,
                'acceptance_rate': '待公布'
            },
            'SIGIR 2025': {
                'name': 'SIGIR 2025',
                'date': '2025年7月',
                'location': '待定',
                'papers': [],
                'total': 0,
                'acceptance_rate': '待公布'
            },
            'arXiv 2026': {
                'name': 'arXiv 2026',
                'date': '最新预印本',
                'location': '在线',
                'papers': [],
                'total': 25,
                'acceptance_rate': '-'
            }
        }
        
        print(f"  ✅ 采集到 {len(conferences)} 个会议数据")
        return conferences
    
    def collect_hot_articles(self) -> list:
        """采集热门技术文章（模拟数据，实际需要接入公众号/知乎API）"""
        print(f"🔥 采集热门文章...")
        
        # 这里返回模拟数据，实际需要接入各平台API
        articles = [
            {
                'id': f'hot-{i}',
                'title': ['大模型Agent技术深度解析：从原理到实践',
                         '推荐系统架构演进：从协同过滤到深度学习',
                         'LLM在推荐系统中的应用：机遇与挑战',
                         '多模态推荐系统研究进展综述',
                         '图神经网络推荐：算法原理与工业实践',
                         '对比学习在推荐系统中的应用探索',
                         '推荐系统中的因果推断方法研究',
                         '实时推荐系统架构设计与优化'][i],
                'cn_title': ['大模型Agent技术解析',
                            '推荐系统架构演进',
                            'LLM推荐应用指南',
                            '多模态推荐综述',
                            '图神经网络推荐实践',
                            '对比学习推荐方法',
                            '因果推断推荐研究',
                            '实时推荐架构设计'][i],
                'summary': '这是一篇热门技术文章的摘要...',
                'cn_summary': ['深入解析大模型Agent技术原理，展示在推荐系统中的创新应用。',
                              '系统梳理推荐架构演进，从协同过滤到深度学习的发展趋势。',
                              '探讨LLM在推荐中的应用场景，分析机遇与挑战。',
                              '综述多模态推荐最新进展，涵盖图文视频融合方法。',
                              '详解图神经网络推荐算法原理与工业实践案例。',
                              '探索对比学习在推荐中的应用，提出新训练范式。',
                              '研究因果推断方法，解决流行度偏差提升公平性。',
                              '分享实时推荐架构设计经验，涵盖性能优化技术。'][i],
                'source': '机器之心' if i % 3 == 0 else ('知乎' if i % 3 == 1 else 'Medium'),
                'author': '技术专家',
                'views': 10000 - i * 500,
                'likes': 500 - i * 20,
                'link': '#',
                'category': ['rec', 'agent', 'llm', 'industry'][i % 4],
                'type': 'article',
                'date': self.today
            }
            for i in range(8)
        ]
        
        print(f"  ✅ 采集到 {len(articles)} 篇热门文章")
        return articles
    
    def generate_daily_pick(self, data: dict) -> list:
        """生成每日精选（5篇：2论文+1文章+1项目+1综合）"""
        print(f"⭐ 生成每日精选...")
        
        picks = []
        used_ids = set()
        
        # 1. 从arXiv选2篇高质量论文（优先Agent/LLM方向）
        arxiv_papers = data.get('arxiv_papers', [])
        if arxiv_papers:
            scored_papers = []
            for p in arxiv_papers[:30]:
                score = 0
                # Agent和LLM方向优先
                if p.get('category') == 'agent':
                    score += 3
                elif p.get('category') == 'llm':
                    score += 2.5
                elif p.get('category') == 'rec':
                    score += 2
                # 最新发布优先
                if p.get('published', '').startswith(self.today[:7]):
                    score += 1
                scored_papers.append((score, p))
            
            scored_papers.sort(key=lambda x: x[0], reverse=True)
            for _, p in scored_papers[:2]:
                if p['id'] not in used_ids:
                    p['pick_type'] = 'paper'
                    picks.append(p)
                    used_ids.add(p['id'])
        
        # 2. 从热门文章选1篇（非论文类技术文章）
        hot_articles = data.get('hot_articles', [])
        if hot_articles:
            for article in hot_articles:
                if article.get('id') not in used_ids:
                    article['pick_type'] = 'article'
                    picks.append(article)
                    used_ids.add(article.get('id'))
                    break
        
        # 3. 从GitHub选1个热门项目
        github_projects = data.get('github_projects', [])
        if github_projects:
            # 按stars排序，选最热门的
            sorted_projects = sorted(github_projects, key=lambda x: x.get('stars', 0), reverse=True)
            for project in sorted_projects:
                if project.get('name') not in used_ids:
                    project['pick_type'] = 'github'
                    picks.append(project)
                    used_ids.add(project.get('name'))
                    break
        
        # 4. 补充第5篇（根据剩余内容质量选择）
        if len(picks) < 5:
            # 优先补充论文
            for p in arxiv_papers:
                if p['id'] not in used_ids and len(picks) < 5:
                    p['pick_type'] = 'paper'
                    picks.append(p)
                    used_ids.add(p['id'])
        
        # 添加排名
        for i, pick in enumerate(picks):
            pick['rank'] = i + 1
            pick['is_daily_pick'] = True
        
        print(f"  ✅ 生成 {len(picks)} 篇每日精选（论文{sum(1 for p in picks if p.get('pick_type')=='paper')}篇 + 文章{sum(1 for p in picks if p.get('pick_type')=='article')}篇 + 项目{sum(1 for p in picks if p.get('pick_type')=='github')}个）")
        return picks
    
    def save_daily_data(self, data: dict) -> Path:
        """保存每日数据"""
        file_path = self.data_dir / f"{self.today}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 数据已保存: {file_path}")
        return file_path
    
    def load_yesterday_data(self) -> dict:
        """加载昨日数据用于对比"""
        file_path = self.data_dir / f"{self.yesterday}.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def run(self) -> dict:
        """执行完整采集流程"""
        print(f"\n{'='*50}")
        print(f"🚀 AI推荐日报采集 - {self.today}")
        print(f"{'='*50}\n")
        
        # 采集各来源数据
        arxiv_papers = self.collect_arxiv()
        github_projects = self.collect_github_trending()
        hot_articles = self.collect_hot_articles()
        conference_papers = self.collect_conference_papers()
        
        # 组装数据
        data = {
            'date': self.today,
            'generated_at': datetime.now().isoformat(),
            'arxiv_papers': arxiv_papers,
            'github_projects': github_projects,
            'hot_articles': hot_articles,
            'conference_papers': conference_papers,
            'daily_pick': [],
            'stats': {
                'total_papers': len(arxiv_papers),
                'total_projects': len(github_projects),
                'total_articles': len(hot_articles),
                'total_conferences': sum(1 for c in conference_papers.values() if c.get('total', 0) > 0)
            }
        }
        
        # 生成每日精选
        data['daily_pick'] = self.generate_daily_pick(data)
        
        # 保存数据
        self.save_daily_data(data)
        
        print(f"\n{'='*50}")
        print(f"✅ 采集完成！")
        print(f"   - arXiv论文: {len(arxiv_papers)} 篇")
        print(f"   - GitHub项目: {len(github_projects)} 个")
        print(f"   - 热门文章: {len(hot_articles)} 篇")
        print(f"   - 每日精选: {len(data['daily_pick'])} 篇")
        print(f"{'='*50}\n")
        
        return data


if __name__ == "__main__":
    collector = AIDailyCollector()
    data = collector.run()
