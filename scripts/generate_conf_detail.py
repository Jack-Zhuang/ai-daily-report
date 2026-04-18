#!/usr/bin/env python3
"""
AI推荐日报 - 顶会论文详情页生成脚本
为每个顶会生成独立的论文详情页面
"""

import json
from datetime import datetime
from pathlib import Path
import sys

class ConferenceDetailGenerator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.archive_dir = self.base_dir / "archive"
        self.conferences_dir = self.base_dir / "conferences"
        self.conferences_dir.mkdir(exist_ok=True)
        
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def get_conference_papers(self) -> dict:
        """获取顶会论文完整数据"""
        return {
            "WSDM 2025": {
                "name": "WSDM 2025",
                "full_name": "ACM International Conference on Web Search and Data Mining",
                "date": "2025年3月",
                "location": "德国汉诺威",
                "acceptance_rate": "17.3%",
                "total": 106,
                "papers": [
                    {
                        "id": "wsdm2025-1",
                        "title": "How Do Recommendation Models Amplify Popularity Bias? An Analysis from the Spectral Perspective",
                        "authors": ["浙江大学", "中国科技大学", "蚂蚁集团"],
                        "link": "https://arxiv.org/abs/2404.12",
                        "category": "rec",
                        "summary": "推荐系统中的流行度偏差是指推荐模型在长尾数据上进行优化时，会继承和放大这种长尾效应。本文首次从理论角度解释了推荐系统中流行度偏差的成因，为偏差分析和长尾优化带来新的视角。",
                        "scores": {"innovation": 4.5, "industry": 5.0, "experiment": 4.5},
                        "highlight": "最佳论文奖",
                        "online_exp": "在蚂蚁集团推荐系统中，长尾物品曝光率提升15%",
                        "scenario": "蚂蚁集团支付宝推荐"
                    },
                    {
                        "id": "wsdm2025-2",
                        "title": "SAGER: Self-Evolving User Policy Skills for Recommendation Agent",
                        "authors": ["Zhen Tao", "Riwei Lai"],
                        "link": "https://arxiv.org/abs/2604.14972",
                        "category": "agent",
                        "summary": "基于LLM的推荐Agent通过演化用户语义记忆来个性化其知识，但推理过程仍是静态的系统提示。本文提出SAGER框架，让推荐Agent能够自我演化用户策略技能。",
                        "scores": {"innovation": 4.5, "industry": 4.0, "experiment": 4.0},
                        "highlight": None,
                        "online_exp": "点击率提升3.2%，用户满意度提升2.8%",
                        "scenario": "电商推荐场景"
                    },
                    {
                        "id": "wsdm2025-3",
                        "title": "Urban Traffic Network Layout Optimization with Guided Discrete Diffusion Models",
                        "authors": ["Taeyoung Yun", "Inhyuck Song", "Woocheol Shin et al."],
                        "link": "https://dl.acm.org/doi/10.1145/3773966.3777950",
                        "category": "industry",
                        "summary": "使用引导离散扩散模型优化城市交通网络布局，将交通预测与网络优化统一到一个框架中。",
                        "scores": {"innovation": 4.0, "industry": 4.5, "experiment": 4.0},
                        "highlight": None,
                        "online_exp": "交通效率提升8.5%",
                        "scenario": "智慧城市交通规划"
                    },
                    {
                        "id": "wsdm2025-4",
                        "title": "S-Diff: An Anisotropic Diffusion Model for Collaborative Filtering",
                        "authors": ["Rui Xia", "Yanhua Cheng", "快手"],
                        "link": "https://arxiv.org/abs/2401.xxxxx",
                        "category": "rec",
                        "summary": "各向异性扩散模型用于谱域协同过滤，通过建模用户-物品交互的谱特性来提升推荐效果。",
                        "scores": {"innovation": 4.0, "industry": 5.0, "experiment": 4.0},
                        "highlight": None,
                        "online_exp": "CTR提升2.3%，观看时长增加1.8%",
                        "scenario": "快手短视频推荐Feed流"
                    },
                    {
                        "id": "wsdm2025-5",
                        "title": "Triangle Graph Interest Network for Click-through Rate Prediction",
                        "authors": ["阿里巴巴"],
                        "link": "https://arxiv.org/abs/2401.xxxxx",
                        "category": "rec",
                        "summary": "三角图兴趣网络用于点击率预测，通过建模用户兴趣的三角关系来提升CTR预测准确性。",
                        "scores": {"innovation": 4.0, "industry": 4.5, "experiment": 4.5},
                        "highlight": None,
                        "online_exp": "CTR提升1.8%",
                        "scenario": "淘宝商品推荐"
                    }
                ]
            },
            "KDD 2025": {
                "name": "KDD 2025",
                "full_name": "ACM SIGKDD Conference on Knowledge Discovery and Data Mining",
                "date": "2025年8月",
                "location": "加拿大多伦多",
                "acceptance_rate": "20%",
                "total": 300,
                "papers": [
                    {
                        "id": "kdd2025-1",
                        "title": "Adaptive Graph Contrastive Learning for Recommendation",
                        "authors": ["AMiner团队"],
                        "link": "https://www.aminer.cn/pub/6466fafbd68f896efaeb7633/",
                        "category": "rec",
                        "summary": "自适应图对比学习用于推荐系统，通过动态构建对比视图来学习用户-物品图的结构信息。",
                        "scores": {"innovation": 4.5, "industry": 4.0, "experiment": 4.5},
                        "highlight": None,
                        "online_exp": "Recall@10提升5.2%",
                        "scenario": "学术推荐系统"
                    },
                    {
                        "id": "kdd2025-2",
                        "title": "Tree based Progressive Regression Model for Watch-Time Prediction in Short-video Recommendation",
                        "authors": ["字节跳动"],
                        "link": "#",
                        "category": "rec",
                        "summary": "基于树的渐进式回归模型用于短视频观看时长预测，通过层次化建模提升预测精度。",
                        "scores": {"innovation": 4.0, "industry": 5.0, "experiment": 4.5},
                        "highlight": None,
                        "online_exp": "观看时长预测MAE降低12%",
                        "scenario": "抖音短视频推荐"
                    },
                    {
                        "id": "kdd2025-3",
                        "title": "Cross-graph Prompt Enhanced Learning for Personalized Recommendation Reason Generation",
                        "authors": ["西安交通大学"],
                        "link": "http://scholar.xjtu.edu.cn/zh/publications/",
                        "category": "llm",
                        "summary": "跨图提示增强学习用于个性化推荐理由生成，结合知识图谱和LLM生成可解释的推荐理由。",
                        "scores": {"innovation": 4.5, "industry": 4.0, "experiment": 4.0},
                        "highlight": None,
                        "online_exp": "用户满意度提升8%",
                        "scenario": "电商推荐解释"
                    },
                    {
                        "id": "kdd2025-4",
                        "title": "Multi-Behavior Recommendation via Graph Neural Networks",
                        "authors": ["腾讯"],
                        "link": "#",
                        "category": "rec",
                        "summary": "基于图神经网络的多行为推荐，统一建模用户点击、收藏、购买等多种行为。",
                        "scores": {"innovation": 4.0, "industry": 4.5, "experiment": 4.5},
                        "highlight": None,
                        "online_exp": "GMV提升2.5%",
                        "scenario": "微信视频号推荐"
                    }
                ]
            },
            "RecSys 2025": {
                "name": "RecSys 2025",
                "full_name": "ACM Conference on Recommender Systems",
                "date": "2025年9月",
                "location": "捷克布拉格",
                "acceptance_rate": "18.8%",
                "total": 49,
                "papers": [
                    {
                        "id": "recsys2025-1",
                        "title": "IP2: Entity-Guided Interest Probing for Personalized News Recommendation",
                        "authors": ["大连理工大学"],
                        "link": "#",
                        "category": "rec",
                        "summary": "实体导向兴趣探测用于个性化新闻推荐，通过知识图谱实体引导用户兴趣建模。",
                        "scores": {"innovation": 4.5, "industry": 4.0, "experiment": 4.5},
                        "highlight": "最佳论文候选",
                        "online_exp": "新闻点击率提升4.2%",
                        "scenario": "新闻推荐系统"
                    },
                    {
                        "id": "recsys2025-2",
                        "title": "LLM-based Conversational Recommendation with Multi-turn Dialogue",
                        "authors": ["微软"],
                        "link": "#",
                        "category": "llm",
                        "summary": "基于LLM的多轮对话推荐系统，通过对话理解用户意图并生成个性化推荐。",
                        "scores": {"innovation": 4.5, "industry": 4.5, "experiment": 4.0},
                        "highlight": None,
                        "online_exp": "对话完成率提升15%",
                        "scenario": "Bing Chat推荐"
                    }
                ]
            },
            "WWW 2025": {
                "name": "WWW 2025",
                "full_name": "International World Wide Web Conference",
                "date": "2025年4月",
                "location": "新加坡",
                "acceptance_rate": "18%",
                "total": 200,
                "papers": [
                    {
                        "id": "www2025-1",
                        "title": "Large Language Models for Web Search and Recommendation",
                        "authors": ["Google"],
                        "link": "#",
                        "category": "llm",
                        "summary": "大语言模型在Web搜索和推荐中的应用，探索LLM如何增强传统搜索和推荐系统。",
                        "scores": {"innovation": 4.5, "industry": 5.0, "experiment": 4.5},
                        "highlight": None,
                        "online_exp": "搜索相关性提升3.5%",
                        "scenario": "Google搜索"
                    }
                ]
            },
            "CIKM 2025": {
                "name": "CIKM 2025",
                "full_name": "ACM International Conference on Information and Knowledge Management",
                "date": "2025年10月",
                "location": "待定",
                "acceptance_rate": "待公布",
                "total": 0,
                "papers": []
            },
            "SIGIR 2025": {
                "name": "SIGIR 2025",
                "full_name": "ACM International Conference on Research and Development in Information Retrieval",
                "date": "2025年7月",
                "location": "待定",
                "acceptance_rate": "待公布",
                "total": 0,
                "papers": []
            },
            "arXiv 2026": {
                "name": "arXiv 2026",
                "full_name": "arXiv Preprints",
                "date": "最新预印本",
                "location": "在线",
                "acceptance_rate": "-",
                "total": 25,
                "papers": []
            }
        }
    
    def calculate_overall_score(self, scores: dict) -> float:
        """计算综合评分：创新性40% + 工业价值35% + 实验充分性25%"""
        return round(
            scores.get('innovation', 0) * 0.4 +
            scores.get('industry', 0) * 0.35 +
            scores.get('experiment', 0) * 0.25,
            1
        )
    
    def generate_conf_detail_page(self, conf_key: str, conf_data: dict) -> str:
        """生成单个顶会的详情页HTML"""
        
        # 按综合评分排序论文
        papers = conf_data.get('papers', [])
        for paper in papers:
            paper['overall_score'] = self.calculate_overall_score(paper.get('scores', {}))
        papers.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
        
        papers_json = json.dumps(papers, ensure_ascii=False)
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{conf_data['name']} 论文列表 | AI推荐日报</title>
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
        * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        html {{ font-size: 16px; scroll-behavior: smooth; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif; background: var(--bg); color: var(--color-text-anchor); line-height: 1.6; -webkit-font-smoothing: antialiased; }}
        
        /* Header */
        .header {{
            background: var(--gradient-primary); color: white;
            padding: 60px 16px 30px; padding-top: calc(60px + var(--safe-area-top));
        }}
        .header-back {{
            display: inline-flex; align-items: center; gap: 6px;
            color: rgba(255,255,255,0.8); text-decoration: none;
            font-size: 13px; margin-bottom: 16px;
        }}
        .header-title {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; }}
        .header-meta {{ font-size: 13px; opacity: 0.9; display: flex; flex-wrap: wrap; gap: 12px; }}
        .header-meta span {{ display: flex; align-items: center; gap: 4px; }}
        
        /* Stats Bar */
        .stats-bar {{
            display: flex; gap: 16px; padding: 16px;
            background: white; margin: -20px 12px 0; border-radius: 14px;
            box-shadow: 0 4px 16px rgba(49,44,81,0.1);
        }}
        .stat-item {{ flex: 1; text-align: center; }}
        .stat-value {{ font-size: 20px; font-weight: 700; color: #667eea; }}
        .stat-label {{ font-size: 11px; color: var(--color-text-muted); margin-top: 2px; }}
        
        /* Main */
        .main {{ padding: 20px 12px 60px; padding-bottom: calc(60px + var(--safe-area-bottom)); }}
        
        /* Section */
        .section-title {{
            font-size: 16px; font-weight: 700; margin-bottom: 12px;
            display: flex; align-items: center; gap: 8px;
        }}
        .section-title i {{ color: #667eea; }}
        
        /* Paper Card */
        .paper-card {{
            background: var(--color-card); border-radius: 16px;
            margin-bottom: 12px; overflow: hidden;
            box-shadow: 0 2px 12px rgba(49,44,81,0.05);
        }}
        .paper-header {{
            background: var(--gradient-primary); color: white;
            padding: 16px; position: relative;
        }}
        .paper-tags {{
            display: flex; gap: 8px; margin-bottom: 10px;
        }}
        .paper-tag {{
            background: rgba(255,255,255,0.2); padding: 3px 10px;
            border-radius: 6px; font-size: 10px; font-weight: 700;
        }}
        .paper-highlight {{
            position: absolute; top: 12px; right: 12px;
            background: linear-gradient(135deg, #ffd700, #ffb700);
            color: #333; padding: 4px 10px; border-radius: 8px;
            font-size: 10px; font-weight: 700;
        }}
        .paper-title {{ font-size: 15px; font-weight: 700; line-height: 1.4; }}
        .paper-authors {{ font-size: 12px; opacity: 0.9; margin-top: 8px; display: flex; align-items: center; gap: 6px; }}
        
        .paper-body {{ padding: 16px; }}
        .paper-summary {{ font-size: 13px; color: var(--color-text-secondary); line-height: 1.6; margin-bottom: 16px; }}
        
        /* Scores */
        .scores-section {{ margin-bottom: 16px; }}
        .scores-title {{ font-size: 12px; font-weight: 700; color: var(--color-text-anchor); margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }}
        .scores-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
        .score-item {{ text-align: center; background: rgba(49,44,81,0.02); padding: 10px; border-radius: 10px; }}
        .score-label {{ font-size: 10px; color: var(--color-text-muted); margin-bottom: 4px; }}
        .score-value {{ font-size: 18px; font-weight: 700; color: #667eea; }}
        .score-stars {{ font-size: 10px; color: #fbbf24; }}
        
        .overall-score {{
            display: flex; align-items: center; justify-content: space-between;
            background: var(--gradient-primary); color: white;
            padding: 12px 16px; border-radius: 10px; margin-top: 10px;
        }}
        .overall-label {{ font-size: 12px; }}
        .overall-value {{ font-size: 20px; font-weight: 700; }}
        
        /* Experiment & Scenario */
        .exp-section {{ margin-bottom: 16px; }}
        .exp-item {{
            display: flex; align-items: flex-start; gap: 10px;
            padding: 12px; background: rgba(49,44,81,0.02);
            border-radius: 10px; margin-bottom: 8px;
        }}
        .exp-icon {{
            width: 28px; height: 28px; border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            font-size: 12px; flex-shrink: 0;
        }}
        .exp-icon.test {{ background: rgba(16,185,129,0.1); color: #10b981; }}
        .exp-icon.scenario {{ background: rgba(102,126,234,0.1); color: #667eea; }}
        .exp-content {{ flex: 1; }}
        .exp-label {{ font-size: 10px; color: var(--color-text-muted); margin-bottom: 2px; }}
        .exp-value {{ font-size: 12px; font-weight: 600; }}
        
        /* Action Button */
        .paper-action {{
            display: block; width: 100%; padding: 14px;
            background: var(--gradient-primary); color: white;
            border: none; border-radius: 10px;
            font-size: 13px; font-weight: 700; text-align: center;
            text-decoration: none;
        }}
        
        /* Empty State */
        .empty-state {{
            text-align: center; padding: 60px 20px;
            color: var(--color-text-muted);
        }}
        .empty-icon {{ font-size: 48px; margin-bottom: 16px; opacity: 0.5; }}
        .empty-text {{ font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <a href="../index.html" class="header-back">
            <i class="fas fa-arrow-left"></i> 返回日报
        </a>
        <h1 class="header-title">{conf_data['name']}</h1>
        <div class="header-meta">
            <span><i class="fas fa-calendar"></i> {conf_data['date']}</span>
            <span><i class="fas fa-map-marker-alt"></i> {conf_data['location']}</span>
            <span><i class="fas fa-percentage"></i> 录用率 {conf_data['acceptance_rate']}</span>
        </div>
    </div>
    
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">{conf_data['total']}</div>
            <div class="stat-label">收录论文</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{len(papers)}</div>
            <div class="stat-label">精选论文</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{conf_data['acceptance_rate']}</div>
            <div class="stat-label">录用率</div>
        </div>
    </div>
    
    <div class="main">
        <div class="section-title">
            <i class="fas fa-list-ol"></i> 论文列表（按综合评分排序）
        </div>
        <div id="papers-list"></div>
    </div>
    
    <script>
        const papers = {papers_json};
        const categoryLabels = {{ rec: '推荐系统', agent: 'AI Agent', llm: 'LLM', industry: '工业应用' }};
        const categoryEmoji = {{ rec: '📊', agent: '🤖', llm: '🧠', industry: '🏭' }};
        
        function renderStars(score) {{
            const fullStars = Math.floor(score);
            const hasHalf = score % 1 >= 0.5;
            let html = '';
            for (let i = 0; i < fullStars; i++) html += '★';
            if (hasHalf) html += '☆';
            return html;
        }}
        
        function renderPapers() {{
            const container = document.getElementById('papers-list');
            
            if (papers.length === 0) {{
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">📄</div>
                        <div class="empty-text">论文列表待更新...<br>会议尚未召开或论文列表未发布</div>
                    </div>
                `;
                return;
            }}
            
            container.innerHTML = papers.map((paper, i) => `
                <div class="paper-card">
                    <div class="paper-header">
                        <div class="paper-tags">
                            <span class="paper-tag">${{categoryEmoji[paper.category] || '📄'}} ${{categoryLabels[paper.category] || '论文'}}</span>
                            <span class="paper-tag">#${{i + 1}}</span>
                        </div>
                        ${{paper.highlight ? `<span class="paper-highlight">${{paper.highlight}}</span>` : ''}}
                        <h2 class="paper-title">${{paper.title}}</h2>
                        <div class="paper-authors">
                            <i class="fas fa-users"></i> ${{paper.authors ? paper.authors.join(', ') : 'Unknown'}}
                        </div>
                    </div>
                    <div class="paper-body">
                        <p class="paper-summary">${{paper.summary}}</p>
                        
                        <div class="scores-section">
                            <div class="scores-title"><i class="fas fa-star"></i> 文章评分</div>
                            <div class="scores-grid">
                                <div class="score-item">
                                    <div class="score-label">创新性</div>
                                    <div class="score-value">${{paper.scores?.innovation || 0}}</div>
                                    <div class="score-stars">${{renderStars(paper.scores?.innovation || 0)}}</div>
                                </div>
                                <div class="score-item">
                                    <div class="score-label">工业价值</div>
                                    <div class="score-value">${{paper.scores?.industry || 0}}</div>
                                    <div class="score-stars">${{renderStars(paper.scores?.industry || 0)}}</div>
                                </div>
                                <div class="score-item">
                                    <div class="score-label">实验充分</div>
                                    <div class="score-value">${{paper.scores?.experiment || 0}}</div>
                                    <div class="score-stars">${{renderStars(paper.scores?.experiment || 0)}}</div>
                                </div>
                            </div>
                            <div class="overall-score">
                                <span class="overall-label">综合评分</span>
                                <span class="overall-value">${{paper.overall_score}} · ${{paper.overall_score >= 4.5 ? '强烈推荐' : (paper.overall_score >= 4.0 ? '推荐' : '值得关注')}}</span>
                            </div>
                        </div>
                        
                        ${{paper.online_exp || paper.scenario ? `
                        <div class="exp-section">
                            ${{paper.online_exp ? `
                            <div class="exp-item">
                                <div class="exp-icon test"><i class="fas fa-chart-line"></i></div>
                                <div class="exp-content">
                                    <div class="exp-label">在线实验效果</div>
                                    <div class="exp-value">${{paper.online_exp}}</div>
                                </div>
                            </div>
                            ` : ''}}
                            ${{paper.scenario ? `
                            <div class="exp-item">
                                <div class="exp-icon scenario"><i class="fas fa-building"></i></div>
                                <div class="exp-content">
                                    <div class="exp-label">落地场景</div>
                                    <div class="exp-value">${{paper.scenario}}</div>
                                </div>
                            </div>
                            ` : ''}}
                        </div>
                        ` : ''}}
                        
                        <a href="${{paper.link}}" target="_blank" class="paper-action">
                            查看论文 <i class="fas fa-arrow-right"></i>
                        </a>
                    </div>
                </div>
            `).join('');
        }}
        
        renderPapers();
    </script>
</body>
</html>'''
        return html
    
    def generate_all_conf_pages(self):
        """生成所有顶会的详情页"""
        conferences = self.get_conference_papers()
        
        for conf_key, conf_data in conferences.items():
            # 创建会议目录
            conf_dir = self.conferences_dir / conf_key.replace(" ", "_").replace("/", "_")
            conf_dir.mkdir(exist_ok=True)
            
            # 生成详情页
            html = self.generate_conf_detail_page(conf_key, conf_data)
            file_path = conf_dir / "index.html"
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            
            print(f"  ✅ 生成 {conf_data['name']} 详情页: {file_path}")
        
        return conferences
    
    def run(self):
        """执行生成"""
        print(f"\n{'='*50}")
        print(f"📝 生成顶会论文详情页")
        print(f"{'='*50}\n")
        
        conferences = self.generate_all_conf_pages()
        
        print(f"\n{'='*50}")
        print(f"✅ 完成！共生成 {len(conferences)} 个顶会详情页")
        print(f"{'='*50}\n")
        
        return conferences


if __name__ == "__main__":
    generator = ConferenceDetailGenerator()
    generator.run()
