#!/usr/bin/env python3
"""
AI推荐日报 - 增强版论文解读生成器
基于完整论文内容生成深度解读，包含流程图、公式、代码示例
"""

import os
import json
import requests
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

# 导入论文提取器
from paper_extractor import PaperExtractor, PaperContent


@dataclass
class InsightSection:
    """解读章节"""
    title: str
    content: str
    diagram: Optional[str] = None  # Mermaid 代码
    formula: Optional[str] = None  # LaTeX 公式
    code: Optional[str] = None     # 代码示例


class EnhancedInsightGenerator:
    """增强版论文解读生成器"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent.parent
        self.base_dir = Path(base_dir)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # MiniMax Token Plan API 配置
        self.api_url = "https://api.minimaxi.com/anthropic/v1/messages"
        self.api_key = self._load_api_key()
        
        # 论文提取器
        self.extractor = PaperExtractor(
            cache_dir=str(self.base_dir / "paper_cache")
        )
    
    def _load_api_key(self) -> str:
        """加载 API Key"""
        api_key = os.environ.get('MINIMAX_API_KEY', '')
        if api_key:
            return api_key
        
        env_file = Path.home() / ".openclaw" / "env.sh"
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("export MINIMAX_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        
        return ""
    
    def _call_api(self, prompt: str, max_tokens: int = 4000) -> str:
        """调用 MiniMax Token Plan API"""
        if not self.api_key:
            return ""
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "MiniMax-M2.7-highspeed",
                "max_tokens": max_tokens + 500,  # 预留思考过程的空间
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                content_blocks = data.get('content', [])
                for block in content_blocks:
                    if block.get('type') == 'text':
                        return block.get('text', '').strip()
        except Exception as e:
            print(f"    ⚠️ API调用失败: {e}")
        
        return ""
    
    def generate_mermaid_diagram(self, method_description: str) -> str:
        """生成 Mermaid 流程图"""
        prompt = f"""根据以下论文方法描述，生成一个 Mermaid 流程图代码。

方法描述：
{method_description[:2000]}

要求：
1. 使用 graph TD 或 graph LR 布局
2. 节点命名简洁明了（中文）
3. 使用子图(subgraph)分组相关模块
4. 添加适当的样式类
5. 只输出 Mermaid 代码，不要解释

Mermaid 代码："""

        result = self._call_api(prompt, max_tokens=1000)
        
        # 提取 mermaid 代码块
        if "```mermaid" in result:
            match = re.search(r"```mermaid\s*([\s\S]*?)```", result)
            if match:
                return match.group(1).strip()
        elif "```" in result:
            match = re.search(r"```\s*([\s\S]*?)```", result)
            if match:
                return match.group(1).strip()
        
        return result if result else ""
    
    def generate_latex_formula(self, formula_description: str) -> str:
        """生成 LaTeX 公式"""
        prompt = f"""将以下公式描述转换为 LaTeX 格式。

描述：
{formula_description}

要求：
1. 使用标准 LaTeX 语法
2. 多行公式使用 align 环境
3. 只输出 LaTeX 代码，不要解释
4. 使用常见的数学符号命令

LaTeX 代码："""

        result = self._call_api(prompt, max_tokens=500)
        
        # 提取 LaTeX 代码
        if "$$" in result:
            match = re.search(r"\$\$([\s\S]*?)\$\$", result)
            if match:
                return match.group(1).strip()
        elif "$" in result:
            match = re.search(r"\$([^\$]+)\$", result)
            if match:
                return match.group(1).strip()
        elif "\\[" in result:
            match = re.search(r"\\\[([\s\S]*?)\\\]", result)
            if match:
                return match.group(1).strip()
        
        return result if result else ""
    
    def generate_formulas_section(self, equations: List[str]) -> List[Dict]:
        """生成公式章节"""
        formulas = []
        
        for eq in equations[:5]:  # 最多处理 5 个公式
            if len(eq) < 10:
                continue
            
            print(f"    🔢 转换公式: {eq[:30]}...")
            latex = self.generate_latex_formula(eq)
            
            if latex:
                formulas.append({
                    "original": eq,
                    "latex": latex
                })
            
            time.sleep(0.3)  # 避免 API 限流
        
        return formulas
    
    def generate_code_example(self, method_description: str, language: str = "python") -> str:
        """生成代码示例"""
        prompt = f"""根据以下论文方法描述，生成一个简化的 {language} 代码示例。

方法描述：
{method_description[:1500]}

要求：
1. 代码简洁易懂，展示核心思想
2. 添加必要的注释
3. 使用伪代码风格，不需要完整实现
4. 只输出代码，不要解释

{language} 代码："""

        result = self._call_api(prompt, max_tokens=1500)
        
        # 提取代码块
        if f"```{language}" in result:
            match = re.search(rf"```{language}\s*([\s\S]*?)```", result)
            if match:
                return match.group(1).strip()
        elif "```" in result:
            match = re.search(r"```\s*([\s\S]*?)```", result)
            if match:
                return match.group(1).strip()
        
        return result if result else ""
    
    def generate_deep_insight(self, paper_content: PaperContent) -> Dict:
        """生成深度解读"""
        
        # 构建完整 prompt
        prompt = f"""你是一位资深的AI技术博主，擅长用通俗易懂的语言解读学术论文。请对以下论文进行深度解读。

论文信息：
- 标题：{paper_content.title}
- arXiv ID：{paper_content.arxiv_id}

摘要：
{paper_content.abstract[:1000]}

主要章节：
{self._format_sections(paper_content.sections)}

图片说明：
{self._format_figures(paper_content.figures)}

关键公式：
{chr(10).join(paper_content.equations[:5])}

请严格按照以下 JSON 格式输出：

{{
  "cn_title": "中文标题（简洁有力）",
  "subtitle": "副标题（一句话概括核心贡献）",
  "reading_time": "预计阅读时间（如：12分钟）",
  "difficulty": "入门/进阶/高级",
  "tags": ["标签1", "标签2", "标签3"],
  
  "summary": {{
    "one_sentence": "一句话总结（20字以内）",
    "core_contribution": "核心贡献（50字以内）",
    "practical_value": "实用价值（50字以内）"
  }},
  
  "background": {{
    "content": "研究背景和动机（200-300字）",
    "key_points": ["要点1", "要点2", "要点3"]
  }},
  
  "method": {{
    "overview": "方法概述（100字）",
    "details": "详细方法描述（300-400字）",
    "diagram_description": "方法流程图描述（用于生成 Mermaid）",
    "key_components": [
      {{"name": "组件1", "description": "描述"}},
      {{"name": "组件2", "description": "描述"}}
    ]
  }},
  
  "experiments": {{
    "datasets": "使用的数据集",
    "metrics": "评价指标",
    "results": "主要实验结果（200字）",
    "key_findings": ["发现1", "发现2", "发现3"]
  }},
  
  "innovations": [
    {{"point": "创新点1", "description": "具体描述（50字）"}},
    {{"point": "创新点2", "description": "具体描述（50字）"}}
  ],
  
  "industry_application": {{
    "scenarios": ["应用场景1", "应用场景2"],
    "difficulty": "实现难度（简单/中等/困难）",
    "challenges": ["挑战1", "挑战2"],
    "code_hint": "代码实现思路（100字）"
  }},
  
  "conclusion": {{
    "takeaway": "核心收获（一句话）",
    "future_work": "未来方向（50字）"
  }},
  
  "qa": [
    {{"question": "读者可能的问题1", "answer": "简要回答"}},
    {{"question": "读者可能的问题2", "answer": "简要回答"}}
  ]
}}

注意：
1. 内容要专业但不晦涩
2. 重点突出工业落地价值
3. 方法描述要具体，便于生成流程图"""

        result = self._call_api(prompt, max_tokens=4000)
        
        # 解析 JSON
        try:
            # 提取 JSON
            if "```json" in result:
                match = re.search(r"```json\s*([\s\S]*?)```", result)
                if match:
                    result = match.group(1)
            elif "{" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                result = result[json_start:json_end]
            
            return json.loads(result)
        except Exception as e:
            print(f"    ⚠️ JSON解析失败: {e}")
            return {}
    
    def _format_sections(self, sections: List) -> str:
        """格式化章节"""
        formatted = []
        for sec in sections[:5]:  # 最多 5 个章节
            formatted.append(f"- {sec.title}: {sec.content[:200]}...")
        return "\n".join(formatted)
    
    def _format_figures(self, figures: List) -> str:
        """格式化图片说明"""
        formatted = []
        for fig in figures[:5]:  # 最多 5 张图
            formatted.append(f"- Figure {fig.index}: {fig.caption}")
        return "\n".join(formatted)
    
    def generate_markdown(self, paper_content: PaperContent, insight: Dict) -> str:
        """生成 Markdown 文档"""
        
        cn_title = insight.get("cn_title", paper_content.title)
        subtitle = insight.get("subtitle", "")
        reading_time = insight.get("reading_time", "10分钟")
        difficulty = insight.get("difficulty", "进阶")
        tags = insight.get("tags", [])
        summary = insight.get("summary", {})
        background = insight.get("background", {})
        method = insight.get("method", {})
        experiments = insight.get("experiments", {})
        innovations = insight.get("innovations", [])
        industry = insight.get("industry_application", {})
        conclusion = insight.get("conclusion", {})
        qa = insight.get("qa", [])
        
        # 生成 Mermaid 流程图
        print("  🎨 生成流程图...")
        mermaid_code = ""
        if method.get("diagram_description"):
            mermaid_code = self.generate_mermaid_diagram(method["diagram_description"])
        
        # 生成代码示例
        print("  💻 生成代码示例...")
        code_example = ""
        if method.get("details"):
            code_example = self.generate_code_example(method["details"])
        
        # 生成公式
        print("  🔢 生成 LaTeX 公式...")
        formulas = []
        if paper_content.equations:
            formulas = self.generate_formulas_section(paper_content.equations)
        
        # 构建 Markdown
        md = f"""# {cn_title}

**{subtitle}**


> 📅 预计阅读：{reading_time} | 
难度：{difficulty} | 
arXiv: [{paper_content.arxiv_id}](http://arxiv.org/abs/{paper_content.arxiv_id})


🏷️ 标签：{' | '.join([f'`{t}`' for t in tags])}


---

### 📌 TL;DR

- **一句话总结**：{summary.get('one_sentence', '')}
- **核心贡献**：{summary.get('core_contribution', '')}
- **实用价值**：{summary.get('practical_value', '')}


---

## 📖 背景与动机

{background.get('content', '')}


**关键要点：**

{chr(10).join([f'- {p}' for p in background.get('key_points', [])])}


---

## 💡 核心方法

### 方法概述

{method.get('overview', '')}


### 详细设计

{method.get('details', '')}


"""
        
        # 添加流程图
        if mermaid_code:
            md += f"""### 📊 方法流程图

```mermaid
{mermaid_code}
```

"""
        
        # 添加关键组件
        components = method.get('key_components', [])
        if components:
            md += """### 🔧 关键组件

| 组件 | 说明 |
|------|------|
"""
            for comp in components:
                md += f"| {comp.get('name', '')} | {comp.get('description', '')} |\n"
            md += "\n"
        
        # 添加代码示例
        if code_example:
            md += f"""### 💻 代码示例

```python
{code_example}
```

"""
        
        # 添加公式
        if formulas:
            md += """### 🔢 核心公式

"""
            for i, formula in enumerate(formulas, 1):
                md += f"""**公式 {i}**：

$$
{formula['latex']}
$$

*含义*：{formula['original'][:100]}

"""
        
        # 实验结果
        md += f"""---

## 🔬 实验结果

**数据集**：{experiments.get('datasets', '')}

**评价指标**：{experiments.get('metrics', '')}

**主要结果**：

{experiments.get('results', '')}


**主要发现：**

{chr(10).join([f'- ✅ {f}' for f in experiments.get('key_findings', [])])}


---

## 🎯 创新点分析

| 创新点 | 说明 |
|--------|------|
"""
        for inn in innovations:
            md += f"| {inn.get('point', '')} | {inn.get('description', '')} |\n"
        
        # 工业落地
        md += f"""
---

## 🏭 工业落地思考

**适用场景：**

{chr(10).join([f'- 🎯 {s}' for s in industry.get('scenarios', [])])}


**实现难度**：{industry.get('difficulty', '中等')}

**工程挑战：**

{chr(10).join([f'- ⚠️ {c}' for c in industry.get('challenges', [])])}


"""
        
        if industry.get('code_hint'):
            md += f"""**代码实现思路**：

{industry.get('code_hint')}


"""
        
        # 总结
        md += f"""---

## 📝 总结与展望

**核心收获**：{conclusion.get('takeaway', '')}

**未来方向**：{conclusion.get('future_work', '')}


---

## ❓ 常见问题

"""
        for q in qa:
            md += f"""**Q：{q.get('question', '')}**

A：{q.get('answer', '')}


"""
        
        # 图片展示
        if paper_content.figures:
            md += """---

## 📷 论文图片

"""
            for fig in paper_content.figures[:5]:
                if fig.image_url:
                    md += f"""**Figure {fig.index}**: {fig.caption}

![Figure {fig.index}]({fig.image_url})

"""
        
        md += """---

*本文由 AI 推荐日报自动生成，仅供参考学习*
"""
        
        return md
    
    def process_paper(self, arxiv_id: str, title: str) -> str:
        """处理单篇论文"""
        print(f"\n{'='*60}")
        print(f"📄 生成增强版论文解读: {arxiv_id}")
        print(f"{'='*60}\n")
        
        # 1. 提取论文内容
        print("📥 步骤 1: 提取论文内容")
        paper_content = self.extractor.extract(arxiv_id, title)
        
        # 2. 生成深度解读
        print("\n🧠 步骤 2: 生成深度解读")
        insight = self.generate_deep_insight(paper_content)
        
        if not insight:
            print("  ❌ 解读生成失败")
            return ""
        
        # 3. 生成 Markdown
        print("\n📝 步骤 3: 生成 Markdown 文档")
        markdown = self.generate_markdown(paper_content, insight)
        
        # 4. 保存
        output_dir = self.base_dir / "insights_enhanced"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{self.today}_{arxiv_id}.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"\n✅ 完成！已保存到: {output_path}")
        
        return str(output_path)


def main():
    """测试入口"""
    generator = EnhancedInsightGenerator()
    
    # 测试
    arxiv_id = "2604.14878"
    title = "GenRec: A Preference-Oriented Generative Framework for Large-Scale Recommendation"
    
    output = generator.process_paper(arxiv_id, title)
    print(f"\n📄 输出文件: {output}")


if __name__ == "__main__":
    main()
