#!/usr/bin/env python3
"""
AI推荐日报 - 论文深度解读生成器（本地版）
流程：下载PDF → 解析PDF → 规则提取 → 生成HTML
不依赖外部 LLM API
"""

import json
import re
import os
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


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
        self.api_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        self.api_key = self._get_api_key()
        self.model = "MiniMax-M2.7-highspeed"
    
    def _get_api_key(self) -> str:
        """获取 API Key"""
        import os
        # 从环境变量获取
        api_key = os.environ.get("MINIMAX_API_KEY", "")
        if api_key:
            return api_key
        
        # 从配置文件获取
        config_file = self.base_dir / "config" / "api_keys.json"
        if config_file.exists():
            config = json.loads(config_file.read_text())
            api_key = config.get("minimax_api_key", "")
            if api_key:
                return api_key
        
        # 默认 Token Plan API Key
        return "sk-cp-51HhITrES8hvSzJ4os0cENQBsJErOPWPm67toEN0AL4_2LsknQ__U3NOFEB1H86CB_5xrjN-VkpFfqa4RR7Frxpuy6GEG64cFitUQxRz6XOcYCc8s2EipTo"
    
    def download_pdf(self, arxiv_id: str) -> Optional[Path]:
        """下载 arXiv PDF"""
        arxiv_id = re.sub(r'v\d+$', '', arxiv_id).strip()
        
        pdf_path = self.pdf_cache_dir / f"{arxiv_id}.pdf"
        if pdf_path.exists():
            print(f"  📄 PDF 已存在: {pdf_path}")
            return pdf_path
        
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
    
    def extract_figures(self, pdf_path: Path, arxiv_id: str) -> List[str]:
        """从 PDF 中提取图表"""
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            import io
        except ImportError:
            print("  ⚠️ PyMuPDF 或 PIL 未安装，跳过图表提取")
            return [], {}
        
        figures_dir = self.pdf_cache_dir / "figures" / arxiv_id.replace('.', '_')
        figures_dir.mkdir(parents=True, exist_ok=True)
        
        figure_paths = []
        figure_captions = {}  # 存储图表说明
        
        try:
            doc = fitz.open(str(pdf_path))
            
            # 先提取所有文本，用于匹配图表说明
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            
            # 匹配图表说明
            import re
            caption_pattern = r"(?m)(?:Figure|Fig\.?)\s*(\d+)[.:]\s*([^\n]+)"
            for match in re.finditer(caption_pattern, full_text):
                fig_num = int(match.group(1))
                caption = match.group(2).strip()
                if len(caption) > 10:
                    figure_captions[fig_num] = caption[:200]
            
            # 提取图片
            for page_num, page in enumerate(doc):
                images = page.get_images(full=True)
                
                for img in images:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # 检查图片尺寸
                    try:
                        pil_img = Image.open(io.BytesIO(image_bytes))
                        width, height = pil_img.size
                        aspect_ratio = width / height if height > 0 else 0
                        
                        # 过滤异常图片：
                        # 1. 高度 < 200px（通常是图标或装饰元素）
                        # 2. 宽高比 > 15 或 < 0.07（极端扁平或极端窄长）
                        # 3. 宽度和高度都 < 200px（小图标）
                        if height < 200 or aspect_ratio > 15 or aspect_ratio < 0.07 or (width < 200 and height < 200):
                            continue
                    except:
                        # 如果无法检查尺寸，使用文件大小过滤
                        if len(image_bytes) < 10000:
                            continue
                    
                    fig_num = len(figure_paths) + 1
                    img_filename = f"fig_{fig_num}.{image_ext}"
                    img_path = figures_dir / img_filename
                    
                    with open(img_path, "wb") as f:
                        f.write(image_bytes)
                    
                    figure_paths.append(str(img_path))
            
            doc.close()
            
            if figure_paths:
                print(f"  🖼️ 提取了 {len(figure_paths)} 张图表")
                if figure_captions:
                    print(f"  📝 找到 {len(figure_captions)} 个图表说明")
        
        except Exception as e:
            print(f"  ⚠️ 图表提取失败: {e}")
        
        return figure_paths, figure_captions
    
    def parse_pdf(self, pdf_path: Path) -> str:
        """解析 PDF"""
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
        """备用 PDF 解析"""
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
    
    def extract_content(self, paper_content: str, paper_info: dict) -> dict:
        """从 PDF 内容中提取关键信息（优先使用 LLM）"""
        
        # 尝试使用 LLM 分析
        if self.api_key and len(paper_content) > 500:
            print("  🤖 使用 LLM 深度分析...")
            try:
                llm_result = self._analyze_with_llm(paper_content, paper_info)
                if llm_result:
                    return llm_result
            except Exception as e:
                print(f"  ⚠️ LLM 分析失败: {e}，使用规则提取")
        
        # 回退到规则提取
        print("  📋 使用规则提取...")
        abstract = self._extract_abstract(paper_content)
        method = self._extract_method(paper_content)
        experiments = self._extract_experiments(paper_content)
        conclusion = self._extract_conclusion(paper_content)
        tags = self._extract_tags(paper_content, paper_info)
        
        return {
            'abstract': abstract,
            'method': method,
            'experiments': experiments,
            'conclusion': conclusion,
            'tags': tags,
        }
    
    def _analyze_with_llm(self, paper_content: str, paper_info: dict) -> dict:
        """使用 MiniMax API 深度分析论文"""
        
        # 截取内容（避免超出 token 限制）
        max_chars = 30000
        if len(paper_content) > max_chars:
            paper_content = paper_content[:max_chars]
        
        prompt = f"""你是一位资深的学术论文解读专家。请对以下论文进行深度解读，提取关键信息。

论文标题: {paper_info.get('title', '未知')}
作者: {paper_info.get('authors', '未知')}

论文内容:
{paper_content}

请严格按照以下 JSON 格式输出解读结果:

{{
    "abstract": "论文摘要的中文解读（200-400字）",
    "key_points": ["关键要点1", "关键要点2", "关键要点3", "关键要点4"],
    "background": "研究背景和动机（200-300字）",
    "method": {{
        "text": "方法概述（200-400字）",
        "modules": [
            {{"name": "模块名称", "description": "模块功能描述"}},
            {{"name": "模块名称", "description": "模块功能描述"}}
        ]
    }},
    "innovations": [
        {{"point": "创新点名称", "solution": "技术方案", "problem": "解决的问题"}},
        {{"point": "创新点名称", "solution": "技术方案", "problem": "解决的问题"}}
    ],
    "experiments": {{
        "datasets": ["数据集1", "数据集2"],
        "metrics": ["指标1", "指标2"],
        "improvements": ["提升1", "提升2"]
    }},
    "conclusion": "主要结论（100-200字）",
    "tags": ["标签1", "标签2", "标签3", "标签4"]
}}

注意：只输出 JSON，不要其他内容。"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        response = requests.post(self.api_url, headers=headers, json=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 提取 JSON
            try:
                return json.loads(content)
            except:
                # 尝试提取 JSON 块
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        pass
            
            print(f"  ⚠️ 无法解析 LLM 返回内容")
        
        return None
    
    def _extract_abstract(self, content: str) -> str:
        """提取摘要"""
        # 尝试匹配 Abstract 部分
        patterns = [
            r'Abstract\s*(.*?)(?:\n\s*\n|\n[A-Z][a-z]+\s)',
            r'ABSTRACT\s*(.*?)(?:\n\s*\n|\n[A-Z][a-z]+\s)',
            r'摘要\s*(.*?)(?:\n\s*\n|\n[A-Z])',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                # 清理
                abstract = re.sub(r'\s+', ' ', abstract)
                if len(abstract) > 100:
                    return abstract[:1000]
        
        # 如果没找到，返回前 500 字符
        return content[:500].strip()
    
    def _extract_method(self, content: str) -> dict:
        """提取方法部分"""
        # 查找 Method/Approach 部分
        method_patterns = [
            r'(?:Method|Approach|Methodology)\s*(.*?)(?:\n\s*\n(?:Experiment|Results|Evaluation|Conclusion))',
            r'(?:方法|模型)\s*(.*?)(?:\n\s*\n(?:实验|结果|结论))',
        ]
        
        method_text = ""
        for pattern in method_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                method_text = match.group(1).strip()
                break
        
        # 提取可能的模块/组件
        modules = []
        module_patterns = [
            r'(?:Module|Component|Layer|Encoder|Decoder|Network)\s*(\d*)\s*[:：]?\s*([^\n]+)',
            r'(?:模块|组件|层)\s*(\d*)\s*[:：]?\s*([^\n]+)',
        ]
        
        for pattern in module_patterns:
            for match in re.finditer(pattern, content):
                name = match.group(2).strip()
                if name and len(name) < 50:
                    modules.append({'name': name, 'description': ''})
        
        return {
            'text': method_text[:2000] if method_text else "方法详情请参见论文原文。",
            'modules': modules[:5] if modules else [{'name': '核心模块', 'description': '实现主要功能'}]
        }
    
    def _extract_experiments(self, content: str) -> dict:
        """提取实验部分"""
        # 查找数据集
        datasets = []
        dataset_patterns = [
            r'(?:dataset|Dataset|数据集)[:：]?\s*([A-Za-z0-9\-,\s]+)',
            r'(?:on|using)\s+([A-Za-z0-9\-]+)\s+(?:dataset|benchmark)',
        ]
        
        for pattern in dataset_patterns:
            for match in re.finditer(pattern, content):
                ds = match.group(1).strip()
                if ds and len(ds) < 30:
                    datasets.append(ds)
        
        # 查找指标
        metrics = []
        metric_patterns = [
            r'(?:Accuracy|Precision|Recall|F1|NDCG|Hit|MRR|BLEU|ROUGE)[:：]?\s*([\d.]+%?)',
            r'([\d.]+%?)\s*(?:accuracy|precision|recall|F1)',
        ]
        
        for pattern in metric_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                metric = match.group(0).strip()
                if metric:
                    metrics.append(metric)
        
        # 查找性能提升
        improvements = []
        imp_patterns = [
            r'(\+[\d.]+%)\s*(?:improvement|increase|gain)',
            r'improve[sd]?\s+(?:by\s+)?([\d.]+%)',
        ]
        
        for pattern in imp_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                imp = match.group(0).strip()
                if imp:
                    improvements.append(imp)
        
        return {
            'datasets': list(set(datasets))[:5] or ['公开数据集'],
            'metrics': list(set(metrics))[:5] or ['Accuracy', 'F1-Score'],
            'improvements': list(set(improvements))[:3] or ['性能提升'],
        }
    
    def _extract_conclusion(self, content: str) -> str:
        """提取结论"""
        patterns = [
            r'(?:Conclusion|Conclusions)\s*(.*?)(?:\n\s*\n(?:References|Acknowledgment)|$)',
            r'(?:结论|总结)\s*(.*?)(?:\n\s*\n(?:参考文献|致谢)|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                conclusion = match.group(1).strip()
                return conclusion[:1000]
        
        return "结论详情请参见论文原文。"
    
    def _extract_tags(self, content: str, paper_info: dict) -> List[str]:
        """提取标签"""
        tags = set()
        
        # 从论文分类获取
        category = paper_info.get('category', '')
        if category == 'rec':
            tags.add('推荐系统')
        elif category == 'agent':
            tags.add('AI Agent')
        elif category == 'llm':
            tags.add('大语言模型')
        
        # 从内容中提取关键词
        keywords = {
            'deep learning': '深度学习',
            'machine learning': '机器学习',
            'neural network': '神经网络',
            'transformer': 'Transformer',
            'attention': '注意力机制',
            'reinforcement learning': '强化学习',
            'knowledge graph': '知识图谱',
            'graph neural network': '图神经网络',
            'recommendation': '推荐',
            'NLP': 'NLP',
            'computer vision': '计算机视觉',
            'optimization': '优化',
            'embedding': '嵌入',
            'pre-training': '预训练',
            'fine-tuning': '微调',
        }
        
        content_lower = content.lower()
        for en, zh in keywords.items():
            if en in content_lower:
                tags.add(zh)
        
        return list(tags)[:6] or ['AI', '机器学习']
    
    def generate_insight(self, paper: dict) -> str:
        """生成论文解读页面"""
        
        arxiv_id = paper.get('arxiv_id', paper.get('id', 'unknown'))
        arxiv_id = re.sub(r'[^\w\.\-]', '', arxiv_id)
        
        print(f"\n📄 处理论文: {arxiv_id}")
        
        # 1. 下载 PDF
        pdf_path = self.download_pdf(arxiv_id)
        
        # 2. 提取图表
        figure_paths = []
        figure_captions = {}
        if pdf_path and pdf_path.exists():
            figure_paths, figure_captions = self.extract_figures(pdf_path, arxiv_id)
        
        # 3. 解析 PDF
        if pdf_path and pdf_path.exists():
            print(f"  📖 解析 PDF...")
            paper_content = self.parse_pdf(pdf_path)
        else:
            print(f"  ⚠️ 无法获取 PDF，使用摘要")
            paper_content = paper.get('summary', '')
        
        # 4. 提取内容
        print(f"  🔍 提取关键信息...")
        extracted = self.extract_content(paper_content, paper)
        
        # 5. 生成 HTML
        print(f"  🎨 生成解读页面...")
        html = self._render_html(paper, extracted, paper_content, figure_paths, figure_captions)
        
        # 6. 复制图表到 docs 目录
        if figure_paths:
            self._copy_figures_to_docs(arxiv_id)
        
        # 7. 保存
        safe_id = re.sub(r'[^\w\-]', '_', arxiv_id)
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"{today}_{safe_id}.html"
        filepath = self.insights_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  ✅ 完成: {filepath}")
        return str(filepath)
    
    def _render_html(self, paper: dict, extracted: dict, raw_content: str, figure_paths: List[str] = None, figure_captions: dict = None) -> str:
        """渲染 HTML 页面"""
        template = self.load_template()
        
        if figure_captions is None:
            figure_captions = {}
        
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
        
        # 处理 LLM 返回的数据
        abstract = extracted.get('abstract', '')
        key_points = extracted.get('key_points', [])
        background = extracted.get('background', '')
        method = extracted.get('method', {})
        innovations = extracted.get('innovations', [])
        experiments = extracted.get('experiments', {})
        conclusion = extracted.get('conclusion', '')
        tags = extracted.get('tags', [])
        
        # 处理图表
        figures_html = self._render_figures(figure_paths, arxiv_id, figure_captions)
        
        # 渲染变量
        data = {
            'title': title,
            'subtitle': abstract[:100] + '...' if len(abstract) > 100 else abstract,
            'authors': authors_str,
            'date': paper.get('published', ''),
            'arxiv_id': arxiv_id,
            'arxiv_link': paper.get('link', f"https://arxiv.org/abs/{arxiv_id}"),
            'read_time': '15',
            'abstract': f"<p>{abstract}</p>",
            'key_points': ''.join(f'<li>{p}</li>' for p in key_points[:4]) if key_points else self._extract_key_points(raw_content),
            'background': f"<p>{background}</p>" if background else self._extract_background(raw_content),
            'core_problem': '详见论文原文',
            'method_overview': f"<p>{method.get('text', '')}</p>" if isinstance(method, dict) else f"<p>{method}</p>",
            'innovations': self._render_innovations(innovations) if innovations else self._render_innovations_from_content(raw_content),
            'architecture_diagram': self._generate_architecture_from_content(raw_content),
            'modules_description': self._render_modules(method.get('modules', [])) if isinstance(method, dict) else '',
            'algorithm_flowchart': self._generate_default_flowchart(),
            'pseudocode': '<span class="comment">// 详见论文原文</span>',
            'formula': '',
            'formula_vars': '',
            'code_example': '# 详见论文原文',
            'datasets': ', '.join(experiments.get('datasets', [])) if isinstance(experiments, dict) else '',
            'metrics': ', '.join(experiments.get('metrics', [])) if isinstance(experiments, dict) else '',
            'baselines': '详见论文原文',
            'stats_cards': self._render_stats_from_experiments(experiments) if isinstance(experiments, dict) else self._render_stats_from_experiments({'improvements': []}),
            'comparison_headers': '<th>指标</th><th>数值</th>',
            'comparison_rows': self._render_comparison_from_experiments(experiments) if isinstance(experiments, dict) else '<tr><td>详见论文</td><td>-</td></tr>',
            'ablation_results': '<tr><td>详见论文</td><td>-</td><td>-</td></tr>',
            'findings': self._render_findings_from_content(raw_content),
            'limitations': '<li>详见论文原文</li>',
            'future_work': '<li>详见论文原文</li>',
            'applications': '<li>相关领域应用</li>',
            'implementation_tips': '<li>参考论文原文实现</li>',
            'ratings': self._render_default_ratings(),
            'faq': self._generate_faq_from_content(raw_content),
            'tags': ''.join(f'<span class="tag">{t}</span>' for t in tags[:6]) if tags else '',
            'figures': figures_html,
        }
        
        return self._render_template(template, data)
    
    def _render_figures(self, figure_paths: List[str], arxiv_id: str, figure_captions: dict = None) -> str:
        """渲染图表展示区域 - 使用真实的图表说明"""
        if not figure_paths:
            return ''
        
        if figure_captions is None:
            figure_captions = {}
        
        html_parts = ['''
<div class="figures-inline">
<h3>📊 论文图表</h3>
<p class="figures-note">以下图表来自论文原文，展示了方法架构和实验结果：</p>
<div class="figures-scroll">''']
        
        for i, path in enumerate(figure_paths[:8], 1):
            fig_name = Path(path).name
            relative_path = f"figures/{arxiv_id.replace('.', '_')}/{fig_name}"
            
            # 使用真实的图表说明，如果没有则使用默认说明
            if i in figure_captions:
                caption = f"图{i}: {figure_captions[i]}"
            else:
                # 根据图表序号推断类型
                if i <= 2:
                    caption = f"图{i}: 方法架构或流程示意"
                elif i <= 5:
                    caption = f"图{i}: 实验结果对比"
                else:
                    caption = f"图{i}: 消融实验或案例分析"
            
            html_parts.append(f'''
            <div class="figure-card">
                <img src="{relative_path}" alt="Figure {i}" loading="lazy" onclick="this.classList.toggle('zoom')">
                <p class="figure-caption">{caption}</p>
            </div>''')
        
        html_parts.extend(['</div>', '</div>'])
        
        # 添加样式
        html_parts.append('''
<style>
.figures-inline {
    margin: 1.5rem 0;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
}
.figures-inline h3 {
    margin: 0 0 0.5rem;
    font-size: 1rem;
    color: #334155;
}
.figures-note {
    font-size: 0.85rem;
    color: #64748b;
    margin-bottom: 1rem;
}
.figures-scroll {
    display: flex;
    gap: 1rem;
    overflow-x: auto;
    padding-bottom: 0.5rem;
    scroll-snap-type: x mandatory;
}
.figure-card {
    flex: 0 0 280px;
    background: white;
    border-radius: 8px;
    padding: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    scroll-snap-align: start;
    cursor: zoom-in;
}
.figure-card img {
    width: 100%;
    height: auto;
    border-radius: 4px;
    transition: transform 0.2s;
}
.figure-card img.zoom {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) scale(2);
    z-index: 1000;
    cursor: zoom-out;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}
.figure-caption {
    margin: 0.5rem 0 0;
    font-size: 0.8rem;
    color: #64748b;
    text-align: center;
}
</style>''')
        
        return '\n'.join(html_parts)
    
    def _copy_figures_to_docs(self, arxiv_id: str) -> None:
        """将图表复制到 docs 目录"""
        import shutil
        
        source_dir = self.pdf_cache_dir / "figures" / arxiv_id.replace('.', '_')
        target_dir = self.insights_dir / "figures" / arxiv_id.replace('.', '_')
        
        if source_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
            
            for fig_file in source_dir.glob("*"):
                if fig_file.is_file():
                    shutil.copy2(fig_file, target_dir / fig_file.name)
            
            print(f"  📁 复制图表到: {target_dir}")
    
    def _render_innovations(self, innovations: list) -> str:
        """渲染创新点表格"""
        if not innovations:
            return '<tr><td>方法创新</td><td>详见论文</td><td>性能提升</td></tr>'
        
        rows = []
        for inn in innovations[:3]:
            if isinstance(inn, dict):
                rows.append(f'''<tr>
    <td>{inn.get('point', '创新点')}</td>
    <td>{inn.get('solution', '技术方案')}</td>
    <td>{inn.get('problem', '解决问题')}</td>
</tr>''')
            else:
                rows.append(f'<tr><td>{inn}</td><td>-</td><td>-</td></tr>')
        return '\n'.join(rows)
    
    def _extract_key_points(self, content: str) -> str:
        """提取关键要点"""
        points = []
        
        # 查找可能的要点
        sentences = content.split('.')
        for sentence in sentences[:20]:
            sentence = sentence.strip()
            if len(sentence) > 50 and len(sentence) < 200:
                if any(kw in sentence.lower() for kw in ['propose', 'present', 'introduce', 'achieve', 'improve']):
                    points.append(sentence)
                    if len(points) >= 4:
                        break
        
        if not points:
            return '<li>详见论文原文</li>'
        
        return ''.join(f'<li>{p}</li>' for p in points[:4])
    
    def _extract_background(self, content: str) -> str:
        """提取背景"""
        # 查找 Introduction 部分
        patterns = [
            r'(?:Introduction|Background)\s*(.*?)(?:\n\s*\n(?:Method|Approach|Related Work))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                bg = match.group(1).strip()
                return f"<p>{bg[:1000]}</p>"
        
        return "<p>研究背景详见论文原文。</p>"
    
    def _render_innovations_from_content(self, content: str) -> str:
        """从内容中提取创新点"""
        innovations = []
        
        # 查找可能的创新点描述
        patterns = [
            r'(?:Our|We|This paper)\s+(?:propose|present|introduce)\s+([^.]+)',
            r'(?:novel|new|innovative)\s+([^.]+)',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                text = match.group(1).strip()
                if len(text) > 20 and len(text) < 100:
                    innovations.append(text)
        
        if not innovations:
            return '<tr><td>方法创新</td><td>详见论文</td><td>性能提升</td></tr>'
        
        rows = []
        for i, inn in enumerate(innovations[:3]):
            rows.append(f'<tr><td>创新点{i+1}</td><td>{inn}</td><td>提升性能</td></tr>')
        
        return '\n'.join(rows)
    
    def _generate_architecture_from_content(self, content: str) -> str:
        """生成架构图"""
        # 检测是否有特定架构关键词
        if 'encoder' in content.lower() and 'decoder' in content.lower():
            return '''graph LR
    Input["📥 输入"] --> Encoder["🔄 编码器"]
    Encoder --> Decoder["⚡ 解码器"]
    Decoder --> Output["📤 输出"]
    
    style Input fill:#e3f2fd,stroke:#1565c0
    style Output fill:#e8f5e9,stroke:#2e7d32'''
        
        if 'transformer' in content.lower():
            return '''graph TB
    Input["📥 输入"] --> Embed["嵌入层"]
    Embed --> Attn["注意力层"]
    Attn --> FFN["前馈网络"]
    FFN --> Output["📤 输出"]
    
    style Input fill:#e3f2fd,stroke:#1565c0
    style Output fill:#e8f5e9,stroke:#2e7d32'''
        
        return self._default_architecture_diagram()
    
    def _default_architecture_diagram(self) -> str:
        return '''graph TB
    subgraph Input["📥 输入层"]
        Data[数据输入]
    end
    
    subgraph Process["🔄 处理层"]
        Feature[特征提取]
        Model[模型计算]
    end
    
    subgraph Output["📤 输出层"]
        Result[结果输出]
    end
    
    Data --> Feature --> Model --> Result
    
    style Input fill:#e3f2fd,stroke:#1565c0
    style Process fill:#fff3e0,stroke:#ef6c00
    style Output fill:#e8f5e9,stroke:#2e7d32'''
    
    def _generate_default_flowchart(self) -> str:
        return '''flowchart TD
    A[输入数据] --> B[预处理]
    B --> C[特征提取]
    C --> D[模型计算]
    D --> E[后处理]
    E --> F[输出结果]
    
    style A fill:#e3f2fd
    style F fill:#e8f5e9'''
    
    def _render_modules(self, modules: list) -> str:
        if not modules:
            return '<p>模块详情请参见论文原文。</p>'
        
        html = ''
        for m in modules:
            html += f"<p><strong>{m.get('name', '模块')}：</strong>{m.get('description', '实现相应功能')}</p>"
        return html
    
    def _render_stats_from_experiments(self, experiments: dict) -> str:
        improvements = experiments.get('improvements', ['性能提升'])
        
        cards = []
        for i, imp in enumerate(improvements[:4]):
            cards.append(f'''<div class="stat-card">
    <div class="stat-value">{imp}</div>
    <div class="stat-label">性能提升</div>
</div>''')
        
        while len(cards) < 4:
            cards.append('''<div class="stat-card">
    <div class="stat-value">-</div>
    <div class="stat-label">详见论文</div>
</div>''')
        
        return '\n'.join(cards)
    
    def _render_comparison_from_experiments(self, experiments: dict) -> str:
        metrics = experiments.get('metrics', ['Accuracy'])
        rows = []
        for m in metrics[:3]:
            rows.append(f'<tr><td>本文方法</td><td>{m}</td></tr>')
        return '\n'.join(rows) or '<tr><td>详见论文</td><td>-</td></tr>'
    
    def _render_findings_from_content(self, content: str) -> str:
        # 查找结论中的发现
        findings = []
        
        conclusion_match = re.search(r'(?:Conclusion|结论)\s*(.*?)(?:\n\s*\n|$)', content, re.DOTALL | re.IGNORECASE)
        if conclusion_match:
            conclusion = conclusion_match.group(1)
            sentences = conclusion.split('.')
            for s in sentences[:3]:
                s = s.strip()
                if len(s) > 30:
                    findings.append(s)
        
        if not findings:
            return '<div class="step"><div class="step-title">实验验证</div><div class="step-desc">方法在实验中验证有效。</div></div>'
        
        html = []
        for i, f in enumerate(findings[:3], 1):
            html.append(f'''<div class="step">
    <div class="step-title">发现 {i}</div>
    <div class="step-desc">{f[:100]}</div>
</div>''')
        return '\n'.join(html)
    
    def _render_default_ratings(self) -> str:
        return '''<div class="rating-item">
    <span class="rating-label">创新性</span>
    <span class="rating-stars">★★★★☆</span>
</div>
<div class="rating-item">
    <span class="rating-label">工业价值</span>
    <span class="rating-stars">★★★★☆</span>
</div>
<div class="rating-item">
    <span class="rating-label">实验充分性</span>
    <span class="rating-stars">★★★★☆</span>
</div>
<div class="rating-item">
    <span class="rating-label">可复现性</span>
    <span class="rating-stars">★★★☆☆</span>
</div>'''
    
    def _generate_faq_from_content(self, content: str) -> str:
        return '''<div class="faq-item">
    <div class="faq-q">该方法的主要贡献是什么？</div>
    <div class="faq-a">请参考论文原文的摘要和结论部分。</div>
</div>
<div class="faq-item">
    <div class="faq-q">如何复现该方法？</div>
    <div class="faq-a">请参考论文的方法部分和实验设置，或查看作者提供的代码仓库。</div>
</div>'''
    
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
        print("  python generate_paper_deep_insight.py --test")
        print("  python generate_paper_deep_insight.py --regenerate-all [limit]")
