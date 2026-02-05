#!/bin/bash
# 逐个发布 Skills 到 ClawdHub（带 Rate Limit 重试机制）

DIST_DIR="/root/clawd/dist"
REGISTRY_URL="https://www.clawhub.ai/api"
LOG_FILE="/root/clawd/logs/publish-skills-retry-$(date +%Y%m%d-%H%M%S).log"
SUCCESS_COUNT=0
FAILED_COUNT=0
SKIPPED_COUNT=0
RETRY_COUNT=0
FAILED_SKILLS=()
SKIPPED_SKILLS=()

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_skip() {
    echo -e "${BLUE}[SKIP]${NC} $1" | tee -a "$LOG_FILE"
}

log_retry() {
    echo -e "${CYAN}[RETRY]${NC} $1" | tee -a "$LOG_FILE"
}

# 带重试的发布函数
publish_with_retry() {
    local skill_dir="$1"
    local skill_name="$2"
    local display_name="$3"
    local max_retries=3
    local retry_delay=5
    local attempt=1

    while [ $attempt -le $max_retries ]; do
        log_info "尝试 $attempt/$max_retries: 发布 $skill_name"

        local tmp_output="/tmp/publish-output-$$-$skill_name-attempt$attempt.txt"

        # 执行发布
        clawdhub publish "$skill_dir" \
            --registry "$REGISTRY_URL" \
            --slug "$skill_name" \
            --name "$display_name" \
            --version "1.0.0" \
            --changelog "AI Prompts 转换 - 生图/生视频/AI 编码相关" > "$tmp_output" 2>&1

        local exit_code=$?

        # 检查结果
        if grep -q "Version already exists" "$tmp_output"; then
            log_skip "⏭️  已存在，跳过: $skill_name"
            rm -f "$tmp_output"
            return 2  # SKIPPED
        elif grep -q "Published successfully\|✔ OK. Published" "$tmp_output"; then
            log_info "✓ 成功发布: $skill_name"
            rm -f "$tmp_output"
            return 0  # SUCCESS
        elif grep -qi "rate limit" "$tmp_output"; then
            log_warn "遇到 Rate Limit，等待 $retry_delay 秒后重试..."
            rm -f "$tmp_output"
            RETRY_COUNT=$((RETRY_COUNT + 1))

            if [ $attempt -lt $max_retries ]; then
                sleep $retry_delay
                retry_delay=$((retry_delay * 2))  # 指数退避
                if [ $retry_delay -gt 60 ]; then
                    retry_delay=60  # 最大等待 60 秒
                fi
            fi
            attempt=$((attempt + 1))
        else
            # 其他错误
            cat "$tmp_output" | tee -a "$LOG_FILE"
            rm -f "$tmp_output"

            if [ $attempt -lt $max_retries ]; then
                log_warn "发布失败，等待 $retry_delay 秒后重试..."
                sleep $retry_delay
                retry_delay=$((retry_delay * 2))
                if [ $retry_delay -gt 60 ]; then
                    retry_delay=60
                fi
                attempt=$((attempt + 1))
            else
                return 1  # FAILED
            fi
        fi
    done

    return 1  # FAILED（重试次数用尽）
}

main() {
    log "=========================================="
    log "📦 逐个发布 Skills 到 ClawdHub（带重试）"
    log "=========================================="
    log ""

    log_info "配置信息:"
    log "  Dist 目录: $DIST_DIR"
    log "  Registry: $REGISTRY_URL"
    log "  最大重试次数: 3（指数退避，最大 60 秒）"
    log "  发布间隔: 5 秒"
    log ""

    if [ ! -d "$DIST_DIR" ]; then
        log_error "Dist 目录不存在: $DIST_DIR"
        exit 1
    fi

    cd "$DIST_DIR" || {
        log_error "无法切换到目录: $DIST_DIR"
        exit 1
    }

    # 获取所有 .skill 文件
    TOTAL_SKILLS=$(ls -1 *.skill 2>/dev/null | wc -l)

    log_info "找到 $TOTAL_SKILLS 个 .skill 文件"
    log ""

    if [ $TOTAL_SKILLS -eq 0 ]; then
        log_warn "没有 .skill 文件需要发布"
        exit 0
    fi

    # 逐个处理
    for skill_file in *.skill; do
        if [ ! -f "$skill_file" ]; then
            continue
        fi

        skill_name=$(basename "$skill_file" .skill)
        temp_dir="/tmp/skill-upload-$$-$skill_name"

        log_info "📦 处理: $skill_name"

        # 创建临时目录
        mkdir -p "$temp_dir"
        cd "$temp_dir"

        # 解压 .skill 文件
        if ! unzip -q "$DIST_DIR/$skill_file"; then
            log_error "解压失败: $skill_file"
            cd "$DIST_DIR"
            rm -rf "$temp_dir"
            FAILED_COUNT=$((FAILED_COUNT + 1))
            FAILED_SKILLS+=("$skill_name: 解压失败")
            sleep 5
            continue
        fi

        # 查找 SKILL.md
        skill_md_path=""
        if [ -f "SKILL.md" ]; then
            skill_md_path="SKILL.md"
        else
            for subdir in */; do
                if [ -d "$subdir" ] && [ -f "$subdir/SKILL.md" ]; then
                    skill_md_path="$subdir/SKILL.md"
                    break
                fi
            done
        fi

        if [ ! -f "$skill_md_path" ]; then
            log_warn "SKILL.md 不存在: $skill_name"
            cd "$DIST_DIR"
            rm -rf "$temp_dir"
            sleep 5
            continue
        fi

        # 提取显示名称
        display_name=$(grep "^# " "$skill_md_path" 2>/dev/null | head -1 | cut -d '#' -f2 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        if [ -z "$display_name" ]; then
            display_name="$skill_name"
        fi

        # 获取 SKILL.md 所在目录
        skill_dir="$(dirname "$skill_md_path")"

        # 切换回原始目录，准备发布
        cd "$DIST_DIR"

        # 发布（带重试）
        publish_with_retry "$temp_dir/$skill_dir" "$skill_name" "$display_name"
        result=$?

        case $result in
            0)  # SUCCESS
                SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
                ;;
            1)  # FAILED
                FAILED_COUNT=$((FAILED_COUNT + 1))
                FAILED_SKILLS+=("$skill_name")
                ;;
            2)  # SKIPPED
                SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
                SKIPPED_SKILLS+=("$skill_name")
                ;;
        esac

        # 清理临时目录
        rm -rf "$temp_dir"

        # 发布间隔
        sleep 5
    done

    # 输出统计
    log ""
    log "=========================================="
    log "📊 发布统计"
    log "=========================================="
    log_info "✅ 成功: $SUCCESS_COUNT"
    log_skip "⏭️  跳过（已存在）: $SKIPPED_COUNT"
    log_error "❌ 失败: $FAILED_COUNT"
    log_retry "🔄 重试次数: $RETRY_COUNT"
    log ""

    if [ ${#SKIPPED_SKILLS[@]} -gt 0 ]; then
        log_skip "跳过的 Skills（已存在）:"
        for skill in "${SKIPPED_SKILLS[@]}"; do
            log "  - $skill"
        done
        log ""
    fi

    if [ ${#FAILED_SKILLS[@]} -gt 0 ]; then
        log_error "失败的 Skills:"
        for skill in "${FAILED_SKILLS[@]}"; do
            log "  - $skill"
        done
        log ""
    fi

    # 发送通知
    if [ $SUCCESS_COUNT -gt 0 ] || [ $FAILED_COUNT -gt 0 ]; then
        SUMMARY_MESSAGE="✅ **ClawdHub Skills 发布完成！**

📊 **统计**:
• 成功发布: $SUCCESS_COUNT
• 跳过（已存在）: $SKIPPED_COUNT
• 失败: $FAILED_COUNT
• 重试次数: $RETRY_COUNT

**结果**: $SUCCESS_COUNT 个新 Skills 已成功发布到 ClawdHub！

🔗 **查看 Skills**: https://www.clawhub.ai/"

        if [ $FAILED_COUNT -gt 0 ]; then
            SUMMARY_MESSAGE+=$'\n\n'⚠️ **失败的 Skills 需要手动处理**
        fi

        # 发送到 Feishu
        clawdbot message send \
            --channel feishu \
            --target ou_3bc5290afc1a94f38e23dc17c35f26d6 \
            --message "$SUMMARY_MESSAGE" >> "$LOG_FILE" 2>&1 || log_error "Feishu 通知发送失败"

        # 发送到 Slack
        clawdbot message send \
            --channel slack \
            --target D0AB0J4QLAH \
            --message "$SUMMARY_MESSAGE" >> "$LOG_FILE" 2>&1 || log_error "Slack 通知发送失败"
    else
        log_info "所有 Skills 已存在，无需发布"
    fi

    log ""
    log "=========================================="
    log "✅ 完成"
    log "=========================================="
    log ""
    log "日志文件: $LOG_FILE"
    log ""

    # 返回适当的退出码
    if [ $FAILED_COUNT -gt 0 ]; then
        exit 1
    fi
    exit 0
}

main "$@"
