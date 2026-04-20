#!/usr/bin/env python3
"""
AI推荐日报 - 热门文章采集脚本（简化版）
直接从可用的数据源采集，不依赖 RSSHub
"""

import json
import requests
import hashlib
import time
from datetime import datetime
from pathlib import Path
import re


class HotArticleCollector:
    """热门文章采集器"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.today = datetime.now().strftime("%Y-%m-%d")

        # 微信公众号 RSS 源（wechat2rss.xlab.app）
        self.wechat_sources = [
            {
                'name': '机器之心',
                'rss_url': 'https://wechat2rss.xlab.app/feed/51e92aad2728acdd1fda7314be32b16639353001.xml',
                'keywords': ['AI', '大模型', 'LLM', 'Agent', '智能体', 'GPT', 'Claude', '推荐', '算法']
            },
            {
                'name': '量子位',
                'rss_url': 'https://wechat2rss.xlab.app/feed/7131b577c61365cb47e81000738c10d872685908.xml',
                'keywords': ['AI', '大模型', 'LLM', 'Agent', '智能体', 'GPT', 'Claude', 'Qwen', 'DeepSeek']
            },
            {
                'name': '新智元',
                'rss_url': 'https://wechat2rss.xlab.app/feed/ede30346413ea70dbef5d485ea5cbb95cca446e7.xml',
                'keywords': ['AI', '大模型', 'LLM', 'Agent', '智能体', 'GPT', 'Claude']
            },
        ]

    def generate_id(self, title: str) -> str:
        """生成唯一 ID"""
        return hashlib.md5(title.encode()).hexdigest()[:12]

    def parse_rss(self, rss_url: str, source_name: str, keywords: list) -> list:
        """解析 RSS 源"""
        articles = []

        try:
            print(f"  📡 采集: {source_name}...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(rss_url, headers=headers, timeout=15)
            response.encoding = 'utf-8'

            # 解析 XML
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)

            # 查找所有 item
            for item in root.findall('.//item'):
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                pubDate = item.find('pubDate')

                if title is None:
                    continue

                title_text = title.text or ''
                desc_text = description.text if description is not None else ''

                # 检查关键词匹配
                matched = False
                for keyword in keywords:
                    if keyword.lower() in title_text.lower() or keyword.lower() in desc_text.lower():
                        matched = True
                        break

                if not matched:
                    continue

                article = {
                    'id': self.generate_id(title_text),
                    'title': title_text[:100],
                    'summary': desc_text[:300] if desc_text else '',
                    'link': link.text if link is not None else '',
                    'source': source_name,
                    'published': pubDate.text if pubDate is not None else self.today,
                    'category': 'wechat',
                    'collected_at': self.today
                }

                articles.append(article)

            print(f"     ✅ 采集到 {len(articles)} 篇文章")

        except Exception as e:
            print(f"     ❌ 采集失败: {e}")

        return articles

    def collect_all(self) -> list:
        """采集所有源"""
        print("\n" + "=" * 60)
        print("📰 采集热门文章")
        print("=" * 60 + "\n")

        all_articles = []

        for source in self.wechat_sources:
            articles = self.parse_rss(
                source['rss_url'],
                source['name'],
                source['keywords']
            )
            all_articles.extend(articles)
            time.sleep(1)  # 避免请求过快

        # 去重
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                unique_articles.append(article)

        # 按时间排序（最新的在前）
        unique_articles.sort(key=lambda x: x.get('published', ''), reverse=True)

        # 限制数量
        max_articles = 20
        unique_articles = unique_articles[:max_articles]

        print(f"\n📊 总计采集: {len(unique_articles)} 篇文章")

        return unique_articles

    def save_to_daily_data(self, articles: list):
        """保存到每日数据文件"""
        data_file = self.base_dir / "daily_data" / f"{self.today}.json"

        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                'date': self.today,
                'daily_pick': [],
                'articles': [],
                'hot_articles': [],
                'github_projects': [],
                'arxiv_papers': []
            }

        # 更新热门文章
        data['hot_articles'] = articles

        # 保存
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 已保存到: {data_file}")

    def run(self):
        """执行采集"""
        articles = self.collect_all()

        if articles:
            self.save_to_daily_data(articles)
            return True
        else:
            print("\n⚠️ 未采集到文章")
            return False


if __name__ == "__main__":
    collector = HotArticleCollector()
    collector.run()
