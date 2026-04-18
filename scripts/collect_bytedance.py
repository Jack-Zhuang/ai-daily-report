#!/usr/bin/env python3
"""
字节跳动技术内容采集脚本
尝试多种方式获取字节跳动技术文章
"""

import json
import urllib.request
import re
from pathlib import Path
from datetime import datetime

class ByteDanceCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
    
    def collect_from_juejin(self, keyword: str = "字节跳动", max_pages: int = 2) -> list:
        """从掘金采集字节跳动相关文章"""
        articles = []
        
        print(f"📡 从掘金采集: {keyword}")
        
        for page in range(1, max_pages + 1):
            try:
                # 掘金 API
                url = f"https://api.juejin.cn/recommend_api/v1/article/recommend_cate_feed"
                
                data = {
                    "id_type": 2,
                    "sort_type": 200,
                    "cate_id": "6809637773935378440",  # 后端分类
                    "cursor": f"{(page-1)*20}",
                    "limit": 20
                }
                
                req = urllib.request.Request(
                    url,
                    data=json.dumps(data).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'Mozilla/5.0'
                    }
                )
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    result = json.loads(response.read().decode('utf-8'))
                
                items = result.get('data', [])
                
                for item in items:
                    article_data = item.get('article_info', {})
                    title = article_data.get('title', '')
                    
                    # 过滤字节跳动相关
                    if keyword in title or '字节' in title or '抖音' in title or 'TikTok' in title:
                        articles.append({
                            'title': title,
                            'cn_title': title,
                            'link': f"https://juejin.cn/post/{article_data.get('article_id', '')}",
                            'summary': article_data.get('brief_content', '')[:200],
                            'cn_summary': article_data.get('brief_content', '')[:200],
                            'published': datetime.now().strftime('%Y-%m-%d'),
                            'source': f'掘金-{keyword}',
                            'type': 'article'
                        })
                
                print(f"  第{page}页: 获取 {len(items)} 篇，筛选 {len([a for a in articles if a.get('source', '').endswith(keyword)])} 篇")
                
            except Exception as e:
                print(f"  第{page}页失败: {e}")
                break
        
        return articles
    
    def collect_from_official(self) -> list:
        """从字节跳动技术官网采集"""
        articles = []
        
        print("📡 从字节跳动技术官网采集")
        
        try:
            # 字节跳动技术团队官网
            url = "https://bytedance.feishu.cn/wiki/wikcnN5XrAGI8YsEabgJzKQMp7f"
            
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8')
            
            # 提取文章标题和链接
            # 这里需要根据实际页面结构解析
            print(f"  获取页面成功，长度: {len(content)}")
            
            # 简单提取标题
            titles = re.findall(r'<title>([^<]+)</title>', content)
            print(f"  找到标题: {titles[:3]}")
            
        except Exception as e:
            print(f"  失败: {e}")
        
        return articles
    
    def run(self) -> list:
        """运行采集"""
        print("="*50)
        print("📚 字节跳动技术内容采集")
        print("="*50)
        
        all_articles = []
        
        # 方式1: 掘金
        articles = self.collect_from_juejin("字节跳动")
        all_articles.extend(articles)
        
        articles = self.collect_from_juejin("推荐算法")
        all_articles.extend(articles)
        
        # 方式2: 官网
        # articles = self.collect_from_official()
        # all_articles.extend(articles)
        
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
            output_file = self.cache_dir / "bytedance_articles.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(unique, f, ensure_ascii=False, indent=2)
            print(f"保存到: {output_file}")
        
        return unique


if __name__ == "__main__":
    collector = ByteDanceCollector()
    collector.run()
