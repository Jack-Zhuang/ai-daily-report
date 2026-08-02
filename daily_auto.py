#!/usr/bin/env python3
"""
Daily automatic AI daily report:
  1. Collect arXiv papers
  2. Generate LLM summaries (MiniMax)
  3. Generate HTML report
  4. Push to GitHub
"""
import sys, os, json, io, subprocess
from pathlib import Path
from datetime import datetime

# Force UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Bypass Windows system proxy (port 10809 not running)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ['NO_PROXY'] = '*'

BASE = Path(__file__).parent
LOG = BASE / "logs" / f"auto_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.log"
LOG.parent.mkdir(exist_ok=True)

def log(msg):
    print(msg, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

today = datetime.now().strftime("%Y-%m-%d")
log(f"Daily Auto Run: {today}")
log("=" * 50)

# 1. Collect papers
log("\n[1/4] Collecting arXiv papers...")
result = subprocess.run(
    [sys.executable, "-X", "utf8", str(BASE / "collect_daily.py")],
    cwd=BASE, capture_output=True, text=True
)
log(result.stdout[-500:] if result.stdout else "No output")
if result.returncode != 0:
    log(f"Collect stderr: {result.stderr[-300:]}")
    log("WARN: collect_daily.py had issues, continuing...")

# 2. Generate summaries
log("\n[2/4] Generating LLM summaries...")
from llm.factory import ModelFactory
from llm_summarizer import clean_llm_response

api_key = os.environ.get("MINIMAX_API_KEY", "")
if not api_key:
    key_file = BASE / "_key.txt"
    if key_file.exists():
        api_key = key_file.read_text(encoding="utf-8").strip()
if api_key:
    config = {"provider": "minimax", "model": "MiniMax-M3",
              "api_key": api_key, "base_url": "https://api.minimaxi.com/v1"}
    try:
        llm = ModelFactory.create(config)
        data_file = BASE / "daily_data" / f"{today}.json"
        if data_file.exists():
            data = json.loads(data_file.read_text(encoding="utf-8"))
            papers = data.get("arxiv_papers", [])
            success = 0
            for i, paper in enumerate(papers):
                title = str(paper.get("title", "")) or ""
                text = str(paper.get("summary", "")) or ""
                if not text:
                    continue
                if paper.get("cn_summary") and len(paper["cn_summary"]) > 30:
                    continue
                try:
                    resp = llm.chat([
                        {"role": "system", "content": "用中文概括论文核心贡献和方法，200字以内。只输出摘要本身。"},
                        {"role": "user", "content": f"标题：{title}\n摘要：{text[:2000]}"}
                    ], max_tokens=300, temperature=0.3)
                    if resp and len(resp) > 30:
                        paper["cn_summary"] = clean_llm_response(resp)[:300]
                        success += 1
                except Exception as e:
                    log(f"  ERR [{i+1}/{len(papers)}]: {e}")
            data_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            log(f"  Summarized: {success}/{len(papers)}")
        else:
            log(f"  No data file for {today}")
    except Exception as e:
        log(f"  LLM init error: {e}")
else:
    log("  No API key, skipping LLM summarization")

# 3. Generate HTML report
log("\n[3/4] Generating HTML report...")
from generate_report import ReportGenerator
try:
    gen = ReportGenerator(str(BASE))
    gen.today = today
    html_path = gen.run()
    if html_path:
        size = Path(html_path).stat().st_size
        log(f"  Report: {html_path} ({size} bytes)")
    else:
        log("  FAILED")
except Exception as e:
    log(f"  Report generation error: {e}")

# 4. Push to GitHub
log("\n[4/4] Pushing to GitHub...")
result = subprocess.run(
    ["git", "add", "-A", str(BASE / "docs"), str(BASE / "index.html")],
    cwd=BASE, capture_output=True, text=True
)
result = subprocess.run(
    ["git", "diff", "--cached", "--quiet"],
    cwd=BASE, capture_output=True
)
if result.returncode != 0:
    result = subprocess.run(
        ["git", "commit", "-m", f"chore: auto daily report {today}"],
        cwd=BASE, capture_output=True, text=True
    )
    log(result.stdout.strip()[-200:] if result.stdout else "")
    result = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=BASE, capture_output=True, text=True
    )
    log(result.stdout.strip()[-200:] if result.stdout else "")
    if result.returncode == 0:
        log("  PUSH OK")
    else:
        log(f"  PUSH FAILED: {result.stderr[-200:]}")
else:
    log("  No changes to commit")

log(f"\n{'='*50}")
log(f"DONE: {today}")
log(f"Log: {LOG}")
