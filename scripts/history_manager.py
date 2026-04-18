#!/usr/bin/env python3
"""
AI推荐日报 - 历史记录管理
确保不同天推送的内容不重复
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

class HistoryManager:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.history_dir = self.base_dir / "history"
        self.history_dir.mkdir(exist_ok=True)
        self.history_file = self.history_dir / "published.json"
        
        # 加载历史记录
        self.history = self._load_history()
    
    def _load_history(self) -> dict:
        """加载历史记录"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'daily_pick': {},      # {id: date}
            'hot_articles': {},    # {id: date}
            'arxiv_papers': {},    # {id: date}
            'github_projects': {}, # {id: date}
            'conference_papers': {} # {conference_id: {paper_id: date}}
        }
    
    def _save_history(self):
        """保存历史记录"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def get_item_id(self, item: dict) -> str:
        """获取项目唯一ID"""
        # 优先使用 arxiv_id 或 id
        if item.get('arxiv_id'):
            return f"arxiv_{item['arxiv_id']}"
        if item.get('id'):
            if 'arxiv.org' in item.get('link', ''):
                return f"arxiv_{item['id']}"
            return f"item_{item['id']}"
        
        # 使用链接
        link = item.get('link', item.get('url', ''))
        if link:
            return f"link_{hash(link) % 1000000}"
        
        # 使用标题
        title = item.get('cn_title', item.get('title', item.get('name', '')))
        return f"title_{hash(title) % 1000000}"
    
    def is_published(self, item: dict, category: str, days: int = 30) -> bool:
        """
        检查项目是否已发布
        category: daily_pick, hot_articles, arxiv_papers, github_projects, conference_papers
        days: 检查最近多少天内的记录
        """
        item_id = self.get_item_id(item)
        today = datetime.now().strftime("%Y-%m-%d")
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        if category == 'conference_papers':
            # 顶会论文特殊处理
            conf_name = item.get('conference', 'unknown')
            if conf_name in self.history.get('conference_papers', {}):
                if item_id in self.history['conference_papers'][conf_name]:
                    pub_date = self.history['conference_papers'][conf_name][item_id]
                    return pub_date >= cutoff_date
            return False
        else:
            # 其他类型
            if item_id in self.history.get(category, {}):
                pub_date = self.history[category][item_id]
                return pub_date >= cutoff_date
            return False
    
    def mark_published(self, item: dict, category: str, date: str = None):
        """标记项目为已发布"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        item_id = self.get_item_id(item)
        
        if category == 'conference_papers':
            # 顶会论文特殊处理
            conf_name = item.get('conference', 'unknown')
            if 'conference_papers' not in self.history:
                self.history['conference_papers'] = {}
            if conf_name not in self.history['conference_papers']:
                self.history['conference_papers'][conf_name] = {}
            self.history['conference_papers'][conf_name][item_id] = date
        else:
            # 其他类型
            if category not in self.history:
                self.history[category] = {}
            self.history[category][item_id] = date
        
        self._save_history()
    
    def filter_unpublished(self, items: list, category: str, days: int = 30) -> list:
        """过滤出未发布的项目"""
        unpublished = []
        for item in items:
            if not self.is_published(item, category, days):
                unpublished.append(item)
        return unpublished
    
    def mark_all_published(self, items: list, category: str, date: str = None):
        """标记所有项目为已发布"""
        for item in items:
            self.mark_published(item, category, date)
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        stats = {
            'daily_pick': len(self.history.get('daily_pick', {})),
            'hot_articles': len(self.history.get('hot_articles', {})),
            'arxiv_papers': len(self.history.get('arxiv_papers', {})),
            'github_projects': len(self.history.get('github_projects', {})),
            'conference_papers': sum(len(papers) for papers in self.history.get('conference_papers', {}).values())
        }
        stats['total'] = sum(stats.values())
        return stats
    
    def cleanup_old_records(self, days: int = 90):
        """清理旧记录"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        for category in ['daily_pick', 'hot_articles', 'arxiv_papers', 'github_projects']:
            if category in self.history:
                self.history[category] = {
                    k: v for k, v in self.history[category].items()
                    if v >= cutoff_date
                }
        
        # 顶会论文
        if 'conference_papers' in self.history:
            for conf_name in self.history['conference_papers']:
                self.history['conference_papers'][conf_name] = {
                    k: v for k, v in self.history['conference_papers'][conf_name].items()
                    if v >= cutoff_date
                }
        
        self._save_history()
        print(f"✅ 已清理 {days} 天前的记录")


if __name__ == "__main__":
    manager = HistoryManager()
    
    print("=== 历史记录统计 ===")
    stats = manager.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    print("\n=== 测试去重 ===")
    test_item = {'id': 'test123', 'title': '测试文章'}
    
    print(f"是否已发布: {manager.is_published(test_item, 'hot_articles')}")
    manager.mark_published(test_item, 'hot_articles')
    print(f"标记后是否已发布: {manager.is_published(test_item, 'hot_articles')}")
