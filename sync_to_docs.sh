#!/bin/bash
# sync_to_docs.sh - 同步所有文件到 docs 目录
# 用法: ./sync_to_docs.sh

set -e

PROJECT_DIR="/home/sandbox/.openclaw/workspace/ai_daily"
cd "$PROJECT_DIR"

echo "=========================================="
echo "🔄 同步文件到 docs 目录"
echo "=========================================="

# 1. 同步主页
echo "📄 同步主页..."
if [ -f "index.html" ]; then
    cp index.html docs/index.html
    # 修复路径引用
    sed -i 's|docs/insights/|insights/|g' docs/index.html
    sed -i 's|docs/conferences/|conferences/|g' docs/index.html
    sed -i 's|conferences/\([^/]*\)/index\.html|conferences/\1.html|g' docs/index.html
    echo "   ✅ 主页已同步"
else
    echo "   ⚠️ 根目录 index.html 不存在"
fi

# 2. 同步会议页面
echo "📋 同步会议页面..."
mkdir -p docs/conferences
for conf_dir in conferences/*/; do
    if [ -d "$conf_dir" ]; then
        name=$(basename "$conf_dir")
        if [ -f "${conf_dir}index.html" ]; then
            cp "${conf_dir}index.html" "docs/conferences/${name}.html"
            echo "   ✅ ${name}.html"
        fi
    fi
done

# 3. 确保 insights 目录存在
mkdir -p docs/insights/figures

# 4. 检查关键文件
echo ""
echo "🔍 检查关键文件..."
files_ok=true

if [ ! -f "docs/index.html" ]; then
    echo "   ❌ docs/index.html 缺失"
    files_ok=false
else
    echo "   ✅ docs/index.html"
fi

if [ ! -d "docs/conferences" ]; then
    echo "   ❌ docs/conferences/ 缺失"
    files_ok=false
else
    echo "   ✅ docs/conferences/ ($(ls docs/conferences/*.html 2>/dev/null | wc -l) 个文件)"
fi

if [ ! -d "docs/insights" ]; then
    echo "   ❌ docs/insights/ 缺失"
    files_ok=false
else
    echo "   ✅ docs/insights/ ($(ls docs/insights/*.html 2>/dev/null | wc -l) 个文件)"
fi

echo ""
if [ "$files_ok" = true ]; then
    echo "=========================================="
    echo "✅ 同步完成！"
    echo "=========================================="
else
    echo "=========================================="
    echo "⚠️ 同步完成，但有缺失文件"
    echo "=========================================="
fi
