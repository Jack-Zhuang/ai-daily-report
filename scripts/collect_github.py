#!/usr/bin/env python3
"""
AI推荐日报 - GitHub Trending 采集脚本
采集 GitHub 上推荐系统、AI Agent、LLM 相关的热门项目
优先使用 GitHub Trending 页面获取增长最快的项目
"""

import requests
import json
import time
import re
from datetime import datetime
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class GitHubCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.data_dir = self.base_dir / "daily_data"
        self.data_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # GitHub API 配置
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # 搜索关键词配置
        self.search_queries = [
            # 推荐系统
            {"query": "recommendation system", "language": "python", "label": "rec"},
            {"query": "recommender system", "language": "python", "label": "rec"},
            # AI Agent
            {"query": "AI agent framework", "language": "python", "label": "agent"},
            {"query": "LLM agent", "language": "python", "label": "agent"},
            # LLM
            {"query": "large language model", "language": "python", "label": "llm"},
            {"query": "RAG retrieval augmented", "language": "python", "label": "llm"},
        ]
    
    def get_trending_from_web(self, since: str = "daily") -> list:
        """从 GitHub Trending 页面获取热门项目（按增长排序）"""
        repos = []
        
        if BeautifulSoup is None:
            print("  ⚠️ BeautifulSoup 未安装，跳过 Trending 页面")
            return []
        
        try:
            url = f"https://github.com/trending?since={since}"
            print(f"  🌐 获取 GitHub Trending ({since})...", end=" ", flush=True)
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('article.Box-row')
            
            for i, article in enumerate(articles[:25]):
                try:
                    h2 = article.select_one('h2 a')
                    if not h2:
                        continue
                    name = h2.get('href', '').strip('/')
                    
                    desc_elem = article.select_one('p.col-9')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    lang_elem = article.select_one('[itemprop="programmingLanguage"]')
                    language = lang_elem.get_text(strip=True) if lang_elem else ""
                    
                    stars_elem = article.select_one('a[href$="/stargazers"]')
                    stars_text = stars_elem.get_text(strip=True) if stars_elem else "0"
                    stars = int(stars_text.replace(',', '')) if stars_text else 0
                    
                    growth_elem = article.select_one('span.float-sm-right')
                    growth_text = growth_elem.get_text(strip=True) if growth_elem else ""
                    growth_match = re.search(r'([\d,]+)\s*stars', growth_text)
                    growth = int(growth_match.group(1).replace(',', '')) if growth_match else 0
                    
                    repos.append({
                        "id": f"trending-{i}",
                        "name": name,
                        "title": name.split('/')[-1] if '/' in name else name,
                        "description": description,
                        "link": f"https://github.com/{name}",
                        "stars": stars,
                        "forks": 0,
                        "language": language,
                        "category": "trending",
                        "published": self.today,
                        "type": "github",
                        "growth": growth,
                        "growth_rate": round(growth / stars * 100, 2) if stars > 0 else 0,
                        "topics": []
                    })
                except Exception:
                    continue
            
            print(f"✅ 找到 {len(repos)} 个")
            
        except Exception as e:
            print(f"❌ {e}")
        
        return repos
    
    def search_repos(self, query: str, language: str, label: str, max_results: int = 3) -> list:
        """搜索 GitHub 仓库"""
        repos = []
        
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                "q": f"{query} language:{language}",
                "sort": "stars",
                "order": "desc",
                "per_page": max_results
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get("items", []):
                    repos.append({
                        "id": str(item.get("id", "")),
                        "name": item.get("full_name", ""),
                        "title": item.get("name", ""),
                        "description": item.get("description", "") or "",
                        "link": item.get("html_url", ""),
                        "stars": item.get("stargazers_count", 0),
                        "forks": item.get("forks_count", 0),
                        "language": item.get("language", ""),
                        "category": label,
                        "published": item.get("pushed_at", "")[:10] if item.get("pushed_at") else self.today,
                        "type": "github",
                        "growth": 0,
                        "growth_rate": 0,
                        "topics": item.get("topics", [])
                    })
        except Exception as e:
            print(f"    ⚠️ 搜索失败: {e}")
        
        return repos
    
    def get_trending_repos(self) -> list:
        """获取热门项目 - 优先使用 GitHub Trending 页面"""
        all_repos = []
        seen_names = set()
        
        print(f"\n{'='*50}")
        print(f"💻 采集 GitHub 热门项目")
        print(f"{'='*50}\n")
        
        # 1. 先尝试从 GitHub Trending 页面获取
        trending_repos = self.get_trending_from_web(since="daily")
        
        if trending_repos:
            for repo in trending_repos:
                if repo["name"] not in seen_names:
                    seen_names.add(repo["name"])
                    all_repos.append(repo)
            
            print(f"  📊 从 Trending 获取 {len(trending_repos)} 个项目")
        
        # 2. 如果 Trending 获取失败或不足，使用 API 搜索补充
        if len(all_repos) < 15:
            print(f"\n  📡 使用 API 搜索补充...")
            
            for search_config in self.search_queries:
                if len(all_repos) >= 20:
                    break
                    
                query = search_config["query"]
                language = search_config["language"]
                label = search_config["label"]
                
                print(f"  🔍 搜索: {query} ({label})...", end=" ", flush=True)
                
                repos = self.search_repos(query, language, label, max_results=3)
                
                new_repos = []
                for repo in repos:
                    if repo["name"] not in seen_names:
                        seen_names.add(repo["name"])
                        new_repos.append(repo)
                
                if new_repos:
                    print(f"✅ 找到 {len(new_repos)} 个")
                    all_repos.extend(new_repos)
                else:
                    print("❌")
                
                time.sleep(0.5)
        
        # 按增长排序（优先），其次按星数
        all_repos.sort(key=lambda x: (x.get('growth', 0), x.get('stars', 0)), reverse=True)
        
        top_repos = all_repos[:20]
        
        print(f"\n✅ 共采集 {len(top_repos)} 个热门项目")
        
        return top_repos
    
    def save_to_daily_data(self, repos: list):
        """保存到今日数据文件"""
        data_file = self.data_dir / f"{self.today}.json"
        
        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {
                "date": self.today,
                "daily_pick": [],
                "articles": [],
                "hot_articles": [],
                "github_projects": [],
                "arxiv_papers": [],
                "conferences": []
            }
        
        data["github_projects"] = repos
        
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 更新缓存
        cache_file = self.cache_dir / "github_cache.json"
        cache_data = {'items': repos, 'date': self.today}
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存到: {data_file}")
    
    def run(self):
        """执行采集"""
        repos = self.get_trending_repos()
        
        if repos:
            self.save_to_daily_data(repos)
            
            print(f"\n📊 热门项目预览:")
            for i, repo in enumerate(repos[:5], 1):
                growth_str = f"+{repo.get('growth', 0)}" if repo.get('growth', 0) > 0 else ""
                print(f"  {i}. [{repo.get('category', '?')}] {repo.get('name', '')}")
                print(f"     ⭐ {repo.get('stars', 0):,} {growth_str} | {repo.get('description', '')[:50]}...")
        
        return repos


if __name__ == "__main__":
    collector = GitHubCollector()
    collector.run()
