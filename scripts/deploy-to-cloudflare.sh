#!/bin/bash
# 自动部署到 Cloudflare Pages

set -e

PROJECT_NAME="jack-portfolio"
SOURCE_DIR="/tmp/hhhh124hhhh.github.io"

echo "🚀 部署到 Cloudflare Pages..."
echo "项目: $PROJECT_NAME"
echo "源目录: $SOURCE_DIR"
echo ""

# 检查 Wrangler 是否安装
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler 未安装"
    echo ""
    echo "请先安装："
    echo "  npm install -g wrangler"
    echo ""
    echo "然后登录："
    echo "  wrangler login"
    exit 1
fi

echo "✅ Wrangler 已安装"
echo ""

# 检查是否已登录
echo "检查登录状态..."
if wrangler whoami &> /dev/null; then
    echo "✅ 已登录 Cloudflare"
else
    echo "❌ 未登录 Cloudflare"
    echo ""
    echo "请先登录："
    echo "  wrangler login"
    exit 1
fi

echo ""
echo "📤 开始部署..."
cd "$SOURCE_DIR"

# 部署到 Cloudflare Pages
wrangler pages deploy . --project-name="$PROJECT_NAME"

echo ""
echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址："
echo "  https://$PROJECT_NAME.pages.dev"
echo ""
echo "📝 管理页面："
echo "  https://dash.cloudflare.com/$PROJECT_NAME"
