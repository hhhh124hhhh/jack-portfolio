#!/bin/bash
# 简化版上下文使用率检查
# 通过估算对话长度来触发清理

set -e

LOG_FILE="/root/clawd/logs/context-clean.log"
STATE_FILE="/root/clawd/memory/heartbeat-state.json"
THRESHOLD=50

mkdir -p "$(dirname "$LOG_FILE")"

# 估算上下文使用率（基于消息历史长度）
estimate_context_usage() {
    # 通过查看 HEARTBEAT.md 的行数来估算
    local heartbeat_lines=$(wc -l < /root/clawd/HEARTBEAT.md 2>/dev/null || echo 0)
    local daily_lines=$(wc -l < /root/clawd/memory/2026-02-05.md 2>/dev/null || echo 0)

    # 简单估算：每 100 行 ≈ 1%
    local estimated_usage=$(( (heartbeat_lines + daily_lines) / 100 ))

    # 限制在 0-100 之间
    if [ $estimated_usage -gt 100 ]; then
        estimated_usage=100
    fi

    echo $estimated_usage
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

main() {
    local usage=$(estimate_context_usage)

    log "估算上下文使用率: ${usage}% (阈值: ${THRESHOLD}%)"

    if [ "$usage" -gt "$THRESHOLD" ]; then
        log "⚠️  超过阈值，触发清理..."

        if bash /root/clawd/scripts/backup-and-flush-memory.sh >> "$LOG_FILE" 2>&1; then
            log "✅ 清理成功"
        else
            log "❌ 清理失败"
            exit 1
        fi
    else
        log "✅ 上下文使用率正常"
    fi
}

main "$@"
