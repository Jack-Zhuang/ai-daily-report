#!/usr/bin/env python3
"""
AI推荐日报 - 后台批量封面生成任务
支持：arXiv论文、GitHub项目、热门文章、每日精选
特点：
1. arXiv论文使用 arxiv_id 命名，避免冲突
2. 其他内容使用 category_index 命名
3. 支持增量处理，跳过已有有效封面
4. 支持断点续传
"""

import json
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class BatchCoverGenerator:
    """后台批量封面生成器"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.covers_dir = self.base_dir / "covers"
        self.covers_dir.mkdir(exist_ok=True)

        self.seedream_script = Path.home() / ".openclaw" / "workspace" / "skills" / "seedream-image_gen" / "scripts" / "generate_seedream.py"
        self.gen_dir = Path.home() / ".openclaw" / "workspace" / "generated-images"

        # 进度文件
        self.progress_file = self.base_dir / "logs" / "cover_generation_progress.json"
        self.progress_file.parent.mkdir(exist_ok=True)

        # 统计
        self.stats = {
            "total": 0,
            "generated": 0,
            "skipped": 0,
            "failed": 0
        }

        # 提示词模板
        self.prompts = {
            'paper': "Academic research paper cover, scientific visualization, neural network architecture diagram, professional academic style, blue and white color scheme, clean modern design, high quality",
            'article': "Tech news article illustration, AI technology concept, digital transformation, gradient background, modern minimalist style, vibrant colors",
            'github': "Open source project showcase, code interface, GitHub style, dark theme, tech aesthetic, developer tools, professional design",
            'rec': "Recommendation system visualization, data flow diagram, algorithm illustration, tech blue theme, modern design, clean layout",
            'agent': "AI agent architecture diagram, multi-agent collaboration network, purple tech theme, futuristic design, innovative",
            'llm': "Large language model illustration, transformer architecture, green tech theme, academic style, professional",
            'pick': "Featured content highlight, premium quality, elegant gradient background, modern design, sophisticated"
        }

    def load_progress(self) -> Dict:
        """加载进度"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "last_run": None,
            "processed": {},
            "stats": {}
        }

    def save_progress(self, progress: Dict):
        """保存进度"""
        progress["last_run"] = datetime.now().isoformat()
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

    def generate_cover_with_seedream(self, prompt: str) -> Optional[str]:
        """使用 Seedream 生成封面"""
        if not self.seedream_script.exists():
            print("    ⚠️ Seedream 脚本不存在")
            return None

        try:
            cmd = ["python3", str(self.seedream_script), "--prompt", prompt, "--max-images", "1"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            # 查找最新生成的图片
            if self.gen_dir.exists():
                images = sorted(self.gen_dir.glob("*.jpg"), key=lambda x: x.stat().st_mtime, reverse=True)
                if images:
                    return str(images[0])

        except subprocess.TimeoutExpired:
            print("    ⚠️ 生成超时")
        except Exception as e:
            print(f"    ⚠️ 生成失败: {e}")

        return None

    def is_valid_cover(self, cover_path: Path) -> bool:
        """检查封面是否有效"""
        return cover_path.exists() and cover_path.stat().st_size > 10000

    def process_arxiv_paper(self, paper: Dict, progress: Dict) -> bool:
        """处理单篇 arXiv 论文"""
        arxiv_id = paper.get('id') or paper.get('arxiv_id')
        if not arxiv_id:
            return False

        self.stats['total'] += 1
        title = paper.get('cn_title') or paper.get('title', 'Untitled')

        # 封面命名：paper_<arxiv_id>.jpg
        cover_name = f"paper_{arxiv_id}.jpg"
        cover_path = self.covers_dir / cover_name

        # 检查是否已处理
        progress_key = f"arxiv_{arxiv_id}"
        if progress_key in progress.get('processed', {}):
            if self.is_valid_cover(cover_path):
                print(f"  ✓ [{arxiv_id}] {title[:40]}... (已处理)")
                self.stats['skipped'] += 1
                return True

        # 检查现有封面
        if self.is_valid_cover(cover_path):
            paper['cover_image'] = f"covers/{cover_name}"
            progress.setdefault('processed', {})[progress_key] = datetime.now().isoformat()
            print(f"  ✓ [{arxiv_id}] {title[:40]}... (已有封面)")
            self.stats['skipped'] += 1
            return True

        # 生成封面
        print(f"  🎨 [{arxiv_id}] {title[:40]}...", end=" ", flush=True)
        prompt = self.prompts['paper']

        gen_image = self.generate_cover_with_seedream(prompt)
        if gen_image:
            # 复制到 covers 目录
            import shutil
            shutil.copy(gen_image, cover_path)
            paper['cover_image'] = f"covers/{cover_name}"
            progress.setdefault('processed', {})[progress_key] = datetime.now().isoformat()
            print("✅")
            self.stats['generated'] += 1
            return True
        else:
            print("❌")
            self.stats['failed'] += 1
            return False

    def process_other_item(self, item: Dict, category: str, index: int, progress: Dict) -> bool:
        """处理其他类型的项目"""
        self.stats['total'] += 1

        title = item.get('cn_title') or item.get('title') or item.get('name', 'Untitled')

        # 封面命名：<category>_<index>.jpg
        cover_name = f"{category}_{index}.jpg"
        cover_path = self.covers_dir / cover_name

        # 检查是否已处理
        progress_key = f"{category}_{index}"
        if progress_key in progress.get('processed', {}):
            if self.is_valid_cover(cover_path):
                print(f"  ✓ [{index}] {title[:40]}... (已处理)")
                self.stats['skipped'] += 1
                return True

        # 检查现有封面
        if self.is_valid_cover(cover_path):
            item['cover_image'] = f"covers/{cover_name}"
            progress.setdefault('processed', {})[progress_key] = datetime.now().isoformat()
            print(f"  ✓ [{index}] {title[:40]}... (已有封面)")
            self.stats['skipped'] += 1
            return True

        # 生成封面
        print(f"  🎨 [{index}] {title[:40]}...", end=" ", flush=True)
        prompt = self.prompts.get(category, self.prompts['article'])

        gen_image = self.generate_cover_with_seedream(prompt)
        if gen_image:
            import shutil
            shutil.copy(gen_image, cover_path)
            item['cover_image'] = f"covers/{cover_name}"
            progress.setdefault('processed', {})[progress_key] = datetime.now().isoformat()
            print("✅")
            self.stats['generated'] += 1
            return True
        else:
            print("❌")
            self.stats['failed'] += 1
            return False

    def process_date(self, date_str: str = None, limit_per_category: int = None):
        """处理指定日期的数据"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        data_file = self.base_dir / "daily_data" / f"{date_str}.json"

        if not data_file.exists():
            print(f"❌ 数据文件不存在: {data_file}")
            return

        print(f"\n{'='*60}")
        print(f"🎨 批量封面生成 - {date_str}")
        if limit_per_category:
            print(f"   每类限制: {limit_per_category} 条")
        print(f"{'='*60}\n")

        # 加载数据和进度
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        progress = self.load_progress()

        # 1. 处理每日精选
        print("📌 每日精选:")
        items = data.get('daily_pick', [])
        items_to_process = items[:limit_per_category] if limit_per_category else items
        for i, item in enumerate(items_to_process, 1):
            self.process_other_item(item, 'pick', i, progress)
            time.sleep(0.5)

        # 2. 处理热门文章
        print("\n📰 热门文章:")
        items = data.get('hot_articles', [])
        items_to_process = items[:limit_per_category] if limit_per_category else items
        for i, item in enumerate(items_to_process, 1):
            self.process_other_item(item, 'article', i, progress)
            time.sleep(0.5)

        # 3. 处理 arXiv 论文（使用 arxiv_id 命名）
        print("\n📄 arXiv 论文:")
        items = data.get('arxiv_papers', [])
        items_to_process = items[:limit_per_category] if limit_per_category else items
        for paper in items_to_process:
            self.process_arxiv_paper(paper, progress)
            time.sleep(0.5)

        # 4. 处理 GitHub 项目
        print("\n💻 GitHub 项目:")
        items = data.get('github_projects', [])
        items_to_process = items[:limit_per_category] if limit_per_category else items
        for i, item in enumerate(items_to_process, 1):
            self.process_other_item(item, 'github', i, progress)
            time.sleep(0.5)

        # 保存数据和进度
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        progress['stats'] = self.stats
        self.save_progress(progress)

        # 输出统计
        print(f"\n{'='*60}")
        print(f"📊 处理完成")
        print(f"{'='*60}")
        print(f"  总计: {self.stats['total']} 条")
        print(f"  已生成: {self.stats['generated']} 条")
        print(f"  已跳过: {self.stats['skipped']} 条")
        print(f"  失败: {self.stats['failed']} 条")
        print(f"{'='*60}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="后台批量封面生成")
    parser.add_argument("--date", type=str, default=None, help="日期 (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=None, help="每类最多处理数量")

    args = parser.parse_args()

    generator = BatchCoverGenerator()
    generator.process_date(args.date, args.limit)


if __name__ == "__main__":
    main()
