#!/bin/bash
# 批量处理所有 .skill 文件（包括根目录和 dist/ 目录）

set -e

# 搜索目录列表
SEARCH_DIRS=(
    "/root/clawd"
    "/root/clawd/dist"
    "/root/clawd/generated-skills"
    "/root/clawd/dist/skills"
)

LOG_DIR="/root/clawd/logs"
LOG_FILE="$LOG_DIR/batch-process-all-skills-$(date +%Y%m%d-%H%M%S).log"
OUTPUT_DIR="/root/clawd/processed-skills"

# 统计
TOTAL_SKILLS=0
PROCESSED=0
SKIPPED=0
FAILED=0

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 创建日志目录
mkdir -p "$LOG_DIR"
mkdir -p "$OUTPUT_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 查找所有 .skill 文件
find_all_skills() {
    local skills=()

    for dir in "${SEARCH_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            while IFS= read -r -d '' skill_file; do
                skills+=("$skill_file")
            done < <(find "$dir" -name "*.skill" -type f -print0)
        fi
    done

    # 去重
    printf '%s\n' "${skills[@]}" | sort -u
}

# 提取并解析 skill 信息
process_skill() {
    local skill_file=$1
    local skill_name=$(basename "$skill_file" .skill)
    local temp_dir="/tmp/skill-process-$$-$skill_name"
    local output_json="$OUTPUT_DIR/${skill_name}.json"

    log "📦 处理: $skill_name"

    # 创建临时目录
    mkdir -p "$temp_dir"
    cd "$temp_dir"

    # 解压 skill 文件
    if ! unzip -q "$skill_file"; then
        log "  ⚠️  解压失败: $skill_file"
        cd - > /dev/null
        rm -rf "$temp_dir"
        return 1
    fi

    # 查找 SKILL.md
    local skill_md=""
    if [ -f "SKILL.md" ]; then
        skill_md="SKILL.md"
    else
        skill_md=$(find . -name "SKILL.md" -type f | head -1)
    fi

    if [ ! -f "$skill_md" ]; then
        log "  ⚠️  SKILL.md 不存在: $skill_name"
        cd - > /dev/null
        rm -rf "$temp_dir"
        return 1
    fi

    # 提取 frontmatter
    local frontmatter=$(sed -n '/^---$/,/^---$/p' "$skill_md" | head -n -1 | tail -n +2)

    # 解析信息
    local name=$(echo "$frontmatter" | grep '^name:' | sed 's/name: *//')
    local description=$(echo "$frontmatter" | grep '^description:' | sed 's/description: *//')
    local category=$(echo "$frontmatter" | grep '^category:' | sed 's/category: *//')
    local tags=$(echo "$frontmatter" | grep '^tags:' | sed 's/tags: *//')

    if [ -z "$name" ]; then
        name=$(grep "^# " "$skill_md" | head -1 | cut -d '#' -f2 | xargs)
    fi

    if [ -z "$name" ]; then
        name="$skill_name"
    fi

    if [ -z "$description" ]; then
        description=$(sed -n '/## 描述/,/^##/p' "$skill_md" | head -n -1 | tail -n +2 | xargs)
    fi

    if [ -z "$description" ]; then
        description="No description provided"
    fi

    # 生成 JSON 输出
    cat > "$output_json" << EOF
{
  "file": "$skill_file",
  "name": "$name",
  "skill_name": "$skill_name",
  "description": "$description",
  "category": "${category:-uncategorized}",
  "tags": "${tags:-}",
  "size_bytes": $(stat -f%z "$skill_file" 2>/dev/null || stat -c%s "$skill_file" 2>/dev/null),
  "modified": $(stat -f%m "$skill_file" 2>/dev/null || stat -c%Y "$skill_file" 2>/dev/null),
  "md5": $(md5sum "$skill_file" | cut -d' ' -f1)
}
EOF

    log "  ✓ 解析成功: $name"
    cd - > /dev/null
    rm -rf "$temp_dir"

    return 0
}

# 生成汇总报告
generate_report() {
    local report_file="$OUTPUT_DIR/report-$(date +%Y%m%d-%H%M%S).json"

    cat > "$report_file" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "summary": {
    "total": $TOTAL_SKILLS,
    "processed": $PROCESSED,
    "skipped": $SKIPPED,
    "failed": $FAILED
  },
  "stats": {
    "total_size_bytes": $(du -sb "$OUTPUT_DIR" | cut -f1),
    "unique_skills": $(find "$OUTPUT_DIR" -name "*.json" -type f | wc -l)
  }
}
EOF

    log ""
    log "📊 报告已生成: $report_file"
}

main() {
    log "========================================"
    log "🚀 批量处理所有 .skill 文件"
    log "========================================"
    log ""

    # 查找所有 skill 文件
    print_status "$BLUE" "🔍 搜索 .skill 文件..."
    local skills=()
    while IFS= read -r skill_file; do
        skills+=("$skill_file")
    done < <(find_all_skills)

    TOTAL_SKILLS=${#skills[@]}

    print_status "$GREEN" "✓ 找到 $TOTAL_SKILLS 个 .skill 文件"
    log ""

    if [ $TOTAL_SKILLS -eq 0 ]; then
        print_status "$YELLOW" "没有找到 .skill 文件"
        exit 0
    fi

    # 处理每个 skill
    print_status "$BLUE" "⚙️  开始处理..."
    log ""

    for skill_file in "${skills[@]}"; do
        if process_skill "$skill_file"; then
            PROCESSED=$((PROCESSED + 1))
        else
            FAILED=$((FAILED + 1))
        fi

        # 避免过快处理
        sleep 0.1
    done

    log ""
    log "========================================"
    log "📊 处理结果"
    log "========================================"
    print_status "$GREEN" "✅ 成功: $PROCESSED"
    print_status "$YELLOW" "⚠️  跳过: $SKIPPED"
    print_status "$RED" "❌ 失败: $FAILED"
    print_status "$BLUE" "📦 总计: $TOTAL_SKILLS"
    log ""

    # 生成报告
    generate_report

    log ""
    log "📁 输出目录: $OUTPUT_DIR"
    log "📝 日志文件: $LOG_FILE"
    log ""
    log "✅ 处理完成！"
}

main "$@"
