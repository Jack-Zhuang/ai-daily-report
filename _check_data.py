#!/usr/bin/env python3
import json
from pathlib import Path

data_file = Path(__file__).parent / "daily_data" / "2026-07-20.json"
if not data_file.exists():
    print("ERROR: data file not found")
    exit(1)

data = json.loads(data_file.read_text(encoding="utf-8"))
print("Keys:", list(data.keys()))
papers = data.get("arxiv_papers", [])
print(f"Papers: {len(papers)}")
if papers:
    print(f"First title: {papers[0].get('title','N/A')[:100]}")
has_summary = sum(1 for p in papers if p.get("cn_summary") and len(p.get("cn_summary","")) > 30)
print(f"Papers with summaries: {has_summary}/{len(papers)}")

# Also check articles and github
articles = data.get("articles", data.get("hot_articles", []))
print(f"Articles: {len(articles)}")
github = data.get("github_projects", data.get("github_trending", []))
print(f"GitHub projects: {len(github)}")
