#!/usr/bin/env python3
"""
AI推荐日报 - 任务协调器
管理和分配任务给不同的子代理
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class TaskOrchestrator:
    """任务协调器"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.logs_dir = self.base_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        # 任务队列
        self.tasks = []
        self.completed_tasks = []

    def spawn_agent(self, task_type: str, task_description: str) -> Optional[str]:
        """生成子代理执行任务"""
        agent_prompts = {
            'cover': f"""
你是一个封面生成助手。

任务：{task_description}

工作目录：{self.base_dir}

请执行以下操作：
1. 检查当前封面生成进度
2. 如果有失败的，重新生成
3. 验证所有封面质量
4. 更新数据文件
5. 部署最新内容

完成后报告结果。
""",
            'collector': f"""
你是一个数据采集助手。

任务：{task_description}

工作目录：{self.base_dir}

请执行以下操作：
1. 确保 RSSHub 运行
2. 采集各类数据
3. 验证数据完整性
4. 报告采集结果

完成后报告结果。
""",
            'report': f"""
你是一个报告生成助手。

任务：{task_description}

工作目录：{self.base_dir}

请执行以下操作：
1. 生成主报告
2. 生成论文解读页面
3. 验证报告完整性
4. 部署最新报告

完成后报告结果。
"""
        }

        prompt = agent_prompts.get(task_type)
        if not prompt:
            print(f"❌ 未知的任务类型: {task_type}")
            return None

        # 使用 sessions_spawn 创建子代理
        try:
            result = subprocess.run(
                ["openclaw", "sessions", "spawn", "--task", prompt],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print(f"✅ 子代理已启动: {task_type}")
                return result.stdout.strip()
            else:
                print(f"❌ 启动子代理失败: {result.stderr}")
                return None

        except Exception as e:
            print(f"❌ 启动子代理异常: {e}")
            return None

    def check_cover_progress(self) -> Dict:
        """检查封面生成进度"""
        covers_dir = self.base_dir / "covers"
        generated = len(list(covers_dir.glob("*.jpg")))
        valid = len([f for f in covers_dir.glob("*.jpg") if f.stat().st_size > 10000])

        return {
            "generated": generated,
            "valid": valid,
            "target": 93,
            "progress": f"{generated * 100 // 93}%"
        }

    def check_data_status(self) -> Dict:
        """检查数据状态"""
        today = datetime.now().strftime("%Y-%m-%d")
        data_file = self.base_dir / "daily_data" / f"{today}.json"

        if not data_file.exists():
            # 尝试昨天的数据
            from datetime import timedelta
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            data_file = self.base_dir / "daily_data" / f"{yesterday}.json"

        if not data_file.exists():
            return {"status": "no_data"}

        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return {
            "status": "ok",
            "daily_pick": len(data.get('daily_pick', [])),
            "arxiv_papers": len(data.get('arxiv_papers', [])),
            "github_projects": len(data.get('github_projects', [])),
            "articles": len(data.get('articles', []))
        }

    def run_parallel_tasks(self):
        """并行运行多个任务"""
        print("\n" + "=" * 60)
        print("🤖 AI推荐日报 - 任务协调器")
        print("=" * 60 + "\n")

        # 检查当前状态
        print("📊 当前状态:")
        cover_progress = self.check_cover_progress()
        print(f"  封面生成: {cover_progress['progress']} ({cover_progress['generated']}/{cover_progress['target']})")

        data_status = self.check_data_status()
        if data_status['status'] == 'ok':
            print(f"  数据状态: ✅")
            print(f"    - 每日精选: {data_status['daily_pick']} 条")
            print(f"    - arXiv论文: {data_status['arxiv_papers']} 条")
            print(f"    - GitHub: {data_status['github_projects']} 条")
            print(f"    - 文章: {data_status['articles']} 条")
        else:
            print(f"  数据状态: ❌ 无数据")

        print("\n" + "=" * 60)

        # 根据状态决定任务
        tasks_to_run = []

        # 如果封面未完成，启动封面生成助手
        if cover_progress['generated'] < cover_progress['target']:
            tasks_to_run.append(('cover', f"继续生成封面，当前进度 {cover_progress['progress']}"))

        # 如果数据不完整，启动数据采集助手
        if data_status['status'] != 'ok' or data_status.get('arxiv_papers', 0) == 0:
            tasks_to_run.append(('collector', "采集今日数据"))

        print(f"\n📋 待执行任务: {len(tasks_to_run)} 个")
        for i, (task_type, desc) in enumerate(tasks_to_run, 1):
            print(f"  {i}. [{task_type}] {desc}")

        print("\n" + "=" * 60)

        # 执行任务
        for task_type, desc in tasks_to_run:
            print(f"\n🚀 启动任务: {task_type}")
            self.spawn_agent(task_type, desc)

        print("\n" + "=" * 60)
        print("✅ 任务分配完成")
        print("=" * 60 + "\n")


def main():
    orchestrator = TaskOrchestrator()
    orchestrator.run_parallel_tasks()


if __name__ == "__main__":
    main()
