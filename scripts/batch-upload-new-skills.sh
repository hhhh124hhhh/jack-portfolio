#!/bin/bash
# 批量上传**新的** Skills 到 ClawdHub（跳过已发布的）

SKILLS_DIR="/root/clawd/dist/skills"
REGISTRY_URL="https://www.clawhub.ai/api"
LOG_FILE="/root/clawd/logs/clawdhub-upload-new-skills.log"
SUCCESS_COUNT=0
FAILED_COUNT=0
SKIPPED_COUNT=0
FAILED_SKILLS=()
SKIPPED_SKILLS=()

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

log_skip() {
    echo -e "${BLUE}[SKIP]${NC} $1" | tee -a "$LOG_FILE"
}

find_skill_md() {
    local dir="$1"
    local skill_md=""
    
    if [ -f "$dir/SKILL.md" ]; then
        skill_md="$dir/SKILL.md"
    else
        for subdir in "$dir"/*/; do
            if [ -d "$subdir" ] && [ -f "$subdir/SKILL.md" ]; then
                skill_md="$subdir/SKILL.md"
                break
            fi
        done
    fi
    
    echo "$skill_md"
}

main() {
    log "=========================================="
    log "📦 批量上传**新的** Skills 到 ClawdHub"
    log "=========================================="
    log ""
    
    log_info "配置信息:"
    log "  Skills 目录: $SKILLS_DIR"
    log "  Registry: $REGISTRY_URL"
    log "  模式: 仅上传新 Skills（跳过已发布的）"
    log ""
    
    if [ ! -d "$SKILLS_DIR" ]; then
        log_error "Skills 目录不存在: $SKILLS_DIR"
        exit 1
    fi
    
    TOTAL_SKILLS=$(find "$SKILLS_DIR" -name "*.skill" -type f 2>/dev/null | wc -l)
    
    log_info "找到 $TOTAL_SKILLS 个 .skill 文件"
    log ""
    
    if [ $TOTAL_SKILLS -eq 0 ]; then
        log_warn "没有 .skill 文件需要上传"
        exit 0
    fi
    
    for skill_file in "$SKILLS_DIR"/*.skill; do
        if [ ! -f "$skill_file" ]; then
            continue
        fi
        
        skill_name=$(basename "$skill_file" .skill)
        temp_dir="/tmp/skill-upload-$$-$skill_name"
        tmp_output="/tmp/publish-output-$$-$skill_name.txt"
        
        log_info "📦 处理: $skill_name"
        
        mkdir -p "$temp_dir"
        cd "$temp_dir"
        
        if ! unzip -q "$skill_file"; then
            log_error "解压失败: $skill_file"
            cd - > /dev/null
            rm -rf "$temp_dir"
            FAILED_COUNT=$((FAILED_COUNT + 1))
            FAILED_SKILLS+=("$skill_name: 解压失败")
            continue
        fi
        
        skill_md_path=$(find_skill_md ".")
        
        if [ ! -f "$skill_md_path" ]; then
            log_warn "SKILL.md 不存在: $skill_name"
            cd - > /dev/null
            rm -rf "$temp_dir"
            continue
        fi
        
        display_name=$(grep "^# " "$skill_md_path" 2>/dev/null | head -1 | cut -d '#' -f2 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        if [ -z "$display_name" ]; then
            display_name="$skill_name"
        fi
        
        # 切换到 SKILL.md 所在的目录
        cd "$(dirname "$skill_md_path")"
        
        # 保存原始工作目录（当前已经是 skill 目录）
        ORIG_DIR=$(pwd)
        
        # 将输出保存到临时文件
        clawdhub publish . \
            --registry "$REGISTRY_URL" \
            --slug "$skill_name" \
            --name "$display_name" \
            --version "1.0.0" \
            --changelog "AI Prompts 转换 - 生图/生视频/AI 编码相关" > "$tmp_output" 2>&1
        
        # 输出结果到日志
        cat "$tmp_output" | tee -a "$LOG_FILE"
        
        # 检查是否是"Version already exists"错误
        if grep -q "Version already exists" "$tmp_output"; then
            log_skip "⏭️  已存在，跳过: $skill_name"
            SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
            SKIPPED_SKILLS+=("$skill_name")
        elif grep -q "Published successfully\|✔ OK. Published" "$tmp_output"; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            log_info "✓ 成功发布: $skill_name"
        else
            FAILED_COUNT=$((FAILED_COUNT + 1))
            FAILED_SKILLS+=("$skill_name")
            log_error "✗ 发布失败: $skill_name"
        fi
        
        rm -f "$tmp_output"
        cd - > /dev/null
        rm -rf "$temp_dir"
        
        sleep 1
    done
    
    log ""
    log "=========================================="
    log "📊 上传统计"
    log "=========================================="
    log_info "✅ 成功: $SUCCESS_COUNT"
    log_skip "⏭️  跳过（已存在）: $SKIPPED_COUNT"
    log_error "❌ 失败: $FAILED_COUNT"
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
    
    if [ $SUCCESS_COUNT -gt 0 ]; then
        SUCCESS_MESSAGE="✅ **ClawdHub 新 Skills 上传完成！**

📊 **统计**:
• 新发布: $SUCCESS_COUNT
• 跳过（已存在）: $SKIPPED_COUNT
• 失败: $FAILED_COUNT

**结果**: $SUCCESS_COUNT 个新 Skills 已成功发布到 ClawdHub！

🔗 **查看 Skills**: https://www.clawhub.ai/ 搜索你上传的 Skills"
        
        clawdbot message send \
            --channel feishu \
            --target ou_3bc5290afc1a94f38e23dc17c35f26d6 \
            --message "$SUCCESS_MESSAGE" >> "$LOG_FILE" 2>&1 || log_error "Feishu 通知发送失败"
        
        clawdbot message send \
            --channel slack \
            --target D0AB0J4QLAH \
            --message "$SUCCESS_MESSAGE" >> "$LOG_FILE" 2>&1 || log_error "Slack 通知发送失败"
    else
        log_info "没有新 Skills 需要上传"
    fi
    
    log ""
    log "=========================================="
    log "✅ 完成"
    log "=========================================="
    log ""
    log "日志文件: $LOG_FILE"
    log ""
}

main "$@"
