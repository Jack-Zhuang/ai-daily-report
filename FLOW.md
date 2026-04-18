# AI推荐日报 - 完整流程文档

## 一、信息来源

### 1.1 数据源配置

| 数据源 | 来源 | 采集方式 | 每日数量 | 脚本 |
|--------|------|----------|----------|------|
| **微信公众号** | wechat2rss.xlab.app | RSS | ~40篇 | `collect_articles.py` |
| - 机器之心 | wechat2rss | RSS | ~10篇 | |
| - 量子位 | wechat2rss | RSS | ~10篇 | |
| - 新智元 | wechat2rss | RSS | ~10篇 | |
| - PaperWeekly | wechat2rss | RSS | ~10篇 | |
| **知乎** | rsshub.rssforever.com | RSS | ~5篇 | `collect_articles.py` |
| - 知乎热榜 | RSSHub | RSS | ~3篇 | |
| - 知乎日报 | RSSHub | RSS | ~2篇 | |
| **技术媒体** | rsshub.rssforever.com | RSS | ~30篇 | `collect_articles.py` |
| - 36氪快讯 | RSSHub | RSS | ~5篇 | |
| - IT之家热榜 | RSSHub | RSS | ~5篇 | |
| - 开源中国资讯 | RSSHub | RSS | ~10篇 | |
| - InfoQ技术文章 | RSSHub | RSS | ~10篇 | |
| **arXiv论文** | export.arxiv.org | API | ~60篇 | `collect_daily.py` |
| - 推荐系统(cs.IR) | arXiv API | API | ~20篇 | |
| - Agent(cs.AI) | arXiv API | API | ~20篇 | |
| - LLM(cs.CL) | arXiv API | API | ~20篇 | |
| **GitHub Trending** | github.com | API | ~20个 | `collect_daily.py` |
| **顶会论文** | arXiv API | API | ~60篇 | `collect_conference_papers.py` |
| - WSDM 2026 | arXiv | API | ~10篇 | |
| - KDD 2025 | arXiv | API | ~10篇 | |
| - RecSys 2025 | arXiv | API | ~10篇 | |
| - WWW 2025 | arXiv | API | ~10篇 | |
| - SIGIR 2025 | arXiv | API | ~10篇 | |
| - CIKM 2025 | arXiv | API | ~10篇 | |

### 1.2 每日采集总量

```
┌─────────────────────────────────────────────────────────────┐
│                    每日采集数据量                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  文章类: ~75篇                                              │
│  ├── 微信公众号: ~40篇                                      │
│  ├── 知乎: ~5篇                                             │
│  └── 技术媒体: ~30篇                                        │
│                                                             │
│  论文类: ~120篇                                             │
│  ├── arXiv论文: ~60篇                                       │
│  └── 顶会论文: ~60篇                                        │
│                                                             │
│  GitHub项目: ~20个                                          │
│                                                             │
│  总计: ~215条内容                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、采集后处理流程

### 2.1 处理步骤

```
┌─────────────────────────────────────────────────────────────┐
│                    采集后处理流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  步骤1: 相关性过滤                                          │
│  ├── 检查标题和摘要是否包含关键词                           │
│  ├── 关键词: recommend, agent, llm, etc.                    │
│  └── 过滤掉不相关内容                                       │
│                                                             │
│  步骤2: 时效性过滤                                          │
│  ├── 检查发布时间是否在3天内                                │
│  └── 过滤掉过期内容                                         │
│                                                             │
│  步骤3: 翻译处理                                            │
│  ├── 翻译英文标题为中文                                     │
│  ├── 翻译英文摘要为中文                                     │
│  └── 使用 MiniMax API 或规则翻译                            │
│                                                             │
│  步骤4: 构建每日精选                                        │
│  ├── 严格按照规则: 3篇文章 + 1篇论文 + 1个GitHub            │
│  ├── 顺序: [article, article, article, paper, github]       │
│  └── 从过滤后的内容中选择                                   │
│                                                             │
│  步骤5: 去重处理                                            │
│  ├── 从热门文章中移除已选入每日精选的内容                   │
│  └── 确保无重复                                             │
│                                                             │
│  步骤6: 封面图生成                                          │
│  ├── 策略1: 从原文提取图片                                  │
│  ├── 策略2: PDF截图                                         │
│  └── 策略3: AI生成                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 处理后数据量

```
┌─────────────────────────────────────────────────────────────┐
│                    处理后数据量                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  每日精选: 5项 (强制)                                       │
│  ├── 文章: 3篇                                              │
│  ├── 论文: 1篇                                              │
│  └── GitHub: 1个                                            │
│                                                             │
│  热门文章: 5-10篇                                           │
│  ├── 已去重（移除每日精选中的内容）                         │
│  └── 已翻译                                                 │
│                                                             │
│  GitHub Trending: 5个                                       │
│                                                             │
│  arXiv论文: 5篇                                             │
│  ├── 已翻译                                                 │
│  └── 已生成封面                                             │
│                                                             │
│  顶会论文: 60篇                                             │
│  └── 每个会议10篇                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、每日精选构建规则（代码强制）

### 3.1 规则定义

**文件**: `scripts/build_daily_pick.py`

```python
# 规则：3篇文章 + 1篇论文 + 1个GitHub项目
# 顺序：[article, article, article, paper, github]

def build_daily_pick(self, data: dict) -> list:
    """
    构建每日精选
    规则：3篇文章 + 1篇论文 + 1个GitHub项目
    顺序：[article, article, article, paper, github]
    """
    # 收集所有可用内容
    articles = []  # 文章
    papers = []    # 论文
    githubs = []   # GitHub项目
    
    # 从热门文章中筛选
    for item in data.get('hot_articles', []):
        link = item.get('link', '')
        
        # 检查相关性和时效性
        if not self.is_relevant(title, summary):
            continue
        if not self.is_recent(published, max_days=3):
            continue
        
        if 'arxiv.org' in link:
            item['pick_type'] = 'paper'
            papers.append(item)
        elif 'github.com' in link:
            item['pick_type'] = 'github'
            githubs.append(item)
        else:
            item['pick_type'] = 'article'
            articles.append(item)
    
    # 从 arXiv 论文中补充
    for item in data.get('arxiv_papers', []):
        if self.is_relevant(title, summary) and self.is_recent(published):
            item['pick_type'] = 'paper'
            papers.append(item)
    
    # 从 GitHub 项目中补充
    for item in data.get('github_trending', []):
        if self.is_relevant(title, summary):
            item['pick_type'] = 'github'
            githubs.append(item)
    
    # 构建每日精选（严格按照规则）
    daily_pick = []
    
    # 3篇文章
    for item in articles[:3]:
        item['pick_type'] = 'article'
        daily_pick.append(item)
    
    # 1篇论文
    if papers:
        papers[0]['pick_type'] = 'paper'
        daily_pick.append(papers[0])
    
    # 1个GitHub
    if githubs:
        githubs[0]['pick_type'] = 'github'
        daily_pick.append(githubs[0])
    
    return daily_pick
```

### 3.2 规则检查

**文件**: `scripts/check_rules.py`

```python
# 检查每日精选规则
def check_rules(data):
    daily_pick = data.get('daily_pick', [])
    
    # 1. 数量检查
    if len(daily_pick) != 5:
        errors.append(f"每日精选应为5项，当前{len(daily_pick)}项")
    
    # 2. 类型检查
    articles = [x for x in daily_pick if x.get('pick_type') == 'article']
    papers = [x for x in daily_pick if x.get('pick_type') == 'paper']
    githubs = [x for x in daily_pick if x.get('pick_type') == 'github']
    
    if len(articles) != 3:
        errors.append(f"每日精选应有3篇文章，当前{len(articles)}篇")
    if len(papers) != 1:
        errors.append(f"每日精选应有1篇论文，当前{len(papers)}篇")
    if len(githubs) != 1:
        errors.append(f"每日精选应有1个GitHub项目，当前{len(githubs)}个")
    
    # 3. 顺序检查
    expected_order = ['article', 'article', 'article', 'paper', 'github']
    actual_order = [x.get('pick_type') for x in daily_pick]
    
    if actual_order != expected_order:
        errors.append(f"每日精选顺序错误: 期望{expected_order}, 实际{actual_order}")
```

---

## 四、完整执行流程

### 4.1 一键执行

```bash
# 完整流程
python3 scripts/run_daily.py

# 流程步骤
步骤1: 采集 (collect)
  ├── 采集 arXiv 论文
  ├── 采集文章
  ├── 采集 GitHub Trending
  └── 采集顶会论文

步骤2: 处理 (process)
  ├── 翻译标题和摘要
  ├── 合并顶会论文
  └── 构建每日精选（强制规则）

步骤3: 生成 (generate)
  ├── 生成日报 HTML
  ├── 生成论文解读页面
  └── 生成封面图

步骤4: 检查 (check)
  └── 运行规则检查

步骤5: 部署 (deploy)
  ├── Git 提交
  ├── Git 推送
  └── GitHub Pages 自动部署
```

### 4.2 脚本调用关系

```
run_daily.py (主入口)
├── step1_collect()
│   ├── collect_daily.py          # arXiv + GitHub
│   ├── collect_articles.py       # 文章
│   └── collect_conference_papers.py  # 顶会论文
│
├── step2_process()
│   ├── translator.py             # 翻译
│   └── build_daily_pick.py       # 构建每日精选（强制规则）
│
├── step3_generate()
│   ├── generate_report.py        # 日报
│   ├── generate_insights.py      # 论文解读
│   └── generate_covers_enhanced.py  # 封面图
│
├── step4_check()
│   └── check_rules.py            # 规则检查
│
└── step5_deploy()
    └── git push                  # 部署
```

---

## 五、数据流转

```
┌─────────────────────────────────────────────────────────────┐
│                    数据流转图                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  采集阶段                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ 微信/RSS │  │ arXiv    │  │ GitHub   │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       │             │             │                         │
│       ▼             ▼             ▼                         │
│  ┌─────────────────────────────────────┐                   │
│  │ cache/*.json (原始数据)              │                   │
│  │ - all_articles.json (~75篇)         │                   │
│  │ - arxiv_papers.json (~60篇)         │                   │
│  │ - github_cache.json (~20个)         │                   │
│  │ - conference_papers.json (~60篇)    │                   │
│  └─────────────────────────────────────┘                   │
│                         │                                   │
│                         ▼                                   │
│  处理阶段                                                    │
│  ┌─────────────────────────────────────┐                   │
│  │ daily_data/YYYY-MM-DD.json          │                   │
│  │ - 相关性过滤                        │                   │
│  │ - 时效性过滤                        │                   │
│  │ - 翻译处理                          │                   │
│  │ - 构建每日精选（强制规则）          │                   │
│  │ - 去重处理                          │                   │
│  └─────────────────────────────────────┘                   │
│                         │                                   │
│                         ▼                                   │
│  生成阶段                                                    │
│  ┌─────────────────────────────────────┐                   │
│  │ 输出文件                             │                   │
│  │ - index.html (主页)                 │                   │
│  │ - insights/*.html (论文解读)        │                   │
│  │ - covers/*.jpg (封面图)             │                   │
│  │ - archive/YYYY-MM-DD/ (归档)        │                   │
│  └─────────────────────────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 六、关键规则汇总

| 规则 | 说明 | 代码位置 |
|------|------|----------|
| **每日精选组成** | 3篇文章 + 1篇论文 + 1个GitHub | `build_daily_pick.py` |
| **每日精选顺序** | [article, article, article, paper, github] | `build_daily_pick.py` |
| **相关性检查** | 必须包含关键词 | `build_daily_pick.py` |
| **时效性检查** | 发布时间 ≤ 3天 | `build_daily_pick.py` |
| **去重规则** | 热门文章与每日精选不重复 | `build_daily_pick.py` |
| **翻译规则** | 所有标题和摘要必须是中文 | `translator.py` |
| **摘要长度** | ≥ 50字 | `check_rules.py` |
| **论文跳转** | 必须先跳转到解读页面 | `generate_report.py` |
