#!/usr/bin/env python3
"""
论文图表提取器 V3 - 混合方案

核心思路：
1. 优先提取嵌入的高分辨率图片
2. 对于没有大嵌入图片的 Figure，使用页面渲染裁剪
3. 结合两种方法，确保所有图表都能完整提取
"""

import fitz  # PyMuPDF
from PIL import Image
import io
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class FigureExtractorV3:
    """混合图表提取器"""
    
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
        
        # 4. 关联图片与 Figure 编号（混合方案）
        figures = self._match_figures_hybrid(doc, embedded_images, figure_positions, captions)
        
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
    
    def _match_figures_hybrid(self, doc, embedded_images: List[Dict],
                               figure_positions: List[Dict],
                               captions: Dict[int, str]) -> List[Dict]:
        """混合方案：优先使用嵌入图片，否则使用页面渲染"""
        figures = []
        used_images = set()
        
        # 按 Figure 编号排序
        figure_positions.sort(key=lambda x: x['fig_num'])
        
        for fig_pos in figure_positions:
            fig_num = fig_pos['fig_num']
            fig_page = fig_pos['page_num']
            fig_bbox = fig_pos['bbox']
            
            # 尝试找嵌入的大图片
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
                    # 大图片加分
                    if img['width'] > 500 and img['height'] > 300:
                        score += 500
                    elif img['width'] > 300 and img['height'] > 200:
                        score += 300
                    
                    # 横向图片加分（图表通常是横向的）
                    if img['width'] > img['height'] * 1.2:
                        score += 200
                
                # 前一页也可以
                elif img['page_num'] == fig_page - 1:
                    score += 500
                    if img['width'] > 500 and img['height'] > 300:
                        score += 250
                
                # 图片大小加分
                size_score = min(img['width'] * img['height'] / 100000, 100)
                score += size_score
                
                if score > best_score:
                    best_score = score
                    best_image = img
            
            # 如果找到高质量嵌入图片，使用它
            if best_image and best_score > 1500:  # 只有非常大的横向图片才使用嵌入图片
                used_images.add((best_image['page_num'], best_image['xref']))
                
                # 保存图片
                img_filename = f"fig_{fig_num}.{best_image['ext']}"
                img_path = self.output_dir / img_filename
                
                with open(img_path, 'wb') as f:
                    f.write(best_image['bytes'])
                
                print(f"    📊 Figure {fig_num}: {best_image['width']}x{best_image['height']} (嵌入图片)")
                
                figures.append({
                    'num': fig_num,
                    'path': f"figures/{self.arxiv_id}/{img_filename}",
                    'caption': captions.get(fig_num, ''),
                    'width': best_image['width'],
                    'height': best_image['height']
                })
            
            # 否则，使用页面渲染裁剪
            else:
                rendered_fig = self._render_figure(doc, fig_pos)
                if rendered_fig:
                    figures.append(rendered_fig)
        
        # 按 Figure 编号排序
        figures.sort(key=lambda x: x['num'])
        
        return figures
    
    def _render_figure(self, doc, fig_pos: Dict) -> Optional[Dict]:
        """渲染页面并裁剪图表"""
        fig_num = fig_pos['fig_num']
        fig_page = fig_pos['page_num']
        fig_bbox = fig_pos['bbox']
        
        page = doc[fig_page]
        page_rect = page.rect
        
        # 高分辨率渲染
        scale = 2.0
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        pil_img = Image.open(io.BytesIO(img_data))
        
        # 估算图表区域
        # Figure 标题通常在图表下方，所以向上裁剪
        fig_y = fig_bbox[1] * scale  # Figure 标题的 Y 坐标
        
        # 向上找图表的顶部（通常是页面顶部或上一个元素）
        # 这里使用启发式方法：向上裁剪 30-50% 的页面高度
        crop_height = int(page_rect.height * scale * 0.4)
        
        # 裁剪区域
        crop_box = (
            0,  # 左边距
            max(0, int(fig_y - crop_height)),  # 顶部
            int(page_rect.width * scale),  # 右边距
            int(fig_y + 30 * scale)  # 底部（包含 Figure 标题）
        )
        
        # 裁剪
        fig_img = pil_img.crop(crop_box)
        
        # 保存
        img_filename = f"fig_{fig_num}.png"
        img_path = self.output_dir / img_filename
        fig_img.save(img_path, 'PNG')
        
        print(f"    📊 Figure {fig_num}: {fig_img.size[0]}x{fig_img.size[1]} (页面渲染)")
        
        return {
            'num': fig_num,
            'path': f"figures/{self.arxiv_id}/{img_filename}",
            'caption': '',
            'width': fig_img.size[0],
            'height': fig_img.size[1]
        }


def extract_figures(pdf_path: str, output_dir: str, arxiv_id: str) -> List[Dict]:
    """提取论文图表的主函数"""
    extractor = FigureExtractorV3(pdf_path, output_dir, arxiv_id)
    return extractor.extract()


if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "/home/sandbox/.openclaw/workspace/ai_daily/cache/pdfs/2604.21593.pdf"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/home/sandbox/.openclaw/workspace/ai_daily/docs/insights/figures/2604_21593"
    arxiv_id = sys.argv[3] if len(sys.argv) > 3 else "2604.21593"
    
    figures = extract_figures(pdf_path, output_dir, arxiv_id)
    print(f"\n提取了 {len(figures)} 张图表")
