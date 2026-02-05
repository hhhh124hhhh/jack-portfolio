#!/bin/bash
# 打包所有生成的 Skills 为 .skill 文件

set -e

SOURCE_DIR="/root/clawd/generated-skills"
OUTPUT_DIR="/root/clawd/dist"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "📦 打包 Skills 为 .skill 文件"
echo "=========================================="

# 统计
SUCCESS_COUNT=0
FAILED_COUNT=0

# 处理每个 markdown 文件
for skill_md in "$SOURCE_DIR"/*.md; do
    if [[ ! -f "$skill_md" ]]; then
        continue
    fi

    # 跳过非 skill 文件
    if [[ "$skill_md" == *"version-report"* ]]; then
        echo "⏭️  跳过: $(basename "$skill_md")"
        continue
    fi

    skill_name=$(basename "$skill_md" .md)
    echo ""
    echo "📦 打包: $skill_name"

    # 创建临时目录
    TEMP_DIR="/tmp/skill-package-$$-$skill_name"
    mkdir -p "$TEMP_DIR"

    try {
        # 复制 markdown 文件
        cp "$skill_md" "$TEMP_DIR/SKILL.md"

        # 检查是否有其他文件（图片、配置等）
        skill_dir=$(dirname "$skill_md")
        if [ -d "$skill_dir" ]; then
            for file in "$skill_dir"/*; do
                if [ -f "$file" ]; then
                    filename=$(basename "$file")
                    if [ "$filename" != "$(basename "$skill_md")" ]; then
                        cp "$file" "$TEMP_DIR/"
                    fi
                fi
            done
        fi

        # 打包成 .skill 文件
        cd "$TEMP_DIR"
        zip -q -r "$OUTPUT_DIR/${skill_name}.skill" *

        echo "✅ 已生成: $OUTPUT_DIR/${skill_name}.skill"
        ((SUCCESS_COUNT++))

    } catch {
        echo "❌ 打包失败: $skill_name"
        ((FAILED_COUNT++))
    }

    # 清理临时目录
    rm -rf "$TEMP_DIR"
done

echo ""
echo "=========================================="
echo "打包总结"
echo "=========================================="
echo "✅ 成功: $SUCCESS_COUNT"
echo "❌ 失败: $FAILED_COUNT"
echo "📁 输出目录: $OUTPUT_DIR"

if [[ $SUCCESS_COUNT -gt 0 ]]; then
    echo ""
    echo "生成的 .skill 文件:"
    ls -lh "$OUTPUT_DIR"/*.skill
fi

echo "=========================================="

# 返回成功状态
if [[ $FAILED_COUNT -eq 0 && $SUCCESS_COUNT -gt 0 ]]; then
    exit 0
else
    exit 1
fi
