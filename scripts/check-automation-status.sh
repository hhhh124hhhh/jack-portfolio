#!/bin/bash
# 自动化流程监控脚本
# 用于 HEARTBEAT 调用，检查 prompt-workflow 运行状态

set -e

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H%M)
LOG_FILE="/root/clawd/logs/automation-status.log"
WORKFLOW_LOG="/root/clawd/logs/prompt-workflow.log"
REPORT_FILE="/root/clawd/reports/automation-status-${DATE}-${TIME}.md"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# 检查最后运行时间
check_last_run() {
    log ""
    log "[1/5] 检查最后运行时间..."

    if [ -f "$WORKFLOW_LOG" ]; then
        LAST_RUN_LINE=$(tail -1 "$WORKFLOW_LOG" | head -1)
        LAST_RUN_TIME=$(tail -1 "$WORKFLOW_LOG" | head -1 | grep -oP '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' || echo "")

        if [ -n "$LAST_RUN_TIME" ]; then
            log_info "✅ 最后运行: $LAST_RUN_TIME"

            # 计算距离现在的时间（分钟）
            LAST_RUN_TS=$(date -d "$LAST_RUN_TIME" +%s 2>/dev/null || echo "0")
            NOW_TS=$(date +%s)
            MINUTES_AGO=$(( (NOW_TS - LAST_RUN_TS) / 60 ))

            log_info "   距离现在: $MINUTES_AGO 分钟"

            if [ $MINUTES_AGO -gt 360 ]; then  # 超过 6 小时
                log_warn "⚠️  距离上次运行超过 6 小时"
            fi
        else
            log_warn "⚠️  无法解析最后运行时间"
        fi
    else
        log_warn "⚠️  工作流日志不存在: $WORKFLOW_LOG"
    fi
}

# 检查最近一次运行是否有错误
check_errors() {
    log ""
    log "[2/5] 检查最近运行错误..."

    if [ -f "$WORKFLOW_LOG" ]; then
        ERROR_COUNT=$(tail -200 "$WORKFLOW_LOG" | grep -i "\[error\]" | wc -l)
        WARN_COUNT=$(tail -200 "$WORKFLOW_LOG" | grep -i "\[warn\]" | wc -l)

        log_info "错误: $ERROR_COUNT, 警告: $WARN_COUNT"

        if [ $ERROR_COUNT -gt 0 ]; then
            log_warn "发现 $ERROR_COUNT 个错误"
            tail -200 "$WORKFLOW_LOG" | grep -i "\[error\]" | tail -5 | tee -a "$LOG_FILE"
        fi
    else
        log_warn "⚠️  工作流日志不存在"
    fi
}

# 统计收集/转换/发布数量
check_statistics() {
    log ""
    log "[3/5] 统计收集/转换/发布数量..."

    # 数据收集统计
    REDDIT_COUNT=$(wc -l /root/clawd/data/prompts/reddit-prompts.jsonl 2>/dev/null || echo "0")
    GITHUB_COUNT=$(wc -l /root/clawd/data/prompts/github-awesome-prompts.jsonl 2>/dev/null || echo "0")
    HN_COUNT=$(wc -l /root/clawd/data/prompts/hacker-news-ai.jsonl 2>/dev/null || echo "0")
    SEARXNG_COUNT=$(wc -l /root/clawd/data/prompts/collected.jsonl 2>/dev/null || echo "0")

    TOTAL_COLLECTED=$((REDDIT_COUNT + GITHUB_COUNT + HN_COUNT + SEARXNG_COUNT))

    log_info "✅ 数据收集总数: $TOTAL_COLLECTED"
    log_info "   Reddit: $REDDIT_COUNT"
    log_info "   GitHub: $GITHUB_COUNT"
    log_info "   HackerNews: $HN_COUNT"
    log_info "   SearXNG: $SEARXNG_COUNT"

    # Skill 转换统计
    GENERATED_SKILLS=$(find /root/clawd/generated-skills -name "*.md" 2>/dev/null | wc -l)
    log_info "✅ 生成的 Skills: $GENERATED_SKILLS"
}

# 检查 ClawdHub 认证状态
check_clawdhub_auth() {
    log ""
    log "[4/5] 检查 ClawdHub 认证状态..."

    # 检查配置文件
    CONFIG_FILE="$HOME/.config/clawdhub/config.json"

    if [ -f "$CONFIG_FILE" ]; then
        # 尝试检查认证状态
        if clawdhub whoami >> "$LOG_FILE" 2>&1; then
            log_info "✅ ClawdHub 认证有效"
        else
            log_warn "⚠️  ClawdHub 认证检查失败（但可能仍然有效）"
        fi
    else
        log_warn "⚠️  ClawdHub 配置文件不存在"
    fi
}

# 发送状态报告
send_report() {
    log ""
    log "[5/5] 生成状态报告..."

    cat >> "$REPORT_FILE" << EOF

## 📊 自动化流程状态

**检查时间**: $(date '+%Y-%m-%d %H:%M:%S')
**报告文件**: $REPORT_FILE

## 🎯 下一步行动

1. 如果距离上次运行超过 6 小时，检查 cron 任务
2. 如果发现错误，查看完整日志: $WORKFLOW_LOG
3. 如果认证失效，重新配置 ClawdHub
4. 如果收集数量偏低，检查数据源配置

---

*自动生成 by Momo*
EOF

    log_info "✅ 报告已生成: $REPORT_FILE"

    # 检查是否在白天（可以发送通知）
    HOUR=$(date +%H)
    if [ "$HOUR" -ge 7 ] && [ "$HOUR" -lt 23 ]; then
        log_info "发送状态通知..."

        # 发送简要通知到 Slack
        MESSAGE="📊 **自动化流程状态检查完成**

检查时间: $(date '+%H:%M')
报告: $REPORT_FILE

详情请查看日志: $LOG_FILE"

        clawdbot message send \
            --channel slack \
            --target D0AB0J4QLAH \
            --message "$MESSAGE" >> "$LOG_FILE" 2>&1 || log_warn "Slack 通知发送失败"
    else
        log_info "深夜模式，跳过通知"
    fi
}

main() {
    log "=========================================="
    log "📊 自动化流程状态检查"
    log "=========================================="

    # 创建报告文件
    cat > "$REPORT_FILE" << EOF
# 自动化流程状态报告

**检查时间**: $(date '+%Y-%m-%d %H:%M:%S')
**执行者**: Momo (HEARTBEAT)

---

EOF

    # 执行检查
    check_last_run
    check_errors
    check_statistics
    check_clawdhub_auth
    send_report

    log ""
    log "=========================================="
    log "✅ 检查完成"
    log "=========================================="
}

main "$@"
