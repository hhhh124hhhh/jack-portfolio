#!/bin/bash
# 测试自动更新脚本

echo "=========================================="
echo "Clawdbot 自动更新测试"
echo "=========================================="
echo ""

echo "1. 检查脚本权限..."
ls -la /root/clawd/scripts/auto-update-clawdbot.sh

echo ""
echo "2. 加载配置文件..."
if [ -f "/root/clawd/scripts/auto-update-config.sh" ]; then
    source /root/clawd/scripts/auto-update-config.sh
    echo "✅ 配置文件加载成功"
    echo "   FEISHU_USER_ID: ${FEISHU_USER_ID:-未设置}"
    echo "   SLACK_DM_ID: ${SLACK_DM_ID:-未设置}"
else
    echo "❌ 配置文件不存在"
fi

echo ""
echo "3. 测试自动更新脚本..."
/root/clawd/scripts/auto-update-clawdbot.sh --help

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="
