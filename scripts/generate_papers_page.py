#!/usr/bin/env python3
"""
AI推荐日报 - 论文列表页面生成器
生成展示所有 arXiv 论文的独立页面
"""

import json
from datetime import datetime
from pathlib import Path

class PapersPageGenerator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
    
    def generate(self, data: dict) -> str:
        papers = data.get('arxiv_papers', [])
        today = data.get('date', datetime.now().strftime("%Y-%m-%d"))
        
        papers_json = json.dumps(papers, ensure_ascii=False)
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>arXiv 论文列表 | AI推荐日报</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        :root {{
            --color-text-anchor: #312C51;
            --color-text-secondary: rgba(49,44,81,0.68);
            --color-text-muted: rgba(49,44,81,0.40);
            --color-card: #FFFFFF;
            --bg: #FAFAFA;
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --safe-area-top: env(safe-area-inset-top, 0px);
            --safe-area-bottom: env(safe-area-inset-bottom, 0px);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: var(--bg);
            color: var(--color-text-anchor);
            line-height: 1.6;
        }}
        
        .nav {{
            position: fixed; top: 0; left: 0; right: 0;
            background: rgba(255,255,255,0.95); backdrop-filter: blur(12px);
            padding: 12px 16px; z-index: 100;
            display: flex; align-items: center; justify-content: space-between;
            border-bottom: 1px solid rgba(49,44,81,0.08);
            padding-top: calc(12px + var(--safe-area-top));
        }}
        .nav-back {{
            display: flex; align-items: center; gap: 8px;
            color: var(--color-text-anchor); text-decoration: none;
            font-size: 14px; font-weight: 600;
        }}
        .nav-title {{ font-size: 16px; font-weight: 700; }}
        .nav-count {{ font-size: 13px; color: var(--color-text-muted); }}
        
        .hero {{
            background: var(--gradient-primary);
            padding: 80px 20px 40px;
            padding-top: calc(80px + var(--safe-area-top));
            color: white;
            text-align: center;
        }}
        .hero-title {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; }}
        .hero-subtitle {{ font-size: 14px; opacity: 0.9; }}
        
        .main {{
            padding: 20px 16px 100px;
            padding-bottom: calc(100px + var(--safe-area-bottom));
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .card {{
            background: var(--color-card); border-radius: 16px;
            margin-bottom: 16px; overflow: hidden;
            cursor: pointer; transition: transform 0.2s;
        }}
        .card:active {{ transform: scale(0.98); }}
        
        .card-image {{
            width: 100%; height: 120px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-size: cover;
            background-position: center;
            position: relative;
        }}
        .card-image::before {{
            content: '';
            position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(180deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.4) 100%);
        }}
        .card-image-badge {{
            position: absolute; top: 10px; right: 10px; z-index: 2;
            background: rgba(255,255,255,0.95); color: var(--color-text-anchor);
            padding: 4px 12px; border-radius: 8px;
            font-size: 11px; font-weight: 700;
        }}
        .card-image-rank {{
            position: absolute; top: 10px; left: 10px; z-index: 2;
            width: 28px; height: 28px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            font-size: 13px; font-weight: 700;
        }}
        
        .card-body {{ padding: 16px; }}
        .card-category {{
            display: inline-flex; align-items: center; gap: 4px;
            padding: 4px 10px; border-radius: 6px;
            font-size: 11px; font-weight: 700; margin-bottom: 8px;
            background: rgba(102,126,234,0.1); color: #667eea;
        }}
        .card-title {{
            font-size: 15px; font-weight: 700; line-height: 1.4;
            color: var(--color-text-anchor); margin-bottom: 8px;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
        }}
        .card-summary {{
            font-size: 13px; color: var(--color-text-secondary); line-height: 1.5;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
            margin-bottom: 12px;
        }}
        .card-meta {{
            display: flex; align-items: center; gap: 12px;
            font-size: 12px; color: var(--color-text-muted);
        }}
        .card-link {{
            display: flex; align-items: center; gap: 4px;
            color: #667eea; font-size: 13px; font-weight: 600;
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="index.html" class="nav-back">
            <i class="fas fa-chevron-left"></i>
            <span>日报</span>
        </a>
        <div class="nav-title">arXiv 论文</div>
        <div class="nav-count">共 {len(papers)} 篇</div>
    </nav>
    
    <div class="hero">
        <h1 class="hero-title">📄 arXiv 论文列表</h1>
        <p class="hero-subtitle">{today} · 推荐算法 × AI Agent × LLM</p>
    </div>
    
    <main class="main" id="papers-list"></main>
    
    <script>
        const papers = {papers_json};
        const categoryLabels = {{ rec: '推荐算法', agent: 'AI Agent', llm: 'LLM应用', industry: '工业实践' }};
        const categoryEmoji = {{ rec: '📊', agent: '🤖', llm: '🧠', industry: '🏭' }};
        
        const container = document.getElementById('papers-list');
        
        container.innerHTML = papers.map((item, i) => {{
            const cnTitle = item.cn_title || (item.title ? item.title.slice(0, 50) + '...' : '论文');
            const cnSummary = item.cn_summary || '本文在推荐系统相关领域做出了创新研究。';
            const paperId = (item.id || item.arxiv_id || '').replace('/', '_').replace('.', '_');
            const insightUrl = `insights/paper_${{paperId}}.html`;
            
            return `
                <div class="card" onclick="window.location.href='${{insightUrl}}'">
                    <div class="card-image" style="${{item.cover_image ? `background-image: url('${{item.cover_image}}')` : ''}}">
                        <div class="card-image-rank">${{i + 1}}</div>
                        <div class="card-image-badge">arXiv</div>
                    </div>
                    <div class="card-body">
                        <div class="card-category">${{categoryEmoji[item.category] || '📄'}} ${{categoryLabels[item.category] || '论文'}}</div>
                        <h3 class="card-title">${{cnTitle}}</h3>
                        <p class="card-summary">${{cnSummary}}</p>
                        <div class="card-meta">
                            <span><i class="fas fa-calendar"></i> ${{item.published || ''}}</span>
                            <span><i class="fas fa-users"></i> ${{item.authors ? item.authors.slice(0,2).join(', ') : 'Unknown'}}</span>
                        </div>
                    </div>
                </div>
            `;
        }}).join('');
    </script>
</body>
</html>'''
        
        return html
    
    def save(self, html: str):
        output_file = self.base_dir / "papers.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ 论文列表页面已生成: {output_file}")


if __name__ == "__main__":
    import sys
    generator = PapersPageGenerator()
    
    # 加载数据
    data_file = generator.base_dir / "daily_data" / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    if len(sys.argv) > 1:
        data_file = Path(sys.argv[1])
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    html = generator.generate(data)
    generator.save(html)
