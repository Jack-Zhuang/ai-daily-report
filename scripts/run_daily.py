#!/usr/bin/env python3
"""
AI推荐日报 - 一键生成脚本
完整流程：采集 → 处理 → 生成 → 检查
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class DailyReportRunner:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.scripts_dir = self.base_dir / "scripts"
        self.data_dir = self.base_dir / "daily_data"
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def run_command(self, cmd: str, desc: str) -> bool:
        """运行命令"""
        print(f"\n{'='*50}")
        print(f"📌 {desc}")
        print(f"{'='*50}")
        
        result = subprocess.run(cmd, shell=True, cwd=self.base_dir)
        
        if result.returncode == 0:
            print(f"✅ {desc} 完成")
            return True
        else:
            print(f"❌ {desc} 失败")
            return False
    
    def step1_collect(self):
        """步骤1: 采集内容"""
        print("\n" + "="*60)
        print("🚀 步骤1: 内容采集")
        print("="*60)
        
        # 采集 arXiv 论文
        print("\n📡 采集 arXiv 论文...")
        cmd = f"python3 {self.scripts_dir / 'collect_daily.py'}"
        self.run_command(cmd, "采集 arXiv 论文")
        
        # 采集文章（如果有脚本）
        articles_script = self.scripts_dir / "collect_articles.py"
        if articles_script.exists():
            print("\n📡 采集文章...")
            cmd = f"python3 {articles_script}"
            self.run_command(cmd, "采集文章")
        
        return True
    
    def step2_process(self):
        """步骤2: 处理内容"""
        print("\n" + "="*60)
        print("🔧 步骤2: 内容处理")
        print("="*60)
        
        # 加载数据
        data_file = self.data_dir / f"{self.today}.json"
        if not data_file.exists():
            # 尝试昨天的数据
            from datetime import timedelta
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            data_file = self.data_dir / f"{yesterday}.json"
            if not data_file.exists():
                print("❌ 未找到数据文件")
                return False
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"加载数据: {data_file.name}")
        
        # 处理论文（翻译标题和摘要）
        print("\n📝 处理论文...")
        for paper in data.get('arxiv_papers', []):
            if not paper.get('cn_title'):
                paper['cn_title'] = paper.get('title', '')
            if not paper.get('cn_summary'):
                paper['cn_summary'] = paper.get('summary', '')[:200]
        
        # 处理每日精选
        print("📝 处理每日精选...")
        for item in data.get('daily_pick', []):
            if not item.get('cn_title'):
                item['cn_title'] = item.get('title', item.get('name', ''))
            if not item.get('cn_summary'):
                item['cn_summary'] = item.get('summary', item.get('description', ''))[:200]
        
        # 处理热门文章
        print("📝 处理热门文章...")
        for item in data.get('hot_articles', []):
            if not item.get('cn_title'):
                item['cn_title'] = item.get('title', '')
            if not item.get('cn_summary'):
                item['cn_summary'] = item.get('summary', '')[:200]
        
        # 保存
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据处理完成")
        return True
    
    def step3_generate(self):
        """步骤3: 生成页面"""
        print("\n" + "="*60)
        print("🎨 步骤3: 页面生成")
        print("="*60)
        
        # 生成日报
        cmd = f"python3 {self.scripts_dir / 'generate_report.py'}"
        if not self.run_command(cmd, "生成日报"):
            return False
        
        # 生成论文解读页面
        insights_script = self.scripts_dir / "generate_insights.py"
        if insights_script.exists():
            cmd = f"python3 {insights_script}"
            self.run_command(cmd, "生成论文解读页面")
        
        return True
    
    def step4_check(self):
        """步骤4: 规则检查"""
        print("\n" + "="*60)
        print("✅ 步骤4: 规则检查")
        print("="*60)
        
        cmd = f"python3 {self.scripts_dir / 'check_rules.py'}"
        result = subprocess.run(cmd, shell=True, cwd=self.base_dir)
        
        return result.returncode == 0
    
    def step5_deploy(self):
        """步骤5: 部署"""
        print("\n" + "="*60)
        print("🚀 步骤5: 部署")
        print("="*60)
        
        # Git 提交
        print("\n📦 提交到 Git...")
        subprocess.run("git add -A", shell=True, cwd=self.base_dir)
        subprocess.run(f'git commit -m "更新日报 {self.today}"', shell=True, cwd=self.base_dir)
        subprocess.run("git push", shell=True, cwd=self.base_dir)
        
        print("\n✅ 部署完成!")
        print(f"🌐 访问: https://jack-zhuang.github.io/ai-daily-report/")
        
        return True
    
    def run(self, steps: list = None):
        """运行完整流程"""
        if steps is None:
            steps = ['collect', 'process', 'generate', 'check', 'deploy']
        
        print("="*60)
        print(f"🚀 AI推荐日报 - 一键生成")
        print(f"📅 日期: {self.today}")
        print("="*60)
        
        step_map = {
            'collect': self.step1_collect,
            'process': self.step2_process,
            'generate': self.step3_generate,
            'check': self.step4_check,
            'deploy': self.step5_deploy
        }
        
        for step in steps:
            if step in step_map:
                if not step_map[step]():
                    print(f"\n❌ 流程在 {step} 步骤失败")
                    return False
        
        print("\n" + "="*60)
        print("🎉 全部完成!")
        print("="*60)
        return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AI推荐日报一键生成')
    parser.add_argument('--steps', nargs='+', 
                       default=['collect', 'process', 'generate', 'check'],
                       help='要执行的步骤')
    parser.add_argument('--skip-collect', action='store_true', help='跳过采集')
    parser.add_argument('--skip-deploy', action='store_true', help='跳过部署')
    
    args = parser.parse_args()
    
    steps = args.steps
    if args.skip_collect and 'collect' in steps:
        steps.remove('collect')
    if args.skip_deploy and 'deploy' in steps:
        steps.remove('deploy')
    
    runner = DailyReportRunner()
    success = runner.run(steps)
    
    sys.exit(0 if success else 1)
