#!/bin/bash
# AI Prompts Collector - Shell Version
# 定期收集 AI 提示词相关信息

DATA_DIR="/root/clawd/data/prompts"
COLLECTED_FILE="$DATA_DIR/collected.jsonl"
DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 创建目录
mkdir -p "$DATA_DIR"

echo "🚀 Starting AI Prompts Collection..."
echo "📅 Date: $DATE"

# 搜索查询列表
queries=(
  "AI prompt engineering tips"
  "ChatGPT prompts"
  "Claude prompts"
  "best AI prompts 2026"
  "prompt templates"
)

# 构建搜索结果数组
results='{"type":"search","date":"'"$DATE"'","queries":['

first=true
for query in "${queries[@]}"; do
  echo "🔍 Searching: $query"

  # 使用 web_search
  if [ "$first" = true ]; then
    first=false
  else
    results="$results,"
  fi

  # 调用 clawdbot 的 web_search
  search_result=$(clawdbot eval 'await tool("web_search", { query: "'"$query"'", count: 5 })' 2>/dev/null)

  # 提取搜索结果数量
  if echo "$search_result" | grep -q '"results"'; then
    count=$(echo "$search_result" | grep -o '"results"' | wc -l)
  else
    count=0
  fi

  results="$results{\"query\":\"$query\",\"count\":$count,\"raw\":$search_result}"
done

results="$results]}"

# 保存到文件
echo "$results" >> "$COLLECTED_FILE"

echo "✅ Saved results to $COLLECTED_FILE"
echo "✨ Collection complete!"
