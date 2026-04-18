#!/usr/bin/env python3
"""
AI推荐日报 - 美化版日报生成脚本
基于 HTML UX 设计规范
"""

import json
from datetime import datetime
from pathlib import Path

class BeautifulReportGenerator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "daily_data"
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def load_data(self) -> dict:
        file_path = self.data_dir / f"{self.today}.json"
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_html(self) -> str:
        data = self.load_data()
        
        # 准备数据
        daily_pick = json.dumps(data.get('daily_pick', []), ensure_ascii=False)
        hot_articles = json.dumps(data.get('hot_articles', []), ensure_ascii=False)
        arxiv_papers = json.dumps(data.get('arxiv_papers', []), ensure_ascii=False)
        github_projects = json.dumps(data.get('github_projects', []), ensure_ascii=False)
        
        # 统计
        total_papers = len(data.get('arxiv_papers', []))
        total_projects = len(data.get('github_projects', []))
        total_articles = len(data.get('hot_articles', []))
        total_pick = len(data.get('daily_pick', []))
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI推荐日报 | {self.today}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/harmonyos-sans-sc@1.0.0/index.css">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --color-base: #EEEBFF;
            --color-flow: #D6E5FA;
            --color-spark: #D1F5EA;
            --color-text-anchor: #312C51;
            --color-text-secondary: rgba(49,44,81,0.68);
            --color-text-muted: rgba(49,44,81,0.40);
            --color-border: rgba(49,44,81,0.08);
            --color-card: #FFFFFF;
            --bg: #FAFAFA;
            --safe-area-top: env(safe-area-inset-top, 0px);
            --safe-area-bottom: env(safe-area-inset-bottom, 0px);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        
        body {{
            font-family: 'HarmonyOS Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: var(--bg);
            color: var(--color-text-anchor);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }}
        
        .number {{ font-family: 'Space Grotesk', sans-serif; }}
        
        /* Auroral Glow */
        .glow-container {{
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            overflow: visible; pointer-events: none; z-index: 0;
        }}
        .glow-ellipse {{ position: absolute; border-radius: 50%; }}
        .glow-1 {{ width: 800px; height: 600px; background: radial-gradient(ellipse, rgba(200,190,240,0.5) 0%, rgba(200,190,240,0.2) 40%, transparent 70%); filter: blur(80px); top: 400px; left: -200px; }}
        .glow-2 {{ width: 700px; height: 550px; background: radial-gradient(ellipse, rgba(160,200,245,0.45) 0%, rgba(160,200,245,0.15) 40%, transparent 70%); filter: blur(90px); top: 600px; right: -150px; }}
        .glow-3 {{ width: 600px; height: 500px; background: radial-gradient(ellipse, rgba(160,225,210,0.4) 0%, rgba(160,225,210,0.12) 40%, transparent 70%); filter: blur(70px); top: 1200px; left: 10%; }}
        .glow-4 {{ width: 750px; height: 580px; background: radial-gradient(ellipse, rgba(190,180,230,0.4) 0%, rgba(190,180,230,0.12) 40%, transparent 70%); filter: blur(85px); top: 1800px; right: -100px; }}
        .glow-5 {{ width: 650px; height: 520px; background: radial-gradient(ellipse, rgba(160,200,245,0.38) 0%, rgba(160,200,245,0.1) 40%, transparent 70%); filter: blur(75px); top: 2500px; left: -150px; }}
        .glow-6 {{ width: 550px; height: 450px; background: radial-gradient(ellipse, rgba(160,225,210,0.35) 0%, rgba(160,225,210,0.1) 40%, transparent 70%); filter: blur(70px); top: 3200px; right: 5%; }}
        
        /* Hero */
        .hero {{
            position: relative; z-index: 1;
            padding: 100px 0 60px; text-align: center;
            margin-left: calc(-50vw + 50%); margin-right: calc(-50vw + 50%);
            width: 100vw; overflow: visible;
        }}
        .hero::before {{
            content: '';
            position: absolute; top: -80px; left: -20%; right: -20%; bottom: -100px;
            z-index: 0;
            background:
                radial-gradient(ellipse 90% 80% at 10% 20%, rgba(200,190,240,0.7) 0%, rgba(200,190,240,0.3) 30%, transparent 60%),
                radial-gradient(ellipse 80% 90% at 85% 10%, rgba(160,200,245,0.65) 0%, rgba(160,200,245,0.25) 35%, transparent 55%),
                radial-gradient(ellipse 70% 60% at 60% 90%, rgba(160,225,210,0.5) 0%, rgba(160,225,210,0.2) 30%, transparent 50%),
                radial-gradient(ellipse 60% 70% at 20% 85%, rgba(190,180,230,0.45) 0%, rgba(190,180,230,0.15) 35%, transparent 55%),
                radial-gradient(ellipse 50% 45% at 50% 45%, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.4) 40%, transparent 70%),
                linear-gradient(160deg, rgba(238,235,255,0.6) 0%, rgba(214,229,250,0.4) 50%, rgba(209,245,234,0.3) 100%);
            filter: blur(2px);
            mask-image: linear-gradient(180deg, black 0%, black 50%, rgba(0,0,0,0.5) 75%, transparent 100%);
            -webkit-mask-image: linear-gradient(180deg, black 0%, black 50%, rgba(0,0,0,0.5) 75%, transparent 100%);
        }}
        .hero::after {{
            content: '';
            position: absolute; top: 0; left: -20%; right: -20%; bottom: 0;
            z-index: 1; opacity: 0.04;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
            pointer-events: none;
            mask-image: linear-gradient(180deg, black 0%, black 60%, transparent 100%);
            -webkit-mask-image: linear-gradient(180deg, black 0%, black 60%, transparent 100%);
        }}
        .hero > * {{ position: relative; z-index: 2; }}
        
        .hero-badge {{
            display: inline-flex; align-items: center; gap: 6px;
            background: rgba(255,255,255,0.95); padding: 6px 14px;
            border-radius: 16px; margin-bottom: 14px;
            box-shadow: 0 2px 10px rgba(49,44,81,0.06);
        }}
        .hero-badge-dot {{ width: 6px; height: 6px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
        .hero-badge-text {{ font-size: 11px; font-weight: 700; color: var(--color-text-secondary); }}
        
        .hero-title {{ font-size: 32px; font-weight: 700; margin-bottom: 12px; color: var(--color-text-anchor); letter-spacing: 2px; }}
        .hero-subtitle {{ font-size: 14px; color: var(--color-text-secondary); margin-bottom: 24px; max-width: 800px; padding: 0 16px; margin-left: auto; margin-right: auto; }}
        .hero-date {{ font-size: 12px; color: var(--color-text-muted); margin-bottom: 20px; }}
        
        .hero-stats {{
            display: flex; justify-content: center; gap: 16px;
            flex-wrap: wrap; padding: 0 16px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.95); border-radius: 16px;
            padding: 16px 24px; text-align: center;
            box-shadow: 0 4px 20px rgba(49,44,81,0.08);
            min-width: 100px;
        }}
        .stat-value {{ font-size: 26px; font-weight: 700; color: var(--color-text-anchor); }}
        .stat-label {{ font-size: 11px; color: var(--color-text-muted); margin-top: 4px; }}
        
        /* Navigation */
        .nav-container {{
            position: fixed; top: 0; left: 0; right: 0; z-index: 100;
            padding: 14px 20px; background: transparent; transition: background 0.3s ease;
            padding-top: calc(14px + var(--safe-area-top));
        }}
        .nav-container.nav-solid {{
            background: rgba(250,250,250,0.88);
            backdrop-filter: blur(12px);
        }}
        .nav-inner {{ max-width: 800px; margin: 0 auto; }}
        .nav-header {{ display: flex; align-items: center; justify-content: space-between; cursor: pointer; }}
        .nav-title {{ display: flex; align-items: center; gap: 12px; }}
        .nav-title-icon {{
            width: 36px; height: 36px; background: rgba(255,255,255,0.95);
            border-radius: 12px; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 2px 12px rgba(49,44,81,0.10);
            color: var(--color-text-anchor);
        }}
        .nav-title-text {{ font-size: 14px; font-weight: 700; color: var(--color-text-anchor); }}
        .nav-toggle {{
            display: flex; align-items: center; gap: 8px; padding: 10px 16px;
            background: rgba(255,255,255,0.9); border: none; border-radius: 12px;
            cursor: pointer; box-shadow: 0 2px 8px rgba(49,44,81,0.08);
        }}
        .nav-toggle-text {{ font-size: 12px; color: var(--color-text-secondary); }}
        .nav-toggle-icon {{ font-size: 12px; color: var(--color-text-muted); transition: transform 0.3s ease; }}
        .nav-container.expanded .nav-toggle-icon {{ transform: rotate(180deg); }}
        .nav-card {{
            background: rgba(255,255,255,0.82); backdrop-filter: blur(24px);
            border-radius: 16px; margin-top: 12px;
            box-shadow: 0 8px 32px rgba(49,44,81,0.12);
            max-height: 0; overflow: hidden; opacity: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .nav-container.expanded .nav-card {{ max-height: 500px; padding: 8px 0; opacity: 1; }}
        .nav-link {{
            display: flex; align-items: center; gap: 12px; padding: 14px 20px;
            text-decoration: none; color: var(--color-text-secondary); font-size: 14px;
        }}
        .nav-link:hover {{ background: rgba(238,235,255,0.4); color: var(--color-text-anchor); }}
        
        /* Main Content */
        .main {{
            position: relative; z-index: 1;
            max-width: 800px; margin: 0 auto;
            padding: 20px 16px 80px;
            padding-bottom: calc(80px + var(--safe-area-bottom));
        }}
        
        /* Section */
        .section {{ margin-bottom: 40px; }}
        .section-header {{
            display: flex; flex-direction: column; align-items: flex-start; gap: 6px;
            margin-bottom: 20px; padding: 0 4px;
        }}
        .section-number {{ font-size: 12px; font-weight: 700; color: var(--color-text-muted); }}
        .section-title {{ font-size: 18px; font-weight: 700; color: var(--color-text-anchor); }}
        .section-subtitle {{ font-size: 14px; color: var(--color-text-muted); }}
        
        /* Cards */
        .card {{
            background: var(--color-card); border-radius: 24px;
            margin-bottom: 16px; overflow: hidden;
            cursor: pointer; transition: transform 0.2s;
        }}
        .card:active {{ transform: scale(0.98); }}
        
        .card-image {{
            width: 100%; height: 160px;
            background-color: var(--color-flow);
            background-size: cover;
            background-position: center;
            position: relative;
        }}
        .card-image::before {{
            content: '';
            position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(180deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.3) 100%);
        }}
        .card-image-badge {{
            position: absolute; top: 12px; right: 12px; z-index: 2;
            background: rgba(255,255,255,0.95); color: var(--color-text-anchor);
            padding: 4px 12px; border-radius: 8px;
            font-size: 11px; font-weight: 700;
        }}
        .card-image-rank {{
            position: absolute; top: 12px; left: 12px; z-index: 2;
            width: 32px; height: 32px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 14px; font-weight: 700;
        }}
        .card-image-rank.gold {{ background: linear-gradient(135deg, #ffd700, #ffb700); }}
        .card-image-rank.silver {{ background: linear-gradient(135deg, #c0c0c0, #a8a8a8); }}
        .card-image-rank.bronze {{ background: linear-gradient(135deg, #cd7f32, #b8722d); }}
        
        .card-body {{ padding: 20px; }}
        .card-category {{
            display: inline-flex; align-items: center; gap: 4px;
            padding: 4px 12px; border-radius: 8px;
            font-size: 11px; font-weight: 700; margin-bottom: 8px;
            background: rgba(214,229,250,0.3); color: #667eea;
        }}
        .card-title {{
            font-size: 16px; font-weight: 700; line-height: 1.4;
            color: var(--color-text-anchor); margin-bottom: 8px;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
        }}
        .card-summary {{
            font-size: 13px; color: var(--color-text-secondary); line-height: 1.6;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
            margin-bottom: 12px;
        }}
        .card-meta {{
            display: flex; align-items: center; gap: 12px;
            font-size: 12px; color: var(--color-text-muted);
        }}
        .card-stats {{
            display: flex; gap: 16px;
            font-size: 12px; color: var(--color-text-muted);
        }}
        .card-action {{
            display: flex; align-items: center; gap: 4px;
            color: #667eea; font-size: 13px; font-weight: 600;
        }}
        
        /* Modal */
        .modal {{
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            z-index: 200; display: none;
        }}
        .modal.active {{ display: flex; flex-direction: column; justify-content: flex-end; }}
        .modal-overlay {{
            position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.5);
        }}
        .modal-content {{
            position: relative; z-index: 1;
            background: var(--color-card); border-radius: 24px 24px 0 0;
            max-height: 85vh; overflow: hidden;
            animation: slideUp 0.3s;
        }}
        @keyframes slideUp {{ from {{ transform: translateY(100%); }} to {{ transform: translateY(0); }} }}
        .modal-handle {{
            width: 36px; height: 4px; background: rgba(49,44,81,0.1);
            border-radius: 2px; margin: 12px auto;
        }}
        .modal-header {{
            padding: 0 20px 16px; border-bottom: 1px solid rgba(49,44,81,0.08);
        }}
        .modal-title {{ font-size: 18px; font-weight: 700; }}
        .modal-body {{
            padding: 20px; overflow-y: auto;
            max-height: calc(85vh - 100px);
        }}
        .detail-section {{ margin-bottom: 20px; }}
        .detail-label {{ font-size: 12px; color: var(--color-text-muted); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .detail-value {{ font-size: 14px; color: var(--color-text-anchor); line-height: 1.6; }}
        .detail-tags {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .detail-tag {{ background: rgba(214,229,250,0.3); padding: 4px 12px; border-radius: 8px; font-size: 12px; color: #667eea; }}
        .detail-link {{
            display: inline-flex; align-items: center; gap: 8px;
            background: linear-gradient(135deg, #667eea, #764ba2); color: white;
            padding: 12px 24px; border-radius: 12px; text-decoration: none;
            font-size: 14px; font-weight: 600; margin-top: 16px;
        }}
        
        /* Bottom Bar */
        .bottom-bar {{
            position: fixed; bottom: 0; left: 0; right: 0;
            background: rgba(255,255,255,0.95); backdrop-filter: blur(12px);
            border-top: 1px solid rgba(49,44,81,0.08);
            padding: 12px 16px;
            padding-bottom: calc(12px + var(--safe-area-bottom));
            display: flex; gap: 12px; z-index: 50;
        }}
        .bottom-btn {{
            flex: 1; height: 44px; border: none; border-radius: 12px;
            font-size: 14px; font-weight: 600; cursor: pointer;
            display: flex; align-items: center; justify-content: center; gap: 6px;
            transition: all 0.2s;
        }}
        .bottom-btn.primary {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; }}
        .bottom-btn.secondary {{ background: rgba(238,235,255,0.5); color: var(--color-text-anchor); }}
        .bottom-btn:active {{ transform: scale(0.98); }}
    </style>
</head>
<body>
    <!-- Auroral Glow -->
    <div class="glow-container">
        <div class="glow-ellipse glow-1"></div>
        <div class="glow-ellipse glow-2"></div>
        <div class="glow-ellipse glow-3"></div>
        <div class="glow-ellipse glow-4"></div>
        <div class="glow-ellipse glow-5"></div>
        <div class="glow-ellipse glow-6"></div>
    </div>
    
    <!-- Hero -->
    <div class="hero" id="hero">
        <div class="hero-badge">
            <div class="hero-badge-dot"></div>
            <span class="hero-badge-text">每日更新</span>
        </div>
        <h1 class="hero-title">AI 推荐日报</h1>
        <p class="hero-subtitle">推荐算法 × AI Agent × LLM 前沿追踪，每日精选最值得阅读的内容</p>
        <div class="hero-date">{self.today}</div>
        <div class="hero-stats">
            <div class="stat-card">
                <div class="stat-value number">{total_pick}</div>
                <div class="stat-label">精选内容</div>
            </div>
            <div class="stat-card">
                <div class="stat-value number">{total_papers}</div>
                <div class="stat-label">arXiv论文</div>
            </div>
            <div class="stat-card">
                <div class="stat-value number">{total_projects}</div>
                <div class="stat-label">GitHub项目</div>
            </div>
            <div class="stat-card">
                <div class="stat-value number">{total_articles}</div>
                <div class="stat-label">热门文章</div>
            </div>
        </div>
    </div>
    
    <!-- Navigation -->
    <nav class="nav-container" id="navContainer">
        <div class="nav-inner">
            <div class="nav-header" onclick="toggleNav()">
                <div class="nav-title">
                    <div class="nav-title-icon"><i class="fas fa-newspaper"></i></div>
                    <span class="nav-title-text">AI推荐日报</span>
                </div>
                <button class="nav-toggle">
                    <span class="nav-toggle-text">目录</span>
                    <i class="fas fa-chevron-down nav-toggle-icon"></i>
                </button>
            </div>
            <div class="nav-card">
                <a href="#section-pick" class="nav-link" onclick="closeNav()"><i class="fas fa-star"></i> 每日精选</a>
                <a href="#section-articles" class="nav-link" onclick="closeNav()"><i class="fas fa-fire"></i> 热门文章</a>
                <a href="#section-github" class="nav-link" onclick="closeNav()"><i class="fab fa-github"></i> GitHub项目</a>
                <a href="#section-papers" class="nav-link" onclick="closeNav()"><i class="fas fa-file-alt"></i> arXiv论文</a>
            </div>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="main">
        <!-- 每日精选 -->
        <section class="section" id="section-pick">
            <div class="section-header">
                <span class="section-number">01 · CHAPTER</span>
                <h2 class="section-title">每日精选</h2>
                <p class="section-subtitle">编辑精选，最值得阅读的内容</p>
            </div>
            <div id="pick-list"></div>
        </section>
        
        <!-- 热门文章 -->
        <section class="section" id="section-articles">
            <div class="section-header">
                <span class="section-number">02 · CHAPTER</span>
                <h2 class="section-title">热门文章</h2>
                <p class="section-subtitle">来自机器之心、量子位、知乎等平台</p>
            </div>
            <div id="articles-list"></div>
        </section>
        
        <!-- GitHub项目 -->
        <section class="section" id="section-github">
            <div class="section-header">
                <span class="section-number">03 · CHAPTER</span>
                <h2 class="section-title">GitHub 项目</h2>
                <p class="section-subtitle">热门开源项目，值得关注</p>
            </div>
            <div id="github-list"></div>
        </section>
        
        <!-- arXiv论文 -->
        <section class="section" id="section-papers">
            <div class="section-header">
                <span class="section-number">04 · CHAPTER</span>
                <h2 class="section-title">arXiv 论文</h2>
                <p class="section-subtitle">最新学术研究，前沿进展</p>
            </div>
            <div id="papers-list"></div>
        </section>
    </main>
    
    <!-- Modal -->
    <div class="modal" id="detailModal">
        <div class="modal-overlay" onclick="closeDetailModal()"></div>
        <div class="modal-content">
            <div class="modal-handle"></div>
            <div class="modal-header">
                <h3 class="modal-title" id="modalTitle"></h3>
            </div>
            <div class="modal-body" id="modalBody"></div>
        </div>
    </div>
    
    <!-- Bottom Bar -->
    <div class="bottom-bar">
        <button class="bottom-btn secondary" onclick="shareReport()">
            <i class="fas fa-share-alt"></i> 分享
        </button>
        <button class="bottom-btn primary" onclick="refreshData()">
            <i class="fas fa-sync-alt"></i> 刷新
        </button>
    </div>
    
    <script>
        // 数据
        const dailyPick = {daily_pick};
        const hotArticles = {hot_articles};
        const arxivPapers = {arxiv_papers};
        const githubProjects = {github_projects};
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {{
            renderPick();
            renderArticles();
            renderGithub();
            renderPapers();
            handleScrollEffects();
        }});
        
        // 渲染每日精选
        function renderPick() {{
            const container = document.getElementById('pick-list');
            container.innerHTML = dailyPick.map((item, i) => `
                <div class="card" onclick="showDetail('pick', ${{i}})">
                    <div class="card-image" style="background-image: url('${{item.cover_image || ''}}')">
                        <div class="card-image-rank ${{i < 3 ? ['gold', 'silver', 'bronze'][i] : ''}}">${{i + 1}}</div>
                        <div class="card-image-badge">${{item.pick_type === 'paper' ? '论文' : (item.pick_type === 'github' ? '项目' : '文章')}}</div>
                    </div>
                    <div class="card-body">
                        <div class="card-category">${{item.category || '精选'}}</div>
                        <h3 class="card-title">${{item.cn_title || item.title || item.name}}</h3>
                        <p class="card-summary">${{(item.cn_summary || item.summary || item.description || '').slice(0, 100)}}</p>
                        <div class="card-meta">
                            <span><i class="far fa-clock"></i> ${{item.published || ''}}</span>
                            <span><i class="far fa-user"></i> ${{item.source || 'arXiv'}}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }}
        
        // 渲染热门文章
        function renderArticles() {{
            const container = document.getElementById('articles-list');
            container.innerHTML = hotArticles.slice(0, 10).map((item, i) => `
                <div class="card" onclick="showDetail('article', ${{i}})">
                    <div class="card-image" style="background-image: url('${{item.cover_image || ''}}')">
                        <div class="card-image-rank ${{i < 3 ? ['gold', 'silver', 'bronze'][i] : ''}}">${{i + 1}}</div>
                        <div class="card-image-badge">${{item.source || '文章'}}</div>
                    </div>
                    <div class="card-body">
                        <div class="card-category">${{item.category || '热门'}}</div>
                        <h3 class="card-title">${{item.cn_title || item.title}}</h3>
                        <p class="card-summary">${{(item.cn_summary || item.summary || '').slice(0, 100)}}</p>
                        <div class="card-meta">
                            <span><i class="far fa-clock"></i> ${{item.published || ''}}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }}
        
        // 渲染GitHub项目
        function renderGithub() {{
            const container = document.getElementById('github-list');
            container.innerHTML = githubProjects.slice(0, 6).map((item, i) => `
                <div class="card" onclick="showDetail('github', ${{i}})">
                    <div class="card-image" style="background-image: url('${{item.cover_image || ''}}')">
                        <div class="card-image-rank ${{i < 3 ? ['gold', 'silver', 'bronze'][i] : ''}}">${{i + 1}}</div>
                        <div class="card-image-badge">${{item.language || 'Code'}}</div>
                    </div>
                    <div class="card-body">
                        <div class="card-category">GitHub</div>
                        <h3 class="card-title">${{item.cn_title || item.name}}</h3>
                        <p class="card-summary">${{(item.cn_summary || item.description || '').slice(0, 100)}}</p>
                        <div class="card-stats">
                            <span><i class="fas fa-star" style="color:#fbbf24"></i> <span class="number">${{(item.stars || 0).toLocaleString()}}</span></span>
                            <span><i class="fas fa-code-branch"></i> <span class="number">${{item.forks || 0}}</span></span>
                        </div>
                    </div>
                </div>
            `).join('');
        }}
        
        // 渲染论文
        function renderPapers() {{
            const container = document.getElementById('papers-list');
            container.innerHTML = arxivPapers.slice(0, 8).map((item, i) => `
                <div class="card" onclick="showDetail('paper', ${{i}})">
                    <div class="card-image" style="background-image: url('${{item.cover_image || ''}}')">
                        <div class="card-image-rank ${{i < 3 ? ['gold', 'silver', 'bronze'][i] : ''}}">${{i + 1}}</div>
                        <div class="card-image-badge">arXiv</div>
                    </div>
                    <div class="card-body">
                        <div class="card-category">${{item.category || '论文'}}</div>
                        <h3 class="card-title">${{item.cn_title || item.title}}</h3>
                        <p class="card-summary">${{(item.cn_summary || item.summary || '').slice(0, 100)}}</p>
                        <div class="card-meta">
                            <span><i class="far fa-clock"></i> ${{item.published || ''}}</span>
                            <span><i class="fas fa-users"></i> ${{(item.authors || []).slice(0, 2).join(', ')}}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }}
        
        // 显示详情
        function showDetail(type, index) {{
            let item;
            if (type === 'pick') item = dailyPick[index];
            else if (type === 'article') item = hotArticles[index];
            else if (type === 'github') item = githubProjects[index];
            else if (type === 'paper') item = arxivPapers[index];
            
            if (!item) return;
            
            const title = item.cn_title || item.title || item.name || '未知';
            const summary = item.cn_summary || item.summary || item.description || '暂无简介';
            
            let html = `
                <div class="detail-section">
                    <div class="detail-label">标题</div>
                    <div class="detail-value">${{item.title || item.name || title}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">简介</div>
                    <div class="detail-value">${{summary}}</div>
                </div>
            `;
            
            if (item.source) html += `<div class="detail-section"><div class="detail-label">来源</div><div class="detail-value">${{item.source}}</div></div>`;
            if (item.published) html += `<div class="detail-section"><div class="detail-label">时间</div><div class="detail-value">${{item.published}}</div></div>`;
            if (item.authors) html += `<div class="detail-section"><div class="detail-label">作者</div><div class="detail-value">${{item.authors.join(', ')}}</div></div>`;
            if (item.stars) html += `<div class="detail-section"><div class="detail-label">统计</div><div class="detail-value">⭐ ${{item.stars.toLocaleString()}} Stars · 🍴 ${{item.forks}} Forks</div></div>`;
            
            const link = item.link || item.url;
            if (link) html += `<a href="${{link}}" target="_blank" class="detail-link"><i class="fas fa-external-link-alt"></i> 查看详情</a>`;
            
            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalBody').innerHTML = html;
            document.getElementById('detailModal').classList.add('active');
        }}
        
        function closeDetailModal() {{
            document.getElementById('detailModal').classList.remove('active');
        }}
        
        // 导航
        function toggleNav() {{ document.getElementById('navContainer').classList.toggle('expanded'); }}
        function closeNav() {{ document.getElementById('navContainer').classList.remove('expanded'); }}
        
        document.addEventListener('click', e => {{
            if (!document.getElementById('navContainer').contains(e.target)) closeNav();
        }});
        
        document.querySelectorAll('a[href^="#"]').forEach(a => {{
            a.addEventListener('click', e => {{
                e.preventDefault();
                document.querySelector(a.getAttribute('href'))?.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }});
        }});
        
        // 滚动效果
        function handleScrollEffects() {{
            const scrollY = window.scrollY;
            const heroEl = document.getElementById('hero');
            const navEl = document.getElementById('navContainer');
            const bannerFadeEnd = heroEl.offsetHeight * 0.6;
            
            navEl.classList.toggle('nav-solid', scrollY > bannerFadeEnd);
        }}
        
        window.addEventListener('scroll', handleScrollEffects, {{ passive: true }});
        
        // 分享和刷新
        function shareReport() {{
            if (navigator.share) {{
                navigator.share({{ title: 'AI推荐日报', url: location.href }});
            }} else {{
                alert('链接已复制');
            }}
        }}
        
        function refreshData() {{ location.reload(); }}
    </script>
</body>
</html>'''
        return html
    
    def save(self, html: str):
        output_file = self.base_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ 日报已生成: {output_file}")


if __name__ == "__main__":
    generator = BeautifulReportGenerator()
    html = generator.generate_html()
    generator.save(html)
