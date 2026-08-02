"""pytest configuration and shared fixtures."""

import os
import pytest
from pathlib import Path


@pytest.fixture
def temp_yaml_config(tmp_path: Path) -> Path:
    """Create a temporary YAML config file for testing."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "llm:\n"
        "  provider: minimax\n"
        "  model: MiniMax-M3\n"
        "  api_key: sk-test-key-123\n"
        "  base_url: https://api.minimaxi.com/v1\n",
        encoding="utf-8",
    )
    return config_path


@pytest.fixture
def mock_env_clean(monkeypatch):
    """Clear LLM-related env vars before each test."""
    for key in [
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_API_KEY",
        "LLM_BASE_URL",
        "MINIMAX_API_KEY",
        "OPENAI_API_KEY",
    ]:
        monkeypatch.delenv(key, raising=False)
