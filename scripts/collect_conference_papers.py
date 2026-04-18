#!/usr/bin/env python3
"""
AI推荐日报 - 顶会论文采集脚本
从 DBLP 和 arXiv 采集顶会论文
集成历史记录去重，确保不同天推送的内容不重复
"""

import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from datetime import datetime
import sys

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))
from history_manager import HistoryManager

class ConferencePaperCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.history_manager = HistoryManager(str(self.base_dir))
        
        # 顶会配置
        self.conferences = {
            "WSDM 2026": {
                "name": "WSDM 2026",
                "date": "2026年3月",
                "location": "德国汉诺威",
                "dblp": "wsdm",
                "year": 2026,
                "keywords": ["recommendation", "search", "data mining"]
            },
            "KDD 2025": {
                "name": "KDD 2025",
                "date": "2025年8月",
                "location": "加拿大多伦多",
                "dblp": "kdd",
                "year": 2025,
                "keywords": ["recommendation", "knowledge discovery"]
            },
            "RecSys 2025": {
                "name": "RecSys 2025",
                "date": "2025年9月",
                "location": "捷克布拉格",
                "dblp": "recsys",
                "year": 2025,
                "keywords": ["recommendation", "recommender"]
            },
            "WWW 2025": {
                "name": "WWW 2025",
                "date": "2025年4月",
                "location": "新加坡",
                "dblp": "www",
                "year": 2025,
                "keywords": ["web", "recommendation"]
            },
            "SIGIR 2025": {
                "name": "SIGIR 2025",
                "date": "2025年7月",
                "location": "意大利帕多瓦",
                "dblp": "sigir",
                "year": 2025,
                "keywords": ["information retrieval", "recommendation"]
            },
            "CIKM 2025": {
                "name": "CIKM 2025",
                "date": "2025年10月",
                "location": "待定",
                "dblp": "cikm",
                "year": 2025,
                "keywords": ["information", "knowledge"]
            }
        }
    
    def search_arxiv_for_conference(self, conf_name: str, keywords: list, max_results: int = 20) -> list:
        """从 arXiv 搜索会议相关论文（已去重）"""
        papers = []
        
        # 构建查询
        query_parts = [f'cat:cs.IR OR cat:cs.AI OR cat:cs.CL']
        keyword_query = ' OR '.join(keywords)
        
        base_url = "http://export.arxiv.org/api/query?"
        params = {
            'search_query': f"({query_parts[0]}) AND ({keyword_query})",
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        url = base_url + urllib.parse.urlencode(params)
        
        try:
            print(f"  搜索 arXiv: {conf_name}...")
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read()
            
            root = ET.fromstring(content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text.strip()
                summary = entry.find('atom:summary', ns).text.strip()[:500]
                link = entry.find('atom:id', ns).text
                published = entry.find('atom:published', ns).text[:10]
                
                id_match = re.search(r'(\d{4}\.\d{4,5})', link)
                arxiv_id = id_match.group(1) if id_match else ''
                
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns)
                    if name is not None:
                        authors.append(name.text)
                
                paper = {
                    'id': arxiv_id,
                    'arxiv_id': arxiv_id,
                    'title': title,
                    'summary': summary,
                    'link': link,
                    'published': published,
                    'authors': authors[:5],
                    'type': 'paper',
                    'conference': conf_name
                }
                
                # 检查是否已发布
                if not self.history_manager.is_published(paper, 'conference_papers', days=30):
                    papers.append(paper)
            
            print(f"    找到 {len(papers)} 篇（已去重）")
        
        except Exception as e:
            print(f"    搜索失败: {e}")
        
        return papers
    
    def collect_all(self) -> dict:
        """采集所有顶会论文"""
        print("="*50)
        print("📚 顶会论文采集（已去重）")
        print("="*50)
        
        result = {}
        
        for conf_key, conf_info in self.conferences.items():
            print(f"\n{conf_info['name']}:")
            
            papers = self.search_arxiv_for_conference(
                conf_info['name'],
                conf_info['keywords'],
                max_results=10
            )
            
            # 标记为已发布
            for paper in papers:
                self.history_manager.mark_published(paper, 'conference_papers')
            
            result[conf_key] = {
                'name': conf_info['name'],
                'date': conf_info['date'],
                'location': conf_info['location'],
                'total': len(papers),
                'papers': papers
            }
        
        # 保存
        output_file = self.cache_dir / "conference_papers.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*50}")
        print(f"✅ 采集完成！")
        print(f"   保存到: {output_file}")
        print(f"{'='*50}")
        
        # 统计
        total = sum(len(c['papers']) for c in result.values())
        print(f"\n统计:")
        for conf_key, conf in result.items():
            print(f"  {conf['name']}: {len(conf['papers'])}篇")
        print(f"  总计: {total}篇")
        
        # 显示历史记录统计
        stats = self.history_manager.get_stats()
        print(f"\n历史记录统计:")
        print(f"   顶会论文: {stats['conference_papers']}条")
        
        return result


if __name__ == "__main__":
    collector = ConferencePaperCollector()
    collector.collect_all()
