#!/bin/bash
# 设置自动化流水线的 Cron 任务

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

CONFIG_FILE="/root/clawd/automation-config.json"
PIPELINE_SCRIPT="/root/clawd/scripts/full-auto-pipeline.sh"

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ 配置文件不存在: $CONFIG_FILE${NC}"
    exit 1
fi

# 读取调度配置
SCHEDULE=$(jq -r '.pipeline.schedule' "$CONFIG_FILE")
SCHEDULE_DESC=$(jq -r '.pipeline.schedule_desc' "$CONFIG_FILE")
ENABLED=$(jq -r '.pipeline.enabled' "$CONFIG_FILE")

echo "=========================================="
echo "自动化流水线 Cron 设置"
echo "=========================================="
echo ""
echo "配置:"
echo "  调度: $SCHEDULE"
echo "  说明: $SCHEDULE_DESC"
echo "  状态: $ENABLED"
echo ""

if [ "$ENABLED" != "true" ]; then
    echo -e "${YELLOW}⚠️  流水线未启用，跳过 Cron 设置${NC}"
    exit 0
fi

# 检查脚本是否存在
if [ ! -f "$PIPELINE_SCRIPT" ]; then
    echo -e "${RED}❌ 流水线脚本不存在: $PIPELINE_SCRIPT${NC}"
    exit 1
fi

# 创建日志目录
LOG_DIR="/root/clawd/logs"
mkdir -p "$LOG_DIR"

# 检查是否已有 cron 任务
EXISTING_CRON=$(crontab -l 2>/dev/null | grep -c "full-auto-pipeline.sh" || echo "0")

if [ "$EXISTING_CRON" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  检测到已有的 Cron 任务${NC}"
    echo ""
    read -p "是否要移除并重新创建？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消操作"
        exit 0
    fi
    # 移除旧任务
    crontab -l 2>/dev/null | grep -v "full-auto-pipeline.sh" | crontab -
    echo -e "${GREEN}✅ 已移除旧的 Cron 任务${NC}"
fi

# 添加新的 Cron 任务
CRON_LINE="$SCHEDULE $PIPELINE_SCRIPT >> /root/clawd/logs/cron.log 2>&1"
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

echo -e "${GREEN}✅ Cron 任务已添加${NC}"
echo ""
echo "当前 Cron 任务:"
crontab -l | grep "full-auto-pipeline.sh"
echo ""
echo "日志文件: /root/clawd/logs/cron.log"
echo ""
echo "=========================================="
echo "✅ 设置完成！"
echo "=========================================="
echo ""
echo "下一步:"
echo "  1. 检查 ClawdHub 登录状态: clawdhub whoami"
echo "  2. 如未登录，运行: clawdhub login --token <YOUR_TOKEN> --no-browser"
echo "  3. 手动测试一次流水线: bash $PIPELINE_SCRIPT"
echo "  4. 监控日志: tail -f /root/clawd/logs/cron.log"
echo ""
