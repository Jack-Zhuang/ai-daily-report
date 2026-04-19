#!/usr/bin/env python3
"""
AI推荐日报 - 批量论文处理任务
1. 采集完整顶会论文列表
2. 下载 PDF
3. 生成增强版解读
4. 转换为 HTML
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from paper_extractor import PaperExtractor
from insight_generator import EnhancedInsightGenerator
from generate_insight_page import generate_insight_page, markdown_to_html


class BatchProcessor:
    """批量论文处理器"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent.parent
        self.base_dir = Path(base_dir)
        
        # 初始化组件
        self.extractor = PaperExtractor(str(self.base_dir / "paper_cache"))
        self.generator = EnhancedInsightGenerator(str(self.base_dir))
        
        # 统计
        self.stats = {
            "total": 0,
            "processed": 0,
            "failed": 0,
            "skipped": 0
        }
    
    def get_all_papers(self) -> List[Dict]:
        """获取所有待处理论文"""
        papers = []
        
        # 1. 从 arXiv 日常采集中获取
        daily_file = self.base_dir / "daily_data" / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        if daily_file.exists():
            with open(daily_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for p in data.get("arxiv_papers", []):
                p["_source"] = "arxiv_daily"
                papers.append(p)
        
        # 2. 从顶会论文中获取
        conf_file = self.base_dir / "cache" / "conference_papers.json"
        if conf_file.exists():
            with open(conf_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for conf_name, conf_data in data.items():
                if isinstance(conf_data, dict) and 'papers' in conf_data:
                    for p in conf_data.get('papers', []):
                        p["_source"] = f"conference_{conf_name}"
                        papers.append(p)
        
        return papers
    
    def is_processed(self, arxiv_id: str) -> bool:
        """检查是否已处理"""
        # 检查任意日期的解读文件
        insights_dir = self.base_dir / "insights_enhanced"
        if insights_dir.exists():
            for md_file in insights_dir.glob(f"*_{arxiv_id}.md"):
                return True
        return False
    
    def load_progress(self) -> Dict:
        """加载处理进度"""
        progress_file = self.base_dir / "paper_cache" / "processing_progress.json"
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "last_run": None,
            "processed_ids": [],
            "failed_ids": [],
            "stats": {}
        }
    
    def save_progress(self, progress: Dict):
        """保存处理进度"""
        progress_file = self.base_dir / "paper_cache" / "processing_progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        progress["last_run"] = datetime.now().isoformat()
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    def process_paper(self, paper: Dict) -> bool:
        """处理单篇论文"""
        arxiv_id = paper.get("arxiv_id", paper.get("id", ""))
        title = paper.get("title", "")
        
        if not arxiv_id:
            print(f"  ⚠️ 跳过（无 arxiv_id）: {title[:40]}")
            self.stats["skipped"] += 1
            return False
        
        # 检查是否已处理
        if self.is_processed(arxiv_id):
            print(f"  ⏭️ 已处理: {arxiv_id}")
            self.stats["skipped"] += 1
            return True
        
        try:
            print(f"\n{'='*60}")
            print(f"📄 [{self.stats['processed']+1}/{self.stats['total']}] {title[:50]}")
            print(f"   arXiv: {arxiv_id}")
            print(f"{'='*60}")
            
            # 1. 提取论文内容
            print("📥 步骤 1: 提取论文内容...")
            paper_content = self.extractor.extract(arxiv_id, title)
            
            # 2. 生成深度解读
            print("\n🧠 步骤 2: 生成深度解读...")
            insight = self.generator.generate_deep_insight(paper_content)
            
            if not insight:
                print("  ❌ 解读生成失败")
                self.stats["failed"] += 1
                return False
            
            # 3. 生成 Markdown
            print("\n📝 步骤 3: 生成 Markdown...")
            markdown = self.generator.generate_markdown(paper_content, insight)
            
            # 4. 保存 Markdown
            output_dir = self.base_dir / "insights_enhanced"
            output_dir.mkdir(parents=True, exist_ok=True)
            today = datetime.now().strftime("%Y-%m-%d")
            md_file = output_dir / f"{today}_{arxiv_id}.md"
            
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            print(f"  ✅ Markdown: {md_file}")
            
            # 5. 生成 HTML
            print("\n🌐 步骤 4: 生成 HTML...")
            html = generate_insight_page(markdown, arxiv_id, title)
            
            html_dir = self.base_dir / "docs" / "insights"
            html_dir.mkdir(parents=True, exist_ok=True)
            html_file = html_dir / f"{today}_{arxiv_id}.html"
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"  ✅ HTML: {html_file}")
            
            self.stats["processed"] += 1
            return True
            
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            self.stats["failed"] += 1
            return False
    
    def run(self, limit: int = None, start_from: int = 0):
        """运行批量处理"""
        print("\n" + "="*60)
        print("🚀 批量论文处理任务")
        print("="*60)
        
        # 加载进度
        progress = self.load_progress()
        processed_ids = set(progress.get("processed_ids", []))
        failed_ids = set(progress.get("failed_ids", []))
        
        print(f"📋 历史已处理: {len(processed_ids)} 篇")
        print(f"📋 历史失败: {len(failed_ids)} 篇")
        
        # 获取所有论文
        papers = self.get_all_papers()
        self.stats["total"] = len(papers)
        
        # 过滤已处理的
        pending_papers = []
        for p in papers:
            arxiv_id = p.get("arxiv_id", p.get("id", ""))
            if arxiv_id and arxiv_id not in processed_ids:
                pending_papers.append(p)
        
        print(f"\n📊 总论文: {len(papers)} 篇")
        print(f"📊 待处理: {len(pending_papers)} 篇")
        
        if limit:
            pending_papers = pending_papers[start_from:start_from+limit]
            print(f"   本次处理: {len(pending_papers)} 篇 (从第 {start_from+1} 篇开始)")
        
        if not pending_papers:
            print("\n✅ 没有待处理的论文")
            return
        
        # 处理论文
        for i, paper in enumerate(pending_papers):
            arxiv_id = paper.get("arxiv_id", paper.get("id", ""))
            print(f"\n进度: {i+1}/{len(pending_papers)}")
            
            success = self.process_paper(paper)
            
            # 更新进度
            if success:
                processed_ids.add(arxiv_id)
            else:
                failed_ids.add(arxiv_id)
            
            # 每 5 篇保存一次进度
            if (i + 1) % 5 == 0:
                progress["processed_ids"] = list(processed_ids)
                progress["failed_ids"] = list(failed_ids)
                self.save_progress(progress)
            
            # 避免API限流
            if i < len(pending_papers) - 1:
                time.sleep(2)
        
        # 最终保存进度
        progress["processed_ids"] = list(processed_ids)
        progress["failed_ids"] = list(failed_ids)
        progress["stats"] = self.stats
        self.save_progress(progress)
        
        # 输出统计
        print("\n" + "="*60)
        print("📊 处理完成统计")
        print("="*60)
        print(f"  本次处理: {len(pending_papers)} 篇")
        print(f"  成功: {self.stats['processed']} 篇")
        print(f"  失败: {self.stats['failed']} 篇")
        print(f"  跳过: {self.stats['skipped']} 篇")
        print(f"  累计已处理: {len(processed_ids)} 篇")
        print("="*60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="批量论文处理")
    parser.add_argument("--limit", type=int, default=None, help="处理数量限制")
    parser.add_argument("--start", type=int, default=0, help="起始位置")
    
    args = parser.parse_args()
    
    processor = BatchProcessor()
    processor.run(limit=args.limit, start_from=args.start)


if __name__ == "__main__":
    main()
