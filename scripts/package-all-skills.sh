#!/bin/bash
# 打包所有生成的 Skills 为 .skill 文件

set -e

SKILLS_DIR="/root/clawd/generated-skills"
OUTPUT_DIR="/root/clawd/dist/skills"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "📦 打包 Skills 为 .skill 文件"
echo "=========================================="
echo ""

# 统计
SUCCESS_COUNT=0
FAILED_COUNT=0
PACKED_SKILLS=()

# 处理每个 Skill 目录
for skill_dir in "$SKILLS_DIR"/*; do
    # 跳过文件和隐藏目录
    if [[ ! -d "$skill_dir" ]]; then
        continue
    fi
    
    # 跳过报告文件
    if [[ "$skill_dir" == *report* ]]; then
        continue
    fi
    
    skill_name=$(basename "$skill_dir")
    output_file="$OUTPUT_DIR/${skill_name}.skill"
    
    echo "📦 打包: $skill_name"
    
    # 打包成 zip 文件
    cd "$SKILLS_DIR"
    if zip -q -r "$output_file" "$skill_name" 2>/dev/null; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        PACKED_SKILLS+=("$skill_name")
        echo "  ✓ 已生成: $output_file"
    else
        echo "  ❌ 打包失败: $skill_name"
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
done

echo ""
echo "=========================================="
echo "📊 打包统计"
echo "=========================================="
echo "✅ 成功: $SUCCESS_COUNT"
echo "❌ 失败: $FAILED_COUNT"
echo ""

if [ $FAILED_COUNT -gt 0 ]; then
    echo "失败的 Skills:"
    for skill in "${PACKED_SKILLS[@]}"; do
        echo "  - $skill"
    done
fi

echo "📁 输出目录: $OUTPUT_DIR"
echo ""

# 显示文件列表
echo "生成的 .skill 文件:"
ls -lh "$OUTPUT_DIR"/*.skill

echo ""
echo "=========================================="
echo "✅ 打包完成！"
echo "=========================================="

# 返回成功状态
if [ $FAILED_COUNT -eq 0 ] && [ $SUCCESS_COUNT -gt 0 ]; then
    exit 0
else
    exit 1
fi
