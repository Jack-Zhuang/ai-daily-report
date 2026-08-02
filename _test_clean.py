#!/usr/bin/env python3
"""Test cleaning MiniMax-M3 thinking preamble from responses."""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"C:\Users\HUAWEI\.openclaw\workspace\ai-daily-report")
import llm_summarizer as ls

def clean(resp):
    resp = re.sub(r'</?think>', '', resp).strip()
    paras = [p.strip() for p in re.split(r'\n\s*\n', resp) if p.strip()]
    cn_paras = [p for p in paras if re.search(r'[\u4e00-\u9fff]', p)]
    return cn_paras[-1] if cn_paras else resp

p = ls._get_llm_provider()
print("provider:", type(p).__name__, "| model:", p.model)
raw = p.chat([
    {"role": "system", "content": "你是AI论文摘要助手。请用中文将以下内容概括为200字以内的摘要，保留核心技术点和价值。只输出摘要本身。"},
    {"role": "user", "content": "标题：Transformer\n摘要：We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."}
], max_tokens=400, temperature=0.3)
print("=== RAW ===")
print(raw)
print("=== CLEANED ===")
print(clean(raw))
