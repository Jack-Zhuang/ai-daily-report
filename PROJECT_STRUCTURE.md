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
    └── generate_paper_insight.py → 生成论文解读页
```

## 目录结构

```
ai_daily/
├── scripts/              # 核心脚本
│   ├── run_daily.py      # 主入口（一键生成）
│   ├── collect_*.py      # 采集脚本
│   ├── generate_*.py     # 生成脚本
│   └── translator.py     # 翻译服务
├── cache/                # 数据缓存
│   ├── arxiv_cache.json  # arXiv 论文（主数据源）
│   ├── github_cache.json # GitHub 项目
│   └── conference_papers.json # 顶会论文
├── config/               # 配置文件
│   ├── sources.json      # 数据源配置
│   └── rss_sources.json  # RSS 源配置
├── daily_data/           # 每日数据
├── docs/                 # 生成的页面
│   ├── index.html        # 日报主页
│   └── insights/         # 论文解读页
├── templates/            # 页面模板
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
```
