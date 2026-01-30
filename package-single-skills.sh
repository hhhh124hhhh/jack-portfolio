#!/bin/bash

# 单个 Skills 打包脚本
# 为每个 skill 创建独立的压缩包

set -e

echo "=========================================="
echo "📦 单个 Skills 打包工具"
echo "=========================================="
echo ""

# 配置
OUTPUT_DIR="dist-skills/single-skills"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Skills 列表
declare -A SKILLS=(
  ["chatgpt-prompts"]="chatgpt-prompts-skill|143k+精选ChatGPT提示词"
  ["job-interviewer"]="job-interviewer-skill|面试模拟器"
  ["resume-builder"]="resume-builder-skill|简历生成器"
  ["ai-music-prompts"]="skills/ai-music-prompts|AI音乐生成(中文优化)"
  ["calendar"]="skills/calendar|日历管理"
  ["clawdbot-security-check"]="skills/clawdbot-security-check|安全审计"
  ["prompt-learning-assistant"]="skills/prompt-learning-assistant|58+技术学习"
  ["prompt-optimizer"]="skills/prompt-optimizer|提示词优化"
  ["x-trends"]="skills/x-trends|X热门话题"
  ["twitter-search"]="skills/twitter-search-skill|Twitter搜索(需API)"
  ["tiktok-ai-model-generator"]="skills/tiktok-ai-model-generator|TikTok AI模型生成"
)

# 打包函数
package_single_skill() {
  local skill_name=$1
  local skill_path=$2
  local skill_desc=$3
  local temp_dir="$OUTPUT_DIR/$skill_name"

  echo "📦 打包: $skill_name"
  echo "   描述: $skill_desc"

  # 创建临时目录
  rm -rf "$temp_dir"
  mkdir -p "$temp_dir"

  # 复制 SKILL.md
  if [ -f "$skill_path/SKILL.md" ]; then
    cp "$skill_path/SKILL.md" "$temp_dir/"
  fi

  # 复制参考资料
  if [ -d "$skill_path/references" ]; then
    cp -r "$skill_path/references" "$temp_dir/"
  fi

  # 复制脚本
  if [ -d "$skill_path/scripts" ]; then
    cp -r "$skill_path/scripts" "$temp_dir/"
  fi

  # 复制示例
  if [ -d "$skill_path/examples" ]; then
    cp -r "$skill_path/examples" "$temp_dir/"
  fi

  # 创建说明文件
  cat > "$temp_dir/README.txt" << README
═══════════════════════════════════════════════════════════
         $skill_name - Clawdbot Skill
═══════════════════════════════════════════════════════════

📝 描述: $skill_desc

🚀 快速安装:
─────────────────────────────────────────────────────────
方法1 - 复制到 clawdbot skills 目录:
  cp -r $skill_name ~/.clawdbot/skills/

方法2 - 使用 ClawdHub:
  clawdhub install $skill_name

─────────────────────────────────────────────────────────

📖 使用方法:
─────────────────────────────────────────────────────────
安装后，在 Clawdbot 中直接使用此 skill。
查看 SKILL.md 了解详细使用方法。

─────────────────────────────────────────────────────────

📦 包含文件:
  - SKILL.md (技能定义)
  - references/ (参考资料，如有)
  - scripts/ (脚本文件，如有)
  - examples/ (示例，如有)

═══════════════════════════════════════════════════════════
打包时间: $(date +%Y-%m-%d)
版本: 1.0.0
═══════════════════════════════════════════════════════════
README

  # 创建压缩包
  tar -czf "${OUTPUT_DIR}/${skill_name}.tar.gz" -C "$OUTPUT_DIR" "$skill_name"

  # 清理临时目录
  rm -rf "$temp_dir"

  # 显示压缩包信息
  size=$(du -sh "${OUTPUT_DIR}/${skill_name}.tar.gz" | cut -f1)
  echo "   ✅ 已创建: ${skill_name}.tar.gz ($size)"
  echo ""
}

# 打包所有 skills
count=0
for skill_name in "${!SKILLS[@]}"; do
  IFS='|' read -r skill_path skill_desc <<< "${SKILLS[$skill_name]}"

  if [ -d "$skill_path" ]; then
    package_single_skill "$skill_name" "$skill_path" "$skill_desc"
    count=$((count+1))
  fi
done

echo "=========================================="
echo "✅ 单独打包完成！"
echo "=========================================="
echo ""
echo "📁 输出目录: $OUTPUT_DIR"
echo "📦 已打包: $count 个 skills"
echo ""

# 列出所有压缩包
echo "📋 压缩包列表:"
echo ""
ls -lh "$OUTPUT_DIR"/*.tar.gz 2>/dev/null | awk '{printf "   %-40s %s\n", $9, $5}'
echo ""

# 创建索引文件
cat > "$OUTPUT_DIR/INDEX.txt" << 'INDEXEOF'
╔══════════════════════════════════════════════════════════════╗
║           Clawdbot Skills - 单独打包索引                     ║
╚══════════════════════════════════════════════════════════════╝

INDEXEOF

for skill_name in "${!SKILLS[@]}"; do
  IFS='|' read -r skill_path skill_desc <<< "${SKILLS[$skill_name]}"

  if [ -d "$skill_path" ]; then
    size=$(du -sh "${OUTPUT_DIR}/${skill_name}.tar.gz" 2>/dev/null | cut -f1)
    echo "✅ $skill_name" >> "$OUTPUT_DIR/INDEX.txt"
    echo "   描述: $skill_desc" >> "$OUTPUT_DIR/INDEX.txt"
    echo "   大小: $size" >> "$OUTPUT_DIR/INDEX.txt"
    echo "" >> "$OUTPUT_DIR/INDEX.txt"
  fi
done

cat >> "$OUTPUT_DIR/INDEX.txt" << 'INDEXEND'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 使用方法:
─────────────────────────────────────────────────────────
1. 查看 INDEX.txt 选择需要的 skill
2. 下载对应的 .tar.gz 文件
3. 解压: tar -xzf skill-name.tar.gz
4. 复制: cp -r skill-name ~/.clawdbot/skills/

或者直接:
   tar -xzf skill-name.tar.gz -C ~/.clawdbot/skills/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 推荐下载:
─────────────────────────────────────────────────────────
新手推荐:
  • chatgpt-prompts.tar.gz - 143k+ 精选提示词
  • prompt-learning-assistant.tar.gz - 系统化学习
  • job-interviewer.tar.gz - 面试练习

内容创作者:
  • ai-music-prompts.tar.gz - AI 音乐生成
  • prompt-optimizer.tar.gz - 提示词优化

开发者:
  • clawdbot-security-check.tar.gz - 安全审计
  • x-trends.tar.gz - 热门话题

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 打包时间: 2026-01-30
📦 版本: 1.0.0
🔗 GitHub: https://github.com/hhhh124hhhh/Clawdbot-Skills-Converter

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INDEXEND

echo "📄 已创建: INDEX.txt"
echo ""

echo "💡 下一步:"
echo "   1. 查看: cat $OUTPUT_DIR/INDEX.txt"
echo "   2. 选择需要的 skill"
echo "   3. 分享对应的 .tar.gz 文件"
echo ""
