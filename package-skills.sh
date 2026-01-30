#!/bin/bash

# Clawdbot Skills 打包脚本
# 用于打包所有 skills 以便分享

set -e

echo "=========================================="
echo "📦 Clawdbot Skills 打包工具"
echo "=========================================="
echo ""

# 配置
PACKAGE_DIR="dist-skills"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
PACKAGE_NAME="clawdbot-skills-$TIMESTAMP"
FINAL_PACKAGE="$PACKAGE_DIR/$PACKAGE_NAME"

# 创建输出目录
echo "📁 创建输出目录..."
mkdir -p "$PACKAGE_DIR"
rm -rf "$FINAL_PACKAGE"
mkdir -p "$FINAL_PACKAGE"

# 打包函数
package_skill() {
  local skill_name=$1
  local skill_path=$2
  local output_path="$FINAL_PACKAGE/$skill_name"

  echo "📦 打包: $skill_name"

  # 创建 skill 目录
  mkdir -p "$output_path"

  # 复制 SKILL.md（必需）
  if [ -f "$skill_path/SKILL.md" ]; then
    cp "$skill_path/SKILL.md" "$output_path/"
    echo "   ✅ SKILL.md"
  else
    echo "   ❌ 缺少 SKILL.md"
    return 1
  fi

  # 复制参考资料（如果有）
  if [ -d "$skill_path/references" ]; then
    cp -r "$skill_path/references" "$output_path/"
    file_count=$(find "$skill_path/references" -type f 2>/dev/null | wc -l)
    echo "   📚 参考资料: $file_count 个文件"
  fi

  # 复制脚本（如果有）
  if [ -d "$skill_path/scripts" ]; then
    cp -r "$skill_path/scripts" "$output_path/"
    script_count=$(find "$skill_path/scripts" -type f 2>/dev/null | wc -l)
    echo "   🔧 脚本: $script_count 个"
  fi

  # 复制示例（如果有）
  if [ -d "$skill_path/examples" ]; then
    cp -r "$skill_path/examples" "$output_path/"
    echo "   💡 示例: 已包含"
  fi

  echo ""
}

# 清空清单文件
> "$FINAL_PACKAGE/.skills-list"

# 打包所有 skills
echo "🚀 开始打包所有 skills..."
echo ""

# 立即可用的 skills
echo "=== 立即可用的 Skills ==="
echo ""

package_skill "chatgpt-prompts" "chatgpt-prompts-skill"
package_skill "job-interviewer" "job-interviewer-skill"
package_skill "resume-builder" "resume-builder-skill"
package_skill "ai-music-prompts" "skills/ai-music-prompts"
package_skill "calendar" "skills/calendar"
package_skill "clawdbot-security-check" "skills/clawdbot-security-check"
package_skill "prompt-learning-assistant" "skills/prompt-learning-assistant"
package_skill "prompt-optimizer" "skills/prompt-optimizer"
package_skill "x-trends" "skills/x-trends"

# 需要配置的 skills
echo "=== 需要配置的 Skills ==="
echo ""

package_skill "twitter-search" "skills/twitter-search-skill"
package_skill "tiktok-ai-model-generator" "skills/tiktok-ai-model-generator"

# 统计
total_skills=$(ls -1 "$FINAL_PACKAGE" 2>/dev/null | wc -l)
echo "✅ 已打包 $total_skills 个 skills"
echo ""

# 创建 README
echo "📝 创建 README.md..."
cat > "$FINAL_PACKAGE/README.md" << 'EOFREADME'
# Clawdbot Skills Collection

完整的 Clawdbot Skills 集合，共 11 个高质量技能。

## 📊 包含内容

### ✅ 立即可用（9个）

1. **chatgpt-prompts** - 143k+ 精选 ChatGPT 提示词
2. **ai-music-prompts** - AI 音乐生成提示词（含中文优化）
3. **prompt-learning-assistant** - 58+ 提示词技术系统化学习
4. **prompt-optimizer** - 提示词优化工具
5. **job-interviewer** - 面试模拟器
6. **resume-builder** - 简历生成器
7. **x-trends** - X/Twitter 热门话题
8. **calendar** - 日历管理
9. **clawdbot-security-check** - 安全审计

### ⚠️ 需要配置（2个）

10. **twitter-search** - 需要 Twitter API key
11. **tiktok-ai-model-generator** - 工作流指导（第三方工具可选）

## 🚀 快速安装

### 方法 1：使用安装脚本（推荐）

```bash
./install.sh
```

### 方法 2：手动安装

```bash
# 复制单个 skill
cp -r chatgpt-prompts ~/.clawdbot/skills/

# 复制所有 skills
cp -r */ ~/.clawdbot/skills/
```

## 📖 使用方法

安装后，在 Clawdbot 中直接使用：

```
你: "我需要练习软件工程师面试"
→ Clawdbot 自动加载 job-interviewer skill

你: "帮我生成一个音乐提示词"
→ Clawdbot 自动加载 ai-music-prompts skill
```

## 📋 Skill 详情

查看每个 skill 目录中的 `SKILL.md` 文件了解详细使用方法。

## 🔗 相关链接

- ClawdHub: https://clawdhub.com
- GitHub: https://github.com/hhhh124hhhh/Clawdbot-Skills-Converter

## 📝 许可证

MIT License
EOFREADME

echo "   ✅ README.md"
echo ""

# 创建清单
echo "📋 创建 SKILLS_MANIFEST.md..."
cat > "$FINAL_PACKAGE/SKILLS_MANIFEST.md" << 'EOFMANIFEST'
# Clawdbot Skills 清单

**总数量**: 11 个
**立即可用**: 9 个 (82%)
**需要配置**: 2 个 (18%)

---

## ✅ 立即可用的 Skills

1. **chatgpt-prompts** - 知识库，143k+ stars
2. **ai-music-prompts** - 3500+ 行，中文优化
3. **prompt-learning-assistant** - 58+ 技术系统化学习
4. **prompt-optimizer** - 提示词优化工具
5. **job-interviewer** - 面试模拟器
6. **resume-builder** - 简历生成器
7. **x-trends** - X 热门话题（无需 API）
8. **calendar** - 日历管理
9. **clawdbot-security-check** - 安全审计

## ⚠️ 需要配置的 Skills

10. **twitter-search** - 需要 Twitter API（免费层可用）
11. **tiktok-ai-model-generator** - 工作流指导（第三方工具可选）

---

## 📊 质量指标

| 指标 | 结果 |
|------|------|
| 结构完整性 | 100% (11/11) |
| 元数据完整性 | 100% (11/11) |
| 内容丰富度 | 91% (10/11 优秀) |
| 即用性 | 82% (9/11) |
EOFMANIFEST

echo "   ✅ SKILLS_MANIFEST.md"
echo ""

# 创建安装脚本
echo "🔧 创建安装脚本..."
cat > "$FINAL_PACKAGE/install.sh" << 'EOFINSTALL'
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
EOFINSTALL

chmod +x "$FINAL_PACKAGE/install.sh"
echo "   ✅ install.sh"
echo ""

# 统计信息
echo "📊 打包统计:"
total_size=$(du -sh "$FINAL_PACKAGE" 2>/dev/null | cut -f1)
total_files=$(find "$FINAL_PACKAGE" -type f 2>/dev/null | wc -l)
skill_md_count=$(find "$FINAL_PACKAGE" -name "SKILL.md" 2>/dev/null | wc -l)

echo "   📦 Skills 数量: $total_skills"
echo "   💾 总大小: $total_size"
echo "   📄 总文件数: $total_files"
echo "   📋 SKILL.md 文件: $skill_md_count"
echo ""

echo "=========================================="
echo "✅ 打包完成！"
echo "=========================================="
echo ""
echo "📁 输出目录: $FINAL_PACKAGE"
echo ""
echo "📋 包含文件:"
echo "   - README.md (使用说明)"
echo "   - SKILLS_MANIFEST.md (技能清单)"
echo "   - install.sh (安装脚本)"
echo "   - 11 个 skill 目录"
echo ""
echo "💡 下一步:"
echo "   1. 查看: cd $FINAL_PACKAGE"
echo "   2. 阅读: cat README.md"
echo "   3. 安装: ./install.sh"
echo ""
