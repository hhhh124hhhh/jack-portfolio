#!/bin/bash
# 部署到 GitHub Pages

echo "🚀 开始部署到 GitHub Pages..."

# 创建临时部署目录
DEPLOY_DIR="/tmp/jack-portfolio-deploy"
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# 复制文件
cp /root/clawd/jack-portfolio/index.html "$DEPLOY_DIR/index.html"

# 创建 README
cat > "$DEPLOY_DIR/README.md" << 'README'
# jack 的个人主页

AI 技能开发者 | 自动化工程师

## 访问

https://hhhh124hhhh.github.io/jack-portfolio/
README

# 初始化 Git
cd "$DEPLOY_DIR"
git init
git add .
git commit -m "Deploy portfolio to GitHub Pages"

# 推送到 GitHub
echo "📦 准备推送到 GitHub..."
echo "请手动执行以下命令："
echo ""
echo "cd $DEPLOY_DIR"
echo "git remote add origin https://github.com/hhhh124hhhh/jack-portfolio.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "然后在 GitHub 仓库设置中启用 GitHub Pages（选择 main 分支）"
echo "访问地址：https://hhhh124hhhh.github.io/jack-portfolio/"
