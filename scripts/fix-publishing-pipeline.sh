#!/bin/bash
# 修复发布流程 - 将生成的 skills 打包并发布

set -e

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
    log "🔧 修复发布流程"
    log "=========================================="

    # 步骤 1: 创建输出目录
    mkdir -p "$OUTPUT_DIR"
    log_info "✅ 输出目录已准备: $OUTPUT_DIR"

    # 步骤 2: 统计待打包的 skills
    SKILL_COUNT=$(find "$SOURCE_DIR" -maxdepth 1 -type d ! -name "$SOURCE_DIR" | wc -l)
    log_info "📦 发现 $SKILL_COUNT 个待打包的 skills"

    # 步骤 3: 打包 skills
    log ""
    log "[步骤 1/3] 打包 Skills"
    SUCCESS_PACKED=0
    FAILED_PACKED=0

    for skill_dir in "$SOURCE_DIR"/*; do
        # 跳过文件
        if [[ ! -d "$skill_dir" ]]; then
            continue
        fi

        skill_name=$(basename "$skill_dir")
        output_file="$OUTPUT_DIR/${skill_name}.skill"

        # 检查 SKILL.md 是否存在
        if [[ ! -f "$skill_dir/SKILL.md" ]]; then
            log_warn "⚠️  跳过 $skill_name (缺少 SKILL.md)"
            ((FAILED_PACKED++))
            continue
        fi

        # 打包成 zip 文件
        cd "$SOURCE_DIR"
        if zip -q -r "$output_file" "$skill_name" 2>/dev/null; then
            log_info "✅ 已打包: ${skill_name}.skill ($(du -h "$output_file" | cut -f1))"
            ((SUCCESS_PACKED++))
        else
            log_error "❌ 打包失败: $skill_name"
            ((FAILED_PACKED++))
        fi
    done

    log_info "📊 打包完成: $SUCCESS_PACKED 成功, $FAILED_PACKED 失败"

    # 步骤 4: 发布到 ClawdHub
    log ""
    log "[步骤 2/3] 发布到 ClawdHub"

    if bash /root/clawd/scripts/auto-publish-skills.sh >> "$LOG_FILE" 2>&1; then
        log_info "✅ 发布流程执行完成"
    else
        log_error "❌ 发布流程执行失败"
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

    # 清理旧的 .skill 文件（可选）
    log_warn "提示: 可以删除 $OUTPUT_DIR 中旧的 .skill 文件"
    log "命令: find $OUTPUT_DIR -name '*.skill' -mtime +7 -delete"

    log ""
    log_info "✅ 修复流程完成！"
    log_info "📝 日志: $LOG_FILE"
}

main "$@"
