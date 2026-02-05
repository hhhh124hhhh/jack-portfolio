#!/bin/bash
# XAI API 配置脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  XAI API 配置工具${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查是否已配置
if [ -n "$XAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  XAI_API_KEY 已配置${NC}"
    echo -e "当前值: ${XAI_API_KEY:0:10}..."
    echo ""
    read -p "是否重新配置? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ 保持当前配置${NC}"
        exit 0
    fi
fi

# 获取 API Key
echo -e "${YELLOW}请输入你的 XAI API Key:${NC}"
echo -e "(从 https://x.ai 获取)"
read -p "> " API_KEY

if [ -z "$API_KEY" ]; then
    echo -e "${RED}❌ API Key 不能为空${NC}"
    exit 1
fi

# 验证格式（基本的长度检查）
if [ ${#API_KEY} -lt 20 ]; then
    echo -e "${RED}⚠️  API Key 看起来太短，请确认${NC}"
    read -p "是否继续? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 创建 .env.d 目录
mkdir -p /root/clawd/.env.d

# 写入配置文件
cat > /root/clawd/.env.d/xai.env <<EOF
# XAI API 配置
export XAI_API_KEY="${API_KEY}"
EOF

echo -e "${GREEN}✅ 配置文件已创建: /root/clawd/.env.d/xai.env${NC}"

# 检查是否已添加到 ~/.bashrc
if ! grep -q "xai.env" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# XAI API 配置" >> ~/.bashrc
    echo "source /root/clawd/.env.d/xai.env" >> ~/.bashrc
    echo -e "${GREEN}✅ 已添加到 ~/.bashrc${NC}"
else
    echo -e "${YELLOW}⚠️  ~/.bashrc 已包含配置${NC}"
fi

# 加载配置
source /root/clawd/.env.d/xai.env

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  配置完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "API Key: ${GREEN}${API_KEY:0:10}...${NC}"
echo ""
echo -e "下一步："
echo -e "1. 测试 API 连接:"
echo -e "   ${YELLOW}python3 /root/clawd/skills/grok-imagine/grok-imagine.py image \"test\"${NC}"
echo ""
echo -e "2. 启动视频生成服务器:"
echo -e "   ${YELLOW}cd /root/clawd/skills/video-prompt-generator${NC}"
echo -e "   ${YELLOW}node generate.js --server --port 3000${NC}"
echo ""
echo -e "3. 打开 Web UI:"
echo -e "   ${YELLOW}https://hhhh124hhhh.github.io/video-prompt-generator.html${NC}"
echo ""
