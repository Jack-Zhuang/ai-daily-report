#!/usr/bin/env python3
"""
AI推荐日报 - 日报生成脚本
生成移动端优化的HTML日报，包含顶会论文和多来源内容
"""

import json
from datetime import datetime
from pathlib import Path
import sys

class ReportGenerator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "daily_data"
        self.archive_dir = self.base_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)
        
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def load_today_data(self) -> dict:
        """加载今日数据"""
        file_path = self.data_dir / f"{self.today}.json"
        if not file_path.exists():
            print(f"❌ 未找到今日数据: {file_path}")
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_conference_papers(self, data: dict) -> dict:
        """获取顶会论文数据（从采集数据）"""
        # 优先使用采集的数据
        if 'conference_papers' in data and data['conference_papers']:
            return data['conference_papers']
        
        # 备用数据
        return {
            "WSDM 2025": {"name": "WSDM 2025", "total": 106, "date": "2025年3月", "location": "德国汉诺威", "papers": []},
            "KDD 2025": {"name": "KDD 2025", "total": 300, "date": "2025年8月", "location": "加拿大多伦多", "papers": []},
            "RecSys 2025": {"name": "RecSys 2025", "total": 49, "date": "2025年9月", "location": "捷克布拉格", "papers": []},
            "WWW 2025": {"name": "WWW 2025", "total": 200, "date": "2025年4月", "location": "新加坡", "papers": []},
            "CIKM 2025": {"name": "CIKM 2025", "total": 0, "date": "2025年10月", "location": "待定", "papers": []},
            "SIGIR 2025": {"name": "SIGIR 2025", "total": 0, "date": "2025年7月", "location": "待定", "papers": []},
            "arXiv 2026": {"name": "arXiv 2026", "total": 25, "date": "最新预印本", "location": "在线", "papers": []}
        }
    
    def generate_html(self, data: dict) -> str:
        """生成HTML日报"""
        
        # ========== 强约束验证 ==========
        # 1. 每日精选必须是5项，顺序为：3文章+1论文+1GitHub
        daily_pick = data.get('daily_pick', [])
        if len(daily_pick) != 5:
            print(f"⚠️ 每日精选数量错误: {len(daily_pick)}项，应为5项")
        
        # 2. GitHub Trending必须是5项
        github_projects = data.get('github_projects', data.get('github_trending', []))
        if len(github_projects) > 5:
            github_projects = github_projects[:5]
            print(f"⚠️ GitHub项目截取为5项")
        
        # 3. arXiv论文必须是5项
        arxiv_papers = data.get('arxiv_papers', [])
        if len(arxiv_papers) > 5:
            arxiv_papers = arxiv_papers[:5]
            print(f"⚠️ arXiv论文截取为5项")
        
        # 4. 热门文章去重（移除与每日精选重复的）
        pick_titles = set()
        for item in daily_pick:
            title = item.get('cn_title', item.get('title', item.get('name', '')))
            pick_titles.add(title)
        
        # 使用 articles 字段（30篇），而不是 hot_articles
        hot_articles = data.get('articles', data.get('hot_articles', []))
        hot_articles = [item for item in hot_articles if item.get('cn_title', item.get('title', '')) not in pick_titles]
        # 不截断，保留所有文章
        
        # 5. 检查摘要是否为中文
        for item in daily_pick:
            cn_summary = item.get('cn_summary', '')
            if not cn_summary:
                print(f"⚠️ 每日精选缺少cn_summary: {item.get('cn_title', '')[:30]}")
            elif len(cn_summary) < 50:
                print(f"⚠️ 每日精选摘要过短: {item.get('cn_title', '')[:30]}")
        
        # ========== 生成JavaScript数据 ==========
        daily_pick_json = json.dumps(daily_pick, ensure_ascii=False)
        hot_articles_json = json.dumps(hot_articles, ensure_ascii=False)
        github_projects_json = json.dumps(github_projects, ensure_ascii=False)
        arxiv_papers_json = json.dumps(arxiv_papers, ensure_ascii=False)
        conference_data = self.get_conference_papers(data)
        conference_json = json.dumps(conference_data, ensure_ascii=False)
        
        # 统计数据
        total_papers = len(data.get('arxiv_papers', []))
        total_projects = len(data.get('github_projects', []))
        total_articles = len(data.get('articles', data.get('hot_articles', [])))
        total_conference = sum(c.get('total', 0) for c in conference_data.values())
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI推荐日报 | {data['date']}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    
    <!-- MathJax 支持 - LaTeX 公式渲染 -->
    <script>
        MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']],
                processEscapes: true
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }}
        }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
    
    <!-- Mermaid 支持 - 流程图渲染 -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'neutral',
            themeVariables: {{
                primaryColor: '#667eea',
                primaryTextColor: '#fff',
                primaryBorderColor: '#764ba2',
                lineColor: '#666',
                secondaryColor: '#f0f0f0',
                tertiaryColor: '#fff'
            }}
        }});
    </script>
    <style>
        :root {{
            --color-text-anchor: #312C51;
            --color-text-secondary: rgba(49,44,81,0.68);
            --color-text-muted: rgba(49,44,81,0.40);
            --color-card: #FFFFFF;
            --bg: #FAFAFA;
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-hot: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --safe-area-top: env(safe-area-inset-top, 0px);
            --safe-area-bottom: env(safe-area-inset-bottom, 0px);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        html {{ font-size: 16px; scroll-behavior: smooth; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: var(--bg);
            color: var(--color-text-anchor);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            overflow-x: hidden;
        }}
        .number {{ font-family: 'SF Mono', monospace; }}
        
        /* Glow Background */
        .glow-container {{
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            overflow: hidden; pointer-events: none; z-index: 0;
        }}
        .glow {{
            position: absolute; border-radius: 50%;
            background: radial-gradient(ellipse, rgba(200,190,240,0.3) 0%, transparent 70%);
            filter: blur(60px);
        }}
        .glow-1 {{ width: 350px; height: 300px; top: 100px; left: -80px; }}
        .glow-2 {{ width: 300px; height: 280px; top: 250px; right: -60px; background: radial-gradient(ellipse, rgba(160,200,245,0.25) 0%, transparent 70%); }}
        .glow-3 {{ width: 280px; height: 260px; top: 550px; left: 5%; background: radial-gradient(ellipse, rgba(160,225,210,0.2) 0%, transparent 70%); }}
        
        /* Navigation */
        .nav {{
            position: fixed; top: 0; left: 0; right: 0; z-index: 100;
            padding: 10px 12px; padding-top: calc(10px + var(--safe-area-top));
            background: transparent; transition: background 0.3s;
        }}
        .nav.solid {{ background: rgba(250,250,250,0.95); backdrop-filter: blur(12px); }}
        .nav-inner {{ display: flex; align-items: center; justify-content: space-between; }}
        .nav-brand {{ display: flex; align-items: center; gap: 10px; }}
        .nav-icon {{
            width: 36px; height: 36px; background: var(--gradient-primary);
            border-radius: 10px; display: flex; align-items: center; justify-content: center;
            color: white; font-size: 16px;
        }}
        .nav-title {{ font-size: 15px; font-weight: 700; }}
        .nav-date {{ font-size: 12px; color: var(--color-text-muted); }}
        
        /* Search Button */
        .nav-actions {{ display: flex; align-items: center; gap: 8px; }}
        .nav-btn {{
            width: 36px; height: 36px; border: none; background: rgba(49,44,81,0.06);
            border-radius: 10px; color: var(--color-text-secondary);
            font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center;
        }}
        .nav-btn:active {{ background: rgba(49,44,81,0.12); }}
        
        /* Search Modal */
        .search-modal {{
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(250,250,250,0.98); z-index: 300;
            display: none; flex-direction: column;
        }}
        .search-modal.active {{ display: flex; }}
        .search-header {{
            padding: 12px 16px; padding-top: calc(12px + var(--safe-area-top));
            background: white; box-shadow: 0 2px 12px rgba(49,44,81,0.06);
        }}
        .search-input-wrap {{ display: flex; align-items: center; gap: 10px; }}
        .search-input {{
            flex: 1; height: 40px; border: none; background: rgba(49,44,81,0.04);
            border-radius: 10px; padding: 0 14px; font-size: 14px;
            outline: none;
        }}
        .search-input:focus {{ background: rgba(49,44,81,0.08); }}
        .search-cancel {{
            background: none; border: none; color: var(--color-text-secondary);
            font-size: 14px; cursor: pointer;
        }}
        .search-filters {{
            display: flex; gap: 8px; padding: 12px 16px; overflow-x: auto;
        }}
        .search-filter {{
            padding: 6px 14px; border-radius: 16px; font-size: 12px; font-weight: 600;
            background: rgba(49,44,81,0.04); color: var(--color-text-secondary);
            border: none; cursor: pointer; white-space: nowrap;
        }}
        .search-filter.active {{ background: var(--gradient-primary); color: white; }}
        .search-results {{ flex: 1; overflow-y: auto; padding: 12px 16px; }}
        .search-empty {{ text-align: center; padding: 60px 20px; color: var(--color-text-muted); }}
        .search-empty i {{ font-size: 48px; margin-bottom: 16px; opacity: 0.3; }}
        
        /* Module Navigation */
        .module-nav {{
            position: fixed; top: 56px; left: 0; right: 0; z-index: 99;
            padding: 8px 12px; padding-top: calc(8px + var(--safe-area-top));
            background: transparent; transition: all 0.3s;
            opacity: 0; transform: translateY(-10px);
        }}
        .module-nav.visible {{
            opacity: 1; transform: translateY(0);
            background: rgba(250,250,250,0.95); backdrop-filter: blur(12px);
            box-shadow: 0 2px 12px rgba(49,44,81,0.06);
        }}
        .module-nav-scroll {{
            display: flex; gap: 8px; overflow-x: auto; -webkit-overflow-scrolling: touch;
            padding-bottom: 4px;
        }}
        .module-nav-scroll::-webkit-scrollbar {{ display: none; }}
        .module-nav-item {{
            display: flex; align-items: center; gap: 6px;
            padding: 8px 14px; border-radius: 10px;
            background: rgba(255,255,255,0.9); color: var(--color-text-secondary);
            font-size: 12px; font-weight: 700; white-space: nowrap;
            text-decoration: none; box-shadow: 0 2px 8px rgba(49,44,81,0.05);
            transition: all 0.2s;
        }}
        .module-nav-item:active, .module-nav-item.active {{
            background: var(--gradient-primary); color: white;
            transform: scale(0.96);
        }}
        .module-nav-item i {{ font-size: 13px; }}
        
        /* Hero */
        .hero {{
            position: relative; z-index: 1;
            padding: 80px 16px 40px; text-align: center;
            padding-top: calc(80px + var(--safe-area-top));
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            margin: -60px -12px 0;
            padding-left: 12px;
            padding-right: 12px;
            margin-bottom: 20px;
            min-height: 200px;
        }}
        .hero::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.08'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.3;
        }}
        .hero-badge {{
            display: inline-flex; align-items: center; gap: 6px;
            background: rgba(255,255,255,0.25); padding: 6px 14px;
            border-radius: 16px; margin-bottom: 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        .hero-badge-dot {{ width: 6px; height: 6px; background: #fbbf24; border-radius: 50%; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
        .hero-badge-text {{ font-size: 11px; font-weight: 700; color: white; }}
        .hero-title {{ font-size: 32px; font-weight: 800; margin-bottom: 12px; color: white; text-shadow: 0 2px 20px rgba(0,0,0,0.2); letter-spacing: 2px; }}
        .hero-subtitle {{ font-size: 14px; color: rgba(255,255,255,0.95); margin-bottom: 24px; max-width: 280px; margin-left: auto; margin-right: auto; }}
        .hero-date {{
            display: inline-flex; align-items: center; gap: 8px;
            background: rgba(255,255,255,0.2); padding: 8px 16px;
            border-radius: 12px; font-size: 13px; color: white;
            margin-bottom: 20px;
        }}
        .hero-cover {{
            margin: 20px 0;
        }}
        .cover-card {{
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .cover-title {{
            color: white;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 16px;
            text-align: left;
        }}
        .cover-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 16px;
        }}
        .cover-item {{
            text-align: center;
        }}
        .cover-icon {{
            font-size: 24px;
            margin-bottom: 4px;
        }}
        .cover-num {{
            font-size: 24px;
            font-weight: 700;
            color: white;
        }}
        .cover-label {{
            font-size: 10px;
            color: rgba(255,255,255,0.8);
        }}
        .cover-sources {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            color: rgba(255,255,255,0.7);
        }}
        .source-badge {{
            background: rgba(255,255,255,0.2);
            padding: 2px 8px;
            border-radius: 10px;
            color: white;
        }}
        
        /* Stats */
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; padding: 0 4px; }}
        .stat {{
            background: rgba(255,255,255,0.95); border-radius: 14px;
            padding: 14px 8px; text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            transition: transform 0.15s, box-shadow 0.15s;
        }}
        .stat-link {{
            text-decoration: none; color: inherit;
            display: block;
        }}
        .stat-link:active {{
            transform: scale(0.96);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat-icon {{ font-size: 20px; margin-bottom: 4px; }}
        .stat-value {{ font-size: 22px; font-weight: 700; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .stat-label {{ font-size: 11px; color: var(--color-text-muted); margin-top: 2px; }}
        
        /* Main */
        .main {{ position: relative; z-index: 1; padding: 0 12px 60px; padding-bottom: calc(60px + var(--safe-area-bottom)); }}
        
        /* Section */
        .section {{ margin-bottom: 32px; }}
        .section-header {{ margin-bottom: 16px; scroll-margin-top: 112px; }}
        .section-title {{ font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 8px; }}
        .section-title i {{ font-size: 16px; color: #667eea; }}
        .section-subtitle {{ font-size: 12px; color: var(--color-text-muted); margin-top: 4px; }}
        
        /* Cards */
        .card {{
            background: var(--color-card); border-radius: 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 12px rgba(49,44,81,0.05);
            position: relative; overflow: hidden;
            cursor: pointer;
            transition: transform 0.15s, box-shadow 0.15s;
        }}
        .card:active {{
            transform: scale(0.98);
            box-shadow: 0 1px 6px rgba(49,44,81,0.08);
        }}
        
        /* Card Click Overlay */
        .card::after {{
            content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0); transition: background 0.15s;
            pointer-events: none; z-index: 5;
        }}
        .card:active::after {{ background: rgba(0,0,0,0.04); }}
        
        /* Card Image */
        .card-image {{
            width: 100%; height: 160px;
            background-color: #667eea;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            display: flex; align-items: center; justify-content: center;
            position: relative; overflow: hidden;
        }}
        .card-image::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(180deg, rgba(0,0,0,0.05) 0%, rgba(0,0,0,0.5) 100%);
            z-index: 1;
        }}
        .card-image-paper {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .card-image-article {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .card-image-github {{ background: linear-gradient(135deg, #24292e 0%, #4a5568 100%); }}
        .card-image-rec {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .card-image-agent {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
        .card-image-llm {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
        .card-image-icon {{ font-size: 48px; color: rgba(255,255,255,0.9); position: relative; z-index: 2; text-shadow: 0 2px 10px rgba(0,0,0,0.3); }}
        .card-image-badge {{
            position: absolute; top: 10px; right: 10px; z-index: 3;
            background: rgba(255,255,255,0.95); color: #1e293b;
            padding: 4px 10px; border-radius: 8px;
            font-size: 11px; font-weight: 700;
        }}
        .card-image-trending {{
            position: absolute; bottom: 10px; left: 10px;
            background: rgba(16,185,129,0.9); color: white;
            padding: 4px 10px; border-radius: 8px;
            font-size: 10px; font-weight: 700;
            display: flex; align-items: center; gap: 4px;
        }}
        
        .card-body {{ padding: 16px; }}
        .card-header {{ display: flex; align-items: flex-start; gap: 12px; margin-bottom: 10px; }}
        .card-rank {{
            width: 32px; height: 32px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 14px; font-weight: 700; flex-shrink: 0;
        }}
        .card-rank.gold {{ background: linear-gradient(135deg, #ffd700, #ffb700); color: white; box-shadow: 0 2px 8px rgba(255,215,0,0.3); }}
        .card-rank.silver {{ background: linear-gradient(135deg, #c0c0c0, #a8a8a8); color: white; box-shadow: 0 2px 8px rgba(192,192,192,0.3); }}
        .card-rank.bronze {{ background: linear-gradient(135deg, #cd7f32, #b8722d); color: white; box-shadow: 0 2px 8px rgba(205,127,50,0.3); }}
        .card-rank.normal {{ background: rgba(49,44,81,0.08); color: var(--color-text-secondary); }}
        .card-meta {{ flex: 1; min-width: 0; }}
        .card-category {{
            display: inline-flex; align-items: center; gap: 4px;
            padding: 3px 10px; border-radius: 6px;
            font-size: 10px; font-weight: 700; margin-bottom: 6px;
        }}
        .card-category.rec {{ background: rgba(102,126,234,0.12); color: #667eea; }}
        .card-category.agent {{ background: rgba(67,233,123,0.12); color: #10b981; }}
        .card-category.llm {{ background: rgba(240,147,251,0.12); color: #d946ef; }}
        .card-category.github {{ background: rgba(36,41,46,0.12); color: #24292e; }}
        .card-category.conference {{ background: rgba(250,112,154,0.12); color: #fa709a; }}
        .card-title {{ font-size: 14px; font-weight: 700; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
        .card-source {{ font-size: 11px; color: var(--color-text-muted); margin-top: 4px; display: flex; align-items: center; gap: 4px; }}
        .card-source i {{ font-size: 10px; }}
        .card-summary {{ font-size: 12px; color: var(--color-text-secondary); line-height: 1.6; margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
        .card-reason {{ display: flex; align-items: flex-start; gap: 6px; padding: 8px 12px; margin-bottom: 10px; background: linear-gradient(135deg, rgba(251,191,36,0.1) 0%, rgba(245,158,11,0.1) 100%); border-radius: 8px; font-size: 12px; color: #92400e; line-height: 1.5; }}
        .card-reason i {{ margin-top: 2px; flex-shrink: 0; }}
        .card-tags {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }}
        .card-tag {{ background: rgba(49,44,81,0.04); padding: 3px 10px; border-radius: 6px; font-size: 10px; color: var(--color-text-secondary); }}
        .card-footer {{ display: flex; align-items: center; justify-content: space-between; }}
        .card-stats {{ display: flex; gap: 14px; }}
        .card-stat {{ font-size: 11px; color: var(--color-text-muted); display: flex; align-items: center; gap: 4px; }}
        .card-stat i {{ font-size: 12px; }}
        .card-link {{
            background: var(--gradient-primary); color: white;
            padding: 7px 14px; border-radius: 8px;
            font-size: 11px; font-weight: 700;
            display: flex; align-items: center; gap: 4px;
            pointer-events: none;
        }}
        
        /* Favorite Button */
        .card-favorite {{
            position: absolute; top: 12px; left: 12px;
            width: 32px; height: 32px; border: none; background: rgba(255,255,255,0.9);
            border-radius: 8px; font-size: 14px; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 2px 8px rgba(49,44,81,0.1);
            z-index: 10;
            transition: transform 0.15s;
        }}
        .card-favorite:active {{ transform: scale(0.9); }}
        .card-favorite.active {{ color: #f87171; }}
        .card-favorite:not(.active) {{ color: var(--color-text-muted); }}
        
        /* Sort Dropdown */
        .sort-bar {{
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 12px; padding: 0 4px;
        }}
        .sort-label {{ font-size: 12px; color: var(--color-text-muted); }}
        .sort-select {{
            background: rgba(49,44,81,0.04); border: none;
            padding: 6px 12px; border-radius: 8px;
            font-size: 12px; font-weight: 600; color: var(--color-text-anchor);
            cursor: pointer;
        }}
        
        /* Back to Top */
        .back-to-top {{
            position: fixed; bottom: 20px; right: 16px;
            width: 44px; height: 44px; border: none;
            background: var(--gradient-primary); color: white;
            border-radius: 12px; font-size: 16px;
            box-shadow: 0 4px 16px rgba(102,126,234,0.3);
            cursor: pointer; opacity: 0; transform: translateY(20px);
            transition: all 0.3s; z-index: 50;
        }}
        .back-to-top.visible {{ opacity: 1; transform: translateY(0); }}
        
        /* Loading Skeleton */
        .skeleton {{
            background: linear-gradient(90deg, rgba(49,44,81,0.04) 25%, rgba(49,44,81,0.08) 50%, rgba(49,44,81,0.04) 75%);
            background-size: 200% 100%; animation: shimmer 1.5s infinite;
            border-radius: 8px;
        }}
        @keyframes shimmer {{ 0% {{ background-position: 200% 0; }} 100% {{ background-position: -200% 0; }} }}
        .skeleton-card {{ height: 180px; margin-bottom: 12px; border-radius: 16px; }}
        
        /* Toast */
        .toast {{
            position: fixed; bottom: 80px; left: 50%; transform: translateX(-50%) translateY(100px);
            background: rgba(49,44,81,0.9); color: white;
            padding: 12px 24px; border-radius: 10px;
            font-size: 13px; font-weight: 600;
            opacity: 0; transition: all 0.3s; z-index: 400;
        }}
        .toast.show {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
        
        /* Tabs */
        .tabs {{ display: flex; gap: 8px; margin-bottom: 14px; overflow-x: auto; -webkit-overflow-scrolling: touch; }}
        .tabs::-webkit-scrollbar {{ display: none; }}
        .tab {{
            padding: 8px 14px; border: none; border-radius: 10px;
            background: var(--color-card); color: var(--color-text-secondary);
            font-size: 12px; font-weight: 700; white-space: nowrap;
            box-shadow: 0 2px 8px rgba(49,44,81,0.05);
        }}
        .tab.active {{ background: var(--gradient-hot); color: white; }}
        
        /* Conference Grid */
        .conf-grid {{ display: grid; grid-template-columns: 1fr; gap: 16px; }}
        
        /* Conference Section */
        .conf-section {{ background: var(--color-card); border-radius: 14px; overflow: hidden; box-shadow: 0 2px 12px rgba(49,44,81,0.05); }}
        .conf-header-new {{ display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; background: rgba(49,44,81,0.02); }}
        .conf-info {{ flex: 1; }}
        .conf-name-new {{ font-size: 15px; font-weight: 700; margin-bottom: 2px; }}
        .conf-meta {{ font-size: 11px; color: var(--color-text-muted); }}
        .conf-total {{ text-align: right; }}
        .conf-count-new {{ font-size: 24px; font-weight: 700; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .conf-label-new {{ font-size: 11px; color: var(--color-text-muted); }}
        
        .conf-papers {{ padding: 8px 0; }}
        .conf-paper-item {{ display: flex; align-items: flex-start; padding: 12px 16px; text-decoration: none; color: inherit; border-bottom: 1px solid rgba(49,44,81,0.04); }}
        .conf-paper-item:last-child {{ border-bottom: none; }}
        .conf-paper-item:active {{ background: rgba(49,44,81,0.04); }}
        .conf-paper-rank {{ width: 24px; height: 24px; background: rgba(49,44,81,0.06); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: var(--color-text-secondary); margin-right: 12px; flex-shrink: 0; }}
        .conf-paper-content {{ flex: 1; min-width: 0; }}
        .conf-paper-title {{ font-size: 13px; font-weight: 600; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 4px; }}
        .conf-paper-authors {{ font-size: 11px; color: var(--color-text-muted); }}
        .conf-paper-highlight {{ background: linear-gradient(135deg, #ffd700, #ffb700); color: white; padding: 1px 6px; border-radius: 4px; font-size: 10px; margin-left: 6px; }}
        .conf-paper-emoji {{ font-size: 18px; margin-left: 8px; }}
        .conf-papers-empty {{ padding: 20px; text-align: center; font-size: 12px; color: var(--color-text-muted); }}
        
        .conf-view-all {{
            display: flex; align-items: center; justify-content: center;
            gap: 6px; padding: 12px; margin: 8px 12px 12px;
            background: var(--gradient-primary); color: white;
            border-radius: 10px; text-decoration: none;
            font-size: 13px; font-weight: 700;
        }}
        .conf-view-all:active {{ transform: scale(0.98); }}
        .conf-card {{
            background: var(--color-card); border-radius: 14px;
            padding: 14px; box-shadow: 0 2px 12px rgba(49,44,81,0.05);
        }}
        .conf-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
        .conf-icon {{
            width: 36px; height: 36px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            color: white; font-size: 14px;
        }}
        .conf-icon.wsdm {{ background: linear-gradient(135deg, #667eea, #764ba2); }}
        .conf-icon.kdd {{ background: linear-gradient(135deg, #f093fb, #f5576c); }}
        .conf-icon.rec {{ background: linear-gradient(135deg, #43e97b, #38f9d7); }}
        .conf-icon.www {{ background: linear-gradient(135deg, #4facfe, #00f2fe); }}
        .conf-icon.cikm {{ background: linear-gradient(135deg, #fa709a, #fee140); }}
        .conf-icon.sigir {{ background: linear-gradient(135deg, #a8edea, #fed6e3); }}
        .conf-icon.arxiv {{ background: linear-gradient(135deg, #667eea, #764ba2); }}
        .conf-name {{ font-size: 13px; font-weight: 700; }}
        .conf-date {{ font-size: 10px; color: var(--color-text-muted); }}
        .conf-count {{ font-size: 18px; font-weight: 700; color: #667eea; }}
        .conf-label {{ font-size: 10px; color: var(--color-text-muted); }}
        
        /* Source Grid */
        .source-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
        .source-card {{
            background: var(--color-card); border-radius: 12px;
            padding: 12px; text-align: center;
            box-shadow: 0 2px 8px rgba(49,44,81,0.05);
        }}
        .source-icon {{
            width: 40px; height: 40px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 8px; font-size: 18px; color: white;
        }}
        .source-icon.wechat {{ background: linear-gradient(135deg, #07c160, #00a854); }}
        .source-icon.zhihu {{ background: linear-gradient(135deg, #0084ff, #0066cc); }}
        .source-icon.github {{ background: linear-gradient(135deg, #24292e, #1a1e22); }}
        .source-icon.medium {{ background: linear-gradient(135deg, #000, #333); }}
        .source-icon.arxiv {{ background: linear-gradient(135deg, #b31b1b, #8b1515); }}
        .source-icon.conf {{ background: linear-gradient(135deg, #667eea, #764ba2); }}
        .source-name {{ font-size: 12px; font-weight: 700; margin-bottom: 2px; }}
        .source-count {{ font-size: 11px; color: var(--color-text-muted); }}
        
        /* Footer */
        .footer {{
            text-align: center; padding: 30px 16px;
            color: var(--color-text-muted); font-size: 11px;
            border-top: 1px solid rgba(49,44,81,0.06);
        }}
        .footer-links {{ display: flex; justify-content: center; gap: 16px; margin-bottom: 10px; }}
        .footer-link {{ color: var(--color-text-secondary); text-decoration: none; font-size: 12px; }}
        
        /* Archive Button */
        .archive-btn {{
            display: block; width: 100%; padding: 14px;
            background: rgba(49,44,81,0.04); border: none; border-radius: 12px;
            font-size: 13px; font-weight: 700; color: var(--color-text-anchor);
            text-align: center; margin-top: 20px; cursor: pointer;
        }}
        
        /* View More Button */
        .view-more-btn {{
            display: flex; align-items: center; justify-content: center; gap: 8px;
            width: 100%; padding: 14px; margin-top: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 12px;
            font-size: 14px; font-weight: 600; cursor: pointer;
            transition: transform 0.2s;
        }}
        .view-more-btn:active {{ transform: scale(0.98); }}
        
        /* Modal */
        .modal-overlay {{
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.4); z-index: 200;
            animation: fadeIn 0.2s;
        }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        
        .modal-content {{
            position: fixed; bottom: 0; left: 0; right: 0;
            background: white; border-radius: 20px 20px 0 0;
            max-height: 70vh; overflow: hidden;
            z-index: 201; animation: slideUp 0.3s;
        }}
        @keyframes slideUp {{ from {{ transform: translateY(100%); }} to {{ transform: translateY(0); }} }}
        
        .modal-header {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 20px 16px 16px; border-bottom: 1px solid rgba(49,44,81,0.06);
        }}
        .modal-header h3 {{ font-size: 16px; display: flex; align-items: center; gap: 8px; }}
        .modal-header h3 i {{ color: #667eea; }}
        .modal-close {{
            width: 32px; height: 32px; border: none; background: rgba(49,44,81,0.06);
            border-radius: 8px; font-size: 14px; color: var(--color-text-secondary);
            cursor: pointer;
        }}
        
        .modal-body {{ padding: 12px 16px 30px; max-height: 50vh; overflow-y: auto; }}
        
        .archive-loading, .archive-empty, .archive-error {{
            text-align: center; padding: 40px 20px;
            color: var(--color-text-muted); font-size: 13px;
        }}
        
        .archive-item {{
            display: flex; align-items: center;
            padding: 14px; margin-bottom: 8px;
            background: rgba(49,44,81,0.02); border-radius: 12px;
            text-decoration: none; color: inherit;
        }}
        .archive-item:active {{ background: rgba(49,44,81,0.06); }}
        .archive-date {{ font-size: 15px; font-weight: 700; flex: 1; }}
        .archive-stats {{ font-size: 11px; color: var(--color-text-muted); margin-right: 12px; }}
        .archive-stats span {{ margin-left: 10px; }}
        .archive-item i {{ color: var(--color-text-muted); }}
    </style>
</head>
<body>
    <div class="glow-container">
        <div class="glow glow-1"></div>
        <div class="glow glow-2"></div>
        <div class="glow glow-3"></div>
    </div>
    
    <nav class="nav" id="nav">
        <div class="nav-inner">
            <div class="nav-brand">
                <div class="nav-icon"><i class="fas fa-robot"></i></div>
                <div>
                    <div class="nav-title">AI推荐日报</div>
                    <div class="nav-date">{data['date']}</div>
                </div>
            </div>
            <div class="nav-actions">
                <button class="nav-btn" onclick="openSearch()"><i class="fas fa-search"></i></button>
                <button class="nav-btn" onclick="showFavorites()"><i class="fas fa-bookmark"></i></button>
            </div>
        </div>
    </nav>
    
    <!-- Search Modal -->
    <div class="search-modal" id="searchModal">
        <div class="search-header">
            <div class="search-input-wrap">
                <i class="fas fa-search" style="color: var(--color-text-muted)"></i>
                <input type="text" class="search-input" id="searchInput" placeholder="搜索论文、项目、文章..." oninput="doSearch()">
                <button class="search-cancel" onclick="closeSearch()">取消</button>
            </div>
            <div class="search-filters">
                <button class="search-filter active" data-filter="all" onclick="setSearchFilter('all')">全部</button>
                <button class="search-filter" data-filter="paper" onclick="setSearchFilter('paper')">论文</button>
                <button class="search-filter" data-filter="project" onclick="setSearchFilter('project')">项目</button>
                <button class="search-filter" data-filter="article" onclick="setSearchFilter('article')">文章</button>
            </div>
        </div>
        <div class="search-results" id="searchResults">
            <div class="search-empty">
                <i class="fas fa-search"></i>
                <div>输入关键词开始搜索</div>
            </div>
        </div>
    </div>
    
    <!-- Detail Modal -->
    <div class="modal-overlay" id="detail-modal" onclick="if(event.target === this) closeDetailModal()" style="display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); z-index:400;">
        <div class="modal-content" style="position:absolute; bottom:0; left:0; right:0; background:white; border-radius:20px 20px 0 0; max-height:80vh; overflow:hidden; animation:slideUp 0.3s; display:flex; flex-direction:column;">
            <div style="width:36px; height:4px; background:#e2e8f0; border-radius:2px; margin:12px auto; flex-shrink:0;"></div>
            <div class="modal-header" style="padding:0 20px 16px; border-bottom:1px solid #e2e8f0; flex-shrink:0;">
                <h3 id="detail-modal-title" style="font-size:18px; font-weight:700;"></h3>
            </div>
            <div id="detail-modal-body" style="padding:20px; overflow-y:auto; flex:1; min-height:0;"></div>
            <div id="detail-modal-footer" style="padding:16px 20px; border-top:1px solid #e2e8f0; background:white; flex-shrink:0;"></div>
        </div>
    </div>
    <style>
        #detail-modal.active {{ display: flex !important; flex-direction: column; justify-content: flex-end; }}
        @keyframes slideUp {{ from {{ transform: translateY(100%); }} to {{ transform: translateY(0); }} }}
        .detail-section {{ margin-bottom: 20px; }}
        .detail-label {{ font-size: 12px; color: #94a3b8; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .detail-value {{ font-size: 14px; color: #1e293b; line-height: 1.6; }}
        .detail-tags {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .detail-tag {{ background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); padding: 4px 12px; border-radius: 8px; font-size: 12px; color: #667eea; }}
        .detail-link {{ display: flex; align-items: center; justify-content: center; gap: 8px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 14px 24px; border-radius: 12px; text-decoration: none; font-size: 14px; font-weight: 600; width: 100%; }}
        .detail-link:hover {{ opacity: 0.9; }}
    </style>
    
    <!-- Back to Top -->
    <button class="back-to-top" id="backToTop" onclick="scrollToTop()">
        <i class="fas fa-arrow-up"></i>
    </button>
    
    <!-- Toast -->
    <div class="toast" id="toast"></div>
    
    <!-- Module Navigation -->
    <div class="module-nav" id="moduleNav">
        <div class="module-nav-scroll">
            <a href="#daily-pick" class="module-nav-item"><i class="fas fa-star"></i> 精选</a>
            <a href="#hot" class="module-nav-item"><i class="fas fa-fire"></i> 热门</a>
            <a href="#github" class="module-nav-item"><i class="fas fa-chart-line"></i> Trending</a>
            <a href="#papers" class="module-nav-item"><i class="fas fa-file-alt"></i> arXiv</a>
            <a href="#conferences" class="module-nav-item"><i class="fas fa-trophy"></i> 顶会</a>
            <a href="#sources" class="module-nav-item"><i class="fas fa-globe"></i> 来源</a>
        </div>
    </div>
    
    <div class="hero">
        <div class="hero-badge">
            <div class="hero-badge-dot"></div>
            <span class="hero-badge-text">每日更新</span>
        </div>
        <h1 class="hero-title">AI 推荐日报</h1>
        <p class="hero-subtitle">推荐算法 × AI Agent × LLM 前沿追踪，每日精选最值得阅读的内容</p>
        <div class="hero-date">
            <i class="far fa-calendar"></i>
            <span>{data['date']}</span>
        </div>
        <!-- 题图：今日数据概览 -->
        <div class="hero-cover">
            <div class="cover-card">
                <div class="cover-title">📊 今日数据概览</div>
                <div class="cover-grid">
                    <div class="cover-item">
                        <div class="cover-icon">📄</div>
                        <div class="cover-num">{total_papers}</div>
                        <div class="cover-label">arXiv论文</div>
                    </div>
                    <div class="cover-item">
                        <div class="cover-icon">💻</div>
                        <div class="cover-num">{total_projects}</div>
                        <div class="cover-label">GitHub项目</div>
                    </div>
                    <div class="cover-item">
                        <div class="cover-icon">📰</div>
                        <div class="cover-num">{total_articles}</div>
                        <div class="cover-label">热门文章</div>
                    </div>
                    <div class="cover-item">
                        <div class="cover-icon">⭐</div>
                        <div class="cover-num">{len(data.get('daily_pick', []))}</div>
                        <div class="cover-label">精选推荐</div>
                    </div>
                </div>
                <div class="cover-sources">
                    <span>数据来源：</span>
                    <span class="source-badge">机器之心</span>
                    <span class="source-badge">量子位</span>
                    <span class="source-badge">知乎</span>
                    <span class="source-badge">GitHub</span>
                    <span class="source-badge">arXiv</span>
                </div>
            </div>
        </div>
        <div class="stats">
            <a href="#daily-pick" class="stat stat-link"><div class="stat-icon">⭐</div><div class="stat-value number">{len(data.get('daily_pick', []))}</div><div class="stat-label">精选内容</div></a>
            <a href="#conferences" class="stat stat-link"><div class="stat-icon">🏆</div><div class="stat-value number">{total_conference}+</div><div class="stat-label">顶会论文</div></a>
            <a href="#papers" class="stat stat-link"><div class="stat-icon">📄</div><div class="stat-value number">{total_papers}</div><div class="stat-label">arXiv论文</div></a>
            <a href="#github" class="stat stat-link"><div class="stat-icon">💻</div><div class="stat-value number">{total_projects}</div><div class="stat-label">GitHub项目</div></a>
            <a href="#hot" class="stat stat-link"><div class="stat-icon">🔥</div><div class="stat-value number">{total_articles}</div><div class="stat-label">热门文章</div></a>
            <a href="#sources" class="stat stat-link"><div class="stat-icon">🌐</div><div class="stat-value number">6</div><div class="stat-label">数据来源</div></a>
        </div>
    </div>
    
    <div class="main">
        <!-- 每日精选 -->
        <section class="section">
            <div class="section-header" id="daily-pick">
                <h2 class="section-title"><i class="fas fa-star"></i> 每日精选</h2>
                <p class="section-subtitle">编辑精选 · 今日最值得阅读</p>
            </div>
            <div id="daily-pick-list"></div>
        </section>
        
        <!-- 热门文章 -->
        <section class="section">
            <div class="section-header" id="hot">
                <h2 class="section-title"><i class="fas fa-fire"></i> 热门文章</h2>
                <p class="section-subtitle">基于热度综合排序</p>
            </div>
            <div class="tabs">
                <button class="tab active" data-tab="all">全部</button>
                <button class="tab" data-tab="rec">推荐</button>
                <button class="tab" data-tab="agent">Agent</button>
                <button class="tab" data-tab="llm">LLM</button>
            </div>
            <div id="hot-list"></div>
        </section>
        
        <!-- GitHub热点 -->
        <section class="section">
            <div class="section-header" id="github">
                <h2 class="section-title"><i class="fas fa-chart-line"></i> GitHub Trending</h2>
                <p class="section-subtitle">高增速项目 · 按增长趋势排序</p>
            </div>
            <div id="github-list"></div>
        </section>
        
        <!-- arXiv最新 -->
        <section class="section">
            <div class="section-header" id="papers">
                <h2 class="section-title"><i class="fas fa-file-alt"></i> arXiv最新</h2>
                <p class="section-subtitle">最新预印本论文</p>
            </div>
            <div id="papers-list"></div>
        </section>
        
        <!-- 顶会论文 -->
        <section class="section">
            <div class="section-header" id="conferences">
                <h2 class="section-title"><i class="fas fa-trophy"></i> 顶会论文</h2>
                <p class="section-subtitle">WSDM · KDD · RecSys · WWW · CIKM · SIGIR</p>
            </div>
            <div class="conf-grid" id="conf-list"></div>
        </section>
        
        <!-- 内容来源 -->
        <section class="section">
            <div class="section-header" id="sources">
                <h2 class="section-title"><i class="fas fa-globe"></i> 内容来源</h2>
                <p class="section-subtitle">多渠道聚合 · 自动追踪</p>
            </div>
            <div class="source-grid">
                <div class="source-card">
                    <div class="source-icon wechat"><i class="fab fa-weixin"></i></div>
                    <div class="source-name">公众号</div>
                    <div class="source-count">机器之心等</div>
                </div>
                <div class="source-card">
                    <div class="source-icon zhihu"><i class="fab fa-zhihu"></i></div>
                    <div class="source-name">知乎</div>
                    <div class="source-count">技术专栏</div>
                </div>
                <div class="source-card">
                    <div class="source-icon github"><i class="fab fa-github"></i></div>
                    <div class="source-name">GitHub</div>
                    <div class="source-count">{total_projects}个项目</div>
                </div>
                <div class="source-card">
                    <div class="source-icon medium"><i class="fab fa-medium"></i></div>
                    <div class="source-name">Medium</div>
                    <div class="source-count">海外博客</div>
                </div>
                <div class="source-card">
                    <div class="source-icon arxiv"><i class="fas fa-file-alt"></i></div>
                    <div class="source-name">arXiv</div>
                    <div class="source-count">{total_papers}篇论文</div>
                </div>
                <div class="source-card">
                    <div class="source-icon conf"><i class="fas fa-trophy"></i></div>
                    <div class="source-name">顶会</div>
                    <div class="source-count">{total_conference}+篇</div>
                </div>
            </div>
        </section>
        
        <!-- 往期日报 -->
        <button class="archive-btn" onclick="showArchive()">
            <i class="fas fa-history"></i> 查看往期日报
        </button>
    </div>
    
    <div class="footer">
        <div class="footer-links">
            <a href="javascript:void(0)" class="footer-link" onclick="showSubscribeModal()">订阅</a>
            <a href="javascript:void(0)" class="footer-link" onclick="shareReport()">分享</a>
            <a href="https://github.com/Jack-Zhuang/ai-daily-report/issues" target="_blank" class="footer-link">反馈</a>
        </div>
        <p>AI推荐日报 © 2026 | 数据来源：顶会论文、arXiv、公众号、知乎、GitHub、Medium</p>
    </div>

    <!-- 订阅弹窗 -->
    <div id="subscribeModal" class="modal" style="display:none;">
        <div class="modal-overlay" onclick="closeSubscribeModal()"></div>
        <div class="modal-content" style="max-width:400px;padding:24px;">
            <h3 style="margin-bottom:16px;font-size:18px;">📬 订阅 AI 推荐日报</h3>
            <p style="color:var(--color-text-secondary);margin-bottom:16px;font-size:14px;">
                每日推送最新 AI 论文、开源项目和热门文章
            </p>
            <div style="background:rgba(102,126,234,0.1);padding:16px;border-radius:12px;margin-bottom:16px;">
                <p style="font-size:13px;color:var(--color-text-secondary);margin-bottom:8px;">订阅方式</p>
                <p style="font-size:14px;font-weight:600;">• 微信公众号：AI推荐日报</p>
                <p style="font-size:14px;font-weight:600;">• RSS：https://jack-zhuang.github.io/ai-daily-report/feed.xml</p>
                <p style="font-size:14px;font-weight:600;">• GitHub Watch：关注仓库获取更新</p>
            </div>
            <button onclick="closeSubscribeModal()" style="width:100%;padding:12px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:12px;font-size:14px;font-weight:600;cursor:pointer;">
                知道了
            </button>
        </div>
    </div>

    <script>
        // 数据
        const dailyPick = {daily_pick_json};
        const hotArticles = {hot_articles_json};
        const githubProjects = {github_projects_json};
        const arxivPapers = {arxiv_papers_json};
        const conferenceData = {conference_json};
        
        // 分类标签
        const categoryLabels = {{
            rec: '推荐算法',
            agent: 'AI Agent',
            llm: 'LLM应用',
            industry: '工业实践',
            github: 'GitHub',
            conference: '顶会论文'
        }};
        
        // 渲染每日精选
        function renderDailyPick() {{
            const container = document.getElementById('daily-pick-list');
            const typeIcons = {{ paper: '📄', article: '📰', github: '💻' }};
            const categoryImages = {{ rec: 'card-image-rec', agent: 'card-image-agent', llm: 'card-image-llm' }};
            
            container.innerHTML = dailyPick.map((item, i) => {{
                const rankClass = i < 3 ? ['gold', 'silver', 'bronze'][i] : 'normal';
                const category = item.type === 'github' ? 'github' : item.category;
                const pickType = item.pick_type || 'paper';
                const typeIcon = typeIcons[pickType] || '📄';
                const imageClass = item.type === 'github' ? 'card-image-github' : (categoryImages[category] || 'card-image-paper');
                const itemId = item.id || item.name || 'pick-' + i;
                const itemType = item.type || 'paper';
                const itemTitle = (item.title || item.name || '').replace(/'/g, "\\\\'").replace(/"/g, '\\"');
                const itemLink = item.link || item.url || '#';
                const isFav = isFavorite(itemId, itemType);
                
                // 中文标题和简介
                const cnTitle = item.cn_title || (item.title || item.name);
                // 摘要限制80字
                const rawSummary = item.cn_summary || (item.summary || item.description || '');
                const cnSummary = rawSummary.length > 80 ? rawSummary.substring(0, 80) + '...' : rawSummary;
                const recommendReason = item._reason || item.recommend_reason || '';
                
                // 存储完整数据到 data 属性
                const itemData = encodeURIComponent(JSON.stringify(item));
                
                return `
                    <div class="card" data-index="${{i}}" onclick="showPickDetail(${{i}})">
                        <button class="card-favorite ${{isFav ? 'active' : ''}}" 
                            data-id="${{itemId}}" data-type="${{itemType}}" data-title="${{itemTitle}}" data-link="${{itemLink}}"
                            onclick="event.stopPropagation(); handleFavoriteClick(this)">
                            <i class="${{isFav ? 'fas' : 'far'}} fa-bookmark"></i>
                        </button>
                        <div class="card-image ${{item.cover_image ? '' : imageClass}}" style="${{item.cover_image ? `background-image: url('${{item.cover_image}}')` : ''}}">
                            <div class="card-image-icon">${{item.cover_image ? '' : typeIcon}}</div>
                            <div class="card-image-badge">TOP ${{i + 1}}</div>
                        </div>
                        <div class="card-body">
                            <div class="card-header">
                                <div class="card-rank ${{rankClass}}">${{i + 1}}</div>
                                <div class="card-meta">
                                    <span class="card-category ${{category}}">${{typeIcon}} ${{categoryLabels[category] || category}}</span>
                                    <h3 class="card-title">${{cnTitle}}</h3>
                                    <div class="card-source"><i class="fas fa-user-edit"></i> ${{item.source || 'arXiv'}} ${{item.authors ? ' · ' + item.authors.slice(0,2).join(',') : ''}}</div>
                                </div>
                            </div>
                            <p class="card-summary">${{cnSummary}}</p>
                            ${{recommendReason ? `<div class="card-reason"><i class="fas fa-lightbulb" style="color:#fbbf24"></i> ${{recommendReason}}</div>` : ''}}
                            <div class="card-footer">
                                <div class="card-stats">
                                    ${{item.stars ? `<span class="card-stat"><i class="fas fa-star" style="color:#fbbf24"></i> ${{item.stars.toLocaleString()}}</span>` : ''}}
                                    ${{item.views ? `<span class="card-stat"><i class="fas fa-eye" style="color:#60a5fa"></i> ${{item.views}}</span>` : ''}}
                                    ${{item.likes ? `<span class="card-stat"><i class="fas fa-heart" style="color:#f87171"></i> ${{item.likes}}</span>` : ''}}
                                </div>
                                <span class="card-link">查看详情 <i class="fas fa-chevron-right"></i></span>
                            </div>
                        </div>
                    </div>
                `;
            }}).join('');
        }}
        
        // 显示每日精选详情弹窗
        function showPickDetail(index) {{
            const item = dailyPick[index];
            if (!item) return;
            
            const pickType = item.pick_type || 'paper';
            const typeIcon = {{ paper: '📄', article: '📰', github: '💻' }}[pickType] || '📄';
            const cnTitle = item.cn_title || item.title || item.name || '未知标题';
            const cnSummary = item.cn_summary || item.summary || item.description || '暂无简介';
            const itemLink = item.link || item.url || '#';
            
            let detailHtml = `
                <div class="detail-section">
                    <div class="detail-label">标题</div>
                    <div class="detail-value">${{item.title || item.name || '未知标题'}}</div>
                </div>
            `;
            
            if (pickType === 'paper') {{
                detailHtml += `
                    <div class="detail-section">
                        <div class="detail-label">作者</div>
                        <div class="detail-value">${{(item.authors || []).join(', ') || '未知'}}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-label">发布时间</div>
                        <div class="detail-value">${{item.published || '未知'}}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-label">摘要</div>
                        <div class="detail-value">${{cnSummary}}</div>
                    </div>
                `;
            }} else if (pickType === 'github') {{
                detailHtml += `
                    <div class="detail-section">
                        <div class="detail-label">语言</div>
                        <div class="detail-value">${{item.language || '未知'}}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-label">统计</div>
                        <div class="detail-value">
                            ⭐ ${{(item.stars || 0).toLocaleString()}} Stars · 
                            🍴 ${{item.forks || 0}} Forks · 
                            📈 +${{(item.growth_rate || 0).toFixed(1)}}% 增长
                        </div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-label">描述</div>
                        <div class="detail-value">${{item.description || '暂无描述'}}</div>
                    </div>
                `;
            }} else {{
                detailHtml += `
                    <div class="detail-section">
                        <div class="detail-label">来源</div>
                        <div class="detail-value">${{item.source || '未知来源'}}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-label">发布时间</div>
                        <div class="detail-value">${{item.published || '未知'}}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-label">摘要</div>
                        <div class="detail-value">${{cnSummary}}</div>
                    </div>
                `;
            }}
            
            // 添加标签
            if (item.topics && item.topics.length > 0) {{
                detailHtml += `
                    <div class="detail-section">
                        <div class="detail-label">标签</div>
                        <div class="detail-tags">${{item.topics.slice(0, 5).map(t => `<span class="detail-tag">${{t}}</span>`).join('')}}</div>
                    </div>
                `;
            }} else if (item.category) {{
                detailHtml += `
                    <div class="detail-section">
                        <div class="detail-label">分类</div>
                        <div class="detail-tags"><span class="detail-tag">${{item.category}}</span></div>
                    </div>
                `;
            }}
            
            // 生成按钮HTML
            let footerHtml = '';
            if (pickType === 'paper') {{
                // 论文：必须先跳转到解读页面，不能直接跳转原文
                const paperId = (item.id || item.arxiv_id || '').replace('/', '_').replace('.', '_');
                const insightUrl = `docs/insights/${{data.date}}_${{paperId}}.html`;
                footerHtml = `<a href="${{insightUrl}}" class="detail-link"><i class="fas fa-book-reader"></i> 查看论文解读</a>`;
            }} else {{
                footerHtml = `<a href="${{itemLink}}" target="_blank" class="detail-link"><i class="fas fa-external-link-alt"></i> ${{pickType === 'github' ? '访问 GitHub' : '阅读原文'}}</a>`;
            }}
            
            document.getElementById('detail-modal-title').innerHTML = `${{typeIcon}} ${{cnTitle}}`;
            document.getElementById('detail-modal-body').innerHTML = detailHtml;
            document.getElementById('detail-modal-footer').innerHTML = footerHtml;
            document.getElementById('detail-modal').classList.add('active');
        }}
        
        // 关闭详情弹窗
        function closeDetailModal() {{
            document.getElementById('detail-modal').classList.remove('active');
        }}
        
        // 收藏按钮点击处理
        function handleFavoriteClick(btn) {{
            event.stopPropagation();
            const id = btn.dataset.id;
            const type = btn.dataset.type;
            const title = btn.dataset.title;
            const link = btn.dataset.link;
            toggleFavorite(id, type, title, link);
            
            // 更新按钮状态
            const isFav = isFavorite(id, type);
            btn.classList.toggle('active', isFav);
            btn.innerHTML = `<i class="${{isFav ? 'fas' : 'far'}} fa-bookmark"></i>`;
        }}
        
        // 渲染顶会论文
        function renderConferences() {{
            const container = document.getElementById('conf-list');
            const confColors = {{
                'WSDM 2025': '#667eea',
                'KDD 2025': '#f093fb',
                'RecSys 2025': '#43e97b',
                'WWW 2025': '#4facfe',
                'CIKM 2025': '#fa709a',
                'SIGIR 2025': '#fee140',
                'arXiv 2026': '#764ba2'
            }};
            
            let html = '';
            
            // 遍历每个会议
            Object.keys(conferenceData).forEach(confName => {{
                const conf = conferenceData[confName];
                const color = confColors[confName] || '#667eea';
                const confUrl = 'conferences/' + confName.replace(/ /g, '_').replace(/\\//g, '_') + '/index.html';
                
                html += `
                    <div class="conf-section">
                        <div class="conf-header-new" style="border-left: 4px solid ${{color}};">
                            <div class="conf-info">
                                <div class="conf-name-new">${{conf.name}}</div>
                                <div class="conf-meta">${{conf.date}} · ${{conf.location || ''}} ${{conf.acceptance_rate ? '· 录用率 ' + conf.acceptance_rate : ''}}</div>
                            </div>
                            <div class="conf-total">
                                <span class="conf-count-new">${{conf.total || 0}}</span>
                                <span class="conf-label-new">篇</span>
                            </div>
                        </div>
                `;
                
                // 显示论文列表（外显3篇，点击查看全部）
                if (conf.papers && conf.papers.length > 0) {{
                    html += `<div class="conf-papers">`;
                    conf.papers.slice(0, 3).forEach((paper, i) => {{
                        const categoryEmoji = {{ rec: '📊', agent: '🤖', llm: '🧠', industry: '🏭' }};
                        const emoji = categoryEmoji[paper.category] || '📄';
                        // 论文解读页面链接 - 从 link 中提取 ID
                        let paperId = paper.id || paper.arxiv_id || '';
                        if (!paperId && paper.link) {{
                            // 从 arXiv 链接提取 ID: https://arxiv.org/abs/2404.12345
                            const arxivMatch = paper.link.match(/arxiv\\.org\\/abs\\/([^\\/\\?]+)/i);
                            if (arxivMatch) paperId = arxivMatch[1];
                            // 从 AMiner 链接提取 ID: https://www.aminer.cn/pub/xxxxx
                            const aminerMatch = paper.link.match(/aminer\\.cn\\/pub\\/([^\\/\\?]+)/i);
                            if (aminerMatch) paperId = aminerMatch[1];
                        }}
                        if (!paperId) paperId = 'unknown_' + i;
                        paperId = paperId.replace('/', '_').replace('.', '_');
                        const insightUrl = `docs/insights/${{data.date}}_${{paperId}}.html`;
                        html += `
                            <a href="${{insightUrl}}" class="conf-paper-item">
                                <div class="conf-paper-rank">${{i + 1}}</div>
                                <div class="conf-paper-content">
                                    <div class="conf-paper-title">${{paper.title}}</div>
                                    <div class="conf-paper-authors">${{paper.authors ? paper.authors.join(', ') : ''}} ${{paper.highlight ? '<span class="conf-paper-highlight">' + paper.highlight + '</span>' : ''}}</div>
                                </div>
                                <div class="conf-paper-emoji">${{emoji}}</div>
                            </a>
                        `;
                    }});
                    html += `</div>`;
                }} else if (conf.total > 0) {{
                    html += `<div class="conf-papers-empty">论文列表待更新...</div>`;
                }} else {{
                    html += `<div class="conf-papers-empty">会议尚未召开或论文列表未发布</div>`;
                }}
                
                // 添加"查看全部论文"按钮 - 跳转到会议页面
                const confPageUrl = 'conferences/' + confName.replace(/ /g, '_') + '.html';
                html += `
                    <a href="${{confPageUrl}}" class="conf-view-all">
                        <span>查看全部论文</span>
                        <i class="fas fa-chevron-right"></i>
                    </a>
                `;
                
                html += `</div>`;
            }});
            
            container.innerHTML = html;
        }}
        
        // 渲染热门文章
        function renderHotArticles(filter = 'all') {{
            const container = document.getElementById('hot-list');
            
            // 筛选逻辑：确保每个子tab至少有1篇
            let filtered = [];
            if (filter === 'all') {{
                // 全部：显示15篇，确保每个分类都有
                const categories = ['rec', 'agent', 'llm'];
                const byCategory = {{}};
                categories.forEach(cat => byCategory[cat] = []);
                const others = [];
                
                hotArticles.forEach(a => {{
                    if (categories.includes(a.category)) {{
                        byCategory[a.category].push(a);
                    }} else {{
                        others.push(a);
                    }}
                }});
                
                // 每个分类至少取1篇
                categories.forEach(cat => {{
                    if (byCategory[cat].length > 0) {{
                        filtered.push(byCategory[cat].shift());
                    }}
                }});
                
                // 补充剩余文章
                const remaining = [...byCategory.rec, ...byCategory.agent, ...byCategory.llm, ...others]
                    .sort((a, b) => (b.views || 0) - (a.views || 0));
                filtered = [...filtered, ...remaining].slice(0, 15);
            }} else {{
                // 按分类筛选
                filtered = hotArticles.filter(a => a.category === filter).slice(0, 15);
            }}
            
            const categoryEmoji = {{ rec: '📊', agent: '🤖', llm: '🧠', industry: '🏭', wechat: '📱', zhihu: '💬', opensource: '💻', tech: '🔧' }};
            const categoryImages = {{ rec: 'card-image-rec', agent: 'card-image-agent', llm: 'card-image-llm', industry: 'card-image-paper' }};
            
            container.innerHTML = filtered.map((item, i) => {{
                const cnTitle = item.cn_title || item.title;
                const cnSummary = item.cn_summary || item.summary || '';
                return `
                    <div class="card" onclick="showArticleDetail(${{i}}, '${{filter}}')">
                        <div class="card-image ${{item.cover_image ? '' : (categoryImages[item.category] || 'card-image-article')}}" style="${{item.cover_image ? `background-image: url('${{item.cover_image}}')` : ''}}">
                            <div class="card-image-icon">${{item.cover_image ? '' : (categoryEmoji[item.category] || '🔥')}}</div>
                            <div class="card-image-badge">HOT</div>
                        </div>
                        <div class="card-body">
                            <div class="card-header">
                                <div class="card-rank ${{i < 3 ? ['gold', 'silver', 'bronze'][i] : 'normal'}}">${{i + 1}}</div>
                                <div class="card-meta">
                                    <span class="card-category ${{item.category}}">${{categoryEmoji[item.category] || '🔥'}} ${{categoryLabels[item.category] || item.category}}</span>
                                    <h3 class="card-title">${{cnTitle}}</h3>
                                    <div class="card-source"><i class="fas fa-external-link-alt"></i> ${{item.source}}</div>
                                </div>
                            </div>
                            <p class="card-summary">${{cnSummary}}</p>
                            <div class="card-footer">
                                <div class="card-stats">
                                    <span class="card-stat"><i class="fas fa-eye" style="color:#60a5fa"></i> ${{item.views || 0}}</span>
                                    <span class="card-stat"><i class="fas fa-heart" style="color:#f87171"></i> ${{item.likes || 0}}</span>
                                </div>
                                <span class="card-link">查看详情 <i class="fas fa-chevron-right"></i></span>
                            </div>
                        </div>
                    </div>
                `;
            }}).join('');
            
            // 添加"查看更多"按钮（如果有超过5篇）
            if (filtered.length > 5) {{
                const moreBtn = document.createElement('button');
                moreBtn.className = 'view-more-btn';
                moreBtn.innerHTML = `<i class="fas fa-book-open"></i> 查看剩余 ${{filtered.length - 5}} 篇文章 <i class="fas fa-chevron-right"></i>`;
                moreBtn.onclick = () => window.location.href = 'articles.html';
                container.appendChild(moreBtn);
            }}
        }}
        
        // 显示文章详情弹窗
        function showArticleDetail(index, filter) {{
            const filtered = filter === 'all' ? hotArticles : hotArticles.filter(a => a.category === filter);
            const item = filtered[index];
            if (!item) return;
            
            const cnTitle = item.cn_title || item.title || '未知标题';
            const cnSummary = item.cn_summary || item.summary || '暂无摘要';
            
            let detailHtml = `
                <div class="detail-section">
                    <div class="detail-label">标题</div>
                    <div class="detail-value">${{item.title || '未知标题'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">来源</div>
                    <div class="detail-value">${{item.source || '未知来源'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">发布时间</div>
                    <div class="detail-value">${{item.published || '未知'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">摘要</div>
                    <div class="detail-value">${{cnSummary}}</div>
                </div>
            `;
            
            if (item.category) {{
                detailHtml += `
                    <div class="detail-section">
                        <div class="detail-label">分类</div>
                        <div class="detail-tags"><span class="detail-tag">${{item.category}}</span></div>
                    </div>
                `;
            }}
            
            const footerHtml = `<a href="${{item.link || '#'}}" target="_blank" class="detail-link"><i class="fas fa-external-link-alt"></i> 阅读原文</a>`;
            
            document.getElementById('detail-modal-title').innerHTML = `📰 ${{cnTitle}}`;
            document.getElementById('detail-modal-body').innerHTML = detailHtml;
            document.getElementById('detail-modal-footer').innerHTML = footerHtml;
            document.getElementById('detail-modal').classList.add('active');
        }}
        
        // 渲染GitHub项目
        function renderGithub() {{
            const container = document.getElementById('github-list');
            const langColors = {{ Python: '#3572A5', JavaScript: '#f1e05a', TypeScript: '#2b7489', Java: '#b07219', Go: '#00ADD8', Rust: '#dea584', 'C++': '#f34b7d' }};
            
            container.innerHTML = githubProjects.slice(0, 5).map((item, i) => {{
                const cnTitle = item.cn_title || item.name;
                const cnSummary = item.cn_summary || item.description;
                return `
                    <div class="card" onclick="showGithubDetail(${{i}})">
                        <div class="card-image ${{item.cover_image ? '' : 'card-image-github'}}" style="${{item.cover_image ? `background-image: url('${{item.cover_image}}')` : ''}}">
                            <div class="card-image-icon">${{item.cover_image ? '' : '<i class="fab fa-github"></i>'}}</div>
                            <div class="card-image-badge">${{item.language || 'Code'}}</div>
                            ${{item.growth_rate ? `<div class="card-image-trending"><i class="fas fa-chart-line"></i> +${{item.growth_rate.toFixed(1)}}% 增长</div>` : ''}}
                        </div>
                        <div class="card-body">
                            <div class="card-header">
                                <div class="card-rank ${{i < 3 ? ['gold', 'silver', 'bronze'][i] : 'normal'}}">${{i + 1}}</div>
                                <div class="card-meta">
                                    <span class="card-category github"><i class="fas fa-fire"></i> Trending</span>
                                    <h3 class="card-title">${{cnTitle}}</h3>
                                    <div class="card-source">
                                        <span style="color:${{langColors[item.language] || '#6b7280'}}">●</span> ${{item.language || 'Code'}}
                                        ${{item.topics && item.topics.length ? ' · ' + item.topics.slice(0,2).join(', ') : ''}}
                                    </div>
                                </div>
                            </div>
                            <p class="card-summary">${{cnSummary}}</p>
                            <div class="card-footer">
                                <div class="card-stats">
                                    <span class="card-stat"><i class="fas fa-star" style="color:#fbbf24"></i> ${{(item.stars || 0).toLocaleString()}}</span>
                                    <span class="card-stat"><i class="fas fa-code-branch" style="color:#60a5fa"></i> ${{(item.forks || 0).toLocaleString()}}</span>
                                </div>
                                <span class="card-link">查看详情 <i class="fas fa-chevron-right"></i></span>
                            </div>
                        </div>
                    </div>
                `;
            }}).join('');
        }}
        
        // 显示 GitHub 项目详情弹窗
        function showGithubDetail(index) {{
            const item = githubProjects[index];
            if (!item) return;
            
            const cnTitle = item.cn_title || item.name || item.full_name || '未知项目';
            // 优先使用中文摘要，确保完整显示
            const cnSummary = item.cn_summary || item.description || '暂无描述';
            const fullDesc = item.description || cnSummary;
            
            let detailHtml = `
                <div class="detail-section">
                    <div class="detail-label">项目名称</div>
                    <div class="detail-value">${{item.full_name || item.name || '未知项目'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">语言</div>
                    <div class="detail-value">${{item.language || '未知'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">统计</div>
                    <div class="detail-value">
                        ⭐ ${{(item.stars || 0).toLocaleString()}} Stars · 
                        🍴 ${{item.forks || 0}} Forks · 
                        📈 +${{(item.growth_rate || 0).toFixed(1)}}% 增长
                    </div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">中文简介</div>
                    <div class="detail-value">${{cnSummary}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">英文描述</div>
                    <div class="detail-value" style="font-size:12px; color:#64748b;">${{fullDesc}}</div>
                </div>
            `;
            
            if (item.topics && item.topics.length > 0) {{
                detailHtml += `
                    <div class="detail-section">
                        <div class="detail-label">标签</div>
                        <div class="detail-tags">${{item.topics.slice(0, 6).map(t => `<span class="detail-tag">${{t}}</span>`).join('')}}</div>
                    </div>
                `;
            }}
            
            const footerHtml = `<a href="${{item.url || '#'}}" target="_blank" class="detail-link"><i class="fab fa-github"></i> 访问 GitHub</a>`;
            
            document.getElementById('detail-modal-title').innerHTML = `💻 ${{cnTitle}}`;
            document.getElementById('detail-modal-body').innerHTML = detailHtml;
            document.getElementById('detail-modal-footer').innerHTML = footerHtml;
            document.getElementById('detail-modal').classList.add('active');
        }}
        
        // 渲染论文
        function renderPapers() {{
            const container = document.getElementById('papers-list');
            const categoryEmoji = {{ rec: '📊', agent: '🤖', llm: '🧠', industry: '🏭' }};
            const categoryImages = {{ rec: 'card-image-rec', agent: 'card-image-agent', llm: 'card-image-llm', industry: 'card-image-paper' }};
            
            // 展示前5篇
            container.innerHTML = arxivPapers.slice(0, 5).map((item, i) => {{
                const cnTitle = item.cn_title || (item.title ? item.title.slice(0, 40) + '...' : '论文');
                const cnSummary = item.cn_summary || '本文在推荐系统相关领域做出了创新研究，提出了新的方法和见解。';
                // 论文解读页面链接
                const paperId = (item.id || item.arxiv_id || '').replace('/', '_').replace('.', '_');
                const insightUrl = `docs/insights/${{data.date}}_${{paperId}}.html`;
                return `
                    <div class="card" onclick="window.location.href='${{insightUrl}}'">
                        <div class="card-image ${{item.cover_image ? '' : (categoryImages[item.category] || 'card-image-paper')}}" style="${{item.cover_image ? `background-image: url('${{item.cover_image}}')` : ''}}">
                            <div class="card-image-icon">${{item.cover_image ? '' : '📄'}}</div>
                            <div class="card-image-badge">arXiv</div>
                        </div>
                        <div class="card-body">
                            <div class="card-header">
                                <div class="card-rank ${{i < 3 ? ['gold', 'silver', 'bronze'][i] : 'normal'}}">${{i + 1}}</div>
                                <div class="card-meta">
                                    <span class="card-category ${{item.category}}">${{categoryEmoji[item.category] || '📄'}} ${{categoryLabels[item.category] || '论文'}}</span>
                                    <h3 class="card-title">${{cnTitle}}</h3>
                                    <div class="card-source"><i class="fas fa-users"></i> ${{item.authors ? item.authors.slice(0,2).join(', ') : 'Unknown'}}</div>
                                </div>
                            </div>
                            <p class="card-summary">${{cnSummary}}</p>
                            <div class="card-footer">
                                <div class="card-stats">
                                    <span class="card-stat"><i class="fas fa-calendar" style="color:#10b981"></i> ${{item.published}}</span>
                                </div>
                                <span class="card-link">查看解读 <i class="fas fa-chevron-right"></i></span>
                            </div>
                        </div>
                    </div>
                `;
            }}).join('');
            
            // 添加"查看更多"按钮（如果有超过5篇）
            if (arxivPapers.length > 5) {{
                const moreBtn = document.createElement('button');
                moreBtn.className = 'view-more-btn';
                moreBtn.innerHTML = `<i class="fas fa-book-open"></i> 查看剩余 ${{arxivPapers.length - 5}} 篇论文 <i class="fas fa-chevron-right"></i>`;
                moreBtn.onclick = () => window.location.href = 'papers.html';
                container.appendChild(moreBtn);
            }}
        }}
        
        // 显示论文详情弹窗
        function showPaperDetail(index) {{
            const item = arxivPapers[index];
            if (!item) return;
            
            const cnTitle = item.cn_title || item.title || '未知标题';
            // 优先使用中文摘要，确保完整显示
            const cnSummary = item.cn_summary || '暂无中文摘要';
            const fullSummary = item.summary || '';
            
            let detailHtml = `
                <div class="detail-section">
                    <div class="detail-label">标题</div>
                    <div class="detail-value">${{item.title || '未知标题'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">作者</div>
                    <div class="detail-value">${{(item.authors || []).join(', ') || '未知'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">发布时间</div>
                    <div class="detail-value">${{item.published || '未知'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">中文解读</div>
                    <div class="detail-value">${{cnSummary}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">英文摘要</div>
                    <div class="detail-value" style="font-size:12px; color:#64748b;">${{fullSummary}}</div>
                </div>
            `;
            
            if (item.category) {{
                detailHtml += `
                    <div class="detail-section">
                        <div class="detail-label">分类</div>
                        <div class="detail-tags"><span class="detail-tag">${{item.category}}</span></div>
                    </div>
                `;
            }}
            
            // 论文解读页面链接
            const paperId = (item.id || '').replace('/', '_').replace('.', '_');
            const insightUrl = `docs/insights/${{data.date}}_${{paperId}}.html`;
            
            // 论文弹窗只显示解读按钮，不显示原文链接
            const footerHtml = `<a href="${{insightUrl}}" class="detail-link"><i class="fas fa-book-open"></i> 查看论文解读</a>`;
            
            document.getElementById('detail-modal-title').innerHTML = `📄 ${{cnTitle}}`;
            document.getElementById('detail-modal-body').innerHTML = detailHtml;
            document.getElementById('detail-modal-footer').innerHTML = footerHtml;
            document.getElementById('detail-modal').classList.add('active');
        }}
        
        // 显示会议详情弹窗
        function showConfDetail(confName) {{
            const conf = conferenceData[confName];
            if (!conf) return;
            
            let detailHtml = `
                <div class="detail-section">
                    <div class="detail-label">会议名称</div>
                    <div class="detail-value">${{conf.name || confName}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">举办时间</div>
                    <div class="detail-value">${{conf.date || '待定'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">举办地点</div>
                    <div class="detail-value">${{conf.location || '待定'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">论文数量</div>
                    <div class="detail-value">${{conf.total || 0}} 篇</div>
                </div>
            `;
            
            if (conf.acceptance_rate) {{
                detailHtml += `
                    <div class="detail-section">
                        <div class="detail-label">录用率</div>
                        <div class="detail-value">${{conf.acceptance_rate}}</div>
                    </div>
                `;
            }}
            
            // 显示论文列表
            if (conf.papers && conf.papers.length > 0) {{
                detailHtml += `
                    <div class="detail-section">
                        <div class="detail-label">论文列表</div>
                        <div style="max-height: 200px; overflow-y: auto;">
                `;
                conf.papers.slice(0, 10).forEach((paper, i) => {{
                    detailHtml += `
                        <div style="padding: 8px 0; border-bottom: 1px solid #e2e8f0; font-size: 13px;">
                            <div style="font-weight: 500;">${{i + 1}}. ${{paper.title || '未知标题'}}</div>
                            <div style="color: #64748b; font-size: 11px;">${{paper.authors ? paper.authors.slice(0,2).join(', ') : ''}}</div>
                        </div>
                    `;
                }});
                if (conf.papers.length > 10) {{
                    detailHtml += `<div style="padding: 8px 0; color: #64748b; font-size: 12px;">还有 ${{conf.papers.length - 10}} 篇论文...</div>`;
                }}
                detailHtml += `</div></div>`;
            }}
            
            document.getElementById('detail-modal-title').innerHTML = `🏆 ${{conf.name || confName}}`;
            document.getElementById('detail-modal-body').innerHTML = detailHtml;
            document.getElementById('detail-modal-footer').innerHTML = '';  // 会议详情无按钮
            document.getElementById('detail-modal').classList.add('active');
        }}
        
        // Tab切换
        document.querySelectorAll('.tab').forEach(tab => {{
            tab.addEventListener('click', () => {{
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                renderHotArticles(tab.dataset.tab);
            }});
        }});
        
        // ========== 搜索功能 ==========
        let searchFilter = 'all';
        const allItems = [
            ...arxivPapers.map(p => ({{...p, type: 'paper', searchType: 'paper'}})),
            ...githubProjects.map(p => ({{...p, type: 'project', searchType: 'project', title: p.name, summary: p.description}})),
            ...hotArticles.map(a => ({{...a, type: 'article', searchType: 'article'}}))
        ];
        
        function openSearch() {{
            document.getElementById('searchModal').classList.add('active');
            document.getElementById('searchInput').focus();
            document.body.style.overflow = 'hidden';
        }}
        
        function closeSearch() {{
            document.getElementById('searchModal').classList.remove('active');
            document.body.style.overflow = '';
        }}
        
        function setSearchFilter(filter) {{
            searchFilter = filter;
            document.querySelectorAll('.search-filter').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.filter === filter);
            }});
            doSearch();
        }}
        
        function doSearch() {{
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const results = document.getElementById('searchResults');
            
            if (!query) {{
                results.innerHTML = '<div class="search-empty"><i class="fas fa-search"></i><div>输入关键词开始搜索</div></div>';
                return;
            }}
            
            let filtered = allItems.filter(item => {{
                const matchFilter = searchFilter === 'all' || item.searchType === searchFilter;
                const matchQuery = (item.title || '').toLowerCase().includes(query) ||
                    (item.summary || '').toLowerCase().includes(query) ||
                    (item.authors && item.authors.join(' ').toLowerCase().includes(query));
                return matchFilter && matchQuery;
            }});
            
            if (filtered.length === 0) {{
                results.innerHTML = '<div class="search-empty"><i class="fas fa-inbox"></i><div>未找到相关内容</div></div>';
                return;
            }}
            
            const typeEmoji = {{ paper: '📄', project: '💻', article: '📰' }};
            const typeLabels = {{ paper: '论文', project: '项目', article: '文章' }};
            
            results.innerHTML = filtered.slice(0, 20).map(item => `
                <div class="card" onclick="closeSearch()">
                    <div class="card-body">
                        <div class="card-header">
                            <div class="card-meta">
                                <span class="card-category ${{item.category || 'rec'}}">${{typeEmoji[item.searchType]}} ${{typeLabels[item.searchType]}}</span>
                                <h3 class="card-title">${{item.title || item.name}}</h3>
                                <div class="card-source">${{item.authors ? item.authors.slice(0,2).join(', ') : (item.source || '')}}</div>
                            </div>
                        </div>
                        <p class="card-summary">${{(item.summary || item.description || '').slice(0, 100)}}...</p>
                        <div class="card-footer">
                            <div class="card-stats">
                                ${{item.stars ? `<span class="card-stat"><i class="fas fa-star" style="color:#fbbf24"></i> ${{item.stars.toLocaleString()}}</span>` : ''}}
                                ${{item.views ? `<span class="card-stat"><i class="fas fa-eye" style="color:#60a5fa"></i> ${{item.views}}</span>` : ''}}
                            </div>
                            <a href="${{item.link || item.url}}" target="_blank" class="card-link">查看详情 <i class="fas fa-arrow-right"></i></a>
                        </div>
                    </div>
                </div>
            `).join('');
        }}
        
        // ========== 收藏功能 ==========
        let favorites = JSON.parse(localStorage.getItem('ai_daily_favorites') || '[]');
        
        function toggleFavorite(id, type, title, link) {{
            const key = `${{type}}_${{id}}`;
            const index = favorites.findIndex(f => f.key === key);
            
            if (index > -1) {{
                favorites.splice(index, 1);
                showToast('已取消收藏');
            }} else {{
                favorites.push({{ key, id, type, title, link, time: Date.now() }});
                showToast('已添加收藏');
            }}
            
            localStorage.setItem('ai_daily_favorites', JSON.stringify(favorites));
            updateFavoriteButtons();
        }}
        
        function isFavorite(id, type) {{
            return favorites.some(f => f.key === `${{type}}_${{id}}`);
        }}
        
        function updateFavoriteButtons() {{
            document.querySelectorAll('.card-favorite').forEach(btn => {{
                const id = btn.dataset.id;
                const type = btn.dataset.type;
                btn.classList.toggle('active', isFavorite(id, type));
                btn.innerHTML = isFavorite(id, type) ? '<i class="fas fa-bookmark"></i>' : '<i class="far fa-bookmark"></i>';
            }});
        }}
        
        function showFavorites() {{
            if (favorites.length === 0) {{
                showToast('暂无收藏内容');
                return;
            }}
            
            const modal = document.createElement('div');
            modal.id = 'favorites-modal';
            modal.innerHTML = `
                <div class="modal-overlay" onclick="closeFavorites()"></div>
                <div class="modal-content">
                    <div class="modal-header">
                        <h3><i class="fas fa-bookmark"></i> 我的收藏</h3>
                        <button class="modal-close" onclick="closeFavorites()"><i class="fas fa-times"></i></button>
                    </div>
                    <div class="modal-body">
                        ${{favorites.map(f => `
                            <a href="${{f.link}}" target="_blank" class="archive-item">
                                <div class="archive-date">${{f.title.slice(0, 30)}}${{f.title.length > 30 ? '...' : ''}}</div>
                                <i class="fas fa-chevron-right"></i>
                            </a>
                        `).join('')}}
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            document.body.style.overflow = 'hidden';
        }}
        
        function closeFavorites() {{
            const modal = document.getElementById('favorites-modal');
            if (modal) {{
                modal.remove();
                document.body.style.overflow = '';
            }}
        }}
        
        // ========== 排序功能 ==========
        let currentSort = 'default';
        
        function sortItems(items, sortBy) {{
            const sorted = [...items];
            switch(sortBy) {{
                case 'score':
                    sorted.sort((a, b) => (b.overall_score || 0) - (a.overall_score || 0));
                    break;
                case 'stars':
                    sorted.sort((a, b) => (b.stars || 0) - (a.stars || 0));
                    break;
                case 'date':
                    sorted.sort((a, b) => new Date(b.published || b.updated_at || 0) - new Date(a.published || a.updated_at || 0));
                    break;
                case 'growth':
                    sorted.sort((a, b) => (b.growth_rate || 0) - (a.growth_rate || 0));
                    break;
                default:
                    break;
            }}
            return sorted;
        }}
        
        // ========== 返回顶部 ==========
        function scrollToTop() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        // ========== Toast提示 ==========
        function showToast(message) {{
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2000);
        }}
        
        // ========== 滚动效果 ==========
        const nav = document.getElementById('nav');
        const moduleNav = document.getElementById('moduleNav');
        const backToTop = document.getElementById('backToTop');
        const sections = ['daily-pick', 'hot', 'github', 'papers', 'conferences', 'sources'];
        
        window.addEventListener('scroll', () => {{
            const scrollY = window.scrollY;
            
            // 主导航变实色
            nav.classList.toggle('solid', scrollY > 50);
            
            // 模块导航显示/隐藏
            moduleNav.classList.toggle('visible', scrollY > 150);
            
            // 返回顶部按钮
            backToTop.classList.toggle('visible', scrollY > 400);
            
            // 高亮当前模块
            let currentSection = 'daily-pick';
            sections.forEach(id => {{
                const section = document.getElementById(id);
                if (section && section.offsetTop - 120 <= scrollY) {{
                    currentSection = id;
                }}
            }});
            
            document.querySelectorAll('.module-nav-item').forEach(item => {{
                item.classList.toggle('active', item.getAttribute('href') === '#' + currentSection);
            }});
        }});
        
        // 平滑滚动
        document.querySelectorAll('.module-nav-item').forEach(item => {{
            item.addEventListener('click', (e) => {{
                e.preventDefault();
                const targetId = item.getAttribute('href').slice(1);
                const target = document.getElementById(targetId);
                if (target) {{
                    // 使用scrollIntoView配合CSS的scroll-margin-top
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }});
        }});
        
        // 订阅弹窗
        function showSubscribeModal() {{
            document.getElementById('subscribeModal').style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }}
        
        function closeSubscribeModal() {{
            document.getElementById('subscribeModal').style.display = 'none';
            document.body.style.overflow = '';
        }}
        
        // 分享功能
        function shareReport() {{
            const shareData = {{
                title: 'AI推荐日报',
                text: '推荐算法 × AI Agent × LLM 前沿追踪，每日精选最值得阅读的内容',
                url: window.location.href
            }};
            
            if (navigator.share) {{
                navigator.share(shareData).catch(() => {{}});
            }} else {{
                // 复制链接
                navigator.clipboard.writeText(window.location.href).then(() => {{
                    alert('链接已复制到剪贴板！');
                }}).catch(() => {{
                    alert('分享链接：' + window.location.href);
                }});
            }}
        }}
        
        // 往期日报
        function showArchive() {{
            // 创建弹窗
            const modal = document.createElement('div');
            modal.id = 'archive-modal';
            modal.innerHTML = `
                <div class="modal-overlay" onclick="closeArchive()"></div>
                <div class="modal-content">
                    <div class="modal-header">
                        <h3><i class="fas fa-history"></i> 往期日报</h3>
                        <button class="modal-close" onclick="closeArchive()"><i class="fas fa-times"></i></button>
                    </div>
                    <div class="modal-body" id="archive-list">
                        <div class="archive-loading"><i class="fas fa-spinner fa-spin"></i> 加载中...</div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            document.body.style.overflow = 'hidden';
            
            // 加载归档列表
            fetch('archive/index.json')
                .then(r => r.json())
                .then(data => {{
                    const list = document.getElementById('archive-list');
                    if (data.archives && data.archives.length > 0) {{
                        list.innerHTML = data.archives.map(item => `
                            <a href="archive/${{item.date}}/index.html" class="archive-item">
                                <div class="archive-date">${{item.date}}</div>
                                <div class="archive-stats">
                                    <span><i class="fas fa-file-alt"></i> ${{item.papers}}篇</span>
                                    <span><i class="fab fa-github"></i> ${{item.projects}}个</span>
                                </div>
                                <i class="fas fa-chevron-right"></i>
                            </a>
                        `).join('');
                    }} else {{
                        list.innerHTML = '<div class="archive-empty">暂无往期日报</div>';
                    }}
                }})
                .catch(() => {{
                    document.getElementById('archive-list').innerHTML = '<div class="archive-error">加载失败，请稍后重试</div>';
                }});
        }}
        
        function closeArchive() {{
            const modal = document.getElementById('archive-modal');
            if (modal) {{
                modal.remove();
                document.body.style.overflow = '';
            }}
        }}
        
        // 初始化
        renderDailyPick();
        renderConferences();
        renderHotArticles();
        renderGithub();
        renderPapers();
    </script>
</body>
</html>'''
        
        return html
    
    def save_to_archive(self, data: dict, html: str):
        """保存到归档"""
        archive_path = self.archive_dir / self.today
        archive_path.mkdir(exist_ok=True)
        
        # 保存HTML
        (archive_path / "index.html").write_text(html, encoding="utf-8")
        
        # 保存JSON数据
        (archive_path / "data.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        # 更新索引
        self._update_archive_index(data)
        
        print(f"📁 已归档: {archive_path}")
    
    def _update_archive_index(self, data: dict):
        """更新归档索引"""
        index_file = self.archive_dir / "index.json"
        
        if index_file.exists():
            index = json.loads(index_file.read_text(encoding="utf-8"))
        else:
            index = {"archives": [], "reports": []}
        
        # 确保 reports 字段存在
        if "reports" not in index:
            index["reports"] = []
        
        # 添加新条目
        index["reports"].insert(0, {
            "date": self.today,
            "total_papers": data.get("stats", {}).get("total_papers", 0),
            "total_projects": data.get("stats", {}).get("total_projects", 0),
            "total_articles": data.get("stats", {}).get("total_articles", 0)
        })
        
        # 保留最近90天
        index["reports"] = index["reports"][:90]
        
        index_file.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def run(self) -> str:
        """执行日报生成"""
        print(f"\n{'='*50}")
        print(f"📝 生成AI推荐日报 - {self.today}")
        print(f"{'='*50}\n")
        
        # 加载数据
        data = self.load_today_data()
        if not data:
            return None
        
        # 生成HTML
        html = self.generate_html(data)
        
        # 保存到归档
        self.save_to_archive(data, html)
        
        # 同时保存到主目录
        main_path = self.base_dir / "index.html"
        main_path.write_text(html, encoding="utf-8")
        
        print(f"\n{'='*50}")
        print(f"✅ 日报生成完成！")
        print(f"   📄 主文件: {main_path}")
        print(f"   📁 归档: {self.archive_dir / self.today}")
        print(f"{'='*50}\n")
        
        return str(main_path)


if __name__ == "__main__":
    generator = ReportGenerator()
    html_path = generator.run()
    if html_path:
        print(f"日报已生成: {html_path}")
        
        # 自动部署
        import subprocess
        from pathlib import Path
        base_dir = Path(__file__).parent.parent
        deploy_script = base_dir / "scripts" / "auto_deploy.sh"
        if deploy_script.exists():
            print("\n🚀 自动部署中...")
            subprocess.run(["bash", str(deploy_script)], cwd=str(base_dir))
