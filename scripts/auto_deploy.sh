#!/bin/bash
# AI推荐日报 - 自动部署脚本
# 在每次修改后自动部署最新内容

set -e  # 遇到错误立即退出

BASE_DIR="/home/sandbox/.openclaw/workspace/ai_daily"
DEPLOY_DIR="$HOME/public_html/ai-daily"

echo "========================================"
echo "🚀 AI推荐日报 - 自动部署"
echo "========================================"
echo ""

# 进入项目目录
cd "$BASE_DIR"

# 1. 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 检测到未提交的更改"
    CHANGED_FILES=$(git status --porcelain | wc -l)
    echo "   变更文件数: $CHANGED_FILES"
fi

# 2. 同步文件到部署目录
echo ""
echo "📦 同步文件..."
echo ""

# 创建部署目录（如果不存在）
mkdir -p "$DEPLOY_DIR"

# 同步主报告
if [ -f "docs/index.html" ]; then
    cp "docs/index.html" "$DEPLOY_DIR/"
    echo "  ✅ 主报告: index.html"
fi

# 同步论文解读页面
if [ -d "docs/insights" ]; then
    mkdir -p "$DEPLOY_DIR/insights"
    cp -r docs/insights/*.html "$DEPLOY_DIR/insights/" 2>/dev/null || true
    INSIGHT_COUNT=$(ls -1 "$DEPLOY_DIR/insights"/*.html 2>/dev/null | wc -l)
    echo "  ✅ 论文解读: $INSIGHT_COUNT 个页面"
fi

# 同步封面图
if [ -d "covers" ]; then
    mkdir -p "$DEPLOY_DIR/covers"
    cp -r covers/*.jpg "$DEPLOY_DIR/covers/" 2>/dev/null || true
    COVER_COUNT=$(ls -1 "$DEPLOY_DIR/covers"/*.jpg 2>/dev/null | wc -l)
    echo "  ✅ 封面图: $COVER_COUNT 个"
fi

# 同步归档
if [ -d "archive" ]; then
    # 只同步归档索引，不同步具体归档内容（太大）
    if [ -f "archive/archive.html" ]; then
        cp "archive/archive.html" "$DEPLOY_DIR/" 2>/dev/null || true
        echo "  ✅ 归档索引: archive.html"
    fi
    if [ -f "archive/index.json" ]; then
        cp "archive/index.json" "$DEPLOY_DIR/" 2>/dev/null || true
        echo "  ✅ 归档数据: index.json"
    fi
fi

# 同步其他必要文件
for file in INTERACTION_RULES.md RSSHUB_SOLUTIONS.md; do
    if [ -f "docs/$file" ]; then
        cp "docs/$file" "$DEPLOY_DIR/" 2>/dev/null || true
    fi
done

# 3. 更新时间戳
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "$TIMESTAMP" > "$DEPLOY_DIR/.last_deploy"

echo ""
echo "========================================"
echo "✅ 部署完成！"
echo "========================================"
echo ""
echo "📍 部署目录: $DEPLOY_DIR"
echo "🕐 部署时间: $TIMESTAMP"
echo ""

# 4. 显示部署统计
echo "📊 部署统计:"
echo "   主报告: $([ -f "$DEPLOY_DIR/index.html" ] && echo "✅" || echo "❌")"
echo "   论文解读: $INSIGHT_COUNT 个"
echo "   封面图: $COVER_COUNT 个"
echo ""

# 5. 可选：推送到 GitHub（如果有更改）
if [ -n "$(git status --porcelain)" ] && [ "$AUTO_PUSH" = "true" ]; then
    echo "🔄 推送到 GitHub..."
    git add -A
    git commit -m "chore: 自动部署 - $TIMESTAMP"
    git push origin main
    echo "  ✅ 已推送到 GitHub"
fi

echo "========================================"
