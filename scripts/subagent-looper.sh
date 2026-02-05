#!/bin/bash
# 子代理持续工作触发器
# 用法：./subagent-looper.sh <sessionKey> [间隔秒数]

SESSION_KEY="${1:-agent:main:subagent:ee7e0c4e-365a-4e84-820f-888985600896}"
INTERVAL="${2:-60}"  # 默认 60 秒

echo "🔄 启动子代理持续工作触发器"
echo "Session: $SESSION_KEY"
echo "Interval: ${INTERVAL}s"
echo "按 Ctrl+C 停止"

while true; do
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 发送续命指令..."

  clawdbot sessions send "$SESSION_KEY" "继续执行任务，从 memory/$(date +%Y-%m-%d).md 读取进度" 2>/dev/null

  sleep $INTERVAL
done
