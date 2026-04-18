#!/usr/bin/env python3
"""
AI推荐日报 - 增强版封面图生成脚本
支持：1. 从原文提取图片 2. PDF截图 3. AI生成
"""

import json
import urllib.request
import re
import os
from pathlib import Path
from datetime import datetime

class EnhancedCoverGenerator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.covers_dir = self.base_dir / "covers"
        self.covers_dir.mkdir(exist_ok=True)
        self.cache_dir = self.base_dir / "cache" / "pdfs"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_image_from_article(self, url: str) -> str:
        """从文章中提取第一张图片"""
        if not url or 'arxiv.org' in url:
            return ""
        
        try:
            print(f"    提取图片: {url[:50]}...")
            
            # 下载页面
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # 查找图片
            # 微信公众号
            if 'mp.weixin.qq.com' in url:
                match = re.search(r'data-src="(https://mmbiz\.qpic\.cn[^"]+)"', html)
                if match:
                    return match.group(1)
            
            # 通用 img 标签
            matches = re.findall(r'<img[^>]+src=["\']([^"\']+\.(jpg|jpeg|png|webp))["\']', html, re.I)
            for img_url, ext in matches:
                if img_url.startswith('http') and 'avatar' not in img_url.lower():
                    return img_url
            
            return ""
        except Exception as e:
            print(f"    提取失败: {e}")
            return ""
    
    def download_pdf_screenshot(self, arxiv_id: str) -> str:
        """下载 PDF 并截图（需要 pdf2image）"""
        if not arxiv_id:
            return ""
        
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        pdf_path = self.cache_dir / f"{arxiv_id}.pdf"
        img_path = self.covers_dir / f"paper_{arxiv_id}.jpg"
        
        if img_path.exists():
            return f"covers/paper_{arxiv_id}.jpg"
        
        try:
            # 下载 PDF
            if not pdf_path.exists():
                print(f"    下载 PDF: {arxiv_id}...")
                urllib.request.urlretrieve(pdf_url, pdf_path)
            
            # 尝试截图
            try:
                from pdf2image import convert_from_path
                
                images = convert_from_path(pdf_path, first_page=1, last_page=1)
                if images:
                    # 裁剪为封面比例
                    img = images[0]
                    width, height = img.size
                    new_height = int(width * 0.7)  # 约 1.43:1
                    img = img.crop((0, 0, width, min(new_height, height)))
                    img.save(img_path, 'JPEG', quality=85)
                    print(f"    ✓ PDF截图成功")
                    return f"covers/paper_{arxiv_id}.jpg"
            except ImportError:
                print(f"    ⚠️ pdf2image 未安装，跳过 PDF 截图")
                return ""
        
        except Exception as e:
            print(f"    PDF处理失败: {e}")
            return ""
    
    def generate_ai_cover(self, title: str, category: str, index: int) -> str:
        """使用 AI 生成封面"""
        output_name = f"{category}_{index}.jpg"
        output_path = self.covers_dir / output_name
        
        if output_path.exists():
            return f"covers/{output_name}"
        
        # 调用 Seedream
        skill_path = Path.home() / ".openclaw" / "workspace" / "skills" / "seedream-image_gen"
        script_path = skill_path / "scripts" / "generate_seedream.py"
        
        if not script_path.exists():
            print(f"    ⚠️ Seedream 脚本不存在")
            return ""
        
        # 生成提示词
        prompts = {
            'rec': f"推荐系统技术图示，数据流和算法可视化，科技蓝色调，简洁现代风格",
            'agent': f"AI智能体架构图，多智能体协作网络，科技紫色调，未来感设计",
            'llm': f"大语言模型原理图，神经网络结构，科技绿色调，学术风格",
            'paper': f"学术论文配图，研究方法示意图，学术风格，专业简洁",
            'article': f"科技新闻配图，AI技术概念，渐变背景，现代简约风格",
            'github': f"开源项目展示，代码界面，GitHub风格，深色主题"
        }
        
        prompt = prompts.get(category, prompts['article'])
        
        import subprocess
        cmd = ["python3", str(script_path), "--prompt", prompt, "--max-images", "1"]
        
        try:
            print(f"    AI生成封面...")
            subprocess.run(cmd, capture_output=True, timeout=120)
            
            # 查找生成的图片
            gen_dir = Path.home() / ".openclaw" / "workspace" / "generated-images"
            if gen_dir.exists():
                images = sorted(gen_dir.glob("*.jpg"), key=os.path.getmtime, reverse=True)
                if images:
                    import shutil
                    shutil.copy(images[0], output_path)
                    print(f"    ✓ AI生成成功")
                    return f"covers/{output_name}"
        except Exception as e:
            print(f"    AI生成失败: {e}")
        
        return ""
    
    def generate_cover(self, item: dict, index: int) -> str:
        """为单个项目生成封面"""
        # 如果已有封面，直接返回
        if item.get('cover_image'):
            return item['cover_image']
        
        title = item.get('cn_title', item.get('title', ''))
        link = item.get('link', '')
        arxiv_id = item.get('id', item.get('arxiv_id', ''))
        category = item.get('category', item.get('pick_type', 'article'))
        
        print(f"  生成封面: {title[:30]}...")
        
        # 策略1: 从文章提取图片
        if link and 'arxiv.org' not in link:
            img_url = self.extract_image_from_article(link)
            if img_url:
                # 下载图片
                try:
                    output_name = f"{category}_{index}.jpg"
                    output_path = self.covers_dir / output_name
                    urllib.request.urlretrieve(img_url, output_path)
                    print(f"    ✓ 从原文提取成功")
                    return f"covers/{output_name}"
                except:
                    pass
        
        # 策略2: PDF 截图
        if arxiv_id:
            cover = self.download_pdf_screenshot(arxiv_id)
            if cover:
                return cover
        
        # 策略3: AI 生成
        return self.generate_ai_cover(title, category, index)
    
    def generate_all_covers(self, data: dict) -> dict:
        """为所有内容生成封面"""
        print("\n=== 生成封面图 ===\n")
        
        # 每日精选
        print("每日精选:")
        for i, item in enumerate(data.get('daily_pick', [])):
            cover = self.generate_cover(item, i+1)
            if cover:
                item['cover_image'] = cover
        
        # 热门文章
        print("\n热门文章:")
        for i, item in enumerate(data.get('hot_articles', [])):
            cover = self.generate_cover(item, i+1)
            if cover:
                item['cover_image'] = cover
        
        # arXiv论文
        print("\narXiv论文:")
        for i, item in enumerate(data.get('arxiv_papers', [])):
            cover = self.generate_cover(item, i+1)
            if cover:
                item['cover_image'] = cover
        
        return data


if __name__ == "__main__":
    import sys
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'daily_data/2026-04-18.json'
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    generator = EnhancedCoverGenerator()
    data = generator.generate_all_covers(data)
    
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 封面生成完成")
