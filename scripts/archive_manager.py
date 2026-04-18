#!/usr/bin/env python3
"""
AI推荐日报 - 归档管理脚本
管理历史日报，支持查看、列表、删除等操作
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

class ArchiveManager:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.archive_dir = self.base_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)
    
    def list_reports(self, limit: int = 30) -> list:
        """列出最近的日报"""
        reports = []
        
        for daily_dir in sorted(self.archive_dir.iterdir(), reverse=True):
            if daily_dir.is_dir() and daily_dir.name != "index.json":
                data_file = daily_dir / "data.json"
                if data_file.exists():
                    try:
                        data = json.loads(data_file.read_text(encoding="utf-8"))
                        reports.append({
                            "date": daily_dir.name,
                            "total_papers": data.get("stats", {}).get("total_papers", 0),
                            "total_projects": data.get("stats", {}).get("total_projects", 0),
                            "total_articles": data.get("stats", {}).get("total_articles", 0),
                            "daily_pick_count": len(data.get("daily_pick", [])),
                            "has_html": (daily_dir / "index.html").exists()
                        })
                    except:
                        pass
                
                if len(reports) >= limit:
                    break
        
        return reports
    
    def get_report(self, date: str) -> dict:
        """获取指定日期的日报"""
        archive_path = self.archive_dir / date
        
        if not archive_path.exists():
            return None
        
        result = {"date": date}
        
        html_file = archive_path / "index.html"
        if html_file.exists():
            result["html"] = html_file.read_text(encoding="utf-8")
            result["html_path"] = str(html_file)
        
        data_file = archive_path / "data.json"
        if data_file.exists():
            result["data"] = json.loads(data_file.read_text(encoding="utf-8"))
        
        return result
    
    def get_latest_report(self) -> dict:
        """获取最新日报"""
        reports = self.list_reports(limit=1)
        if reports:
            return self.get_report(reports[0]["date"])
        return None
    
    def generate_archive_index(self):
        """生成归档索引页面"""
        reports = self.list_reports(limit=90)
        
        if not reports:
            return None
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <title>往期日报 | AI推荐日报</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        :root {{
            --color-text-anchor: #312C51;
            --color-text-secondary: rgba(49,44,81,0.68);
            --color-text-muted: rgba(49,44,81,0.40);
            --color-card: #FFFFFF;
            --bg: #FAFAFA;
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, sans-serif; background: var(--bg); color: var(--color-text-anchor); }}
        
        .header {{
            background: var(--gradient-primary); color: white;
            padding: 60px 16px 30px; text-align: center;
        }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .header p {{ font-size: 13px; opacity: 0.9; }}
        
        .main {{ padding: 20px 12px 60px; max-width: 600px; margin: 0 auto; }}
        
        .report-card {{
            background: var(--color-card); border-radius: 14px;
            padding: 16px; margin-bottom: 12px;
            box-shadow: 0 2px 12px rgba(49,44,81,0.06);
            display: flex; align-items: center; justify-content: space-between;
            text-decoration: none; color: inherit;
        }}
        .report-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 16px rgba(49,44,81,0.1); }}
        
        .report-date {{ font-size: 16px; font-weight: 700; margin-bottom: 4px; }}
        .report-stats {{ font-size: 12px; color: var(--color-text-muted); }}
        .report-stats span {{ margin-right: 12px; }}
        
        .report-link {{
            background: var(--gradient-primary); color: white;
            padding: 8px 16px; border-radius: 10px;
            font-size: 12px; font-weight: 700; text-decoration: none;
        }}
        
        .back-link {{
            display: block; text-align: center;
            padding: 16px; color: var(--color-text-secondary);
            text-decoration: none; font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-history"></i> 往期日报</h1>
        <p>共 {len(reports)} 期日报</p>
    </div>
    
    <div class="main">
        {"".join([f'''
        <a href="../{r["date"]}/index.html" class="report-card">
            <div>
                <div class="report-date">{r["date"]}</div>
                <div class="report-stats">
                    <span><i class="fas fa-file-alt"></i> {r["total_papers"]}篇论文</span>
                    <span><i class="fab fa-github"></i> {r["total_projects"]}个项目</span>
                    <span><i class="fas fa-star"></i> {r["daily_pick_count"]}篇精选</span>
                </div>
            </div>
            <span class="report-link">查看</span>
        </a>
        ''' for r in reports])}
        
        <a href="../index.html" class="back-link">
            <i class="fas fa-arrow-left"></i> 返回今日日报
        </a>
    </div>
</body>
</html>'''
        
        index_file = self.archive_dir / "archive.html"
        index_file.write_text(html, encoding="utf-8")
        
        return str(index_file)
    
    def print_list(self, limit: int = 10):
        """打印日报列表"""
        reports = self.list_reports(limit=limit)
        
        print(f"\n📚 往期日报列表（最近{len(reports)}期）\n")
        print(f"{'日期':<12} {'论文':<6} {'项目':<6} {'精选':<6}")
        print("-" * 40)
        
        for r in reports:
            print(f"{r['date']:<12} {r['total_papers']:<6} {r['total_projects']:<6} {r['daily_pick_count']:<6}")
        
        print()


if __name__ == "__main__":
    manager = ArchiveManager()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "list":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            manager.print_list(limit=limit)
        
        elif cmd == "get":
            if len(sys.argv) > 2:
                date = sys.argv[2]
                report = manager.get_report(date)
                if report:
                    print(f"日报: {date}")
                    print(f"HTML: {report.get('html_path', 'N/A')}")
                else:
                    print(f"未找到 {date} 的日报")
            else:
                print("用法: python archive_manager.py get YYYY-MM-DD")
        
        elif cmd == "index":
            index_path = manager.generate_archive_index()
            print(f"归档索引已生成: {index_path}")
        
        else:
            print("用法:")
            print("  python archive_manager.py list [limit]  - 列出往期日报")
            print("  python archive_manager.py get <date>    - 获取指定日期日报")
            print("  python archive_manager.py index         - 生成归档索引页面")
    else:
        manager.print_list()
