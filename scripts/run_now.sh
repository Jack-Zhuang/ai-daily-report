#!/bin/bash
# AI推荐日报 - 一键运行脚本
# 用法: ./run_now.sh [--skip-collect] [--skip-deploy]

set -e

BASE_DIR="/home/sandbox/.openclaw/workspace/ai_daily"
SCRIPTS_DIR="$BASE_DIR/scripts"
TODAY=$(date +%Y-%m-%d)
LOG_FILE="$BASE_DIR/logs/run_$TODAY.log"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "🚀 AI推荐日报 - 一键运行"
log "📅 日期: $TODAY"
log "=========================================="

# 解析参数
SKIP_COLLECT=false
SKIP_DEPLOY=false

for arg in "$@"; do
    case $arg in
        --skip-collect) SKIP_COLLECT=true ;;
        --skip-deploy) SKIP_DEPLOY=true ;;
    esac
done

cd "$BASE_DIR"

# 步骤1: 采集
if [ "$SKIP_COLLECT" = false ]; then
    log ""
    log "📥 步骤1: 内容采集"
    log "------------------------------------------"
    
    log "采集 arXiv 论文..."
    python3 "$SCRIPTS_DIR/collect_daily.py" >> "$LOG_FILE" 2>&1 || log "⚠️ arXiv 采集失败"
    
    log "采集 GitHub Trending..."
    python3 "$SCRIPTS_DIR/collect_github.py" >> "$LOG_FILE" 2>&1 || log "⚠️ GitHub 采集失败"
    
    log "采集热门文章..."
    python3 "$SCRIPTS_DIR/collect_articles.py" >> "$LOG_FILE" 2>&1 || log "⚠️ 文章采集失败"
fi

# 步骤2: 处理
log ""
log "🔧 步骤2: 内容处理"
log "------------------------------------------"

DATA_FILE="$BASE_DIR/daily_data/$TODAY.json"

log "构建每日精选..."
python3 "$SCRIPTS_DIR/build_daily_pick.py" "$DATA_FILE" >> "$LOG_FILE" 2>&1 || log "⚠️ 构建精选失败"

# 步骤3: 封面
log ""
log "🎨 步骤3: 封面生成"
log "------------------------------------------"

log "生成 AI 封面..."
python3 "$SCRIPTS_DIR/generate_covers_v2.py" >> "$LOG_FILE" 2>&1 || log "⚠️ 封面生成失败"

# 步骤4: 报告
log ""
log "📄 步骤4: 报告生成"
log "------------------------------------------"

log "生成日报 HTML..."
python3 "$SCRIPTS_DIR/generate_report.py" >> "$LOG_FILE" 2>&1 || log "⚠️ 报告生成失败"

log "生成文章列表页..."
python3 "$SCRIPTS_DIR/generate_articles_page.py" >> "$LOG_FILE" 2>&1 || log "⚠️ 文章列表页生成失败"

log "生成论文列表页..."
python3 "$SCRIPTS_DIR/generate_papers_list_page.py" >> "$LOG_FILE" 2>&1 || log "⚠️ 论文列表页生成失败"

log "生成论文解读..."
python3 "$SCRIPTS_DIR/generate_paper_insights.py" >> "$LOG_FILE" 2>&1 || log "⚠️ 论文解读生成失败"

log "生成解读 HTML 页面..."
python3 "$SCRIPTS_DIR/generate_insights.py" >> "$LOG_FILE" 2>&1 || log "⚠️ 解读页面生成失败"

# 步骤5: 检查
log ""
log "✅ 步骤5: 质量检查"
log "------------------------------------------"

python3 "$SCRIPTS_DIR/check_rules.py" >> "$LOG_FILE" 2>&1 || log "⚠️ 规则检查失败"

# 步骤6: 部署
if [ "$SKIP_DEPLOY" = false ]; then
    log ""
    log "🚀 步骤6: 部署发布"
    log "------------------------------------------"
    
    git add -A
    git commit -m "自动更新日报 $TODAY" || log "⚠️ 无变更需要提交"
    git push || log "⚠️ 推送失败"
fi

log ""
log "=========================================="
log "🎉 完成!"
log "🌐 https://jack-zhuang.github.io/ai-daily-report/"
log "=========================================="
