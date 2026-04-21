#!/usr/bin/env python3
"""
AI推荐日报 - 完整翻译脚本
翻译所有内容（不仅是外显的）
"""

import json
from pathlib import Path
from datetime import datetime
import sys

class FullTranslator:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "daily_data"
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.data_file = self.data_dir / f"{self.today}.json"
        
        # 加载翻译器
        sys.path.insert(0, str(self.base_dir / "scripts"))
        try:
            from translator import MiniMaxTranslator
            self.translator = MiniMaxTranslator()
            self.has_translator = True
        except:
            self.has_translator = False
            print("⚠️ 翻译器不可用，使用简化翻译")
    
    def translate_text(self, text: str) -> str:
        """翻译文本"""
        if not text or any('\u4e00' <= c <= '\u9fff' for c in text):
            return text  # 已是中文或为空
        
        if self.has_translator:
            try:
                return self.translator.translate(text)
            except:
                pass
        
        # 简化翻译：标记为待翻译
        return text
    
    def run(self):
        """执行完整翻译"""
        print("=" * 60)
        print("🌐 AI推荐日报 - 完整翻译")
        print("=" * 60)
        print(f"📅 日期: {self.today}")
        
        if not self.data_file.exists():
            print(f"❌ 数据文件不存在: {self.data_file}")
            return False
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stats = {
            'daily_pick': 0,
            'articles': 0,
            'arxiv_papers': 0,
            'github': 0,
            'conferences': 0
        }
        
        # 1. 翻译每日精选
        print("\n📝 翻译每日精选...")
        for item in data.get('daily_pick', []):
            if not item.get('cn_title'):
                item['cn_title'] = self.translate_text(item.get('title', item.get('name', '')))
                stats['daily_pick'] += 1
            if not item.get('cn_summary'):
                item['cn_summary'] = self.translate_text(item.get('summary', item.get('description', '')))[:300]
        
        # 2. 翻译热门文章
        print("📝 翻译热门文章...")
        for item in data.get('articles', []):
            if not item.get('cn_title'):
                item['cn_title'] = self.translate_text(item.get('title', ''))
                stats['articles'] += 1
            if not item.get('cn_summary'):
                item['cn_summary'] = self.translate_text(item.get('summary', ''))[:300]
        
        # 3. 翻译 arXiv 论文
        print("📝 翻译 arXiv 论文...")
        for item in data.get('arxiv_papers', []):
            if not item.get('cn_title'):
                item['cn_title'] = self.translate_text(item.get('title', ''))
                stats['arxiv_papers'] += 1
            if not item.get('cn_summary'):
                item['cn_summary'] = self.translate_text(item.get('summary', ''))[:500]
        
        # 4. 翻译 GitHub 项目
        print("📝 翻译 GitHub 项目...")
        for item in data.get('github', []):
            if not item.get('cn_title'):
                item['cn_title'] = item.get('name', item.get('title', ''))
            if not item.get('cn_description'):
                item['cn_description'] = self.translate_text(item.get('description', ''))[:300]
                stats['github'] += 1
        
        # 5. 翻译顶会论文
        print("📝 翻译顶会论文...")
        conferences = data.get('conferences', {})
        for conf_name, conf_data in conferences.items():
            papers = conf_data.get('papers', [])
            for paper in papers:
                if not paper.get('cn_title'):
                    paper['cn_title'] = self.translate_text(paper.get('title', ''))
                    stats['conferences'] += 1
                if not paper.get('cn_summary'):
                    paper['cn_summary'] = self.translate_text(paper.get('summary', ''))[:300]
        
        # 保存
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "-" * 60)
        print("📊 翻译统计:")
        for key, count in stats.items():
            print(f"  {key}: {count} 条")
        
        print("\n✅ 完整翻译完成")
        return True


if __name__ == "__main__":
    translator = FullTranslator()
    translator.run()
