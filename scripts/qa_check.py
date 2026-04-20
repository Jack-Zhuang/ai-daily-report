#!/usr/bin/env python3
"""
AI推荐日报 - 质量保证检查脚本
全面检查系统各个层面的质量
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class QAChecker:
    """质量保证检查器"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)

        self.results = {
            "passed": [],
            "warnings": [],
            "failed": []
        }

    def check(self, verbose: bool = False) -> Dict:
        """执行全面检查"""
        print("\n" + "=" * 60)
        print("🔍 AI推荐日报 - 质量检查")
        print("=" * 60 + "\n")

        # 1. 数据层检查
        print("📊 数据层检查...")
        self._check_data_layer()

        # 2. 封面层检查
        print("\n🎨 封面层检查...")
        self._check_cover_layer()

        # 3. 报告层检查
        print("\n📄 报告层检查...")
        self._check_report_layer()

        # 4. 部署层检查
        print("\n🚀 部署层检查...")
        self._check_deployment_layer()

        # 5. 体验层检查
        print("\n✨ 体验层检查...")
        self._check_experience_layer()

        # 输出结果
        self._print_results(verbose)

        return self.results

    def _check_data_layer(self):
        """检查数据层"""
        # 查找最新数据文件
        data_dir = self.base_dir / "daily_data"
        data_files = sorted(data_dir.glob("*.json"), reverse=True)

        if not data_files:
            self.results["failed"].append(("数据文件", "未找到任何数据文件"))
            return

        latest_data_file = data_files[0]
        print(f"  检查文件: {latest_data_file.name}")

        with open(latest_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 检查各部分数据
        checks = [
            ('daily_pick', 5, '每日精选'),
            ('arxiv_papers', 40, 'arXiv论文'),
            ('github_projects', 10, 'GitHub项目'),
            ('articles', 20, '热门文章'),
        ]

        for key, min_count, name in checks:
            items = data.get(key, [])
            count = len(items)

            if count >= min_count:
                # 检查是否有封面
                with_cover = sum(1 for i in items if i.get('cover_image'))
                if with_cover == count:
                    self.results["passed"].append((
                        f"{name}数据",
                        f"{count}条，全部有封面"
                    ))
                elif with_cover > 0:
                    self.results["warnings"].append((
                        f"{name}数据",
                        f"{count}条，{with_cover}条有封面，{count-with_cover}条缺失"
                    ))
                else:
                    self.results["failed"].append((
                        f"{name}数据",
                        f"{count}条，无封面"
                    ))
            elif count > 0:
                self.results["warnings"].append((
                    f"{name}数据",
                    f"仅{count}条，建议至少{min_count}条"
                ))
            else:
                self.results["warnings"].append((
                    f"{name}数据",
                    "无数据"
                ))

    def _check_cover_layer(self):
        """检查封面层"""
        covers_dir = self.base_dir / "covers"

        if not covers_dir.exists():
            self.results["failed"].append(("封面目录", "不存在"))
            return

        # 统计封面
        all_covers = list(covers_dir.glob("*.jpg"))
        valid_covers = [f for f in all_covers if f.stat().st_size > 10000]
        invalid_covers = [f for f in all_covers if f.stat().st_size <= 10000]

        if len(all_covers) >= 90:
            if len(valid_covers) == len(all_covers):
                self.results["passed"].append((
                    "封面数量",
                    f"{len(all_covers)}个，全部有效"
                ))
            else:
                self.results["warnings"].append((
                    "封面质量",
                    f"{len(all_covers)}个，{len(invalid_covers)}个无效（<10KB）"
                ))
        else:
            self.results["warnings"].append((
                "封面数量",
                f"仅{len(all_covers)}个，建议至少90个"
            ))

    def _check_report_layer(self):
        """检查报告层"""
        # 主报告
        index_file = self.base_dir / "docs" / "index.html"
        if index_file.exists():
            size = index_file.stat().st_size
            if size > 100000:  # >100KB
                self.results["passed"].append(("主报告", f"{size//1024}KB"))
            else:
                self.results["warnings"].append(("主报告", f"仅{size//1024}KB，可能不完整"))
        else:
            self.results["failed"].append(("主报告", "不存在"))

        # 论文解读
        insights_dir = self.base_dir / "docs" / "insights"
        if insights_dir.exists():
            count = len(list(insights_dir.glob("*.html")))
            if count >= 50:
                self.results["passed"].append(("论文解读", f"{count}个页面"))
            elif count > 0:
                self.results["warnings"].append(("论文解读", f"仅{count}个页面"))
            else:
                self.results["warnings"].append(("论文解读", "无解读页面"))

    def _check_deployment_layer(self):
        """检查部署层"""
        deploy_dir = Path.home() / "public_html" / "ai-daily"

        if not deploy_dir.exists():
            self.results["failed"].append(("部署目录", "不存在"))
            return

        # 检查关键文件
        checks = [
            ("index.html", "主报告"),
            ("covers", "封面目录"),
            ("insights", "解读目录"),
        ]

        for filename, name in checks:
            path = deploy_dir / filename
            if path.exists():
                if filename in ["covers", "insights"]:
                    count = len(list(path.glob("*"))) if path.is_dir() else 0
                    self.results["passed"].append((f"部署-{name}", f"{count}个文件"))
                else:
                    self.results["passed"].append((f"部署-{name}", "已部署"))
            else:
                self.results["failed"].append((f"部署-{name}", "未部署"))

        # 检查部署时间
        deploy_time_file = deploy_dir / ".last_deploy"
        if deploy_time_file.exists():
            deploy_time = deploy_time_file.read_text().strip()
            self.results["passed"].append(("部署时间", deploy_time))

    def _check_experience_layer(self):
        """检查体验层"""
        # 检查报告中的数据完整性
        index_file = self.base_dir / "docs" / "index.html"
        if not index_file.exists():
            return

        with open(index_file, 'r', encoding='utf-8') as f:
            html = f.read()

        # 检查关键数据
        checks = [
            ("const dailyPick", "每日精选数据"),
            ("const hotArticles", "热门文章数据"),
            ("const arxivPapers", "arXiv论文数据"),
            ("const githubProjects", "GitHub项目数据"),
        ]

        for marker, name in checks:
            if marker in html:
                self.results["passed"].append((f"数据嵌入-{name}", "已嵌入"))
            else:
                self.results["warnings"].append((f"数据嵌入-{name}", "未找到"))

    def _print_results(self, verbose: bool = False):
        """打印检查结果"""
        print("\n" + "=" * 60)
        print("📋 检查结果")
        print("=" * 60 + "\n")

        total = len(self.results["passed"]) + len(self.results["warnings"]) + len(self.results["failed"])

        print(f"✅ 通过: {len(self.results['passed'])} 个")
        print(f"⚠️  警告: {len(self.results['warnings'])} 个")
        print(f"❌ 失败: {len(self.results['failed'])} 个")
        print(f"\n总分: {len(self.results['passed'])}/{total}")

        if verbose or self.results["warnings"] or self.results["failed"]:
            print("\n" + "-" * 60)

            if self.results["failed"]:
                print("\n❌ 失败项:")
                for name, desc in self.results["failed"]:
                    print(f"  • {name}: {desc}")

            if self.results["warnings"]:
                print("\n⚠️  警告项:")
                for name, desc in self.results["warnings"]:
                    print(f"  • {name}: {desc}")

            if verbose and self.results["passed"]:
                print("\n✅ 通过项:")
                for name, desc in self.results["passed"]:
                    print(f"  • {name}: {desc}")

        print("\n" + "=" * 60)

        # 建议
        if self.results["failed"]:
            print("\n🔧 建议操作:")
            print("  1. 运行: python3 scripts/check_and_fix_config.py")
            print("  2. 运行: bash scripts/task_manager.sh")
            print("  3. 检查日志: tail -f logs/*.log")
        elif self.results["warnings"]:
            print("\n💡 优化建议:")
            print("  • 部分封面缺失，等待后台生成完成")
            print("  • 使用 monitor_cover_generation.sh 查看进度")
        else:
            print("\n✨ 系统状态良好！")

        print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="质量保证检查")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    parser.add_argument("--fix", action="store_true", help="尝试自动修复")

    args = parser.parse_args()

    checker = QAChecker()
    results = checker.check(verbose=args.verbose)

    # 返回状态码
    if results["failed"]:
        sys.exit(1)
    elif results["warnings"]:
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
