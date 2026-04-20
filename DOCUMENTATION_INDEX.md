# AI 推荐日报 - 文档索引

## 📚 文档导航

### 🚀 新手入门

| 文档 | 说明 | 阅读时间 |
|------|------|----------|
| [README.md](README.md) | 项目总览和完整文档 | 15 分钟 |
| [QUICKSTART.md](QUICKSTART.md) | 5 分钟快速上手 | 5 分钟 |
| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | 项目概览和统计 | 5 分钟 |

### 🔧 技术文档

| 文档 | 说明 | 适用人群 |
|------|------|----------|
| [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) | 技术架构详解 | 开发者 |
| API 集成文档 | API 使用说明 | 开发者 |
| 数据格式规范 | JSON 数据结构 | 开发者 |

### 📖 使用手册

| 文档 | 说明 | 场景 |
|------|------|------|
| 数据采集指南 | 如何采集数据 | 日常运维 |
| 报告生成指南 | 如何生成报告 | 日常运维 |
| 封面生成指南 | 如何生成封面 | 日常运维 |
| 部署运维指南 | 如何部署和维护 | 运维人员 |

## 🎯 按场景查找

### 我想快速了解项目
→ 阅读 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

### 我想快速上手使用
→ 阅读 [QUICKSTART.md](QUICKSTART.md)

### 我想深入了解技术细节
→ 阅读 [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)

### 我想查看完整文档
→ 阅读 [README.md](README.md)

### 我想解决具体问题
→ 查看 [故障排查](TECHNICAL_GUIDE.md#故障排查)

## 📂 项目文件结构

```
ai_daily/
├── 📄 文档文件
│   ├── README.md                    # 主文档
│   ├── QUICKSTART.md                # 快速上手
│   ├── TECHNICAL_GUIDE.md           # 技术架构
│   ├── PROJECT_OVERVIEW.md          # 项目概览
│   └── DOCUMENTATION_INDEX.md       # 文档索引（本文件）
│
├── 📂 scripts/                      # 脚本目录
│   ├── collect_*.py                # 数据采集脚本
│   ├── generate_*.py               # 报告生成脚本
│   ├── batch_*.py                  # 批量处理脚本
│   └── enhanced/                   # 增强模块
│
├── 📂 daily_data/                   # 每日数据
├── 📂 covers/                       # 封面图
├── 📂 insights_enhanced/            # 论文解读
├── 📂 docs/                         # 部署目录
├── 📂 archive/                      # 历史归档
└── 📂 logs/                         # 日志文件
```

## 🔍 快速查找

### 常用命令

```bash
# 每日完整流程
python3 scripts/run_daily.py

# 采集数据
python3 scripts/collect_daily.py

# 生成报告
python3 scripts/generate_report.py

# 生成封面
python3 scripts/batch_generate_covers.py

# 查看进度
bash scripts/check_cover_progress.sh
```

### 常见问题

| 问题 | 解决方案 | 文档位置 |
|------|----------|----------|
| 采集失败 | 检查网络和日志 | [故障排查](TECHNICAL_GUIDE.md#故障排查) |
| 封面生成失败 | 检查 API 配置 | [封面生成](README.md#封面图生成) |
| 报告生成异常 | 检查数据格式 | [报告生成](README.md#报告生成) |

## 📊 文档更新记录

| 日期 | 更新内容 | 作者 |
|------|----------|------|
| 2026-04-20 | 创建完整文档体系 | AI 推荐日报团队 |

## 💡 文档贡献

欢迎贡献文档！请遵循以下规范：

1. 使用 Markdown 格式
2. 保持文档结构清晰
3. 添加适当的示例代码
4. 及时更新索引

## 📞 获取帮助

- 📖 查看文档
- 🐛 提交 Issue
- 💬 加入 Discord 讨论

---

*最后更新: 2026-04-20*
