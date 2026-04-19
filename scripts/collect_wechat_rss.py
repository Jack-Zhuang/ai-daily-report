#!/usr/bin/env python3
"""
AI推荐日报 - 微信公众号RSS采集脚本
使用 wechat2rss 服务获取微信公众号文章
"""

import json
import requests
import hashlib
import time
import feedparser
from datetime import datetime
from pathlib import Path


class WechatRSSCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # 加载RSS配置
        config_file = self.base_dir / "config" / "wechat_rss_found.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.rss_sources = config.get('found_accounts', [])
        else:
            self.rss_sources = []
    
    def load_cache(self) -> dict:
        """加载缓存"""
        cache_file = self.cache_dir / "wechat_articles.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'items': [], 'last_update': ''}
    
    def save_cache(self, data: dict):
        """保存缓存"""
        cache_file = self.cache_dir / "wechat_articles.json"
        data['last_update'] = datetime.now().isoformat()
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def fetch_rss(self, rss_url: str, source_name: str) -> list:
        """获取单个RSS源的文章"""
        articles = []
        try:
            response = requests.get(rss_url, timeout=15)
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries[:15]:  # 每个源取最近15篇
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    summary = entry.get('summary', '')[:300] if entry.get('summary') else ''
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
                        'source': source_name,
                        'views': 0,
                        'likes': 0,
                        'type': 'article'
                    })
        except Exception as e:
            print(f"    ⚠️ {source_name}: {e}")
        
        return articles
    
    def collect_all(self) -> list:
        """采集所有RSS源的文章"""
        print(f"\n{'='*50}")
        print(f"📰 采集微信公众号RSS")
        print(f"{'='*50}\n")
        
        all_articles = []
        cache = self.load_cache()
        cached_links = {a['link'] for a in cache.get('items', [])}
        
        for source in self.rss_sources:
            name = source['name']
            rss_url = source['rss_url']
            keywords = source.get('keywords', [])
            
            print(f"  📰 {name}...", end=' ', flush=True)
            
            articles = self.fetch_rss(rss_url, name)
            
            # 关键词过滤
            filtered = []
            for article in articles:
                title = article.get('title', '').lower()
                summary = article.get('summary', '').lower()
                
                # 检查关键词匹配
                matched = any(kw.lower() in title or kw.lower() in summary for kw in keywords)
                
                if matched or not keywords:
                    # 分类
                    if '推荐' in title or 'recommend' in title:
                        article['category'] = 'rec'
                    elif 'agent' in title or '智能体' in title:
                        article['category'] = 'agent'
                    elif 'llm' in title or '大模型' in title or 'gpt' in title:
                        article['category'] = 'llm'
                    else:
                        article['category'] = 'industry'
                    
                    filtered.append(article)
            
            new_count = len([a for a in filtered if a['link'] not in cached_links])
            print(f"✅ {len(filtered)} 篇 (新 {new_count} 篇)")
            
            all_articles.extend(filtered)
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
        
        # 保存缓存
        self.save_cache({'items': unique[:200]})
        
        # 生成中文内容
        for article in unique:
            article['cn_title'] = article.get('title', '')[:25]
            article['cn_summary'] = article.get('summary', '')[:60]
        
        new_articles = [a for a in all_articles if a['link'] not in cached_links]
        print(f"\n✅ 采集完成: {len(new_articles)} 篇新文章，缓存共 {len(unique)} 篇")
        
        return unique[:30]


if __name__ == "__main__":
    collector = WechatRSSCollector()
    articles = collector.collect_all()
    
    print(f"\n最终文章数: {len(articles)}")
    for a in articles[:10]:
        print(f"  - [{a['source']}] {a['cn_title']}")
