#!/usr/bin/env python3
"""Check GitHub Pages deployment status"""
import urllib.request, json

# Check repo
url = "https://api.github.com/repos/Jack-Zhuang/ai-daily-report"
with urllib.request.urlopen(url) as resp:
    data = json.load(resp)
print(f"Default branch: {data['default_branch']}")

# Check Pages
try:
    pages_url = "https://api.github.com/repos/Jack-Zhuang/ai-daily-report/pages"
    with urllib.request.urlopen(pages_url) as resp:
        pages = json.load(resp)
    print(f"Pages status: {pages['status']}")
    print(f"Pages URL: {pages.get('html_url', 'N/A')}")
    src = pages.get('source', {})
    print(f"Pages branch: {src.get('branch', 'N/A')}")
    print(f"Pages path: {src.get('path', '/')}")
except Exception as e:
    print(f"Pages API error: {e}")

# Check latest Actions run
runs_url = "https://api.github.com/repos/Jack-Zhuang/ai-daily-report/actions/runs?per_page=3"
with urllib.request.urlopen(runs_url) as resp:
    runs = json.load(resp)
for run in runs.get('workflow_runs', []):
    print(f"[{run['created_at'][:19]}] {run['name']}: {run['status']}/{run.get('conclusion','?')} ({run['head_branch']})")
    
# Test GitHub Pages site
try:
    site_req = urllib.request.Request("https://jack-zhuang.github.io/ai-daily-report/", method="HEAD")
    with urllib.request.urlopen(site_req) as resp:
        print(f"GitHub Pages site: HTTP {resp.getcode()}")
except Exception as e:
    print(f"GitHub Pages site: {e}")
