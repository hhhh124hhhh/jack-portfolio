#!/bin/bash

# 打包 TikTok AI Model Generator Skill

SKILL_NAME="tiktok-ai-model-generator"
SKILL_DIR="skills/${SKILL_NAME}"
OUTPUT_DIR="dist"
SKILL_FILE="${OUTPUT_DIR}/${SKILL_NAME}.skill"

echo "=========================================="
echo "打包 Skill: ${SKILL_NAME}"
echo "=========================================="
echo ""

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 检查技能目录是否存在
if [ ! -d "$SKILL_DIR" ]; then
    echo "❌ 错误: 技能目录不存在 $SKILL_DIR"
    exit 1
fi

# 检查 SKILL.md 是否存在
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "❌ 错误: SKILL.md 不存在"
    exit 1
fi

# 验证 frontmatter
echo "验证 SKILL.md..."

if ! grep -q "^name:" "$SKILL_DIR/SKILL.md"; then
    echo "❌ 错误: SKILL.md 缺少 name 字段"
    exit 1
fi

if ! grep -q "^description:" "$SKILL_DIR/SKILL.md"; then
    echo "❌ 错误: SKILL.md 缺少 description 字段"
    exit 1
fi

if ! grep -q "^version:" "$SKILL_DIR/SKILL.md"; then
    echo "❌ 错误: SKILL.md 缺少 version 字段"
    exit 1
fi

echo "✓ Frontmatter 验证通过"

# 提取 skill 信息
NAME=$(grep "^name:" "$SKILL_DIR/SKILL.md" | head -1 | sed 's/^name: //' | tr -d '"')
VERSION=$(grep "^version:" "$SKILL_DIR/SKILL.md" | head -1 | sed 's/^version: //' | tr -d '"')
DESCRIPTION=$(grep "^description:" "$SKILL_DIR/SKILL.md" | head -1 | sed 's/^description: //' | cut -c1-80)

echo ""
echo "Skill 信息:"
echo "  Name: $NAME"
echo "  Version: $VERSION"
echo "  Description: $DESCRIPTION..."
echo ""

# 列出将要打包的文件
echo "将要打包的文件:"
find "$SKILL_DIR" -type f | sort | sed 's/^/  /'
echo ""

# 打包成 .skill 文件
echo "开始打包..."
cd "$SKILL_DIR"
if zip -r "../../$SKILL_FILE" . -q; then
    cd ../..
else
    echo "❌ 打包失败"
    exit 1
fi

# 检查打包是否成功
if [ -f "$SKILL_FILE" ]; then
    SIZE=$(du -h "$SKILL_FILE" | cut -f1)
    echo "✓ 打包成功: $SKILL_FILE ($SIZE)"
    echo ""
    
    # 显示打包文件内容
    echo "打包文件内容:"
    echo "----------------------------------------"
    zipinfo -1 "$SKILL_FILE" | sed 's/^/  /'
    echo "----------------------------------------"
    echo ""
    
    echo "=========================================="
    echo "✓ 打包完成！"
    echo "=========================================="
    echo ""
    echo "Skill 文件: $SKILL_FILE"
    echo "Skill 名称: $NAME"
    echo "Skill 版本: $VERSION"
    echo "文件大小: $SIZE"
    echo ""
    echo "可以安装到 Clawdbot:"
    echo "  clawd skill install $SKILL_NAME"
    echo ""
    echo "或手动复制 .skill 文件到 skills 目录"
    
    exit 0
else
    echo "❌ 打包失败: 文件未生成"
    exit 1
fi
