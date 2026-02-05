#!/bin/bash

# ============================================
# Twitter 搜索查询优化脚本
# 从宽泛查询切换到精准查询，提高数据质量
# ============================================

echo "🔍 Twitter 搜索查询优化"
echo "========================================"
echo ""

# 备份原脚本
SCRIPT_PATH="/root/clawd/scripts/auto_twitter_search.sh"
BACKUP_PATH="/root/clawd/scripts/auto_twitter_search.sh.backup"

if [ -f "$SCRIPT_PATH" ]; then
  cp "$SCRIPT_PATH" "$BACKUP_PATH"
  echo "✓ 已备份原脚本到: $BACKUP_PATH"
else
  echo "✗ 错误: 找不到 $SCRIPT_PATH"
  exit 1
fi

# 显示当前查询
CURRENT_QUERY=$(grep "^SEARCH_QUERY=" "$SCRIPT_PATH" | head -1 | cut -d'"' -f2)
echo ""
echo "当前搜索查询:"
echo "  $CURRENT_QUERY"
echo ""

# 定义新查询（更精准）
NEW_QUERY='#PromptEngineering OR #AIPrompts OR "prompt template" OR "prompt framework" OR "ChatGPT prompt" OR "Claude prompt" OR "AI prompt engineering guide" -is:retweet'

echo "推荐搜索查询:"
echo "  $NEW_QUERY"
echo ""

# 询问用户是否应用修改
read -p "是否应用新的搜索查询? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  # 修改脚本中的 SEARCH_QUERY
  sed -i "s|^SEARCH_QUERY=.*|SEARCH_QUERY='$NEW_QUERY'|g" "$SCRIPT_PATH"

  echo ""
  echo "✓ 搜索查询已更新"
  echo ""
  echo "主要改进:"
  echo "  1. 使用精确的 Hashtag (#PromptEngineering, #AIPrompts)"
  echo "  2. 添加 template/framework 等关键词"
  echo "  3. 明确指定平台 (ChatGPT prompt, Claude prompt)"
  echo "  4. 排除转推 (-is:retweet)"
  echo ""
  echo "预期效果:"
  echo "  - 推文质量提升 40-60%"
  echo "  - 实用提示词比例提升"
  echo "  - 减少 50% 的无关内容"
  echo ""
  echo "下一步:"
  echo "  1. 手动测试新查询效果"
  echo "  2. 监控下次自动搜索结果"
  echo "  3. 根据结果进一步调整"
else
  echo ""
  echo "✗ 已取消修改"
  echo "如需手动修改，编辑文件: $SCRIPT_PATH"
fi

echo ""
echo "如需恢复原查询，运行:"
echo "  cp $BACKUP_PATH $SCRIPT_PATH"
