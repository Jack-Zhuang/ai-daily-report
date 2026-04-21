#!/usr/bin/env python3
"""
AI日报规则约束检查脚本
检查所有内容是否符合用户要求
"""

import json
import sys

def check_rules(data_file):
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    errors = []
    warnings = []
    
    # ========== 1. 内容数量规则 ==========
    print("=== 1. 内容数量规则 ===")
    
    # 每日精选：5项（3文章+1论文+1GitHub）
    daily_pick = data.get('daily_pick', [])
    if len(daily_pick) != 5:
        errors.append(f"每日精选应为5项，当前{len(daily_pick)}项")
    
    articles = [x for x in daily_pick if x.get('pick_type') == 'article']
    papers = [x for x in daily_pick if x.get('pick_type') == 'paper']
    githubs = [x for x in daily_pick if x.get('pick_type') == 'github']
    
    if len(articles) != 3:
        errors.append(f"每日精选应有3篇文章，当前{len(articles)}篇")
    if len(papers) != 1:
        errors.append(f"每日精选应有1篇论文，当前{len(papers)}篇")
    if len(githubs) != 1:
        errors.append(f"每日精选应有1个GitHub项目，当前{len(githubs)}个")
    
    print(f"  每日精选: {len(daily_pick)}项 (文章{len(articles)}+论文{len(papers)}+GitHub{len(githubs)})")
    
    # 热门文章：5-10项
    hot_articles = data.get('hot_articles', [])
    if len(hot_articles) < 5 or len(hot_articles) > 10:
        warnings.append(f"热门文章应为5-10项，当前{len(hot_articles)}项")
    print(f"  热门文章: {len(hot_articles)}项")
    
    # GitHub Trending：5项
    github_trending = data.get('github_trending', [])
    if len(github_trending) != 5:
        errors.append(f"GitHub Trending应为5项，当前{len(github_trending)}项")
    print(f"  GitHub Trending: {len(github_trending)}项")
    
    # arXiv论文：5项
    arxiv_papers = data.get('arxiv_papers', [])
    if len(arxiv_papers) != 5:
        errors.append(f"arXiv论文应为5项，当前{len(arxiv_papers)}项")
    print(f"  arXiv论文: {len(arxiv_papers)}项")
    
    # 顶会论文：每个会议3篇
    conf_papers = data.get('conference_papers', [])
    print(f"  顶会论文: {len(conf_papers)}个会议")
    
    # ========== 2. 内容顺序规则 ==========
    print("\n=== 2. 内容顺序规则 ===")
    
    # 每日精选顺序：3文章 → 1论文 → 1GitHub
    expected_order = ['article', 'article', 'article', 'paper', 'github']
    actual_order = [x.get('pick_type', 'unknown') for x in daily_pick]
    if actual_order != expected_order:
        errors.append(f"每日精选顺序错误: 期望{expected_order}, 实际{actual_order}")
    print(f"  每日精选顺序: {actual_order}")
    
    # ========== 3. 去重规则 ==========
    print("\n=== 3. 去重规则 ===")
    
    pick_titles = set()
    for item in daily_pick:
        title = item.get('cn_title', item.get('title', item.get('name', '')))
        pick_titles.add(title)
    
    duplicates = []
    for item in hot_articles:
        title = item.get('cn_title', item.get('title', ''))
        if title in pick_titles:
            duplicates.append(title)
    
    if duplicates:
        errors.append(f"热门文章与每日精选重复: {duplicates}")
    print(f"  重复检查: {'✅ 无重复' if not duplicates else f'❌ {len(duplicates)}项重复'}")
    
    # ========== 4. 摘要规则 ==========
    print("\n=== 4. 摘要规则 ===")
    
    for i, item in enumerate(daily_pick):
        cn_summary = item.get('cn_summary', '')
        if not cn_summary:
            errors.append(f"每日精选第{i+1}项缺少cn_summary")
        elif len(cn_summary) < 50:
            warnings.append(f"每日精选第{i+1}项摘要过短: {len(cn_summary)}字")
        else:
            # 检查是否是英文
            english_chars = sum(1 for c in cn_summary if c.isascii() and c.isalpha())
            total_chars = sum(1 for c in cn_summary if c.isalpha())
            if total_chars > 0 and english_chars / total_chars > 0.5:
                errors.append(f"每日精选第{i+1}项摘要主要是英文")
    
    print(f"  摘要检查: 已检查{len(daily_pick)}项")
    
    # ========== 5. 标题规则 ==========
    print("\n=== 5. 标题规则 ===")
    
    for i, item in enumerate(daily_pick):
        cn_title = item.get('cn_title', '')
        en_title = item.get('title', item.get('name', ''))
        
        if not cn_title:
            errors.append(f"每日精选第{i+1}项缺少cn_title")
        
        # 检查中英文标题是否一致（论文类型）
        if item.get('pick_type') == 'paper':
            if cn_title and en_title and cn_title not in en_title and en_title[:20] not in cn_title:
                warnings.append(f"每日精选第{i+1}项中英文标题可能不一致")
    
    print(f"  标题检查: 已检查{len(daily_pick)}项")
    
    # ========== 6. 时效性规则 ==========
    print("\n=== 6. 时效性规则 ===")
    
    from datetime import datetime, timedelta
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    for i, item in enumerate(daily_pick):
        published = item.get('published', '')
        if published:
            try:
                pub_date = datetime.strptime(published[:10], '%Y-%m-%d').date()
                days_ago = (today - pub_date).days
                if days_ago > 3:
                    warnings.append(f"每日精选第{i+1}项发布于{days_ago}天前，超过3天")
            except:
                pass
    
    print(f"  时效性检查: 已检查{len(daily_pick)}项")
    
    # ========== 输出结果 ==========
    print("\n" + "="*50)
    if errors:
        print(f"❌ 发现 {len(errors)} 个错误:")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print(f"⚠️ 发现 {len(warnings)} 个警告:")
        for w in warnings:
            print(f"  - {w}")
    if not errors and not warnings:
        print("✅ 所有规则检查通过!")
    
    return len(errors) == 0

if __name__ == '__main__':
    today = datetime.now().strftime("%Y-%m-%d")
    data_file = sys.argv[1] if len(sys.argv) > 1 else f'daily_data/{today}.json'
    success = check_rules(data_file)
    sys.exit(0 if success else 1)
