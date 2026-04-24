#!/usr/bin/env python3
"""
生成文章列表页面
"""

import json
from pathlib import Path
from datetime import datetime

def generate_articles_page():
    base_dir = Path(__file__).parent.parent
    
    # 查找最新的数据文件
    data_dir = base_dir / "daily_data"
    data_files = sorted(data_dir.glob("*.json"), reverse=True)
    
    if not data_files:
        print("❌ 没有找到数据文件")
        return
    
    data_file = data_files[0]
    print(f"📂 使用数据文件: {data_file.name}")
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    articles = data.get('articles', [])
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>热门文章 - AI推荐日报 {date}</title>
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
        .articles-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(350px, 100%), 1fr)); gap: 20px; }}
        .article-card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; text-decoration: none; display: block; }}
        .article-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.12); }}
        .card-image {{ width: 100%; height: 160px; background-size: cover; background-position: center; background-color: #f1f5f9; }}
        .card-body {{ padding: 16px; }}
        .card-title {{ font-size: 16px; font-weight: 600; margin-bottom: 8px; line-height: 1.4; color: #1e293b; }}
        .card-summary {{ font-size: 14px; color: #64748b; line-height: 1.6; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
        .card-meta {{ display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #94a3b8; }}
        .card-source {{ display: flex; align-items: center; gap: 4px; }}
        .card-date {{ color: #94a3b8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-newspaper"></i> 热门文章</h1>
        <p>共 {len(articles)} 篇文章 · {date}</p>
        <a href="index.html" class="back-link"><i class="fas fa-arrow-left"></i> 返回首页</a>
    </div>
    
    <div class="container">
        <div class="articles-grid">
'''
    
    for i, article in enumerate(articles, 1):
        title = article.get('cn_title', article.get('title', '未知标题'))
        summary = article.get('cn_summary', article.get('summary', '暂无摘要'))[:150]
        source = article.get('source', '未知来源')
        link = article.get('link', '#')
        cover = article.get('cover_image', '')
        published = article.get('published', '')
        
        # 如果没有封面图，使用渐变背景
        if not cover or cover == '':
            cover_style = 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'
        else:
            cover_style = f"background-image: url('{cover}');"
        
        html += f'''
            <a href="{link}" target="_blank" class="article-card">
                <div class="card-image" style="{cover_style}"></div>
                <div class="card-body">
                    <div class="card-title">{title}</div>
                    <div class="card-summary">{summary}</div>
                    <div class="card-meta">
                        <span class="card-source"><i class="fas fa-rss"></i> {source}</span>
                        <span class="card-date">{published}</span>
                    </div>
                </div>
            </a>
'''
    
    html += '''
        </div>
    </div>
</body>
</html>
'''
    
    output_file = base_dir / "articles.html"
    output_file.write_text(html, encoding='utf-8')
    print(f"✅ 已生成: {output_file}")

if __name__ == "__main__":
    generate_articles_page()
