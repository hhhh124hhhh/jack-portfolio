#!/bin/bash

# ============================================
# Twitter 报告清理脚本
# 功能：删除超过指定天数的旧报告
# ============================================

set -e

# 配置变量
REPORT_DIR="/root/clawd/ai-prompt-marketplace/reports"
DAYS_TO_KEEP=7
LOG_FILE="$REPORT_DIR/cleanup.log"

# 创建目录
mkdir -p "$REPORT_DIR"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Starting old reports cleanup"
log "=========================================="

# 统计清理前的文件数量
json_before=$(find "$REPORT_DIR" -name "twitter-report-*.json" -type f 2>/dev/null | wc -l)
md_before=$(find "$REPORT_DIR" -name "twitter-summary-*.md" -type f 2>/dev/null | wc -l)

log "Before cleanup: $json_before JSON files, $md_before Markdown files"

# 删除超过指定天数的 JSON 报告
json_deleted=$(find "$REPORT_DIR" -name "twitter-report-*.json" -type f -mtime +$DAYS_TO_KEEP -delete -print 2>/dev/null | wc -l)

# 删除超过指定天数的 Markdown 报告
md_deleted=$(find "$REPORT_DIR" -name "twitter-summary-*.md" -type f -mtime +$DAYS_TO_KEEP -delete -print 2>/dev/null | wc -l)

# 统计清理后的文件数量
json_after=$(find "$REPORT_DIR" -name "twitter-report-*.json" -type f 2>/dev/null | wc -l)
md_after=$(find "$REPORT_DIR" -name "twitter-summary-*.md" -type f 2>/dev/null | wc -l)

log "After cleanup: $json_after JSON files, $md_after Markdown files"
log "Deleted: $json_deleted JSON files, $md_deleted Markdown files"

# 计算磁盘空间释放（可选）
disk_usage=$(du -sh "$REPORT_DIR" 2>/dev/null | awk '{print $1}')
log "Current disk usage: $disk_usage"

log "Cleanup completed successfully"
