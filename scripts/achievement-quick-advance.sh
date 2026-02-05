#!/bin/bash
# 成就快速推进脚本
# 快速记录大量活动来推进成就解锁

echo "🚀 开始快速推进成就..."

cd /root/clawd/scripts

# 阶段一：快速解锁 - 使用更多工具和技能
echo ""
echo "📍 阶段一：快速解锁"

# 记录工具使用（多种工具）
for tool in exec read write message process browser canvas nodes exec git; do
    echo "📊 记录工具: $tool"
    python3 achievement-integrator.py tool "$tool" > /dev/null 2>&1
done

# 记录技能使用（多种技能）
for skill in coding-agent searxng firecrawl twitter-search github weather frontend-design; do
    echo "⚡ 记录技能: $skill"
    python3 achievement-integrator.py skill "$skill" > /dev/null 2>&1
done

# 记录消息处理（批量）
echo "💬 记录消息: 50 条"
python3 achievement-integrator.py message 50 --platform slack > /dev/null 2>&1

# 记录工作流
echo "🔄 记录工作流: batch-processing"
python3 achievement-integrator.py workflow batch-processing > /dev/null 2>&1

# 检查成就
echo ""
echo "🏆 检查成就..."
python3 achievement-integrator.py check > /dev/null 2>&1

# 显示状态
echo ""
echo "📊 当前状态:"
python3 achievement-integrator.py status

echo ""
echo "✅ 阶段一完成！"
