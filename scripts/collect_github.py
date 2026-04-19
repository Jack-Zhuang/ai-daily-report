#!/usr/bin/env python3
"""
AI推荐日报 - GitHub Trending 采集脚本
采集 GitHub 上推荐系统、AI Agent、LLM 相关的热门项目
"""

import requests
import json
import time
import re
from datetime import datetime
from pathlib import Path


class GitHubCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # GitHub API 配置
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Daily-Report"
        }
        
        # 搜索关键词配置
        self.search_queries = [
            # 推荐系统
            {"query": "recommendation system", "language": "python", "label": "rec"},
            {"query": "recommender system", "language": "python", "label": "rec"},
            {"query": "collaborative filtering", "language": "python", "label": "rec"},
            {"query": "ctr prediction", "language": "python", "label": "rec"},
            # AI Agent
            {"query": "AI agent framework", "language": "python", "label": "agent"},
            {"query": "LLM agent", "language": "python", "label": "agent"},
            {"query": "autonomous agent", "language": "python", "label": "agent"},
            {"query": "multi-agent system", "language": "python", "label": "agent"},
            # LLM
            {"query": "large language model", "language": "python", "label": "llm"},
            {"query": "RAG retrieval augmented", "language": "python", "label": "llm"},
            {"query": "text embedding", "language": "python", "label": "llm"},
        ]
    
    def search_repos(self, query: str, language: str, label: str, max_results: int = 5) -> list:
        """搜索 GitHub 仓库"""
        repos = []
        
        try:
            # 使用 GitHub Search API
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
                        "type": "github"
                    })
        except Exception as e:
            print(f"    ⚠️ 搜索失败: {e}")
        
        return repos
    
    def get_trending_repos(self) -> list:
        """获取热门项目"""
        all_repos = []
        seen_names = set()
        
        print(f"\n{'='*50}")
        print(f"💻 采集 GitHub 热门项目")
        print(f"{'='*50}\n")
        
        for search_config in self.search_queries:
            query = search_config["query"]
            language = search_config["language"]
            label = search_config["label"]
            
            print(f"  🔍 搜索: {query} ({label})...", end=" ", flush=True)
            
            repos = self.search_repos(query, language, label, max_results=5)
            
            # 去重
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
            
            time.sleep(0.5)  # 避免 API 限流
        
        # 按星数排序
        all_repos.sort(key=lambda x: x.get("stars", 0), reverse=True)
        
        # 取前 20 个
        top_repos = all_repos[:20]
        
        print(f"\n✅ 共采集 {len(top_repos)} 个热门项目")
        
        return top_repos
    
    def save_to_daily_data(self, repos: list):
        """保存到今日数据文件"""
        data_file = self.base_dir / "daily_data" / f"{self.today}.json"
        
        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {
                "date": self.today,
                "daily_pick": [],
                "hot_articles": [],
                "github_projects": [],
                "arxiv_papers": [],
                "conferences": []
            }
        
        # 更新 GitHub 项目
        data["github_projects"] = repos
        
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存到: {data_file}")
    
    def run(self):
        """执行采集"""
        repos = self.get_trending_repos()
        
        if repos:
            self.save_to_daily_data(repos)
            
            print(f"\n📊 热门项目预览:")
            for i, repo in enumerate(repos[:5], 1):
                print(f"  {i}. [{repo.get('category', '?')}] {repo.get('name', '')}")
                print(f"     ⭐ {repo.get('stars', 0)} | {repo.get('description', '')[:50]}...")
        
        return repos


if __name__ == "__main__":
    collector = GitHubCollector()
    collector.run()
