#!/bin/bash

# 检查审查代理状态并记录

MEMORY_DIR="/root/clawd/memory/reviews"
LOG_FILE="$MEMORY_DIR/check-$(date +%Y%m%d).log"
REVIEW_SESSION="agent:main:subagent:e1ca37f2-faac-42e7-a0c7-d57c9e1539f5"
DEV_SESSION="agent:main:subagent:71743fbd-74e2-4ed5-a8b6-4ae25819372f"

# 创建目录
mkdir -p "$MEMORY_DIR"

# 记录检查时间
echo "=== 检查时间: $(date) ===" >> "$LOG_FILE"

# 检查审查代理是否活跃
echo "审查代理状态:" >> "$LOG_FILE"
sessions_history "$REVIEW_SESSION" --limit 3 >> "$LOG_FILE" 2>&1

echo "" >> "$LOG_FILE"

# 检查开发代理状态
echo "开发代理状态:" >> "$LOG_FILE"
sessions_history "$DEV_SESSION" --limit 3 >> "$LOG_FILE" 2>&1

echo "" >> "$LOG_FILE"
echo "-------------------" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 返回最后修改时间（用于判断活跃度）
if [ -f "$LOG_FILE" ]; then
    echo "最后检查: $(stat -c %y "$LOG_FILE")"
fi
