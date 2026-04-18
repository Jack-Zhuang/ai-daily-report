#!/usr/bin/env python3
"""
AI推荐日报 - 每日精选构建脚本
严格按照规则构建每日精选：3篇文章 + 1篇论文 + 1个GitHub项目
顺序：[article, article, article, paper, github]
集成历史记录去重，确保不同天推送的内容不重复
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import sys

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))
from history_manager import HistoryManager

class DailyPickBuilder:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.history_manager = HistoryManager(str(self.base_dir))
    
    def is_recent(self, published: str, max_days: int = 3) -> bool:
        """检查内容是否足够新"""
        if not published:
            return True
        try:
            pub_date = datetime.strptime(published[:10], '%Y-%m-%d')
            days_ago = (datetime.now() - pub_date).days
            return days_ago <= max_days
        except:
            return True
    
    def is_relevant(self, title: str, summary: str = '') -> bool:
        """检查内容是否相关"""
        keywords = [
            'recommend', 'recommendation', 'recsys', 'ctr',
            'agent', 'multi-agent', 'autonomous',
            'llm', 'large language model', 'gpt', 'bert', 'transformer'
        ]
        text = (title + ' ' + summary).lower()
        return any(kw in text for kw in keywords)
    
    def build_daily_pick(self, data: dict) -> list:
        """
        构建每日精选
        规则：3篇文章 + 1篇论文 + 1个GitHub项目
        顺序：[article, article, article, paper, github]
        去重：确保不同天推送的内容不重复
        """
        print("="*50)
        print("📌 构建每日精选")
        print("="*50)
        print("规则: 3篇文章 + 1篇论文 + 1个GitHub项目")
        print("顺序: [article, article, article, paper, github]")
        print("去重: 排除最近30天内已发布的内容")
        print()
        
        # 收集所有可用内容
        articles = []
        papers = []
        githubs = []
        
        # 从热门文章中筛选
        for item in data.get('hot_articles', []):
            link = item.get('link', '')
            title = item.get('cn_title', item.get('title', ''))
            summary = item.get('cn_summary', item.get('summary', ''))
            published = item.get('published', '')
            
            # 检查相关性和时效性
            if not self.is_relevant(title, summary):
                continue
            if not self.is_recent(published, max_days=3):
                continue
            
            # 检查是否已发布
            if self.history_manager.is_published(item, 'hot_articles', days=30):
                continue
            
            if 'arxiv.org' in link:
                item['pick_type'] = 'paper'
                papers.append(item)
            elif 'github.com' in link:
                item['pick_type'] = 'github'
                githubs.append(item)
            else:
                item['pick_type'] = 'article'
                articles.append(item)
        
        # 从 arXiv 论文中补充
        for item in data.get('arxiv_papers', []):
            title = item.get('cn_title', item.get('title', ''))
            summary = item.get('cn_summary', item.get('summary', ''))
            published = item.get('published', '')
            
            if not self.is_relevant(title, summary):
                continue
            if not self.is_recent(published, max_days=3):
                continue
            
            # 检查是否已发布
            if self.history_manager.is_published(item, 'arxiv_papers', days=30):
                continue
            
            item['pick_type'] = 'paper'
            papers.append(item)
        
        # 从 GitHub 项目中补充
        for item in data.get('github_trending', data.get('github_projects', [])):
            title = item.get('cn_title', item.get('name', ''))
            summary = item.get('cn_summary', item.get('description', ''))
            
            if not self.is_relevant(title, summary):
                continue
            
            # 检查是否已发布
            if self.history_manager.is_published(item, 'github_projects', days=30):
                continue
            
            item['pick_type'] = 'github'
            githubs.append(item)
        
        print(f"可用内容（已去重）:")
        print(f"  文章: {len(articles)}篇")
        print(f"  论文: {len(papers)}篇")
        print(f"  GitHub: {len(githubs)}个")
        print()
        
        # 构建每日精选
        daily_pick = []
        
        # 3篇文章
        print("选择文章:")
        for i, item in enumerate(articles[:3]):
            print(f"  {i+1}. {item.get('cn_title', item.get('title', ''))[:40]}...")
            item['pick_type'] = 'article'
            daily_pick.append(item)
        
        # 1篇论文
        print("\n选择论文:")
        if papers:
            print(f"  1. {papers[0].get('cn_title', papers[0].get('title', ''))[:40]}...")
            papers[0]['pick_type'] = 'paper'
            daily_pick.append(papers[0])
        
        # 1个GitHub
        print("\n选择GitHub:")
        if githubs:
            print(f"  1. {githubs[0].get('cn_title', githubs[0].get('name', ''))[:40]}...")
            githubs[0]['pick_type'] = 'github'
            daily_pick.append(githubs[0])
        
        # 标记为已发布
        for item in daily_pick:
            self.history_manager.mark_published(item, 'daily_pick')
        
        # 验证
        print(f"\n{'='*50}")
        print(f"✅ 每日精选构建完成: {len(daily_pick)}项")
        
        types = [item.get('pick_type') for item in daily_pick]
        expected = ['article', 'article', 'article', 'paper', 'github']
        
        if types == expected:
            print(f"   顺序: ✅ {types}")
        else:
            print(f"   顺序: ⚠️ {types} (期望: {expected})")
        
        # 显示历史记录统计
        stats = self.history_manager.get_stats()
        print(f"\n历史记录统计:")
        print(f"   每日精选: {stats['daily_pick']}条")
        print(f"   热门文章: {stats['hot_articles']}条")
        print(f"   arXiv论文: {stats['arxiv_papers']}条")
        print(f"   GitHub项目: {stats['github_projects']}条")
        
        print(f"{'='*50}")
        
        return daily_pick
    
    def run(self, data_file: str = None):
        """运行构建"""
        if data_file is None:
            # 尝试今天或昨天的数据
            for date in [self.today, self.yesterday]:
                path = self.base_dir / "daily_data" / f"{date}.json"
                if path.exists():
                    data_file = path
                    break
        
        if not data_file:
            print("❌ 未找到数据文件")
            return None
        
        print(f"加载数据: {data_file}")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 构建每日精选
        daily_pick = self.build_daily_pick(data)
        
        # 更新数据
        data['daily_pick'] = daily_pick
        
        # 从热门文章中移除已选入每日精选的
        pick_titles = set()
        for item in daily_pick:
            title = item.get('cn_title', item.get('title', item.get('name', '')))
            pick_titles.add(title)
        
        hot_articles = []
        for item in data.get('hot_articles', []):
            title = item.get('cn_title', item.get('title', ''))
            if title not in pick_titles:
                hot_articles.append(item)
        
        data['hot_articles'] = hot_articles
        
        # 保存
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 数据已保存")
        
        return data


if __name__ == "__main__":
    import sys
    
    data_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    builder = DailyPickBuilder()
    builder.run(data_file)
