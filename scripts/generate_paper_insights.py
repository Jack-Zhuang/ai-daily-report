#!/usr/bin/env python3
"""
AI推荐日报 - 论文深度解读脚本
生成论文的详细解读，包括：背景、方法、实验、创新点、工业价值
"""

import json
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class PaperInsightGenerator:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.insights_dir = self.base_dir / "insights"
        self.insights_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # MiniMax API 配置
        self.api_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        self.api_key = self._load_api_key()
    
    def _load_api_key(self) -> str:
        """加载 API Key"""
        env_file = self.base_dir.parent / ".xiaoyienv"
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("PERSONAL-API-KEY="):
                        return line.split("=", 1)[1].strip().strip('"')
        return ""
    
    def generate_insight(self, paper: Dict) -> Dict:
        """生成单篇论文的深度解读"""
        title = paper.get("title", "")
        summary = paper.get("summary", "")
        
        if not title or not self.api_key:
            return paper
        
        prompt = f"""请对以下论文进行深度解读，生成结构化的分析报告。

论文标题：{title}

论文摘要：{summary[:1000]}

请按以下结构输出（使用 JSON 格式）：

{{
  "cn_title": "中文标题",
  "background": "研究背景（50字以内，说明解决了什么问题）",
  "method": "核心方法（100字以内，说明主要技术方案）",
  "innovation": "创新点（列出2-3个关键创新）",
  "experiments": "实验结果（50字以内，说明主要实验结论）",
  "industry_value": "工业价值（说明实际应用场景和价值）",
  "difficulty": "实现难度（简单/中等/困难，并说明原因）",
  "keywords": ["关键词1", "关键词2", "关键词3"]
}}

注意：
1. 内容要简洁、专业
2. 工业价值要具体，说明可以应用在哪些场景
3. 实现难度要客观评估"""

        try:
            payload = {
                "model": "abab6.5s-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的AI论文解读专家，擅长分析推荐系统、AI Agent、LLM领域的论文。请用简洁专业的语言进行解读。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # 尝试解析 JSON
                try:
                    # 提取 JSON 部分
                    json_match = content[content.find("{"):content.rfind("}")+1]
                    insight = json.loads(json_match)
                    
                    # 合并到论文数据
                    paper.update({
                        "cn_title": insight.get("cn_title", ""),
                        "background": insight.get("background", ""),
                        "method": insight.get("method", ""),
                        "innovation": insight.get("innovation", []),
                        "experiments": insight.get("experiments", ""),
                        "industry_value": insight.get("industry_value", ""),
                        "difficulty": insight.get("difficulty", ""),
                        "keywords": insight.get("keywords", []),
                        "has_insight": True
                    })
                except:
                    # JSON 解析失败，使用原始内容
                    paper["cn_summary"] = content[:300]
                    paper["has_insight"] = False
        except Exception as e:
            print(f"    ⚠️ 解读失败: {e}")
            paper["has_insight"] = False
        
        return paper
    
    def generate_insights_for_papers(self, papers: List[Dict], max_count: int = 10) -> List[Dict]:
        """批量生成论文解读"""
        print(f"\n{'='*60}")
        print(f"📝 生成论文深度解读")
        print(f"{'='*60}\n")
        
        # 只处理没有解读的论文
        papers_to_process = [p for p in papers if not p.get("has_insight")][:max_count]
        
        for i, paper in enumerate(papers_to_process):
            title = paper.get("title", "")[:40]
            print(f"  📄 [{i+1}/{len(papers_to_process)}] {title}...", end=" ", flush=True)
            
            paper = self.generate_insight(paper)
            
            if paper.get("has_insight"):
                print("✅")
            else:
                print("⚠️")
            
            time.sleep(0.5)  # 避免 API 限流
        
        return papers
    
    def run(self):
        """执行解读生成"""
        # 加载今日数据
        data_file = self.base_dir / "daily_data" / f"{self.today}.json"
        
        if not data_file.exists():
            print(f"❌ 今日数据文件不存在: {data_file}")
            return
        
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        papers = data.get("arxiv_papers", [])
        
        if not papers:
            print("❌ 没有论文需要解读")
            return
        
        # 生成解读
        papers = self.generate_insights_for_papers(papers, max_count=10)
        data["arxiv_papers"] = papers
        
        # 同样处理每日精选中的论文
        daily_pick = data.get("daily_pick", [])
        for item in daily_pick:
            if item.get("_type") == "paper" or item.get("type") == "paper":
                if not item.get("has_insight"):
                    item = self.generate_insight(item)
        data["daily_pick"] = daily_pick
        
        # 保存
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 解读完成，已保存到: {data_file}")
        
        # 保存解读报告
        self._save_insight_report(papers[:10])
    
    def _save_insight_report(self, papers: List[Dict]):
        """保存解读报告"""
        report_lines = [f"# 论文深度解读 - {self.today}\n"]
        
        for i, paper in enumerate(papers, 1):
            if not paper.get("has_insight"):
                continue
            
            report_lines.append(f"\n## {i}. {paper.get('cn_title', paper.get('title', ''))}\n")
            report_lines.append(f"**原文标题**: {paper.get('title', '')}\n")
            report_lines.append(f"**arXiv**: [{paper.get('arxiv_id', '')}]({paper.get('link', '')})\n")
            report_lines.append(f"\n### 研究背景\n{paper.get('background', 'N/A')}\n")
            report_lines.append(f"\n### 核心方法\n{paper.get('method', 'N/A')}\n")
            report_lines.append(f"\n### 创新点\n")
            for inn in paper.get("innovation", []):
                report_lines.append(f"- {inn}\n")
            report_lines.append(f"\n### 实验结果\n{paper.get('experiments', 'N/A')}\n")
            report_lines.append(f"\n### 工业价值\n{paper.get('industry_value', 'N/A')}\n")
            report_lines.append(f"\n### 实现难度\n{paper.get('difficulty', 'N/A')}\n")
            report_lines.append("\n---\n")
        
        report_file = self.insights_dir / f"{self.today}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.writelines(report_lines)
        
        print(f"📄 解读报告已保存: {report_file}")


if __name__ == "__main__":
    generator = PaperInsightGenerator()
    generator.run()
