#!/usr/bin/env python3
"""Check GitHub Actions deployment status"""
import urllib.request, json

url = "https://api.github.com/repos/Jack-Zhuang/ai-daily-report/actions/runs?per_page=5"
with urllib.request.urlopen(url) as resp:
    data = json.load(resp)

for run in data.get('workflow_runs', [])[:5]:
    name = run['name']
    status = run['status']
    conclusion = run['conclusion'] or 'in_progress'
    created = run['created_at'][:19].replace('T', ' ')
    branch = run['head_branch']
    print(f"[{created}] {name}: {status}/{conclusion} ({branch})")
