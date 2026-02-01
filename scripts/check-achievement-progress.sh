#!/bin/bash
# 成就系统进度检查脚本
# 用于 HEARTBEAT 调用，检查成就系统开发进度

set -e

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H%M)
LOG_FILE="/root/clawd/logs/achievement-progress.log"
REPORT_FILE="/root/clawd/reports/achievement-progress-${DATE}-${TIME}.md"

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

# 检查子代理状态
check_subagents() {
    log ""
    log "[1/4] 检查子代理状态..."

    # 使用 sessions_list 检查活跃会话
    ACTIVE_SESSIONS=$(clawdbot sessions list --limit 50 2>/dev/null || echo "检查失败")

    # 查找 achievement-system-dev 相关的会话
    ACHIEVEMENT_SESSION=$(echo "$ACTIVE_SESSIONS" | grep -i "achievement" || echo "")

    if [ -n "$ACHIEVEMENT_SESSION" ]; then
        log_info "✅ 发现活跃的成就系统会话"
        echo "$ACHIEVEMENT_SESSION" >> "$REPORT_FILE"
    else
        log_warn "⚠️  未发现活跃的成就系统会话"
    fi
}

# 检查终端工具开发进度
check_terminal_tools() {
    log ""
    log "[2/4] 检查终端工具开发进度..."

    # 检查 achievement-system-dev 目录
    ACHIEVEMENT_DIR="/root/clawd/achievement-system-dev"

    if [ -d "$ACHIEVEMENT_DIR" ]; then
        # 检查文件数量
        FILE_COUNT=$(find "$ACHIEVEMENT_DIR" -type f | wc -l)
        # 检查最近修改时间
        LAST_MOD=$(find "$ACHIEVEMENT_DIR" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)

        log_info "✅ 成就系统目录存在"
        log_info "   文件数量: $FILE_COUNT"
        log_info "   最近修改: $LAST_MOD"

        echo "### 终端工具开发进度" >> "$REPORT_FILE"
        echo "- 目录: $ACHIEVEMENT_DIR" >> "$REPORT_FILE"
        echo "- 文件数量: $FILE_COUNT" >> "$REPORT_FILE"
        echo "- 最近修改: $LAST_MOD" >> "$REPORT_FILE"
    else
        log_warn "⚠️  成就系统目录不存在: $ACHIEVEMENT_DIR"
    fi
}

# 检查成就数据收集状态
check_data_collection() {
    log ""
    log "[3/4] 检查成就数据收集状态..."

    # 检查成就数据目录
    DATA_DIR="/root/clawd/memory/achievements"

    if [ -d "$DATA_DIR" ]; then
        # 统计成就数据文件
        DATA_FILES=$(find "$DATA_DIR" -type f -name "*.json" 2>/dev/null | wc -l)
        DATA_SIZE=$(du -sh "$DATA_DIR" 2>/dev/null | cut -f1)

        log_info "✅ 成就数据目录存在"
        log_info "   数据文件: $DATA_FILES"
        log_info "   数据大小: $DATA_SIZE"

        echo "### 成就数据收集状态" >> "$REPORT_FILE"
        echo "- 数据目录: $DATA_DIR" >> "$REPORT_FILE"
        echo "- 数据文件: $DATA_FILES" >> "$REPORT_FILE"
        echo "- 数据大小: $DATA_SIZE" >> "$REPORT_FILE"
    else
        log_warn "⚠️  成就数据目录不存在: $DATA_DIR"
    fi
}

# 发送进度报告
send_report() {
    log ""
    log "[4/4] 生成进度报告..."

    cat >> "$REPORT_FILE" << EOF

## 📊 进度总结

**检查时间**: $(date '+%Y-%m-%d %H:%M:%S')
**报告文件**: $REPORT_FILE

## 🎯 下一步行动

1. 如果子代理不活跃，重新启动 achievement-system-dev
2. 如果终端工具开发缓慢，调整优先级
3. 如果数据收集不足，加强监控

---

*自动生成 by Momo*
EOF

    log_info "✅ 报告已生成: $REPORT_FILE"

    # 检查是否在白天（可以发送通知）
    HOUR=$(date +%H)
    if [ "$HOUR" -ge 7 ] && [ "$HOUR" -lt 23 ]; then
        log_info "发送进度通知..."

        # 发送简要通知到 Slack
        MESSAGE="📊 **成就系统进度检查完成**

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
    log "📊 成就系统进度检查"
    log "=========================================="

    # 创建报告文件
    cat > "$REPORT_FILE" << EOF
# 成就系统进度报告

**检查时间**: $(date '+%Y-%m-%d %H:%M:%S')
**执行者**: Momo (HEARTBEAT)

---

EOF

    # 执行检查
    check_subagents
    check_terminal_tools
    check_data_collection
    send_report

    log ""
    log "=========================================="
    log "✅ 检查完成"
    log "=========================================="
}

main "$@"
