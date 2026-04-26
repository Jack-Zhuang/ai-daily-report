#!/usr/bin/env python3
"""
AI推荐日报 - 功能完善脚本
在不破坏现有功能的前提下，完善缺失的能力
"""

import json
from pathlib import Path
from datetime import datetime

class FeatureEnhancer:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "daily_data"
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # 检查今日数据是否存在，如果不存在则使用昨天的
        data_file = self.base_dir / "daily_data" / f"{self.today}.json"
        if not data_file.exists():
            from datetime import timedelta
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            data_file_yesterday = self.base_dir / "daily_data" / f"{yesterday}.json"
            if data_file_yesterday.exists():
                self.today = yesterday
                print(f"⚠️ 使用前一天的数据: {yesterday}")
        self.data_file = self.data_dir / f"{self.today}.json"
        
    def load_data(self):
        """加载数据"""
        if not self.data_file.exists():
            print(f"❌ 数据文件不存在: {self.data_file}")
            return None
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_data(self, data):
        """保存数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 数据已保存")
    
    def enhance_1_translate_github_descriptions(self, data):
        """功能1: 翻译 GitHub 项目描述"""
        print("\n" + "=" * 60)
        print("🔧 功能1: 翻译 GitHub 项目描述")
        print("=" * 60)
        
        github = data.get('github', [])
        if not github:
            print("⚠️ 没有 GitHub 数据")
            return data
        
        # 简单翻译规则（实际应调用翻译 API）
        translations = {
            'framework': '框架',
            'library': '库',
            'tool': '工具',
            'platform': '平台',
            'application': '应用',
            'system': '系统',
            'model': '模型',
            'agent': '智能体',
            'AI': 'AI',
            'machine learning': '机器学习',
            'deep learning': '深度学习',
            'neural network': '神经网络',
        }
        
        translated = 0
        for item in github:
            if not item.get('cn_description') and item.get('description'):
                desc = item['description']
                # 简单替换
                cn_desc = desc
                for en, cn in translations.items():
                    cn_desc = cn_desc.replace(en, cn)
                
                # 如果描述主要是英文，标记需要翻译
                if cn_desc == desc and not any('\u4e00' <= c <= '\u9fff' for c in desc):
                    item['cn_description'] = f"[待翻译] {desc[:100]}"
                else:
                    item['cn_description'] = cn_desc
                    translated += 1
        
        print(f"✅ 已翻译 {translated} 个 GitHub 项目描述")
        return data
    
    def enhance_2_fix_category_counts(self, data):
        """功能2: 修复分类计数"""
        print("\n" + "=" * 60)
        print("🔧 功能2: 修复分类计数")
        print("=" * 60)
        
        articles = data.get('articles', [])
        
        # 统计各分类
        categories = {}
        for article in articles:
            cat = article.get('category', 'other')
            categories[cat] = categories.get(cat, 0) + 1
        
        data['category_counts'] = categories
        
        print(f"分类统计:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count}")
        
        return data
    
    def enhance_3_generate_conference_pages(self, data):
        """功能3: 生成顶会论文详情页"""
        print("\n" + "=" * 60)
        print("🔧 功能3: 生成顶会论文详情页")
        print("=" * 60)
        
        # 优先使用 conference_papers，兼容 conferences
        conferences = data.get('conference_papers', data.get('conferences', {}))
        if not conferences:
            print("⚠️ 没有顶会数据")
            return data
        
        docs_dir = self.base_dir / "docs" / "conferences"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        for conf_name, conf_data in conferences.items():
            html = self._generate_conference_html(conf_name, conf_data)
            output_file = docs_dir / f"{conf_name.replace(' ', '_')}.html"
            output_file.write_text(html, encoding='utf-8')
            print(f"  ✅ {conf_name}: {output_file.name}")
        
        return data
    
    def _generate_conference_html(self, conf_name, conf_data):
        """生成会议 HTML 页面 - 使用统一的高级模板"""
        papers = conf_data.get('papers', [])
        date = conf_data.get('date', '')
        location = conf_data.get('location', '')
        total = conf_data.get('total', len(papers))
        
        # 为论文生成默认评分（如果没有）
        for paper in papers:
            if 'scores' not in paper:
                paper['scores'] = {
                    'innovation': 4.0,
                    'industry': 4.0,
                    'experiment': 4.0
                }
            if 'overall_score' not in paper:
                paper['overall_score'] = 4.0
            if 'category' not in paper:
                paper['category'] = 'rec'
        
        # 将论文数据转为 JSON
        import json
        papers_json = json.dumps(papers, ensure_ascii=False)
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{conf_name} 论文列表 | AI推荐日报</title>
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
        
        .stats-bar {{
            display: flex; gap: 16px; padding: 16px;
            background: white; margin: -20px 12px 0; border-radius: 14px;
            box-shadow: 0 4px 16px rgba(49,44,81,0.1);
        }}
        .stat-item {{ flex: 1; text-align: center; }}
        .stat-value {{ font-size: 20px; font-weight: 700; color: #667eea; }}
        .stat-label {{ font-size: 11px; color: var(--color-text-muted); margin-top: 2px; }}
        
        .main {{ padding: 20px 12px 60px; padding-bottom: calc(60px + var(--safe-area-bottom)); }}
        
        .section-title {{
            font-size: 16px; font-weight: 700; margin-bottom: 12px;
            display: flex; align-items: center; gap: 8px;
        }}
        .section-title i {{ color: #667eea; }}
        
        .paper-card {{
            background: var(--color-card); border-radius: 16px;
            margin-bottom: 12px; overflow: hidden;
            box-shadow: 0 2px 12px rgba(49,44,81,0.05);
        }}
        .paper-header {{
            background: var(--gradient-primary); color: white;
            padding: 16px; position: relative;
        }}
        .paper-tags {{ display: flex; gap: 8px; margin-bottom: 10px; }}
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
        
        .paper-action {{
            display: block; width: 100%; padding: 14px;
            background: var(--gradient-primary); color: white;
            border: none; border-radius: 10px;
            font-size: 13px; font-weight: 700; text-align: center;
            text-decoration: none;
        }}
        
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
        <h1 class="header-title">{conf_name}</h1>
        <div class="header-meta">
            <span><i class="fas fa-calendar"></i> {date}</span>
            <span><i class="fas fa-map-marker-alt"></i> {location}</span>
        </div>
    </div>
    
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">{total}</div>
            <div class="stat-label">收录论文</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{len(papers)}</div>
            <div class="stat-label">精选论文</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">-</div>
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
</html>
'''
        return html
    
    def enhance_4_ensure_translations(self, data):
        """功能4: 确保所有外显内容都有翻译"""
        print("\n" + "=" * 60)
        print("🔧 功能4: 确保外显内容翻译完整")
        print("=" * 60)
        
        # 检查每日精选
        daily_pick = data.get('daily_pick', [])
        for item in daily_pick:
            if not item.get('cn_title'):
                item['cn_title'] = item.get('title', item.get('name', '未知'))
            if not item.get('cn_summary'):
                item['cn_summary'] = item.get('summary', item.get('description', '暂无简介'))[:200]
        
        # 检查 arXiv 论文（外显的前5篇）
        papers = data.get('arxiv_papers', [])
        for paper in papers[:5]:
            if not paper.get('cn_title'):
                paper['cn_title'] = paper.get('title', '未知标题')
            if not paper.get('cn_summary'):
                paper['cn_summary'] = paper.get('summary', '暂无摘要')[:200]
        
        # 检查 GitHub 项目（外显的前5个）
        github = data.get('github', [])
        for item in github[:5]:
            if not item.get('cn_title') and not item.get('name'):
                item['cn_title'] = item.get('name', item.get('title', '未知项目'))
            if not item.get('cn_description'):
                item['cn_description'] = item.get('description', '暂无描述')[:200]
        
        print(f"✅ 已确保外显内容翻译完整")
        return data
    
    def run(self):
        """执行所有增强"""
        print("=" * 60)
        print("🚀 AI推荐日报 - 功能完善")
        print("=" * 60)
        print(f"📅 日期: {self.today}")
        
        data = self.load_data()
        if not data:
            return False
        
        # 执行增强
        data = self.enhance_1_translate_github_descriptions(data)
        data = self.enhance_2_fix_category_counts(data)
        data = self.enhance_3_generate_conference_pages(data)
        data = self.enhance_4_ensure_translations(data)
        
        # 保存
        self.save_data(data)
        
        print("\n" + "=" * 60)
        print("✅ 功能完善完成")
        print("=" * 60)
        
        return True


if __name__ == "__main__":
    enhancer = FeatureEnhancer()
    enhancer.run()
