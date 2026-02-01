#!/bin/bash
# 端到端 AI 提示词自动化流程
# 收集 → 转换 → 发布 → 通知

set -e

# 配置
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H%M)
LOG_FILE="/root/clawd/logs/prompt-workflow.log"
REPORT_DIR="/root/clawd/reports"

# Slack 通知配置
SLACK_DM_ID="D0AB0J4QLAH"
FEISHU_USER_ID="ou_3bc5290afc1a94f38e23dc17c35f26d6"

# 创建目录
mkdir -p "$(dirname $LOG_FILE)"
mkdir -p "$REPORT_DIR"

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

# Slack 通知函数
send_slack() {
    local message=$1
    clawdbot message send \
        --channel slack \
        --target "$SLACK_DM_ID" \
        --message "$message" >> "$LOG_FILE" 2>&1 || log_error "Slack 通知发送失败"
}

# Feishu 通知函数
send_feishu() {
    local message=$1
    clawdbot message send \
        --channel feishu \
        --target "$FEISHU_USER_ID" \
        --message "$message" >> "$LOG_FILE" 2>&1 || log_error "Feishu 通知发送失败"
}

# 发送双平台通知
send_notification() {
    local level=$1
    local message=$2

    case $level in
        "info")
            emoji="ℹ️"
            ;;
        "success")
            emoji="✅"
            ;;
        "warning")
            emoji="⚠️"
            ;;
        "error")
            emoji="❌"
            ;;
        *)
            emoji="📋"
            ;;
    esac

    local full_message="${emoji} ${message}"

    log_info "发送通知..."
    send_slack "$full_message"
    send_feishu "$full_message"
}

main() {
    log "=========================================="
    log "🚀 AI 提示词自动化流程开始"
    log "=========================================="

    # 标记：是否有新数据
    HAS_NEW_DATA=false

    # 阶段 1: 数据收集 (V2 - Firecrawl + Twitter)
    log ""
    log "[阶段 1/4] 数据收集 (V2 - Firecrawl + Twitter)"

    if bash /root/clawd/scripts/collect-all-sources-prompts-v2.sh >> "$LOG_FILE" 2>&1; then
        TOTAL_COLLECTED=$(tail -50 "$LOG_FILE" | grep "📊 总收集:" | tail -1 | sed 's/.*总收集: //' | sed 's/ 条//' | awk '{$1=$1};1' || echo "0")
        TOTAL_PROMPTS=$(tail -50 "$LOG_FILE" | grep "📝 总提示词:" | tail -1 | sed 's/.*总提示词: //' | sed 's/ 个//' | awk '{$1=$1};1' || echo "0")
        log_info "✅ 数据收集完成: $TOTAL_COLLECTED 条, $TOTAL_PROMPTS 提示词"
        if [ "$TOTAL_COLLECTED" -gt 0 ]; then
            HAS_NEW_DATA=true
        fi
    else
        log_error "❌ 数据收集失败"
        send_notification "error" "数据收集失败，请检查日志"
        exit 1
    fi

    # 阶段 2: 转换成 Skills
    log ""
    log "[阶段 2/4] 转换成 Skills"

    if node /root/clawd/scripts/tweet-to-skill-converter.js >> "$LOG_FILE" 2>&1; then
        SKILLS_GENERATED=$(tail -50 "$LOG_FILE" | grep "转换完成！生成了" | sed 's/.*生成了 //' | sed 's/ 个.*//' | awk '{$1=$1};1' || echo "0")
        SKILLS_CONVERTED=$(tail -50 "$LOG_FILE" | grep "转换完成！" | grep -oP '\d+(?= 个 Skill 文件)' | tail -1 || echo "0")
        log_info "✅ 转换完成: 生成了 $SKILLS_GENERATED 个 Skill"
        if [ "$SKILLS_GENERATED" -gt 0 ]; then
            HAS_NEW_DATA=true
        fi
    else
        log_warn "⚠️  Skill 转换部分失败（可能没有新数据）"
    fi

    # 阶段 3: 发布到 ClawdHub
    log ""
    log "[阶段 3/4] 发布到 ClawdHub"

    if bash /root/clawd/scripts/auto-publish-skills.sh >> "$LOG_FILE" 2>&1; then
        PUBLISHED_COUNT=$(tail -50 "$LOG_FILE" | grep "✅ Successfully published:" | wc -l || echo "0")
        FAILED_COUNT=$(tail -50 "$LOG_FILE" | grep "❌ Failed to publish:" | wc -l || echo "0")
        log_info "✅ 发布完成: 成功 $PUBLISHED_COUNT 个，失败 $FAILED_COUNT 个"
        if [ "$PUBLISHED_COUNT" -gt 0 ]; then
            HAS_NEW_DATA=true
        fi
    else
        log_warn "⚠️  发布失败或没有新 Skill"
    fi

    # 阶段 4: 生成报告
    log ""
    log "[阶段 4/4] 生成报告"

    REPORT_FILE="$REPORT_DIR/workflow-report-${DATE}-${TIME}.md"

    cat > "$REPORT_FILE" << EOF
# AI 提示词自动化流程报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 📊 流程统计

| 阶段 | 状态 | 详情 |
|------|------|------|
| 1. 数据收集 | ✅ 完成 | ${TOTAL_COLLECTED} 条提示词, ${TOTAL_PROMPTS} 提取 |
| 2. Skill 转换 | ✅ 完成 | ${SKILLS_GENERATED} 个 Skill |
| 3. ClawdHub 发布 | ✅ 完成 | ${PUBLISHED_COUNT} 成功, ${FAILED_COUNT} 失败 |

## 📈 数据统计

**数据源**: Reddit, GitHub, Hacker News, SearXNG, Firecrawl 🔥, Twitter/X 🐦

**收集数据**:
- Reddit prompts: $(wc -l /root/clawd/data/prompts/reddit-prompts.jsonl 2>/dev/null || echo "0")
- GitHub prompts: $(wc -l /root/clawd/data/prompts/github-awesome-prompts.jsonl 2>/dev/null || echo "0")
- Hacker News: $(wc -l /root/clawd/data/prompts/hacker-news-ai.jsonl 2>/dev/null || echo "0")
- SearXNG prompts: $(wc -l /root/clawd/data/prompts/collected.jsonl 2>/dev/null || echo "0")

**转换统计**:
- 生成的 Skills: ${SKILLS_GENERATED}
- 转换的推文: ${SKILLS_CONVERTED}
- 使用的推文: 总计 $(ls -1 /root/clawd/generated-skills/*.md 2>/dev/null | wc -l || echo "0")

**发布统计**:
- 成功发布: ${PUBLISHED_COUNT}
- 发布失败: ${FAILED_COUNT}
- 总 Skills: $((PUBLISHED_COUNT + FAILED_COUNT))

## 🎯 下一步

1. **查看已发布的 Skills**: 访问 ClawdHub
2. **评估质量**: 检查用户反馈和使用数据
3. **优化转换**: 调整评分标准和转换策略

---

*报告自动生成*
EOF

    log_info "✅ 报告已生成: $REPORT_FILE"

    # Git 提交
    log ""
    log "提交到 Git..."
    cd /root/clawd
    git add reports/workflow-report-*.md generated-skills/ data/prompts/*.jsonl 2>/dev/null || true
    git commit -m "自动化流程完成 - ${DATE} ${TIME}

- 数据收集: ${TOTAL_COLLECTED} 条
- Skill 转换: ${SKILLS_GENERATED} 个
- ClawdHub 发布: ${PUBLISHED_COUNT} 成功, ${FAILED_COUNT} 失败
- 报告: $REPORT_FILE" || log_warn "⚠️  没有变更需要提交"

    git push origin master 2>&1 | tee -a "$LOG_FILE" || log_warn "⚠️  Git push 失败或已最新"

    # 总结通知（仅在有新数据时发送）
    log ""
    log "=========================================="
    log "✅ 自动化流程完成！"
    log "=========================================="

    log ""
    log "=========================================="
    log "✅ 全部完成！"
    log "=========================================="
    log ""
    log "数据收集: ${TOTAL_COLLECTED} 条"
    log "Skill 转换: ${SKILLS_GENERATED} 个"
    log "ClawdHub 发布: ${PUBLISHED_COUNT} 成功, ${FAILED_COUNT} 失败"
    log "报告: $REPORT_FILE"
    log "日志: $LOG_FILE"

    # 只在有新数据时发送通知
    if [ "$HAS_NEW_DATA" = true ]; then
        log_info "有新数据，发送通知..."

        SUMMARY="📊 **自动化流程完成！**

**流程统计**:
• 数据收集: ${TOTAL_COLLECTED} 条, ${TOTAL_PROMPTS} 提示词
• Skill 转换: ${SKILLS_GENERATED} 个
• ClawdHub 发布: ${PUBLISHED_COUNT} 成功
• 失败: ${FAILED_COUNT} 个

**数据源**: Reddit, GitHub, Hacker News, SearXNG, Firecrawl 🔥, Twitter/X 🐦

**报告**: ${REPORT_FILE}
**详情**: 查看完整日志: ${LOG_FILE}
🚀 **下一个周期**: 明天 9:00
📱 **通知**: 已发送到 Feishu 和 Slack

---
*自动化运行*"

        send_notification "success" "$SUMMARY"
    else
        log_info "没有新数据，跳过通知"
    fi
}

# 运行主函数
main "$@"
