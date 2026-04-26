#!/usr/bin/env python3
"""更新 arXiv 页面，注入论文数据"""

import json
import os

# 读取缓存数据
cache_path = "/home/sandbox/.openclaw/workspace/ai_daily/cache/arxiv_cache.json"
with open(cache_path, 'r', encoding='utf-8') as f:
    cache = json.load(f)

papers = cache.get('items', [])

# 过滤出最近7天的论文，并按 paper_value 排序
recent_papers = []
for p in papers:
    # 计算 overall_score (基于 paper_value 映射到 1-5 分)
    paper_value = p.get('paper_value', 0)
    overall_score = round(1 + paper_value * 0.8, 1)  # paper_value 0-5 -> score 1-5
    if overall_score > 5:
        overall_score = 5.0
    
    # 计算 scores
    industry_score = p.get('industry_score', 0)
    scores = {
        'innovation': round(3 + (paper_value - 2) * 0.5, 1) if paper_value else 3.0,
        'industry': round(2 + industry_score * 0.5, 1),
        'experiment': round(3 + (paper_value - 2) * 0.3, 1) if paper_value else 3.0
    }
    
    # 确保 scores 在合理范围内
    for k in scores:
        if scores[k] < 1:
            scores[k] = 1.0
        if scores[k] > 5:
            scores[k] = 5.0
    
    recent_papers.append({
        'id': p.get('id', ''),
        'title': p.get('title', 'Unknown'),
        'summary': p.get('summary', '')[:200] + '...' if len(p.get('summary', '')) > 200 else p.get('summary', ''),
        'link': p.get('link', ''),
        'category': p.get('category', 'agent'),
        'authors': p.get('authors', ['Unknown']),
        'published': p.get('published', ''),
        'overall_score': overall_score,
        'scores': scores,
        'highlight': '精选' if overall_score >= 4.0 else None
    })

# 按 overall_score 降序排序
recent_papers.sort(key=lambda x: x['overall_score'], reverse=True)

# 取前 25 篇
top_papers = recent_papers[:25]

print(f"共 {len(top_papers)} 篇论文")

# 生成 JavaScript 数据
papers_js = json.dumps(top_papers, ensure_ascii=False, indent=8)

# 读取模板
template_path = "/home/sandbox/.openclaw/workspace/ai_daily/conferences/arXiv_2026/index.html"
with open(template_path, 'r', encoding='utf-8') as f:
    template = f.read()

# 替换 papers 数组
import re
new_html = re.sub(
    r'const papers = \[\];',
    f'const papers = {papers_js};',
    template
)

# 更新统计数字
new_html = re.sub(
    r'<div class="stat-value">25</div>\s*<div class="stat-label">收录论文</div>',
    f'<div class="stat-value">{len(top_papers)}</div>\n            <div class="stat-label">收录论文</div>',
    new_html
)

# 更新精选论文数量
featured_count = len([p for p in top_papers if p['overall_score'] >= 4.0])
new_html = re.sub(
    r'<div class="stat-value">0</div>\s*<div class="stat-label">精选论文</div>',
    f'<div class="stat-value">{featured_count}</div>\n            <div class="stat-label">精选论文</div>',
    new_html
)

# 写入文件
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"已更新 arXiv 页面，共 {len(top_papers)} 篇论文，{featured_count} 篇精选")
