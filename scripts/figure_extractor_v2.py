#!/usr/bin/env python3
"""
论文图表提取器 V2 - 提取嵌入的高分辨率图片

核心思路：
1. 从 PDF 中提取嵌入的高分辨率图片
2. 根据 Figure 标题位置确定图片编号
3. 从论文全文中提取图表说明
"""

import fitz  # PyMuPDF
from PIL import Image
import io
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class FigureExtractorV2:
    """提取嵌入的高分辨率图片"""
    
    def __init__(self, pdf_path: str, output_dir: str, arxiv_id: str):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.arxiv_id = arxiv_id.replace('.', '_')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract(self) -> List[Dict]:
        """提取所有图表"""
        
        try:
            doc = fitz.open(str(self.pdf_path))
        except Exception as e:
            print(f"  ⚠️ 无法打开 PDF: {e}")
            return []
        
        # 1. 提取所有图表说明
        captions = self._extract_captions(doc)
        print(f"  📝 找到 {len(captions)} 个图表说明")
        
        # 2. 找到所有 Figure 标题位置
        figure_positions = self._find_figure_positions(doc)
        
        # 3. 提取嵌入的高分辨率图片
        embedded_images = self._extract_embedded_images(doc)
        
        # 4. 关联图片与 Figure 编号
        figures = self._match_images_to_figures(doc, embedded_images, figure_positions, captions)
        
        doc.close()
        
        return figures
    
    def _extract_captions(self, doc) -> Dict[int, str]:
        """从论文全文中提取图表说明"""
        captions = {}
        full_text = ""
        
        for page in doc:
            full_text += page.get_text()
        
        # 匹配 "Figure X. ..."
        pattern = r'Figure\s+(\d+)\.\s*([^\n]+(?:\n(?![A-Z][a-z]*\s+\d+\.|Figure\s+\d+\.)([^\n]+))*)'
        
        for match in re.finditer(pattern, full_text):
            fig_num = int(match.group(1))
            caption = match.group(0).strip()
            caption = re.sub(r'\s+', ' ', caption)
            caption = re.sub(r'^Figure\s+\d+\.\s*', '', caption)
            if len(caption) > 10:
                captions[fig_num] = caption[:200]
        
        return captions
    
    def _find_figure_positions(self, doc) -> List[Dict]:
        """找到所有 "Figure X." 标题的位置"""
        positions = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_dict = page.get_text("dict")
            
            for block in text_dict["blocks"]:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span.get("text", "")
                        match = re.match(r'^(Figure|Fig\.)\s*(\d+)\.?', text)
                        if match:
                            fig_num = int(match.group(2))
                            positions.append({
                                'page_num': page_num,
                                'fig_num': fig_num,
                                'bbox': span['bbox'],
                                'text': text
                            })
        
        return positions
    
    def _extract_embedded_images(self, doc) -> List[Dict]:
        """提取嵌入的高分辨率图片"""
        images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)
            
            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                
                try:
                    # 提取图片
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # 检查图片尺寸
                    pil_img = Image.open(io.BytesIO(image_bytes))
                    width, height = pil_img.size
                    
                    # 过滤太小的图片（图标、符号等）
                    if width < 200 or height < 100:
                        continue
                    
                    # 过滤太大的图片（整页扫描）
                    if width > 3000 and height > 3000:
                        continue
                    
                    images.append({
                        'page_num': page_num,
                        'xref': xref,
                        'width': width,
                        'height': height,
                        'ext': image_ext,
                        'bytes': image_bytes,
                        'pil_img': pil_img
                    })
                
                except Exception as e:
                    continue
        
        return images
    
    def _match_images_to_figures(self, doc, embedded_images: List[Dict],
                                   figure_positions: List[Dict],
                                   captions: Dict[int, str]) -> List[Dict]:
        """将嵌入图片与 Figure 编号关联"""
        figures = []
        used_images = set()
        
        # 按 Figure 编号排序
        figure_positions.sort(key=lambda x: x['fig_num'])
        
        for fig_pos in figure_positions:
            fig_num = fig_pos['fig_num']
            fig_page = fig_pos['page_num']
            fig_bbox = fig_pos['bbox']
            
            # 找最近的图片
            best_image = None
            best_score = -1
            
            for img in embedded_images:
                img_id = (img['page_num'], img['xref'])
                if img_id in used_images:
                    continue
                
                score = 0
                
                # 同一页优先
                if img['page_num'] == fig_page:
                    score += 1000
                    
                    # 图片应该在 Figure 标题上方
                    # 但由于我们不知道图片在页面上的确切位置，
                    # 我们假设同一页的大图片就是对应的图表
                    if img['width'] > 300 and img['height'] > 200:
                        score += 500
                
                # 前一页也可以
                elif img['page_num'] == fig_page - 1:
                    score += 500
                    if img['width'] > 300 and img['height'] > 200:
                        score += 250
                
                # 图片大小加分（更大的图片更可能是主图表）
                size_score = min(img['width'] * img['height'] / 100000, 100)
                score += size_score
                
                if score > best_score:
                    best_score = score
                    best_image = img
            
            if best_image and best_score > 500:  # 只有足够高的分数才关联
                used_images.add((best_image['page_num'], best_image['xref']))
                
                # 保存图片
                img_filename = f"fig_{fig_num}.{best_image['ext']}"
                img_path = self.output_dir / img_filename
                
                with open(img_path, 'wb') as f:
                    f.write(best_image['bytes'])
                
                print(f"    📊 Figure {fig_num}: {best_image['width']}x{best_image['height']}")
                
                figures.append({
                    'num': fig_num,
                    'path': f"figures/{self.arxiv_id}/{img_filename}",
                    'caption': captions.get(fig_num, ''),
                    'width': best_image['width'],
                    'height': best_image['height']
                })
        
        # 按 Figure 编号排序
        figures.sort(key=lambda x: x['num'])
        
        return figures


def extract_figures(pdf_path: str, output_dir: str, arxiv_id: str) -> List[Dict]:
    """提取论文图表的主函数"""
    extractor = FigureExtractorV2(pdf_path, output_dir, arxiv_id)
    return extractor.extract()


if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "/home/sandbox/.openclaw/workspace/ai_daily/cache/pdfs/2604.21593.pdf"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/home/sandbox/.openclaw/workspace/ai_daily/docs/insights/figures/2604_21593"
    arxiv_id = sys.argv[3] if len(sys.argv) > 3 else "2604.21593"
    
    figures = extract_figures(pdf_path, output_dir, arxiv_id)
    print(f"\n提取了 {len(figures)} 张图表")
