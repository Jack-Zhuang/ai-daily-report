#!/usr/bin/env python3
"""Tests for processors/ — normalizer.py and dedup.py."""

import pytest

from processors.normalizer import (
    FieldNormalizer,
    DateNormalizer,
    ContentNormalizer,
)
from processors.dedup import (
    TextDeduplicator,
    DailyPickDeduplicator,
)

# ── FieldNormalizer ─────────────────────────────────────────


class TestFieldNormalizer:
    def test_normalize_maps_alias_to_target(self):
        item = {"chinese_title": "中文标题", "summary": "摘要内容"}
        result = FieldNormalizer.normalize(item)
        assert result["cn_title"] == "中文标题"
        assert result["summary"] == "摘要内容"

    def test_normalize_keeps_existing_target(self):
        """If target field already exists, don't overwrite with alias."""
        item = {"cn_title": "已有标题", "chinese_title": "另一个标题"}
        result = FieldNormalizer.normalize(item)
        assert result["cn_title"] == "已有标题"

    def test_normalize_no_falsy_overwrite(self):
        """Empty string / None alias should not overwrite existing target."""
        item = {"cn_title": "", "chinese_title": "有效标题"}
        result = FieldNormalizer.normalize(item)
        assert result["cn_title"] == "有效标题"

    def test_normalize_passthrough_unknown_fields(self):
        item = {"unknown_field": "value"}
        result = FieldNormalizer.normalize(item)
        assert result["unknown_field"] == "value"

    def test_normalize_batch(self):
        items = [
            {"chinese_title": "标题1"},
            {"title_cn": "标题2"},
        ]
        results = FieldNormalizer.normalize_batch(items)
        assert results[0]["cn_title"] == "标题1"
        assert results[1]["cn_title"] == "标题2"

    def test_all_target_fields_in_map(self):
        """Every target in FIELD_MAP should be a key we try to normalize."""
        assert "cn_title" in FieldNormalizer.FIELD_MAP
        assert "stars" in FieldNormalizer.FIELD_MAP
        assert "category" in FieldNormalizer.FIELD_MAP


# ── DateNormalizer ──────────────────────────────────────────


class TestDateNormalizer:
    def test_iso_date(self):
        assert DateNormalizer.normalize("2024-03-15") == "2024-03-15"

    def test_iso_datetime(self):
        assert DateNormalizer.normalize("2024-03-15T09:30:00") == "2024-03-15"

    def test_rfc2822_date_truncated_fallback(self):
        """Normalizer truncates to 19 chars first, so long RFC2822 falls back."""
        assert DateNormalizer.normalize("Fri, 15 Mar 2024 09:30:00") == "Fri, 15 Ma"

    def test_empty_returns_none(self):
        assert DateNormalizer.normalize("") is None
        assert DateNormalizer.normalize(None) is None

    def test_unparseable_fallback(self):
        assert DateNormalizer.normalize("random string") == "random str"

    def test_short_string(self):
        assert DateNormalizer.normalize("ab") == "ab"


# ── ContentNormalizer ───────────────────────────────────────


class TestContentNormalizer:
    def test_truncate_under_limit(self):
        text = "短文本"
        assert ContentNormalizer.truncate_summary(text, max_len=80) == text

    def test_truncate_over_limit(self):
        text = "A" * 100
        result = ContentNormalizer.truncate_summary(text, max_len=80)
        assert result.endswith("...")
        assert len(result) == 83  # 80 + "..."

    def test_truncate_empty(self):
        assert ContentNormalizer.truncate_summary("", max_len=80) == ""
        assert ContentNormalizer.truncate_summary(None, max_len=80) == ""

    def test_clean_html(self):
        raw = "<p>Hello <b>world</b></p>"
        assert ContentNormalizer.clean_html(raw) == "Hello world"

    def test_clean_html_empty(self):
        assert ContentNormalizer.clean_html("") == ""
        assert ContentNormalizer.clean_html(None) == ""

    def test_classify_agent(self):
        assert ContentNormalizer.classify_by_keywords("多智能体协作系统") == "agent"
        assert (
            ContentNormalizer.classify_by_keywords("Autonomous agent framework")
            == "agent"
        )

    def test_classify_llm(self):
        assert ContentNormalizer.classify_by_keywords("大语言模型微调") == "llm"
        assert (
            ContentNormalizer.classify_by_keywords("GPT-4 prompt engineering") == "llm"
        )

    def test_classify_rec_default(self):
        assert ContentNormalizer.classify_by_keywords("推荐算法改进") == "rec"
        assert ContentNormalizer.classify_by_keywords("random stuff") == "rec"


# ── TextDeduplicator ────────────────────────────────────────


class TestTextDeduplicator:
    def test_duplicate_title(self):
        dedup = TextDeduplicator()
        assert dedup.is_duplicate_title("Hello World") is False
        assert dedup.is_duplicate_title("hello world") is True  # case-insensitive
        assert dedup.is_duplicate_title("Hello, World!") is True  # punctuation stripped

    def test_duplicate_url(self):
        dedup = TextDeduplicator()
        assert dedup.is_duplicate_url("https://a.com/1") is False
        assert dedup.is_duplicate_url("https://a.com/1") is True
        assert dedup.is_duplicate_url("") is False

    def test_is_duplicate_item(self):
        dedup = TextDeduplicator()
        item = {"title": "Test", "link": "https://a.com"}
        assert dedup.is_duplicate(item) is False
        assert dedup.is_duplicate({"title": "Test"}) is True
        assert dedup.is_duplicate({"link": "https://a.com"}) is True

    def test_reset(self):
        dedup = TextDeduplicator()
        dedup.is_duplicate_title("Title A")
        dedup.reset()
        assert dedup.is_duplicate_title("Title A") is False

    def test_normalize_title_strips_punctuation(self):
        assert TextDeduplicator._normalize_title("A, B & C!") == "abc"
        assert TextDeduplicator._normalize_title("  中文  标题  ") == "中文标题"


# ── DailyPickDeduplicator ───────────────────────────────────


class TestDailyPickDeduplicator:
    def test_dedup_by_title(self):
        pick = [
            {"title": "A", "link": "https://a.com"},
            {"title": "B", "link": "https://b.com"},
            {"title": "A", "link": "https://a2.com"},  # dup
        ]
        result = DailyPickDeduplicator.dedup_daily_pick(pick)
        assert len(result) == 2
        assert result[0]["title"] == "A"
        assert result[1]["title"] == "B"

    def test_dedup_fallback_to_cn_title(self):
        pick = [
            {"cn_title": "标题1"},
            {"name": "标题1"},  # dup via fallback
        ]
        result = DailyPickDeduplicator.dedup_daily_pick(pick)
        assert len(result) == 1

    def test_filter_pick_overlap(self):
        daily_pick = [{"cn_title": "已选文章"}]
        articles = [
            {"cn_title": "已选文章", "link": "https://a.com"},
            {"cn_title": "新文章", "link": "https://b.com"},
        ]
        result = DailyPickDeduplicator.filter_pick_overlap(daily_pick, articles)
        assert len(result) == 1
        assert result[0]["cn_title"] == "新文章"

    def test_filter_pick_empty(self):
        assert DailyPickDeduplicator.filter_pick_overlap([], [{"title": "T"}]) == [
            {"title": "T"}
        ]
