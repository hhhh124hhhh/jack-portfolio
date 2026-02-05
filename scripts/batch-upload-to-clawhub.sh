#!/bin/bash
# 批量上传 Skills 到 ClawdHub（使用正确的 registry）

set -e

SKILLS_DIR="/root/clawd/dist/skills"
REGISTRY_URL="https://www.clawhub.ai/api"
LOG_FILE="/root/clawd/logs/clawdhub-batch-upload.log"
SUCCESS_COUNT=0
FAILED_COUNT=0
FAILED_SKILLS=()

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

# 主函数
main() {
    log "=========================================="
    log "📦 批量上传 Skills 到 ClawdHub"
    log "=========================================="
    log ""
    
    log_info "配置信息:"
    log "  Skills 目录: $SKILLS_DIR"
    log "  Registry: $REGISTRY_URL"
    log ""
    
    # 检查目录
    if [ ! -d "$SKILLS_DIR" ]; then
        log_error "Skills 目录不存在: $SKILLS_DIR"
        exit 1
    fi
    
    # 统计
    TOTAL_SKILLS=$(find "$SKILLS_DIR" -name "*.skill" -type f | wc -l)
    log_info "找到 $TOTAL_SKILLS 个 .skill 文件"
    log ""
    
    # 解压并上传每个 skill
    for skill_file in "$SKILLS_DIR"/*.skill; do
        if [ ! -f "$skill_file" ]; then
            continue
        fi
        
        skill_name=$(basename "$skill_file" .skill)
        temp_dir="/tmp/skill-upload-$$-$skill_name"
        
        log_info "📦 处理: $skill_name"
        
        # 创建临时目录
        mkdir -p "$temp_dir"
        
        # 解压
        cd "$temp_dir"
        if ! unzip -q "$skill_file"; then
            log_error "解压失败: $skill_file"
            rm -rf "$temp_dir"
            continue
        fi
        
        # 查找 SKILL.md（可能在子目录中）
        SKILL_MD_PATH=""
        if [ -f "SKILL.md" ]; then
            SKILL_MD_PATH="$temp_dir/SKILL.md"
        else
            # 查找子目录中的 SKILL.md
            for dir in */; do
                if [ -f "$dir/SKILL.md" ]; then
                    SKILL_MD_PATH="$temp_dir/$dir/SKILL.md"
                    break
                fi
            done
        fi
        
        if [ ! -f "$SKILL_MD_PATH" ]; then
            log_warn "SKILL.md 不存在，跳过"
            rm -rf "$temp_dir"
            continue
        fi
        
        # 读取 name（从 SKILL.md）
        name=$(grep "^# " "$SKILL_MD_PATH" 2>/dev/null | head -1 | cut -d '#' -f2 | xargs)
        if [ -z "$name" ]; then
            name="$skill_name"
        fi
        
        # 读取 name
        name=$(grep "^# " SKILL.md 2>/dev/null | head -1 | cut -d '#' -f2 | xargs)
        if [ -z "$name" ]; then
            name="$skill_name"
        fi
        
        # 上传
        log_info "  上传: $name ($skill_name)"
        
        if clawdhub publish \
            --registry "$REGISTRY_URL" \
            --slug "$skill_name" \
            --name "$name" \
            --version "1.0.0" \
            --changelog "批量上传 - 生图/生视频/AI 编码相关 Prompts" 2>&1 | tee -a "$LOG_FILE"; then
            
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            log_info "  ✓ 成功发布: $skill_name"
        else
            FAILED_COUNT=$((FAILED_COUNT + 1))
            FAILED_SKILLS+=("$skill_name")
            log_error "  ✗ 发布失败: $skill_name"
        fi
        
        # 清理
        cd - > /dev/null
        rm -rf "$temp_dir"
    done
    
    # 输出统计
    log ""
    log "=========================================="
    log "📊 上传统计"
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
        
        # Feishu/Slack 通知（失败通知）
        FAIL_MESSAGE="❌ **ClawdHub 批量上传完成**

📊 **统计**:
• 成功: $SUCCESS_COUNT
• 失败: $FAILED_COUNT

**失败的 Skills**:
${FAILED_SKILLS[@]}"
        
        # 发送 Feishu
        clawdbot message send --channel feishu --target ou_3bc5290afc1a94f38e23dc17c35f26d6 --message "$FAIL_MESSAGE" > /dev/null 2>&1
        
        # 发送 Slack
        clawdbot message send --channel slack --target D0AB0J4QLAH --message "$FAIL_MESSAGE" > /dev/null 2>&1
    else
        log_info "所有 Skills 上传成功！"
        log ""
        
        # 生成成功报告
        SUCCESS_MESSAGE="✅ **ClawdHub 批量上传完成！**

📊 **统计**:
• 成功: $SUCCESS_COUNT
• 失败: 0

**结果**: 所有 Skills 已成功发布到 ClawdHub！

🔗 **查看 Skills**: https://www.clawhub.ai/ 搜索已上传的 Skills"
        
        # 发送 Feishu
        clawdbot message send --channel feishu --target ou_3bc5290afc1a94f38e23dc17c35f26d6 --message "$SUCCESS_MESSAGE" > /dev/null 2>&1
        
        # 发送 Slack
        clawdbot message send --channel slack --target D0AB0J4QLAH --message "$SUCCESS_MESSAGE" > /dev/null 2>&1
    fi
    
    log ""
    log "=========================================="
    log "✅ 批量上传完成"
    log "=========================================="
    log ""
    log "日志文件: $LOG_FILE"
    log ""
}

# 运行主函数
main "$@"
