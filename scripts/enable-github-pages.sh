#!/bin/bash
# 启用 GitHub Pages（使用 GitHub CLI）

set -e

REPO="hhhh124hhhh/hhhh124hhhh.github.io"

echo "🚀 启用 GitHub Pages..."
echo "仓库: $REPO"
echo ""

# 使用 gh CLI 启用 Pages
gh api \
  --method POST \
  -H "Accept: application/vnd.github.v3+json" \
  "/repos/$REPO/pages" \
  -f build_type=legacy \
  -f source[branch]=master \
  -f source[path]=/

echo ""
echo "✅ GitHub Pages 已启用！"
echo ""
echo "📊 状态信息:"
gh api "/repos/$REPO/pages" | jq '{status: .status, html_url: .html_url, build_type: .build_type}'
echo ""
echo "⏳ 等待 1-2 分钟，然后访问:"
echo "   https://hhhh124hhhh.github.io/"
