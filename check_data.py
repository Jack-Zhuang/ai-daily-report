#!/usr/bin/env python3
import json
data = json.load(open(r'C:\Users\HUAWEI\.openclaw\workspace\ai-daily-report\daily_data\2026-07-10.json', encoding='utf-8'))
p = data.get('arxiv_papers', [])
if p:
    print('First paper cn_summary:', p[0].get('cn_summary', '')[:100])
else:
    print('No papers')
print('Articles:', len(data.get('articles',[])), 'GitHub:', len(data.get('github_projects',[])), 'Hot:', len(data.get('hot_articles',[])))
