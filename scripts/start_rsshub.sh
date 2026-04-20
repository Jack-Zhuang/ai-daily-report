#!/bin/bash
# RSSHub 启动脚本

RSSHUB_DIR="$HOME/.openclaw/workspace/rsshub-local"
LOG_FILE="$HOME/.openclaw/workspace/ai_daily/logs/rsshub.log"

echo "=== 检查 RSSHub 状态 ==="

# 检查是否已运行
if curl -s http://localhost:1200/ > /dev/null 2>&1; then
    echo "✅ RSSHub 已在运行"
    exit 0
fi

echo "📡 启动 RSSHub..."

# 进入 RSSHub 目录
cd "$RSSHUB_DIR"

# 启动 RSSHub
nohup npm start > "$LOG_FILE" 2>&1 &
RSSHUB_PID=$!

echo "PID: $RSSHUB_PID"

# 等待启动
echo "⏳ 等待启动..."
for i in {1..30}; do
    if curl -s http://localhost:1200/ > /dev/null 2>&1; then
        echo "✅ RSSHub 启动成功！"
        echo "🌐 访问地址: http://localhost:1200"
        exit 0
    fi
    sleep 1
done

echo "❌ RSSHub 启动超时"
echo "📋 查看日志: $LOG_FILE"
exit 1
