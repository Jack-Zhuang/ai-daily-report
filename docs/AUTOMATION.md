# AI推荐日报 - 自动化部署指南

## 📅 时间规划

| 时间 | 任务 | 预计耗时 |
|------|------|---------|
| 06:00 | 开始采集内容 | 30 分钟 |
| 06:30 | 处理内容、翻译 | 20 分钟 |
| 06:50 | 生成 AI 封面 | 30 分钟 |
| 07:20 | 生成报告 | 5 分钟 |
| 07:25 | **生成论文深度解读** | **30 分钟** |
| 07:55 | 生成解读 HTML 页面 | 10 分钟 |
| 08:05 | 质量检查 | 2 分钟 |
| 08:07 | Git 提交推送 | 3 分钟 |
| **09:00** | **用户看到新日报** | - |

> GitHub Pages 缓存约 1-2 分钟，07:35 左右即可访问

## 🚀 快速使用

### 方式1: 一键运行（推荐）

```bash
cd /home/sandbox/.openclaw/workspace/ai_daily
./scripts/run_now.sh
```

### 方式2: Python 调度器

```bash
# 立即执行
python3 scripts/schedule_daily.py --now

# 定时执行（默认 06:00）
python3 scripts/schedule_daily.py --time 06:00
```

### 方式3: 完整流程控制

```bash
# 跳过采集（使用已有数据）
./scripts/run_now.sh --skip-collect

# 跳过部署（仅本地生成）
./scripts/run_now.sh --skip-deploy
```

## ⏰ 配置定时任务

```bash
# 安装 cron 任务（每天 06:00 自动运行）
./scripts/setup_cron.sh

# 查看当前定时任务
crontab -l

# 查看执行日志
tail -f logs/cron.log
tail -f logs/schedule_$(date +%Y-%m-%d).log
```

## 📊 监控与告警

### 检查脚本

```bash
# 跨天更新测试
python3 scripts/test_cross_day.py

# 规则检查
python3 scripts/check_rules.py

# QA 检查
python3 scripts/qa_check.py
```

### 日志位置

- 执行日志: `logs/run_YYYY-MM-DD.log`
- 调度日志: `logs/schedule_YYYY-MM-DD.log`
- Cron 日志: `logs/cron.log`

## 🔧 故障排查

### 1. 采集失败

```bash
# 手动采集
python3 scripts/collect_daily.py
python3 scripts/collect_github.py
python3 scripts/collect_articles.py
```

### 2. 封面生成失败

```bash
# 检查 Seedream skill
ls ~/.openclaw/workspace/skills/seedream-image_gen/

# 手动生成
python3 scripts/generate_covers_v2.py
```

### 3. 推送失败

```bash
# 检查 Git 状态
git status

# 手动推送
git add -A && git commit -m "更新日报" && git push
```

## 📱 通知配置（可选）

可在 `scripts/notify.py` 中配置：
- 邮件通知
- 企业微信通知
- 钉钉通知

## 🔄 回滚

如果当天日报有问题：

```bash
# 回滚到上一个版本
git log --oneline -5
git revert HEAD
git push
```
