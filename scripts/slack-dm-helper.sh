#!/bin/bash
# Slack DM Channel ID 获取辅助工具

echo "=========================================="
echo "Slack 私聊（DM）配置助手"
echo "=========================================="
echo ""

echo "方法 1: 查看浏览器 URL（最简单）"
echo "----------------------------------------"
echo "1. 在 Slack 中给你的 Bot 发消息"
echo "2. 打开私聊窗口"
echo "3. 查看浏览器地址栏"
echo "4. URL 格式: https://workspace.slack.com/archives/D0123456789"
echo "5. 复制 D 开头的 ID"
echo ""

echo "方法 2: 使用浏览器开发者工具"
echo "----------------------------------------"
echo "1. 在 Slack 私聊窗口按 F12"
echo "2. 切换到 Console 标签"
echo "3. 粘贴以下代码并回车:"
echo ""
cat << 'JS_CODE'
// 复制当前 DM Channel ID
const channelId = window.location.pathname.split('/').pop();
if (channelId.startsWith('D')) {
  console.log('✅ DM Channel ID:', channelId);
  navigator.clipboard.writeText(channelId);
  console.log('✅ 已复制到剪贴板！');
} else {
  console.log('❌ 当前不是 DM 窗口');
}
JS_CODE
echo ""

echo "=========================================="
echo "准备好后，请将 DM Channel ID（D 开头）发给我"
echo "=========================================="
