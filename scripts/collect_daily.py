#!/usr/bin/env python3
"""
AI推荐日报 - 每日内容采集脚本
确保采集最新、最相关的内容
"""

import json
import requests
import re
from datetime import datetime, timedelta
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
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 关键词过滤
        self.keywords = {
            'rec': ['recommend', 'recommendation', 'recsys', 'collaborative filtering', 'ctr', 'ranking'],
            'agent': ['agent', 'multi-agent', 'autonomous', 'tool use', 'planning'],
            'llm': ['llm', 'large language model', 'gpt', 'bert', 'transformer', 'chatgpt']
        }
    
    def is_relevant(self, title: str, summary: str = '') -> tuple:
        """检查内容是否相关"""
        text = (title + ' ' + summary).lower()
        
        for category, kws in self.keywords.items():
            for kw in kws:
                if kw in text:
                    return True, category
        
        return False, None
    
    def is_recent(self, published: str, max_days: int = 3) -> bool:
        """检查内容是否足够新"""
        if not published:
            return True  # 无时间信息，默认通过
        
        try:
            pub_date = datetime.strptime(published[:10], '%Y-%m-%d')
            days_ago = (datetime.now() - pub_date).days
            return days_ago <= max_days
        except:
            return True
    
    def collect_arxiv_papers(self) -> list:
        """采集最新的 arXiv 论文"""
        papers = []
        
        # arXiv API - 只获取最近3天的论文
        queries = [
            "cat:cs.IR AND (recommend OR recommendation)",
            "cat:cs.AI AND agent",
            "cat:cs.CL AND (LLM OR \"large language model\")",
        ]
        
        for query in queries:
            try:
                print(f"  采集: arXiv - {query[:30]}...")
                url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=20&sortBy=submittedDate&sortOrder=descending"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.content)
                    
                    ns = {'atom': 'http://www.w3.org/2005/Atom'}
                    
                    for entry in root.findall('atom:entry', ns):
                        title_elem = entry.find('atom:title', ns)
                        summary_elem = entry.find('atom:summary', ns)
                        link_elem = entry.find('atom:id', ns)
                        published_elem = entry.find('atom:published', ns)
                        
                        title = title_elem.text.strip() if title_elem is not None else ''
                        summary = summary_elem.text.strip()[:500] if summary_elem is not None else ''
                        link = link_elem.text if link_elem is not None else ''
                        published = published_elem.text[:10] if published_elem is not None else ''
                        
                        # 检查相关性和时效性
                        is_rel, category = self.is_relevant(title, summary)
                        is_rec = self.is_recent(published, max_days=3)
                        
                        if is_rel and is_rec:
                            # 提取 arXiv ID
                            id_match = re.search(r'(\d{4}\.\d{4,5})', link)
                            arxiv_id = id_match.group(1) if id_match else ''
                            
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
        
        print(f"  ✅ 采集到 {len(unique_papers)} 篇最新相关论文")
        return unique_papers
    
    def run(self):
        """执行采集"""
        print(f"{'='*50}")
        print(f"📝 AI推荐日报 - 内容采集")
        print(f"{'='*50}")
        print(f"日期: {self.today}")
        print(f"要求: 内容必须是最近3天内的\n")
        
        # 采集论文
        print("📡 采集最新 arXiv 论文...")
        papers = self.collect_arxiv_papers()
        
        # 保存数据
        data = {
            'date': self.today,
            'daily_pick': [],
            'hot_articles': [],
            'github_projects': [],
            'arxiv_papers': papers[:20],
            'stats': {
                'total_papers': len(papers[:20]),
                'total_projects': 0,
                'total_articles': 0,
                'total_pick': 0
            }
        }
        
        output_file = self.base_dir / "daily_data" / f"{self.today}.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*50}")
        print(f"✅ 采集完成！")
        print(f"   arXiv论文: {len(papers[:20])} 篇（最近3天内）")
        print(f"{'='*50}")
        
        return data


if __name__ == "__main__":
    collector = DailyCollector()
    collector.run()
