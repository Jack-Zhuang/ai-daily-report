#!/usr/bin/env python3
"""
AI推荐日报 - 定时调度器
每天早上 6:00 开始采集，8:30 生成报告，9:00 发布
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

class DailyScheduler:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.scripts_dir = self.base_dir / "scripts"
        self.log_dir = self.base_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # 写入日志文件
        log_file = self.log_dir / f"schedule_{datetime.now().strftime('%Y-%m-%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def run_step(self, name: str, cmd: str, timeout: int = 3600) -> bool:
        """执行单个步骤"""
        self.log(f"开始: {name}")
        self.log(f"命令: {cmd}")
        
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                cwd=self.base_dir,
                timeout=timeout,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log(f"✅ 完成: {name}")
                return True
            else:
                self.log(f"❌ 失败: {name}")
                self.log(f"错误: {result.stderr[:500]}")
                return False
        except subprocess.TimeoutExpired:
            self.log(f"⏰ 超时: {name} (>{timeout}秒)")
            return False
        except Exception as e:
            self.log(f"❌ 异常: {name} - {str(e)}")
            return False
    
    def run_full_pipeline(self):
        """运行完整流程"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.log("=" * 60)
        self.log(f"🚀 AI推荐日报 - 自动化流程")
        self.log(f"📅 日期: {today}")
        self.log("=" * 60)
        
        # 步骤1: 采集内容 (预计 30 分钟)
        self.log("\n" + "=" * 60)
        self.log("📥 步骤1: 内容采集")
        self.log("=" * 60)
        
        steps = [
            ("采集 arXiv 论文", f"python3 {self.scripts_dir / 'collect_daily.py'}", 1800),
            ("采集 GitHub Trending", f"python3 {self.scripts_dir / 'collect_github.py'}", 600),
            ("采集热门文章", f"python3 {self.scripts_dir / 'collect_articles.py'}", 600),
        ]
        
        for name, cmd, timeout in steps:
            if not self.run_step(name, cmd, timeout):
                self.log(f"⚠️ {name} 失败，继续执行...")
        
        # 步骤2: 处理内容 (预计 20 分钟)
        self.log("\n" + "=" * 60)
        self.log("🔧 步骤2: 内容处理")
        self.log("=" * 60)
        
        data_file = self.base_dir / "daily_data" / f"{today}.json"
        
        steps = [
            ("构建每日精选", f"python3 {self.scripts_dir / 'build_daily_pick.py'} {data_file}", 300),
            ("功能增强", f"python3 {self.scripts_dir / 'enhance_features.py'}", 300),
            ("翻译内容", f"python3 {self.scripts_dir / 'translate_papers.py'}", 1200),
        ]
        
        for name, cmd, timeout in steps:
            if not self.run_step(name, cmd, timeout):
                self.log(f"⚠️ {name} 失败，继续执行...")
        
        # 步骤3: 生成封面 (预计 30 分钟)
        self.log("\n" + "=" * 60)
        self.log("🎨 步骤3: 封面生成")
        self.log("=" * 60)
        
        self.run_step(
            "生成 AI 封面", 
            f"python3 {self.scripts_dir / 'generate_covers_v2.py'}", 
            1800
        )
        
        # 步骤4: 生成报告 (预计 5 分钟)
        self.log("\n" + "=" * 60)
        self.log("📄 步骤4: 报告生成")
        self.log("=" * 60)
        
        steps = [
            ("生成日报 HTML", f"python3 {self.scripts_dir / 'generate_report.py'}", 300),
            ("生成论文深度解读", f"python3 {self.scripts_dir / 'generate_paper_insights.py'}", 1800),
            ("生成解读 HTML 页面", f"python3 {self.scripts_dir / 'generate_insights.py'}", 600),
        ]
        
        for name, cmd, timeout in steps:
            if not self.run_step(name, cmd, timeout):
                self.log(f"⚠️ {name} 失败，继续执行...")
        
        # 步骤5: 质量检查 (预计 1 分钟)
        self.log("\n" + "=" * 60)
        self.log("✅ 步骤5: 质量检查")
        self.log("=" * 60)
        
        self.run_step(
            "规则检查", 
            f"python3 {self.scripts_dir / 'check_rules.py'}", 
            60
        )
        
        # 步骤6: 部署 (预计 2 分钟)
        self.log("\n" + "=" * 60)
        self.log("🚀 步骤6: 部署发布")
        self.log("=" * 60)
        
        self.run_step(
            "Git 提交并推送", 
            f"cd {self.base_dir} && git add -A && git commit -m '自动更新日报 {today}' && git push", 
            120
        )
        
        self.log("\n" + "=" * 60)
        self.log("🎉 自动化流程完成!")
        self.log(f"🌐 访问: https://jack-zhuang.github.io/ai-daily-report/")
        self.log("=" * 60)
        
        return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='AI推荐日报定时调度器')
    parser.add_argument('--now', action='store_true', help='立即执行（不等待定时）')
    parser.add_argument('--time', type=str, default='06:00', help='执行时间（默认 06:00）')
    
    args = parser.parse_args()
    
    scheduler = DailyScheduler()
    
    if args.now:
        # 立即执行
        scheduler.run_full_pipeline()
    else:
        # 等待到指定时间
        target_time = datetime.strptime(args.time, '%H:%M').time()
        now = datetime.now()
        target = datetime.combine(now.date(), target_time)
        
        if target <= now:
            # 如果目标时间已过，设置为明天
            target += timedelta(days=1)
        
        wait_seconds = (target - now).total_seconds()
        
        print(f"⏰ 等待到 {target.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   还有 {int(wait_seconds // 3600)} 小时 {int((wait_seconds % 3600) // 60)} 分钟")
        
        time.sleep(wait_seconds)
        scheduler.run_full_pipeline()


if __name__ == "__main__":
    main()
