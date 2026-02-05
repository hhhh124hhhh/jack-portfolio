#!/bin/bash

# 批量发布手动创建的 Skills 到 ClawdHub

echo "============================================================"
echo "发布手动创建的 Skills 到 ClawdHub"
echo "============================================================"
echo ""

SKILLS_DIR="/root/clawd/skills/manual-prompts"
LOG_FILE="/root/clawd/logs/publish-manual-skills-$(date +%Y%m%d-%H%M%S).log"

# 创建日志目录
mkdir -p /root/clawd/logs

# 统计
total_skills=$(find "$SKILLS_DIR" -name "SKILL.md" | wc -l)
published_count=0
failed_count=0

echo "找到 $total_skills 个 Skills"
echo "日志: $LOG_FILE"
echo ""

# 遍历所有 Skills
for skill_dir in "$SKILLS_DIR"/*; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        echo "[$((published_count + failed_count + 1))/$total_skills] 发布: $skill_name"

        # 发布 Skill
        if clawdhub publish "$skill_dir" --version 1.0.0 >> "$LOG_FILE" 2>&1; then
            echo "  ✅ 成功"
            ((published_count++))
        else
            echo "  ❌ 失败 (查看日志: $LOG_FILE)"
            ((failed_count++))
        fi

        # 短暂延迟，避免请求过快
        sleep 2
    fi
done

echo ""
echo "============================================================"
echo "✅ 发布完成！"
echo "============================================================"
echo "总计: $total_skills 个 Skills"
echo "成功: $published_count 个"
echo "失败: $failed_count 个"
echo "成功率: $((published_count * 100 / total_skills))%"
echo ""
echo "日志: $LOG_FILE"
