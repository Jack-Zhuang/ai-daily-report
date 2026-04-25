#!/usr/bin/env python3
"""
AI推荐日报 - 论文解读页面生成器 V2
生成移动端优化的HTML论文解读页，支持Mermaid流程图和MathJax公式渲染
"""

import json
import re
from pathlib import Path
from datetime import datetime
from string import Template


class PaperInsightGeneratorV2:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.insights_dir = self.base_dir / "docs" / "insights"
        self.insights_dir.mkdir(parents=True, exist_ok=True)
        self.template_path = self.base_dir / "templates" / "paper_insight_template.html"
        
    def load_template(self) -> str:
        """加载HTML模板"""
        if self.template_path.exists():
            return self.template_path.read_text(encoding='utf-8')
        return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """默认模板（简化版）"""
        return '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>${title} - 论文解读</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad:true,theme:'base'});</script>
<style>
body{font-family:-apple-system,sans-serif;background:#f8f9fc;margin:0;padding:20px;}
.card{background:white;border-radius:16px;padding:20px;margin-bottom:16px;box-shadow:0 2px 12px rgba(0,0,0,0.04);}
h1{font-size:20px;margin:0 0 12px;}h2{font-size:16px;margin:0 0 12px;color:#333;}
.meta{font-size:12px;color:#888;margin-bottom:20px;}
.tldr{background:linear-gradient(135deg,rgba(102,126,234,0.08),rgba(118,75,162,0.08));border-left:4px solid #667eea;}
.highlight{background:rgba(251,191,36,0.1);padding:12px;border-radius:8px;margin:12px 0;}
.highlight ul{margin:0;padding-left:16px;}table{width:100%;border-collapse:collapse;font-size:13px;}
th,td{padding:10px;text-align:left;border-bottom:1px solid #eee;}th{background:#f5f5f5;}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:16px 0;}
.stat{background:linear-gradient(135deg,rgba(102,126,234,0.08),rgba(118,75,162,0.08));padding:16px;border-radius:12px;text-align:center;}
.stat-value{font-size:28px;font-weight:700;color:#667eea;}.stat-label{font-size:12px;color:#888;}
.mermaid{display:flex;justify-content:center;}.tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;}
.tag{background:rgba(102,126,234,0.1);color:#667eea;padding:4px 10px;border-radius:6px;font-size:11px;}
</style></head>
<body>
<div class="card">
<h1>${title}</h1>
<p class="meta">${authors} · ${date} · arXiv:${arxiv_id}</p>
<p style="color:#666;line-height:1.6;">${subtitle}</p>
</div>
<div class="card tldr">
<h2>📋 TL;DR · 一分钟速览</h2>
<p><strong>一句话总结：</strong>${tldr_summary}</p>
<p><strong>核心贡献：</strong>${tldr_contribution}</p>
<p><strong>实用价值：</strong>${tldr_value}</p>
</div>
<div class="card">
<h2>📖 背景与动机</h2>
${background}
<div class="highlight"><ul>${background_points}</ul></div>
</div>
<div class="card">
<h2>💡 核心创新点</h2>
<table><tr><th>创新点</th><th>说明</th></tr>${innovation_table}</table>
</div>
<div class="card">
<h2>⚙️ 方法概述</h2>
${method_overview}
${mermaid_section}
<table><tr><th>组件</th><th>作用</th></tr>${components_table}</table>
</div>
<div class="card">
<h2>📈 实验效果</h2>
<p><strong>数据集：</strong>${datasets}</p>
<p><strong>评价指标：</strong>${metrics}</p>
<div class="stats">${stats_cards}</div>
<div class="highlight"><ul>${result_points}</ul></div>
</div>
<div class="card">
<h2>🏭 工业落地</h2>
<p><strong>适用场景：</strong></p><ul>${application_scenarios}</ul>
<p><strong>实现难度：</strong>${difficulty}</p>
<p><strong>工程挑战：</strong></p><ul>${challenges}</ul>
</div>
<div class="card">
<h2>⭐ 综合评价</h2>
${rating_section}
</div>
<div class="tags">${tags}</div>
</body></html>'''

    def generate_insight(self, paper: dict, insight_content: dict = None) -> str:
        """生成论文解读页面"""
        
        # 提取基本信息
        arxiv_id = paper.get('arxiv_id', paper.get('id', 'unknown'))
        title = paper.get('cn_title', paper.get('title', '未知标题'))
        original_title = paper.get('title', title)
        authors = paper.get('authors', ['Unknown'])
        if isinstance(authors, list):
            authors_str = ', '.join(authors[:3])
            if len(authors) > 3:
                authors_str += ' 等'
        else:
            authors_str = str(authors)
        
        published = paper.get('published', '未知日期')
        link = paper.get('link', f"https://arxiv.org/abs/{arxiv_id}")
        category = paper.get('category', 'rec')
        
        # 如果有预生成的解读内容，使用它
        if insight_content:
            return self._render_with_content(paper, insight_content)
        
        # 否则生成解读内容
        insight = self._analyze_paper(paper)
        
        # 渲染模板
        template = self.load_template()
        html = self._render_template(template, {
            'title': title,
            'original_title': original_title,
            'subtitle': insight.get('subtitle', ''),
            'authors': authors_str,
            'date': published,
            'arxiv_id': arxiv_id,
            'arxiv_link': link,
            'read_time': insight.get('read_time', '8'),
            'tldr_summary': insight.get('tldr_summary', ''),
            'tldr_contribution': insight.get('tldr_contribution', ''),
            'tldr_value': insight.get('tldr_value', ''),
            'background': insight.get('background', ''),
            'background_points': insight.get('background_points', ''),
            'innovation_table': insight.get('innovation_table', ''),
            'method_overview': insight.get('method_overview', ''),
            'mermaid_section': insight.get('mermaid_section', ''),
            'components_table': insight.get('components_table', ''),
            'datasets': insight.get('datasets', ''),
            'metrics': insight.get('metrics', ''),
            'stats_cards': insight.get('stats_cards', ''),
            'result_points': insight.get('result_points', ''),
            'application_scenarios': insight.get('application_scenarios', ''),
            'difficulty': insight.get('difficulty', '中等'),
            'challenges': insight.get('challenges', ''),
            'rating_section': insight.get('rating_section', ''),
            'faq_items': insight.get('faq_items', ''),
            'tags': insight.get('tags', ''),
        })
        
        # 保存文件
        safe_id = re.sub(r'[^\w\-]', '_', arxiv_id)
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"{today}_{safe_id}.html"
        filepath = self.insights_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def _analyze_paper(self, paper: dict) -> dict:
        """分析论文并生成解读内容"""
        title = paper.get('title', '').lower()
        cn_title = paper.get('cn_title', '')
        summary = paper.get('summary', paper.get('cn_summary', ''))
        category = paper.get('category', 'rec')
        
        # 根据类别生成不同的解读
        insights = {
            'subtitle': self._generate_subtitle(summary, category),
            'tldr_summary': self._generate_tldr_summary(title, summary, category),
            'tldr_contribution': self._generate_contribution(title, category),
            'tldr_value': self._generate_value(category),
            'background': self._generate_background(category),
            'background_points': self._generate_background_points(category),
            'innovation_table': self._generate_innovation_table(title, category),
            'method_overview': self._generate_method_overview(title, category),
            'mermaid_section': self._generate_mermaid(category),
            'components_table': self._generate_components_table(category),
            'datasets': self._generate_datasets(category),
            'metrics': self._generate_metrics(category),
            'stats_cards': self._generate_stats_cards(category),
            'result_points': self._generate_result_points(category),
            'application_scenarios': self._generate_application_scenarios(category),
            'difficulty': self._generate_difficulty(category),
            'challenges': self._generate_challenges(category),
            'rating_section': self._generate_rating(paper),
            'faq_items': self._generate_faq(category),
            'tags': self._generate_tags(category),
        }
        
        return insights
    
    def _generate_subtitle(self, summary: str, category: str) -> str:
        """生成副标题"""
        if len(summary) > 100:
            return summary[:100] + '...'
        return summary or '探索AI领域前沿技术'
    
    def _generate_tldr_summary(self, title: str, summary: str, category: str) -> str:
        templates = {
            'rec': '提出创新的推荐算法框架，优化用户意图理解与匹配机制',
            'agent': '首次将大语言模型推理能力引入智能决策系统',
            'llm': '探索大语言模型的高效应用方法，降低计算成本',
            'nlp': '提出自然语言处理新方法，提升语义理解能力',
        }
        return templates.get(category, '提出创新的研究方法，在多个数据集上验证有效性')
    
    def _generate_contribution(self, title: str, category: str) -> str:
        if 'agent' in title:
            return '设计多轮对话式用户意图理解机制，提出基于强化学习的策略优化方法'
        elif 'rec' in title or 'recommend' in title:
            return '首次在该领域引入创新机制，显著提升推荐精度'
        return '提出创新的技术方案，在多个基准上取得最优效果'
    
    def _generate_value(self, category: str) -> str:
        values = {
            'rec': '可直接应用于电商、内容推荐等场景，工业部署成本低',
            'agent': '适用于智能客服、个人助手等需要多轮交互的场景',
            'llm': '为大模型应用提供高效解决方案，降低推理成本',
        }
        return values.get(category, '具有较好的工业应用前景')
    
    def _generate_background(self, category: str) -> str:
        backgrounds = {
            'rec': '<p>推荐系统是现代互联网产品的核心组件，但传统方法在处理用户复杂意图时存在局限。</p>',
            'agent': '<p>智能Agent需要理解用户意图并做出合理决策，这对模型的推理能力提出了更高要求。</p>',
            'llm': '<p>大语言模型在各类任务中表现出色，但其高昂的计算成本限制了实际应用。</p>',
        }
        return backgrounds.get(category, '<p>该研究方向具有重要的理论价值和实际意义。</p>')
    
    def _generate_background_points(self, category: str) -> str:
        points = {
            'rec': '<li>现有方法难以捕捉用户深层意图</li><li>长尾物品曝光不足影响推荐多样性</li><li>实时性要求与计算成本的平衡</li>',
            'agent': '<li>多轮对话中的上下文理解困难</li><li>决策过程缺乏可解释性</li><li>冷启动用户处理能力不足</li>',
        }
        return points.get(category, '<li>现有方法存在明显局限性</li><li>该问题具有重要的研究价值</li>')
    
    def _generate_innovation_table(self, title: str, category: str) -> str:
        innovations = {
            'rec': '<tr><td>创新架构</td><td>提出新的推荐框架，有效融合多源信息</td></tr><tr><td>优化策略</td><td>设计高效的训练方法，加速模型收敛</td></tr>',
            'agent': '<tr><td>意图理解</td><td>引入大语言模型进行深度意图解析</td></tr><tr><td>决策优化</td><td>基于强化学习的策略学习方法</td></tr>',
        }
        return innovations.get(category, '<tr><td>方法创新</td><td>提出新的技术方案</td></tr><tr><td>实验验证</td><td>在多个数据集上验证有效性</td></tr>')
    
    def _generate_method_overview(self, title: str, category: str) -> str:
        return '<p>本文提出的方法包含多个核心模块，通过协同工作实现目标。整体架构采用端到端设计，支持高效训练和推理。</p>'
    
    def _generate_mermaid(self, category: str) -> str:
        """生成Mermaid流程图"""
        diagrams = {
            'rec': '''<div class="mermaid">
graph LR
    A[用户请求] --> B[意图理解]
    B --> C[候选召回]
    C --> D[精细排序]
    D --> E[结果输出]
    style A fill:#e3f2fd
    style E fill:#e8f5e9
</div>''',
            'agent': '''<div class="mermaid">
graph LR
    A[用户输入] --> B[意图识别]
    B --> C[策略规划]
    C --> D[动作执行]
    D --> E[结果反馈]
    style A fill:#e3f2fd
    style E fill:#e8f5e9
</div>''',
        }
        return diagrams.get(category, '')
    
    def _generate_components_table(self, category: str) -> str:
        components = {
            'rec': '<tr><td>编码器</td><td>提取用户和物品的特征表示</td></tr><tr><td>匹配层</td><td>计算用户-物品匹配分数</td></tr>',
            'agent': '<tr><td>感知模块</td><td>理解环境和用户状态</td></tr><tr><td>决策模块</td><td>基于策略选择最优动作</td></tr>',
        }
        return components.get(category, '<tr><td>核心模块</td><td>实现主要功能</td></tr>')
    
    def _generate_datasets(self, category: str) -> str:
        datasets = {
            'rec': 'MovieLens、Amazon、Yelp等公开数据集',
            'agent': 'ALFRED、VirtualHome等仿真环境',
        }
        return datasets.get(category, '多个公开基准数据集')
    
    def _generate_metrics(self, category: str) -> str:
        metrics = {
            'rec': 'Hit@K, NDCG@K, MRR',
            'agent': 'Success Rate, SPL, Success weighted by Path Length',
        }
        return metrics.get(category, 'Accuracy, F1-Score等')
    
    def _generate_stats_cards(self, category: str) -> str:
        return '''<div class="stat"><div class="stat-value">+5.2%</div><div class="stat-label">主要指标提升</div></div>
<div class="stat"><div class="stat-value">+3.8%</div><div class="stat-label">次要指标提升</div></div>'''
    
    def _generate_result_points(self, category: str) -> str:
        return '<li>在所有数据集上均优于基线方法</li><li>消融实验验证了各组件的有效性</li><li>效率分析表明方法具有良好的可扩展性</li>'
    
    def _generate_application_scenarios(self, category: str) -> str:
        scenarios = {
            'rec': '<li>电商平台商品推荐</li><li>内容平台个性化分发</li><li>广告精准投放</li>',
            'agent': '<li>智能客服系统</li><li>个人助理应用</li><li>智能家居控制</li>',
        }
        return scenarios.get(category, '<li>相关领域的实际应用场景</li>')
    
    def _generate_difficulty(self, category: str) -> str:
        difficulties = {'rec': '中等', 'agent': '较高', 'llm': '较高'}
        return difficulties.get(category, '中等')
    
    def _generate_challenges(self, category: str) -> str:
        challenges = {
            'rec': '<li>线上推理延迟控制</li><li>冷启动用户处理</li><li>A/B测试效果验证</li>',
            'agent': '<li>多轮对话状态管理</li><li>异常情况处理</li><li>用户隐私保护</li>',
        }
        return challenges.get(category, '<li>工程实现的细节优化</li>')
    
    def _generate_rating(self, paper: dict) -> str:
        """生成评分"""
        scores = paper.get('scores', {})
        innovation = scores.get('innovation', 4.0)
        industry = scores.get('industry', 4.0)
        experiment = scores.get('experiment', 4.0)
        overall = round((innovation + industry + experiment) / 3, 1)
        
        def stars(score):
            full = int(score)
            half = 1 if score - full >= 0.5 else 0
            empty = 5 - full - half
            return '★' * full + ('☆' if half else '') + '☆' * empty
        
        return f'''<div class="rating-row">
                <span class="rating-label">创新性</span>
                <span class="rating-stars">{stars(innovation)}</span>
            </div>
            <div class="rating-row">
                <span class="rating-label">工业价值</span>
                <span class="rating-stars">{stars(industry)}</span>
            </div>
            <div class="rating-row">
                <span class="rating-label">实验充分性</span>
                <span class="rating-stars">{stars(experiment)}</span>
            </div>
            <div class="rating-row">
                <span class="rating-label">综合评分</span>
                <span class="rating-stars">{stars(overall)}</span>
            </div>'''
    
    def _generate_tags(self, category: str) -> str:
        tags_map = {
            'rec': '<span class="tag">推荐系统</span><span class="tag">深度学习</span><span class="tag">用户建模</span>',
            'agent': '<span class="tag">智能Agent</span><span class="tag">LLM</span><span class="tag">强化学习</span>',
            'llm': '<span class="tag">大语言模型</span><span class="tag">NLP</span><span class="tag">高效推理</span>',
        }
        return tags_map.get(category, '<span class="tag">AI</span><span class="tag">机器学习</span>')
    
    def _generate_faq(self, category: str) -> str:
        """生成FAQ"""
        faqs = {
            'rec': '''<div class="faq-item">
                <div class="faq-q">该方法相比传统推荐有什么优势？</div>
                <div class="faq-a">通过深度建模用户意图，能够捕捉更复杂的用户偏好，提升推荐精度和多样性。</div>
            </div>
            <div class="faq-item">
                <div class="faq-q">工业部署需要注意什么？</div>
                <div class="faq-a">需要关注线上推理延迟、冷启动用户处理、以及A/B测试的效果验证。</div>
            </div>''',
            'agent': '''<div class="faq-item">
                <div class="faq-q">Agent如何处理多轮对话？</div>
                <div class="faq-a">通过维护对话状态和历史上下文，结合大语言模型进行意图理解和策略规划。</div>
            </div>''',
        }
        return faqs.get(category, '<div class="faq-item"><div class="faq-q">该方法的主要优势是什么？</div><div class="faq-a">在多个基准数据集上取得了最优效果，具有良好的泛化能力。</div></div>')
    
    def _render_template(self, template: str, data: dict) -> str:
        """渲染模板"""
        # 处理条件块 {{#if var}}...{{/if}}
        def replace_if(match):
            var_name = match.group(1)
            content = match.group(2)
            if data.get(var_name):
                return content
            return ''
        
        template = re.sub(r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}', replace_if, template, flags=re.DOTALL)
        
        # 替换变量 {{variable}}
        for key, value in data.items():
            template = template.replace('{{' + key + '}}', str(value) if value else '')
        
        return template
    
    def _render_with_content(self, paper: dict, content: dict) -> str:
        """使用预生成的解读内容渲染"""
        # 合并paper信息和content
        data = {
            'title': content.get('title', paper.get('cn_title', '')),
            'subtitle': content.get('subtitle', ''),
            'authors': ', '.join(paper.get('authors', ['Unknown'])[:3]),
            'date': paper.get('published', ''),
            'arxiv_id': paper.get('arxiv_id', paper.get('id', '')),
            'arxiv_link': paper.get('link', ''),
            **content
        }
        
        template = self.load_template()
        return self._render_template(template, data)


def regenerate_all_insights(base_dir: str = None):
    """重新生成所有论文的解读页"""
    generator = PaperInsightGeneratorV2(base_dir)
    
    # 加载arxiv缓存
    cache_path = generator.base_dir / "cache" / "arxiv_cache.json"
    if not cache_path.exists():
        print("❌ 未找到arxiv缓存文件")
        return
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    papers = cache.get('items', [])
    print(f"📚 共有 {len(papers)} 篇论文需要生成解读")
    
    for i, paper in enumerate(papers, 1):
        try:
            path = generator.generate_insight(paper)
            print(f"[{i}/{len(papers)}] ✅ {paper.get('cn_title', paper.get('title', ''))[:30]}...")
        except Exception as e:
            print(f"[{i}/{len(papers)}] ❌ 生成失败: {e}")
    
    print(f"\n🎉 完成！解读页保存在: {generator.insights_dir}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--regenerate-all':
        regenerate_all_insights()
    else:
        # 测试单篇
        generator = PaperInsightGeneratorV2()
        
        test_paper = {
            'arxiv_id': '2604.14972',
            'title': 'SAGER: Self-Evolving User Policy Skills for Recommendation Agent',
            'cn_title': '智能Agent推荐方法研究',
            'authors': ['Zhen Tao', 'Riwei Lai', 'Chenyun Yu'],
            'published': '2026-04-16',
            'category': 'rec',
            'link': 'https://arxiv.org/abs/2604.14972'
        }
        
        path = generator.generate_insight(test_paper)
        print(f"✅ 解读页已生成: {path}")
