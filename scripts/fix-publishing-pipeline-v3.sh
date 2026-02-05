#!/bin/bash
# 修复发布流程 - 将生成的 skills 打包并发布
# V3: 修复打包问题，确保 SKILL.md 在顶层

# 配置
SOURCE_DIR="/root/clawd/generated-skills"
OUTPUT_DIR="/root/clawd/dist"
LOG_FILE="/root/clawd/logs/fix-publishing-$(date +%Y%m%d-%H%M%S).log"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

main() {
    log "=========================================="
    log "🔧 修复发布流程 V3"
    log "=========================================="

    # 步骤 1: 创建输出目录
    mkdir -p "$OUTPUT_DIR"
    log_info "✅ 输出目录已准备: $OUTPUT_DIR"

    # 步骤 2: 统计待打包的 skills
    SKILL_COUNT=$(find "$SOURCE_DIR" -maxdepth 1 -type d ! -name "$SOURCE_DIR" ! -name "." | wc -l)
    log_info "📦 发现 $SKILL_COUNT 个待打包的 skills"

    # 保存当前目录
    ORIGINAL_DIR=$(pwd)

    # 步骤 3: 打包 skills
    log ""
    log "[步骤 1/3] 打包 Skills (修复版 - SKILL.md 在顶层)"
    SUCCESS_PACKED=0
    FAILED_PACKED=0

    cd "$SOURCE_DIR" || { log_error "无法进入目录: $SOURCE_DIR"; exit 1; }

    for skill_dir in */; do
        # 跳过空行
        [[ -z "$skill_dir" ]] && continue

        # 移除末尾的斜杠
        skill_name=${skill_dir%/}

        output_file="$OUTPUT_DIR/${skill_name}.skill"
        temp_dir="/tmp/skill-package-$$-${skill_name}"

        # 检查 SKILL.md 是否存在
        if [[ ! -f "${skill_dir}SKILL.md" ]]; then
            log_warn "⚠️  跳过 $skill_name (缺少 SKILL.md)"
            FAILED_PACKED=$((FAILED_PACKED + 1))
            continue
        fi

        # 创建临时目录
        mkdir -p "$temp_dir"

        # 复制所有文件到临时目录（去掉 skill_name 前缀）
        cp -r "${skill_dir}"* "$temp_dir/" 2>> "$LOG_FILE"

        # 打包成 zip 文件（从临时目录）
        cd "$temp_dir" || { log_error "无法进入临时目录"; continue; }
        if zip -q -r "$output_file" . 2>> "$LOG_FILE"; then
            file_size=$(du -h "$output_file" | cut -f1)
            log_info "✅ 已打包: ${skill_name}.skill ($file_size)"
            SUCCESS_PACKED=$((SUCCESS_PACKED + 1))
        else
            log_error "❌ 打包失败: $skill_name"
            FAILED_PACKED=$((FAILED_PACKED + 1))
        fi

        # 清理临时目录
        cd "$SOURCE_DIR" || true
        rm -rf "$temp_dir"
    done

    # 返回原始目录
    cd "$ORIGINAL_DIR" || true

    log_info "📊 打包完成: $SUCCESS_PACKED 成功, $FAILED_PACKED 失败"

    # 步骤 4: 发布到 ClawdHub
    log ""
    log "[步骤 2/3] 发布到 ClawdHub"

    if bash /root/clawd/scripts/auto-publish-skills.sh >> "$LOG_FILE" 2>&1; then
        log_info "✅ 发布流程执行完成"
    else
        log_error "⚠️  发布流程执行失败（查看日志获取详情）"
    fi

    # 步骤 5: 统计发布结果
    log ""
    log "[步骤 3/3] 统计发布结果"

    PUBLISHED_COUNT=$(grep -c "✅ Successfully published:" "$LOG_FILE" 2>/dev/null || echo "0")
    FAILED_COUNT=$(grep -c "❌ Failed to publish:" "$LOG_FILE" 2>/dev/null || echo "0")
    SKIPPED_COUNT=$(grep -c "⏭️" "$LOG_FILE" 2>/dev/null || echo "0")

    log_info "📊 发布统计:"
    log_info "  - 成功: $PUBLISHED_COUNT"
    log_info "  - 失败: $FAILED_COUNT"
    log_info "  - 已存在: $SKIPPED_COUNT"

    # 步骤 6: 生成报告
    log ""
    log "=========================================="
    log "📋 修复报告"
    log "=========================================="
    log "打包统计:"
    log "  - 成功: $SUCCESS_PACKED"
    log "  - 失败: $FAILED_PACKED"
    log "发布统计:"
    log "  - 成功: $PUBLISHED_COUNT"
    log "  - 失败: $FAILED_COUNT"
    log "  - 已存在: $SKIPPED_COUNT"
    log "=========================================="

    log ""
    log_info "✅ 修复流程完成！"
    log_info "📝 日志: $LOG_FILE"
}

main "$@"
