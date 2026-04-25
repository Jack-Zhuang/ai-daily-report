# AI推荐日报 - 项目结构

## 核心流程

```
run_daily.py (主入口)
    ├── collect_daily.py      → 采集 arXiv 论文
    ├── collect_articles.py   → 采集热门文章
    ├── collect_github.py     → 采集 GitHub 项目
    ├── collect_conference_papers.py → 采集顶会论文
    ├── translator.py         → 翻译标题和摘要
    ├── build_daily_pick.py   → 构建每日精选
    ├── generate_report.py    → 生成日报 HTML
    └── generate_paper_deep_insight.py → 深度解读论文（下载PDF → 解析 → LLM分析 → 生成HTML）
```

## 论文深度解读流程

```
generate_paper_deep_insight.py
    │
    ├── 1. 下载 PDF (arXiv)
    │       └── 保存到 cache/pdfs/
    │
    ├── 2. 解析 PDF
    │       ├── markitdown (首选)
    │       ├── pdftotext (备选)
    │       └── PyPDF2 (最后备选)
    │
    ├── 3. LLM 深度分析
    │       └── MiniMax API
    │           ├── 提取摘要、背景、方法
    │           ├── 生成架构图描述
    │           ├── 提取伪代码和公式
    │           ├── 分析实验结果
    │           └── 生成 FAQ
    │
    └── 4. 生成 HTML
            └── 使用 templates/paper_insight_template.html
```

## 目录结构

```
ai_daily/
├── scripts/              # 核心脚本
│   ├── run_daily.py      # 主入口（一键生成）
│   ├── collect_*.py      # 采集脚本
│   ├── generate_*.py     # 生成脚本
│   ├── translator.py     # 翻译服务
│   └── generate_paper_deep_insight.py  # 论文深度解读
├── cache/                # 数据缓存
│   ├── arxiv_cache.json  # arXiv 论文（主数据源）
│   ├── github_cache.json # GitHub 项目
│   ├── conference_papers.json # 顶会论文
│   └── pdfs/             # 下载的 PDF 文件
├── config/               # 配置文件
│   ├── sources.json      # 数据源配置
│   └── rss_sources.json  # RSS 源配置
├── daily_data/           # 每日数据
├── docs/                 # 生成的页面
│   ├── index.html        # 日报主页
│   └── insights/         # 论文解读页
├── templates/            # 页面模板
│   └── paper_insight_template.html  # 论文解读模板
└── archive/              # 归档（废弃代码）
    ├── deprecated_scripts/
    └── deprecated_config/
```

## 数据源

| 来源 | 文件 | 说明 |
|------|------|------|
| arXiv | `arxiv_cache.json` | 主论文数据源（96篇） |
| GitHub | `github_cache.json` | 热门开源项目 |
| 顶会 | `conference_papers.json` | KDD/WSDM/RecSys 等 |

## 使用方法

```bash
# 完整流程
python3 scripts/run_daily.py

# 仅生成（跳过采集）
python3 scripts/run_daily.py --skip-collect

# 仅采集
python3 scripts/run_daily.py --steps collect

# 深度解读论文（测试单篇）
python3 scripts/generate_paper_deep_insight.py --test

# 深度解读所有论文
python3 scripts/generate_paper_deep_insight.py --regenerate-all

# 深度解读前10篇
python3 scripts/generate_paper_deep_insight.py --regenerate-all 10
```

## 论文解读页内容

| 模块 | 内容来源 |
|------|----------|
| 摘要速览 | PDF 解析 + LLM 提取 |
| 研究背景 | PDF 解析 + LLM 总结 |
| 方法详解 | PDF 解析 + LLM 分析 |
| 架构设计 | LLM 生成 Mermaid 图 |
| 算法实现 | PDF 提取伪代码 + LLM 格式化 |
| 核心公式 | PDF 提取 + LaTeX 格式化 |
| 实验分析 | PDF 表格提取 + LLM 总结 |
| 结果对比 | PDF 表格数据 |
| FAQ | LLM 生成 |
