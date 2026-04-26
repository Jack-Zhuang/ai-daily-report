#!/usr/bin/env python3
"""
论文图表提取器 - 基于 PDF 图片对象位置精确截取

核心思路：
1. 从 PDF 中提取所有图片对象及其精确位置（bbox）
2. 找到 "Figure X." 标题文字的位置
3. 将图片对象与 Figure 标题关联
4. 直接使用图片对象的 bbox 进行精确裁剪
"""

import fitz  # PyMuPDF
from PIL import Image
import io
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class FigureExtractor:
    """基于 PDF 图片对象的图表提取器"""
    
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
        
        # 2. 提取所有图片对象及其位置
        all_images = self._extract_image_objects(doc)
        
        # 3. 找到 Figure 标题位置
        figure_positions = self._find_figure_positions(doc)
        
        # 4. 关联图片与 Figure 标题
        figures = self._match_images_to_figures(doc, all_images, figure_positions, captions)
        
        # 5. 保存图片
        saved_figures = self._save_figures(doc, figures)
        
        doc.close()
        
        return saved_figures
    
    def _extract_captions(self, doc) -> Dict[int, str]:
        """从论文全文中提取图表说明"""
        captions = {}
        full_text = ""
        
        for page in doc:
            full_text += page.get_text()
        
        # 匹配 "Figure X. ..." 直到下一个 Figure 或章节标题
        pattern = r'Figure\s+(\d+)\.\s*([^\n]+(?:\n(?![A-Z][a-z]*\s+\d+\.|Figure\s+\d+\.)([^\n]+))*)'
        
        for match in re.finditer(pattern, full_text):
            fig_num = int(match.group(1))
            caption = match.group(0).strip()
            caption = re.sub(r'\s+', ' ', caption)
            caption = re.sub(r'^Figure\s+\d+\.\s*', '', caption)
            if len(caption) > 10:
                captions[fig_num] = caption[:200]
        
        return captions
    
    def _extract_image_objects(self, doc) -> List[Dict]:
        """提取 PDF 中所有图片对象及其位置"""
        all_images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 获取页面上的所有图片信息
            image_list = page.get_images(full=True)
            
            # 获取页面的所有块（包括图片块）
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block.get("type") == 1:  # 图片块
                    bbox = block.get("bbox")
                    if not bbox:
                        continue
                    
                    # 过滤太小的图片（可能是图标、符号等）
                    width = bbox[2] - bbox[0]
                    height = bbox[3] - bbox[1]
                    
                    if width < 100 or height < 50:
                        continue
                    
                    # 过滤太大的图片（可能是整页背景）
                    page_rect = page.rect
                    if width > page_rect.width * 0.95 and height > page_rect.height * 0.9:
                        continue
                    
                    all_images.append({
                        'page_num': page_num,
                        'bbox': bbox,
                        'width': width,
                        'height': height,
                        'block': block
                    })
        
        return all_images
    
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
    
    def _match_images_to_figures(self, doc, all_images: List[Dict], 
                                  figure_positions: List[Dict], 
                                  captions: Dict[int, str]) -> List[Dict]:
        """将图片对象与 Figure 标题关联"""
        figures = []
        used_images = set()
        
        for fig_pos in figure_positions:
            fig_num = fig_pos['fig_num']
            fig_page = fig_pos['page_num']
            fig_bbox = fig_pos['bbox']
            
            # 在同一页或前一页找最近的图片
            best_image = None
            best_distance = float('inf')
            
            for img in all_images:
                img_id = (img['page_num'], img['bbox'])
                if img_id in used_images:
                    continue
                
                # 图片必须在 Figure 标题上方
                if img['page_num'] == fig_page:
                    # 同一页：图片底部应该在 Figure 标题顶部附近
                    if img['bbox'][3] <= fig_bbox[1] + 20:  # 图片底部 <= Figure 顶部 + 20px
                        # 计算水平距离
                        img_center_x = (img['bbox'][0] + img['bbox'][2]) / 2
                        fig_center_x = (fig_bbox[0] + fig_bbox[2]) / 2
                        distance = abs(img_center_x - fig_center_x)
                        
                        if distance < best_distance:
                            best_distance = distance
                            best_image = img
                elif img['page_num'] == fig_page - 1:
                    # 前一页：图片应该在页面底部
                    prev_page = doc[img['page_num']]
                    if img['bbox'][3] > prev_page.rect.height * 0.5:
                        distance = 1000 + abs(img['page_num'] - fig_page) * 100
                        if distance < best_distance:
                            best_distance = distance
                            best_image = img
            
            if best_image:
                used_images.add((best_image['page_num'], best_image['bbox']))
                figures.append({
                    'fig_num': fig_num,
                    'page_num': best_image['page_num'],
                    'bbox': best_image['bbox'],
                    'caption': captions.get(fig_num, ''),
                    'width': best_image['width'],
                    'height': best_image['height']
                })
        
        # 按 Figure 编号排序
        figures.sort(key=lambda x: x['fig_num'])
        
        return figures
    
    def _save_figures(self, doc, figures: List[Dict]) -> List[Dict]:
        """保存图表为图片文件"""
        saved = []
        
        # 高分辨率渲染
        scale = 2.0
        mat = fitz.Matrix(scale, scale)
        
        for fig in figures:
            page_num = fig['page_num']
            bbox = fig['bbox']
            
            page = doc[page_num]
            
            # 渲染页面
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            pil_img = Image.open(io.BytesIO(img_data))
            
            # 裁剪图表（加上一点边距）
            margin = 10
            crop_box = (
                int((bbox[0] - margin) * scale),
                int((bbox[1] - margin) * scale),
                int((bbox[2] + margin) * scale),
                int((bbox[3] + margin) * scale)
            )
            
            # 确保裁剪区域在图片范围内
            crop_box = (
                max(0, crop_box[0]),
                max(0, crop_box[1]),
                min(pil_img.width, crop_box[2]),
                min(pil_img.height, crop_box[3])
            )
            
            fig_img = pil_img.crop(crop_box)
            
            # 保存
            img_filename = f"fig_{fig['fig_num']}.png"
            img_path = self.output_dir / img_filename
            fig_img.save(img_path, 'PNG')
            
            print(f"    📊 Figure {fig['fig_num']}: {int(fig['width'])}x{int(fig['height'])}")
            
            saved.append({
                'num': fig['fig_num'],
                'path': f"figures/{self.arxiv_id}/{img_filename}",
                'caption': fig['caption']
            })
        
        return saved


def extract_figures(pdf_path: str, output_dir: str, arxiv_id: str) -> List[Dict]:
    """提取论文图表的主函数"""
    extractor = FigureExtractor(pdf_path, output_dir, arxiv_id)
    return extractor.extract()


if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "/home/sandbox/.openclaw/workspace/ai_daily/cache/pdfs/2604.21593.pdf"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/home/sandbox/.openclaw/workspace/ai_daily/docs/insights/figures/2604_21593"
    arxiv_id = sys.argv[3] if len(sys.argv) > 3 else "2604.21593"
    
    figures = extract_figures(pdf_path, output_dir, arxiv_id)
    print(f"\n提取了 {len(figures)} 张图表")
