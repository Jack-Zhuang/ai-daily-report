#!/usr/bin/env python3
"""
LLM 摘要生成器 - 统一的摘要生成模块

支持：
- 论文摘要生成
- GitHub 项目简介生成
- 文章摘要生成

使用 MiniMax Token Plan API（Anthropic 兼容）
"""

import json
import re
import requests
import time
from pathlib import Path
from typing import Optional, Dict, Any

class LLMSummarizer:
    """LLM 摘要生成器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or self._load_api_key()
        self.api_url = "https://api.minimaxi.com/anthropic/v1/messages"
        self.model = "MiniMax-M2.7-highspeed"
    
    def _load_api_key(self) -> str:
        """从环境变量或配置文件加载 API Key"""
        import os
        
        # 1. 尝试从环境变量加载
        api_key = os.environ.get("MINIMAX_API_KEY", "")
        if api_key:
            return api_key
        
        # 2. 尝试从 env.sh 加载
        env_file = Path.home() / ".openclaw" / "env.sh"
        if env_file.exists():
            for line in env_file.read_text().split('\n'):
                if line.startswith("export MINIMAX_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
        
        return ""
    
    def _call_llm(self, prompt: str, system: str = "你是一位专业的科技编辑。") -> str:
        """调用 MiniMax Token Plan API（Anthropic 兼容）"""
        if not self.api_key:
            print("  ⚠️ API Key 未配置")
            return ""
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "max_tokens": 500,
                "messages": [
                    {"role": "user", "content": f"{system}\n\n{prompt}"}
                ]
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content_blocks = result.get('content', [])
                for block in content_blocks:
                    if block.get('type') == 'text':
                        return block.get('text', '').strip()
            else:
                print(f"  ⚠️ API 错误: {response.status_code}")
                return ""
        except Exception as e:
            print(f"  ⚠️ 调用失败: {e}")
            return ""
    
    def summarize_paper(self, title: str, abstract: str, arxiv_id: str = "") -> str:
        """
        生成论文中文摘要
        
        Args:
            title: 论文标题
            abstract: 论文摘要
            arxiv_id: arXiv ID（可选）
        
        Returns:
            中文摘要（150-200字）
        """
        prompt = f"""请为以下学术论文撰写一段中文摘要，要求：

1. **风格**：通俗易懂，像给技术同行介绍，不要翻译腔
2. **长度**：150-200字
3. **结构**：问题背景 → 核心方法 → 主要效果
4. **开头**：直接切入主题，不要"本文提出"这类套话
5. **重点**：突出创新点和实际价值

论文标题：{title}

论文摘要：{abstract[:1500]}

请直接输出摘要内容："""
        
        return self._call_llm(prompt, "你是一位专业的学术编辑，擅长用简洁流畅的中文介绍AI论文。")
    
    def summarize_github(self, name: str, description: str, topics: list = None, readme: str = "") -> str:
        """
        生成 GitHub 项目中文简介
        
        Args:
            name: 项目名称
            description: 项目描述
            topics: 项目标签
            readme: README 内容（可选）
        
        Returns:
            中文简介（80-120字）
        """
        topics_str = ", ".join(topics[:5]) if topics else ""
        content = f"项目描述：{description}\n\n"
        if topics_str:
            content += f"标签：{topics_str}\n\n"
        if readme:
            content += f"README片段：{readme[:800]}"
        
        prompt = f"""请为以下 GitHub 项目撰写一段中文简介，要求：

1. **风格**：简洁有力，突出价值
2. **长度**：80-120字
3. **内容**：是什么、能做什么、适合谁用
4. **开头**：直接说项目是什么，不要"这是一个"套话

项目名称：{name}

{content}

请直接输出简介内容："""
        
        return self._call_llm(prompt, "你是一位技术博主，擅长用简洁的语言介绍开源项目。")
    
    def summarize_article(self, title: str, content: str, source: str = "") -> str:
        """
        生成文章中文摘要
        
        Args:
            title: 文章标题
            content: 文章内容
            source: 来源（可选）
        
        Returns:
            中文摘要（150-200字）
        """
        prompt = f"""请为以下技术文章撰写一段中文摘要，要求：

1. **风格**：通俗易懂，像给技术同行介绍
2. **长度**：150-200字
3. **内容**：抓住核心内容和价值点
4. **开头**：直接切入主题，不要"这篇文章介绍了"套话
5. **重点**：突出关键信息和读者能获得什么

文章标题：{title}

文章内容：{content[:1500]}

请直接输出摘要内容："""
        
        return self._call_llm(prompt, "你是一位专业的科技编辑，擅长用简洁流畅的中文介绍技术文章。")


def needs_llm_summary(text: str, original: str) -> bool:
    """
    判断是否需要 LLM 生成摘要
    
    Args:
        text: 当前摘要
        original: 原始内容
    
    Returns:
        True 如果需要生成新摘要
    """
    if not text:
        return True
    if len(text) < 100:
        return True
    # 如果摘要就是原文的截取，需要生成
    if text == original[:len(text)]:
        return True
    return False


def generate_all_summaries(data_file: Path, force: bool = False):
    """
    为所有内容生成 LLM 摘要
    
    Args:
        data_file: 数据文件路径
        force: 是否强制重新生成（即使已有摘要）
    """
    summarizer = LLMSummarizer()
    
    data = json.loads(data_file.read_text(encoding='utf-8'))
    stats = {"papers": 0, "projects": 0, "articles": 0}
    
    # 1. 处理 arXiv 论文
    print("\n" + "=" * 60)
    print("📚 生成 arXiv 论文摘要")
    print("=" * 60)
    arxiv_papers = data.get('arxiv_papers', [])
    for i, paper in enumerate(arxiv_papers):
        arxiv_id = paper.get('arxiv_id', paper.get('id', ''))
        title = paper.get('title', '')
        abstract = paper.get('summary', '')
        cn_summary = paper.get('cn_summary', '')
        
        # 检查是否需要生成
        need_generate = force or needs_llm_summary(cn_summary, abstract)
        
        if need_generate:
            print(f"\n[{i+1}/{len(arxiv_papers)}] {arxiv_id}: {title[:40]}...")
            new_summary = summarizer.summarize_paper(title, abstract, arxiv_id)
            if new_summary:
                paper['cn_summary'] = new_summary
                stats["papers"] += 1
                print(f"  ✅ {new_summary[:60]}...")
                # 每 10 篇保存一次
                if stats["papers"] % 10 == 0:
                    data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
                    print(f"  💾 已保存 {stats['papers']} 篇摘要")
            time.sleep(0.5)  # 避免 API 限流
    
    # 2. 处理 GitHub 项目
    print("\n" + "=" * 60)
    print("🔧 生成 GitHub 项目简介")
    print("=" * 60)
    github_projects = data.get('github_projects', [])
    for i, project in enumerate(github_projects):
        name = project.get('name', '')
        description = project.get('description', '')
        topics = project.get('topics', [])
        cn_description = project.get('cn_description', '')
        
        # 检查是否需要生成
        need_generate = force or needs_llm_summary(cn_description, description)
        
        if need_generate:
            print(f"\n[{i+1}/{len(github_projects)}] {name}")
            new_desc = summarizer.summarize_github(name, description, topics)
            if new_desc:
                project['cn_description'] = new_desc
                stats["projects"] += 1
                print(f"  ✅ {new_desc[:60]}...")
            time.sleep(0.5)
    
    # 3. 处理热门文章
    print("\n" + "=" * 60)
    print("📰 生成热门文章摘要")
    print("=" * 60)
    articles = data.get('articles', data.get('hot_articles', []))
    for i, article in enumerate(articles):
        title = article.get('title', '')
        content = article.get('summary', article.get('content', ''))
        cn_summary = article.get('cn_summary', '')
        
        # 检查是否需要生成
        need_generate = force or needs_llm_summary(cn_summary, content)
        
        if need_generate:
            print(f"\n[{i+1}/{len(articles)}] {title[:40]}...")
            new_summary = summarizer.summarize_article(title, content)
            if new_summary:
                article['cn_summary'] = new_summary
                stats["articles"] += 1
                print(f"  ✅ {new_summary[:60]}...")
            time.sleep(0.5)
    
    # 4. 同步每日精选
    sync_daily_pick_summaries(data)
    
    # 保存数据
    data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print("\n" + "=" * 60)
    print("📊 生成统计")
    print("=" * 60)
    print(f"  论文摘要: {stats['papers']} 篇")
    print(f"  项目简介: {stats['projects']} 个")
    print(f"  文章摘要: {stats['articles']} 篇")
    print(f"\n✅ 数据已保存到: {data_file}")
    
    return stats


def sync_daily_pick_summaries(data: dict):
    """
    同步每日精选的摘要
    
    从 arxiv_papers 和 github_projects 同步到 daily_pick
    """
    daily_pick = data.get('daily_pick', [])
    
    # 构建映射
    arxiv_papers = data.get('arxiv_papers', [])
    arxiv_cn_map = {p.get('arxiv_id', p.get('id', '')): p.get('cn_summary', '') 
                    for p in arxiv_papers if p.get('cn_summary')}
    
    github_projects = data.get('github_projects', [])
    github_cn_map = {p.get('name', ''): p.get('cn_description', '') 
                     for p in github_projects if p.get('cn_description')}
    
    for item in daily_pick:
        item_type = item.get('type', '')
        
        if item_type == 'paper':
            arxiv_id = item.get('arxiv_id', item.get('id', ''))
            if arxiv_id in arxiv_cn_map:
                item['cn_summary'] = arxiv_cn_map[arxiv_id]
                item['cn_description'] = arxiv_cn_map[arxiv_id]
        
        elif item_type == 'github':
            name = item.get('name', '')
            if name in github_cn_map:
                item['cn_description'] = github_cn_map[name]
                item['cn_summary'] = github_cn_map[name]


if __name__ == "__main__":
    import sys
    
    # 默认数据文件
    base_dir = Path(__file__).parent.parent
    today = time.strftime("%Y-%m-%d")
    data_file = base_dir / "daily_data" / f"{today}.json"
    
    # 检查命令行参数
    force = "--force" in sys.argv or "-f" in sys.argv
    
    if not data_file.exists():
        print(f"❌ 数据文件不存在: {data_file}")
        sys.exit(1)
    
    print(f"📄 数据文件: {data_file}")
    print(f"🔄 强制重新生成: {force}")
    
    generate_all_summaries(data_file, force=force)
