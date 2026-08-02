#!/usr/bin/env python3
import json
from pathlib import Path

data_file = Path(__file__).parent / "daily_data" / "2026-07-20.json"
data = json.loads(data_file.read_text(encoding="utf-8"))
papers = data.get("arxiv_papers", [])
has = sum(1 for p in papers if p.get("cn_summary") and len(p.get("cn_summary","")) > 30)
print(f"Papers with summaries: {has}/{len(papers)}")
for p in papers[:3]:
    title = p.get("title","?")[:40]
    summ = p.get("cn_summary","")[:80]
    print(f"  {title}: {summ}")
