#!/usr/bin/env python3
"""
AI推荐日报 - 完整配置检查和修复脚本
检查所有模块的配置，确保系统完整可用
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime


class ConfigChecker:
    """配置检查器"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.issues = []
        self.fixed = []

    def check_all(self):
        """检查所有配置"""
        print("=" * 60)
        print("🔍 AI推荐日报 - 配置完整性检查")
        print("=" * 60)
        print()

        # 1. 检查目录结构
        self.check_directories()

        # 2. 检查配置文件
        self.check_config_files()

        # 3. 检查数据文件
        self.check_data_files()

        # 4. 检查 API 配置
        self.check_api_config()

        # 5. 检查脚本文件
        self.check_scripts()

        # 6. 检查报告文件
        self.check_reports()

        # 输出结果
        self.print_results()

    def check_directories(self):
        """检查目录结构"""
        print("📁 检查目录结构...")

        required_dirs = [
            "daily_data",
            "covers",
            "insights_enhanced",
            "docs",
            "docs/insights",
            "archive",
            "logs",
            "paper_cache",
            "cache",
            "config",
            "scripts",
            "scripts/enhanced",
            "conferences",
        ]

        for dir_name in required_dirs:
            dir_path = self.base_dir / dir_name
            if not dir_path.exists():
                print(f"  ❌ 缺失: {dir_name}")
                self.issues.append(f"目录缺失: {dir_name}")
                # 创建目录
                dir_path.mkdir(parents=True, exist_ok=True)
                self.fixed.append(f"已创建目录: {dir_name}")
            else:
                print(f"  ✅ {dir_name}")

    def check_config_files(self):
        """检查配置文件"""
        print("\n⚙️ 检查配置文件...")

        # 主配置文件
        config_file = self.base_dir / "config" / "config.yaml"
        if config_file.exists():
            print(f"  ✅ config.yaml")
        else:
            print(f"  ❌ 缺失: config.yaml")
            self.issues.append("配置文件缺失: config.yaml")
            self.create_default_config()

        # 数据源配置
        sources_file = self.base_dir / "config" / "sources.json"
        if not sources_file.exists():
            print(f"  ⚠️ 缺失: sources.json (将创建默认配置)")
            self.create_default_sources()

        # 微信账号配置
        wechat_file = self.base_dir / "config" / "wechat_accounts.json"
        if wechat_file.exists():
            print(f"  ✅ wechat_accounts.json")
        else:
            print(f"  ⚠️ 缺失: wechat_accounts.json")

    def check_data_files(self):
        """检查数据文件"""
        print("\n📊 检查数据文件...")

        today = datetime.now().strftime("%Y-%m-%d")
        data_file = self.base_dir / "daily_data" / f"{today}.json"

        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"  ✅ 今日数据: {data_file.name}")

            # 检查各部分数据
            sections = {
                'daily_pick': '每日精选',
                'arxiv_papers': 'arXiv论文',
                'github_projects': 'GitHub项目',
                'hot_articles': '热门文章'
            }

            for key, name in sections.items():
                count = len(data.get(key, []))
                status = "✅" if count > 0 else "⚠️"
                print(f"     {status} {name}: {count} 条")

                if count == 0 and key != 'hot_articles':  # 热门文章可以为空
                    self.issues.append(f"{name}数据为空")
        else:
            print(f"  ❌ 今日数据文件不存在: {data_file.name}")
            self.issues.append("今日数据文件不存在")

    def check_api_config(self):
        """检查 API 配置"""
        print("\n🔑 检查 API 配置...")

        # 检查 .xiaoyienv 文件
        env_file = Path.home() / ".openclaw" / ".xiaoyienv"
        if env_file.exists():
            print(f"  ✅ .xiaoyienv 文件存在")

            # 检查必要的配置项
            with open(env_file, 'r') as f:
                content = f.read()

            required_keys = [
                'PERSONAL-API-KEY',
                'PERSONAL-UID',
                'SERVICE_URL'
            ]

            for key in required_keys:
                if key in content:
                    print(f"     ✅ {key}")
                else:
                    print(f"     ❌ 缺失: {key}")
                    self.issues.append(f"API配置缺失: {key}")
        else:
            print(f"  ❌ .xiaoyienv 文件不存在")
            self.issues.append("API配置文件不存在")

        # 检查 MiniMax API Key
        minimax_key = os.environ.get('MINIMAX_API_KEY', '')
        if minimax_key:
            print(f"  ✅ MINIMAX_API_KEY 已配置")
        else:
            print(f"  ⚠️ MINIMAX_API_KEY 未配置（可选）")

    def check_scripts(self):
        """检查脚本文件"""
        print("\n📜 检查脚本文件...")

        required_scripts = [
            "scripts/collect_daily.py",
            "scripts/generate_report.py",
            "scripts/batch_generate_covers.py",
            "scripts/select_daily_pick.py",
            "scripts/run_daily.py",
            "scripts/enhanced/batch_processor.py",
            "scripts/enhanced/paper_extractor.py",
            "scripts/enhanced/insight_generator.py",
        ]

        for script in required_scripts:
            script_path = self.base_dir / script
            if script_path.exists():
                print(f"  ✅ {script}")
            else:
                print(f"  ❌ 缺失: {script}")
                self.issues.append(f"脚本缺失: {script}")

    def check_reports(self):
        """检查报告文件"""
        print("\n📄 检查报告文件...")

        # 主报告
        index_file = self.base_dir / "docs" / "index.html"
        if index_file.exists():
            size = index_file.stat().st_size
            print(f"  ✅ 主报告: {size//1024}KB")
        else:
            print(f"  ❌ 主报告不存在")
            self.issues.append("主报告文件不存在")

        # 论文解读页面
        insights_dir = self.base_dir / "docs" / "insights"
        if insights_dir.exists():
            count = len(list(insights_dir.glob("*.html")))
            print(f"  ✅ 论文解读页面: {count} 个")
        else:
            print(f"  ⚠️ 论文解读目录不存在")

        # 封面图
        covers_dir = self.base_dir / "covers"
        if covers_dir.exists():
            count = len(list(covers_dir.glob("*.jpg")))
            valid_count = len([f for f in covers_dir.glob("*.jpg") if f.stat().st_size > 10000])
            print(f"  ✅ 封面图: {count} 个 (有效: {valid_count} 个)")
        else:
            print(f"  ⚠️ 封面图目录不存在")

    def create_default_config(self):
        """创建默认配置文件"""
        config_content = """# AI推荐日报配置文件

collection:
  schedule: "0 6 * * *"
  arxiv:
    enabled: true
    categories: [cs.IR, cs.AI, cs.LG, cs.CL]
    max_results: 50
  github:
    enabled: true
    max_results: 30
  conferences:
    enabled: true

generation:
  schedule: "30 8 * * *"
  daily_pick_count: 5
  hot_articles_count: 8
  github_count: 6

push:
  schedule: "0 9 * * *"
  channels: [xiaoyi-channel]

archive:
  retention_days: 90
  directory: ./archive

logging:
  level: INFO
  file: ./logs/ai_daily.log
"""
        config_file = self.base_dir / "config" / "config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        self.fixed.append("已创建默认配置文件: config.yaml")

    def create_default_sources(self):
        """创建默认数据源配置"""
        sources = {
            "arxiv": {
                "enabled": True,
                "categories": ["cs.IR", "cs.AI", "cs.LG", "cs.CL"],
                "max_results": 50,
                "sort_by": "submittedDate"
            },
            "github": {
                "enabled": True,
                "languages": ["Python", "JavaScript", "TypeScript"],
                "since": "daily",
                "topics": ["recommendation-system", "llm", "ai-agent"]
            },
            "wechat": {
                "enabled": True,
                "accounts": ["机器之心", "量子位", "InfoQ"],
                "rsshub_url": "http://localhost:1200"
            },
            "articles": {
                "enabled": True,
                "sources": [
                    "https://www.infoq.cn",
                    "https://www.jiqizhixin.com"
                ]
            }
        }

        sources_file = self.base_dir / "config" / "sources.json"
        with open(sources_file, 'w', encoding='utf-8') as f:
            json.dump(sources, f, ensure_ascii=False, indent=2)
        self.fixed.append("已创建默认数据源配置: sources.json")

    def print_results(self):
        """输出检查结果"""
        print("\n" + "=" * 60)
        print("📋 检查结果")
        print("=" * 60)

        if self.issues:
            print(f"\n⚠️ 发现 {len(self.issues)} 个问题:")
            for issue in self.issues:
                print(f"  - {issue}")
        else:
            print("\n✅ 所有检查通过！")

        if self.fixed:
            print(f"\n🔧 已修复 {len(self.fixed)} 个问题:")
            for fix in self.fixed:
                print(f"  - {fix}")

        print("\n" + "=" * 60)


def main():
    checker = ConfigChecker()
    checker.check_all()


if __name__ == "__main__":
    main()
