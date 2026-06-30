#!/usr/bin/env python3
"""
processors/normalizer.py - 数据标准化模块
"""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime


class FieldNormalizer:
    FIELD_MAP = {
        'cn_title': ['cn_title', 'chinese_title', 'title_cn'],
        'title': ['title', 'name', 'article_title', 'paper_title'],
        'cn_summary': ['cn_summary', 'chinese_summary', 'cn_description'],
        'summary': ['summary', 'abstract', 'description', 'desc'],
        'link': ['link', 'url', 'href', 'source_url'],
        'id': ['id', 'article_id', 'paper_id', '_id'],
        'arxiv_id': ['arxiv_id', 'arxiv', 'eprint'],
        'authors': ['authors', 'author', 'creators'],
        'date': ['date', 'published', 'pub_date', 'created_at', 'updated_at'],
        'source': ['source', 'source_name', 'origin'],
        'category': ['category', 'categories', 'topic', 'type'],
        'stars': ['stars', 'stargazers_count', 'star_count'],
        'forks': ['forks', 'forks_count', 'fork_count'],
        'views': ['views', 'view_count', 'read_count'],
        'likes': ['likes', 'like_count', 'upvotes'],
    }

    @classmethod
    def normalize(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(item)
        for target, aliases in cls.FIELD_MAP.items():
            if target not in result or not result[target]:
                for alias in aliases:
                    if alias != target and alias in result and result[alias]:
                        result[target] = result[alias]
                        break
        return result

    @classmethod
    def normalize_batch(cls, items: List[Dict]) -> List[Dict]:
        return [cls.normalize(item) for item in items]


class DateNormalizer:
    DATE_PATTERNS = [
        ('%Y-%m-%d', r'\d{4}-\d{2}-\d{2}'),
        ('%Y-%m-%dT%H:%M:%S', r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'),
        ('%a, %d %b %Y %H:%M:%S', r'\w{3}, \d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2}'),
    ]

    @classmethod
    def normalize(cls, date_str: Optional[str]) -> Optional[str]:
        if not date_str:
            return None
        date_str = str(date_str)[:19]
        for fmt, _ in cls.DATE_PATTERNS:
            try:
                dt = datetime.strptime(date_str[:len(datetime.now().strftime(fmt))], fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        return date_str[:10] if len(date_str) >= 10 else date_str


class ContentNormalizer:
    @staticmethod
    def truncate_summary(text: str, max_len: int = 80) -> str:
        if not text:
            return ''
        return text[:max_len] + '...' if len(text) > max_len else text

    @staticmethod
    def clean_html(text: str) -> str:
        if not text:
            return ''
        return re.sub(r'<[^>]+>', '', text)

    @staticmethod
    def classify_by_keywords(text: str) -> str:
        text_lower = text.lower()
        if any(kw in text_lower for kw in ['agent', '智能体', '多智能体', 'autonomous', '自主']):
            return 'agent'
        if any(kw in text_lower for kw in ['llm', '大模型', 'gpt', 'claude', 'llama',
                                            'transformer', '语言模型', 'prompt', 'rag']):
            return 'llm'
        return 'rec'
