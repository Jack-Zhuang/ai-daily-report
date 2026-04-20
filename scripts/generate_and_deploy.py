#!/usr/bin/env python3
"""
AI推荐日报 - 带自动部署的报告生成脚本
生成报告后自动部署到 public_html
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_command(cmd, cwd=None):
    """运行命令并实时输出"""
    print(f"🔧 执行: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=False,
        text=True
    )
    return result.returncode == 0


def generate_report(date=None):
    """生成报告"""
    base_dir = Path(__file__).parent.parent

    print("\n" + "=" * 60)
    print("📝 生成 AI 推荐日报")
    print("=" * 60 + "\n")

    # 生成报告
    cmd = f"python3 scripts/generate_report.py"
    if date:
        cmd += f" --date {date}"

    if not run_command(cmd, cwd=base_dir):
        print("❌ 报告生成失败")
        return False

    # 复制到 docs 目录
    print("\n📦 复制报告到 docs 目录...")
    run_command("cp index.html docs/index.html", cwd=base_dir)

    return True


def deploy():
    """部署到 public_html"""
    base_dir = Path(__file__).parent.parent

    print("\n" + "=" * 60)
    print("🚀 部署到 public_html")
    print("=" * 60 + "\n")

    # 运行自动部署脚本
    if not run_command("bash scripts/auto_deploy.sh", cwd=base_dir):
        print("❌ 部署失败")
        return False

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="生成报告并自动部署")
    parser.add_argument("--date", type=str, help="日期 (YYYY-MM-DD)")
    parser.add_argument("--skip-deploy", action="store_true", help="跳过部署")

    args = parser.parse_args()

    # 生成报告
    if not generate_report(args.date):
        sys.exit(1)

    # 部署
    if not args.skip_deploy:
        if not deploy():
            sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ 完成！报告已生成并部署")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
