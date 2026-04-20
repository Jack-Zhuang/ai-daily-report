# AI 推荐日报 - 项目概览

## 📊 项目统计

| 指标 | 数值 |
|------|------|
| 核心脚本 | 40+ 个 |
| 数据采集源 | 6 个 |
| 支持的顶会 | 6 个 |
| 日均处理论文 | 40-50 篇 |
| 封面生成速度 | ~1 分钟/张 |
| 报告生成时间 | < 1 分钟 |

## 🎯 核心功能

### 1. 自动化采集
- ✅ arXiv 论文（每日更新）
- ✅ GitHub Trending 项目
- ✅ 技术博客文章
- ✅ 微信公众号文章
- ✅ 顶会论文（RecSys, KDD, SIGIR, WSDM, WWW, CIKM）

### 2. 智能分析
- ✅ 工业界评分算法
- ✅ 论文价值评估
- ✅ AI 摘要生成
- ✅ 中文翻译

### 3. 深度解读
- ✅ PDF 内容提取
- ✅ 章节结构解析
- ✅ 图表公式提取
- ✅ AI 深度解读
- ✅ 流程图生成
- ✅ 代码示例

### 4. 视觉增强
- ✅ AI 封面生成
- ✅ 高质量图片
- ✅ 分类主题

### 5. 报告生成
- ✅ 交互式 HTML
- ✅ 响应式设计
- ✅ 历史归档
- ✅ 搜索功能

## 📁 目录结构一览

```
ai_daily/
├── 📄 README.md                    # 项目文档
├── 📄 QUICKSTART.md                # 快速上手
├── 📄 TECHNICAL_GUIDE.md           # 技术架构
├── 📄 PROJECT_OVERVIEW.md          # 项目概览（本文件）
│
├── 📂 scripts/                     # 核心脚本 (40+)
│   ├── collect_*.py               # 数据采集
│   ├── generate_*.py              # 报告生成
│   ├── batch_*.py                 # 批量处理
│   └── enhanced/                  # 增强模块
│
├── 📂 daily_data/                  # 每日数据
│   └── YYYY-MM-DD.json
│
├── 📂 covers/                      # 封面图 (86+)
│   ├── paper_*.jpg
│   ├── pick_*.jpg
│   └── github_*.jpg
│
├── 📂 insights_enhanced/           # 论文解读 (60+)
│   └── YYYY-MM-DD_<arxiv_id>.md
│
├── 📂 docs/                        # 部署目录
│   ├── index.html
│   ├── insights/
│   └── covers/
│
├── 📂 archive/                     # 历史归档
│   └── YYYY-MM-DD/
│
├── 📂 conferences/                 # 顶会数据
│   ├── RecSys_2025/
│   ├── KDD_2025/
│   └── ...
│
└── 📂 logs/                        # 日志文件
    ├── batch_process.log
    └── cover_generation.log
```

## 🔧 技术栈

### 后端
- **Python 3.12**: 主要开发语言
- **Requests**: HTTP 请求
- **BeautifulSoup4**: HTML 解析
- **Feedparser**: RSS 解析
- **PyMuPDF**: PDF 处理

### AI 服务
- **MiniMax API**: 论文解读、翻译
- **Seedream API**: 封面图生成

### 前端
- **HTML5/CSS3**: 页面结构
- **JavaScript**: 交互逻辑
- **Mermaid**: 流程图渲染
- **KaTeX**: 数学公式渲染

### 部署
- **Nginx**: Web 服务器
- **Cron**: 定时任务

## 📈 数据流程

```
采集 → 处理 → 生成 → 部署 → 归档
 ↓      ↓      ↓      ↓      ↓
2min   5min   1min   10s    5s
```

## 🎨 封面图示例

| 类型 | 示例 | 大小 |
|------|------|------|
| 论文 | `paper_2604.15037.jpg` | 280KB |
| 精选 | `pick_1.jpg` | 200KB |
| 项目 | `github_1.jpg` | 310KB |

## 📊 内容分类

### 论文分类
- `agent`: AI 智能体
- `llm`: 大语言模型
- `rec`: 推荐系统
- `paper`: 其他论文

### 评分维度
- **工业界评分** (0-10): 实用性、落地潜力
- **论文价值** (0-10): 创新性、影响力

## 🚀 性能指标

| 操作 | 时间 | 备注 |
|------|------|------|
| 数据采集 | 2 分钟 | 并行采集 |
| 论文翻译 | 5 分钟 | 50 篇论文 |
| 报告生成 | 30 秒 | HTML + 归档 |
| 封面生成 | 1 分钟/张 | Seedream API |
| 完整流程 | 30-60 分钟 | 含封面生成 |

## 📝 维护清单

### 每日
- [ ] 检查采集日志
- [ ] 验证报告生成
- [ ] 监控封面生成进度

### 每周
- [ ] 清理过期缓存
- [ ] 备份数据文件
- [ ] 更新依赖包

### 每月
- [ ] 检查 API 用量
- [ ] 优化采集策略
- [ ] 更新文档

## 🔮 路线图

### v1.0 (当前)
- ✅ 基础采集功能
- ✅ 报告生成
- ✅ 封面生成
- ✅ 论文解读

### v1.1 (计划中)
- [ ] 用户订阅系统
- [ ] 邮件推送
- [ ] 移动端适配

### v2.0 (未来)
- [ ] 知识图谱
- [ ] 个性化推荐
- [ ] 社区功能

## 📞 联系方式

- **项目地址**: https://github.com/your-org/ai-daily
- **问题反馈**: https://github.com/your-org/ai-daily/issues
- **社区讨论**: https://discord.gg/clawd

---

*最后更新: 2026-04-20*
