#!/usr/bin/env python3
"""Test MiniMax API chat via openai library."""
import os, sys
from pathlib import Path

os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

sys.path.insert(0, str(Path(__file__).parent))
from llm.factory import ModelFactory

api_key = os.environ.get("MINIMAX_API_KEY", "")
config = {"provider": "minimax", "model": "MiniMax-M2.7",
          "api_key": api_key, "base_url": "https://api.minimaxi.com/v1"}

import httpx
# Check httpx version
print(f"httpx version: {httpx.__version__}")

# Create http client without proxy
import openai
print(f"openai version: {openai.__version__}")

# Method 1: Use the factory
try:
    llm = ModelFactory.create(config)
    print(f"LLM created: {type(llm).__name__}")
    resp = llm.chat([
        {"role": "system", "content": "用中文回答：你好，测试连接。"},
        {"role": "user", "content": "你好"}
    ], max_tokens=50, temperature=0.3)
    print(f"Response: {resp}")
except Exception as e:
    print(f"Factory method failed: {e}")

# Method 2: Direct openai client
try:
    import httpx
    http_client = httpx.Client(verify=True)
    client = openai.OpenAI(api_key=api_key, base_url="https://api.minimaxi.com/v1", http_client=http_client)
    resp = client.chat.completions.create(
        model="MiniMax-M2.7",
        messages=[{"role": "system", "content": "用中文回答：你好。"}, {"role": "user", "content": "你好"}],
        max_tokens=50,
        temperature=0.3
    )
    print(f"Direct OpenAI: {resp.choices[0].message.content}")
except Exception as e:
    print(f"Direct OpenAI failed: {e}")
