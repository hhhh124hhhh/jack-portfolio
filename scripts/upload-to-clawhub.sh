#!/bin/bash
# ClawdHub Skill 上传脚本（使用正确的 registry）
# 解决：明确指定 registry URL 和 workdir

set -e

# 配置
REGISTRY_URL="https://www.clawhub.ai/api"
WORKDIR="/root/clawd/generated-skills"
LOG_FILE="/root/clawd/logs/clawdhub-upload.log"

# Slack 通知配置
SLACK_DM_ID="D0AB0J4QLAH"

# 创建目录
mkdir -p "$(dirname $LOG_FILE)"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

main() {
    log "=========================================="
    log "📦 ClawdHub Skill 上传"
    log "=========================================="
    log ""

    log_info "配置信息:"
    log "  Registry: $REGISTRY_URL"
    log "  Workdir: $WORKDIR"
    log ""

    # 检查目录
    if [ ! -d "$WORKDIR" ]; then
        log_error "Skills 目录不存在: $WORKDIR"
        send_slack "❌ Skills 目录不存在，请检查路径"
        exit 1
    fi

    # 统计
    TOTAL_SKILLS=$(find "$WORKDIR" -name "*.md" -type f | wc -l)
    SUCCESS_COUNT=0
    FAILED_COUNT=0
    FAILED_SKILLS=()

    if [ $TOTAL_SKILLS -eq 0 ]; then
        log_warn "没有找到 Skill 文件"
        send_slack "⚠️  没有找到 Skill 文件，请先生成 Skills"
        exit 0
    fi

    log_info "找到 $TOTAL_SKILLS 个 Skill 文件"
    log ""

    # 上传每个 Skill
    for skill_md in "$WORKDIR"/*.md; do
        if [[ "$skill_md" == *"report"* ]]; then
            continue
        fi

        skill_name=$(basename "$skill_md" .md)
        skill_dir="$WORKDIR/$skill_name"

        log_info "📦 处理 Skill: $skill_name"

        try {
            # 创建临时目录
            TEMP_DIR="/tmp/clawdhub-upload-$$-$skill_name"
            mkdir -p "$TEMP_DIR"

            # 复制 SKILL.md
            cp "$skill_md" "$TEMP_DIR/SKILL.md"

            # 进入临时目录
            cd "$TEMP_DIR"

            # 调用 clawdhub publish（使用正确的参数）
            if clawdhub publish \
                --registry "$REGISTRY_URL" \
                --slug "$skill_name" \
                --name "$skill_name" \
                --version "1.0.0" \
                --changelog "从 Twitter 转换的 AI Prompt Skill" 2>&1 | tee -a "$LOG_FILE"; then

                SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
                log_info "✅ 成功发布: $skill_name"
            else
                FAILED_COUNT=$((FAILED_COUNT + 1))
                FAILED_SKILLS+=("$skill_name")
                log_error "❌ 发布失败: $skill_name"
            fi

            # 清理
            cd - > /dev/null
            rm -rf "$TEMP_DIR"
        } catch {
            log_error "❌ 处理 $skill_name 时出错: $1"
            FAILED_COUNT=$((FAILED_COUNT + 1))
            FAILED_SKILLS+=("$skill_name")
        }
    done

    # 输出统计
    log ""
    log "=========================================="
    log "📊 上传统计"
    log "=========================================="
    log_info "✅ 成功: $SUCCESS_COUNT"
    log_error "❌ 失败: $FAILED_COUNT"
    log ""

    if [ $FAILED_COUNT -gt 0 ]; then
        log_error "失败的 Skills:"
        for skill in "${FAILED_SKILLS[@]}"; do
            log "  - $skill"
        done
        log ""

        SLACK_MESSAGE="❌ **ClawdHub 上传完成**

📊 **统计**:
• 成功: $SUCCESS_COUNT
• 失败: $FAILED_COUNT

**失败的 Skills**:
${FAILED_SKILLS[@]}"
    else
        log_info "所有 Skills 上传成功！"
        log ""

        SLACK_MESSAGE="✅ **ClawdHub 上传完成！**

📊 **统计**:
• 成功: $SUCCESS_COUNT
• 失败: 0

**结果**: 所有 Skills 已成功发布到 ClawdHub！

🔗 **查看 Skills**: https://www.clawhub.ai/ 搜索你的 Skills"
"
    fi

    # 发送 Slack 通知
    log "发送 Slack 通知..."
    send_slack "$SLACK_MESSAGE"

    log ""
    log "=========================================="
    log "✅ 脚本完成"
    log "=========================================="
    log ""
    log "日志文件: $LOG_FILE"
}

main "$@"
