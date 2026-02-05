#!/bin/bash
# 批量发布 Skills 到 ClawdHub（从源代码直接发布）

set -e

SKILLS_DIR="/root/clawd/skills"
REGISTRY_URL="https://www.clawhub.ai/api"
LOG_FILE="/root/clawd/logs/clawdhub-publish-from-source.log"
SUCCESS_COUNT=0
FAILED_COUNT=0
FAILED_SKILLS=()

# 要发布的 Skills 列表（有 package.json 的）
SKILLS=(
  "ad-creative-generator"
  "ai-music-prompts"
  "ai-video-gen"
  "brand-creative-suite"
  "clawdbot-filesystem"
  "creative-illustration"
  "feishu-bridge"
  "game-character-gen"
  "prompt-craft"
  "prompts-workflow"
  "humanizer"
  "interview-coach"
  "coding-agent"
  "prompt-optimizer"
  "prompt-rewriter"
)

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

log_skill() {
    echo -e "${BLUE}[SKILL]${NC} $1" | tee -a "$LOG_FILE"
}

get_skill_info() {
    local skill_dir="$1"
    local skill_md="$2"

    # 从 package.json 读取信息
    local pkg_info=$(cat "$skill_dir/package.json" 2>/dev/null)

    local name=$(echo "$pkg_info" | grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | cut -d'"' -f4)
    local version=$(echo "$pkg_info" | grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | cut -d'"' -f4)
    local description=$(echo "$pkg_info" | grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | cut -d'"' -f4)

    # 如果 SKILL.md 存在，补充信息
    if [ -f "$skill_md" ]; then
        local md_name=$(grep "^# " "$skill_md" 2>/dev/null | head -1 | cut -d '#' -f2 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        if [ -n "$md_name" ]; then
            name="$md_name"
        fi
    fi

    echo "$name|$version|$description"
}

main() {
    log "=========================================="
    log "📦 批量发布 Skills 到 ClawdHub（从源代码）"
    log "=========================================="
    log ""

    log_info "配置信息:"
    log "  Skills 目录: $SKILLS_DIR"
    log "  Registry: $REGISTRY_URL"
    log "  待发布 Skills: ${#SKILLS[@]} 个"
    log ""

    # 先验证 clawdhub token
    log_info "验证 ClawdHub Token..."
    if ! clawdhub whoami > /dev/null 2>&1; then
        log_warn "clawdhub whoami 返回错误（可能正常，继续测试）"
    fi

    # 测试搜索功能验证 token
    log_info "测试 Token 有效性..."
    if clawdhub search "test" > /dev/null 2>&1; then
        log_info "✓ Token 有效"
    else
        log_error "✗ Token 无效，请检查配置"
        exit 1
    fi

    log ""
    log_info "开始发布 Skills..."
    log ""

    for skill_name in "${SKILLS[@]}"; do
        skill_path="$SKILLS_DIR/$skill_name"
        skill_md="$skill_path/SKILL.md"

        if [ ! -d "$skill_path" ]; then
            log_warn "跳过: $skill_name (目录不存在)"
            continue
        fi

        if [ ! -f "$skill_path/package.json" ]; then
            log_warn "跳过: $skill_name (没有 package.json)"
            continue
        fi

        log_skill "📦 处理: $skill_name"

        # 获取 skill 信息
        local info=$(get_skill_info "$skill_path" "$skill_md")
        local display_name=$(echo "$info" | cut -d'|' -f1)
        local version=$(echo "$info" | cut -d'|' -f2)
        local description=$(echo "$info" | cut -d'|' -f3)

        if [ -z "$display_name" ]; then
            display_name="$skill_name"
        fi

        if [ -z "$version" ]; then
            version="1.0.0"
        fi

        log_info "  名称: $display_name"
        log_info "  版本: $version"

        # 发布到 ClawdHub
        cd "$skill_path"

        if clawdhub publish . \
            --registry "$REGISTRY_URL" \
            --slug "$skill_name" \
            --name "$display_name" \
            --version "$version" \
            --description "$description" \
            2>&1 | tee -a "$LOG_FILE"; then

            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            log_info "  ✓ 成功发布: $skill_name"
        else
            FAILED_COUNT=$((FAILED_COUNT + 1))
            FAILED_SKILLS+=("$skill_name")
            log_error "  ✗ 发布失败: $skill_name"
        fi

        cd - > /dev/null

        log ""
        sleep 1
    done

    log ""
    log "=========================================="
    log "📊 发布统计"
    log "=========================================="
    log_info "✅ 成功: $SUCCESS_COUNT"
    log_error "❌ 失败: $FAILED_COUNT"
    log ""

    if [ ${#FAILED_SKILLS[@]} -gt 0 ]; then
        log_error "失败的 Skills:"
        for skill in "${FAILED_SKILLS[@]}"; do
            log "  - $skill"
        done
        log ""
    fi

    if [ $SUCCESS_COUNT -gt 0 ]; then
        SUCCESS_MESSAGE="✅ **ClawdHub 批量发布完成！**

📊 **统计**:
• 成功: $SUCCESS_COUNT
• 失败: $FAILED_COUNT
• 总计: ${#SKILLS[@]}

**结果**: $SUCCESS_COUNT 个 Skills 已成功发布到 ClawdHub！

🔗 **查看 Skills**: https://www.clawhub.ai/
💡 **搜索已发布的 Skills** 可以在页面中找到"

        log_info "发送通知..."
        # 发送到 Feishu
        if command -v clawdbot &> /dev/null; then
            clawdbot message send \
                --channel feishu \
                --target ou_3bc5290afc1a94f38e23dc17c35f26d6 \
                --message "$SUCCESS_MESSAGE" >> "$LOG_FILE" 2>&1 || log_error "Feishu 通知发送失败"
        fi

        # 发送到 Slack
        if command -v clawdbot &> /dev/null; then
            clawdbot message send \
                --channel slack \
                --target D0AB0J4QLAH \
                --message "$SUCCESS_MESSAGE" >> "$LOG_FILE" 2>&1 || log_error "Slack 通知发送失败"
        fi
    else
        log_info "没有 Skills 成功发布"
    fi

    log ""
    log "=========================================="
    log "✅ 发布完成"
    log "=========================================="
    log ""
    log "日志文件: $LOG_FILE"
    log ""
}

main "$@"
