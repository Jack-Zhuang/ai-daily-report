#!/bin/bash
# AI推荐日报 - 自动部署脚本
# 每次修改后自动部署最新内容到 GitHub Pages
# 用法: bash scripts/auto_deploy.sh

set -e

# 自动检测项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "🚀 AI推荐日报 - 自动部署"
echo "📅 $TIMESTAMP"
echo ""

cd "$BASE_DIR" || { echo "❌ 无法进入 $BASE_DIR"; exit 1; }

# 1. 同步封面图到 docs/covers（GitHub Pages以docs/为根）
echo "📦 同步封面图..."
mkdir -p docs/covers
if [ -d covers ]; then
    cp covers/*.jpg docs/covers/ 2>/dev/null || true
    COVER_COUNT=$(ls docs/covers/*.jpg 2>/dev/null | wc -l)
    echo "  ✅ 封面图: $COVER_COUNT 个"
fi

# 2. 部署自检
echo ""
echo "🔍 部署自检..."
if [ -f "docs/index.html" ]; then
    echo "  ✅ 主报告已生成 ($(wc -c < docs/index.html | tr -d ' ') bytes)"
else
    echo "  ⚠️  主报告不存在（尚未生成）"
fi
INSIGHT_COUNT=$(ls docs/insights/*.html 2>/dev/null | wc -l)
echo "  ✅ 解读: $INSIGHT_COUNT 个"

# 3. 推送到 GitHub
echo ""
echo "🔄 推送到 GitHub..."

# 检查是否有未提交的更改
if [ -z "$(git status --porcelain)" ]; then
    echo "  没有新更改，跳过推送"
else
    CHANGED_FILES=$(git status --porcelain | wc -l)
    echo "  检测到 $CHANGED_FILES 个文件变更"
    git add -A
    git commit -m "chore: 自动部署日报 - $TIMESTAMP"
    if git push origin main 2>&1; then
        echo "  ✅ 已推送到 GitHub"
    else
        echo "  ⚠️  推送失败（可能 Token 过期）"
        exit 1
    fi
fi

echo ""
echo "📊 部署统计"
echo "  主报告: docs/index.html"
echo "  解读: $INSIGHT_COUNT 个"
echo "  时间: $TIMESTAMP"
echo ""
echo "✅ 部署完成！"
echo "🌐 GitHub Pages: https://jack-zhuang.github.io/ai-daily-report/"
