#!/usr/bin/env python3
"""Run LLM summarization for today's papers - writes to log file."""
import os, sys, json, time
from pathlib import Path

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

BASE = Path(__file__).parent
LOG_FILE = BASE / "logs" / f"summary_run_{time.strftime('%Y%m%d_%H%M%S')}.log"

def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log(f"Starting LLM summarization for 2026-07-20")
sys.stdout.flush()

sys.path.insert(0, str(BASE))
from llm.factory import ModelFactory

api_key = os.environ.get("MINIMAX_API_KEY", "")
today = "2026-07-20"
data_file = BASE / "daily_data" / f"{today}.json"

data = json.loads(data_file.read_text(encoding="utf-8"))
papers = data.get("arxiv_papers", [])
log(f"Found {len(papers)} papers")

to_do = [p for p in papers if not p.get("cn_summary") or len(p.get("cn_summary", "")) <= 30]
log(f"Papers needing summary: {len(to_do)}/{len(papers)}")

if not to_do:
    log("All done, nothing to summarize")
    exit(0)

log("Initializing LLM...")
sys.stdout.flush()

config = {"provider": "minimax", "model": "MiniMax-M2.7",
          "api_key": api_key, "base_url": "https://api.minimaxi.com/v1"}
llm = ModelFactory.create(config)
log(f"LLM initialized: {type(llm).__name__}")
sys.stdout.flush()

success = 0
for i, paper in enumerate(to_do):
    title = str(paper.get("title", ""))
    text = str(paper.get("summary", ""))
    if not text:
        continue
    
    log(f"[{i+1}/{len(to_do)}] Summarizing: {title[:80]}...")
    sys.stdout.flush()
    try:
        resp = llm.chat([
            {"role": "system", "content": "用中文概括论文核心贡献和方法，200字以内。只输出摘要本身，不要用thinking标签。"},
            {"role": "user", "content": f"标题：{title}\n摘要：{text[:2000]}"}
        ], max_tokens=300, temperature=0.3)
        if resp:
            for tag in ["<think>", "</think>", "<thought>", "</thought>"]:
                resp = resp.replace(tag, "")
            cleaned = resp.strip()
            if len(cleaned) > 30:
                paper["cn_summary"] = cleaned[:300]
                success += 1
                log(f"  OK ({len(cleaned)} chars)")
            else:
                log(f"  SHORT ({len(cleaned)} chars): {cleaned[:50]}")
        else:
            log(f"  EMPTY response")
    except Exception as e:
        log(f"  ERR: {e}")

data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
log(f"\nDone: {success}/{len(to_do)} papers summarized")
