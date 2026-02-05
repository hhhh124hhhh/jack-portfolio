#!/bin/bash
# 测试打包 - 只打包，不发布

SOURCE_DIR="/root/clawd/generated-skills"
OUTPUT_DIR="/root/clawd/dist/test"

mkdir -p "$OUTPUT_DIR"

echo "测试打包 skills..."
echo ""

SUCCESS_PACKED=0
FAILED_PACKED=0

cd "$SOURCE_DIR" || exit 1

for skill_dir in */; do
    [[ -z "$skill_dir" ]] && continue
    skill_name=${skill_dir%/}
    output_file="$OUTPUT_DIR/${skill_name}.skill"
    temp_dir="/tmp/skill-package-$$-${skill_name}"

    if [[ ! -f "${skill_dir}SKILL.md" ]]; then
        echo "⚠️  跳过 $skill_name (缺少 SKILL.md)"
        ((FAILED_PACKED++))
        continue
    fi

    mkdir -p "$temp_dir"
    cp -r "${skill_dir}"* "$temp_dir/" 2>/dev/null

    cd "$temp_dir" || continue
    if zip -q -r "$output_file" . 2>/dev/null; then
        file_size=$(du -h "$output_file" | cut -f1)
        echo "✅ 已打包: ${skill_name}.skill ($file_size)"
        ((SUCCESS_PACKED++))
    else
        echo "❌ 打包失败: $skill_name"
        ((FAILED_PACKED++))
    fi

    cd "$SOURCE_DIR"
    rm -rf "$temp_dir"
done

echo ""
echo "打包完成: $SUCCESS_PACKED 成功, $FAILED_PACKED 失败"
