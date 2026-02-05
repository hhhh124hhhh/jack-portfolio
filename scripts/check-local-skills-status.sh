#!/bin/bash
# 检查本地技能开发和发布状态

echo "=== 本地技能开发状态检查 ==="
echo ""

# 1. 统计各类技能数量
echo "📊 技能统计："
echo ""

# /root/clawd/ 下直接包含 SKILL.md 的目录（核心开发技能）
core_dev_count=$(find /root/clawd -maxdepth 1 -name "SKILL.md" -type f 2>/dev/null | wc -l)
echo "  核心开发目录: $core_dev_count 个"

# /root/clawd/*/ 目录下包含 SKILL.md 的（自定义技能）
custom_skills=$(for dir in /root/clawd/*/; do if [ -f "$dir/SKILL.md" ]; then echo "$(basename "$dir")"; fi; done | sort)
custom_count=$(echo "$custom_skills" | grep -v "^$" | wc -l)
echo "  自定义技能: $custom_count 个"

# /root/clawd/skills/ 下的官方技能
official_skills=$(ls /root/clawd/skills/ 2>/dev/null | grep -E "^[a-z].*-?[a-z]*$" | grep -v "\.md$" | grep -v "^dist$" | grep -v "^public$")
official_count=$(echo "$official_skills" | grep -v "^$" | wc -l)
echo "  官方技能库: $official_count 个"

# /root/clawd/dist/skills/ 下已转换的提示词技能
dist_count=$(ls /root/clawd/dist/skills/ 2>/dev/null | grep -v "\.skill$" | wc -l)
echo "  提示词转换: $dist_count 个"

echo ""
echo "📋 已发布到 ClawdHub 的技能："
echo ""

# 获取已发布的技能列表
published=$(clawdhub list --registry https://www.clawhub.ai/api 2>&1 | awk '{print $1}')
published_count=$(echo "$published" | grep -v "^$" | wc -l)
echo "  总数: $published_count 个"
echo ""

# 显示已发布技能列表
echo "  已发布技能列表："
echo "$published" | while read skill; do
  if [ -n "$skill" ]; then
    echo "    - $skill"
  fi
done

echo ""
echo "🔍 核心开发技能详情："
echo ""

if [ $custom_count -gt 0 ]; then
  echo "$custom_skills" | while read skill; do
    if [ -n "$skill" ] && [ "$skill" != "skills-bundle" ]; then
      skill_dir="/root/clawd/$skill"
      if [ -f "$skill_dir/SKILL.md" ]; then
        # 提取技能描述
        desc=$(grep "^description:" "$skill_dir/SKILL.md" | head -1 | sed 's/description: //')
        name=$(grep "^name:" "$skill_dir/SKILL.md" | head -1 | sed 's/name: //')

        # 检查是否已发布
        is_published=0
        if echo "$published" | grep -q "^$skill$"; then
          is_published=1
        fi

        status="❌ 未发布"
        if [ $is_published -eq 1 ]; then
          status="✅ 已发布"
        fi

        echo "  $status | $name ($skill)"
        if [ -n "$desc" ] && [ "$desc" != "description:" ]; then
          echo "    $desc"
        fi
        echo ""
      fi
    fi
  done
else
  echo "  无自定义开发技能"
fi

echo ""
echo "⚠️  未发布的核心技能："
echo ""

unpublished=0
echo "$custom_skills" | while read skill; do
  if [ -n "$skill" ] && [ "$skill" != "skills-bundle" ]; then
    if ! echo "$published" | grep -q "^$skill$"; then
      if [ -f "/root/clawd/$skill/SKILL.md" ]; then
        name=$(grep "^name:" "/root/clawd/$skill/SKILL.md" | head -1 | sed 's/name: //')
        echo "  - $skill: $name"
        unpublished=$((unpublished + 1))
      fi
    fi
  fi
done

echo ""
echo "📦 dist/skills/ 提示词技能（待发布）："
echo ""
echo "  共 $dist_count 个提示词转换技能"
echo "  这些通常不发布到 ClawdHub（数量多，内容相似）"
echo ""
echo "  示例技能："
ls /root/clawd/dist/skills/ 2>/dev/null | grep -v "\.skill$" | head -10 | while read skill; do
  if [ -n "$skill" ]; then
    echo "    - $skill"
  fi
done

echo ""
echo "=== 总结 ==="
echo ""
echo "✅ 已发布到 ClawdHub: $published_count 个"
echo "🔧 核心开发技能: $custom_count 个"
echo "📚 官方技能库: $official_count 个"
echo "🔄 提示词转换: $dist_count 个"
echo ""
