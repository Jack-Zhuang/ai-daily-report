#!/bin/bash
# 封面生成进度监控脚本

LOG_FILE="$HOME/.openclaw/workspace/ai_daily/logs/cover_generation.log"
PROGRESS_FILE="$HOME/.openclaw/workspace/ai_daily/logs/cover_generation_progress.json"

echo "========================================"
echo "📊 封面生成进度监控"
echo "========================================"

# 检查进程
if ps aux | grep batch_generate_covers | grep -v grep > /dev/null; then
    echo "✅ 任务状态: 运行中"
    ps aux | grep batch_generate_covers | grep -v grep | awk '{print "   PID:", $2}'
else
    echo "⏸️  任务状态: 未运行"
fi

echo ""

# 统计进度
if [ -f "$LOG_FILE" ]; then
    TOTAL=$(grep -c "🎨\|✓" "$LOG_FILE" 2>/dev/null || echo 0)
    SUCCESS=$(grep -c "✅" "$LOG_FILE" 2>/dev/null || echo 0)
    SKIPPED=$(grep -c "✓" "$LOG_FILE" 2>/dev/null || echo 0)

    echo "📈 处理统计:"
    echo "   总计处理: $TOTAL 条"
    echo "   新生成: $SUCCESS 条"
    echo "   已跳过: $SKIPPED 条"
fi

echo ""

# 显示最新日志
if [ -f "$LOG_FILE" ]; then
    echo "📝 最新日志 (最后 10 行):"
    tail -10 "$LOG_FILE" | sed 's/^/   /'
fi

echo ""
echo "========================================"

# 如果任务完成，显示最终统计
if [ -f "$PROGRESS_FILE" ] && ! ps aux | grep batch_generate_covers | grep -v grep > /dev/null; then
    echo "✅ 任务已完成"
    if command -v jq > /dev/null; then
        echo ""
        echo "📊 最终统计:"
        cat "$PROGRESS_FILE" | jq '.stats' 2>/dev/null | sed 's/^/   /'
    fi
fi
