#!/bin/bash

# AI 信息搜索脚本 - 简化版
# 无需子代理，直接搜索、分析、生成报告

set -e

# 配置
SEARXNG_URL="${SEARXNG_URL:-http://localhost:8080}"
SEARCH_TERMS=("AI prompt engineering" "Claude AI tips" "ChatGPT automation" "Moltbot best practices" "AI skills development")
OUTPUT_DIR="/root/clawd/memory/ai-research"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$OUTPUT_DIR/report-${DATE}.json"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo "[$(date)] AI 信息搜索开始" | tee -a "$OUTPUT_DIR/search.log"
echo "搜索术语: ${SEARCH_TERMS[*]}" | tee -a "$OUTPUT_DIR/search.log"

# 初始化报告
cat > "$REPORT_FILE" << EOF
{
  "date": "$DATE",
  "timestamp": "$TIMESTAMP",
  "search_terms": ${SEARCH_TERMS[@]},
  "results": []
}
EOF

# 搜索每个术语
total_results=0
for term in "${SEARCH_TERMS[@]}"; do
    echo "[$(date)] 搜索: $term" | tee -a "$OUTPUT_DIR/search.log"

    # 使用 SearXNG 搜索
    results=$(curl -s -G "$SEARXNG_URL/search" \
        --data-urlencode "q=$term" \
        --data-urlencode "format=json" \
        --data-urlencode "engines=google,bing,duckduckgo" \
        --data-urlencode "language=auto" \
        --data-urlencode "time_range=week" 2>&1 || echo "[]")

    # 保存原始结果
    echo "$results" > "$OUTPUT_DIR/raw_${TIMESTAMP}_$(echo $term | tr ' ' '_).json"

    # 提取结果数量和前 5 条
    result_count=$(echo "$results" | jq -r '(.results | length) // 0' 2>/dev/null || echo "0")
    total_results=$((total_results + result_count))

    # 提取前 5 个结果
    top_5=$(echo "$results" | jq -r '.results[:5] | map({
        title: .title,
        url: .url,
        content: (.content[:200] // ""),
        engine: .engine,
        score: (.score // 0)
    })' 2>/dev/null || echo "[]")

    # 添加到报告
    echo "$results" | jq -r --arg term "$term" --argjson top5 "$top_5" '{
        term: $term,
        result_count: (.results | length // 0),
        top_results: $top5
    }' 2>/dev/null >> /tmp/temp_results.json

    sleep 1
done

# 合并结果到报告
echo "[" > /tmp/all_results.json
first=true
for term in "${SEARCH_TERMS[@]}"; do
    if [ "$first" = true ]; then
        first=false
    else
        echo "," >> /tmp/all_results.json
    fi
    echo "$results" | jq -r '.results[:5] | map({
        term: "'$term'",
        title: .title,
        url: .url,
        snippet: (.content[:200] // ""),
        engine: .engine
    })' 2>/dev/null >> /tmp/all_results.json
done
echo "]" >> /tmp/all_results.json

# 生成最终报告
cat > "$REPORT_FILE" << EOF
{
  "date": "$DATE",
  "timestamp": "$TIMESTAMP",
  "total_results": $total_results,
  "search_terms": [$(for t in "${SEARCH_TERMS[@]}"; do echo "\"$t\""; done | paste -sd ',')],
  "summary": {
    "searched_terms": ${#SEARCH_TERMS[@]},
    "total_results": $total_results,
    "avg_results_per_term": $((total_results / ${#SEARCH_TERMS[@]}))
  },
  "top_results": $(cat /tmp/all_results.json),
  "generated_at": "$(date -Iseconds)"
}
EOF

# 清理临时文件
rm -f /tmp/temp_results.json /tmp/all_results.json

echo "" | tee -a "$OUTPUT_DIR/search.log"
echo "[$(date)] 搜索完成" | tee -a "$OUTPUT_DIR/search.log"
echo "总结果数: $total_results" | tee -a "$OUTPUT_DIR/search.log"
echo "报告文件: $REPORT_FILE" | tee -a "$OUTPUT_DIR/search.log"

# 显示 Top 10 结果
echo "" | tee -a "$OUTPUT_DIR/search.log"
echo "=== Top 10 结果 ===" | tee -a "$OUTPUT_DIR/search.log"
echo "$results" | jq -r '.results[:10] | to_entries[] | "  \(.key + 1). \(.value.title[:80])"' 2>/dev/null | head -10 | tee -a "$OUTPUT_DIR/search.log"

exit 0
