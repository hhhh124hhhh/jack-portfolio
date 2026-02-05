#!/bin/bash
# Video Prompt API 部署脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/tmp/video-prompt-api"
REPO_NAME="video-prompt-api"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Video Prompt API 部署到 Vercel${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查 xAI API Key
if [ -z "$XAI_API_KEY" ]; then
    echo -e "${RED}❌ 错误: XAI_API_KEY 未配置${NC}"
    echo -e "${YELLOW}请先运行: bash /root/clawd/scripts/setup-xai-api.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ XAI_API_KEY 已配置${NC}"
echo ""

# 检查是否已安装 Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}⚠️  Vercel CLI 未安装，正在安装...${NC}"
    npm i -g vercel
    echo -e "${GREEN}✅ Vercel CLI 安装完成${NC}"
else
    echo -e "${GREEN}✅ Vercel CLI 已安装${NC}"
fi

echo ""

# 进入项目目录
cd "$PROJECT_DIR"

# 初始化 git
if [ ! -d ".git" ]; then
    echo -e "${BLUE}[1/5] 初始化 Git 仓库...${NC}"
    git init
    git add .
    git commit -m "Initial commit: Video Prompt Generator API"
    echo -e "${GREEN}✅ Git 仓库已初始化${NC}"
else
    echo -e "${BLUE}[1/5] Git 仓库已存在${NC}"
fi

echo ""

# 创建 GitHub 仓库（如果不存在）
echo -e "${BLUE}[2/5] 创建 GitHub 仓库...${NC}"

# 检查是否已经存在远程仓库
if git remote get-url origin &> /dev/null; then
    REMOTE_URL=$(git remote get-url origin)
    echo -e "${YELLOW}⚠️  已存在远程仓库: ${REMOTE_URL}${NC}"
    read -p "是否使用现有仓库? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}取消部署${NC}"
        exit 0
    fi
else
    # 使用 gh CLI 创建仓库
    if command -v gh &> /dev/null; then
        gh repo create "$REPO_NAME" --public --source=. --remote=origin
        echo -e "${GREEN}✅ GitHub 仓库已创建: https://github.com/$(gh api user --jq .login)/$REPO_NAME${NC}"
    else
        echo -e "${RED}❌ gh CLI 未安装${NC}"
        echo -e "${YELLOW}请手动创建 GitHub 仓库: https://github.com/new${NC}"
        echo -e "${YELLOW}仓库名: $REPO_NAME${NC}"
        echo ""
        read -p "手动创建后按 Enter 继续: " -r
        echo ""

        read -p "输入仓库 URL: " REPO_URL
        git remote add origin "$REPO_URL"
        echo -e "${GREEN}✅ 远程仓库已添加${NC}"
    fi
fi

echo ""

# 推送代码
echo -e "${BLUE}[3/5] 推送代码到 GitHub...${NC}"
git branch -M main
git push -u origin main --force
echo -e "${GREEN}✅ 代码已推送${NC}"

echo ""

# 部署到 Vercel
echo -e "${BLUE}[4/5] 部署到 Vercel...${NC}"
echo -e "${YELLOW}注意: 部署过程中需要输入一些配置${NC}"
echo ""

vercel --prod

echo ""

# 获取部署 URL
DEPLOY_URL=$(vercel ls --prod 2>/dev/null | grep "video-prompt-api" | awk '{print $2}' | head -1)

if [ -z "$DEPLOY_URL" ]; then
    DEPLOY_URL="https://video-prompt-api.vercel.app"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "API URL: ${GREEN}${DEPLOY_URL}${NC}"
echo ""
echo -e "${BLUE}下一步：${NC}"
echo -e "1. ${YELLOW}配置环境变量${NC}"
echo -e "   访问: https://vercel.com/dashboard"
echo -e "   项目: video-prompt-api"
echo -e "   Settings → Environment Variables"
echo -e "   添加: XAI_API_KEY = ${XAI_API_KEY:0:10}..."
echo ""
echo -e "2. ${YELLOW}重启部署${NC}"
echo -e "   在 Vercel Dashboard 点击 'Redeploy'"
echo ""
echo -e "3. ${YELLOW}测试 API${NC}"
echo -e "   ${BLUE}curl ${DEPLOY_URL}/api/status${NC}"
echo ""
echo -e "4. ${YELLOW}更新 Web UI${NC}"
echo -e "   修改前端代码中的 API 地址为: ${DEPLOY_URL}/api/generate-video"
echo ""
