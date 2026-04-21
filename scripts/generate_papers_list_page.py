#!/usr/bin/env python3
"""
生成论文列表页面
"""

import json
from pathlib import Path
from datetime import datetime

def generate_papers_page():
    base_dir = Path(__file__).parent.parent
    data_file = base_dir / "daily_data" / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    
    if not data_file.exists():
        print("❌ 数据文件不存在")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    papers = data.get('arxiv_papers', [])
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arXiv 论文 - AI推荐日报 {date}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #1e293b; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; margin-bottom: 30px; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .back-link {{ display: inline-block; margin-top: 15px; color: white; text-decoration: none; }}
        .back-link:hover {{ text-decoration: underline; }}
        .papers-list {{ display: flex; flex-direction: column; gap: 16px; }}
        .paper-card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .paper-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }}
        .paper-title {{ font-size: 16px; font-weight: 600; line-height: 1.4; flex: 1; }}
        .paper-category {{ background: rgba(102,126,234,0.1); color: #667eea; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; white-space: nowrap; margin-left: 12px; }}
        .paper-summary {{ font-size: 14px; color: #64748b; line-height: 1.6; margin-bottom: 12px; }}
        .paper-meta {{ display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #94a3b8; }}
        .paper-id {{ font-family: monospace; }}
        .paper-links {{ display: flex; gap: 12px; }}
        .paper-link {{ color: #667eea; text-decoration: none; font-weight: 500; }}
        .paper-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-file-alt"></i> arXiv 论文</h1>
        <p>共 {len(papers)} 篇论文 · {date}</p>
        <a href="index.html" class="back-link"><i class="fas fa-arrow-left"></i> 返回首页</a>
    </div>
    
    <div class="container">
        <div class="papers-list">
'''
    
    for i, paper in enumerate(papers, 1):
        title = paper.get('cn_title', paper.get('title', '未知标题'))
        summary = paper.get('cn_summary', paper.get('summary', '暂无摘要'))[:200]
        arxiv_id = paper.get('arxiv_id', paper.get('id', ''))
        category = paper.get('category', 'other')
        link = paper.get('link', f'http://arxiv.org/abs/{arxiv_id}')
        published = paper.get('published', '')
        
        # 解读页面链接
        paper_id = arxiv_id.replace('/', '_').replace('.', '_')
        insight_url = f'docs/insights/{date}_{paper_id}.html'
        
        html += f'''
            <div class="paper-card">
                <div class="paper-header">
                    <div class="paper-title">{title}</div>
                    <span class="paper-category">{category}</span>
                </div>
                <div class="paper-summary">{summary}</div>
                <div class="paper-meta">
                    <span class="paper-id"><i class="fas fa-hashtag"></i> {arxiv_id} · {published}</span>
                    <div class="paper-links">
                        <a href="{link}" target="_blank" class="paper-link"><i class="fas fa-external-link-alt"></i> 原文</a>
                        <a href="{insight_url}" class="paper-link"><i class="fas fa-book-open"></i> 解读</a>
                    </div>
                </div>
            </div>
'''
    
    html += '''
        </div>
    </div>
</body>
</html>
'''
    
    output_file = base_dir / "papers.html"
    output_file.write_text(html, encoding='utf-8')
    print(f"✅ 已生成: {output_file}")

if __name__ == "__main__":
    generate_papers_page()
