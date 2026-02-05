#!/bin/bash
# AI Prompt Hunter - 完整自动化工作流
# 功能：搜索、评估、转换、上传 AI 提示词到 ClawdHub

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
WORKSPACE="/root/clawd"
DATA_DIR="$WORKSPACE/data/prompts"
DIST_DIR="$WORKSPACE/dist/skills"
LOGS_DIR="$WORKSPACE/logs"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# 日志文件
MAIN_LOG="$LOGS_DIR/ai-prompt-hunter-$TIMESTAMP.log"

# Telegram 配置（可选）
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

# 函数：输出带时间戳的日志
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$MAIN_LOG"
}

# 函数：发送 Telegram 通知
send_telegram() {
    if [[ -n "$TELEGRAM_BOT_TOKEN" && -n "$TELEGRAM_CHAT_ID" ]]; then
        local message="$1"
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=$message" \
            -d "parse_mode=HTML" >/dev/null
    fi
}

# 函数：阶段开始
phase_start() {
    local phase="$1"
    log "INFO" "========================================"
    log "INFO" "🚀 开始阶段: $phase"
    log "INFO" "========================================"
}

# 函数：阶段完成
phase_complete() {
    local phase="$1"
    local result="$2"
    log "INFO" "✅ 阶段完成: $phase - $result"
}

# 函数：阶段失败
phase_fail() {
    local phase="$1"
    local error="$2"
    log "ERROR" "❌ 阶段失败: $phase"
    log "ERROR" "错误: $error"
    send_telegram "🚨 <b>AI Prompt Hunter 错误</b>%0A阶段: $phase%0A错误: $error"
}

# 主流程
main() {
    cd "$WORKSPACE"

    log "INFO" "========================================"
    log "INFO" "🏹 AI Prompt Hunter 启动"
    log "INFO" "========================================"
    log "INFO" "开始时间: $(date)"

    send_telegram "🏹 <b>AI Prompt Hunter</b> 开始运行"

    # 阶段 1: 搜索 AI 提示词（使用 SearXNG）
    phase_start "搜索 AI 提示词 (SearXNG)"
    if python3 "$WORKSPACE/scripts/collect-prompts-via-searxng.py" 2>&1 | tee -a "$MAIN_LOG"; then
        phase_complete "搜索 AI 提示词" "成功"
    else
        phase_fail "搜索 AI 提示词" "SearXNG 搜索失败"
        return 1
    fi

    # 阶段 2: 搜索 X (Twitter) 提示词（可选）
    if [[ "${ENABLE_X_SEARCH:-false}" == "true" ]]; then
        phase_start "搜索 X 提示词"
        if python3 "$WORKSPACE/scripts/search-x-prompts.py" 2>&1 | tee -a "$MAIN_LOG"; then
            phase_complete "搜索 X 提示词" "成功"
        else
            log "WARNING" "⚠️  X 搜索失败，继续下一步"
        fi
    fi

    # 阶段 3: 评估提示词质量
    phase_start "评估提示词质量"
    if python3 "$WORKSPACE/scripts/evaluate-prompts.py" 2>&1 | tee -a "$MAIN_LOG"; then
        phase_complete "评估提示词质量" "成功"
    else
        phase_fail "评估提示词质量" "评估失败"
        return 1
    fi

    # 阶段 4: 转换为 Skills
    phase_start "转换为 Skills"
    if python3 "$WORKSPACE/scripts/convert-prompts-to-skills.py" 2>&1 | tee -a "$MAIN_LOG"; then
        phase_complete "转换为 Skills" "成功"
    else
        phase_fail "转换为 Skills" "转换失败"
        return 1
    fi

    # 阶段 5: 上传到 ClawdHub
    phase_start "上传到 ClawdHub"
    if bash "$WORKSPACE/scripts/batch-upload-skills-v3.sh" 2>&1 | tee -a "$MAIN_LOG"; then
        phase_complete "上传到 ClawdHub" "成功"
    else
        phase_fail "上传到 ClawdHub" "上传失败"
        return 1
    fi

    # 完成
    log "INFO" "========================================"
    log "INFO" "✅ AI Prompt Hunter 完成"
    log "INFO" "========================================"
    log "INFO" "完成时间: $(date)"

    # 统计结果
    local skill_count=$(ls -1 "$DIST_DIR"/*.skill 2>/dev/null | wc -l)
    log "INFO" "生成的 Skills: $skill_count"

    send_telegram "✅ <b>AI Prompt Hunter</b> 完成！%0A生成的 Skills: $skill_count%0A日志: $MAIN_LOG"

    return 0
}

# 执行主流程
main
exit_code=$?

# 备份日志
cp "$MAIN_LOG" "$LOGS_DIR/ai-prompt-hunter-latest.log"

exit $exit_code
