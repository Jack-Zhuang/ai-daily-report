#!/usr/bin/env python3
"""
AI推荐日报 - arXiv 论文采集脚本
采集推荐系统、AI Agent、LLM 领域的最新论文，优先关注工业落地
"""

import json
import requests
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET


class ArxivCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # 采集配置
        self.max_papers = 30  # 每天最多采集 30 篇
        self.max_days = 7     # 最近 7 天内的论文
        
        # 工业落地关键词（加分项）
        self.industry_keywords = [
            "production", "industrial", "deploy", "deployment", "online",
            "real-time", "realtime", "scalable", "large-scale", "distributed",
            "A/B test", "experiment", "application", "system", "framework",
            "efficiency", "optimization", "serving", "inference"
        ]
        
        # 核心领域关键词
        self.domain_keywords = {
            'rec': [
                'recommend', 'recommendation', 'recsys', 'collaborative filtering',
                'ctr', 'ranking', 'personalization', 'user modeling'
            ],
            'agent': [
                'agent', 'multi-agent', 'autonomous', 'tool use', 'planning',
                'reasoning', 'action', 'task automation'
            ],
            'llm': [
                'llm', 'large language model', 'gpt', 'bert', 'transformer',
                'chatgpt', 'language model', 'generation'
            ]
        }
        
        # 加载已采集的论文ID（用于去重）
        self.collected_ids = self._load_collected_ids()
    
    def _load_collected_ids(self) -> set:
        """加载已采集的论文ID"""
        collected = set()
        cache_file = self.cache_dir / "arxiv_papers.json"
        
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                papers = data.get('items', data) if isinstance(data, dict) else data
                for p in papers:
                    if p.get('arxiv_id'):
                        collected.add(p['arxiv_id'])
        
        # 也检查最近几天的数据文件
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            data_file = self.base_dir / "daily_data" / f"{date}.json"
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for p in data.get('arxiv_papers', []):
                        if p.get('arxiv_id'):
                            collected.add(p['arxiv_id'])
        
        return collected
    
    def calculate_industry_score(self, title: str, summary: str) -> float:
        """计算工业落地相关性分数"""
        text = (title + ' ' + summary).lower()
        score = 0
        
        for kw in self.industry_keywords:
            if kw.lower() in text:
                score += 1
        
        return min(score, 5)  # 最高 5 分
    
    def categorize_paper(self, title: str, summary: str) -> str:
        """对论文进行分类"""
        text = (title + ' ' + summary).lower()
        
        for category, keywords in self.domain_keywords.items():
            for kw in keywords:
                if kw.lower() in text:
                    return category
        
        return 'other'
    
    def is_recent(self, published: str) -> bool:
        """检查论文是否足够新"""
        if not published:
            return True
        
        try:
            pub_date = datetime.strptime(published[:10], '%Y-%m-%d')
            days_ago = (datetime.now() - pub_date).days
            return days_ago <= self.max_days
        except:
            return True
    
    def collect_papers(self) -> list:
        """采集 arXiv 论文"""
        papers = []
        
        # arXiv API 查询
        queries = [
            ("cat:cs.IR", "信息检索"),
            ("cat:cs.AI", "人工智能"),
            ("cat:cs.CL", "计算语言学"),
            ("cat:cs.LG", "机器学习"),
        ]
        
        print(f"\n{'='*50}")
        print(f"📚 采集 arXiv 论文（最近 {self.max_days} 天）")
        print(f"{'='*50}\n")
        
        for query, desc in queries:
            print(f"  🔍 查询: {desc}...", end=" ", flush=True)
            
            try:
                url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=30&sortBy=submittedDate&sortOrder=descending"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    ns = {'atom': 'http://www.w3.org/2005/Atom'}
                    
                    count = 0
                    for entry in root.findall('atom:entry', ns):
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
                        
                        # 去重检查
                        if arxiv_id in self.collected_ids:
                            continue
                        
                        # 时效性检查
                        if not self.is_recent(published):
                            continue
                        
                        # 相关性检查
                        category = self.categorize_paper(title, summary)
                        if category == 'other':
                            continue
                        
                        # 计算工业落地分数
                        industry_score = self.calculate_industry_score(title, summary)
                        
                        papers.append({
                            'id': arxiv_id,
                            'arxiv_id': arxiv_id,
                            'title': title,
                            'summary': summary,
                            'link': link,
                            'category': category,
                            'published': published,
                            'industry_score': industry_score,
                            'type': 'paper'
                        })
                        
                        self.collected_ids.add(arxiv_id)
                        count += 1
                    
                    print(f"✅ 新增 {count} 篇")
                else:
                    print(f"❌ ({response.status_code})")
            except Exception as e:
                print(f"❌ {e}")
        
        # 按工业落地分数和发布时间排序
        papers.sort(key=lambda x: (x.get('industry_score', 0), x.get('published', '')), reverse=True)
        
        # 限制数量
        papers = papers[:self.max_papers]
        
        print(f"\n✅ 共采集 {len(papers)} 篇论文（去重后）")
        
        return papers
    
    def save_papers(self, papers: list):
        """保存论文数据"""
        # 保存到今日数据文件
        data_file = self.base_dir / "daily_data" / f"{self.today}.json"
        
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                'date': self.today,
                'daily_pick': [],
                'hot_articles': [],
                'github_projects': [],
                'arxiv_papers': [],
                'conferences': []
            }
        
        # 更新论文列表
        data['arxiv_papers'] = papers
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存到: {data_file}")
        
        # 更新缓存
        cache_file = self.cache_dir / "arxiv_papers.json"
        cache_data = {'items': papers, 'last_update': self.today}
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def run(self):
        """执行采集"""
        papers = self.collect_papers()
        
        if papers:
            self.save_papers(papers)
            
            # 显示工业落地分数最高的论文
            print(f"\n📊 工业落地相关性最高的论文:")
            for i, p in enumerate(papers[:5], 1):
                score = p.get('industry_score', 0)
                print(f"  {i}. [{score}⭐] {p.get('title', '')[:50]}...")
        
        return papers


if __name__ == "__main__":
    collector = ArxivCollector()
    collector.run()
