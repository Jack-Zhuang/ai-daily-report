#!/bin/bash
# AI推荐日报 - Cron 定时任务配置

SCRIPT_DIR="/home/sandbox/.openclaw/workspace/ai_daily/scripts"
LOG_DIR="/home/sandbox/.openclaw/workspace/ai_daily/logs"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 添加 cron 任务
# 每天 06:00 开始采集和处理
# 每天 08:30 生成报告
# 每天 09:00 发布

(crontab -l 2>/dev/null | grep -v "schedule_daily.py"; cat << CRON
# AI推荐日报 - 每天早上6点开始
0 6 * * * cd /home/sandbox/.openclaw/workspace/ai_daily && /usr/bin/python3 scripts/schedule_daily.py --now >> logs/cron.log 2>&1
CRON
) | crontab -

echo "✅ Cron 任务已配置"
echo ""
echo "当前 crontab:"
crontab -l
