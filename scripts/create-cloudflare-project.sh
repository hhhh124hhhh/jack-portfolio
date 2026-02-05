#!/bin/bash
# 使用 curl 直接部署到 Cloudflare Pages

set -e

API_TOKEN="Sd0vKvLKAVaKIScuBEEsPb1d3tAmL8aR-wh4M6sf"
ACCOUNT_ID="944fa484617a666c2f04aa2cc308285c"
PROJECT_NAME="jack-portfolio"

echo "🚀 部署到 Cloudflare Pages"
echo ""

# 测试 Token
echo "🔑 验证 API Token..."
VERIFY=$(curl -s -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $API_TOKEN")

if echo "$VERIFY" | jq -e '.success' > /dev/null; then
  echo "✅ Token 有效"
else
  echo "❌ Token 无效"
  echo "$VERIFY" | jq '.'
  exit 1
fi

echo ""

# 创建项目（如果不存在）
echo "📝 创建项目..."
CREATE=$(curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/pages/projects" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  --data "{\"name\":\"$PROJECT_NAME\",\"production_branch\":\"main\"}")

if echo "$CREATE" | jq -e '.success' > /dev/null; then
  echo "✅ 项目创建成功"
elif echo "$CREATE" | jq -e '.errors[0].code == 10009' > /dev/null; then
  echo "✅ 项目已存在"
else
  echo "❌ 项目创建失败"
  echo "$CREATE" | jq '.'
  exit 1
fi

echo ""
echo "🌐 访问地址："
echo "  https://$PROJECT_NAME.pages.dev"
echo ""
echo "📝 项目管理："
echo "  https://dash.cloudflare.com/$ACCOUNT_ID/pages/view/$PROJECT_NAME"
echo ""
echo "⚠️  注意："
echo "  - 项目已创建，但还需要上传文件"
echo "  - 请使用 Cloudflare Dashboard 手动上传"
echo "  - 或者使用 GitHub Actions 自动部署"
