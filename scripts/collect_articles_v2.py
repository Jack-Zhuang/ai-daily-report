#!/usr/bin/env python3
"""
AI推荐日报 - 文章采集脚本（多源方案）
支持多种数据源，优先使用稳定的API
"""

import json
import requests
import hashlib
import time
import re
from datetime import datetime
from pathlib import Path

class ArticleCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # RSSHub镜像列表（按优先级排序）
        self.rsshub_mirrors = [
            'https://rsshub.rssforever.com',
            'https://rsshub.app',
            'https://rsshub.liumingye.cn',
        ]
        
        # 数据源配置
        self.sources = [
            # 技术博客（更稳定）
            {
                'name': '美团技术团队',
                'type': 'rsshub',
                'path': '/meituan/tech/home',
                'keywords': ['推荐', '算法', '机器学习', '深度学习']
            },
            {
                'name': '字节跳动技术团队',
                'type': 'rsshub',
                'path': '/bytedance/tech/home',
                'keywords': ['推荐', '算法', '机器学习']
            },
            # 知乎话题
            {
                'name': '知乎-推荐系统',
                'type': 'rsshub',
                'path': '/zhihu/topic/19554298',
                'keywords': ['推荐系统', '协同过滤', 'CTR']
            },
            {
                'name': '知乎-机器学习',
                'type': 'rsshub',
                'path': '/zhihu/topic/19559450',
                'keywords': ['机器学习', '深度学习', 'LLM']
            },
            # 微信公众号（通过RSSHub）
            {
                'name': '机器之心',
                'type': 'rsshub',
                'path': '/wechat/mp/msgalbum/机器之心',
                'keywords': ['推荐', 'LLM', 'Agent', 'AI']
            },
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
    
    def fetch_rss_with_retry(self, path: str, timeout: int = 10) -> list:
        """尝试多个RSSHub镜像获取RSS"""
        for mirror in self.rsshub_mirrors:
            url = f"{mirror}{path}"
            try:
                response = requests.get(url, timeout=timeout)
                if response.status_code == 200:
                    return self.parse_rss(response.text)
            except Exception as e:
                continue
        return []
    
    def parse_rss(self, rss_text: str) -> list:
        """解析RSS内容"""
        articles = []
        try:
            import feedparser
            feed = feedparser.parse(rss_text)
            
            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                link = entry.get('link', '')
                summary = entry.get('summary', '')[:200] if entry.get('summary') else ''
                published = entry.get('published', '')[:10] if entry.get('published') else self.today
                
                if not title or not link:
                    continue
                
                article_id = hashlib.md5(link.encode()).hexdigest()[:12]
                
                articles.append({
                    'id': article_id,
                    'title': title,
                    'summary': summary,
                    'link': link,
                    'published': published,
                    'views': 0,
                    'likes': 0,
                    'type': 'article'
                })
        except Exception as e:
            print(f"    ⚠️ RSS解析失败: {e}")
        
        return articles
    
    def fetch_from_source(self, source: dict) -> list:
        """从单个源获取文章"""
        articles = []
        name = source['name']
        keywords = source.get('keywords', [])
        
        print(f"  📰 {name}...", end=' ')
        
        if source['type'] == 'rsshub':
            raw_articles = self.fetch_rss_with_retry(source['path'])
            
            # 关键词过滤
            for article in raw_articles:
                title = article.get('title', '').lower()
                summary = article.get('summary', '').lower()
                
                # 检查关键词匹配
                matched = any(kw.lower() in title or kw.lower() in summary for kw in keywords)
                
                if matched or not keywords:  # 如果没有关键词限制，全部接受
                    article['source'] = name
                    
                    # 分类
                    if '推荐' in title or 'recommend' in title:
                        article['category'] = 'rec'
                    elif 'agent' in title or '智能体' in title:
                        article['category'] = 'agent'
                    elif 'llm' in title or '大模型' in title or 'gpt' in title:
                        article['category'] = 'llm'
                    else:
                        article['category'] = 'industry'
                    
                    articles.append(article)
            
            print(f"✅ {len(articles)} 篇")
        else:
            print("⚠️ 不支持的类型")
        
        return articles
    
    def collect_all_articles(self) -> list:
        """采集所有文章"""
        print(f"\n{'='*50}")
        print(f"📰 采集热门文章")
        print(f"{'='*50}\n")
        
        all_articles = []
        cache = self.load_cache('all')
        cached_links = {a['link'] for a in cache.get('items', [])}
        
        for source in self.sources:
            try:
                articles = self.fetch_from_source(source)
                for article in articles:
                    if article['link'] not in cached_links:
                        all_articles.append(article)
                time.sleep(0.5)  # 避免请求过快
            except Exception as e:
                print(f"    ❌ {source['name']}: {e}")
        
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
        
        # 保存缓存
        self.save_cache('all', {'items': unique[:100]})
        
        # 生成中文内容
        for article in unique:
            article['cn_title'] = article.get('title', '')[:25]
            article['cn_summary'] = article.get('summary', '')[:60]
        
        print(f"\n✅ 采集完成: {len(all_articles)} 篇新文章，缓存共 {len(unique)} 篇")
        return unique[:20]
    
    def get_fallback_articles(self) -> list:
        """获取备用文章（当RSS不可用时）"""
        return [
            {
                'id': 'fallback-1',
                'title': '深度学习在推荐系统中的最新进展',
                'summary': '本文综述了深度学习技术在推荐系统中的应用，包括序列推荐、图神经网络推荐等前沿方向。',
                'link': 'https://arxiv.org/list/cs.IR/recent',
                'source': 'arXiv',
                'published': self.today,
                'category': 'rec',
                'cn_title': '深度学习推荐系统进展',
                'cn_summary': '综述深度学习在推荐系统中的应用，包括序列推荐、图神经网络等。',
                'type': 'article'
            },
            {
                'id': 'fallback-2',
                'title': '大语言模型赋能推荐系统：机遇与挑战',
                'summary': '探讨LLM在推荐系统中的应用潜力，分析当前面临的挑战和未来研究方向。',
                'link': 'https://arxiv.org/list/cs.IR/recent',
                'source': 'arXiv',
                'published': self.today,
                'category': 'llm',
                'cn_title': 'LLM赋能推荐系统',
                'cn_summary': '探讨LLM在推荐系统中的应用潜力，分析挑战和未来方向。',
                'type': 'article'
            },
            {
                'id': 'fallback-3',
                'title': 'AI Agent在推荐场景的落地实践',
                'summary': '分享AI Agent技术在推荐系统中的实际应用案例，包括智能客服、个性化推荐等场景。',
                'link': 'https://arxiv.org/list/cs.IR/recent',
                'source': 'arXiv',
                'published': self.today,
                'category': 'agent',
                'cn_title': 'AI Agent推荐落地实践',
                'cn_summary': '分享AI Agent在推荐系统中的实际应用案例和经验。',
                'type': 'article'
            }
        ]


if __name__ == "__main__":
    collector = ArticleCollector()
    articles = collector.collect_all_articles()
    
    if not articles:
        print("\n使用备用文章...")
        articles = collector.get_fallback_articles()
    
    print(f"\n最终文章数: {len(articles)}")
    for a in articles[:5]:
        print(f"  - [{a['source']}] {a['cn_title']}")
