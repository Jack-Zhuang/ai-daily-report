#!/usr/bin/env python3
"""
AI推荐日报 - 为缺失封面的内容生成封面图
支持：arXiv论文、GitHub项目、热门文章
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from generate_covers_enhanced import EnhancedCoverGenerator
    HAS_COVER_GENERATOR = True
except ImportError:
    HAS_COVER_GENERATOR = False
    print("❌ 封面生成器未安装，请检查 generate_covers_enhanced.py")


class MissingCoverGenerator:
    """为缺失封面的内容生成封面"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        
        if HAS_COVER_GENERATOR:
            self.cover_gen = EnhancedCoverGenerator(str(self.base_dir))
        
        self.stats = {
            "total": 0,
            "generated": 0,
            "skipped": 0,
            "failed": 0
        }
    
    def process_daily_data(self, date_str: str = None):
        """处理指定日期的数据"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        data_file = self.base_dir / "daily_data" / f"{date_str}.json"
        
        if not data_file.exists():
            print(f"❌ 数据文件不存在: {data_file}")
            return
        
        print(f"\n{'='*60}")
        print(f"🎨 为 {date_str} 的内容生成封面")
        print(f"{'='*60}\n")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 1. 处理每日精选
        print("📌 每日精选:")
        for i, item in enumerate(data.get('daily_pick', [])):
            self._process_item(item, 'pick', i+1)
        
        # 2. 处理热门文章
        print("\n📰 热门文章:")
        for i, item in enumerate(data.get('hot_articles', [])):
            self._process_item(item, 'article', i+1)
        
        # 3. 处理 arXiv 论文
        print("\n📄 arXiv 论文:")
        for i, item in enumerate(data.get('arxiv_papers', [])):
            self._process_item(item, 'paper', i+1)
        
        # 4. 处理 GitHub 项目
        print("\n💻 GitHub 项目:")
        for i, item in enumerate(data.get('github_projects', [])):
            self._process_item(item, 'github', i+1)
        
        # 保存更新后的数据
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 输出统计
        print(f"\n{'='*60}")
        print(f"📊 封面生成统计")
        print(f"{'='*60}")
        print(f"  总计: {self.stats['total']} 项")
        print(f"  已生成: {self.stats['generated']} 项")
        print(f"  已跳过: {self.stats['skipped']} 项")
        print(f"  失败: {self.stats['failed']} 项")
        print(f"{'='*60}")
    
    def _process_item(self, item: dict, category: str, index: int):
        """处理单个项目"""
        self.stats['total'] += 1
        
        title = item.get('cn_title') or item.get('title') or item.get('name', '')
        existing_cover = item.get('cover_image')
        
        # 检查是否已有有效封面
        if existing_cover:
            cover_path = self.base_dir / existing_cover
            if cover_path.exists() and cover_path.stat().st_size > 10000:
                print(f"  ✓ [{index}] {title[:40]}... (已有封面)")
                self.stats['skipped'] += 1
                return
        
        print(f"  🎨 [{index}] {title[:40]}...", end=" ")
        
        if not HAS_COVER_GENERATOR:
            print("❌ (生成器未安装)")
            self.stats['failed'] += 1
            return
        
        try:
            # 生成封面
            cover = self.cover_gen.generate_cover(item, index)
            
            if cover:
                item['cover_image'] = cover
                print(f"✅ ({cover})")
                self.stats['generated'] += 1
            else:
                print("❌ (生成失败)")
                self.stats['failed'] += 1
            
            # 避免 API 限流
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ ({e})")
            self.stats['failed'] += 1


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="为缺失封面的内容生成封面")
    parser.add_argument("--date", type=str, default=None, help="日期 (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    generator = MissingCoverGenerator()
    generator.process_daily_data(args.date)


if __name__ == "__main__":
    main()
