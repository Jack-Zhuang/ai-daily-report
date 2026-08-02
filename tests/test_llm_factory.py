#!/usr/bin/env python3
"""Tests for llm/factory.py — ModelFactory and provider hierarchy."""

import os
from pathlib import Path

import pytest

from llm.factory import (
    LLMProvider,
    ModelFactory,
    OpenAIProvider,
    DeepSeekProvider,
    MiniMaxProvider,
)

# ── LLMProvider base class ──────────────────────────────────


class TestLLMProvider:
    def test_base_chat_not_implemented(self):
        provider = LLMProvider({"model": "test"})
        with pytest.raises(NotImplementedError):
            provider.chat([{"role": "user", "content": "hi"}])

    def test_base_summarize_not_implemented(self):
        provider = LLMProvider({"model": "test"})
        with pytest.raises(NotImplementedError):
            provider.summarize("some text")

    def test_default_api_key_empty(self):
        provider = LLMProvider({})
        assert provider.api_key == ""
        assert provider.base_url == ""
        assert provider.model == "default"


# ── ModelFactory.create() ───────────────────────────────────


class TestModelFactoryCreate:
    def test_create_openai(self):
        config = {"provider": "openai", "api_key": "sk-test", "model": "gpt-4o"}
        provider = ModelFactory.create(config)
        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-4o"
        assert provider.api_key == "sk-test"

    def test_create_deepseek(self):
        config = {"provider": "deepseek", "api_key": "sk-test"}
        provider = ModelFactory.create(config)
        assert isinstance(provider, DeepSeekProvider)
        assert provider.model == "deepseek-chat"
        assert "deepseek.com" in provider.base_url

    def test_create_minimax(self):
        config = {"provider": "minimax", "api_key": "sk-test"}
        provider = ModelFactory.create(config)
        assert isinstance(provider, MiniMaxProvider)
        assert provider.model == "MiniMax-M3"
        assert "minimaxi.com" in provider.base_url

    def test_create_case_insensitive(self):
        config = {"provider": "MiniMax", "api_key": "sk-test"}
        provider = ModelFactory.create(config)
        assert isinstance(provider, MiniMaxProvider)

    def test_create_unsupported_provider_raises(self):
        config = {"provider": "unknown"}
        with pytest.raises(ValueError, match="不支持的 LLM 提供商"):
            ModelFactory.create(config)

    def test_create_default_provider_is_openai(self):
        """When provider is missing, default to openai."""
        config = {"api_key": "sk-test"}
        provider = ModelFactory.create(config)
        assert isinstance(provider, OpenAIProvider)


# ── ModelFactory.from_yaml() ────────────────────────────────


class TestModelFactoryFromYaml:
    def test_from_yaml_minimax(self, temp_yaml_config: Path):
        provider = ModelFactory.from_yaml(temp_yaml_config)
        assert isinstance(provider, MiniMaxProvider)
        assert provider.model == "MiniMax-M3"
        assert provider.api_key == "sk-test-key-123"

    def test_from_yaml_missing_file(self, tmp_path: Path):
        missing = tmp_path / "nonexistent.yaml"
        with pytest.raises(FileNotFoundError):
            ModelFactory.from_yaml(missing)


# ── ModelFactory.from_env() ─────────────────────────────────


class TestModelFactoryFromEnv:
    def test_from_env_minimax(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "minimax")
        monkeypatch.setenv("LLM_MODEL", "MiniMax-M3")
        monkeypatch.setenv("LLM_API_KEY", "env-key")
        monkeypatch.setenv("LLM_BASE_URL", "https://custom.minimax.com/v1")

        provider = ModelFactory.from_env()
        assert isinstance(provider, MiniMaxProvider)
        assert provider.model == "MiniMax-M3"
        assert provider.api_key == "env-key"
        assert provider.base_url == "https://custom.minimax.com/v1"

    def test_from_env_defaults(self, mock_env_clean):
        provider = ModelFactory.from_env()
        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-4o"
        assert provider.api_key == ""


# ── Provider inheritance & defaults ─────────────────────────


class TestProviderDefaults:
    def test_openai_default_base_url(self):
        p = OpenAIProvider({"api_key": "sk"})
        assert p.base_url == "https://api.openai.com/v1"

    def test_openai_reads_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "env-openai-key")
        p = OpenAIProvider({})
        assert p.api_key == "env-openai-key"

    def test_deepseek_inherits_openai_chat(self):
        """DeepSeekProvider does not override chat(), inherits from OpenAIProvider."""
        assert DeepSeekProvider.chat is OpenAIProvider.chat

    def test_deepseek_default_overrides(self):
        p = DeepSeekProvider({"api_key": "sk"})
        assert p.base_url == "https://api.deepseek.com/v1"
        assert p.model == "deepseek-chat"

    def test_minimax_reads_from_minimax_env(self, monkeypatch):
        monkeypatch.setenv("MINIMAX_API_KEY", "minimax-env-key")
        p = MiniMaxProvider({})
        assert p.api_key == "minimax-env-key"

    def test_minimax_fallback_to_llm_api_key_env(self, monkeypatch):
        # 非封闭测试修复：必须清掉 MINIMAX_API_KEY，否则本机/CI 配置了真实 key 时
        # 会优先命中 MINIMAX_API_KEY 导致断言失败（环境依赖）
        monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
        monkeypatch.setenv("LLM_API_KEY", "fallback-key")
        p = MiniMaxProvider({})
        assert p.api_key == "fallback-key"

    def test_minimax_prefers_minimax_env_over_llm_env(self, monkeypatch):
        monkeypatch.setenv("MINIMAX_API_KEY", "mini-key")
        monkeypatch.setenv("LLM_API_KEY", "llm-key")
        p = MiniMaxProvider({})
        assert p.api_key == "mini-key"


# ── Proxy bypass sanity check ───────────────────────────────


class TestProxyBypass:
    def test_proxy_vars_cleared_on_import(self):
        """Verify llm/factory.py clears proxy env vars on import."""
        # We can't easily re-test import side-effects, but we can verify
        # the module-level code is present by reading the source.
        import llm.factory as factory_mod

        source = Path(factory_mod.__file__).read_text(encoding="utf-8")
        assert "os.environ.pop('HTTP_PROXY'" in source
        assert "NO_PROXY" in source
