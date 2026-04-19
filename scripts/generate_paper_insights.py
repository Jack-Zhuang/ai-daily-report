#!/usr/bin/env python3
"""
AI推荐日报 - 论文深度解读脚本
生成图文并茂的技术博客风格论文解读
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
        self.images_dir = self.insights_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # MiniMax API 配置
        self.api_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        self.api_key = self._load_api_key()
    
    def _load_api_key(self) -> str:
        """加载 API Key"""
        import os
        
        # 优先从环境变量获取
        api_key = os.environ.get('MINIMAX_API_KEY', '')
        if api_key:
            return api_key
        
        # 尝试从配置文件获取
        env_file = self.base_dir.parent / ".xiaoyienv"
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("PERSONAL-API-KEY="):
                        return line.split("=", 1)[1].strip().strip('"')
        
        return ""
    
    def generate_simple_insight(self, paper: Dict) -> Dict:
        """生成简化版论文解读（无需 API）"""
        title = paper.get("title", "")
        summary = paper.get("summary", "")
        category = paper.get("category", "other")
        
        # 基于规则的简化解读
        category_names = {
            "rec": "推荐系统",
            "agent": "AI Agent",
            "llm": "大语言模型"
        }
        
        # 提取关键词
        keywords = []
        keyword_patterns = [
            ("recommendation", "推荐"), ("recommender", "推荐系统"),
            ("agent", "智能体"), ("multi-agent", "多智能体"),
            ("LLM", "大语言模型"), ("GPT", "GPT"),
            ("personalization", "个性化"), ("CTR", "点击率"),
            ("embedding", "嵌入"), ("transformer", "Transformer"),
            ("attention", "注意力机制"), ("RAG", "RAG"),
            ("fine-tuning", "微调"), ("training-free", "免训练")
        ]
        
        text_lower = (title + " " + summary).lower()
        for en, cn in keyword_patterns:
            if en.lower() in text_lower:
                keywords.append(cn)
        
        keywords = list(set(keywords))[:5]
        
        # 生成简化解读
        paper.update({
            "cn_title": title,  # 保持原标题
            "subtitle": f"一篇关于{category_names.get(category, 'AI')}领域的研究论文",
            "reading_time": "5分钟",
            "difficulty": "进阶",
            "tags": keywords if keywords else [category_names.get(category, "AI")],
            "summary_detail": {
                "one_sentence": summary[:50] + "..." if len(summary) > 50 else summary,
                "core_contribution": "请查看论文原文了解核心贡献",
                "practical_value": "请查看论文原文了解实用价值"
            },
            "sections": [
                {
                    "title": "📖 论文摘要",
                    "content": summary[:300] + "..." if len(summary) > 300 else summary,
                    "key_points": []
                },
                {
                    "title": "🏷️ 关键词",
                    "content": "、".join(keywords) if keywords else "请查看论文原文",
                    "key_points": []
                }
            ],
            "has_insight": True,
            "insight_type": "simple"  # 标记为简化版
        })
        
        return paper
    
    def generate_detailed_insight(self, paper: Dict) -> Dict:
        """生成单篇论文的详细解读（技术博客风格）"""
        title = paper.get("title", "")
        summary = paper.get("summary", "")
        
        if not title or not self.api_key:
            return paper
        
        prompt = f"""请对以下论文进行深度解读，生成一篇图文并茂的技术博客风格文章。

论文标题：{title}

论文摘要：{summary[:1500]}

请严格按照以下 JSON 格式输出：

{{
  "cn_title": "中文标题（简洁有力）",
  "subtitle": "副标题（一句话概括核心贡献）",
  "reading_time": "预计阅读时间（如：8分钟）",
  "difficulty": "入门/进阶/高级",
  "tags": ["标签1", "标签2", "标签3"],
  
  "summary": {{
    "one_sentence": "一句话总结（20字以内）",
    "core_contribution": "核心贡献（50字以内）",
    "practical_value": "实用价值（50字以内）"
  }},
  
  "sections": [
    {{
      "title": "📖 背景与动机",
      "content": "介绍研究背景、现有方法的局限性、本文要解决的问题（150-200字）",
      "key_points": ["要点1", "要点2", "要点3"]
    }},
    {{
      "title": "💡 核心方法",
      "content": "详细介绍本文提出的方法，包括模型架构、算法流程等（200-300字）",
      "diagram_description": "方法流程图描述（用于生成示意图）",
      "formula_explanation": "核心公式解释（如有）"
    }},
    {{
      "title": "🔬 实验结果",
      "content": "主要实验设置和结果，包括数据集、评价指标、对比方法等（150-200字）",
      "key_findings": ["发现1", "发现2", "发现3"],
      "performance_gain": "性能提升幅度（如：相比基线提升5%）"
    }},
    {{
      "title": "🎯 创新点分析",
      "content": "本文的主要创新点和亮点（100-150字）",
      "innovations": [
        {{"point": "创新点1", "description": "具体描述"}},
        {{"point": "创新点2", "description": "具体描述"}}
      ]
    }},
    {{
      "title": "🏭 工业落地思考",
      "content": "如何在实际业务中应用本文方法，需要注意的问题（150-200字）",
      "application_scenarios": ["场景1", "场景2"],
      "implementation_difficulty": "实现难度评估（简单/中等/困难）及原因",
      "engineering_challenges": ["工程挑战1", "工程挑战2"]
    }},
    {{
      "title": "📝 总结与展望",
      "content": "总结本文贡献，展望未来研究方向（100字左右）",
      "takeaway": "核心收获（一句话）"
    }}
  ],
  
  "references": [
    {{"title": "相关工作1", "description": "简要说明关系"}},
    {{"title": "相关工作2", "description": "简要说明关系"}}
  ],
  
  "qa": [
    {{"question": "读者可能的问题1", "answer": "简要回答"}},
    {{"question": "读者可能的问题2", "answer": "简要回答"}}
  ]
}}

注意：
1. 内容要专业但不晦涩，适合技术人员阅读
2. 重点突出工业落地价值
3. 创新点要具体，不要泛泛而谈
4. 工程挑战要实事求是"""

        try:
            payload = {
                "model": "abab6.5s-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一位资深的AI技术博主，擅长用通俗易懂的语言解读学术论文，注重实践价值和工程落地。你的文章风格类似于机器之心、量子位等科技媒体。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 3000
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=90)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # 尝试解析 JSON
                try:
                    json_start = content.find("{")
                    json_end = content.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        insight = json.loads(json_str)
                        
                        # 合并到论文数据
                        paper.update({
                            "cn_title": insight.get("cn_title", ""),
                            "subtitle": insight.get("subtitle", ""),
                            "reading_time": insight.get("reading_time", ""),
                            "difficulty": insight.get("difficulty", ""),
                            "tags": insight.get("tags", []),
                            "summary_detail": insight.get("summary", {}),
                            "sections": insight.get("sections", []),
                            "references": insight.get("references", []),
                            "qa": insight.get("qa", []),
                            "has_insight": True
                        })
                    else:
                        paper["has_insight"] = False
                except Exception as e:
                    print(f"    ⚠️ JSON解析失败: {e}")
                    paper["has_insight"] = False
            else:
                paper["has_insight"] = False
        except Exception as e:
            print(f"    ⚠️ 解读失败: {e}")
            paper["has_insight"] = False
        
        return paper
    
    def generate_insights_for_papers(self, papers: List[Dict], max_count: int = 10) -> List[Dict]:
        """批量生成论文解读"""
        print(f"\n{'='*60}")
        print(f"📝 生成论文深度解读（技术博客风格）")
        print(f"{'='*60}\n")
        
        # 检查是否有 API Key
        has_api = bool(self.api_key)
        if has_api:
            print("  ✅ 使用 MiniMax API 生成详细解读\n")
        else:
            print("  ⚠️ 未配置 API Key，使用简化版解读\n")
        
        # 只处理没有解读的论文
        papers_to_process = [p for p in papers if not p.get("has_insight")][:max_count]
        
        for i, paper in enumerate(papers_to_process):
            title = paper.get("title", "")[:40]
            print(f"  📄 [{i+1}/{len(papers_to_process)}] {title}...", end=" ", flush=True)
            
            if has_api:
                paper = self.generate_detailed_insight(paper)
            else:
                paper = self.generate_simple_insight(paper)
            
            if paper.get("has_insight"):
                print("✅")
            else:
                print("⚠️")
            
            time.sleep(0.3)  # 避免 API 限流
        
        return papers
    
    def generate_markdown_report(self, paper: Dict) -> str:
        """生成 Markdown 格式的技术博客"""
        if not paper.get("has_insight"):
            return ""
        
        lines = []
        
        # 标题
        lines.append(f"# {paper.get('cn_title', paper.get('title', ''))}\n")
        
        if paper.get("subtitle"):
            lines.append(f"**{paper.get('subtitle')}**\n")
        
        # 元信息
        lines.append(f"\n> 📅 预计阅读：{paper.get('reading_time', '5分钟')} | ")
        lines.append(f"难度：{paper.get('difficulty', '进阶')} | ")
        lines.append(f"arXiv: [{paper.get('arxiv_id', '')}]({paper.get('link', '')})\n")
        
        # 标签
        tags = paper.get("tags", [])
        if tags:
            lines.append(f"\n🏷️ 标签：{' | '.join([f'`{t}`' for t in tags])}\n")
        
        # 摘要卡片
        summary = paper.get("summary_detail", {})
        if summary:
            lines.append("\n---\n")
            lines.append("### 📌 TL;DR\n")
            lines.append(f"- **一句话总结**：{summary.get('one_sentence', '')}")
            lines.append(f"- **核心贡献**：{summary.get('core_contribution', '')}")
            lines.append(f"- **实用价值**：{summary.get('practical_value', '')}\n")
        
        # 各章节
        sections = paper.get("sections", [])
        for section in sections:
            lines.append("\n---\n")
            lines.append(f"## {section.get('title', '')}\n")
            lines.append(f"{section.get('content', '')}\n")
            
            # 要点列表
            key_points = section.get("key_points", [])
            if key_points:
                lines.append("\n**关键要点：**\n")
                for point in key_points:
                    lines.append(f"- {point}")
                lines.append("")
            
            # 创新点
            innovations = section.get("innovations", [])
            if innovations:
                lines.append("\n| 创新点 | 说明 |")
                lines.append("|--------|------|")
                for inn in innovations:
                    lines.append(f"| {inn.get('point', '')} | {inn.get('description', '')} |")
                lines.append("")
            
            # 发现列表
            key_findings = section.get("key_findings", [])
            if key_findings:
                lines.append("\n**主要发现：**\n")
                for finding in key_findings:
                    lines.append(f"- ✅ {finding}")
                lines.append("")
            
            # 应用场景
            scenarios = section.get("application_scenarios", [])
            if scenarios:
                lines.append("\n**适用场景：**\n")
                for s in scenarios:
                    lines.append(f"- 🎯 {s}")
                lines.append("")
            
            # 工程挑战
            challenges = section.get("engineering_challenges", [])
            if challenges:
                lines.append("\n**工程挑战：**\n")
                for c in challenges:
                    lines.append(f"- ⚠️ {c}")
                lines.append("")
        
        # 参考文献
        references = paper.get("references", [])
        if references:
            lines.append("\n---\n")
            lines.append("## 📚 参考文献\n")
            for ref in references:
                lines.append(f"- **{ref.get('title', '')}**：{ref.get('description', '')}")
            lines.append("")
        
        # Q&A
        qa = paper.get("qa", [])
        if qa:
            lines.append("\n---\n")
            lines.append("## ❓ 常见问题\n")
            for q in qa:
                lines.append(f"**Q：{q.get('question', '')}**")
                lines.append(f"\nA：{q.get('answer', '')}\n")
        
        # 页脚
        lines.append("\n---\n")
        lines.append("*本文由 AI 推荐日报自动生成，仅供参考学习*\n")
        
        return "\n".join(lines)
    
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
                    item = self.generate_detailed_insight(item)
        data["daily_pick"] = daily_pick
        
        # 保存
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 解读完成，已保存到: {data_file}")
        
        # 生成 Markdown 报告
        self._save_insight_reports(papers[:10])
    
    def _save_insight_reports(self, papers: List[Dict]):
        """保存解读报告"""
        # 生成合并报告
        report_lines = [f"# 论文深度解读 - {self.today}\n\n"]
        report_lines.append("> 本文由 AI 推荐日报自动生成，共解读以下论文：\n\n")
        
        saved_count = 0
        for i, paper in enumerate(papers, 1):
            if not paper.get("has_insight"):
                continue
            
            saved_count += 1
            
            # 生成单篇报告
            md_content = self.generate_markdown_report(paper)
            if md_content:
                # 保存单篇
                arxiv_id = paper.get("arxiv_id", f"paper_{i}")
                single_file = self.insights_dir / f"{self.today}_{arxiv_id}.md"
                with open(single_file, "w", encoding="utf-8") as f:
                    f.write(md_content)
                
                # 添加到目录
                cn_title = paper.get("cn_title", paper.get("title", ""))[:30]
                report_lines.append(f"{i}. [{cn_title}]({single_file.name})\n")
        
        # 保存目录
        if saved_count > 0:
            index_file = self.insights_dir / f"{self.today}.md"
            with open(index_file, "w", encoding="utf-8") as f:
                f.writelines(report_lines)
            
            print(f"📄 已生成 {saved_count} 篇解读报告")
            print(f"   目录: {index_file}")


if __name__ == "__main__":
    generator = PaperInsightGenerator()
    generator.run()
