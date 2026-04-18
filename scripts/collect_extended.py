#!/usr/bin/env python3
"""
扩展数据源采集脚本
采集更多推荐系统、AI相关内容
"""

import json
import urllib.request
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from datetime import datetime

class ExtendedCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
    
    def collect_rss(self, name: str, url: str, keywords: list) -> list:
        """采集 RSS 源"""
        articles = []
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read()
            
            root = ET.fromstring(content)
            
            for item in root.findall('.//item'):
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                pubDate = item.find('pubDate')
                
                if title is not None:
                    title_text = title.text or ''
                    desc_text = description.text if description is not None else ''
                    
                    # 关键词过滤
                    text = (title_text + ' ' + desc_text).lower()
                    if any(kw.lower() in text for kw in keywords):
                        articles.append({
                            'title': title_text,
                            'cn_title': title_text,
                            'link': link.text if link is not None else '',
                            'summary': desc_text[:200],
                            'cn_summary': desc_text[:200],
                            'published': datetime.now().strftime('%Y-%m-%d'),
                            'source': name,
                            'type': 'article'
                        })
            
            print(f"  ✅ {name}: {len(articles)}篇")
            
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:50]}")
        
        return articles
    
    def run(self) -> list:
        """运行采集"""
        print("="*50)
        print("📚 扩展数据源采集")
        print("="*50)
        
        # 数据源配置
        sources = [
            # 微信公众号
            ("机器之心", "https://wechat2rss.xlab.app/feed/51e92aad2728acdd1fda7314be32b16639353001.xml", 
             ["AI", "大模型", "推荐", "算法", "LLM", "Agent"]),
            ("量子位", "https://wechat2rss.xlab.app/feed/7131b577c61365cb47e81000738c10d872685908.xml",
             ["AI", "大模型", "推荐", "算法"]),
            ("新智元", "https://wechat2rss.xlab.app/feed/ede30346413ea70dbef5d485ea5cbb95cca446e7.xml",
             ["AI", "大模型", "推荐", "算法"]),
            ("PaperWeekly", "https://wechat2rss.xlab.app/feed/3be891c2f4e526629ab055a297cc2cd6c1f0a563.xml",
             ["论文", "AI", "推荐", "算法"]),
            
            # 技术博客
            ("美团技术团队", "https://rsshub.rssforever.com/meituan/tech",
             ["推荐", "算法", "搜索", "广告", "AI", "大模型"]),
            
            # 技术媒体
            ("InfoQ", "https://rsshub.rssforever.com/infoq/recommend",
             ["AI", "推荐", "算法", "架构"]),
            ("36氪快讯", "https://rsshub.rssforever.com/36kr/newsflashes",
             ["AI", "大模型"]),
            ("IT之家热榜", "https://rsshub.rssforever.com/ithome/ranking/7days",
             ["AI", "大模型"]),
            ("开源中国资讯", "https://rsshub.rssforever.com/oschina/news",
             ["AI", "开源", "推荐"]),
            
            # 知乎
            ("知乎日报", "https://rsshub.rssforever.com/zhihu/daily",
             ["AI", "推荐", "算法"]),
        ]
        
        all_articles = []
        
        for name, url, keywords in sources:
            print(f"\n📡 采集 {name}...")
            articles = self.collect_rss(name, url, keywords)
            all_articles.extend(articles)
        
        # 去重
        seen = set()
        unique = []
        for a in all_articles:
            if a['title'] not in seen:
                seen.add(a['title'])
                unique.append(a)
        
        print(f"\n{'='*50}")
        print(f"✅ 采集完成: {len(unique)} 篇不重复文章")
        print(f"{'='*50}")
        
        # 保存
        if unique:
            output_file = self.cache_dir / "extended_articles.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(unique, f, ensure_ascii=False, indent=2)
            print(f"保存到: {output_file}")
            
            # 显示前5篇
            print("\n文章预览:")
            for i, a in enumerate(unique[:5]):
                print(f"  {i+1}. [{a['source']}] {a['title'][:40]}...")
        
        return unique


if __name__ == "__main__":
    collector = ExtendedCollector()
    collector.run()
