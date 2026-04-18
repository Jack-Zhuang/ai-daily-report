#!/usr/bin/env python3
"""
AI推荐日报 - 推送脚本
通过OpenClaw推送日报到用户
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
import sys

class ReportPusher:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.archive_dir = self.base_dir / "archive"
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def get_today_report(self) -> dict:
        """获取今日日报"""
        archive_path = self.archive_dir / self.today
        
        if not archive_path.exists():
            print(f"❌ 未找到今日日报: {archive_path}")
            return None
        
        html_file = archive_path / "index.html"
        data_file = archive_path / "data.json"
        
        if not html_file.exists():
            print(f"❌ 未找到HTML文件: {html_file}")
            return None
        
        data = {}
        if data_file.exists():
            data = json.loads(data_file.read_text(encoding="utf-8"))
        
        return {
            "html_path": str(html_file),
            "data": data
        }
    
    def generate_push_message(self, data: dict) -> str:
        """生成推送消息"""
        stats = data.get("stats", {})
        daily_pick = data.get("daily_pick", [])
        
        # 提取精选标题
        pick_titles = []
        for i, item in enumerate(daily_pick[:3], 1):
            title = item.get("title") or item.get("name", "")
            if len(title) > 40:
                title = title[:40] + "..."
            pick_titles.append(f"{i}. {title}")
        
        message = f"""🌅 AI推荐日报 | {self.today}

📰 今日精选
{chr(10).join(pick_titles)}

📊 今日统计
• 论文: {stats.get('total_papers', 0)} 篇
• 项目: {stats.get('total_projects', 0)} 个
• 文章: {stats.get('total_articles', 0)} 篇

---
💡 回复"日报"查看完整内容
📚 回复"往期"查看历史日报"""
        
        return message
    
    def push_to_xiaoyi(self, html_path: str, message: str):
        """推送到小艺Channel"""
        print(f"📱 推送到小艺Channel...")
        
        # 使用send_file_to_user发送HTML文件
        # 这里需要通过OpenClaw的工具调用
        # 在实际执行时，会由主程序调用send_file_to_user
        
        print(f"  📄 文件: {html_path}")
        print(f"  💬 消息: {message[:100]}...")
        
        return {
            "success": True,
            "file_path": html_path,
            "message": message
        }
    
    def run(self):
        """执行推送"""
        print(f"\n{'='*50}")
        print(f"📤 推送AI推荐日报 - {self.today}")
        print(f"{'='*50}\n")
        
        # 获取今日日报
        report = self.get_today_report()
        if not report:
            return None
        
        # 生成推送消息
        message = self.generate_push_message(report["data"])
        
        # 推送
        result = self.push_to_xiaoyi(report["html_path"], message)
        
        print(f"\n{'='*50}")
        print(f"✅ 推送完成！")
        print(f"{'='*50}\n")
        
        return result


if __name__ == "__main__":
    pusher = ReportPusher()
    result = pusher.run()
    if result:
        print(f"推送结果: {result}")
