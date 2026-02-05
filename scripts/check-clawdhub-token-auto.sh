#!/bin/bash

# ClawdHub Token 自动检测脚本（非交互式）
# 用途：自动化检测 token 有效性，记录到日志

set -e

# 配置文件路径
CONFIG_FILE="$HOME/.config/clawdhub/config.json"
LOG_FILE="/root/clawd/memory/clawdhub-token-check.log"
ALERT_LOG="/root/clawd/memory/clawdhub-token-alerts.txt"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

alert() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$ALERT_LOG"
    log "ALERT: $1"
}

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    alert "配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 提取当前 token
TOKEN=$(jq -r '.token // empty' "$CONFIG_FILE" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
    alert "未找到 Token"
    exit 1
fi

# 测试 token 是否有效
if clawdhub search "test" --limit 1 >/dev/null 2>&1; then
    log "Token 有效: ${TOKEN:0:20}..."
    exit 0
else
    alert "Token 无效: ${TOKEN:0:20}..."
    exit 1
fi
