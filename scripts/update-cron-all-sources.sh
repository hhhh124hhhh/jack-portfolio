#!/bin/bash
# 更新定时任务：移除旧任务，添加新的全源收集任务

echo "=========================================="
echo "更新定时任务"
echo "=========================================="

# 1. 删除旧的多源任务（如果有）
echo ""
echo "[1/3] 删除旧的多源收集任务..."
clawdbot cron remove 6cff3f0c-c6e3-4b69-abfc-a2981ccb3355 2>/dev/null || echo "旧任务不存在"

# 2. 添加新的全源收集任务
echo ""
echo "[2/3] 添加新的全源收集任务..."
clawdbot cron add \
  --name "all-sources-collect" \
  --cron "0 */6 * * *" \
  --session main \
  --wake next-heartbeat \
  --system-event "运行 /root/clawd/scripts/collect-all-sources-prompts.sh 集成所有数据源收集 AI 提示词"

# 3. 显示所有定时任务
echo ""
echo "[3/3] 查看所有定时任务..."
clawdbot cron list

echo ""
echo "=========================================="
echo "✅ 定时任务更新完成！"
echo "=========================================="
echo ""
echo "新的全源收集任务："
echo "  频率: 每 6 小时"
echo "  数据源: Reddit, GitHub, Hacker News, SearXNG"
echo "  预计收集: 50-100 条/次"
echo "=========================================="
