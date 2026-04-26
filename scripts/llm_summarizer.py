#!/usr/bin/env python3
"""
LLM 摘要生成器 - 统一的摘要生成模块

支持：
- 论文摘要生成
- GitHub 项目简介生成
- 文章摘要生成

注意：由于外部 API 可能不可用，此模块提供规则基础的摘要生成
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, Any

class LLMSummarizer:
    """LLM 摘要生成器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        # 不再依赖外部 API
    
    def summarize_paper(self, title: str, abstract: str, arxiv_id: str = "") -> str:
        """
        生成论文中文摘要
        
        使用规则基础的方法生成摘要：
        1. 提取第一句话作为背景
        2. 提取关键方法词
        3. 组合成简洁摘要
        """
        if not abstract:
            return f"论文探讨了{title}相关问题。"
        
        # 提取第一句话
        sentences = re.split(r'[.!?]', abstract)
        first_sentence = sentences[0].strip() if sentences else ""
        
        # 简单翻译关键词
        keywords = {
            'propose': '提出',
            'introduce': '引入',
            'present': '呈现',
            'demonstrate': '证明',
            'show': '展示',
            'achieve': '实现',
            'improve': '改进',
            'novel': '新颖的',
            'new': '新的',
            'method': '方法',
            'approach': '方法',
            'framework': '框架',
            'model': '模型',
            'system': '系统',
            'algorithm': '算法',
            'technique': '技术',
        }
        
        # 生成摘要
        if len(first_sentence) > 200:
            summary = first_sentence[:200] + "..."
        else:
            summary = first_sentence
        
        # 如果摘要是英文，返回提示
        if re.match(r'^[A-Za-z]', summary):
            return f"本研究探讨了{title[:50]}...相关课题。" + f" 核心内容：{abstract[:150]}..."
        
        return summary
    
    def summarize_github(self, name: str, description: str, topics: list = None, readme: str = "") -> str:
        """
        生成 GitHub 项目中文简介
        
        使用规则基础的方法生成简介
        """
        if not description:
            return f"{name} 是一个开源项目。"
        
        # 如果描述已经是中文，直接返回
        if re.search(r'[\u4e00-\u9fff]', description):
            return description[:120]
        
        # 简单翻译
        keywords = {
            'A ': '一个',
            'An ': '一个',
            'The ': '',
            'tool': '工具',
            'library': '库',
            'framework': '框架',
            'for': '用于',
            'to': '用于',
        }
        
        # 返回描述的前120字符
        return description[:120] if len(description) > 120 else description
    
    def summarize_article(self, title: str, content: str, source: str = "") -> str:
        """
        生成文章中文摘要
        
        使用规则基础的方法生成摘要
        """
        if not content:
            return f"文章《{title}》讨论了相关话题。"
        
        # 如果内容已经是中文，提取关键句子
        if re.search(r'[\u4e00-\u9fff]', content):
            # 提取前几句
            sentences = re.split(r'[。！？\n]', content)
            valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:3]
            if valid_sentences:
                return ''.join(valid_sentences)[:200]
            return content[:200]
        
        # 英文内容，返回前200字符
        return content[:200]


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
    today = __import__('time').strftime("%Y-%m-%d")
    data_file = base_dir / "daily_data" / f"{today}.json"
    
    if not data_file.exists():
        print(f"❌ 数据文件不存在: {data_file}")
        sys.exit(1)
    
    data = json.loads(data_file.read_text(encoding='utf-8'))
    sync_daily_pick_summaries(data)
    data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ 摘要同步完成")

