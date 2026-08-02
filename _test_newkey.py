#!/usr/bin/env python3
"""Test new MiniMax Token Plan Key with MiniMax-M3."""
import os, sys
from pathlib import Path

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

sys.path.insert(0, str(Path(__file__).parent))
from llm.factory import ModelFactory

NEW_KEY = "sk-cp-uk1Twy3ft8Yw5toDxIGJS-Uv1xM52xBvu7nIKTgETcRnZoTmWvUN2kv1XAjLpCuHkLJwKuxBDqb8Rt61t3vzLXDprLkw_ZKwxaRTI7nkoc4OKsU6bwp7PrU"

config = {"provider": "minimax", "model": "MiniMax-M3",
          "api_key": NEW_KEY, "base_url": "https://api.minimaxi.com/v1"}

import httpx, openai
print(f"httpx: {httpx.__version__}, openai: {openai.__version__}")

try:
    llm = ModelFactory.create(config)
    print(f"LLM created: {type(llm).__name__}, model={llm.model}")
    resp = llm.chat([
        {"role": "system", "content": "你是AI论文摘要助手。请用中文将以下内容概括为200字以内的摘要，保留核心技术点和价值。只输出摘要本身，不要输出思考过程。"},
        {"role": "user", "content": "标题：Transformer。摘要：We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."}
    ], max_tokens=300, temperature=0.3)
    resp = resp.replace("<think>", "").replace("</think>", "").strip()
    print(f"SUCCESS | model=MiniMax-M3 | len={len(resp)}")
    print(f"RESPONSE: {resp}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
    sys.exit(1)
