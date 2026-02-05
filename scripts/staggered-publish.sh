#!/bin/bash
# 逐步发布 Skills 到 ClawdHub（带延迟，避免 Rate Limit）

DIST_DIR="/root/clawd/dist"
REGISTRY_URL="https://www.clawhub.ai/api"
LOG_FILE="/root/clawd/logs/staggered-publish-$(date +%Y%m%d-%H%M%S).log"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "📦 逐步发布 Skills 到 ClawdHub（带延迟）"
log "=========================================="
log ""

cd "$DIST_DIR" || {
    log_error "无法切换到目录: $DIST_DIR"
    exit 1
}

log_info "当前目录: $(pwd)"
log ""

# 使用 clawdhub sync 逐步发布
log_info "运行 clawdhub sync（带延迟）..."
log ""

clawdhub sync --root . --all \
    --registry "$REGISTRY_URL" \
    --changelog "AI Prompts 转换 - 生图/生视频/AI 编码相关" \
    --concurrency 1 \
    2>&1 | tee -a "$LOG_FILE"

exit_code=${PIPESTATUS[0]}

log ""
log "=========================================="
if [ $exit_code -eq 0 ]; then
    log_info "✅ 发布完成！"
else
    log_error "❌ 发布过程中遇到错误（退出码: $exit_code）"
fi
log "=========================================="
log ""
log "日志文件: $LOG_FILE"
log ""

exit $exit_code
