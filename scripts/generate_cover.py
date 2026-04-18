#!/usr/bin/env python3
"""
AI推荐日报 - 题图生成脚本
从文章/论文中提取有意义的图片作为题图
"""

import json
import requests
import re
from pathlib import Path
from datetime import datetime
import hashlib

class CoverGenerator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache"
        self.covers_dir = self.base_dir / "covers"
        self.covers_dir.mkdir(exist_ok=True)
        
    def extract_image_from_rss(self, rss_url: str) -> str:
        """从 RSS 文章中提取第一张图片"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(rss_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            content = response.text
            
            # 尝试提取图片 URL
            # 1. 从 content:encoded 中提取
            img_patterns = [
                r'<img[^>]+src=["\']([^"\']+\.(?:jpg|jpeg|png|gif|webp))["\']',
                r'<enclosure[^>]+url=["\']([^"\']+\.(?:jpg|jpeg|png|gif|webp))["\']',
                r'data-src=["\']([^"\']+\.(?:jpg|jpeg|png|gif|webp))["\']',
            ]
            
            for pattern in img_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # 过滤掉太小的图片（通常是图标）
                    for img_url in matches:
                        if 'avatar' not in img_url.lower() and 'icon' not in img_url.lower():
                            if 'mmbiz.qpic.cn' in img_url or 'pic' in img_url.lower():
                                return img_url
            
            return None
        except Exception as e:
            print(f"  ⚠️ 提取图片失败: {e}")
            return None
    
    def download_image(self, url: str, save_path: str) -> bool:
        """下载图片到本地"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://mp.weixin.qq.com/'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(f"  ⚠️ 下载图片失败: {e}")
            return False
    
    def get_article_cover(self, article: dict) -> str:
        """获取文章的题图"""
        # 1. 尝试从文章链接中提取图片
        link = article.get('link', '')
        if link:
            img_url = self.extract_image_from_rss(link)
            if img_url:
                # 下载图片
                img_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
                save_path = self.covers_dir / f"article_{img_hash}.jpg"
                if self.download_image(img_url, str(save_path)):
                    return str(save_path)
        
        # 2. 使用文章摘要生成信息图
        return self.generate_info_graphic(article)
    
    def generate_info_graphic(self, article: dict) -> str:
        """基于文章内容生成信息图"""
        # 使用 seedream 生成有意义的图片
        title = article.get('cn_title', article.get('title', ''))
        summary = article.get('cn_summary', article.get('summary', ''))
        source = article.get('source', '')
        
        # 构建提示词
        prompt = f"""
        科技资讯卡片设计，展示文章核心观点。
        标题：{title[:50]}
        来源：{source}
        关键信息：{summary[:100]}
        风格：现代简约，科技感，适合移动端展示，清晰的文字排版
        """
        
        # 调用 seedream 生成图片
        try:
            import subprocess
            result = subprocess.run([
                'python3', 
                '/home/sandbox/.openclaw/workspace/skills/seedream-image_gen/scripts/generate_seedream.py',
                '--prompt', prompt.strip(),
                '--max-images', '1'
            ], capture_output=True, text=True, timeout=120)
            
            # 解析输出获取图片路径
            output = result.stdout
            if 'Saved to:' in output:
                for line in output.split('\n'):
                    if 'Saved to:' in line:
                        return line.split('Saved to:')[-1].strip()
        except Exception as e:
            print(f"  ⚠️ 生成信息图失败: {e}")
        
        return None
    
    def get_paper_cover(self, paper: dict) -> str:
        """获取论文的题图（从 PDF 截图或生成信息图）"""
        title = paper.get('cn_title', paper.get('title', ''))
        summary = paper.get('cn_summary', paper.get('summary', ''))
        category = paper.get('category', '')
        
        # 生成论文信息图
        prompt = f"""
        学术论文信息卡片，展示研究核心。
        论文标题：{title[:60]}
        研究领域：{category}
        核心贡献：{summary[:150]}
        风格：学术风格，简洁专业，包含图表元素，适合技术读者
        """
        
        try:
            import subprocess
            result = subprocess.run([
                'python3', 
                '/home/sandbox/.openclaw/workspace/skills/seedream-image_gen/scripts/generate_seedream.py',
                '--prompt', prompt.strip(),
                '--max-images', '1'
            ], capture_output=True, text=True, timeout=120)
            
            output = result.stdout
            if 'Saved to:' in output:
                for line in output.split('\n'):
                    if 'Saved to:' in line:
                        return line.split('Saved to:')[-1].strip()
        except Exception as e:
            print(f"  ⚠️ 生成论文图失败: {e}")
        
        return None
    
    def generate_daily_cover(self, data: dict) -> str:
        """生成日报主页题图"""
        # 获取今日精选的第一篇文章
        daily_pick = data.get('daily_pick', [])
        if daily_pick:
            first_pick = daily_pick[0]
            pick_type = first_pick.get('pick_type', 'paper')
            
            if pick_type == 'paper':
                return self.get_paper_cover(first_pick)
            else:
                return self.get_article_cover(first_pick)
        
        # 如果没有精选，使用统计信息生成
        stats = {
            'papers': len(data.get('arxiv_papers', [])),
            'projects': len(data.get('github_projects', [])),
            'articles': len(data.get('hot_articles', [])),
            'date': datetime.now().strftime("%Y-%m-%d")
        }
        
        prompt = f"""
        AI推荐日报封面，{stats['date']}。
        今日数据：{stats['papers']}篇论文，{stats['projects']}个项目，{stats['articles']}篇文章。
        主题：推荐算法、AI Agent、大语言模型。
        风格：科技感，数据可视化，现代简约，适合移动端展示。
        """
        
        try:
            import subprocess
            result = subprocess.run([
                'python3', 
                '/home/sandbox/.openclaw/workspace/skills/seedream-image_gen/scripts/generate_seedream.py',
                '--prompt', prompt.strip(),
                '--max-images', '1'
            ], capture_output=True, text=True, timeout=120)
            
            output = result.stdout
            if 'Saved to:' in output:
                for line in output.split('\n'):
                    if 'Saved to:' in line:
                        cover_path = line.split('Saved to:')[-1].strip()
                        # 复制到 ai_daily 目录
                        import shutil
                        target_path = self.base_dir / "cover.jpg"
                        shutil.copy(cover_path, target_path)
                        return str(target_path)
        except Exception as e:
            print(f"  ⚠️ 生成日报封面失败: {e}")
        
        return None


if __name__ == "__main__":
    import json
    
    # 加载数据
    base_dir = Path(__file__).parent.parent
    with open(base_dir / "daily_data" / "2026-04-18.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    generator = CoverGenerator()
    
    print("🎨 生成日报题图...")
    cover_path = generator.generate_daily_cover(data)
    if cover_path:
        print(f"✅ 题图已生成: {cover_path}")
    else:
        print("❌ 题图生成失败")
