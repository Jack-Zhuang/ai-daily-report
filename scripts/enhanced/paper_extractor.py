#!/usr/bin/env python3
"""
AI推荐日报 - 论文内容提取器
从 arXiv PDF 提取完整内容，包括文本、图片、表格、公式
"""

import os
import re
import json
import requests
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Figure:
    """图片信息"""
    index: int
    caption: str
    image_url: Optional[str] = None
    local_path: Optional[str] = None


@dataclass
class Table:
    """表格信息"""
    index: int
    caption: str
    content: str  # Markdown 格式


@dataclass
class Section:
    """章节信息"""
    title: str
    content: str
    level: int


@dataclass
class PaperContent:
    """论文完整内容"""
    arxiv_id: str
    title: str
    abstract: str
    sections: List[Section]
    figures: List[Figure]
    tables: List[Table]
    equations: List[str]
    references: List[str]
    full_text: str
    extracted_at: str


class PaperExtractor:
    """论文内容提取器"""
    
    def __init__(self, cache_dir: str = None):
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent / "paper_cache"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def download_pdf(self, arxiv_id: str) -> Optional[str]:
        """下载 arXiv PDF"""
        # 清理 arxiv_id (可能包含版本号)
        clean_id = arxiv_id.replace("v1", "").replace("v2", "").replace("v3", "")
        
        pdf_url = f"https://arxiv.org/pdf/{clean_id}.pdf"
        pdf_path = self.cache_dir / f"{arxiv_id}.pdf"
        
        if pdf_path.exists():
            print(f"  📄 使用缓存: {pdf_path}")
            return str(pdf_path)
        
        print(f"  📥 下载 PDF: {pdf_url}")
        
        try:
            response = requests.get(pdf_url, timeout=60, stream=True)
            if response.status_code == 200:
                with open(pdf_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"  ✅ 下载完成: {pdf_path}")
                return str(pdf_path)
            else:
                print(f"  ❌ 下载失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"  ❌ 下载出错: {e}")
            return None
    
    def extract_with_pymupdf(self, pdf_path: str) -> Dict:
        """使用 PyMuPDF 提取内容"""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            print("  ⚠️ PyMuPDF 未安装，尝试安装...")
            os.system("pip install pymupdf -q")
            import fitz
        
        doc = fitz.open(pdf_path)
        
        result = {
            "full_text": "",
            "pages": [],
            "images": [],
            "tables": []
        }
        
        for page_num, page in enumerate(doc):
            # 提取文本
            text = page.get_text()
            result["full_text"] += text + "\n"
            result["pages"].append({
                "page_num": page_num + 1,
                "text": text
            })
            
            # 提取图片
            images = page.get_images()
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # 保存图片
                img_filename = f"figure_{page_num}_{img_index}.{image_ext}"
                img_path = self.cache_dir / img_filename
                with open(img_path, 'wb') as f:
                    f.write(image_bytes)
                
                result["images"].append({
                    "page": page_num + 1,
                    "index": img_index,
                    "path": str(img_path),
                    "ext": image_ext
                })
        
        doc.close()
        return result
    
    def parse_sections(self, full_text: str) -> List[Section]:
        """解析论文章节"""
        sections = []
        
        # 常见章节标题模式
        section_patterns = [
            r"(?m)^(?:Abstract|ABSTRACT)\s*\n([\s\S]*?)(?=Introduction|INTRODUCTION|1\.|$)",
            r"(?m)^(?:1\.?\s*)?(?:Introduction|INTRODUCTION)\s*\n([\s\S]*?)(?=2\.|Related Work|RELATED WORK|$)",
            r"(?m)^(?:2\.?\s*)?(?:Related Work|RELATED WORK|Background|BACKGROUND)\s*\n([\s\S]*?)(?=3\.|Method|METHOD|$)",
            r"(?m)^(?:3\.?\s*)?(?:Method|METHOD|Approach|APPROACH|Our Method)\s*\n([\s\S]*?)(?=4\.|Experiment|EXPERIMENT|$)",
            r"(?m)^(?:4\.?\s*)?(?:Experiment|EXPERIMENT|Experiments|EXPERIMENTS|Evaluation)\s*\n([\s\S]*?)(?=5\.|Conclusion|CONCLUSION|$)",
            r"(?m)^(?:5\.?\s*)?(?:Conclusion|CONCLUSION|Discussion|DISCUSSION)\s*\n([\s\S]*?)(?=References|REFERENCES|$)",
        ]
        
        # 简化版：按数字编号分割
        section_regex = r"(?m)^(\d+\.?\s+[A-Z][^\n]+)\s*\n([\s\S]*?)(?=^\d+\.?\s+[A-Z]|References|REFERENCES|$)"
        
        matches = re.findall(section_regex, full_text)
        for title, content in matches:
            title = title.strip()
            content = content.strip()
            if len(content) > 100:  # 过滤太短的章节
                sections.append(Section(
                    title=title,
                    content=content[:3000],  # 限制长度
                    level=1
                ))
        
        return sections
    
    def parse_figures(self, full_text: str, images: List[Dict]) -> List[Figure]:
        """解析图片说明"""
        figures = []
        
        # 匹配 Figure X: caption 或 Fig. X: caption
        figure_pattern = r"(?m)(?:Figure|Fig\.?)\s*(\d+)[.:]\s*([^\n]+)"
        matches = re.findall(figure_pattern, full_text)
        
        for idx, (fig_num, caption) in enumerate(matches):
            fig_num = int(fig_num)
            caption = caption.strip()
            
            # 尝试匹配图片文件
            image_url = None
            for img in images:
                if img.get("index") == idx:
                    image_url = img.get("path")
                    break
            
            figures.append(Figure(
                index=fig_num,
                caption=caption[:200],  # 限制长度
                image_url=image_url
            ))
        
        return figures[:10]  # 最多 10 张图
    
    def parse_tables(self, full_text: str) -> List[Table]:
        """解析表格说明"""
        tables = []
        
        # 匹配 Table X: caption
        table_pattern = r"(?m)(?:Table|Tab\.?)\s*(\d+)[.:]\s*([^\n]+)"
        matches = re.findall(table_pattern, full_text)
        
        for table_num, caption in matches:
            tables.append(Table(
                index=int(table_num),
                caption=caption.strip()[:200],
                content=""  # 表格内容需要更复杂的解析
            ))
        
        return tables[:5]  # 最多 5 个表格
    
    def parse_equations(self, full_text: str) -> List[str]:
        """解析公式（增强版）"""
        equations = []
        
        # 模式1: 编号公式 (1), (2), etc.
        eq_pattern = r"\((\d+)\)\s*([^\n]{10,150})"
        matches = re.findall(eq_pattern, full_text)
        
        for eq_num, eq_content in matches:
            # 过滤非公式内容
            if any(c in eq_content for c in ['=', '+', '-', '*', '/', '\\', '∑', '∏', '∫', 'α', 'β', 'γ', 'θ', 'λ']):
                equations.append(eq_content.strip())
        
        # 模式2: LaTeX 风格公式 $...$ 或 $$...$$
        latex_pattern = r"\$\$?([^\$]+)\$\$?"
        latex_matches = re.findall(latex_pattern, full_text)
        equations.extend([m.strip() for m in latex_matches if len(m) > 5])
        
        # 模式3: 常见数学符号开头的行
        math_pattern = r"(?m)^([∑∏∫∂∇αβγδθλμπσφψω∈∉⊂⊃∪∩∀∃].*[^\.\?\!])$"
        math_matches = re.findall(math_pattern, full_text)
        equations.extend([m.strip() for m in math_matches if len(m) > 5])
        
        return equations[:15]  # 最多 15 个公式
    
    def parse_references(self, full_text: str) -> List[str]:
        """解析参考文献"""
        references = []
        
        # 找到 References 部分
        ref_start = full_text.lower().find("references")
        if ref_start == -1:
            return references
        
        ref_text = full_text[ref_start:]
        
        # 匹配 [1] Author, Title, ...
        ref_pattern = r"\[(\d+)\]\s*([^\[]+)"
        matches = re.findall(ref_pattern, ref_text)
        
        for ref_num, ref_content in matches:
            ref_content = ref_content.strip()
            if len(ref_content) > 20:
                references.append(ref_content[:200])
        
        return references[:20]  # 最多 20 条参考文献
    
    def extract_abstract(self, full_text: str) -> str:
        """提取摘要"""
        # 尝试多种模式
        patterns = [
            r"(?m)(?:Abstract|ABSTRACT)\s*\n([\s\S]*?)(?=Introduction|INTRODUCTION|1\.|Keywords)",
            r"(?m)(?:Abstract|ABSTRACT)[:\s]+([^\n]+(?:\n(?![A-Z][a-z]+)[^\n]+)*)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, full_text)
            if match:
                abstract = match.group(1).strip()
                # 清理多余空白
                abstract = re.sub(r'\s+', ' ', abstract)
                return abstract[:1500]  # 限制长度
        
        return ""
    
    def extract(self, arxiv_id: str, title: str = "") -> PaperContent:
        """提取论文完整内容"""
        print(f"\n{'='*50}")
        print(f"📄 提取论文内容: {arxiv_id}")
        print(f"{'='*50}\n")
        
        # 下载 PDF
        pdf_path = self.download_pdf(arxiv_id)
        if not pdf_path:
            raise Exception(f"无法下载 PDF: {arxiv_id}")
        
        # 提取内容
        print("  📝 解析 PDF 内容...")
        raw_content = self.extract_with_pymupdf(pdf_path)
        full_text = raw_content["full_text"]
        
        # 解析各部分
        print("  📊 解析章节结构...")
        sections = self.parse_sections(full_text)
        
        print("  🖼️ 解析图片说明...")
        figures = self.parse_figures(full_text, raw_content["images"])
        
        print("  📋 解析表格...")
        tables = self.parse_tables(full_text)
        
        print("  🔢 解析公式...")
        equations = self.parse_equations(full_text)
        
        print("  📚 解析参考文献...")
        references = self.parse_references(full_text)
        
        print("  📝 提取摘要...")
        abstract = self.extract_abstract(full_text)
        
        # 构建结果
        content = PaperContent(
            arxiv_id=arxiv_id,
            title=title,
            abstract=abstract,
            sections=sections,
            figures=figures,
            tables=tables,
            equations=equations,
            references=references,
            full_text=full_text[:50000],  # 限制总长度
            extracted_at=datetime.now().isoformat()
        )
        
        print(f"\n  ✅ 提取完成:")
        print(f"     - 章节: {len(sections)}")
        print(f"     - 图片: {len(figures)}")
        print(f"     - 表格: {len(tables)}")
        print(f"     - 公式: {len(equations)}")
        print(f"     - 参考文献: {len(references)}")
        
        return content
    
    def save(self, content: PaperContent, output_path: str = None):
        """保存提取结果"""
        if output_path is None:
            output_path = self.cache_dir / f"{content.arxiv_id}_content.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(content), f, ensure_ascii=False, indent=2)
        
        print(f"  💾 已保存: {output_path}")
        return output_path
    
    def load(self, arxiv_id: str) -> Optional[PaperContent]:
        """加载已提取的内容"""
        cache_path = self.cache_dir / f"{arxiv_id}_content.json"
        
        if not cache_path.exists():
            return None
        
        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return PaperContent(**data)


def main():
    """测试入口"""
    extractor = PaperExtractor()
    
    # 测试提取
    arxiv_id = "2604.14878"  # GenRec 论文
    content = extractor.extract(arxiv_id, "GenRec: A Preference-Oriented Generative Framework")
    
    # 保存
    extractor.save(content)
    
    # 打印摘要
    print(f"\n{'='*50}")
    print(f"📄 论文摘要:")
    print(f"{'='*50}")
    print(content.abstract[:500])


if __name__ == "__main__":
    main()
