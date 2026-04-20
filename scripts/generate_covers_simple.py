#!/usr/bin/env python3
"""
AI推荐日报 - 快速封面生成脚本
直接使用 Seedream AI 生成封面，跳过 PDF 处理
"""

import json
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime


class SimpleCoverGenerator:
    """快速封面生成器"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.covers_dir = self.base_dir / "covers"
        self.covers_dir.mkdir(exist_ok=True)
        
        self.seedream_script = Path.home() / ".openclaw" / "workspace" / "skills" / "seedream-image_gen" / "scripts" / "generate_seedream.py"
        self.gen_dir = Path.home() / ".openclaw" / "workspace" / "generated-images"
    
    def generate_cover(self, title: str, category: str, index: int) -> str:
        """使用 Seedream 生成封面"""
        output_name = f"{category}_{index}.jpg"
        output_path = self.covers_dir / output_name
        
        # 如果已存在且大于 10KB，直接返回
        if output_path.exists() and output_path.stat().st_size > 10000:
            return f"covers/{output_name}"
        
        # 生成提示词
        prompts = {
            'paper': f"Academic research paper cover, scientific visualization, neural network diagram, professional academic style, blue and white color scheme, clean modern design",
            'article': f"Tech news article illustration, AI technology concept, digital transformation, gradient background, modern minimalist style",
            'github': f"Open source project showcase, code interface, GitHub style, dark theme, tech aesthetic, developer tools",
            'rec': f"Recommendation system visualization, data flow diagram, algorithm illustration, tech blue theme, modern design",
            'agent': f"AI agent architecture diagram, multi-agent collaboration network, purple tech theme, futuristic design",
            'llm': f"Large language model illustration, transformer architecture, green tech theme, academic style",
            'pick': f"Featured content highlight, premium quality, elegant gradient background, modern design"
        }
        
        prompt = prompts.get(category, prompts['article'])
        
        # 调用 Seedream
        if not self.seedream_script.exists():
            print(f"    ⚠️ Seedream 脚本不存在")
            return ""
        
        try:
            cmd = ["python3", str(self.seedream_script), "--prompt", prompt, "--max-images", "1"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # 查找最新生成的图片
            if self.gen_dir.exists():
                images = sorted(self.gen_dir.glob("*.jpg"), key=lambda x: x.stat().st_mtime, reverse=True)
                if images:
                    # 复制到 covers 目录
                    import shutil
                    shutil.copy(images[0], output_path)
                    return f"covers/{output_name}"
        
        except subprocess.TimeoutExpired:
            print(f"    ⚠️ 生成超时")
        except Exception as e:
            print(f"    ⚠️ 生成失败: {e}")
        
        return ""
    
    def process_daily_data(self, date_str: str = None, limit: int = 5):
        """处理指定日期的数据"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        data_file = self.base_dir / "daily_data" / f"{date_str}.json"
        
        if not data_file.exists():
            print(f"❌ 数据文件不存在: {data_file}")
            return
        
        print(f"\n{'='*60}")
        print(f"🎨 为 {date_str} 的内容生成封面 (每类最多 {limit} 个)")
        print(f"{'='*60}\n")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stats = {"total": 0, "generated": 0, "skipped": 0, "failed": 0}
        
        # 处理各类内容
        categories = [
            ('daily_pick', 'pick', '📌 每日精选'),
            ('hot_articles', 'article', '📰 热门文章'),
            ('arxiv_papers', 'paper', '📄 arXiv 论文'),
            ('github_projects', 'github', '💻 GitHub 项目')
        ]
        
        for key, cat, label in categories:
            items = data.get(key, [])
            if not items:
                continue
            
            print(f"\n{label}:")
            
            for i, item in enumerate(items[:limit]):
                stats['total'] += 1
                title = item.get('cn_title') or item.get('title') or item.get('name', 'Untitled')
                existing = item.get('cover_image')
                
                # 检查是否已有有效封面
                if existing:
                    cover_path = self.base_dir / existing
                    if cover_path.exists() and cover_path.stat().st_size > 10000:
                        print(f"  ✓ [{i+1}] {title[:40]}... (已有)")
                        stats['skipped'] += 1
                        continue
                
                # 生成封面
                print(f"  🎨 [{i+1}] {title[:40]}...", end=" ", flush=True)
                cover = self.generate_cover(title, cat, i+1)
                
                if cover:
                    item['cover_image'] = cover
                    print(f"✅")
                    stats['generated'] += 1
                else:
                    print(f"❌")
                    stats['failed'] += 1
                
                time.sleep(0.5)  # 避免 API 限流
        
        # 保存数据
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 输出统计
        print(f"\n{'='*60}")
        print(f"📊 统计: 总计 {stats['total']} | 生成 {stats['generated']} | 跳过 {stats['skipped']} | 失败 {stats['failed']}")
        print(f"{'='*60}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="快速封面生成")
    parser.add_argument("--date", type=str, default=None, help="日期 (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=5, help="每类最多处理数量")
    
    args = parser.parse_args()
    
    generator = SimpleCoverGenerator()
    generator.process_daily_data(args.date, args.limit)


if __name__ == "__main__":
    main()
