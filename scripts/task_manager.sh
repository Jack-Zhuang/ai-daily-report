#!/bin/bash
# AI推荐日报 - 任务分配脚本
# 根据当前状态自动分配任务给子代理

BASE_DIR="/home/sandbox/.openclaw/workspace/ai_daily"
cd "$BASE_DIR"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          🤖 AI推荐日报 - 智能任务分配                       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 1. 检查封面生成进度
COVERS_GENERATED=$(ls -1 covers/*.jpg 2>/dev/null | wc -l)
COVERS_TARGET=93

echo "📊 系统状态检查:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎨 封面生成:"
echo "   进度: $COVERS_GENERATED / $COVERS_TARGET ($(expr $COVERS_GENERATED \* 100 / $COVERS_TARGET)%)"

# 2. 检查数据状态
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)

if [ -f "daily_data/$TODAY.json" ]; then
    DATA_DATE=$TODAY
elif [ -f "daily_data/$YESTERDAY.json" ]; then
    DATA_DATE=$YESTERDAY
else
    DATA_DATE="none"
fi

if [ "$DATA_DATE" != "none" ]; then
    PAPERS=$(python3 -c "import json; print(len(json.load(open('daily_data/$DATA_DATE.json')).get('arxiv_papers', [])))")
    GITHUB=$(python3 -c "import json; print(len(json.load(open('daily_data/$DATA_DATE.json')).get('github_projects', [])))")
    ARTICLES=$(python3 -c "import json; print(len(json.load(open('daily_data/$DATA_DATE.json')).get('articles', [])))")

    echo ""
    echo "📄 数据状态 ($DATA_DATE):"
    echo "   arXiv论文: $PAPERS 条"
    echo "   GitHub项目: $GITHUB 条"
    echo "   热门文章: $ARTICLES 条"
else
    echo ""
    echo "📄 数据状态: ❌ 无数据"
fi

# 3. 检查 RSSHub 状态
if curl -s http://localhost:1200/ > /dev/null 2>&1; then
    echo ""
    echo "📡 RSSHub: ✅ 运行中"
else
    echo ""
    echo "📡 RSSHub: ❌ 未运行"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 4. 决定需要执行的任务
TASKS=()

# 封面未完成
if [ $COVERS_GENERATED -lt $COVERS_TARGET ]; then
    REMAINING=$((COVERS_TARGET - COVERS_GENERATED))
    TASKS+=("封面生成: 还需生成 $REMAINING 个封面")
fi

# RSSHub 未运行
if ! curl -s http://localhost:1200/ > /dev/null 2>&1; then
    TASKS+=("启动 RSSHub")
fi

# 数据不完整
if [ "$DATA_DATE" = "none" ] || [ "$PAPERS" = "0" ]; then
    TASKS+=("数据采集: 采集今日数据")
fi

# 5. 显示任务列表
if [ ${#TASKS[@]} -eq 0 ]; then
    echo "✅ 所有任务已完成！"
    echo ""
    echo "🎉 系统状态良好，无需额外操作"
else
    echo "📋 待执行任务:"
    echo ""
    for i in "${!TASKS[@]}"; do
        echo "  $((i+1)). ${TASKS[$i]}"
    done
    echo ""

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # 6. 执行任务
    echo "🚀 开始执行任务..."
    echo ""

    # 启动 RSSHub
    if ! curl -s http://localhost:1200/ > /dev/null 2>&1; then
        echo "📡 启动 RSSHub..."
        bash scripts/start_rsshub.sh
        echo ""
    fi

    # 封面生成（后台运行）
    if [ $COVERS_GENERATED -lt $COVERS_TARGET ]; then
        echo "🎨 封面生成任务已在后台运行"
        echo "   查看进度: bash scripts/monitor_cover_generation.sh"
        echo ""
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "💡 提示:"
    echo "   - 封面生成在后台运行，约需 1.5 小时"
    echo "   - 使用 monitor_cover_generation.sh 查看进度"
    echo "   - 完成后会自动部署"
fi

echo ""

# 7. 质量检查
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 质量检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 scripts/qa_check.py

echo ""
