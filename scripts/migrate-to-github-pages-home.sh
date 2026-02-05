#!/bin/bash
# 将 jack-portfolio 迁移到 hhhh124hhhh.github.io

set -e

echo "🚀 开始迁移到 GitHub Pages 主页..."

# 1. 进入当前目录
cd /root/clawd/jack-portfolio

# 2. 备份当前仓库
echo "📦 备份当前仓库..."
git branch backup-$(date +%Y%m%d)
git push origin backup-$(date +%Y%m%d)

# 3. 创建新的 GitHub Pages 仓库
echo "📝 创建新仓库..."
NEW_REPO="hhhh124hhhh.github.io"

# 4. 复制内容到临时目录
TEMP_DIR="/tmp/$NEW_REPO"
echo "📋 复制内容到临时目录..."
cp -r /root/clawd/jack-portfolio "$TEMP_DIR"

# 5. 在临时目录中初始化新的 git 仓库
echo "🔧 初始化新仓库..."
cd "$TEMP_DIR"
rm -rf .git
git init

# 6. 添加所有文件
git add .

# 7. 创建首次提交
git commit -m "初始化 GitHub Pages 主页

个人主页：
- AI 技能开发者 | 自动化工程师
- 主页 + 6 个项目子页面
- GitHub Pages 部署
- Google Analytics 追踪"

# 8. 添加远程仓库
echo "🔗 添加远程仓库..."
git remote add origin git@github.com:hhhh124hhhh/$NEW_REPO.git

# 9. 推送到 GitHub
echo "📤 推送到 GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ 迁移完成！"
echo ""
echo "📊 新仓库信息："
echo "  仓库名: $NEW_REPO"
echo "  本地路径: $TEMP_DIR"
echo "  访问地址: https://hhhh124hhhh.github.io/"
echo ""
echo "📝 下一步："
echo "  1. 访问 https://github.com/hhhh124hhhh/$NEW_REPO"
echo "  2. 启用 GitHub Pages（Settings → Pages → Source: Deploy from branch 'main'）"
echo "  3. 等待 1-2 分钟"
echo "  4. 访问 https://hhhh124hhhh.github.io/"
