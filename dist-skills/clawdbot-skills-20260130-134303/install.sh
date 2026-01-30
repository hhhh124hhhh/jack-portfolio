#!/bin/bash

# Clawdbot Skills 批量安装脚本

set -e

echo "=========================================="
echo "🚀 Clawdbot Skills 安装向导"
echo "=========================================="
echo ""

# 检测安装路径
CLAWDBOT_DIR="$HOME/.clawdbot/skills"
if [ ! -d "$CLAWDBOT_DIR" ]; then
  CLAWDBOT_DIR="./skills"
  mkdir -p "$CLAWDBOT_DIR"
fi

echo "📁 安装路径: $CLAWDBOT_DIR"
echo ""

# 询问安装方式
echo "请选择安装方式："
echo "1) 安装所有 skills（推荐）"
echo "2) 选择性安装"
echo "3) 仅安装立即可用的 skills（9个）"
echo ""
read -p "请输入选项 (1-3): " choice

case $choice in
  1)
    echo ""
    echo "📦 安装所有 skills..."
    for skill_dir in */; do
      if [ -f "$skill_dir/SKILL.md" ]; then
        skill_name=$(basename "$skill_dir")
        echo "   ✅ $skill_name"
        cp -r "$skill_dir" "$CLAWDBOT_DIR/"
      fi
    done
    ;;
  2)
    echo ""
    echo "可用的 skills:"
    i=1
    declare -A skill_map
    for skill_dir in */; do
      if [ -f "$skill_dir/SKILL.md" ]; then
        skill_name=$(basename "$skill_dir")
        name=$(grep "^name:" "$skill_dir/SKILL.md" | cut -d':' -f2 | xargs)
        echo "$i) $skill_name"
        skill_map[$i]="$skill_name"
        i=$((i+1))
      fi
    done
    echo ""
    read -p "请输入要安装的 skill 编号（多个用空格分隔）: " selections
    echo ""
    echo "📦 安装选定的 skills..."
    for selection in $selections; do
      skill="${skill_map[$selection]}"
      if [ -d "$skill" ]; then
        echo "   ✅ $skill"
        cp -r "$skill" "$CLAWDBOT_DIR/"
      fi
    done
    ;;
  3)
    echo ""
    echo "📦 仅安装立即可用的 skills..."
    instant_skills=(
      "chatgpt-prompts"
      "ai-music-prompts"
      "prompt-learning-assistant"
      "prompt-optimizer"
      "job-interviewer"
      "resume-builder"
      "x-trends"
      "calendar"
      "clawdbot-security-check"
    )
    for skill in "${instant_skills[@]}"; do
      if [ -d "$skill" ]; then
        echo "   ✅ $skill"
        cp -r "$skill" "$CLAWDBOT_DIR/"
      fi
    done
    ;;
  *)
    echo "❌ 无效选项"
    exit 1
    ;;
esac

echo ""
echo "=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo ""
echo "已安装到: $CLAWDBOT_DIR"
echo ""
echo "现在可以在 Clawdbot 中使用这些 skills 了！"
