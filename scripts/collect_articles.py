#!/usr/bin/env python3
"""
AI推荐日报 - 文章采集脚本
从多个技术媒体平台采集真实文章数据
使用本地 RSSHub 或国内镜像源
"""

import json
import requests
import hashlib
import time
import subprocess
from datetime import datetime
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def ensure_rsshub_running():
    """确保 RSSHub 正在运行"""
    try:
        # 检查本地 RSSHub 是否可用
        response = requests.get("http://localhost:1200/", timeout=2)
        if response.status_code == 200:
            print("  ✅ RSSHub 已在运行")
            return True
    except:
        pass

    # 尝试启动 RSSHub
    print("  ⚠️ RSSHub 未运行，尝试启动...")
    start_script = Path(__file__).parent / "start_rsshub.sh"
    if start_script.exists():
        result = subprocess.run(["bash", str(start_script)], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ RSSHub 启动成功")
            return True
        else:
            print(f"  ❌ RSSHub 启动失败: {result.stderr}")
            return False
    return False


class ArticleCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # 使用本地 RSSHub 实例（优先）或国内镜像
        self.rsshub_local = "http://localhost:1200"
        self.rsshub_mirror = "https://rsshub.rssforever.com"
        
        # 检测本地 RSSHub 是否可用
        try:
            import urllib.request
            urllib.request.urlopen(f"{self.rsshub_local}/", timeout=2)
            self.rsshub_base = self.rsshub_local
            print(f"  ✅ 使用本地 RSSHub: {self.rsshub_local}")
        except:
            self.rsshub_base = self.rsshub_mirror
            print(f"  ⚠️ 本地 RSSHub 不可用，使用镜像: {self.rsshub_mirror}")
        
        # 高质量技术媒体 RSS 源（已验证可用）
        self.rss_sources = [
            # ===== 微信公众号（通过 wechat2rss.xlab.app）=====
            {
                'name': '机器之心',
                'rss_url': 'https://wechat2rss.xlab.app/feed/51e92aad2728acdd1fda7314be32b16639353001.xml',
                'keywords': ['AI', '大模型', '推荐', '算法', '机器学习', 'LLM', 'Agent', '智能体', 'GPT', 'Claude'],
                'category': 'wechat',
                'priority': 1
            },
            {
                'name': '量子位',
                'rss_url': 'https://wechat2rss.xlab.app/feed/7131b577c61365cb47e81000738c10d872685908.xml',
                'keywords': ['AI', '大模型', '推荐', '算法', '机器学习', 'LLM', 'Agent', '智能体', 'GPT', 'Claude', 'Qwen', 'DeepSeek'],
                'category': 'wechat',
                'priority': 1
            },
            {
                'name': '新智元',
                'rss_url': 'https://wechat2rss.xlab.app/feed/ede30346413ea70dbef5d485ea5cbb95cca446e7.xml',
                'keywords': ['AI', '大模型', '推荐', '算法', '机器学习', 'LLM', 'Agent', '智能体', 'GPT', 'Claude'],
                'category': 'wechat',
                'priority': 1
            },
            {
                'name': 'PaperWeekly',
                'rss_url': 'https://wechat2rss.xlab.app/feed/3be891c2f4e526629ab055a297cc2cd6c1f0a563.xml',
                'keywords': ['AI', '大模型', '推荐', '算法', '机器学习', 'LLM', 'Agent', '智能体', '论文', 'Paper'],
                'category': 'wechat',
                'priority': 1
            },
            # ===== 技术博客（通过 RSSHub）=====
            {
                'name': '美团技术团队',
                'rss_url': f'{self.rsshub_base}/meituan/tech',
                'keywords': ['推荐', '算法', '机器学习', 'AI', '大模型', '搜索', '广告'],
                'category': 'tech_blog',
                'priority': 1
            },
            # ===== 知乎（通过 RSSHub 国内镜像）=====
            {
                'name': '知乎热榜',
                'rss_url': f'{self.rsshub_base}/zhihu/hot',
                'keywords': ['AI', '大模型', '推荐', '算法', '机器学习', 'LLM', 'Agent', '智能体'],
                'category': 'zhihu',
                'priority': 2
            },
            {
                'name': '知乎日报',
                'rss_url': f'{self.rsshub_base}/zhihu/daily',
                'keywords': ['AI', '大模型', '推荐', '算法', '机器学习', 'LLM', 'Agent', '智能体'],
                'category': 'zhihu',
                'priority': 2
            },
            # ===== 技术媒体（通过 RSSHub 国内镜像）=====
            {
                'name': '36氪快讯',
                'rss_url': f'{self.rsshub_base}/36kr/newsflashes',
                'keywords': ['AI', '大模型', '推荐', '算法', '机器学习', 'LLM', 'Agent', '智能体'],
                'category': 'industry',
                'priority': 1
            },
            {
                'name': 'IT之家热榜',
                'rss_url': f'{self.rsshub_base}/ithome/ranking/7days',
                'keywords': ['AI', '大模型', '推荐', '算法', '机器学习', 'LLM', 'Agent', '智能体', 'GPT', 'Claude'],
                'category': 'tech',
                'priority': 2
            },
            {
                'name': '开源中国资讯',
                'rss_url': f'{self.rsshub_base}/oschina/news',
                'keywords': ['AI', '大模型', '推荐', '算法', '机器学习', 'LLM', 'Agent', '智能体', 'GPT', 'Claude', 'Qwen', 'DeepSeek'],
                'category': 'opensource',
                'priority': 1
            },
            {
                'name': 'InfoQ技术文章',
                'rss_url': f'{self.rsshub_base}/infoq/recommend',
                'keywords': ['AI', '大模型', '推荐', '算法', '机器学习', 'LLM', 'Agent'],
                'category': 'tech',
                'priority': 2
            }
        ]
    
    def load_cache(self, source: str) -> dict:
        """加载缓存"""
        cache_file = self.cache_dir / f"{source}_articles.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'items': [], 'last_update': ''}
    
    def save_cache(self, source: str, data: dict):
        """保存缓存"""
        cache_file = self.cache_dir / f"{source}_articles.json"
        data['last_update'] = datetime.now().isoformat()
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def parse_rss_xml(self, xml_content: str) -> list:
        """解析 RSS XML 内容"""
        items = []
        try:
            root = ET.fromstring(xml_content)
            channel = root.find('channel')
            if channel is None:
                return items
            
            for item in channel.findall('item'):
                entry = {}
                
                # 标题
                title_elem = item.find('title')
                entry['title'] = title_elem.text if title_elem is not None else ''
                
                # 链接
                link_elem = item.find('link')
                entry['link'] = link_elem.text if link_elem is not None else ''
                
                # 描述/摘要
                desc_elem = item.find('description')
                desc_text = desc_elem.text if desc_elem is not None else ''
                # 清理 HTML 标签
                entry['summary'] = re.sub(r'<[^>]+>', '', desc_text)[:300] if desc_text else ''
                
                # 发布时间
                pub_elem = item.find('pubDate')
                entry['published'] = pub_elem.text if pub_elem is not None else ''
                
                items.append(entry)
                
        except ET.ParseError as e:
            print(f"  ⚠️ XML解析错误: {e}")
        
        return items
    
    def fetch_rss(self, rss_url: str, source_name: str, keywords: list, category: str) -> list:
        """通过RSS获取文章"""
        articles = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/rss+xml, application/xml, text/xml'
            }
            
            response = requests.get(rss_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            items = self.parse_rss_xml(response.content)
            
            for entry in items[:15]:  # 每个源取最近15篇
                title = entry.get('title', '')
                link = entry.get('link', '')
                summary = entry.get('summary', '')
                published = entry.get('published', '')
                
                if not title or not link:
                    continue
                
                # 检查关键词匹配（宽松匹配：标题或摘要包含任一关键词）
                title_lower = title.lower()
                summary_lower = summary.lower()
                
                matched = any(kw.lower() in title_lower or kw.lower() in summary_lower for kw in keywords)
                
                # 如果不匹配关键词，但有内容也保留（作为行业资讯）
                if not matched:
                    # 检查是否是技术相关
                    tech_keywords = ['技术', '开发', '代码', '软件', '系统', '架构', '框架', '开源', '发布', '更新']
                    if not any(kw in title for kw in tech_keywords):
                        continue
                
                # 生成ID
                article_id = hashlib.md5(link.encode()).hexdigest()[:12]
                
                # 解析发布时间
                pub_date = self.today
                if published:
                    try:
                        # 解析 RFC 2822 格式时间
                        from email.utils import parsedate_to_datetime
                        dt = parsedate_to_datetime(published)
                        pub_date = dt.strftime("%Y-%m-%d")
                    except:
                        pass
                
                article = {
                    'id': article_id,
                    'title': title,
                    'summary': summary[:200] if summary else '',
                    'link': link,
                    'source': source_name,
                    'published': pub_date,
                    'views': 0,
                    'likes': 0,
                    'type': 'article',
                    'category': category,
                    'collected_at': datetime.now().isoformat()
                }
                
                # 智能分类
                title_lower = title.lower()
                if '推荐' in title or 'recommend' in title_lower:
                    article['category'] = 'rec'
                elif 'agent' in title_lower or '智能体' in title:
                    article['category'] = 'agent'
                elif 'llm' in title_lower or '大模型' in title or 'gpt' in title_lower or 'claude' in title_lower:
                    article['category'] = 'llm'
                elif 'qwen' in title_lower or 'deepseek' in title_lower or '开源' in title:
                    article['category'] = 'opensource'
                
                articles.append(article)
                
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ {source_name} RSS获取失败: {e}")
        except Exception as e:
            print(f"  ⚠️ {source_name} 处理失败: {e}")
        
        return articles
    
    def collect_all_articles(self) -> list:
        """采集所有文章源"""
        print(f"📰 开始采集技术文章...")
        
        all_articles = []
        cache = self.load_cache('all')
        cached_links = {a['link'] for a in cache.get('items', [])}
        
        for source in self.rss_sources:
            print(f"  📡 采集 {source['name']}...")
            articles = self.fetch_rss(
                source['rss_url'], 
                source['name'], 
                source['keywords'],
                source['category']
            )
            
            new_count = 0
            for article in articles:
                if article['link'] not in cached_links:
                    all_articles.append(article)
                    new_count += 1
            
            print(f"    ✅ 获取 {len(articles)} 篇，新增 {new_count} 篇")
            time.sleep(0.5)  # 避免请求过快
        
        # 合并缓存
        all_cached = all_articles + cache.get('items', [])
        seen = set()
        unique = []
        for a in all_cached:
            if a['link'] not in seen:
                seen.add(a['link'])
                unique.append(a)
        
        # 按时间排序
        unique.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        # 保存缓存（保留最近100篇）
        self.save_cache('all', {'items': unique[:100]})
        
        print(f"\n✅ 共采集 {len(all_articles)} 篇新文章，缓存共 {len(unique)} 篇")
        
        # 生成中文内容（不截断标题，保留完整标题）
        for article in unique:
            article['cn_title'] = article.get('title', '')
            article['cn_summary'] = article.get('summary', '')[:200]
        
        return unique[:30]
    
    def get_hot_articles(self, limit: int = 15) -> list:
        """获取热门文章（用于日报展示，共15篇）"""
        all_articles = self.collect_all_articles()
        
        # 按分类筛选，确保每个子tab都有内容
        hot_articles = []
        categories = {'wechat': [], 'tech_blog': [], 'industry': [], 'zhihu': [], 'other': []}
        
        for article in all_articles:
            cat = article.get('category', 'other')
            if cat in categories and len(categories[cat]) < 5:
                categories[cat].append(article)
        
        # 合并，确保每个分类至少有1篇
        for cat, articles in categories.items():
            if articles:
                hot_articles.extend(articles[:3])  # 每个分类最多3篇
        
        # 按时间排序
        hot_articles.sort(key=lambda x: x.get('published', x.get('date', '')), reverse=True)
        
        return hot_articles[:limit]
    
    def save_to_daily_data(self, articles: list):
        """保存文章到 daily_data"""
        from datetime import datetime
        
        today = datetime.now().strftime("%Y-%m-%d")
        data_file = self.base_dir / "daily_data" / f"{today}.json"
        
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                'date': today,
                'daily_pick': [],
                'articles': [],
                'hot_articles': [],
                'github_projects': [],
                'arxiv_papers': [],
                'conferences': []
            }
        
        # 更新文章列表
        data['articles'] = articles
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存 {len(articles)} 篇文章到: {data_file}")


if __name__ == "__main__":
    collector = ArticleCollector()
    articles = collector.collect_all_articles()
    
    # 保存到 daily_data
    collector.save_to_daily_data(articles)
    
    print(f"\n📚 共采集 {len(articles)} 篇文章")
    print("\n热门文章预览：")
    for i, a in enumerate(articles[:10], 1):
        print(f"  {i}. [{a['source']}] {a['title'][:40]}")
