#!/usr/bin/env python3
"""
AI推荐日报 - 增强版日报生成脚本
包含题图、简介、交互式详情页面
"""

import json
from datetime import datetime
from pathlib import Path
import base64

class EnhancedReportGenerator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "daily_data"
        self.cache_dir = self.base_dir / "cache"
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def load_data(self) -> dict:
        """加载所有数据"""
        # 加载日报数据
        daily_file = self.data_dir / f"{self.today}.json"
        if daily_file.exists():
            with open(daily_file, 'r', encoding='utf-8') as f:
                daily_data = json.load(f)
        else:
            daily_data = {}
        
        # 加载文章缓存
        articles_file = self.cache_dir / "all_articles.json"
        if articles_file.exists():
            with open(articles_file, 'r', encoding='utf-8') as f:
                articles_data = json.load(f)
        else:
            articles_data = {'items': []}
        
        # 加载 arXiv 缓存
        arxiv_file = self.cache_dir / "arxiv_cache.json"
        if arxiv_file.exists():
            with open(arxiv_file, 'r', encoding='utf-8') as f:
                arxiv_data = json.load(f)
        else:
            arxiv_data = {'items': []}
        
        # 加载 GitHub 缓存
        github_file = self.cache_dir / "github_cache.json"
        if github_file.exists():
            with open(github_file, 'r', encoding='utf-8') as f:
                github_data = json.load(f)
        else:
            github_data = {'items': []}
        
        return {
            'daily': daily_data,
            'articles': articles_data.get('items', [])[:20],
            'arxiv': arxiv_data.get('items', [])[:10],
            'github': github_data.get('items', [])[:6]
        }
    
    def generate_html(self) -> str:
        """生成增强版 HTML"""
        data = self.load_data()
        
        # 生成 SVG 题图
        cover_svg = self.generate_cover_svg()
        
        # 准备数据
        articles_json = json.dumps(data['articles'], ensure_ascii=False)
        arxiv_json = json.dumps(data['arxiv'], ensure_ascii=False)
        github_json = json.dumps(data['github'], ensure_ascii=False)
        
        # 统计数据
        total_papers = len(data['arxiv'])
        total_projects = len(data['github'])
        total_articles = len(data['articles'])
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI推荐日报 | {self.today}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #ec4899;
            --accent: #f59e0b;
            --success: #10b981;
            --text: #1e293b;
            --text-secondary: #64748b;
            --text-muted: #94a3b8;
            --bg: #f8fafc;
            --card: #ffffff;
            --border: #e2e8f0;
            --gradient-hero: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            --gradient-card: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(236,72,153,0.1) 100%);
            --safe-area-top: env(safe-area-inset-top, 0px);
            --safe-area-bottom: env(safe-area-inset-bottom, 0px);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }}
        
        /* 题图区域 */
        .cover {{
            position: relative;
            width: 100%;
            min-height: 320px;
            background: var(--gradient-hero);
            overflow: hidden;
        }}
        
        .cover-bg {{
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            opacity: 0.15;
        }}
        
        .cover-content {{
            position: relative;
            z-index: 2;
            padding: 60px 20px 40px;
            padding-top: calc(60px + var(--safe-area-top));
            text-align: center;
            color: white;
        }}
        
        .cover-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            padding: 6px 14px;
            border-radius: 20px;
            margin-bottom: 16px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .cover-badge i {{ color: #fbbf24; }}
        
        .cover-title {{
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 12px;
            text-shadow: 0 2px 20px rgba(0,0,0,0.2);
            letter-spacing: 2px;
        }}
        
        .cover-subtitle {{
            font-size: 15px;
            opacity: 0.95;
            margin-bottom: 24px;
            max-width: 300px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .cover-date {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255,255,255,0.15);
            padding: 8px 16px;
            border-radius: 12px;
            font-size: 13px;
        }}
        
        .cover-stats {{
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-top: 24px;
        }}
        
        .cover-stat {{
            text-align: center;
        }}
        
        .cover-stat-value {{
            font-size: 24px;
            font-weight: 700;
        }}
        
        .cover-stat-label {{
            font-size: 11px;
            opacity: 0.8;
        }}
        
        /* 装饰元素 */
        .cover-deco {{
            position: absolute;
            border-radius: 50%;
            background: rgba(255,255,255,0.1);
        }}
        
        .deco-1 {{ width: 200px; height: 200px; top: -50px; right: -50px; }}
        .deco-2 {{ width: 150px; height: 150px; bottom: 30px; left: -30px; }}
        .deco-3 {{ width: 80px; height: 80px; top: 100px; left: 20%; }}
        
        /* 导航 */
        .nav {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(248,250,252,0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 12px 16px;
        }}
        
        .nav-inner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            max-width: 600px;
            margin: 0 auto;
        }}
        
        .nav-title {{
            font-size: 16px;
            font-weight: 700;
            color: var(--primary);
        }}
        
        .nav-actions {{
            display: flex;
            gap: 8px;
        }}
        
        .nav-btn {{
            width: 36px;
            height: 36px;
            border: none;
            background: var(--gradient-card);
            border-radius: 10px;
            color: var(--text-secondary);
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }}
        
        .nav-btn:active {{
            transform: scale(0.95);
            background: var(--primary);
            color: white;
        }}
        
        /* 主内容 */
        .main {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px 16px 80px;
            padding-bottom: calc(80px + var(--safe-area-bottom));
        }}
        
        /* 区块 */
        .section {{
            margin-bottom: 32px;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .section-title i {{
            color: var(--primary);
        }}
        
        .section-more {{
            font-size: 13px;
            color: var(--text-muted);
            text-decoration: none;
        }}
        
        /* 卡片 */
        .card {{
            background: var(--card);
            border-radius: 16px;
            margin-bottom: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            overflow: hidden;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .card:active {{
            transform: scale(0.98);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .card-content {{
            padding: 16px;
        }}
        
        .card-header {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 10px;
        }}
        
        .card-icon {{
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
        }}
        
        .card-icon.paper {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; }}
        .card-icon.github {{ background: linear-gradient(135deg, #1e293b, #334155); color: white; }}
        .card-icon.article {{ background: linear-gradient(135deg, #f59e0b, #f97316); color: white; }}
        .card-icon.hot {{ background: linear-gradient(135deg, #ec4899, #f43f5e); color: white; }}
        
        .card-title-wrap {{
            flex: 1;
            min-width: 0;
        }}
        
        .card-title {{
            font-size: 15px;
            font-weight: 600;
            color: var(--text);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.4;
        }}
        
        .card-meta {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 6px;
            font-size: 12px;
            color: var(--text-muted);
        }}
        
        .card-tag {{
            background: var(--gradient-card);
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 11px;
            color: var(--primary);
            font-weight: 500;
        }}
        
        .card-desc {{
            font-size: 13px;
            color: var(--text-secondary);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.5;
        }}
        
        .card-footer {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid var(--border);
        }}
        
        .card-stats {{
            display: flex;
            gap: 12px;
            font-size: 12px;
            color: var(--text-muted);
        }}
        
        .card-stats span {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        
        .card-action {{
            color: var(--primary);
            font-size: 13px;
            font-weight: 500;
        }}
        
        /* 详情弹窗 */
        .modal {{
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            z-index: 200;
            display: none;
        }}
        
        .modal.active {{
            display: flex;
            flex-direction: column;
        }}
        
        .modal-overlay {{
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.5);
            animation: fadeIn 0.2s;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .modal-content {{
            position: relative;
            z-index: 1;
            background: var(--card);
            border-radius: 24px 24px 0 0;
            margin-top: auto;
            max-height: 85vh;
            overflow: hidden;
            animation: slideUp 0.3s;
        }}
        
        @keyframes slideUp {{
            from {{ transform: translateY(100%); }}
            to {{ transform: translateY(0); }}
        }}
        
        .modal-handle {{
            width: 36px;
            height: 4px;
            background: var(--border);
            border-radius: 2px;
            margin: 12px auto;
        }}
        
        .modal-header {{
            padding: 0 20px 16px;
            border-bottom: 1px solid var(--border);
        }}
        
        .modal-title {{
            font-size: 18px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .modal-title i {{
            color: var(--primary);
        }}
        
        .modal-body {{
            padding: 20px;
            overflow-y: auto;
            max-height: calc(85vh - 100px);
        }}
        
        .detail-section {{
            margin-bottom: 20px;
        }}
        
        .detail-label {{
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .detail-value {{
            font-size: 14px;
            color: var(--text);
            line-height: 1.6;
        }}
        
        .detail-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .detail-tag {{
            background: var(--gradient-card);
            padding: 4px 12px;
            border-radius: 8px;
            font-size: 12px;
            color: var(--primary);
        }}
        
        .detail-link {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--primary);
            color: white;
            padding: 10px 20px;
            border-radius: 12px;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            margin-top: 8px;
        }}
        
        .detail-link:active {{
            background: var(--primary-dark);
        }}
        
        /* 底部操作栏 */
        .bottom-bar {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--card);
            border-top: 1px solid var(--border);
            padding: 12px 16px;
            padding-bottom: calc(12px + var(--safe-area-bottom));
            display: flex;
            gap: 12px;
            z-index: 50;
        }}
        
        .bottom-btn {{
            flex: 1;
            height: 44px;
            border: none;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.2s;
        }}
        
        .bottom-btn.primary {{
            background: var(--gradient-hero);
            color: white;
        }}
        
        .bottom-btn.secondary {{
            background: var(--gradient-card);
            color: var(--primary);
        }}
        
        .bottom-btn:active {{
            transform: scale(0.98);
        }}
        
        /* 空状态 */
        .empty {{
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
        }}
        
        .empty i {{
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.3;
        }}
    </style>
</head>
<body>
    <!-- 题图区域 -->
    <div class="cover">
        <div class="cover-deco deco-1"></div>
        <div class="cover-deco deco-2"></div>
        <div class="cover-deco deco-3"></div>
        <div class="cover-content">
            <div class="cover-badge">
                <i class="fas fa-bolt"></i>
                <span>每日更新</span>
            </div>
            <h1 class="cover-title">AI 推荐日报</h1>
            <p class="cover-subtitle">推荐算法 × AI Agent × LLM 前沿追踪，每日精选最值得阅读的内容</p>
            <div class="cover-date">
                <i class="far fa-calendar"></i>
                <span>{self.today}</span>
            </div>
            <div class="cover-stats">
                <div class="cover-stat">
                    <div class="cover-stat-value">{total_papers}</div>
                    <div class="cover-stat-label">论文</div>
                </div>
                <div class="cover-stat">
                    <div class="cover-stat-value">{total_projects}</div>
                    <div class="cover-stat-label">项目</div>
                </div>
                <div class="cover-stat">
                    <div class="cover-stat-value">{total_articles}</div>
                    <div class="cover-stat-label">文章</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 导航 -->
    <nav class="nav">
        <div class="nav-inner">
            <div class="nav-title">AI推荐日报</div>
            <div class="nav-actions">
                <button class="nav-btn" onclick="showSearch()">
                    <i class="fas fa-search"></i>
                </button>
                <button class="nav-btn" onclick="showFavorites()">
                    <i class="far fa-bookmark"></i>
                </button>
                <button class="nav-btn" onclick="shareReport()">
                    <i class="fas fa-share-alt"></i>
                </button>
            </div>
        </div>
    </nav>
    
    <!-- 主内容 -->
    <main class="main">
        <!-- 每日精选 -->
        <section class="section" id="picks">
            <div class="section-header">
                <h2 class="section-title"><i class="fas fa-star"></i> 每日精选</h2>
            </div>
            <div id="picks-list"></div>
        </section>
        
        <!-- 热门文章 -->
        <section class="section" id="articles">
            <div class="section-header">
                <h2 class="section-title"><i class="fas fa-fire"></i> 热门文章</h2>
                <a href="#" class="section-more" onclick="showAllArticles()">查看全部</a>
            </div>
            <div id="articles-list"></div>
        </section>
        
        <!-- GitHub 项目 -->
        <section class="section" id="github">
            <div class="section-header">
                <h2 class="section-title"><i class="fab fa-github"></i> 热门项目</h2>
            </div>
            <div id="github-list"></div>
        </section>
        
        <!-- arXiv 论文 -->
        <section class="section" id="papers">
            <div class="section-header">
                <h2 class="section-title"><i class="fas fa-file-alt"></i> 最新论文</h2>
            </div>
            <div id="papers-list"></div>
        </section>
    </main>
    
    <!-- 详情弹窗 -->
    <div class="modal" id="detailModal">
        <div class="modal-overlay" onclick="closeDetail()"></div>
        <div class="modal-content">
            <div class="modal-handle"></div>
            <div class="modal-header">
                <h3 class="modal-title" id="detail-title"></h3>
            </div>
            <div class="modal-body" id="detail-body"></div>
        </div>
    </div>
    
    <!-- 底部操作栏 -->
    <div class="bottom-bar">
        <button class="bottom-btn secondary" onclick="showArchive()">
            <i class="far fa-calendar-alt"></i>
            历史日报
        </button>
        <button class="bottom-btn primary" onclick="refreshData()">
            <i class="fas fa-sync-alt"></i>
            刷新数据
        </button>
    </div>
    
    <script>
        // 数据
        const articles = {articles_json};
        const arxivPapers = {arxiv_json};
        const githubProjects = {github_json};
        
        // 收藏列表
        let favorites = JSON.parse(localStorage.getItem('ai-daily-favorites') || '[]');
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {{
            renderArticles();
            renderPapers();
            renderGithub();
        }});
        
        // 渲染文章
        function renderArticles() {{
            const container = document.getElementById('articles-list');
            if (!articles || articles.length === 0) {{
                container.innerHTML = '<div class="empty"><i class="far fa-newspaper"></i><p>暂无文章数据</p></div>';
                return;
            }}
            
            container.innerHTML = articles.slice(0, 5).map((item, index) => `
                <div class="card" onclick="showArticleDetail(${{index}})">
                    <div class="card-content">
                        <div class="card-header">
                            <div class="card-icon article">
                                <i class="fas fa-newspaper"></i>
                            </div>
                            <div class="card-title-wrap">
                                <div class="card-title">${{item.title || '未知标题'}}</div>
                                <div class="card-meta">
                                    <span class="card-tag">${{item.source || '未知来源'}}</span>
                                    <span>${{item.published || ''}}</span>
                                </div>
                            </div>
                        </div>
                        <div class="card-desc">${{item.summary || ''}}</div>
                        <div class="card-footer">
                            <div class="card-stats">
                                <span><i class="far fa-eye"></i> ${{item.views || 0}}</span>
                                <span><i class="far fa-heart"></i> ${{item.likes || 0}}</span>
                            </div>
                            <span class="card-action">查看详情 <i class="fas fa-chevron-right"></i></span>
                        </div>
                    </div>
                </div>
            `).join('');
        }}
        
        // 渲染论文
        function renderPapers() {{
            const container = document.getElementById('papers-list');
            if (!arxivPapers || arxivPapers.length === 0) {{
                container.innerHTML = '<div class="empty"><i class="far fa-file"></i><p>暂无论文数据</p></div>';
                return;
            }}
            
            container.innerHTML = arxivPapers.slice(0, 5).map((item, index) => `
                <div class="card" onclick="showPaperDetail(${{index}})">
                    <div class="card-content">
                        <div class="card-header">
                            <div class="card-icon paper">
                                <i class="fas fa-file-alt"></i>
                            </div>
                            <div class="card-title-wrap">
                                <div class="card-title">${{item.title || '未知标题'}}</div>
                                <div class="card-meta">
                                    <span class="card-tag">${{item.category || 'arXiv'}}</span>
                                    <span>${{item.published || ''}}</span>
                                </div>
                            </div>
                        </div>
                        <div class="card-desc">${{item.cn_summary || item.summary || ''}}</div>
                        <div class="card-footer">
                            <div class="card-stats">
                                <span><i class="fas fa-users"></i> ${{(item.authors || []).length}} 位作者</span>
                            </div>
                            <span class="card-action">阅读论文 <i class="fas fa-external-link-alt"></i></span>
                        </div>
                    </div>
                </div>
            `).join('');
        }}
        
        // 渲染 GitHub 项目
        function renderGithub() {{
            const container = document.getElementById('github-list');
            if (!githubProjects || githubProjects.length === 0) {{
                container.innerHTML = '<div class="empty"><i class="fab fa-github"></i><p>暂无项目数据</p></div>';
                return;
            }}
            
            container.innerHTML = githubProjects.slice(0, 5).map((item, index) => `
                <div class="card" onclick="showGithubDetail(${{index}})">
                    <div class="card-content">
                        <div class="card-header">
                            <div class="card-icon github">
                                <i class="fab fa-github"></i>
                            </div>
                            <div class="card-title-wrap">
                                <div class="card-title">${{item.name || item.full_name || '未知项目'}}</div>
                                <div class="card-meta">
                                    <span class="card-tag">${{item.language || 'Code'}}</span>
                                    <span><i class="fas fa-star"></i> ${{(item.stars || 0).toLocaleString()}}</span>
                                </div>
                            </div>
                        </div>
                        <div class="card-desc">${{item.description || ''}}</div>
                        <div class="card-footer">
                            <div class="card-stats">
                                <span><i class="fas fa-code-branch"></i> ${{item.forks || 0}}</span>
                                <span><i class="fas fa-chart-line"></i> +${{(item.growth_rate || 0).toFixed(1)}}%</span>
                            </div>
                            <span class="card-action">查看项目 <i class="fas fa-external-link-alt"></i></span>
                        </div>
                    </div>
                </div>
            `).join('');
        }}
        
        // 显示文章详情
        function showArticleDetail(index) {{
            const item = articles[index];
            if (!item) return;
            
            document.getElementById('detail-title').innerHTML = `<i class="fas fa-newspaper"></i> 文章详情`;
            document.getElementById('detail-body').innerHTML = `
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
                    <div class="detail-value">${{item.summary || '暂无摘要'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">分类</div>
                    <div class="detail-tags">
                        <span class="detail-tag">${{item.category || '未分类'}}</span>
                    </div>
                </div>
                ${{item.link ? `<a href="${{item.link}}" target="_blank" class="detail-link"><i class="fas fa-external-link-alt"></i> 阅读原文</a>` : ''}}
            `;
            document.getElementById('detailModal').classList.add('active');
        }}
        
        // 显示论文详情
        function showPaperDetail(index) {{
            const item = arxivPapers[index];
            if (!item) return;
            
            document.getElementById('detail-title').innerHTML = `<i class="fas fa-file-alt"></i> 论文详情`;
            document.getElementById('detail-body').innerHTML = `
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
                    <div class="detail-label">摘要</div>
                    <div class="detail-value">${{item.summary || '暂无摘要'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">分类</div>
                    <div class="detail-tags">
                        <span class="detail-tag">${{item.category || 'arXiv'}}</span>
                    </div>
                </div>
                ${{item.link ? `<a href="${{item.link}}" target="_blank" class="detail-link"><i class="fas fa-external-link-alt"></i> 阅读论文</a>` : ''}}
            `;
            document.getElementById('detailModal').classList.add('active');
        }}
        
        // 显示 GitHub 详情
        function showGithubDetail(index) {{
            const item = githubProjects[index];
            if (!item) return;
            
            document.getElementById('detail-title').innerHTML = `<i class="fab fa-github"></i> 项目详情`;
            document.getElementById('detail-body').innerHTML = `
                <div class="detail-section">
                    <div class="detail-label">项目名称</div>
                    <div class="detail-value">${{item.full_name || item.name || '未知项目'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">描述</div>
                    <div class="detail-value">${{item.description || '暂无描述'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">语言</div>
                    <div class="detail-value">${{item.language || '未知'}}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">统计</div>
                    <div class="detail-value">
                        <i class="fas fa-star"></i> ${{(item.stars || 0).toLocaleString()}} Stars · 
                        <i class="fas fa-code-branch"></i> ${{item.forks || 0}} Forks · 
                        <i class="fas fa-chart-line"></i> +${{(item.growth_rate || 0).toFixed(1)}}% 增长
                    </div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">标签</div>
                    <div class="detail-tags">
                        ${{(item.topics || []).slice(0, 5).map(t => `<span class="detail-tag">${{t}}</span>`).join('')}}
                    </div>
                </div>
                ${{item.url ? `<a href="${{item.url}}" target="_blank" class="detail-link"><i class="fab fa-github"></i> 查看项目</a>` : ''}}
            `;
            document.getElementById('detailModal').classList.add('active');
        }}
        
        // 关闭详情
        function closeDetail() {{
            document.getElementById('detailModal').classList.remove('active');
        }}
        
        // 显示搜索
        function showSearch() {{
            alert('搜索功能开发中...');
        }}
        
        // 显示收藏
        function showFavorites() {{
            alert('收藏功能开发中...');
        }}
        
        // 分享日报
        function shareReport() {{
            if (navigator.share) {{
                navigator.share({{
                    title: 'AI推荐日报',
                    text: '推荐算法 × AI Agent × LLM 前沿追踪',
                    url: window.location.href
                }});
            }} else {{
                alert('已复制链接到剪贴板');
            }}
        }}
        
        // 显示历史
        function showArchive() {{
            alert('历史日报功能开发中...');
        }}
        
        // 刷新数据
        function refreshData() {{
            location.reload();
        }}
        
        // 显示所有文章
        function showAllArticles() {{
            alert('查看全部文章功能开发中...');
        }}
    </script>
</body>
</html>'''
        return html
    
    def generate_cover_svg(self) -> str:
        """生成 SVG 题图"""
        return '''<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#667eea"/>
                    <stop offset="50%" style="stop-color:#764ba2"/>
                    <stop offset="100%" style="stop-color:#f093fb"/>
                </linearGradient>
            </defs>
            <rect width="400" height="200" fill="url(#grad)"/>
            <text x="200" y="100" text-anchor="middle" fill="white" font-size="24" font-weight="bold">AI 推荐日报</text>
        </svg>'''
    
    def save(self, html: str):
        """保存 HTML"""
        output_file = self.base_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ 日报已生成: {output_file}")


if __name__ == "__main__":
    generator = EnhancedReportGenerator()
    html = generator.generate_html()
    generator.save(html)
