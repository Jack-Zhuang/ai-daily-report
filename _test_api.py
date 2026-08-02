#!/usr/bin/env python3
"""Test MiniMax API call with timeout."""
import os, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from llm.factory import ModelFactory

api_key = os.environ.get("MINIMAX_API_KEY", "")
if not api_key:
    print("NO API KEY")
    exit(1)

config = {"provider": "minimax", "model": "MiniMax-M2.7",
          "api_key": api_key, "base_url": "https://api.minimaxi.com/v1"}

try:
    import httpx
    # Test connectivity first
    r = httpx.get("https://api.minimaxi.com/v1", timeout=10)
    print(f"Connectivity: status={r.status_code}")
except Exception as e:
    print(f"Connectivity issue: {e}")

try:
    llm = ModelFactory.create(config)
    print(f"LLM created: {type(llm).__name__}")
    
    resp = llm.chat([
        {"role": "system", "content": "用中文回答：你好，测试连接。"},
        {"role": "user", "content": "你好"}
    ], max_tokens=50, temperature=0.3)
    print(f"Response: {resp[:100]}")
except Exception as e:
    print(f"Error: {e}")
