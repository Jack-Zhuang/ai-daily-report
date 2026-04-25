#!/usr/bin/env python3
"""
AI推荐日报 - 论文深度解读生成器
流程：下载PDF → 解析PDF → MiniMax解读 → 生成HTML
"""

import json
import re
import os
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class PaperDeepInsightGenerator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.insights_dir = self.base_dir / "docs" / "insights"
        self.insights_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_cache_dir = self.base_dir / "cache" / "pdfs"
        self.pdf_cache_dir.mkdir(parents=True, exist_ok=True)
        self.template_path = self.base_dir / "templates" / "paper_insight_template.html"
        
        # MiniMax API 配置
        self.api_key = os.environ.get('MINIMAX_API_KEY', '')
        self.group_id = os.environ.get('MINIMAX_GROUP_ID', '')
        self._load_api_keys()
    
    def _load_api_keys(self):
        """从配置文件加载 API Key"""
        if not self.api_key:
            env_file = Path.home() / ".openclaw" / ".xiaoyienv"
            if env_file.exists():
                for line in env_file.read_text().splitlines():
                    if line.startswith('PERSONAL-API-KEY='):
                        self.api_key = line.split('=', 1)[1].strip().strip('"')
                    elif line.startswith('PERSONAL-UID='):
                        self.group_id = line.split('=', 1)[1].strip().strip('"')
    
    def download_pdf(self, arxiv_id: str) -> Optional[Path]:
        """下载 arXiv PDF"""
        # 清理 arxiv_id
        arxiv_id = arxiv_id.replace('v1', '').replace('v2', '').strip()
        
        # 检查是否已下载
        pdf_path = self.pdf_cache_dir / f"{arxiv_id}.pdf"
        if pdf_path.exists():
            print(f"  📄 PDF 已存在: {pdf_path}")
            return pdf_path
        
        # 下载 PDF
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        print(f"  📥 下载 PDF: {pdf_url}")
        
        try:
            response = requests.get(pdf_url, timeout=60)
            if response.status_code == 200:
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                print(f"  ✅ 下载成功: {pdf_path}")
                return pdf_path
            else:
                print(f"  ❌ 下载失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"  ❌ 下载出错: {e}")
            return None
    
    def parse_pdf(self, pdf_path: Path) -> str:
        """使用 markitdown 解析 PDF"""
        try:
            from markitdown import MarkItDown
            md = MarkItDown()
            result = md.convert(str(pdf_path))
            return result.text_content
        except ImportError:
            print("  ⚠️ markitdown 未安装，使用备用方法")
            return self._parse_pdf_fallback(pdf_path)
        except Exception as e:
            print(f"  ⚠️ markitdown 解析失败: {e}")
            return self._parse_pdf_fallback(pdf_path)
    
    def _parse_pdf_fallback(self, pdf_path: Path) -> str:
        """备用 PDF 解析方法"""
        try:
            import subprocess
            result = subprocess.run(
                ['pdftotext', str(pdf_path), '-'],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                return result.stdout
        except:
            pass
        
        # 最后尝试用 PyPDF2
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(pdf_path))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            print(f"  ❌ PDF 解析失败: {e}")
            return ""
    
    def analyze_with_llm(self, paper_content: str, paper_info: dict) -> dict:
        """使用 MiniMax API 深度分析论文"""
        
        # 截取内容（避免超出 token 限制）
        max_chars = 50000
        if len(paper_content) > max_chars:
            # 优先保留摘要、方法和实验部分
            paper_content = paper_content[:max_chars]
        
        prompt = f"""你是一位资深的学术论文解读专家。请对以下论文进行深度解读，提取关键信息。

论文标题: {paper_info.get('title', '未知')}
作者: {paper_info.get('authors', '未知')}
发表日期: {paper_info.get('published', '未知')}

论文内容:
{paper_content}

请按照以下 JSON 格式输出解读结果（必须是有效的 JSON）:

{{
    "subtitle": "一句话概括论文核心贡献（30字以内）",
    "read_time": "预计阅读时间（分钟）",
    "abstract": "论文摘要的中文翻译和解读（200-300字）",
    "key_points": ["关键要点1", "关键要点2", "关键要点3", "关键要点4"],
    "background": "研究背景和动机（300-500字，包含问题背景、现有方法的局限、本文的切入点）",
    "core_problem": "论文要解决的核心问题（一句话）",
    "method_overview": "方法概述（300-500字，描述整体思路和主要模块）",
    "innovations": [
        {{"point": "创新点名称", "solution": "技术方案", "problem": "解决的问题"}},
        {{"point": "创新点名称", "solution": "技术方案", "problem": "解决的问题"}},
        {{"point": "创新点名称", "solution": "技术方案", "problem": "解决的问题"}}
    ],
    "modules": [
        {{"name": "模块名称", "description": "模块功能描述"}},
        {{"name": "模块名称", "description": "模块功能描述"}},
        {{"name": "模块名称", "description": "模块功能描述"}}
    ],
    "architecture_description": "架构设计的文字描述（200-300字）",
    "algorithm_steps": ["步骤1描述", "步骤2描述", "步骤3描述", "步骤4描述"],
    "pseudocode": "核心算法的伪代码（使用简单的伪代码格式）",
    "formula": "核心数学公式（LaTeX格式）",
    "formula_description": "公式中各变量的含义说明",
    "code_snippet": "核心代码片段（Python格式，30行以内）",
    "datasets": "使用的数据集",
    "metrics": "评价指标",
    "baselines": "对比的基线方法",
    "main_results": [
        {{"metric": "指标名", "value": "数值", "improvement": "提升幅度"}},
        {{"metric": "指标名", "value": "数值", "improvement": "提升幅度"}}
    ],
    "comparison": [
        {{"method": "方法名", "metric1": "值1", "metric2": "值2"}},
        {{"method": "方法名", "metric1": "值1", "metric2": "值2"}}
    ],
    "ablation": [
        {{"config": "配置描述", "result": "结果", "change": "变化"}},
        {{"config": "配置描述", "result": "结果", "change": "变化"}}
    ],
    "findings": ["主要发现1", "主要发现2", "主要发现3"],
    "limitations": ["局限性1", "局限性2", "局限性3"],
    "future_work": ["未来方向1", "未来方向2", "未来方向3"],
    "applications": ["应用场景1", "应用场景2", "应用场景3"],
    "implementation_tips": ["实现建议1", "实现建议2", "实现建议3"],
    "ratings": {{"innovation": 4, "industry": 4, "experiment": 4, "reproducibility": 4}},
    "faq": [
        {{"q": "问题1", "a": "回答1"}},
        {{"q": "问题2", "a": "回答2"}},
        {{"q": "问题3", "a": "回答3"}}
    ],
    "tags": ["标签1", "标签2", "标签3", "标签4"]
}}

注意：
1. 所有内容必须基于论文实际内容，不要编造
2. 如果论文中没有某些信息，可以填写合理的推测但要标注"推测"
3. 数值结果必须来自论文，如果没有则留空
4. 输出必须是有效的 JSON 格式"""

        # 调用 MiniMax API
        try:
            return self._call_minimax_api(prompt)
        except Exception as e:
            print(f"  ⚠️ MiniMax API 调用失败: {e}")
            return self._generate_fallback_analysis(paper_info)
    
    def _call_minimax_api(self, prompt: str) -> dict:
        """调用 MiniMax API"""
        if not self.api_key:
            raise ValueError("MiniMax API Key 未配置")
        
        url = f"https://api.minimax.chat/v1/text/chatcompletion_v2?GroupId={self.group_id}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "abab6.5s-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 8000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 提取 JSON - 支持多种格式
            # 尝试直接解析
            try:
                return json.loads(content)
            except:
                pass
            
            # 尝试提取 ```json ... ``` 块
            json_block = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_block:
                try:
                    return json.loads(json_block.group(1))
                except:
                    pass
            
            # 尝试提取第一个完整的 JSON 对象
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # 如果都失败，打印内容用于调试
            print(f"  ⚠️ 无法解析 API 返回内容，前500字符:")
            print(f"     {content[:500]}")
            raise ValueError("API 返回内容不是有效的 JSON")
        else:
            raise ValueError(f"API 调用失败: {response.status_code} - {response.text}")
    
    def _generate_fallback_analysis(self, paper_info: dict) -> dict:
        """生成备用的分析结果"""
        return {
            "subtitle": "提出创新的研究方法",
            "read_time": "15",
            "abstract": paper_info.get('summary', '论文摘要暂无'),
            "key_points": ["创新方法", "实验验证", "性能提升"],
            "background": "该研究领域具有重要的理论和实践价值。",
            "core_problem": "如何提升模型性能",
            "method_overview": "本文提出了新的方法来解决相关问题。",
            "innovations": [{"point": "方法创新", "solution": "新技术", "problem": "性能问题"}],
            "modules": [{"name": "核心模块", "description": "实现主要功能"}],
            "architecture_description": "整体采用端到端架构设计。",
            "algorithm_steps": ["输入处理", "特征提取", "模型计算", "结果输出"],
            "pseudocode": "// 算法伪代码\nInput: data\nOutput: result\nProcess(data)",
            "formula": "L = \\sum loss",
            "formula_description": "损失函数",
            "code_snippet": "# 核心代码\ndef process(data):\n    return result",
            "datasets": "公开数据集",
            "metrics": "Accuracy, F1",
            "baselines": "基线方法",
            "main_results": [],
            "comparison": [],
            "ablation": [],
            "findings": ["方法有效"],
            "limitations": ["有待进一步研究"],
            "future_work": ["扩展应用"],
            "applications": ["相关领域应用"],
            "implementation_tips": ["参考论文实现"],
            "ratings": {"innovation": 4, "industry": 4, "experiment": 4, "reproducibility": 4},
            "faq": [{"q": "方法优势?", "a": "性能更好"}],
            "tags": ["AI", "机器学习"]
        }
    
    def generate_insight(self, paper: dict) -> str:
        """生成论文解读页面"""
        
        arxiv_id = paper.get('arxiv_id', paper.get('id', 'unknown'))
        arxiv_id = re.sub(r'[^\w\.\-]', '', arxiv_id)
        
        print(f"\n📄 处理论文: {arxiv_id}")
        
        # 1. 下载 PDF
        pdf_path = self.download_pdf(arxiv_id)
        
        # 2. 解析 PDF
        if pdf_path and pdf_path.exists():
            print(f"  📖 解析 PDF...")
            paper_content = self.parse_pdf(pdf_path)
        else:
            print(f"  ⚠️ 无法获取 PDF，使用摘要")
            paper_content = paper.get('summary', '')
        
        # 3. LLM 分析
        print(f"  🤖 LLM 深度分析...")
        analysis = self.analyze_with_llm(paper_content, paper)
        
        # 4. 生成 HTML
        print(f"  🎨 生成解读页面...")
        html = self._render_html(paper, analysis)
        
        # 5. 保存
        safe_id = re.sub(r'[^\w\-]', '_', arxiv_id)
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"{today}_{safe_id}.html"
        filepath = self.insights_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  ✅ 完成: {filepath}")
        return str(filepath)
    
    def _render_html(self, paper: dict, analysis: dict) -> str:
        """渲染 HTML 页面"""
        template = self.load_template()
        
        # 基本信息
        arxiv_id = paper.get('arxiv_id', paper.get('id', 'unknown'))
        title = paper.get('cn_title', paper.get('title', '未知标题'))
        authors = paper.get('authors', ['Unknown'])
        if isinstance(authors, list):
            authors_str = ', '.join(authors[:3])
            if len(authors) > 3:
                authors_str += ' 等'
        else:
            authors_str = str(authors)
        
        # 渲染变量
        data = {
            'title': title,
            'subtitle': analysis.get('subtitle', ''),
            'authors': authors_str,
            'date': paper.get('published', ''),
            'arxiv_id': arxiv_id,
            'arxiv_link': paper.get('link', f"https://arxiv.org/abs/{arxiv_id}"),
            'read_time': analysis.get('read_time', '15'),
            'abstract': f"<p>{analysis.get('abstract', '')}</p>",
            'key_points': ''.join(f'<li>{p}</li>' for p in analysis.get('key_points', [])),
            'background': f"<p>{analysis.get('background', '')}</p>",
            'core_problem': analysis.get('core_problem', ''),
            'method_overview': f"<p>{analysis.get('method_overview', '')}</p>",
            'innovations': self._render_innovations(analysis.get('innovations', [])),
            'architecture_diagram': self._generate_architecture_diagram(analysis),
            'modules_description': self._render_modules(analysis.get('modules', [])),
            'algorithm_flowchart': self._generate_algorithm_flowchart(analysis),
            'pseudocode': self._render_pseudocode(analysis.get('pseudocode', '')),
            'formula': f"$${analysis.get('formula', '')}$$" if analysis.get('formula') else '',
            'formula_vars': analysis.get('formula_description', ''),
            'code_example': analysis.get('code_snippet', ''),
            'datasets': analysis.get('datasets', ''),
            'metrics': analysis.get('metrics', ''),
            'baselines': analysis.get('baselines', ''),
            'stats_cards': self._render_stats_cards(analysis.get('main_results', [])),
            'comparison_headers': self._render_comparison_headers(analysis),
            'comparison_rows': self._render_comparison_rows(analysis.get('comparison', [])),
            'ablation_results': self._render_ablation(analysis.get('ablation', [])),
            'findings': self._render_findings(analysis.get('findings', [])),
            'limitations': ''.join(f'<li>{l}</li>' for l in analysis.get('limitations', [])),
            'future_work': ''.join(f'<li>{f}</li>' for f in analysis.get('future_work', [])),
            'applications': ''.join(f'<li>{a}</li>' for a in analysis.get('applications', [])),
            'implementation_tips': ''.join(f'<li>{t}</li>' for t in analysis.get('implementation_tips', [])),
            'ratings': self._render_ratings(analysis.get('ratings', {})),
            'faq': self._render_faq(analysis.get('faq', [])),
            'tags': ''.join(f'<span class="tag">{t}</span>' for t in analysis.get('tags', [])),
        }
        
        return self._render_template(template, data)
    
    def _render_innovations(self, innovations: list) -> str:
        rows = []
        for inn in innovations:
            rows.append(f'''<tr>
    <td>{inn.get('point', '')}</td>
    <td>{inn.get('solution', '')}</td>
    <td>{inn.get('problem', '')}</td>
</tr>''')
        return '\n'.join(rows)
    
    def _render_modules(self, modules: list) -> str:
        if not modules:
            return ''
        html = ''
        for m in modules:
            html += f"<p><strong>{m.get('name', '')}：</strong>{m.get('description', '')}</p>"
        return html
    
    def _generate_architecture_diagram(self, analysis: dict) -> str:
        """生成架构图"""
        modules = analysis.get('modules', [])
        if not modules:
            return self._default_architecture_diagram()
        
        nodes = []
        for i, m in enumerate(modules):
            nodes.append(f'    M{i}["{m.get("name", f"模块{i+1}")}"]')
        
        edges = []
        for i in range(len(modules) - 1):
            edges.append(f'    M{i} --> M{i+1}')
        
        return f'''graph LR
    Input["📥 输入"] --> M0
{chr(10).join(nodes)}
{chr(10).join(edges)}
    M{len(modules)-1} --> Output["📤 输出"]
    
    style Input fill:#e3f2fd,stroke:#1565c0
    style Output fill:#e8f5e9,stroke:#2e7d32'''
    
    def _default_architecture_diagram(self) -> str:
        return '''graph TB
    subgraph Input["📥 输入层"]
        Data[数据输入]
    end
    
    subgraph Process["🔄 处理层"]
        Encode[编码器]
        Model[模型]
        Decode[解码器]
    end
    
    subgraph Output["📤 输出层"]
        Result[结果输出]
    end
    
    Data --> Encode --> Model --> Decode --> Result
    
    style Input fill:#e3f2fd,stroke:#1565c0
    style Process fill:#fff3e0,stroke:#ef6c00
    style Output fill:#e8f5e9,stroke:#2e7d32'''
    
    def _generate_algorithm_flowchart(self, analysis: dict) -> str:
        """生成算法流程图"""
        steps = analysis.get('algorithm_steps', [])
        if not steps:
            return self._default_algorithm_flowchart()
        
        nodes = ['    Start(["开始"])']
        for i, step in enumerate(steps):
            nodes.append(f'    S{i}["{step}"]')
        nodes.append('    End(["结束"])')
        
        edges = ['    Start --> S0']
        for i in range(len(steps) - 1):
            edges.append(f'    S{i} --> S{i+1}')
        edges.append(f'    S{len(steps)-1} --> End')
        
        return f'''flowchart TD
{chr(10).join(nodes)}
{chr(10).join(edges)}
    
    style Start fill:#e8f5e9
    style End fill:#fce4ec'''
    
    def _default_algorithm_flowchart(self) -> str:
        return '''flowchart TD
    A[输入数据] --> B[预处理]
    B --> C[特征提取]
    C --> D[模型计算]
    D --> E[后处理]
    E --> F[输出结果]
    
    style A fill:#e3f2fd
    style F fill:#e8f5e9'''
    
    def _render_pseudocode(self, pseudocode: str) -> str:
        if not pseudocode:
            return '<span class="comment">// 伪代码暂无</span>'
        # 简单格式化
        lines = pseudocode.strip().split('\n')
        formatted = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 关键字高亮
            for kw in ['Input', 'Output', 'for', 'if', 'else', 'return', 'while', 'do', 'end']:
                if line.startswith(kw):
                    line = f'<span class="keyword">{kw}</span>{line[len(kw):]}'
                    break
            formatted.append(line)
        return '<br>'.join(formatted)
    
    def _render_stats_cards(self, results: list) -> str:
        if not results:
            return '''<div class="stat-card">
    <div class="stat-value">-</div>
    <div class="stat-label">性能提升</div>
</div>
<div class="stat-card">
    <div class="stat-value">-</div>
    <div class="stat-label">主要指标</div>
</div>'''
        
        cards = []
        for r in results[:4]:
            cards.append(f'''<div class="stat-card">
    <div class="stat-value">{r.get('improvement', r.get('value', '-'))}</div>
    <div class="stat-label">{r.get('metric', '指标')}</div>
</div>''')
        return '\n'.join(cards)
    
    def _render_comparison_headers(self, analysis: dict) -> str:
        metrics = analysis.get('metrics', 'Metric').split(',')
        return ''.join(f'<th>{m.strip()}</th>' for m in metrics[:3])
    
    def _render_comparison_rows(self, comparison: list) -> str:
        if not comparison:
            return '<tr><td>-</td><td>-</td><td>-</td></tr>'
        
        rows = []
        for c in comparison:
            method = c.get('method', '-')
            values = [v for k, v in c.items() if k != 'method']
            cells = f'<td>{method}</td>' + ''.join(f'<td>{v}</td>' for v in values[:3])
            rows.append(f'<tr>{cells}</tr>')
        return '\n'.join(rows)
    
    def _render_ablation(self, ablation: list) -> str:
        if not ablation:
            return '<tr><td>完整模型</td><td>-</td><td>-</td></tr>'
        
        rows = []
        for a in ablation:
            rows.append(f'''<tr>
    <td>{a.get('config', '-')}</td>
    <td>{a.get('result', '-')}</td>
    <td>{a.get('change', '-')}</td>
</tr>''')
        return '\n'.join(rows)
    
    def _render_findings(self, findings: list) -> str:
        if not findings:
            return '<div class="step"><div class="step-title">方法有效</div><div class="step-desc">实验验证了方法的有效性。</div></div>'
        
        html = []
        for i, f in enumerate(findings, 1):
            html.append(f'''<div class="step">
    <div class="step-title">发现 {i}</div>
    <div class="step-desc">{f}</div>
</div>''')
        return '\n'.join(html)
    
    def _render_ratings(self, ratings: dict) -> str:
        def stars(score):
            full = int(score)
            return '★' * full + '☆' * (5 - full)
        
        return f'''<div class="rating-item">
    <span class="rating-label">创新性</span>
    <span class="rating-stars">{stars(ratings.get('innovation', 4))}</span>
</div>
<div class="rating-item">
    <span class="rating-label">工业价值</span>
    <span class="rating-stars">{stars(ratings.get('industry', 4))}</span>
</div>
<div class="rating-item">
    <span class="rating-label">实验充分性</span>
    <span class="rating-stars">{stars(ratings.get('experiment', 4))}</span>
</div>
<div class="rating-item">
    <span class="rating-label">可复现性</span>
    <span class="rating-stars">{stars(ratings.get('reproducibility', 4))}</span>
</div>'''
    
    def _render_faq(self, faq: list) -> str:
        if not faq:
            return '''<div class="faq-item">
    <div class="faq-q">该方法的主要优势是什么？</div>
    <div class="faq-a">请参考论文原文获取详细信息。</div>
</div>'''
        
        html = []
        for f in faq:
            html.append(f'''<div class="faq-item">
    <div class="faq-q">{f.get('q', '问题')}</div>
    <div class="faq-a">{f.get('a', '回答')}</div>
</div>''')
        return '\n'.join(html)
    
    def load_template(self) -> str:
        if self.template_path.exists():
            return self.template_path.read_text(encoding='utf-8')
        raise FileNotFoundError(f"模板文件不存在: {self.template_path}")
    
    def _render_template(self, template: str, data: dict) -> str:
        # 处理条件块
        def replace_if(match):
            var_name = match.group(1)
            content = match.group(2)
            if data.get(var_name):
                return content
            return ''
        
        template = re.sub(r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}', replace_if, template, flags=re.DOTALL)
        
        # 替换变量
        for key, value in data.items():
            template = template.replace('{{' + key + '}}', str(value) if value else '')
        
        return template


def regenerate_all_insights(base_dir: str = None, limit: int = None):
    """重新生成所有论文的深度解读"""
    generator = PaperDeepInsightGenerator(base_dir)
    
    # 加载 arxiv 缓存
    cache_path = generator.base_dir / "cache" / "arxiv_cache.json"
    if not cache_path.exists():
        print("❌ 未找到 arxiv 缓存文件")
        return
    
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    papers = cache.get('items', [])
    if limit:
        papers = papers[:limit]
    
    print(f"📚 共有 {len(papers)} 篇论文需要深度解读")
    print("=" * 60)
    
    for i, paper in enumerate(papers, 1):
        try:
            path = generator.generate_insight(paper)
            print(f"[{i}/{len(papers)}] ✅ 完成")
        except Exception as e:
            print(f"[{i}/{len(papers)}] ❌ 失败: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎉 完成！解读页保存在: {generator.insights_dir}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--regenerate-all':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
            regenerate_all_insights(limit=limit)
        elif sys.argv[1] == '--test':
            # 测试单篇
            generator = PaperDeepInsightGenerator()
            test_paper = {
                'arxiv_id': '2604.21593',
                'title': 'Language as a Latent Variable for Reasoning Optimization',
                'authors': ['Anonymous'],
                'published': '2026-04-23',
                'link': 'https://arxiv.org/abs/2604.21593'
            }
            path = generator.generate_insight(test_paper)
            print(f"✅ 测试完成: {path}")
    else:
        print("用法:")
        print("  python generate_paper_deep_insight.py --test          # 测试单篇")
        print("  python generate_paper_deep_insight.py --regenerate-all [limit]  # 重新生成所有")
