#!/usr/bin/env python3
"""Test MiniMax models to find one that works well."""
import os, sys, json
from pathlib import Path

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

sys.path.insert(0, str(Path(__file__).parent))
from llm.factory import ModelFactory

api_key = os.environ.get("MINIMAX_API_KEY", "")

# Test different models
models_to_test = [
    "MiniMax-M3",
    "MiniMax-M2.7",
    "MiniMax-Text-01",
    "MiniMax-T2.0",
]
test_prompt = "用中文概括以下论文：标题：Transformer是一种用于序列转导的模型架构，主要依赖注意力机制。摘要：We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."

for model_name in models_to_test:
    print(f"\n--- Testing {model_name} ---")
    config = {"provider": "minimax", "model": model_name,
              "api_key": api_key, "base_url": "https://api.minimaxi.com/v1"}
    try:
        llm = ModelFactory.create(config)
        resp = llm.chat([
            {"role": "system", "content": "你是一个AI论文摘要助手。请用中文将以下内容概括为200字以内的摘要，保留核心技术点和价值。只输出摘要本身，不要输出思考过程。"},
            {"role": "user", "content": test_prompt}
        ], max_tokens=300, temperature=0.3)
        
        # Clean
        for tag in ["<think>", "</think>", "<thought>", "</thought>", "<｜end▁of▁thinking｜>", " /think>"]:
            resp = resp.replace(tag, "")
        resp = resp.strip()
        
        # Check if response is useful
        has_thinking = "概括" in resp[:30] or "让我" in resp[:30]
        print(f"  Length: {len(resp)} chars")
        print(f"  First 100 chars: {resp[:100]}")
        print(f"  Has thinking meta: {has_thinking}")
        
    except Exception as e:
        print(f"  Error: {e}")
