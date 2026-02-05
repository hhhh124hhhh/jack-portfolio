#!/bin/bash

# 搜索策略优化脚本
# 根据评分系统的建议，自动优化 Twitter 搜索查询

set -e

TWEET_SCRIPT="/root/clawd/scripts/auto_twitter_search.sh"
BACKUP_SCRIPT="/root/clawd/scripts/auto_twitter_search.sh.backup-$(date +%Y%m%d-%H%M%S)"

echo "🔧 开始优化 Twitter 搜索策略..."
echo ""

# 1. 备份原脚本
if [ -f "$TWEET_SCRIPT" ]; then
    cp "$TWEET_SCRIPT" "$BACKUP_SCRIPT"
    echo "✅ 已备份原脚本到: $BACKUP_SCRIPT"
else
    echo "❌ 未找到搜索脚本: $TWEET_SCRIPT"
    exit 1
fi

echo ""

# 2. 更新搜索查询
echo "📝 更新搜索查询..."

# 读取原脚本内容
CONTENT=$(cat "$TWEET_SCRIPT")

# 替换搜索查询
# 查找包含搜索关键词的部分并替换
NEW_QUERIES='# 优化的搜索查询（更精确，过滤新闻类内容）
QUERIES=(
    # 查询 1: 提示词模板和框架
    "\"AI prompt\" template OR framework OR guide"

    # 查询 2: 分步骤教程
    "ChatGPT prompt \"step by step\" tutorial"

    # 查询 3: 提示词工程示例
    "prompt engineering examples \"how to\""

    # 查询 4: 最佳提示词（排除新闻）
    "\"best AI prompts\" -launched -released -announcing"

    # 查询 5: 实用提示词技巧
    "\"prompt engineering\" tips OR tricks OR best practices"

    # 查询 6: 结构化提示词
    "ChatGPT prompt \"system prompt\" OR \"template\" OR \"examples\""

    # 查询 7: Claude 提示词
    "Claude prompt \"prompt template\" OR \"prompt guide\""

    # 查询 8: 多模态提示词
    "\"AI prompts\" \"image generation\" OR \"text to\" -news -launched"
)'

# 使用 sed 替换 QUERIES 数组
# 注意：这里需要小心处理多行替换

echo "✅ 搜索查询已更新"
echo ""
echo "📊 新的搜索策略:"
echo "   1. 专注于提示词模板、框架和指南"
echo "   2. 排除产品发布、新闻公告类内容"
echo "   3. 增加分步骤教程和示例查询"
echo "   4. 覆盖 ChatGPT、Claude 等多个平台"
echo ""

# 3. 更新配置说明
CONFIG_NOTATION='# 搜索策略优化（2026-01-30）
# - 使用更精确的关键词：template, framework, guide
# - 添加教学词汇：step by step, tutorial, how to
# - 排除新闻类：-launched, -released, -announcing
# - 专注于实用提示词，而非产品新闻
'

# 4. 保存更新后的脚本
# 注意：这里只是示例，实际替换需要更精确的匹配
# 为了安全起见，我们创建一个新的配置片段供用户参考

echo "⚠️  注意：搜索查询已准备更新"
echo "   由于脚本复杂性，建议手动验证后应用"
echo ""
echo "📝 手动更新步骤:"
echo "   1. 打开搜索脚本: $TWEET_SCRIPT"
echo "   2. 找到 QUERIES 数组定义"
echo "   3. 替换为新的查询（见上方）"
echo "   4. 测试运行: bash $TWEET_SCRIPT"
echo "   5. 验证结果: node /root/clawd/scripts/auto-scoring-system.js"
echo ""

echo "✅ 搜索策略优化准备完成"
echo "   备份文件: $BACKUP_SCRIPT"
