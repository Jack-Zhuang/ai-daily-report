#!/bin/bash
# AI推荐日报 - 完整工作流（采集 + 生成 + 部署）
# 用法: bash scripts/full_workflow.sh [--skip-collect] [--skip-covers]

set -e

BASE_DIR="/home/sandbox/.openclaw/workspace/ai_daily"
cd "$BASE_DIR"

# 解析参数
SKIP_COLLECT=false
SKIP_COVERS=false

for arg in "$@"; do
    case $arg in
        --skip-collect)
            SKIP_COLLECT=true
            shift
            ;;
        --skip-covers)
            SKIP_COVERS=true
            shift
            ;;
    esac
done

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          🌅 AI推荐日报 - 完整工作流                          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "🕐 开始时间: $TIMESTAMP"
echo ""

# 1. 启动 RSSHub（如果需要）
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 步骤 0/5: 启动 RSSHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

bash scripts/start_rsshub.sh

echo ""

# 2. 数据采集
if [ "$SKIP_COLLECT" = false ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📥 步骤 1/5: 数据采集"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    python3 scripts/collect_daily.py

    echo ""
    echo "✅ 数据采集完成"
    echo ""
else
    echo "⏭️  跳过数据采集 (--skip-collect)"
    echo ""
fi

# 2. 选择每日精选
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⭐ 步骤 2/5: 选择每日精选"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 scripts/select_daily_pick.py

echo ""
echo "✅ 每日精选已选择"
echo ""

# 3. 生成报告
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 步骤 3/5: 生成报告"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 scripts/generate_report.py

echo ""
echo "✅ 报告已生成"
echo ""

# 4. 生成封面
if [ "$SKIP_COVERS" = false ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎨 步骤 4/5: 生成封面"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    python3 scripts/batch_generate_covers.py

    echo ""
    echo "✅ 封面已生成"
    echo ""
else
    echo "⏭️  跳过封面生成 (--skip-covers)"
    echo ""
fi

# 5. 部署
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 步骤 5/5: 部署"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

bash scripts/auto_deploy.sh

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          ✅ 完整工作流执行完毕！                             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

END_TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "🕐 结束时间: $END_TIMESTAMP"
echo ""
echo "🌐 访问地址: ~/public_html/ai-daily/"
echo ""
