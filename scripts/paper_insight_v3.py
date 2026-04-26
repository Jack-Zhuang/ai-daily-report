#!/usr/bin/env python3
"""
论文解读生成器 V3 - 多轮深度分析，打造精品文章

核心理念：
1. 多轮对话：一次搞不清楚就多问几次
2. 搜索补充：不懂的概念主动搜索
3. 精品意识：每篇文章都值得花时间深入理解

流程：
1. 快速浏览 → 了解论文大意
2. 深度提问 → 理解核心创新
3. 实验分析 → 提取关键数据
4. 批判思考 → 局限性与影响
5. 整合输出 → 生成高质量解读
"""

import json
import re
import os
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import fitz
from PIL import Image
import io
import time


class PaperInsightV3:
    """论文解读生成器 V3 - 多轮深度分析"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.insights_dir = self.base_dir / "docs" / "insights"
        self.insights_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_cache_dir = self.base_dir / "cache" / "pdfs"
        self.pdf_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # API 配置
        self.api_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        self.api_key = self._get_api_key()
        self.model = "MiniMax-M2.7-highspeed"
        
        # 对话历史（用于多轮对话）
        self.conversation_history = []
    
    def _get_api_key(self) -> str:
        api_key = os.environ.get("MINIMAX_API_KEY", "")
        if api_key:
            return api_key
        return "sk-cp-51HhITrES8hvSzJ4os0cENQBsJErOPWPm67toEN0AL4_2LsknQ__U3NOFEB1H86CB_5xrjN-VkpFfqa4RR7Frxpuy6GEG64cFitUQxRz6XOcYCc8s2EipTo"
    
    def generate(self, paper: dict) -> str:
        """生成论文解读页面 - 主入口"""
        
        arxiv_id = paper.get('arxiv_id', paper.get('id', 'unknown'))
        arxiv_id = re.sub(r'[^\w\.\-]', '', arxiv_id)
        
        print(f"\n{'='*60}")
        print(f"📄 深度解读论文: {arxiv_id}")
        print(f"{'='*60}")
        
        # 1. 下载/获取 PDF
        pdf_path = self._get_pdf(arxiv_id)
        
        # 2. 解析 PDF 内容
        print("\n📖 解析 PDF...")
        pdf_content = self._parse_pdf(pdf_path) if pdf_path else ""
        
        # 3. 提取图表
        print("🖼️ 提取图表...")
        figures = self._extract_figures(pdf_path, arxiv_id) if pdf_path else []
        
        # 4. 多轮深度分析
        print("\n🧠 多轮深度分析...")
        analysis = self._deep_analysis(pdf_content, paper)
        
        # 5. 构建页面
        print("\n🎨 构建页面...")
        html = self._build_page(paper, analysis, figures, arxiv_id)
        
        # 6. 保存
        safe_id = re.sub(r'[^\w\-]', '_', arxiv_id)
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"{today}_{safe_id}.html"
        filepath = self.insights_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ 完成: {filepath}")
        return str(filepath)
    
    def _get_pdf(self, arxiv_id: str) -> Optional[Path]:
        """下载或获取 PDF"""
        pdf_path = self.pdf_cache_dir / f"{arxiv_id}.pdf"
        
        if pdf_path.exists():
            print(f"  📄 PDF 已存在: {pdf_path}")
            return pdf_path
        
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                print(f"  📥 下载 PDF: {pdf_path}")
                return pdf_path
        except Exception as e:
            print(f"  ⚠️ 下载失败: {e}")
        
        return None
    
    def _parse_pdf(self, pdf_path: Path) -> str:
        """解析 PDF 提取文本"""
        if not pdf_path or not pdf_path.exists():
            return ""
        
        try:
            doc = fitz.open(str(pdf_path))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"  ⚠️ 解析失败: {e}")
            return ""
    
    def _extract_figures(self, pdf_path: Path, arxiv_id: str) -> List[Dict]:
        """提取图表 - 使用嵌入的高分辨率图片"""
        if not pdf_path or not pdf_path.exists():
            return []
        
        figures = []
        figures_dir = self.insights_dir / "figures" / arxiv_id.replace('.', '_')
        figures_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 导入新的图表提取器
            import sys
            scripts_dir = self.base_dir / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            
            from figure_extractor_v2 import extract_figures as extract_figures_v2
            
            figures = extract_figures_v2(str(pdf_path), str(figures_dir), arxiv_id)
            
            if figures:
                print(f"    提取了 {len(figures)} 张图表")
        
        except ImportError as e:
            # 回退到旧方法
            print(f"  ⚠️ 使用旧版图表提取: {e}")
            return self._extract_figures_legacy(pdf_path, arxiv_id)
        
        except Exception as e:
            print(f"  ⚠️ 图表提取失败: {e}")
        
        return figures
    
    def _extract_figures_legacy(self, pdf_path: Path, arxiv_id: str) -> List[Dict]:
        """旧版图表提取方法（回退用）"""
        if not pdf_path or not pdf_path.exists():
            return []
        
        figures = []
        figures_dir = self.insights_dir / "figures" / arxiv_id.replace('.', '_')
        figures_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            doc = fitz.open(str(pdf_path))
            
            # 提取图表说明
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            
            captions = {}
            caption_pattern = r'(Figure\s+(\d+)\.\s*[^\n]+(?:\n(?![A-Z][a-z]*\s+\d+\.)([^\n]+))*)'
            for match in re.finditer(caption_pattern, full_text):
                fig_num = int(match.group(2))
                caption = match.group(1).strip()
                caption = re.sub(r'\s+', ' ', caption)
                caption = re.sub(r'^Figure\s+\d+\.\s*', '', caption)
                if len(caption) > 10:
                    captions[fig_num] = caption[:200]
            
            # 渲染并裁剪图表
            scale = 2.0
            mat = fitz.Matrix(scale, scale)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_rect = page.rect
                
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                pil_img = Image.open(io.BytesIO(img_data))
                
                text_dict = page.get_text("dict")
                
                for block in text_dict["blocks"]:
                    if "lines" not in block:
                        continue
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text_content = span.get("text", "")
                            match = re.match(r'^(Figure|Fig\.)\s*(\d+)\.', text_content)
                            if match:
                                fig_num = int(match.group(2))
                                bbox = span["bbox"]
                                
                                fig_height = page_rect.height * 0.30
                                fig_top = max(page_rect.height * 0.08, bbox[1] - fig_height)
                                fig_bottom = bbox[1] - 5
                                
                                if bbox[0] > page_rect.width * 0.4:
                                    fig_left = page_rect.width * 0.5
                                    fig_right = page_rect.width - 20
                                else:
                                    fig_left = 20
                                    fig_right = page_rect.width * 0.5 - 10
                                
                                crop_box = (
                                    int(fig_left * scale),
                                    int(fig_top * scale),
                                    int(fig_right * scale),
                                    int(fig_bottom * scale)
                                )
                                
                                fig_img = pil_img.crop(crop_box)
                                
                                if fig_img.width < 200 or fig_img.height < 100:
                                    continue
                                
                                img_filename = f"fig_{fig_num}.png"
                                img_path = figures_dir / img_filename
                                fig_img.save(img_path, 'PNG')
                                
                                figures.append({
                                    'num': fig_num,
                                    'path': f"figures/{arxiv_id.replace('.', '_')}/{img_filename}",
                                    'caption': captions.get(fig_num, '')
                                })
            
            doc.close()
            
            if figures:
                print(f"    提取了 {len(figures)} 张图表")
        
        except Exception as e:
            print(f"  ⚠️ 图表提取失败: {e}")
        
        return figures
    
    def _call_llm(self, prompt: str, temperature: float = 0.3) -> str:
        """调用 LLM"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": 4000
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        except Exception as e:
            print(f"    ⚠️ LLM 调用失败: {e}")
        
        return ""
    
    def _deep_analysis(self, content: str, paper: dict) -> Dict:
        """多轮深度分析"""
        
        if not content:
            content = paper.get('summary', '')
        
        # 截取内容
        max_chars = 35000
        if len(content) > max_chars:
            content = content[:max_chars]
        
        title = paper.get('title', '未知')
        
        # ========== 第一轮：快速浏览 ==========
        print("  📚 第一轮：快速浏览...")
        round1_prompt = f"""你是一位资深的学术论文解读专家。请快速阅读以下论文，回答：

论文标题: {title}

论文内容:
{content}

请回答以下问题（每个问题用一段话回答）：

1. 这篇论文的核心贡献是什么？（一句话概括）
2. 论文解决了什么问题？为什么这个问题重要？
3. 作者提出了什么方法？核心思路是什么？
4. 实验结果如何？有哪些关键数据？
5. 这篇论文的创新点在哪里？

请用中文回答，简洁明了。"""

        round1_response = self._call_llm(round1_prompt)
        print(f"    ✓ 第一轮完成 ({len(round1_response)} 字)")
        
        # ========== 第二轮：深度理解方法 ==========
        print("  🔬 第二轮：深度理解方法...")
        round2_prompt = f"""基于对论文的初步理解：

{round1_response}

现在请深入分析论文的方法部分，回答：

1. 方法的具体技术细节是什么？请用通俗的语言解释
2. 方法中有哪些关键的设计决策？为什么这样设计？
3. 与现有方法相比，这个方法有什么独特之处？
4. 方法的实现复杂度如何？是否容易复现？

论文原文供参考：
{content[:15000]}

请用中文回答，注重技术细节和可理解性。"""

        round2_response = self._call_llm(round2_prompt, temperature=0.4)
        print(f"    ✓ 第二轮完成 ({len(round2_response)} 字)")
        
        # ========== 第三轮：实验数据分析 ==========
        print("  📊 第三轮：实验数据分析...")
        round3_prompt = f"""请深入分析论文的实验部分，提取关键数据：

论文原文：
{content}

请提取以下信息（如果论文中有）：

1. 使用了哪些数据集？每个数据集的作用是什么？
2. 主要实验结果是什么？请列出具体的数值（如准确率、F1分数等）
3. 与基线方法相比，提升了多少？请列出具体对比数据
4. 消融实验的结果如何？哪些组件最重要？
5. 是否有失败的案例或局限性？

请用中文回答，必须包含具体数值。如果某项信息论文中没有，请说明"论文中未提及"。"""

        round3_response = self._call_llm(round3_prompt, temperature=0.2)
        print(f"    ✓ 第三轮完成 ({len(round3_response)} 字)")
        
        # ========== 第四轮：批判性思考 ==========
        print("  🤔 第四轮：批判性思考...")
        round4_prompt = f"""基于前面的分析：

第一轮理解：
{round1_response}

第二轮方法分析：
{round2_response}

第三轮实验分析：
{round3_response}

现在请进行批判性思考：

1. 这篇论文的局限性是什么？（方法层面、实验层面、应用层面）
2. 论文的结论是否站得住脚？实验是否充分？
3. 这个方法在实际应用中可能遇到什么问题？
4. 这篇论文对领域的影响可能是什么？
5. 未来可以如何改进这个工作？

请用中文回答，要有批判性思维，不要只是一味赞扬。"""

        round4_response = self._call_llm(round4_prompt, temperature=0.5)
        print(f"    ✓ 第四轮完成 ({len(round4_response)} 字)")
        
        # ========== 第五轮：整合输出 ==========
        print("  ✍️ 第五轮：整合输出...")
        round5_prompt = f"""现在请整合前面的分析，生成一份高质量的论文解读。

前面的分析：
- 快速浏览：{round1_response}
- 方法分析：{round2_response}
- 实验分析：{round3_response}
- 批判思考：{round4_response}

请按照以下 JSON 格式输出最终的论文解读：

{{
    "abstract": "论文核心贡献的精炼解读（200-300字，必须包含具体方法和关键数值）",
    "key_insights": ["洞察1", "洞察2", "洞察3"],
    "background": "研究背景和动机（150-250字，说明为什么这个问题重要）",
    "method": "方法详解（250-400字，用通俗语言解释技术细节）",
    "innovations": [
        {{"point": "创新点名称", "description": "具体描述（50-100字）"}},
        {{"point": "创新点名称", "description": "具体描述（50-100字）"}}
    ],
    "experiments": {{
        "datasets": ["数据集名称及用途"],
        "results": ["具体实验结果（必须包含数值）"],
        "comparisons": ["与基线方法的对比结果"]
    }},
    "findings": ["主要发现1", "主要发现2", "主要发现3"],
    "limitations": "研究的局限性（100-200字）",
    "future_work": "未来研究方向（100-200字）",
    "applications": "潜在应用场景（100-200字）",
    "impact": "对领域的影响（50-100字）",
    "tags": ["标签1", "标签2", "标签3", "标签4", "标签5"]
}}

重要提示：
1. 所有内容必须基于前面的分析，不要编造
2. 实验结果必须包含具体数值
3. 局限性要有批判性思考
4. 只输出 JSON，不要其他内容"""

        round5_response = self._call_llm(round5_prompt, temperature=0.3)
        print(f"    ✓ 第五轮完成 ({len(round5_response)} 字)")
        
        # 解析 JSON
        try:
            json_match = re.search(r'\{[\s\S]*\}', round5_response)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"    ⚠️ JSON 解析失败: {e}")
        
        return {}
    
    def _build_page(self, paper: dict, analysis: Dict, figures: List, arxiv_id: str) -> str:
        """构建页面"""
        
        title = paper.get('cn_title', paper.get('title', '未知标题'))
        arxiv_link = f"https://arxiv.org/abs/{arxiv_id}"
        
        sections = []
        
        # 1. 摘要速览
        abstract = analysis.get('abstract', '')
        if abstract:
            key_insights = analysis.get('key_insights', [])
            sections.append(self._section_abstract(abstract, key_insights))
        
        # 2. 研究背景
        background = analysis.get('background', '')
        if background:
            sections.append(self._section_background(background))
        
        # 3. 方法详解
        method = analysis.get('method', '')
        innovations = analysis.get('innovations', [])
        if method or innovations:
            sections.append(self._section_method(method, innovations))
        
        # 4. 图表展示
        if figures:
            sections.append(self._section_figures(figures))
        
        # 5. 实验结果
        experiments = analysis.get('experiments', {})
        if experiments and (experiments.get('results') or experiments.get('datasets')):
            sections.append(self._section_experiments(experiments))
        
        # 6. 主要发现
        findings = analysis.get('findings', [])
        if findings:
            sections.append(self._section_findings(findings))
        
        # 7. 讨论与展望
        limitations = analysis.get('limitations', '')
        future_work = analysis.get('future_work', '')
        applications = analysis.get('applications', '')
        impact = analysis.get('impact', '')
        if limitations or future_work or applications or impact:
            sections.append(self._section_discussion(limitations, future_work, applications, impact))
        
        tags = analysis.get('tags', [])
        
        return self._render_html(title, arxiv_id, arxiv_link, sections, tags)
    
    def _section_abstract(self, abstract: str, key_insights: List[str]) -> str:
        insights_html = ''
        if key_insights:
            insights_html = '<ul class="key-points">' + ''.join(f'<li>{i}</li>' for i in key_insights[:4]) + '</ul>'
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-icon yellow">📋</div>
                <h2 class="section-title">摘要速览</h2>
            </div>
            <div class="content">
                <p>{abstract}</p>
                {insights_html}
            </div>
        </div>'''
    
    def _section_background(self, background: str) -> str:
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-icon blue">📖</div>
                <h2 class="section-title">研究背景</h2>
            </div>
            <div class="content">
                <p>{background}</p>
            </div>
        </div>'''
    
    def _section_method(self, method: str, innovations: List[Dict]) -> str:
        method_html = f'<p>{method}</p>' if method else ''
        
        innovations_html = ''
        if innovations:
            rows = []
            for inn in innovations[:3]:
                point = inn.get('point', '')
                desc = inn.get('description', '')
                if point and desc:
                    rows.append(f'<tr><td><strong>{point}</strong></td><td>{desc}</td></tr>')
            if rows:
                innovations_html = f'''
                <h3>核心创新</h3>
                <table class="innovation-table">
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>'''
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-icon green">⚙️</div>
                <h2 class="section-title">方法详解</h2>
            </div>
            <div class="content">
                {method_html}
                {innovations_html}
            </div>
        </div>'''
    
    def _section_figures(self, figures: List[Dict]) -> str:
        figures_html = ''
        for fig in figures[:6]:
            caption = fig.get('caption', '')
            caption_html = f'<p class="figure-caption">图{fig["num"]}: {caption}</p>' if caption else ''
            figures_html += f'''
            <div class="figure-card">
                <img src="{fig['path']}" alt="Figure {fig['num']}" loading="lazy">
                {caption_html}
            </div>'''
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-icon purple">📊</div>
                <h2 class="section-title">论文图表</h2>
            </div>
            <div class="figures-grid">
                {figures_html}
            </div>
        </div>'''
    
    def _section_experiments(self, experiments: Dict) -> str:
        datasets = experiments.get('datasets', [])
        results = experiments.get('results', [])
        comparisons = experiments.get('comparisons', [])
        
        datasets_html = ''
        if datasets:
            datasets_html = f'<p><strong>数据集：</strong>{", ".join(datasets)}</p>'
        
        results_html = ''
        if results:
            cards = []
            for r in results[:4]:
                cards.append(f'''
                <div class="stat-card">
                    <div class="stat-value">{r}</div>
                </div>''')
            results_html = f'''
            <h3>主要结果</h3>
            <div class="stats-grid">
                {''.join(cards)}
            </div>'''
        
        comparisons_html = ''
        if comparisons:
            rows = []
            for c in comparisons[:3]:
                rows.append(f'<tr><td>{c}</td></tr>')
            comparisons_html = f'''
            <h3>方法对比</h3>
            <table class="comparison-table">
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>'''
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-icon pink">📈</div>
                <h2 class="section-title">实验结果</h2>
            </div>
            <div class="content">
                {datasets_html}
            </div>
            {results_html}
            {comparisons_html}
        </div>'''
    
    def _section_findings(self, findings: List[str]) -> str:
        findings_html = ''
        for i, f in enumerate(findings[:3], 1):
            findings_html += f'''
            <div class="finding-item">
                <div class="finding-num">{i}</div>
                <div class="finding-text">{f}</div>
            </div>'''
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-icon orange">🏆</div>
                <h2 class="section-title">主要发现</h2>
            </div>
            <div class="findings-list">
                {findings_html}
            </div>
        </div>'''
    
    def _section_discussion(self, limitations: str, future_work: str, applications: str, impact: str) -> str:
        items = []
        if limitations:
            items.append(f'<div class="discussion-item"><h4>⚠️ 局限性</h4><p>{limitations}</p></div>')
        if future_work:
            items.append(f'<div class="discussion-item"><h4>🔮 未来方向</h4><p>{future_work}</p></div>')
        if applications:
            items.append(f'<div class="discussion-item"><h4>💡 应用场景</h4><p>{applications}</p></div>')
        if impact:
            items.append(f'<div class="discussion-item"><h4>🌍 领域影响</h4><p>{impact}</p></div>')
        
        return f'''
        <div class="section">
            <div class="section-header">
                <div class="section-icon cyan">💬</div>
                <h2 class="section-title">讨论与展望</h2>
            </div>
            <div class="discussion-content">
                {''.join(items)}
            </div>
        </div>'''
    
    def _render_html(self, title: str, arxiv_id: str, arxiv_link: str, sections: List[str], tags: List[str]) -> str:
        tags_html = ''.join(f'<span class="tag">{t}</span>' for t in tags[:6]) if tags else ''
        
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{title} - 论文解读</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        :root {{
            --color-text: #1a1a2e;
            --color-text-secondary: #4a4a6a;
            --color-text-muted: #8888a0;
            --color-card: #ffffff;
            --color-bg: #f5f7fa;
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.8;
        }}
        
        .nav {{
            position: fixed; top: 0; left: 0; right: 0;
            background: rgba(255,255,255,0.98);
            backdrop-filter: blur(12px);
            padding: 12px 20px;
            z-index: 100;
            display: flex; align-items: center; justify-content: space-between;
            border-bottom: 1px solid rgba(0,0,0,0.08);
        }}
        .nav-back {{
            width: 36px; height: 36px;
            background: rgba(102,126,234,0.1);
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            color: #667eea; text-decoration: none; font-size: 16px;
        }}
        .nav-title {{ font-size: 15px; font-weight: 600; }}
        .nav-link {{
            padding: 8px 16px;
            background: var(--gradient-primary);
            color: white;
            border-radius: 10px;
            font-size: 13px; font-weight: 600;
            text-decoration: none;
        }}
        
        .hero {{
            background: var(--gradient-primary);
            padding: 80px 20px 40px;
            color: white;
        }}
        .hero-badge {{
            display: inline-flex; align-items: center; gap: 6px;
            background: rgba(255,255,255,0.2);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px; font-weight: 600;
            margin-bottom: 16px;
        }}
        .hero-title {{
            font-size: 22px; font-weight: 700;
            line-height: 1.4; margin-bottom: 12px;
        }}
        
        .main {{
            padding: 20px 20px 100px;
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .section {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }}
        .section-header {{
            display: flex; align-items: center; gap: 12px;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 2px solid rgba(102,126,234,0.1);
        }}
        .section-icon {{
            width: 40px; height: 40px;
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 18px;
        }}
        .section-icon.yellow {{ background: linear-gradient(135deg, #fbbf24, #f59e0b); }}
        .section-icon.blue {{ background: linear-gradient(135deg, #60a5fa, #3b82f6); }}
        .section-icon.green {{ background: linear-gradient(135deg, #34d399, #10b981); }}
        .section-icon.purple {{ background: linear-gradient(135deg, #a78bfa, #8b5cf6); }}
        .section-icon.pink {{ background: linear-gradient(135deg, #f472b6, #ec4899); }}
        .section-icon.orange {{ background: linear-gradient(135deg, #fb923c, #f97316); }}
        .section-icon.cyan {{ background: linear-gradient(135deg, #22d3ee, #06b6d4); }}
        .section-title {{ font-size: 18px; font-weight: 700; }}
        
        .content {{ font-size: 15px; color: var(--color-text-secondary); }}
        .content p {{ margin-bottom: 16px; }}
        .content h3 {{ font-size: 16px; font-weight: 600; color: var(--color-text); margin: 24px 0 12px; }}
        
        .key-points {{ margin: 16px 0; padding-left: 24px; }}
        .key-points li {{ margin-bottom: 8px; color: var(--color-text); }}
        
        .innovation-table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        .innovation-table td {{ padding: 12px; border-bottom: 1px solid rgba(0,0,0,0.06); vertical-align: top; }}
        .innovation-table td:first-child {{ width: 30%; color: #667eea; }}
        
        .figures-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }}
        .figure-card {{
            background: #f8fafc;
            border-radius: 12px;
            padding: 12px;
        }}
        .figure-card img {{
            width: 100%;
            height: auto;
            border-radius: 8px;
            background: white;
        }}
        .figure-caption {{
            margin-top: 8px;
            font-size: 13px;
            color: var(--color-text-muted);
            text-align: center;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin: 16px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, rgba(102,126,234,0.08), rgba(118,75,162,0.08));
            border-radius: 12px;
            padding: 16px;
        }}
        .stat-value {{
            font-size: 14px;
            font-weight: 600;
            color: var(--color-text);
            line-height: 1.5;
        }}
        
        .comparison-table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        .comparison-table td {{ padding: 12px; border-bottom: 1px solid rgba(0,0,0,0.06); }}
        
        .findings-list {{ display: flex; flex-direction: column; gap: 16px; }}
        .finding-item {{ display: flex; gap: 16px; align-items: flex-start; }}
        .finding-num {{
            width: 32px; height: 32px;
            background: var(--gradient-primary);
            color: white;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 14px;
            flex-shrink: 0;
        }}
        .finding-text {{ font-size: 15px; color: var(--color-text-secondary); }}
        
        .discussion-content {{ display: flex; flex-direction: column; gap: 20px; }}
        .discussion-item h4 {{
            font-size: 14px;
            color: #667eea;
            margin-bottom: 8px;
        }}
        .discussion-item p {{ font-size: 14px; color: var(--color-text-secondary); }}
        
        .tags {{
            display: flex; flex-wrap: wrap; gap: 8px;
            padding: 16px 0;
        }}
        .tag {{
            background: rgba(102,126,234,0.1);
            color: #667eea;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px; font-weight: 600;
        }}
        
        .bottom-bar {{
            position: fixed; bottom: 0; left: 0; right: 0;
            background: rgba(255,255,255,0.98);
            backdrop-filter: blur(12px);
            padding: 12px 20px;
            border-top: 1px solid rgba(0,0,0,0.08);
            display: flex; gap: 12px;
        }}
        .btn {{
            flex: 1;
            height: 48px;
            border: none; border-radius: 12px;
            font-size: 15px; font-weight: 600;
            display: flex; align-items: center; justify-content: center; gap: 8px;
            cursor: pointer; text-decoration: none;
        }}
        .btn-primary {{ background: var(--gradient-primary); color: white; }}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="javascript:history.back()" class="nav-back"><i class="fas fa-arrow-left"></i></a>
        <span class="nav-title">论文解读</span>
        <a href="{arxiv_link}" class="nav-link" target="_blank"><i class="fas fa-external-link-alt"></i> 原文</a>
    </nav>
    
    <div class="hero">
        <div class="hero-badge">
            <i class="fas fa-file-alt"></i>
            <span>arXiv:{arxiv_id}</span>
        </div>
        <h1 class="hero-title">{title}</h1>
    </div>
    
    <main class="main">
        {''.join(sections)}
        
        {f'<div class="tags">{tags_html}</div>' if tags_html else ''}
    </main>
    
    <div class="bottom-bar">
        <a href="{arxiv_link}" class="btn btn-primary" target="_blank">
            <i class="fas fa-book"></i> 阅读原论文
        </a>
    </div>
</body>
</html>'''


def generate_insight(paper: dict) -> str:
    """生成论文解读页面"""
    generator = PaperInsightV3()
    return generator.generate(paper)


if __name__ == "__main__":
    import sys
    arxiv_id = sys.argv[1] if len(sys.argv) > 1 else "2604.21593"
    generate_insight({'arxiv_id': arxiv_id, 'title': ''})
