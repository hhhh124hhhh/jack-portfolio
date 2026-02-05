#!/bin/bash
# 更新定时任务：移除 Twitter，添加多源收集

echo "=========================================="
echo "更新定时任务"
echo "=========================================="

# 1. 删除 Twitter 任务（API 额度不足）
echo ""
echo "[1/3] 删除 Twitter 搜索任务..."
clawdbot cron remove 547dbb49-0a26-405a-a4f4-7bb8597158a8

# 2. 添加多源收集任务
echo ""
echo "[2/3] 添加多源收集任务..."
clawdbot cron add \
  --name "multi-source-collect" \
  --cron "0 */6 * * *" \
  --session main \
  --wake next-heartbeat \
  --system-event "运行 /root/clawd/scripts/collect-multi-source-prompts.sh 集成 Reddit 和 SearXNG 收集 AI 提示词"

# 3. 显示任务列表
echo ""
echo "[3/3] 查看所有定时任务..."
clawdbot cron list

echo ""
echo "=========================================="
echo "✅ 定时任务更新完成！"
echo "=========================================="
