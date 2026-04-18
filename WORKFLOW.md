# AI推荐日报 - 完整工作流程

## 流程概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI推荐日报生成流程                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. 内容获取        2. 数据加工        3. 持久化        4. 页面生成          │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐        │
│  │ 采集脚本 │ ───▶ │ 规则过滤 │ ───▶ │ JSON存储 │ ───▶ │ HTML生成 │        │
│  └──────────┘      └──────────┘      └──────────┘      └──────────┘        │
│       │                 │                 │                 │              │
│       ▼                 ▼                 ▼                 ▼              │
│  - 微信公众号       - 相关性检查       - daily_data/      - index.html     │
│  - 知乎/技术媒体    - 时效性检查       - cache/           - insights/      │
│  - arXiv论文        - 去重处理         - archive/         - articles.html  │
│  - GitHub Trending  - 标题翻译                           - papers.html    │
│                     - 摘要翻译                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 第一阶段：内容获取

### 1.1 数据源

| 数据源 | 采集方式 | 脚本 | 频率 |
|--------|----------|------|------|
| 微信公众号 | wechat2rss.xlab.app | `collect_articles.py` | 每日 |
| 知乎日报 | RSSHub 国内镜像 | `collect_articles.py` | 每日 |
| 36氪/IT之家/开源中国/InfoQ | RSSHub 国内镜像 | `collect_articles.py` | 每日 |
| arXiv论文 | arXiv API | `collect_daily.py` | 每日 |
| GitHub Trending | GitHub API | `collect_daily.py` | 每日 |
| 顶会论文 | 手动/缓存 | `collect_daily.py` | 按需 |

### 1.2 采集脚本

**主脚本：`scripts/collect_daily.py`**

```python
# 采集流程
1. 采集 arXiv 论文（最近3天）
   - 查询: cat:cs.IR AND recommend
   - 查询: cat:cs.AI AND agent
   - 查询: cat:cs.CL AND LLM
   - 按提交时间降序排列

2. 采集 GitHub Trending
   - 获取今日高增长项目
   - 筛选 AI/ML 相关项目

3. 采集文章
   - 微信公众号（机器之心、量子位、新智元、PaperWeekly）
   - 知乎日报
   - 技术媒体（36氪、IT之家、开源中国、InfoQ）
```

### 1.3 采集规则

**规则1：相关性检查**
```python
keywords = {
    'rec': ['recommend', 'recommendation', 'recsys', 'collaborative filtering', 'ctr'],
    'agent': ['agent', 'multi-agent', 'autonomous', 'tool use', 'planning'],
    'llm': ['llm', 'large language model', 'gpt', 'bert', 'transformer']
}

# 标题或摘要必须包含至少一个关键词
```

**规则2：时效性检查**
```python
# 只采集最近3天内的内容
max_days = 3
pub_date = datetime.strptime(published[:10], '%Y-%m-%d')
days_ago = (datetime.now() - pub_date).days
return days_ago <= max_days
```

---

## 第二阶段：数据加工

### 2.1 数据结构

**`daily_data/YYYY-MM-DD.json`**

```json
{
  "date": "2026-04-18",
  "daily_pick": [...],      // 每日精选 5项
  "hot_articles": [...],    // 热门文章 5-10项
  "github_trending": [...], // GitHub项目 5项
  "arxiv_papers": [...],    // arXiv论文 5项
  "conference_papers": [...], // 顶会论文
  "stats": {
    "total_papers": 5,
    "total_projects": 5,
    "total_articles": 8,
    "total_pick": 5
  }
}
```

### 2.2 加工规则

**规则3：每日精选组成**
```
每日精选 = 3篇文章 + 1篇论文 + 1个GitHub项目
顺序: [article, article, article, paper, github]
```

**规则4：去重处理**
```python
# 热门文章中移除与每日精选重复的内容
pick_titles = set(item['cn_title'] for item in daily_pick)
hot_articles = [item for item in hot_articles 
                if item['cn_title'] not in pick_titles]
```

**规则5：标题翻译**
```python
# 论文标题格式
cn_title = "中文标题（英文标题）"

# 示例
"SAGER: Self-Evolving User Policy Skills for Recommendation Agent"
→ "SAGER：推荐Agent的自演化用户策略技能"
```

**规则6：摘要翻译**
```python
# 所有摘要必须是完整中文
# 不能截断，长度 >= 50字
# 不能是英文摘要

cn_summary = translate_to_chinese(summary)
if len(cn_summary) < 50:
    print("⚠️ 摘要过短")
```

**规则7：pick_type 判断**
```python
# 根据链接判断类型
if 'arxiv.org' in link:
    pick_type = 'paper'
elif 'github.com' in link:
    pick_type = 'github'
else:
    pick_type = 'article'
```

---

## 第三阶段：持久化

### 3.1 存储位置

```
ai_daily/
├── daily_data/           # 每日数据
│   ├── 2026-04-17.json
│   └── 2026-04-18.json
├── cache/                # 缓存数据
│   ├── arxiv_cache.json
│   ├── github_cache.json
│   └── all_articles.json
└── archive/              # 归档页面
    └── 2026-04-18/
        └── index.html
```

### 3.2 数据版本

- 每日数据独立存储
- 缓存数据持续更新
- 归档页面永久保存

---

## 第四阶段：页面生成

### 4.1 生成脚本

**主脚本：`scripts/generate_report.py`**

```python
# 生成流程
1. 加载今日数据 (daily_data/YYYY-MM-DD.json)
2. 强约束验证
3. 生成 HTML 页面
4. 生成论文解读页面 (insights/)
5. 归档到 archive/YYYY-MM-DD/
```

### 4.2 强约束验证

**规则8：内容数量约束**
```python
# 在 generate_html() 开头强制验证
if len(daily_pick) != 5:
    print("⚠️ 每日精选数量错误")

if len(github_projects) > 5:
    github_projects = github_projects[:5]  # 强制截取

if len(arxiv_papers) > 5:
    arxiv_papers = arxiv_papers[:5]  # 强制截取
```

**规则9：去重约束**
```python
# 在生成时再次去重
pick_titles = set(item['cn_title'] for item in daily_pick)
hot_articles = [item for item in hot_articles 
                if item['cn_title'] not in pick_titles]
```

**规则10：摘要检查**
```python
for item in daily_pick:
    cn_summary = item.get('cn_summary', '')
    if not cn_summary:
        print("⚠️ 缺少cn_summary")
    elif len(cn_summary) < 50:
        print("⚠️ 摘要过短")
```

### 4.3 页面结构

```
ai_daily/
├── index.html              # 主页
├── articles.html           # 文章列表页
├── papers.html             # 论文列表页
├── insights/               # 论文解读页面
│   ├── paper_2604_14972v1.html
│   └── github_*.html
└── archive/                # 归档
    └── 2026-04-18/
        └── index.html
```

### 4.4 交互规则

**规则11：论文跳转**
```javascript
// 论文弹窗只显示"查看论文解读"按钮
if (pickType === 'paper') {
    const insightUrl = `insights/paper_${paperId}.html`;
    footerHtml = `<a href="${insightUrl}">查看论文解读</a>`;
}
// 不显示 arXiv 原文链接
```

**规则12：弹窗布局**
```css
/* 弹窗结构 */
.modal-content {
    display: flex;
    flex-direction: column;
}
.modal-header { flex-shrink: 0; }  /* 固定 */
.modal-body { flex: 1; overflow-y: auto; }  /* 可滚动 */
.modal-footer { flex-shrink: 0; }  /* 固定底部 */
```

---

## 第五阶段：部署

### 5.1 部署流程

```bash
# 1. 生成页面
python3 scripts/generate_report.py

# 2. 运行规则检查
python3 scripts/check_rules.py

# 3. 提交到 Git
git add -A
git commit -m "更新日报"
git push

# 4. GitHub Pages 自动部署
# 访问: https://jack-zhuang.github.io/ai-daily-report/
```

### 5.2 规则检查脚本

**`scripts/check_rules.py`**

```python
# 检查项目
1. 内容数量规则
   - 每日精选: 5项 (3文章+1论文+1GitHub)
   - GitHub Trending: 5项
   - arXiv论文: 5项
   - 热门文章: 5-10项

2. 内容顺序规则
   - 每日精选顺序: [article, article, article, paper, github]

3. 去重规则
   - 热门文章与每日精选无重复

4. 摘要规则
   - 所有摘要必须是中文
   - 摘要长度 >= 50字

5. 标题规则
   - 中英文标题一致

6. 时效性规则
   - 内容发布时间 <= 3天
```

---

## 规则汇总

| 编号 | 规则名称 | 阶段 | 强制方式 |
|------|----------|------|----------|
| 1 | 相关性检查 | 采集 | 代码过滤 |
| 2 | 时效性检查 | 采集 | 代码过滤 |
| 3 | 每日精选组成 | 加工 | 数据结构 |
| 4 | 去重处理 | 加工+生成 | 代码过滤 |
| 5 | 标题翻译 | 加工 | 人工/自动 |
| 6 | 摘要翻译 | 加工 | 人工/自动 |
| 7 | pick_type判断 | 加工 | 代码判断 |
| 8 | 内容数量约束 | 生成 | 代码截取 |
| 9 | 去重约束 | 生成 | 代码过滤 |
| 10 | 摘要检查 | 生成 | 代码验证 |
| 11 | 论文跳转 | 生成 | 代码强制 |
| 12 | 弹窗布局 | 生成 | CSS固定 |

---

## 当前问题

### 问题1：采集脚本未完整运行
- **现象**: `collect_daily.py` 只采集 arXiv 论文
- **原因**: 文章和 GitHub 采集逻辑未集成
- **影响**: 需要手动补充数据

### 问题2：标题翻译未自动化
- **现象**: 中文标题需要手动设置
- **原因**: 未集成翻译 API
- **影响**: 可能出现中英文标题不一致

### 问题3：摘要翻译未自动化
- **现象**: 摘要需要手动翻译
- **原因**: 未集成翻译 API
- **影响**: 可能出现英文摘要

### 问题4：论文解读页面生成不完整
- **现象**: `generate_insights.py` 未被调用
- **原因**: 未集成到主流程
- **影响**: 论文解读页面可能缺失

---

## 优化改进（2026-04-19）

### 已完成的优化

1. **✅ 集成完整采集流程**
   - 创建 `scripts/run_daily.py` 一键生成脚本
   - 整合 arXiv 论文、文章、GitHub 采集
   - 支持按步骤执行或完整流程

2. **✅ 自动化论文处理**
   - 创建 `scripts/process_papers.py` 论文处理脚本
   - 支持下载 TeX 源码、提取摘要
   - 自动翻译标题和摘要（基础版）

3. **✅ 自动化封面图生成**
   - 创建 `scripts/generate_covers_v2.py` 封面生成脚本
   - 集成 Seedream 图像生成能力
   - 根据内容类别生成不同风格的封面

4. **✅ 规则检查自动化**
   - `scripts/check_rules.py` 在生成时自动运行
   - 检查失败时显示警告

### 新增脚本

| 脚本 | 功能 | 状态 |
|------|------|------|
| `run_daily.py` | 一键生成完整流程 | ✅ |
| `process_papers.py` | 论文下载和解析 | ✅ |
| `generate_covers_v2.py` | 封面图生成 | ✅ |
| `check_rules.py` | 规则检查 | ✅ |

### 使用方法

```bash
# 完整流程
python3 scripts/run_daily.py

# 跳过采集
python3 scripts/run_daily.py --skip-collect

# 跳过部署
python3 scripts/run_daily.py --skip-deploy

# 指定步骤
python3 scripts/run_daily.py --steps process generate check
```

### 待优化项

1. **翻译 API 集成**
   - 当前使用简单规则翻译
   - 需要集成 MiniMax 或其他翻译 API

2. **顶会论文采集**
   - 当前顶会论文数据不完整
   - 需要从会议官网或 DBLP 采集

3. **封面图质量**
   - 当前使用 Seedream 生成
   - 可考虑从原文提取图片或 PDF 截图
