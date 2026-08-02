#!/usr/bin/env python3
"""Test MiniMax API with proxy bypass."""
import os, sys
from pathlib import Path

# Clear ALL proxy settings including those that httpx/requests might use
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("ALL_PROXY", None)
os.environ.pop("all_proxy", None)
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

sys.path.insert(0, str(Path(__file__).parent))
from llm.factory import ModelFactory

api_key = os.environ.get("MINIMAX_API_KEY", "")
config = {"provider": "minimax", "model": "MiniMax-M2.7",
          "api_key": api_key, "base_url": "https://api.minimaxi.com/v1"}

# Test with httpx directly, bypassing proxy
import httpx

# Try direct connection first
try:
    client = httpx.Client(verify=True, proxies=None, follow_redirects=True)
    r = client.get("https://api.minimaxi.com/v1", timeout=10)
    print(f"Direct (proxies=None): status={r.status_code}")
except Exception as e:
    print(f"Direct failed: {e}")

# Try with explicit no proxy env
try:
    r = httpx.get("https://api.minimaxi.com/v1", timeout=10)
    print(f"Default httpx: status={r.status_code}")
except Exception as e:
    print(f"Default failed: {e}")

# Try with the openai library directly
try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url="https://api.minimaxi.com/v1", http_client=httpx.Client(proxies=None, verify=True))
    resp = client.chat.completions.create(
        model="MiniMax-M2.7",
        messages=[{"role": "user", "content": "Hello, say hi in one word."}],
        max_tokens=10,
        temperature=0.3
    )
    print(f"OpenAI client: {resp.choices[0].message.content}")
except Exception as e:
    print(f"OpenAI failed: {e}")
