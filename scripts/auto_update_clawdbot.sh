#!/bin/bash
# Clawdbot 自动更新脚本
# 每天 0:00 运行

set -e

# 配置
LOG_FILE="/root/clawd/logs/clawdbot-update.log"
NPM_PACKAGE="clawdbot"
LOCK_FILE="/tmp/clawdbot-update.lock"

# 加载 .npmrc 以获取正确的 registry
export NPM_CONFIG_REGISTRY=https://registry.npmjs.org/

# 防止重复运行
if [ -f "$LOCK_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 另一个更新进程正在运行，跳过" >> "$LOG_FILE"
    exit 0
fi

touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== 开始检查更新 =========="

# 获取当前版本
CURRENT_VERSION=$(clawdbot --version 2>/dev/null || echo "unknown")
log "当前版本: $CURRENT_VERSION"

# 获取最新版本（使用 npm view）
LATEST_VERSION=$(npm view $NPM_PACKAGE version 2>/dev/null || echo "unknown")
log "最新版本: $LATEST_VERSION"

# 比较版本
if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    log "已是最新版本，无需更新"
    exit 0
fi

log "发现新版本: $LATEST_VERSION，开始更新..."

# 执行更新
log "运行: sudo npm install -g $NPM_PACKAGE@latest"
if sudo npm install -g $NPM_PACKAGE@latest >> "$LOG_FILE" 2>&1; then
    NEW_VERSION=$(clawdbot --version 2>/dev/null || echo "unknown")
    log "更新成功! 新版本: $NEW_VERSION"

    # 可选: 重启 gateway
    # log "重启 gateway..."
    # clawdbot gateway restart >> "$LOG_FILE" 2>&1 || true

    # 可选: 发送通知到 Slack
    # if command -v curl &> /dev/null; then
    #     curl -X POST "YOUR_SLACK_WEBHOOK_URL" \
    #         -H 'Content-Type: application/json' \
    #         -d "{\"text\": \"🦞 Clawdbot 已更新: $CURRENT_VERSION → $NEW_VERSION\"}"
    # fi
else
    log "更新失败！请检查日志"
    exit 1
fi

log "========== 更新检查完成 =========="
