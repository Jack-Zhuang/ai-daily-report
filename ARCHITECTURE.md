# AI推荐日报 - 项目架构规范

> **重要**: 此文档定义了项目的文件结构和路径规范，所有修改必须遵循此规范！

## 1. 网站模块总览

主页 (`docs/index.html`) 包含以下 **6 大模块**：

| 模块 | 数据来源 | 数据文件 | 展示位置 |
|------|----------|----------|----------|
| ⭐ 每日精选 | 编辑精选 | `cache/all_articles.json` | 主页 `#daily-pick` |
| 🔥 热门文章 | 公众号/知乎/36氪等 | `cache/all_articles.json` | 主页 `#hot` |
| 📈 GitHub Trending | GitHub API | `cache/github_cache.json` | 主页 `#github` |
| 📄 arXiv 最新 | arXiv API | `cache/arxiv_cache.json` | 主页 `#papers` + 独立页面 |
| 🏆 顶会论文 | AMiner/会议官网 | `cache/conference_papers.json` | 主页 `#conferences` + 独立页面 |
| 🌐 内容来源 | 静态配置 | - | 主页 `#sources` |

## 2. GitHub Pages 配置

- **Pages 源目录**: `/docs`
- **访问 URL**: `https://jack-zhuang.github.io/ai-daily-report/`
- **关键规则**: 只有 `docs/` 目录下的文件会被部署到线上

## 3. 完整文件结构

```
ai_daily/
├── docs/                              # GitHub Pages 根目录（唯一部署源）
│   ├── index.html                     # 主页（包含所有 6 大模块）
│   │
│   ├── conferences/                   # 顶会论文独立页面
│   │   ├── arXiv_2026.html           # arXiv 论文列表（25篇）
│   │   ├── KDD_2025.html             # KDD 2025 论文列表
│   │   ├── WSDM_2025.html            # WSDM 2025 论文列表
│   │   ├── RecSys_2025.html          # RecSys 2025 论文列表
│   │   ├── WWW_2025.html             # WWW 2025 论文列表
│   │   ├── CIKM_2025.html            # CIKM 2025 论文列表
│   │   └── SIGIR_2025.html           # SIGIR 2025 论文列表
│   │
│   ├── insights/                      # 论文深度解读页面
│   │   ├── 2026-04-26_2604_21593.html # 单篇论文解读
│   │   ├── 2026-04-26_2604_21896.html
│   │   └── figures/                   # 论文图表
│   │       └── 2604_21593/
│   │           ├── fig_1.jpeg
│   │           ├── fig_2.jpeg
│   │           └── ...
│   │
│   ├── covers/                        # 文章封面图
│   │   └── xxx.jpg
│   │
│   └── archive/                       # 往期日报归档
│       └── 2026-04-25/
│           └── index.html
│
├── cache/                             # 数据缓存（不部署，仅用于生成页面）
│   ├── all_articles.json              # 所有文章数据（热门文章 + 每日精选）
│   ├── arxiv_cache.json               # arXiv 论文数据
│   ├── github_cache.json              # GitHub Trending 数据
│   ├── conference_papers.json         # 顶会论文数据
│   └── pdfs/                          # 论文 PDF 缓存
│
├── index.html                         # 主页开发版本（需同步到 docs/）
├── conferences/                       # 会议页面开发版本
│   ├── arXiv_2026/
│   │   └── index.html
│   ├── KDD_2025/
│   │   └── index.html
│   └── ...
│
├── ARCHITECTURE.md                    # 本文档
└── sync_to_docs.sh                    # 同步脚本
```

## 4. 数据流向

```
┌─────────────────────────────────────────────────────────────────┐
│                        数据采集层                                │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│ 公众号/知乎  │  arXiv API  │  GitHub API │  AMiner/会议官网     │
└──────┬──────┴──────┬──────┴──────┬──────┴──────────┬──────────┘
       │             │             │                  │
       ▼             ▼             ▼                  ▼
┌─────────────┬─────────────┬─────────────┬─────────────────────┐
│all_articles │arxiv_cache  │github_cache │conference_papers    │
│   .json     │   .json     │   .json     │     .json           │
└──────┬──────┴──────┬──────┴──────┬──────┴──────────┬──────────┘
       │             │             │                  │
       └─────────────┴──────┬──────┴──────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │   页面生成器     │
                   │ (Python 脚本)   │
                   └────────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ docs/         │   │ docs/         │   │ docs/         │
│ index.html    │   │ conferences/  │   │ insights/     │
│ (主页6模块)   │   │ (会议论文)    │   │ (论文解读)    │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │   GitHub Pages  │
                   │  (自动部署)      │
                   └─────────────────┘
```

## 5. 各模块详细说明

### 5.1 每日精选 (Daily Pick)

- **数据源**: `cache/all_articles.json` 中标记为精选的文章
- **展示位置**: 主页 `#daily-pick` 区域
- **特点**: 编辑人工筛选的高质量内容
- **链接**: 点击跳转到原文或详情页

### 5.2 热门文章 (Hot Articles)

- **数据源**: `cache/all_articles.json`
- **来源**: 机器之心、量子位、36氪、InfoQ、知乎等
- **展示位置**: 主页 `#hot` 区域
- **分类**: 推荐、Agent、LLM 等
- **链接**: 点击跳转到原文

### 5.3 GitHub Trending

- **数据源**: `cache/github_cache.json`
- **展示位置**: 主页 `#github` 区域
- **内容**: 高增长开源项目
- **指标**: Stars 数、增长率、语言

### 5.4 arXiv 最新

- **数据源**: `cache/arxiv_cache.json`
- **展示位置**: 
  - 主页 `#papers` 区域（显示前 5 篇）
  - `docs/conferences/arXiv_2026.html`（完整列表）
- **特点**: 最新预印本论文，带中文解读
- **链接**: 
  - "查看论文" → arXiv 原文
  - "查看解读" → `docs/insights/xxx.html`

### 5.5 顶会论文

- **数据源**: `cache/conference_papers.json`
- **展示位置**:
  - 主页 `#conferences` 区域（各会议概览）
  - `docs/conferences/{会议名}_{年份}.html`（详细列表）
- **支持的会议**: WSDM、KDD、RecSys、WWW、CIKM、SIGIR

### 5.6 论文深度解读

- **位置**: `docs/insights/*.html`
- **内容**: 
  - 论文摘要翻译
  - 核心贡献分析
  - 方法架构图
  - 实验结果图表
  - 个人点评
- **图表**: `docs/insights/figures/{论文ID}/`

## 6. 路径引用规范

### 6.1 在 `docs/index.html` 中的引用

```html
<!-- 正确 -->
<a href="conferences/arXiv_2026.html">arXiv 论文</a>
<a href="insights/2026-04-26_2604_21593.html">论文解读</a>
<img src="covers/xxx.jpg">

<!-- 错误 -->
<a href="docs/conferences/...">  <!-- 多了 docs/ 前缀 -->
```

### 6.2 在 `docs/conferences/*.html` 中的引用

```html
<a href="../index.html">返回日报</a>
<a href="../insights/2026-04-26_2604_21593.html">查看解读</a>
```

### 6.3 在 `docs/insights/*.html` 中的引用

```html
<img src="figures/2604_21593/fig_1.jpeg">
<a href="../index.html">返回日报</a>
```

## 7. 文件命名规范

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 主页 | `index.html` | `docs/index.html` |
| 会议页面 | `{会议名}_{年份}.html` | `docs/conferences/KDD_2025.html` |
| 论文解读 | `{日期}_{论文ID}.html` | `docs/insights/2026-04-26_2604_21593.html` |
| 论文图表 | `fig_{序号}.jpeg` | `docs/insights/figures/2604_21593/fig_1.jpeg` |
| 封面图 | `{文章ID}.jpg` | `docs/covers/article_001.jpg` |

## 8. Git 提交检查清单

每次提交前必须检查：

- [ ] `docs/index.html` 是否是最新版本
- [ ] 所有路径引用是否正确（无 `docs/` 前缀）
- [ ] 会议页面是否同步到 `docs/conferences/`
- [ ] 论文解读页面是否在 `docs/insights/`
- [ ] 图表文件是否在 `docs/insights/figures/`
- [ ] 数据缓存是否更新（如有变化）

## 9. 同步脚本使用

```bash
# 同步所有文件到 docs 目录
./sync_to_docs.sh

# 手动同步主页
cp index.html docs/index.html
sed -i 's|docs/insights/|insights/|g' docs/index.html
sed -i 's|docs/conferences/|conferences/|g' docs/index.html
```

## 10. 常见错误及修复

| 错误 | 原因 | 修复方法 |
|------|------|----------|
| 页面 404 | 文件不在 `docs/` 目录 | 复制到 `docs/` 对应位置 |
| 链接失效 | 路径多了 `docs/` 前缀 | 使用相对路径，去掉 `docs/` |
| 图片不显示 | 图表路径错误 | 检查 `figures/` 相对路径 |
| 内容不更新 | 只修改了根目录文件 | 同步到 `docs/` 目录 |
| 数据不同步 | cache 未更新 | 重新运行数据采集脚本 |

## 11. 代码逻辑规范（重要！）

### 11.1 按钮文案判断逻辑

**问题**：每日精选中混合了 arXiv 论文和普通技术文章，按钮文案需要区分。

**正确逻辑**：
```javascript
// 根据来源判断是否是 arXiv 论文
const isArxivPaper = item.source === 'arXiv' || item.type === 'paper' || (item.link && item.link.includes('arxiv.org'));

if (isArxivPaper) {
    // arXiv 论文：显示"查看 arXiv 原文"或"查看论文解读"
} else if (item.type === 'github') {
    // GitHub 项目：显示"访问 GitHub"
} else {
    // 普通文章：显示"阅读原文"
}
```

**错误逻辑**（已修复）：
```javascript
// ❌ 错误：仅根据 pickType 判断，导致普通文章也显示"查看 arXiv 原文"
if (pickType === 'paper') {
    footerHtml = "查看 arXiv 原文";
}
```

### 11.2 数据类型字段说明

| 字段 | 含义 | 可能值 |
|------|------|--------|
| `type` | 内容类型 | `article`, `paper`, `github` |
| `source` | 来源平台 | `arXiv`, `机器之心`, `量子位`, `InfoQ技术文章`, `GitHub` 等 |
| `pick_type` | 精选类型 | `paper`, `article`, `github`（已废弃，应使用 `type`） |
| `has_insight` | 是否有解读 | `true`, `false` |

### 11.3 同步时的注意事项

**每次同步 `index.html` 到 `docs/index.html` 时，必须保留以下修复：**

1. ✅ 路径修复：`docs/insights/` → `insights/`
2. ✅ 路径修复：`docs/conferences/` → `conferences/`
3. ✅ 路径修复：`conferences/xxx/index.html` → `conferences/xxx.html`
4. ✅ 按钮文案逻辑：根据 `source` 判断是否是 arXiv
5. ✅ arXiv 数据注入：`arxivPapers` 不能为空数组
6. ✅ pickType 优先使用 item.type：`item.pick_type || item.type || 'paper'`
7. ✅ JavaScript 初始化时机：使用 `document.readyState` 判断
8. ✅ 热门文章点击：使用 `item.id` 而不是索引
9. ✅ 论文ID替换：`replace(/[^\w\-]/g, '_')` 处理点号等特殊字符
10. ✅ 顶会论文 has_insight 判断：决定跳转解读页还是原文

### 11.4 已验证存在的优化（无需修复）

以下优化已确认存在于当前代码中：

| 优化项 | 状态 | 说明 |
|--------|------|------|
| JavaScript 初始化时机 | ✅ | `document.readyState` + `DOMContentLoaded` |
| arXiv 论文点击事件 | ✅ | 使用 `addEventListener` DOM 方式绑定 |
| 热门文章点击索引 | ✅ | 使用 `item.id` 查找而非数组索引 |
| 论文ID点号替换 | ✅ | `replace(/[^\w\-]/g, '_')` |
| 顶会论文 has_insight | ✅ | 根据 `has_insight` 决定跳转目标 |
| 封面图支持 | ✅ | `cover_image` 字段和 CSS 背景 |
| DOM 加载完成判断 | ✅ | `if (document.readyState === 'loading')` |
| **GitHub 项目历史去重** | ✅ | `history/published.json` 记录已发布项目，30天内不重复 |

### 11.5 GitHub 项目去重机制

**问题**：热门项目（如 langchain）长期占据 GitHub Trending，导致每天重复推送。

**解决方案**：
1. 维护 `history/published.json` 记录已发布的 GitHub 项目 ID
2. 生成日报时过滤掉 30 天内已发布的项目
3. 每次生成后更新历史记录

**相关文件**：
- `scripts/generate_report.py` - 包含过滤逻辑
- `history/published.json` - 历史记录文件
- `scripts/history_manager.py` - 历史管理模块（备用）

### 11.6 GitHub Trending 按增长排序

**问题**：之前显示的是 Star 数最多的老牌项目（如 langchain），而不是真正热门的新项目。

**解决方案**：
1. 优先从 GitHub Trending 页面获取数据（`since=daily`）
2. 提取每个项目的当日增长数（`growth` 字段）
3. 按 `growth` 降序排序，优先展示增长最快的项目
4. 如果 Trending 页面获取失败，fallback 到 API 搜索

**数据字段**：
- `growth`: 当日新增 Star 数
- `growth_rate`: 增长百分比
- `stars`: 总 Star 数

**排序逻辑**：
```python
all_repos.sort(key=lambda x: (x.get('growth', 0), x.get('stars', 0)), reverse=True)
```

---

**最后更新**: 2026-04-26
**维护者**: AI推荐日报项目组
