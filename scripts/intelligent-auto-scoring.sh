#!/bin/bash

# 智能自动化评分系统
# 不仅自动评分，还能在评分过低时优化搜索策略

set -e

SCRIPT_DIR="/root/clawd/scripts"
REPORT_DIR="/root/clawd/reports/auto-scoring"
TWEET_SCRIPT="$SCRIPT_DIR/auto_twitter_search.sh"

echo "========================================"
echo "🤖 智能自动化评分系统"
echo "========================================"
echo ""

# 1. 运行自动化评分系统
echo "📊 步骤 1/3: 运行自动化评分..."
cd /root/clawd
SUMMARY=$(node "$SCRIPT_DIR/auto-scoring-system.js" | grep -A 50 "🎯 全自动化评分系统报告")
echo "✅ 评分完成"
echo ""

# 2. 提取关键指标
echo "📈 步骤 2/3: 分析评分结果..."

# 读取最新的权重历史记录
HISTORY_FILE="/root/clawd/reports/auto-scoring/history/weight-history.jsonl"
if [ -f "$HISTORY_FILE" ]; then
    LATEST_RECORD=$(tail -1 "$HISTORY_FILE")
    AVG_SCORE=$(echo "$LATEST_RECORD" | jq -r '.analysis.averageScore')
    HIGH_QUALITY_PERCENT=$(echo "$LATEST_RECORD" | jq -r '.analysis.highQualityPercent')
    ADJUSTED=$(echo "$LATEST_RECORD" | jq -r '.decision.adjusted')
    
    echo "   平均评分: $AVG_SCORE"
    echo "   高质量占比: $HIGH_QUALITY_PERCENT%"
    echo "   权重已调整: $ADJUSTED"
else
    echo "⚠️  未找到权重历史记录"
    exit 0
fi
echo ""

# 3. 智能决策
echo "🧠 步骤 3/3: 智能决策..."

# 定义阈值
MIN_AVG_SCORE=50  # 最低平均分
MIN_HIGH_QUALITY=5  # 最低高质量占比 %

NEED_SEARCH_OPTIMIZATION=false
REASONS=()

# 检查是否需要优化搜索策略
if (( $(echo "$AVG_SCORE < $MIN_AVG_SCORE" | bc -l) )); then
    NEED_SEARCH_OPTIMIZATION=true
    REASONS+=("平均分过低 ($AVG_SCORE < $MIN_AVG_SCORE)")
fi

if (( $(echo "$HIGH_QUALITY_PERCENT < $MIN_HIGH_QUALITY" | bc -l) )); then
    NEED_SEARCH_OPTIMIZATION=true
    REASONS+=("高质量占比过低 ($HIGH_QUALITY_PERCENT% < $MIN_HIGH_QUALITY%)")
fi

echo ""
echo "📊 分析结果:"
echo "   平均评分: $AVG_SCORE"
echo "   高质量占比: $HIGH_QUALITY_PERCENT%"
echo ""

if [ "$NEED_SEARCH_OPTIMIZATION" = true ]; then
    echo "⚠️  检测到评分过低，需要优化搜索策略"
    echo "   原因: ${REASONS[*]}"
    echo ""
    
    # 检查当前搜索配置
    echo "🔍 当前搜索配置:"
    if [ -f "$TWEET_SCRIPT" ]; then
        echo "   脚本路径: $TWEET_SCRIPT"
        
        # 提取当前搜索查询
        QUERIES=$(grep -A 5 "搜索关键词" "$TWEET_SCRIPT" | head -10 || echo "未找到查询配置")
        echo "   当前查询:"
        echo "$QUERIES" | sed 's/^/     /'
    else
        echo "   ⚠️  未找到搜索脚本"
    fi
    
    echo ""
    echo "💡 优化建议:"
    echo "   1. 使用更精确的搜索查询:"
    echo "      - 添加 'template', 'framework', 'guide' 关键词"
    echo "      - 添加 'step by step', 'tutorial' 等教学词汇"
    echo "   2. 过滤新闻类内容:"
    echo "      - 排除 'announcing', 'launched', 'released' 等词"
    echo "   3. 关注特定账号:"
    echo "      - 添加提示词工程专家账号列表"
    echo ""
    
    # 生成优化后的搜索查询建议
    echo "📝 建议的搜索查询:"
    echo "   查询 1: \"AI prompt\" template OR framework OR guide"
    echo "   查询 2: ChatGPT prompt \"step by step\" tutorial"
    echo "   查询 3: prompt engineering examples \"how to\""
    echo "   查询 4: \"best AI prompts\" -news -launched"
    echo ""
    
    # 创建优化报告
    OPTIMIZATION_REPORT="$REPORT_DIR/optimization-suggestion-$(date +%Y%m%d-%H%M%S).md"
    cat > "$OPTIMIZATION_REPORT" << EOF
# 搜索策略优化建议

## 📊 当前评分情况

- **平均评分**: $AVG_SCORE (目标: 65)
- **高质量占比**: $HIGH_QUALITY_PERCENT% (目标: 15%)
- **检测时间**: $(date '+%Y-%m-%d %H:%M:%S')

## ⚠️ 问题分析

**原因**:
$(for reason in "${REASONS[@]}"; do echo "- $reason"; done)

## 🔍 根本原因

当前搜索查询过于宽泛，抓取的内容包括：
- 产品新闻和公告（如 "New feature", "Launched"）
- 行业动态（如 "Google Genie 3"）
- 示例展示（如生成的 AI 图像、视频）

这些内容虽然有热度，但不包含实用的提示词教程。

## 💡 优化方案

### 方案 1: 精确关键词匹配

**原查询**: \`"AI" OR "prompt" OR "ChatGPT"\`

**优化后**:
1. \`"AI prompt" template OR framework OR guide\`
2. \`ChatGPT prompt "step by step" tutorial\`
3. \`prompt engineering examples "how to"\`
4. \`"best AI prompts" -news -launched\`

### 方案 2: 过滤新闻类内容

添加排除词:
- \`-launched -released -announcing -new feature\`

### 方案 3: 关注专业账号

创建白名单账号列表，优先抓取:
- 提示词工程专家
- AI 工具开发者
- 技术教程创作者

### 方案 4: 增加最小互动阈值

设置最低要求:
- 最小点赞数: 50
- 最小转发数: 10
- 最小收藏数: 5

## 🎯 预期效果

- 平均评分提升至 60+
- 高质量占比提升至 10%+
- 减少新闻/公告类内容比例

## 📝 下一步行动

1. 更新搜索脚本 \`$TWEET_SCRIPT\`
2. 测试新的搜索查询
3. 运行自动化评分系统验证效果
4. 根据结果进一步优化

---

**报告生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
EOF
    
    echo "✅ 优化建议已保存: $OPTIMIZATION_REPORT"
    echo ""
    
    # 发送优化建议到 Slack
    SLACK_MESSAGE="⚠️ 评分过低，建议优化搜索策略

📊 **当前评分**:
• 平均分: $AVG_SCORE (目标: 65)
• 高质量: $HIGH_QUALITY_PERCENT% (目标: 15%)

🔍 **问题原因**:
${REASONS[*]}

💡 **优化建议**:
1. 使用更精确的查询: \"AI prompt\" template OR framework
2. 过滤新闻类: -launched -released -announcing
3. 关注专业账号
4. 设置最小互动阈值

📝 详细建议: $OPTIMIZATION_REPORT

🔧 是否立即优化搜索策略？回复 \"优化搜索\" 执行"

    echo "========================================"
    echo "$SLACK_MESSAGE"
    echo "========================================"
    
else
    echo "✅ 评分良好，无需优化搜索策略"
    echo ""
    echo "📊 当前状态:"
    echo "   平均评分: $AVG_SCORE (>= $MIN_AVG_SCORE) ✅"
    echo "   高质量占比: $HIGH_QUALITY_PERCENT% (>= $MIN_HIGH_QUALITY%) ✅"
fi

echo ""
echo "========================================"
echo "✅ 智能自动化评分系统执行完成"
echo "========================================"
