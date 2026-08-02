#!/usr/bin/env python3
"""
llm/factory.py - LLM 模型工厂
"""

from typing import Optional, Dict, Any
import os
from pathlib import Path

# Bypass any proxy settings (Windows system proxy can break API calls)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'


class LLMProvider:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get('model', 'default')
        self.api_key = config.get('api_key', '')
        self.base_url = config.get('base_url', '')

    def chat(self, messages: list, **kwargs) -> str:
        raise NotImplementedError

    def summarize(self, text: str, max_length: int = 200) -> str:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key', os.environ.get('OPENAI_API_KEY', ''))
        self.base_url = config.get('base_url', 'https://api.openai.com/v1')

    def chat(self, messages: list, **kwargs) -> str:
        try:
            import httpx
            from openai import OpenAI
            # trust_env=False: ignore any system/registry proxy for API calls
            http_client = httpx.Client(trust_env=False, verify=True)
            client = OpenAI(api_key=self.api_key, base_url=self.base_url, http_client=http_client)
            response = client.chat.completions.create(
                model=self.model, messages=messages, **kwargs
            )
            return response.choices[0].message.content or ''
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def summarize(self, text: str, max_length: int = 200) -> str:
        messages = [
            {"role": "system", "content": f"用中文概括为{max_length}字以内的摘要，保留关键信息。"},
            {"role": "user", "content": text}
        ]
        return self.chat(messages, max_tokens=max_length)


class DeepSeekProvider(OpenAIProvider):
    def __init__(self, config: Dict[str, Any]):
        config.setdefault('base_url', 'https://api.deepseek.com/v1')
        config.setdefault('model', 'deepseek-chat')
        super().__init__(config)


class MiniMaxProvider(OpenAIProvider):
    def __init__(self, config: Dict[str, Any]):
        # Token Plan Subscription Key uses api.minimaxi.com/v1 (OpenAI-compatible)
        config.setdefault('base_url', 'https://api.minimaxi.com/v1')
        config.setdefault('model', 'MiniMax-M3')
        if not config.get('api_key'):
            config['api_key'] = os.environ.get('MINIMAX_API_KEY', os.environ.get('LLM_API_KEY', ''))
        super().__init__(config)


class ModelFactory:
    PROVIDERS = {
        'openai': OpenAIProvider,
        'deepseek': DeepSeekProvider,
        'minimax': MiniMaxProvider,
    }

    @classmethod
    def create(cls, config: Dict[str, Any]) -> LLMProvider:
        provider_name = config.get('provider', 'openai').lower()
        provider_class = cls.PROVIDERS.get(provider_name)
        if not provider_class:
            raise ValueError(f"不支持的 LLM 提供商: {provider_name}，支持: {list(cls.PROVIDERS.keys())}")
        return provider_class(config)

    @classmethod
    def from_yaml(cls, config_path: Path) -> LLMProvider:
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except ImportError:
            raise ImportError("PyYAML 未安装。运行: pip install pyyaml")
        llm_config = config.get('llm', {})
        return cls.create(llm_config)

    @classmethod
    def from_env(cls) -> LLMProvider:
        config = {
            'provider': os.environ.get('LLM_PROVIDER', 'openai'),
            'model': os.environ.get('LLM_MODEL', 'gpt-4o'),
            'api_key': os.environ.get('LLM_API_KEY', ''),
            'base_url': os.environ.get('LLM_BASE_URL', ''),
        }
        return cls.create(config)
