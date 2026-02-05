#!/bin/bash
# 简化版：打包单个 Skill

set -e

SOURCE_MD="$1"
if [ -z "$SOURCE_MD" ]; then
    echo "用法: $0 <skill.md 文件路径>"
    exit 1
fi

SKILL_NAME=$(basename "$SOURCE_MD" .md)
OUTPUT_DIR="/root/clawd/dist"
TEMP_DIR="/tmp/skill-package-$$"

echo "📦 打包 Skill: $SKILL_NAME"

# 创建临时目录
mkdir -p "$TEMP_DIR"
mkdir -p "$OUTPUT_DIR"

# 复制文件
cp "$SOURCE_MD" "$TEMP_DIR/SKILL.md"

# 打包
cd "$TEMP_DIR"
zip -q -r "$OUTPUT_DIR/${SKILL_NAME}.skill" *

# 清理
cd -
rm -rf "$TEMP_DIR"

echo "✅ 已生成: $OUTPUT_DIR/${SKILL_NAME}.skill"
ls -lh "$OUTPUT_DIR/${SKILL_NAME}.skill"
