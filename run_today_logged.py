#!/usr/bin/env python3
"""Run today's AI daily report - with logging to file."""
import sys, os, json
from pathlib import Path

LOG = Path(__file__).parent / "logs" / "run_2026-07-10.log"
LOG.parent.mkdir(exist_ok=True)

def log(msg):
    print(msg, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=" * 50)
log("STEP 1: Generate LLM summaries for arXiv papers")
log("=" * 50)

from llm.factory import ModelFactory

api_key = os.environ.get("MINIMAX_API_KEY", "")
if not api_key:
    log("ERROR: No MINIMAX_API_KEY set")
    sys.exit(1)

config = {
    "provider": "minimax",
    "model": "MiniMax-M2.7",
    "api_key": api_key,
    "base_url": "https://api.minimaxi.com/v1",
}
llm = ModelFactory.create(config)
log(f"LLM Provider: {config['provider']}/{config['model']}")

BASE = Path(__file__).parent
DATA_FILE = BASE / "daily_data" / "2026-07-10.json"
data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
papers = data.get("arxiv_papers", [])
log(f"\nPapers to summarize: {len(papers)}")

summarized = 0
for i, paper in enumerate(papers):
    title = paper.get("title", "") or ""
    text = paper.get("summary", "") or ""
    arxiv_id = paper.get("arxiv_id", "")
    
    if paper.get("cn_summary") and len(paper["cn_summary"]) > 30:
        continue
    
    if not text:
        paper["cn_summary"] = arxiv_id
        continue
    
    try:
        resp = llm.chat([
            {"role": "system", "content": "你是一个AI论文摘要助手。请用中文概括以下AI/ML论文的核心贡献和方法，控制在200字以内。只说关键点，不要套话。"},
            {"role": "user", "content": f"标题：{title}\n摘要：{str(text)[:2000]}"}
        ], max_tokens=300, temperature=0.3)
        
        if resp and len(resp) > 30:
            paper["cn_summary"] = resp.strip()[:300]
            summarized += 1
            log(f"  [{i+1}/{len(papers)}] OK {str(title)[:40]}")
        else:
            paper["cn_summary"] = arxiv_id
            log(f"  [{i+1}/{len(papers)}] SHORT {str(title)[:40]}")
    except Exception as e:
        paper["cn_summary"] = arxiv_id
        log(f"  [{i+1}/{len(papers)}] ERR {str(title)[:40]}: {e}")

log(f"\nSummarized: {summarized}/{len(papers)}")

DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
log("Data saved with summaries")

log("\n" + "=" * 50)
log("STEP 2: Generate HTML report")
log("=" * 50)

from generate_report import ReportGenerator

gen = ReportGenerator(str(BASE))
gen.today = "2026-07-10"
html_path = gen.run()

if html_path:
    log(f"\nReport generated: {html_path}")
else:
    log("Failed to generate report")
    sys.exit(1)

log("\nDONE")
