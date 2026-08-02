#!/usr/bin/env python3
"""Tests for llm_summarizer.py — response cleaning and summary helpers."""

import pytest

from llm_summarizer import clean_llm_response, needs_llm_summary

# ── clean_llm_response() ────────────────────────────────────


class TestCleanLLMResponse:
    def test_removes_think_tags(self):
        raw = "<think>推理中...</think>\n\n这是最终摘要。"
        assert clean_llm_response(raw) == "这是最终摘要。"

    def test_removes_thinking_tags(self):
        """Code only strips tags, not content inside."""
        raw = "<thinking>思考过程</thinking>结论在这里。"
        assert clean_llm_response(raw) == "思考过程结论在这里。"

    def test_picks_last_chinese_paragraph(self):
        raw = "First paragraph in English.\n\n第二段中文摘要。\n\n最后一段才是精华。"
        assert clean_llm_response(raw) == "最后一段才是精华。"

    def test_no_chinese_falls_back_to_full(self):
        raw = "Only English text here."
        assert clean_llm_response(raw) == "Only English text here."

    def test_empty_input(self):
        assert clean_llm_response("") == ""
        assert clean_llm_response(None) == ""

    def test_whitespace_only(self):
        assert clean_llm_response("   \n\n   ") == ""

    def test_single_chinese_paragraph(self):
        raw = "只有一段中文。"
        assert clean_llm_response(raw) == "只有一段中文。"


# ── needs_llm_summary() ─────────────────────────────────────


class TestNeedsLLMSummary:
    def test_empty_cn_summary(self):
        assert needs_llm_summary("", "original text here") is True

    def test_short_cn_summary(self):
        assert needs_llm_summary("太短", "original") is True

    def test_long_enough_cn_summary(self):
        long_summary = (
            "这是一段明显超过三十个字符的中文摘要内容，完全不需要重新生成了。"
        )
        assert len(long_summary) > 30
        assert needs_llm_summary(long_summary, "original") is False

    def test_none_cn_summary(self):
        assert needs_llm_summary(None, "original") is True

    def test_exactly_30_chars(self):
        s30 = "x" * 30
        assert needs_llm_summary(s30, "original") is True  # 30 is not > 30

    def test_31_chars(self):
        s31 = "x" * 31
        assert needs_llm_summary(s31, "original") is False  # 31 > 30
