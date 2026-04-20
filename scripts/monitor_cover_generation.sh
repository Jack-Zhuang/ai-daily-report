#!/bin/bash
# 封面生成进度监控

COVERS_DIR="/home/sandbox/.openclaw/workspace/ai_daily/covers"
LOG_FILE="/home/sandbox/.openclaw/workspace/ai_daily/logs/cover_regeneration.log"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          🎨 封面生成进度监控                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 统计已生成封面
GENERATED=$(ls -1 "$COVERS_DIR"/*.jpg 2>/dev/null | wc -l)
VALID=$(find "$COVERS_DIR" -name "*.jpg" -size +10k 2>/dev/null | wc -l)

echo "📊 生成统计:"
echo "  已生成: $GENERATED 个"
echo "  有效封面: $VALID 个"
echo "  目标: 93 个"
echo ""

# 计算进度
if [ $GENERATED -gt 0 ]; then
    PERCENT=$((GENERATED * 100 / 93))
    echo "  进度: $PERCENT%"
    echo ""
fi

# 显示最新日志
echo "📝 最新日志:"
tail -10 "$LOG_FILE" 2>/dev/null | sed 's/^/  /'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
