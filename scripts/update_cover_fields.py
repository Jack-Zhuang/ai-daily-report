#!/usr/bin/env python3
"""
更新数据文件中的封面字段
根据已生成的封面文件，更新对应内容的 cover_image 字段
"""

import json
from pathlib import Path

base_dir = Path("/home/sandbox/.openclaw/workspace/ai_daily")
data_file = base_dir / "daily_data" / "2026-04-20.json"
covers_dir = base_dir / "covers"

with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

updated = 0

# 1. 更新 arXiv 论文
print("📄 更新 arXiv 论文封面...")
for paper in data.get('arxiv_papers', []):
    arxiv_id = paper.get('id') or paper.get('arxiv_id')
    if not arxiv_id:
        continue

    cover_name = f"paper_{arxiv_id}.jpg"
    cover_path = covers_dir / cover_name

    if cover_path.exists() and cover_path.stat().st_size > 10000:
        paper['cover_image'] = f"covers/{cover_name}"
        updated += 1

print(f"   更新: {updated} 条")

# 2. 更新每日精选
pick_updated = 0
print("\n📌 更新每日精选封面...")
for i, item in enumerate(data.get('daily_pick', []), 1):
    cover_name = f"pick_{i}.jpg"
    cover_path = covers_dir / cover_name

    if cover_path.exists() and cover_path.stat().st_size > 10000:
        item['cover_image'] = f"covers/{cover_name}"
        pick_updated += 1

print(f"   更新: {pick_updated} 条")

# 3. 更新热门文章
article_updated = 0
print("\n📰 更新热门文章封面...")
for i, item in enumerate(data.get('hot_articles', []), 1):
    cover_name = f"article_{i}.jpg"
    cover_path = covers_dir / cover_name

    if cover_path.exists() and cover_path.stat().st_size > 10000:
        item['cover_image'] = f"covers/{cover_name}"
        article_updated += 1

print(f"   更新: {article_updated} 条")

# 4. 更新 GitHub 项目
github_updated = 0
print("\n💻 更新 GitHub 项目封面...")
for i, item in enumerate(data.get('github_projects', []), 1):
    cover_name = f"github_{i}.jpg"
    cover_path = covers_dir / cover_name

    if cover_path.exists() and cover_path.stat().st_size > 10000:
        item['cover_image'] = f"covers/{cover_name}"
        github_updated += 1

print(f"   更新: {github_updated} 条")

# 保存数据
with open(data_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 总计更新: {updated + pick_updated + article_updated + github_updated} 条")
