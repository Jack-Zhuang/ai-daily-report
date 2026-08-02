#!/usr/bin/env python3
"""Force-regenerate all summaries with MiniMax, replacing mock placeholders."""
import sys, os, json
from pathlib import Path

LOG = Path(__file__).parent / "logs" / "force_summaries.log"
LOG.parent.mkdir(exist_ok=True)

def log(msg):
    print(msg, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=" * 50)
log("Force-regenerate summaries with MiniMax")
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
try:
    llm = ModelFactory.create(config)
    log(f"LLM Provider: {config['provider']}/{config['model']}")
except Exception as e:
    log(f"Failed to create LLM: {e}")
    sys.exit(1)

BASE = Path(__file__).parent
DATA_FILE = BASE / "daily_data" / "2026-07-10.json"
data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

# Force-regenerate paper summaries
papers = data.get("arxiv_papers", [])
log(f"\nPapers: {len(papers)}")

success = 0
for i, paper in enumerate(papers):
    title = str(paper.get("title", "")) or ""
    text = str(paper.get("summary", "")) or ""
    
    if not text:
        paper["cn_summary"] = title[:200]
        log(f"  [{i+1}/{len(papers)}] SKIP (no text) {title[:40]}")
        continue
    
    try:
        resp = llm.chat([
            {"role": "system", "content": "你是一个AI论文摘要助手。用中文概括核心贡献和方法，200字以内。只输出摘要本身，不要思考过程，不要用<think>标签。"},
            {"role": "user", "content": f"标题：{title}\n摘要：{text[:2000]}"}
        ], max_tokens=300, temperature=0.3)
        
        if resp and len(resp) > 30:
            # Clean up any think tags
            cleaned = resp.replace("<think>", "").replace("</think>", "").strip()
            paper["cn_summary"] = cleaned[:300]
            success += 1
            log(f"  [{i+1}/{len(papers)}] OK {title[:40]}")
        else:
            paper["cn_summary"] = title[:200]
            log(f"  [{i+1}/{len(papers)}] SHORT {title[:40]}")
    except Exception as e:
        paper["cn_summary"] = title[:200]
        log(f"  [{i+1}/{len(papers)}] ERR {title[:40]}: {e}")

log(f"\nSuccessfully summarized: {success}/{len(papers)}")

# Save
DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
log("Data saved with MiniMax summaries")

# Now run report generation
log("\n" + "=" * 50)
log("STEP 2: Generate HTML report")
log("=" * 50)

from generate_report import ReportGenerator

gen = ReportGenerator(str(BASE))
gen.today = "2026-07-10"
html_path = gen.run()

if html_path:
    log(f"\nReport: {html_path}")
    size = Path(html_path).stat().st_size
    log(f"Size: {size} bytes")
else:
    log("FAILED")
    sys.exit(1)

log("\nDONE")
