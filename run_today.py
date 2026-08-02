#!/usr/bin/env python3
"""Run today's AI daily report: collect data + generate summaries + build HTML."""
import sys, os, json, io

# Force UTF-8 for all output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

BASE = Path(__file__).parent
DATA_FILE = BASE / "daily_data" / "2026-07-10.json"

print("=" * 50)
print("STEP 1: Generate LLM summaries for arXiv papers")
print("=" * 50)

from llm.factory import ModelFactory

# Init MiniMax
api_key = os.environ.get("MINIMAX_API_KEY", "")
if not api_key:
    print("ERROR: No MINIMAX_API_KEY set")
    sys.exit(1)

config = {
    "provider": "minimax",
    "model": "MiniMax-M2.7",
    "api_key": api_key,
    "base_url": "https://api.minimaxi.com/v1",
}
llm = ModelFactory.create(config)
print(f"LLM Provider: {config['provider']}/{config['model']}")

# Load data
data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
papers = data.get("arxiv_papers", [])
articles = data.get("articles", [])
github = data.get("github_projects", [])

print(f"\nPapers: {len(papers)}, Articles: {len(articles)}, GitHub: {len(github)}")

# Summarize papers one by one
summarized = 0
for i, paper in enumerate(papers):
    title = paper.get("title", "") or ""
    text = paper.get("summary", "") or ""
    arxiv_id = paper.get("arxiv_id", "")
    
    if paper.get("cn_summary") and len(paper["cn_summary"]) > 30:
        continue
    
    if not text:
        paper["cn_summary"] = f"arXiv论文 {arxiv_id}: {title[:80]}"
        continue
    
    try:
        resp = llm.chat([
            {"role": "system", "content": "你是一个AI论文摘要助手。请用中文概括以下AI/ML论文的核心贡献和方法，控制在200字以内。只说关键点，不要套话。"},
            {"role": "user", "content": f"标题：{title}\n摘要：{str(text)[:2000]}"}
        ], max_tokens=300, temperature=0.3)
        
        if resp and len(resp) > 30:
            paper["cn_summary"] = resp.strip()[:300]
            summarized += 1
            print(f"  [{i+1}/{len(papers)}] ✅ {str(title)[:40]}...")
        else:
            paper["cn_summary"] = f"arXiv论文 {arxiv_id}: {title[:80]}"
            print(f"  [{i+1}/{len(papers)}] ⚠️ {str(title)[:40]}... (short response)")
    except Exception as e:
        paper["cn_summary"] = f"arXiv论文 {arxiv_id}: {title[:80]}"
        print(f"  [{i+1}/{len(papers)}] ❌ {str(title)[:40]}... error: {e}")

print(f"\nSummarized: {summarized}/{len(papers)}")

# Save updated data
DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("Data saved with summaries")

print("\n" + "=" * 50)
print("STEP 2: Generate HTML report")
print("=" * 50)

from generate_report import ReportGenerator

gen = ReportGenerator(str(BASE))
gen.today = "2026-07-10"
html_path = gen.run()

if html_path:
    print(f"\nReport generated: {html_path}")
else:
    print("Failed to generate report")
    sys.exit(1)
