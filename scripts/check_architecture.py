#!/usr/bin/env python3
"""
AI推荐日报 - 架构完整性检查
检查所有模块是否正确实现
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

class ArchitectureChecker:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.scripts_dir = self.base_dir / "scripts"
        self.data_dir = self.base_dir / "daily_data"
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.results = {}
        
    def check_module(self, name: str, description: str, scripts: list, data_check: str = None) -> dict:
        """检查单个模块"""
        result = {
            "name": name,
            "description": description,
            "scripts_exist": [],
            "scripts_missing": [],
            "data_ok": False,
            "status": "❌"
        }
        
        # 检查脚本是否存在
        for script in scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                result["scripts_exist"].append(script)
            else:
                result["scripts_missing"].append(script)
        
        # 检查数据
        if data_check:
            data_file = self.data_dir / f"{self.today}.json"
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                parts = data_check.split('.')
                value = data
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part, [])
                    else:
                        value = []
                        break
                result["data_ok"] = len(value) > 0 if isinstance(value, list) else bool(value)
                result["data_count"] = len(value) if isinstance(value, list) else 1
        
        # 判断状态
        if result["scripts_exist"] and (result["data_ok"] if data_check else True):
            result["status"] = "✅"
        elif result["scripts_exist"]:
            result["status"] = "⚠️"
        
        return result
    
    def run_all_checks(self):
        """运行所有检查"""
        print("=" * 70)
        print("🔍 AI推荐日报 - 架构完整性检查")
        print("=" * 70)
        print(f"📅 日期: {self.today}")
        print()
        
        # 定义所有模块
        modules = [
            # 采集模块
            {
                "name": "热门文章采集",
                "description": "从公众号、知乎、技术博客采集热门文章",
                "scripts": ["collect_articles.py", "collect_hot_articles.py"],
                "data_check": "articles"
            },
            {
                "name": "GitHub Trending 采集",
                "description": "采集 GitHub 热门项目和趋势",
                "scripts": ["collect_github.py"],
                "data_check": "github"
            },
            {
                "name": "arXiv 新论文采集",
                "description": "采集 arXiv 最新论文",
                "scripts": ["collect_daily.py"],
                "data_check": "arxiv_papers"
            },
            {
                "name": "顶会论文采集",
                "description": "采集顶会论文（WSDM/KDD/RecSys等）",
                "scripts": ["collect_conference_papers.py", "collect_conferences.py"],
                "data_check": "conferences"
            },
            
            # 处理模块
            {
                "name": "每日精选构建",
                "description": "从采集内容中选择每日精选（3文章+1论文+1GitHub）",
                "scripts": ["build_daily_pick.py", "select_daily_pick.py"],
                "data_check": "daily_pick"
            },
            {
                "name": "标题翻译",
                "description": "翻译英文标题为中文",
                "scripts": ["translator.py", "translate_papers.py"],
                "data_check": None
            },
            {
                "name": "摘要翻译",
                "description": "翻译英文摘要为中文",
                "scripts": ["translator.py"],
                "data_check": None
            },
            
            # 生成模块
            {
                "name": "AI 封面生成",
                "description": "基于内容生成相关封面图",
                "scripts": ["generate_covers_v2.py", "generate_covers_enhanced.py"],
                "data_check": None
            },
            {
                "name": "论文深度解读",
                "description": "生成论文深度解读（技术博客风格）",
                "scripts": ["generate_paper_insights.py"],
                "data_check": None
            },
            {
                "name": "解读页面生成",
                "description": "生成论文解读 HTML 页面",
                "scripts": ["generate_insights.py"],
                "data_check": None
            },
            {
                "name": "日报 HTML 生成",
                "description": "生成主报告 HTML 页面",
                "scripts": ["generate_report.py"],
                "data_check": None
            },
            
            # 检查模块
            {
                "name": "规则检查",
                "description": "检查数据是否符合规则",
                "scripts": ["check_rules.py"],
                "data_check": None
            },
            {
                "name": "QA 检查",
                "description": "质量保证检查",
                "scripts": ["qa_check.py"],
                "data_check": None
            },
            
            # 部署模块
            {
                "name": "自动部署",
                "description": "Git 提交并推送到 GitHub Pages",
                "scripts": ["push_report.py", "generate_and_deploy.py"],
                "data_check": None
            },
            {
                "name": "定时调度",
                "description": "定时任务调度器",
                "scripts": ["schedule_daily.py", "run_daily.py"],
                "data_check": None
            },
        ]
        
        # 执行检查
        results = []
        for module in modules:
            result = self.check_module(
                module["name"],
                module["description"],
                module["scripts"],
                module.get("data_check")
            )
            results.append(result)
        
        # 输出结果
        print("-" * 70)
        print(f"{'模块':<20} {'状态':<6} {'脚本':<30} {'数据':<10}")
        print("-" * 70)
        
        for r in results:
            scripts_str = f"{len(r['scripts_exist'])}/{len(r['scripts_exist'])+len(r['scripts_missing'])}"
            data_str = f"✅ {r.get('data_count', 'N/A')}" if r.get('data_ok') else ("❌" if 'data_check' in r else "-")
            print(f"{r['name']:<20} {r['status']:<6} {scripts_str:<30} {data_str:<10}")
        
        print("-" * 70)
        
        # 统计
        passed = sum(1 for r in results if r["status"] == "✅")
        warned = sum(1 for r in results if r["status"] == "⚠️")
        failed = sum(1 for r in results if r["status"] == "❌")
        
        print(f"\n📊 统计: ✅ {passed} | ⚠️ {warned} | ❌ {failed}")
        
        # 详细问题
        issues = [r for r in results if r["status"] != "✅"]
        if issues:
            print("\n⚠️ 需要关注的问题:")
            for r in issues:
                print(f"\n  【{r['name']}】")
                if r["scripts_missing"]:
                    print(f"    缺失脚本: {', '.join(r['scripts_missing'])}")
                if not r.get("data_ok") and "data_check" in r:
                    print(f"    数据问题: 无数据或数据为空")
        
        print("\n" + "=" * 70)
        
        return failed == 0


if __name__ == "__main__":
    checker = ArchitectureChecker()
    success = checker.run_all_checks()
    exit(0 if success else 1)
