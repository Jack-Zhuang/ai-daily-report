#!/usr/bin/env python3
"""
processors/dedup.py - 内容去重模块
"""

from typing import List, Dict, Set, Any


class TextDeduplicator:
    def __init__(self):
        self._seen_titles: Set[str] = set()
        self._seen_urls: Set[str] = set()

    def reset(self):
        self._seen_titles.clear()
        self._seen_urls.clear()

    def is_duplicate_title(self, title: str) -> bool:
        normalized = self._normalize_title(title)
        if normalized in self._seen_titles:
            return True
        self._seen_titles.add(normalized)
        return False

    def is_duplicate_url(self, url: str) -> bool:
        if not url:
            return False
        if url in self._seen_urls:
            return True
        self._seen_urls.add(url)
        return False

    def is_duplicate(self, item: Dict[str, Any]) -> bool:
        title = item.get('title', item.get('cn_title', item.get('name', '')))
        url = item.get('link', item.get('url', ''))
        return self.is_duplicate_title(title) or self.is_duplicate_url(url)

    @staticmethod
    def _normalize_title(title: str) -> str:
        import re
        normalized = title.lower().strip()
        normalized = re.sub(r'[^\w\u4e00-\u9fff]', '', normalized)
        return normalized


class DailyPickDeduplicator:
    @staticmethod
    def dedup_daily_pick(daily_pick: List[Dict]) -> List[Dict]:
        seen_titles = set()
        result = []
        for item in daily_pick:
            title = item.get('title', item.get('cn_title', item.get('name', '')))
            if title in seen_titles:
                continue
            seen_titles.add(title)
            result.append(item)
        return result

    @staticmethod
    def filter_pick_overlap(daily_pick: List[Dict], articles: List[Dict]) -> List[Dict]:
        pick_titles = set()
        for item in daily_pick:
            title = item.get('cn_title', item.get('title', item.get('name', '')))
            pick_titles.add(title)
        return [a for a in articles if a.get('cn_title', a.get('title', '')) not in pick_titles]
