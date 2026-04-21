#!/usr/bin/env python3
"""
AI推荐日报 - 封面图生成脚本
使用 Seedream 生成卡片封面图
"""

import json
import subprocess
import os
from pathlib import Path
from datetime import datetime

class CoverGenerator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.covers_dir = self.base_dir / "covers"
        self.covers_dir.mkdir(exist_ok=True)
        self.skill_path = Path.home() / ".openclaw" / "workspace" / "skills" / "seedream-image_gen"
    
    def generate_cover(self, title: str, category: str, index: int) -> str:
        """生成封面图"""
        # 根据类别生成不同的提示词
        prompts = {
            'rec': f"推荐系统技术图示，数据流和算法可视化，科技蓝色调，简洁现代风格，标题\"{title[:20]}\"",
            'agent': f"AI智能体架构图，多智能体协作网络，科技紫色调，未来感设计，标题\"{title[:20]}\"",
            'llm': f"大语言模型原理图，神经网络结构，科技绿色调，学术风格，标题\"{title[:20]}\"",
            'article': f"科技新闻配图，AI技术概念，渐变背景，现代简约风格",
            'github': f"开源项目展示，代码界面，GitHub风格，深色主题，科技感",
            'paper': f"学术论文配图，研究方法示意图，学术风格，专业简洁"
        }
        
        prompt = prompts.get(category, prompts['article'])
        
        # 调用 Seedream 生成
        output_name = f"{category}_{index}.jpg"
        output_path = self.covers_dir / output_name
        
        if output_path.exists():
            print(f"  ✓ 已存在: {output_name}")
            return f"covers/{output_name}"
        
        # 调用生成脚本
        script_path = self.skill_path / "scripts" / "generate_seedream.py"
        if not script_path.exists():
            print(f"  ✗ 脚本不存在: {script_path}")
            return ""
        
        cmd = [
            "python3", str(script_path),
            "--prompt", prompt,
            "--max-images", "1"
        ]
        
        try:
            print(f"  生成: {title[:30]}...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # 查找生成的图片
            gen_dir = Path.home() / ".openclaw" / "workspace" / "generated-images"
            if gen_dir.exists():
                # 获取最新的图片
                images = sorted(gen_dir.glob("*.jpg"), key=os.path.getmtime, reverse=True)
                if images:
                    # 复制到 covers 目录
                    import shutil
                    shutil.copy(images[0], output_path)
                    print(f"  ✓ 生成成功: {output_name}")
                    return f"covers/{output_name}"
        except Exception as e:
            print(f"  ✗ 生成失败: {e}")
        
        return ""
    
    def generate_all_covers(self, data: dict) -> dict:
        """为所有内容生成封面"""
        print("=== 生成封面图 ===\n")
        
        # 每日精选
        print("每日精选:")
        for i, item in enumerate(data.get('daily_pick', [])):
            if not item.get('cover_image'):
                category = item.get('category', item.get('pick_type', 'article'))
                title = item.get('cn_title', item.get('title', ''))
                cover = self.generate_cover(title, category, i+1)
                if cover:
                    item['cover_image'] = cover
        
        # 热门文章
        print("\n热门文章:")
        for i, item in enumerate(data.get('hot_articles', [])):
            if not item.get('cover_image'):
                category = item.get('category', 'article')
                title = item.get('cn_title', item.get('title', ''))
                cover = self.generate_cover(title, category, i+1)
                if cover:
                    item['cover_image'] = cover
        
        # arXiv论文
        print("\narXiv论文:")
        for i, item in enumerate(data.get('arxiv_papers', [])):
            if not item.get('cover_image'):
                category = item.get('category', 'paper')
                title = item.get('cn_title', item.get('title', ''))
                cover = self.generate_cover(title, category, i+1)
                if cover:
                    item['cover_image'] = cover
        
        return data


if __name__ == "__main__":
    import sys
    
    # 加载数据
    today = datetime.now().strftime("%Y-%m-%d")
    input_file = sys.argv[1] if len(sys.argv) > 1 else f'daily_data/{today}.json'
    
    # 检查文件是否存在，如果不存在则使用前一天
    if not Path(input_file).exists():
        from datetime import timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        input_file_yesterday = f'daily_data/{yesterday}.json'
        if Path(input_file_yesterday).exists():
            input_file = input_file_yesterday
            print(f"⚠️ 使用前一天的数据: {yesterday}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 生成封面
    generator = CoverGenerator()
    data = generator.generate_all_covers(data)
    
    # 保存
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 封面生成完成")
