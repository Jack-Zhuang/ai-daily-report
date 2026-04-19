#!/usr/bin/env python3
"""
AI推荐日报 - 顶会论文采集脚本
一次性采集各大顶会的推荐系统、AI Agent、LLM 相关论文
支持：KDD、WSDM、RecSys、SIGIR、WWW、CIKM、NeurIPS、ICML、ICLR
"""

import json
import requests
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class ConferencePaperCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "conference_papers"
        self.data_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # 顶会配置
        self.conferences = {
            # 推荐系统相关
            "RecSys": {
                "year": 2025,
                "focus": ["recommendation", "recsys", "personalization"],
                "source": "recsys.org"
            },
            "WSDM": {
                "year": 2025,
                "focus": ["web search", "data mining", "recommendation"],
                "source": "wsdm.org"
            },
            # 数据挖掘与信息检索
            "KDD": {
                "year": 2025,
                "focus": ["data mining", "knowledge discovery", "recommendation"],
                "source": "kdd.org"
            },
            "SIGIR": {
                "year": 2025,
                "focus": ["information retrieval", "search", "recommendation"],
                "source": "sigir.org"
            },
            "WWW": {
                "year": 2025,
                "focus": ["web", "social network", "recommendation"],
                "source": "www2025.org"
            },
            "CIKM": {
                "year": 2025,
                "focus": ["information management", "knowledge management"],
                "source": "cikm.org"
            },
            # 机器学习
            "NeurIPS": {
                "year": 2024,
                "focus": ["neural networks", "deep learning", "LLM", "agent"],
                "source": "neurips.cc"
            },
            "ICML": {
                "year": 2025,
                "focus": ["machine learning", "deep learning"],
                "source": "icml.cc"
            },
            "ICLR": {
                "year": 2025,
                "focus": ["representation learning", "deep learning"],
                "source": "iclr.cc"
            }
        }
        
        # 关键词过滤
        self.target_keywords = [
            # 推荐系统
            "recommendation", "recommender", "recsys", "collaborative filtering",
            "ctr", "ranking", "personalization", "user modeling",
            # AI Agent
            "agent", "multi-agent", "autonomous", "tool use", "planning",
            "reasoning", "action", "task automation",
            # LLM
            "llm", "large language model", "gpt", "bert", "transformer",
            "rag", "retrieval augmented", "prompt", "fine-tuning"
        ]
        
        # 工业界关键词
        self.industry_keywords = [
            "production", "industrial", "deploy", "deployment", "online",
            "real-time", "realtime", "scalable", "large-scale", "distributed",
            "A/B test", "experiment", "application", "system", "framework",
            "efficiency", "optimization", "serving", "inference",
            "alibaba", "amazon", "google", "meta", "microsoft", "netflix",
            "bytedance", "tencent", "meituan", "baidu", "jd", "kuaishou"
        ]
    
    def is_relevant(self, title: str) -> bool:
        """检查论文是否相关"""
        title_lower = title.lower()
        for kw in self.target_keywords:
            if kw in title_lower:
                return True
        return False
    
    def categorize_paper(self, title: str) -> str:
        """对论文进行分类"""
        title_lower = title.lower()
        
        if any(kw in title_lower for kw in ["recommend", "recsys", "collaborative", "ctr", "ranking", "personalization"]):
            return "rec"
        elif any(kw in title_lower for kw in ["agent", "multi-agent", "autonomous", "tool use", "planning"]):
            return "agent"
        elif any(kw in title_lower for kw in ["llm", "language model", "gpt", "bert", "transformer", "rag"]):
            return "llm"
        else:
            return "other"
    
    def is_industry_paper(self, title: str, summary: str = "") -> bool:
        """判断是否为工业界论文"""
        text = (title + ' ' + summary).lower()
        
        for kw in self.industry_keywords:
            if kw.lower() in text:
                return True
        
        return False
    
    def calculate_industry_score(self, title: str, summary: str = "") -> int:
        """计算工业相关性分数"""
        text = (title + ' ' + summary).lower()
        score = 0
        
        for kw in self.industry_keywords:
            if kw.lower() in text:
                score += 1
        
        return min(score, 5)
    
    def fetch_from_arxiv(self, conference: str, year: int) -> List[Dict]:
        """从 arXiv 获取会议相关论文"""
        papers = []
        
        try:
            # 使用 arXiv API 搜索会议相关论文
            query = f"all:{conference.lower()}"
            url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=50&sortBy=submittedDate"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', ns):
                    title_elem = entry.find('atom:title', ns)
                    summary_elem = entry.find('atom:summary', ns)
                    link_elem = entry.find('atom:id', ns)
                    
                    title = title_elem.text.strip() if title_elem is not None else ''
                    summary = summary_elem.text.strip()[:500] if summary_elem is not None else ''
                    link = link_elem.text if link_elem is not None else ''
                    
                    if not self.is_relevant(title):
                        continue
                    
                    # 提取 arXiv ID
                    id_match = re.search(r'(\d{4}\.\d{4,5})', link)
                    arxiv_id = id_match.group(1) if id_match else ''
                    
                    papers.append({
                        'id': arxiv_id,
                        'arxiv_id': arxiv_id,
                        'title': title,
                        'summary': summary,
                        'link': link,
                        'conference': conference,
                        'year': year,
                        'category': self.categorize_paper(title),
                        'is_industry': self.is_industry_paper(title, summary),
                        'industry_score': self.calculate_industry_score(title, summary),
                        'type': 'conference_paper'
                    })
        except Exception as e:
            print(f"    ⚠️ arXiv 查询失败: {e}")
        
        return papers
    
    def fetch_from_openreview(self, conference: str, year: int) -> List[Dict]:
        """从 OpenReview 获取会议论文"""
        papers = []
        
        try:
            # OpenReview API
            # NeurIPS, ICLR, ICML 等会议使用 OpenReview
            conf_mapping = {
                "NeurIPS": f"NeurIPS.cc/{year}/Conference",
                "ICLR": f"ICLR.cc/{year}/Conference",
                "ICML": f"ICML.cc/{year}/Conference"
            }
            
            if conference not in conf_mapping:
                return papers
            
            # OpenReview API 查询
            url = "https://api.openreview.net/notes"
            params = {
                "content.venueid": conf_mapping[conference],
                "limit": 100
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                for note in data.get('notes', []):
                    content = note.get('content', {})
                    title = content.get('title', '')
                    abstract = content.get('abstract', '')[:500]
                    
                    if not self.is_relevant(title):
                        continue
                    
                    papers.append({
                        'id': note.get('id', ''),
                        'arxiv_id': '',
                        'title': title,
                        'summary': abstract,
                        'link': f"https://openreview.net/forum?id={note.get('id', '')}",
                        'conference': conference,
                        'year': year,
                        'category': self.categorize_paper(title),
                        'is_industry': self.is_industry_paper(title, abstract),
                        'industry_score': self.calculate_industry_score(title, abstract),
                        'type': 'conference_paper'
                    })
        except Exception as e:
            print(f"    ⚠️ OpenReview 查询失败: {e}")
        
        return papers
    
    def fetch_from_semantic_scholar(self, conference: str, year: int) -> List[Dict]:
        """从 Semantic Scholar 获取会议论文"""
        papers = []
        
        try:
            # Semantic Scholar API
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": f"{conference} {year}",
                "year": f"{year}-{year}",
                "limit": 50,
                "fields": "title,abstract,url,year,venue"
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('data', []):
                    title = item.get('title', '')
                    abstract = item.get('abstract', '')[:500] if item.get('abstract') else ''
                    
                    if not self.is_relevant(title):
                        continue
                    
                    papers.append({
                        'id': item.get('paperId', ''),
                        'arxiv_id': '',
                        'title': title,
                        'summary': abstract,
                        'link': item.get('url', ''),
                        'conference': conference,
                        'year': year,
                        'category': self.categorize_paper(title),
                        'is_industry': self.is_industry_paper(title, abstract),
                        'industry_score': self.calculate_industry_score(title, abstract),
                        'type': 'conference_paper'
                    })
        except Exception as e:
            print(f"    ⚠️ Semantic Scholar 查询失败: {e}")
        
        return papers
    
    def collect_conference_papers(self, conference: str, config: Dict) -> List[Dict]:
        """采集单个会议的论文"""
        papers = []
        year = config['year']
        
        print(f"\n  📚 {conference} {year}")
        
        # 尝试多个数据源
        # 1. OpenReview（NeurIPS, ICLR, ICML）
        if conference in ["NeurIPS", "ICLR", "ICML"]:
            papers.extend(self.fetch_from_openreview(conference, year))
        
        # 2. Semantic Scholar
        papers.extend(self.fetch_from_semantic_scholar(conference, year))
        
        # 3. arXiv（备用）
        if len(papers) < 10:
            papers.extend(self.fetch_from_arxiv(conference, year))
        
        # 去重
        seen_titles = set()
        unique_papers = []
        for p in papers:
            title_key = p['title'][:50].lower()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_papers.append(p)
        
        print(f"    ✅ 找到 {len(unique_papers)} 篇相关论文")
        
        return unique_papers
    
    def run(self):
        """执行采集"""
        print(f"\n{'='*60}")
        print(f"🎓 顶会论文采集")
        print(f"{'='*60}")
        
        all_papers = {}
        
        for conference, config in self.conferences.items():
            papers = self.collect_conference_papers(conference, config)
            if papers:
                all_papers[conference] = papers
        
        # 保存数据
        output_file = self.data_dir / "all_conferences.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'last_update': self.today,
                'conferences': all_papers
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✅ 采集完成！")
        print(f"{'='*60}")
        
        # 统计
        total = sum(len(papers) for papers in all_papers.values())
        industry_count = sum(1 for conf_papers in all_papers.values() for p in conf_papers if p.get('is_industry'))
        
        print(f"\n{'='*60}")
        print(f"✅ 采集完成！")
        print(f"{'='*60}")
        
        print(f"\n📊 统计:")
        for conf, papers in all_papers.items():
            conf_industry = sum(1 for p in papers if p.get('is_industry'))
            print(f"  - {conf}: {len(papers)} 篇 (工业界: {conf_industry} 篇)")
        print(f"\n  总计: {total} 篇")
        print(f"  工业界相关: {industry_count} 篇 ({industry_count*100//total if total > 0 else 0}%)")
        print(f"\n📁 保存到: {output_file}")
        
        return all_papers


if __name__ == "__main__":
    collector = ConferencePaperCollector()
    collector.run()
