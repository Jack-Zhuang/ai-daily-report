#!/usr/bin/env python3
"""
AI推荐日报 - 完整采集流程
集成MiniMax API进行论文理解和文章摘要生成
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from collect_articles import ArticleCollector
from minimax_client import MiniMaxClient

class EnhancedCollector:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # 初始化采集器和MiniMax客户端
        self.article_collector = ArticleCollector(base_dir)
        self.minimax = MiniMaxClient()  # 使用内置凭证
    
    def collect_articles_with_ai(self) -> list:
        """采集文章并使用AI生成摘要"""
        print(f"\n{'='*50}")
        print(f"📰 采集热门文章（AI增强）")
        print(f"{'='*50}\n")
        
        # 采集原始文章
        articles = self.article_collector.collect_all_articles()
        
        # 使用MiniMax生成中文摘要
        print(f"\n🤖 使用MiniMax生成文章摘要...")
        for i, article in enumerate(articles[:10]):  # 只处理前10篇
            try:
                result = self.minimax.generate_article_summary(article)
                article['cn_title'] = result.get('cn_title', article.get('title', '')[:25])
                article['cn_summary'] = result.get('cn_summary', article.get('summary', '')[:60])
                article['category'] = result.get('category', 'industry')
                print(f"  ✅ [{i+1}/{min(10, len(articles))}] {article['cn_title']}")
            except Exception as e:
                print(f"  ⚠️ [{i+1}] 摘要生成失败: {e}")
                article['cn_title'] = article.get('title', '')[:25]
                article['cn_summary'] = article.get('summary', '')[:60]
        
        return articles
    
    def enhance_papers_with_ai(self, papers: list) -> list:
        """使用AI增强论文解读"""
        print(f"\n{'='*50}")
        print(f"📄 使用MiniMax生成论文解读")
        print(f"{'='*50}\n")
        
        for i, paper in enumerate(papers[:5]):  # 只处理前5篇
            try:
                # 生成论文解读
                insights = self.minimax.analyze_paper(paper)
                paper['insights'] = insights
                paper['cn_title'] = paper.get('cn_title', paper.get('title', '')[:25])
                paper['cn_summary'] = insights.get('innovation', '').replace('<p>', '').replace('</p>', '')[:60]
                print(f"  ✅ [{i+1}/5] {paper['cn_title']}")
            except Exception as e:
                print(f"  ⚠️ [{i+1}] 解读生成失败: {e}")
        
        return papers
    
    def save_daily_data(self, data: dict):
        """保存每日数据"""
        data_file = self.base_dir / "daily_data" / f"{self.today}.json"
        data_file.parent.mkdir(exist_ok=True)
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 数据已保存: {data_file}")
    
    def run(self):
        """运行完整采集流程"""
        print(f"\n{'='*50}")
        print(f"🚀 AI推荐日报采集 - {self.today}")
        print(f"{'='*50}\n")
        
        # 1. 采集文章（AI增强）
        articles = self.collect_articles_with_ai()
        
        # 2. 加载已有数据
        data_file = self.base_dir / "daily_data" / f"{self.today}.json"
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                'date': self.today,
                'papers': [],
                'github_projects': [],
                'articles': [],
                'daily_pick': [],
                'conferences': {}
            }
        
        # 3. 更新文章数据
        data['articles'] = articles
        
        # 4. 增强论文解读
        if data.get('papers'):
            data['papers'] = self.enhance_papers_with_ai(data['papers'])
        
        # 5. 保存数据
        self.save_daily_data(data)
        
        print(f"\n{'='*50}")
        print(f"✅ 采集完成！")
        print(f"   - 文章: {len(articles)} 篇")
        print(f"   - 论文: {len(data.get('papers', []))} 篇")
        print(f"   - GitHub: {len(data.get('github_projects', []))} 个")
        print(f"{'='*50}\n")
        
        return data


if __name__ == "__main__":
    collector = EnhancedCollector()
    collector.run()
