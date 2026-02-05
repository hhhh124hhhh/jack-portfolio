#!/bin/bash
# AI Research Cron - 深夜 AI 信息搜索任务
# 功能：使用 SearXNG 搜索 AI 相关信息，分析并保存到 memory/ai-research/

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
WORKSPACE="/root/clawd"
MEMORY_DIR="$WORKSPACE/memory/ai-research"
LOG_FILE="$MEMORY_DIR/research.log"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
DATE=$(date +%Y-%m-%d)

# 创建目录
mkdir -p "$MEMORY_DIR"

# 函数：输出带时间戳的日志
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

# 函数：使用 SearXNG 搜索
search_searxng() {
    local query="$1"
    local output_file="$2"
    local category="${3:-search}"

    log "INFO" "搜索: $query"

    # 使用 searXNG 搜索
    if command -v searxng &> /dev/null; then
        searxng --format json --category "$category" "$query" 2>/dev/null | tee "$output_file"
    else
        # 使用 SearXNG API
        curl -s "http://localhost:8080/search?format=json&q=$(echo "$query" | sed 's/ /%20/g')&category=$category" -o "$output_file"
    fi

    log "INFO" "结果已保存到: $output_file"
}

# 函数：分析搜索结果
analyze_results() {
    local input_file="$1"
    local output_file="$2"
    local topic="$3"

    log "INFO" "分析结果: $topic"

    # 简单统计
    local count=$(cat "$input_file" | jq '.results | length' 2>/dev/null || echo "0")

    # 提取标题和 URL
    cat "$input_file" | jq -r '.results[] | "- \(.title): \(.url)"' 2>/dev/null > "$output_file" || echo "解析失败" > "$output_file"

    log "INFO" "找到 $count 个结果，已保存到: $output_file"
}

# 主流程
main() {
    log "INFO" "========================================"
    log "INFO" "🔍 AI Research Cron 启动"
    log "INFO" "========================================"
    log "INFO" "开始时间: $(date)"
    log "INFO" "模式: 深夜 AI 研究搜索"

    # 搜索主题列表
    declare -A topics=(
        ["AI news"]="AI news 2026 artificial intelligence latest"
        ["AI tools"]="AI tools 2026 best new software"
        ["AI agents"]="AI agents 2026 autonomous workflow"
        ["AI prompt engineering"]="AI prompt engineering 2026 techniques"
        ["Claude AI"]="Claude AI 2026 Anthropic features"
        ["OpenAI"]="OpenAI 2026 GPT updates"
        ["multimodal AI"]="multimodal AI 2026 vision audio"
        ["AI coding"]="AI coding 2026 programming assistants"
    )

    # 对每个主题进行搜索
    for topic_name in "${!topics[@]}"; do
        local query="${topics[$topic_name]}"
        local json_file="$MEMORY_DIR/${topic_name// /_}_$TIMESTAMP.json"
        local md_file="$MEMORY_DIR/${topic_name// /_}_$TIMESTAMP.md"

        log "INFO" "----------------------------------------"
        log "INFO" "主题: $topic_name"

        # 搜索
        search_searxng "$query" "$json_file" "search"

        # 分析
        analyze_results "$json_file" "$md_file" "$topic_name"
    done

    # 生成汇总报告
    local report_file="$MEMORY_DIR/research_summary_$DATE.md"
    log "INFO" "生成汇总报告: $report_file"

    cat > "$report_file" << EOF
# AI Research Summary - $DATE

生成时间: $(date '+%Y-%m-%d %H:%M:%S')
搜索来源: SearXNG (localhost:8080)

## 搜索主题

EOF

    for topic_name in "${!topics[@]}"; do
        local md_file="$MEMORY_DIR/${topic_name// /_}_$TIMESTAMP.md"
        local count=$(cat "$json_file" 2>/dev/null | jq '.results | length' 2>/dev/null || echo "0")

        echo "### $topic_name" >> "$report_file"
        echo "" >> "$report_file"
        echo "**找到结果数:** $count" >> "$report_file"
        echo "" >> "$report_file"

        if [ -f "$md_file" ]; then
            cat "$md_file" >> "$report_file"
            echo "" >> "$report_file"
        fi
    done

    log "INFO" "========================================"
    log "INFO" "✅ AI Research Cron 完成"
    log "INFO" "========================================"
    log "INFO" "完成时间: $(date)"
    log "INFO" "汇总报告: $report_file"
    log "INFO" "详细日志: $LOG_FILE"

    # 返回成功
    return 0
}

# 执行主流程
main
exit_code=$?

exit $exit_code
