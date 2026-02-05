#!/bin/bash

# 分析技能，判断是否可以发布到 ClawdHub

SKILLS_DIR="/root/clawd/skills"
REPORT_FILE="/root/clawd/memory/skills-publish-analysis.md"

echo "# 技能发布分析报告
生成时间: $(date '+%Y-%m-%d %H:%M:%S')
" > "$REPORT_FILE"

cd "$SKILLS_DIR"

for skill_dir in */; do
    skill_name="${skill_dir%/}"

    # 检查是否是目录
    if [ ! -d "$skill_dir" ]; then
        continue
    fi

    # 检查 SKILL.md 是否存在
    if [ ! -f "${skill_dir}SKILL.md" ]; then
        continue
    fi

    echo "## $skill_name" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    # 检查 frontmatter
    if grep -q "^name:" "${skill_dir}SKILL.md"; then
        name_value=$(grep "^name:" "${skill_dir}SKILL.md" | head -1 | cut -d':' -f2- | xargs)
        echo "- ✅ 有 name 字段: \`$name_value\`" >> "$REPORT_FILE"
    else
        echo "- ❌ 缺少 name 字段" >> "$REPORT_FILE"
    fi

    if grep -q "^description:" "${skill_dir}SKILL.md"; then
        desc_value=$(grep "^description:" "${skill_dir}SKILL.md" | head -1 | cut -d':' -f2- | xargs)
        echo "- ✅ 有 description 字段: \`${desc_value}\`" >> "$REPORT_FILE"
    else
        echo "- ❌ 缺少 description 字段" >> "$REPORT_FILE"
    fi

    # 检查是否有代码文件
    code_files=$(find "$skill_dir" -type f \( -name "*.py" -o -name "*.sh" -o -name "*.js" -o -name "*.ts" \) | wc -l)
    if [ "$code_files" -gt 0 ]; then
        echo "- 📝 代码文件数量: $code_files" >> "$REPORT_FILE"
        find "$skill_dir" -type f \( -name "*.py" -o -name "*.sh" -o -name "*.js" -o -name "*.ts" \) | head -3 | while read file; do
            echo "  - \`$(basename "$file")\`" >> "$REPORT_FILE"
        done
    else
        echo "- 📄 纯文档技能" >> "$REPORT_FILE"
    fi

    # 检查敏感信息（硬编码路径、API keys）
    sensitive_found=0
    if grep -r "/root/clawd" "$skill_dir" 2>/dev/null | grep -v "^Binary" | head -1 | grep -q .; then
        echo "- ⚠️  发现硬编码路径 \`/root/clawd\`" >> "$REPORT_FILE"
        sensitive_found=1
    fi

    if grep -rE "(API_KEY|SECRET_KEY|api_key|secret_key)" "$skill_dir" --include="*.md" --include="*.py" --include="*.sh" 2>/dev/null | head -1 | grep -q .; then
        echo "- ⚠️  发现敏感信息关键词" >> "$REPORT_FILE"
        sensitive_found=1
    fi

    # 评估是否可以发布
    echo "" >> "$REPORT_FILE"
    echo "**发布评估:** " >> "$REPORT_FILE"

    can_publish=1
    reasons=""

    if ! grep -q "^name:" "${skill_dir}SKILL.md"; then
        can_publish=0
        reasons="[缺少 name] "
    fi

    if ! grep -q "^description:" "${skill_dir}SKILL.md"; then
        can_publish=0
        reasons="${reasons}[缺少 description] "
    fi

    if [ "$sensitive_found" -eq 1 ]; then
        can_publish=0
        reasons="${reasons}[需要清理硬编码路径或敏感信息] "
    fi

    if [ "$can_publish" -eq 1 ]; then
        echo "✅ **可以发布**" >> "$REPORT_FILE"
    else
        echo "❌ **需要修复**: $reasons" >> "$REPORT_FILE"
    fi

    echo "" >> "$REPORT_FILE"
    echo "---" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
done

echo "分析完成！报告已保存到: $REPORT_FILE"
