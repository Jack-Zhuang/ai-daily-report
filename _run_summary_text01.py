#!/usr/bin/env python3
"""Summarize all papers using MiniMax-Text-01 (clean output, no thinking)."""
import os, sys, json, time
from pathlib import Path

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

BASE = Path(__file__).parent
LOG_FILE = BASE / "logs" / f"summary_text01_{time.strftime('%Y%m%d_%H%M%S')}.log"

def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

sys.path.insert(0, str(BASE))
from llm.factory import ModelFactory

api_key = os.environ.get("MINIMAX_API_KEY", "")
today = "2026-07-20"
data_file = BASE / "daily_data" / f"{today}.json"

data = json.loads(data_file.read_text(encoding="utf-8"))
papers = data.get("arxiv_papers", [])
log(f"Total papers: {len(papers)}")

# Clear all existing summaries (they have thinking noise from M2.7)
for p in papers:
    p.pop("cn_summary", None)
log("Cleared existing summaries")

log("Initializing LLM with MiniMax-Text-01...")
config = {"provider": "minimax", "model": "MiniMax-Text-01",
          "api_key": api_key, "base_url": "https://api.minimaxi.com/v1"}
llm = ModelFactory.create(config)
log(f"LLM initialized: {type(llm).__name__} with MiniMax-Text-01")
sys.stdout.flush()

success = 0
errors = 0
for i, paper in enumerate(papers):
    title = str(paper.get("title", ""))
    text = str(paper.get("summary", ""))
    if not text:
        log(f"[{i+1}/{len(papers)}] {title[:60]}... SKIP (no text)")
        continue
    
    log(f"[{i+1}/{len(papers)}] {title[:80]}...")
    sys.stdout.flush()
    try:
        resp = llm.chat([
            {"role": "system", "content": "你是一个AI论文摘要助手。请用中文将以下内容概括为200字以内的摘要，保留核心技术点和价值。只输出摘要本身。"},
            {"role": "user", "content": f"标题：{title}\n摘要：{text[:2000]}"}
        ], max_tokens=300, temperature=0.3)
        if resp:
            cleaned = resp.strip()
            if len(cleaned) > 30:
                paper["cn_summary"] = cleaned[:300]
                success += 1
                log(f"  OK ({len(cleaned)} chars)")
            else:
                paper["cn_summary"] = cleaned
                success += 1
                log(f"  SHORT ({len(cleaned)} chars)")
        else:
            log(f"  EMPTY response")
            errors += 1
    except Exception as e:
        log(f"  ERR: {e}")
        errors += 1

data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
log(f"\nDone: {success} OK, {errors} errors out of {len(papers)} papers")
