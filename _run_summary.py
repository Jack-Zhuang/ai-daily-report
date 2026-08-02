#!/usr/bin/env python3
"""Run LLM summarization for today's papers with timeout and proxy bypass."""
import os, sys, json, time, io
from pathlib import Path

# Set UTF-8 encoding for stdout/stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
from llm.factory import ModelFactory

api_key = os.environ.get("MINIMAX_API_KEY", "")
today = "2026-07-20"
data_file = BASE / "daily_data" / f"{today}.json"

if not data_file.exists():
    print(f"Data file not found: {data_file}")
    exit(1)

data = json.loads(data_file.read_text(encoding="utf-8"))
papers = data.get("arxiv_papers", [])
if not papers:
    print("No papers to summarize")
    exit(0)

print(f"Found {len(papers)} papers. Checking existing summaries...")
to_do = [p for p in papers if not p.get("cn_summary") or len(p.get("cn_summary", "")) <= 30]
print(f"Papers needing summary: {len(to_do)}/{len(papers)}")

if not to_do:
    print("All papers already have summaries. Skipping LLM.")
    exit(0)

config = {"provider": "minimax", "model": "MiniMax-M2.7",
          "api_key": api_key, "base_url": "https://api.minimaxi.com/v1"}

llm = ModelFactory.create(config)
print(f"LLM initialized: {type(llm).__name__}")

success = 0
for i, paper in enumerate(to_do):
    title = str(paper.get("title", ""))
    text = str(paper.get("summary", ""))
    if not text:
        continue
    
    print(f"  [{i+1}/{len(to_do)}] Summarizing: {title[:60]}...")
    try:
        resp = llm.chat([
            {"role": "system", "content": "用中文概括论文核心贡献和方法，200字以内。只输出摘要本身，不要用<think>标签。"},
            {"role": "user", "content": f"标题：{title}\n摘要：{text[:2000]}"}
        ], max_tokens=300, temperature=0.3, timeout=60)
        if resp and len(resp) > 30:
            # Strip think tags
            cleaned = resp.replace("<think>", "").replace("</think>", "").strip()
            # Strip  tags too
            cleaned = cleaned.replace("<thought>", "").replace("</thought>", "").strip()
            paper["cn_summary"] = cleaned[:300]
            success += 1
            print(f"[OK] ({len(cleaned)} chars)")
        else:
            print(f"✗ short response: {resp}")
    except Exception as e:
        print(f"[ERR] {e}")

data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nDone: {success}/{len(to_do)} papers summarized")
