#!/usr/bin/env python3
"""
AI推荐日报 - 每日内容采集脚本
每日精选：5篇（论文/文章/GitHub项目）
热门文章：15篇（推荐算法/Agent/AI相关）
GitHub项目：5个
arXiv论文：20篇（展示5篇，剩余15篇在新页面）
"""

import json
import requests
import re
from datetime import datetime
from pathlib import Path
import hashlib

class DailyCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # 关键词过滤
        self.keywords = {
            'rec': ['recommend', 'recommendation', 'recsys', 'collaborative filtering', 'ctr', 'ranking'],
            'agent': ['agent', 'multi-agent', 'autonomous', 'tool use', 'planning'],
            'llm': ['llm', 'large language model', 'gpt', 'bert', 'transformer', 'chatgpt'],
            'ai': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network']
        }
    
    def is_relevant(self, title: str, summary: str = '') -> tuple:
        """检查内容是否相关，返回 (是否相关, 类别)"""
        text = (title + ' ' + summary).lower()
        
        for category, kws in self.keywords.items():
            for kw in kws:
                if kw in text:
                    return True, category
        
        return False, None
    
    def collect_rss_articles(self) -> list:
        """从 RSS 源采集文章"""
        articles = []
        
        # RSS 源列表
        rss_sources = [
            # 微信公众号
            ("https://wechat2rss.xlab.app/feed/51e92aad2728acdd1fda7314be32b16639353001.xml", "机器之心"),
            ("https://wechat2rss.xlab.app/feed/7131b577c61365cb47e81000738c10d872685908.xml", "量子位"),
            ("https://wechat2rss.xlab.app/feed/ede30346413ea70dbef5d485ea5cbb95cca446e7.xml", "新智元"),
            # 技术媒体
            ("https://rsshub.rssforever.com/36kr/newsflashes", "36氪"),
            ("https://rsshub.rssforever.com/ithome/ranking/7days", "IT之家"),
            ("https://rsshub.rssforever.com/oschina/news", "开源中国"),
        ]
        
        for rss_url, source in rss_sources:
            try:
                print(f"  采集: {source}...")
                response = requests.get(rss_url, timeout=15)
                if response.status_code == 200:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.content)
                    channel = root.find('channel')
                    
                    if channel:
                        for item in channel.findall('item')[:10]:
                            title_elem = item.find('title')
                            link_elem = item.find('link')
                            desc_elem = item.find('description')
                            
                            title = title_elem.text if title_elem is not None else ''
                            link = link_elem.text if link_elem is not None else ''
                            desc = desc_elem.text if desc_elem is not None else ''
                            
                            # 检查相关性
                            is_rel, category = self.is_relevant(title, desc)
                            if is_rel:
                                articles.append({
                                    'id': hashlib.md5(link.encode()).hexdigest()[:12],
                                    'title': title,
                                    'link': link,
                                    'summary': desc[:500],
                                    'source': source,
                                    'category': category,
                                    'published': self.today,
                                    'type': 'article'
                                })
            except Exception as e:
                print(f"    ⚠️ 采集失败: {e}")
        
        print(f"  ✅ 采集到 {len(articles)} 篇相关文章")
        return articles
    
    def collect_github_projects(self) -> list:
        """采集 GitHub 项目"""
        projects = []
        
        # GitHub Trending API (使用 RSSHub)
        try:
            print("  采集: GitHub Trending...")
            response = requests.get(
                "https://rsshub.rssforever.com/github/trending/daily",
                timeout=15
            )
            
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                channel = root.find('channel')
                
                if channel:
                    for item in channel.findall('item')[:20]:
                        title_elem = item.find('title')
                        link_elem = item.find('link')
                        desc_elem = item.find('description')
                        
                        title = title_elem.text if title_elem is not None else ''
                        link = link_elem.text if link_elem is not None else ''
                        desc = desc_elem.text if desc_elem is not None else ''
                        
                        # 检查相关性
                        is_rel, category = self.is_relevant(title, desc)
                        if is_rel:
                            # 提取项目名
                            name_match = re.search(r'github\.com/([^/]+/[^/]+)', link)
                            name = name_match.group(1) if name_match else title
                            
                            projects.append({
                                'id': hashlib.md5(link.encode()).hexdigest()[:12],
                                'name': name,
                                'title': title,
                                'link': link,
                                'description': desc[:500],
                                'category': category,
                                'type': 'github'
                            })
        except Exception as e:
            print(f"    ⚠️ 采集失败: {e}")
        
        print(f"  ✅ 采集到 {len(projects)} 个相关项目")
        return projects
    
    def collect_arxiv_papers(self) -> list:
        """采集 arXiv 论文"""
        papers = []
        
        # arXiv API
        queries = [
            "cat:cs.IR AND (recommend OR recommendation)",  # 推荐系统
            "cat:cs.AI AND agent",  # AI Agent
            "cat:cs.CL AND (LLM OR \"large language model\")",  # LLM
        ]
        
        for query in queries:
            try:
                print(f"  采集: arXiv - {query[:30]}...")
                url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.content)
                    
                    ns = {'atom': 'http://www.w3.org/2005/Atom'}
                    
                    for entry in root.findall('atom:entry', ns)[:10]:
                        title_elem = entry.find('atom:title', ns)
                        summary_elem = entry.find('atom:summary', ns)
                        link_elem = entry.find('atom:id', ns)
                        published_elem = entry.find('atom:published', ns)
                        
                        title = title_elem.text.strip() if title_elem is not None else ''
                        summary = summary_elem.text.strip()[:500] if summary_elem is not None else ''
                        link = link_elem.text if link_elem is not None else ''
                        published = published_elem.text[:10] if published_elem is not None else ''
                        
                        # 提取 arXiv ID
                        id_match = re.search(r'(\d{4}\.\d{4,5})', link)
                        arxiv_id = id_match.group(1) if id_match else ''
                        
                        # 检查相关性
                        is_rel, category = self.is_relevant(title, summary)
                        if is_rel:
                            papers.append({
                                'id': arxiv_id,
                                'arxiv_id': arxiv_id,
                                'title': title,
                                'summary': summary,
                                'link': link,
                                'category': category,
                                'published': published,
                                'type': 'paper'
                            })
            except Exception as e:
                print(f"    ⚠️ 采集失败: {e}")
        
        # 去重
        seen = set()
        unique_papers = []
        for p in papers:
            if p['id'] not in seen:
                seen.add(p['id'])
                unique_papers.append(p)
        
        print(f"  ✅ 采集到 {len(unique_papers)} 篇相关论文")
        return unique_papers
    
    def select_daily_pick(self, articles: list, projects: list, papers: list) -> list:
        """选择每日精选（5篇）"""
        picks = []
        
        # 策略：优先选择高质量内容
        # 1. 论文（2篇）
        for paper in papers[:2]:
            paper['pick_type'] = 'paper'
            paper['rank'] = len(picks) + 1
            picks.append(paper)
        
        # 2. GitHub 项目（1篇）
        for project in projects[:1]:
            project['pick_type'] = 'github'
            project['rank'] = len(picks) + 1
            picks.append(project)
        
        # 3. 文章（2篇）
        for article in articles[:2]:
            article['pick_type'] = 'article'
            article['rank'] = len(picks) + 1
            picks.append(article)
        
        return picks[:5]
    
    def run(self):
        """执行采集"""
        print(f"{'='*50}")
        print(f"📝 AI推荐日报 - 内容采集")
        print(f"{'='*50}")
        print(f"日期: {self.today}\n")
        
        # 采集各类内容
        print("📡 采集文章...")
        articles = self.collect_rss_articles()
        
        print("\n📡 采集 GitHub 项目...")
        projects = self.collect_github_projects()
        
        print("\n📡 采集 arXiv 论文...")
        papers = self.collect_arxiv_papers()
        
        # 选择每日精选
        print("\n⭐ 选择每日精选...")
        daily_pick = self.select_daily_pick(articles, projects, papers)
        
        # 限制数量
        articles = articles[:15]  # 热门文章 15 篇
        projects = projects[:5]   # GitHub 项目 5 个
        papers = papers[:20]      # arXiv 论文 20 篇
        
        # 保存数据
        data = {
            'date': self.today,
            'daily_pick': daily_pick,
            'hot_articles': articles,
            'github_projects': projects,
            'arxiv_papers': papers,
            'stats': {
                'total_papers': len(papers),
                'total_projects': len(projects),
                'total_articles': len(articles),
                'total_pick': len(daily_pick)
            }
        }
        
        output_file = self.base_dir / "daily_data" / f"{self.today}.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*50}")
        print(f"✅ 采集完成！")
        print(f"   每日精选: {len(daily_pick)} 篇")
        print(f"   热门文章: {len(articles)} 篇")
        print(f"   GitHub项目: {len(projects)} 个")
        print(f"   arXiv论文: {len(papers)} 篇")
        print(f"{'='*50}")
        
        return data


if __name__ == "__main__":
    collector = DailyCollector()
    collector.run()
