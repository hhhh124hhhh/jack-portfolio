#!/bin/bash

# 批量审核 Skills 使用 Coding Agent
# 将 40 个 skills 分批审核，每批 5 个

set -e

SKILLS_DIR="/root/clawd/dist/skills"
OUTPUT_DIR="/root/clawd/data/skills-audit"
BATCH_SIZE=5

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 获取所有 skill 文件并排序
readarray -t SKILLS < <(ls "$SKILLS_DIR"/*.skill | sort)

TOTAL=${#SKILLS[@]}
echo "🔍 开始审核 $TOTAL 个 Skills"
echo "================================"
echo ""

# 分批处理
for ((i=0; i<TOTAL; i+=BATCH_SIZE)); do
  BATCH_NUM=$((i/BATCH_SIZE + 1))
  BATCH_END=$((i+BATCH_SIZE))
  if [ $BATCH_END -gt $TOTAL ]; then
    BATCH_END=$TOTAL
  fi

  # 获取当前批次的 skill 文件
  BATCH_SKILLS=("${SKILLS[@]:i:BATCH_SIZE}")
  BATCH_FILES=$(printf '%s\n' "${BATCH_SKILLS[@]}" | paste -sd ' ')

  echo "📦 启动第 $BATCH_NUM 批审核 (Skills $((i+1))-$BATCH_END)"

  # 创建任务描述
  TASK_FILE="/tmp/audit-batch-$BATCH_NUM.txt"
  cat > "$TASK_FILE" <<EOF
你是一个专业的 Skill 审核专家。请审核以下 5 个 Clawdbot Skill 文件，并生成详细的质量评估报告。

**审核标准（100分制）**：
1. 🎯 实用性 (30%): 提示词是否具体？是否有明确的使用场景？是否包含必要的参数和步骤？
2. 🎨 创新性 (20%): 提示词是否独特？是否有新颖的角度或方法？
3. 📖 完整性 (20%): Skill 文档是否完整？是否包含描述、标签、示例？
4. 🔥 热度 (25%): 从文件名判断主题热度（如 "50 viral", "best practices", "ultimate guide" 等）
5. 👨‍💼 专业性 (5%): 是否来自权威来源（IBM、Google、Reddit 社区等）

**审核流程**：
1. 解压每个 skill 文件（使用 unzip）
2. 读取 SKILL.md 内容
3. 提取 Prompt 内容
4. 根据标准评分并给出评级
5. 生成 JSON 格式的评估报告

**评级标准**：
- A+ (90-100): $9.99
- A (85-89): $4.99
- B+ (80-84): $2.99
- B (70-79): $1.99
- C+ (60-69): $0.99
- C (50-59): 免费
- D (0-49): 不收录

**输出要求**：
生成 JSON 格式的报告，保存到 $OUTPUT_DIR/audit-batch-$BATCH_NUM.json
报告格式：
```json
{
  "batch": $BATCH_NUM,
  "skills": [
    {
      "filename": "xxx.skill",
      "title": "从 SKILL.md 提取",
      "prompt": "提取的 Prompt 内容",
      "scores": {
        "实用性": 0,
        "创新性": 0,
        "完整性": 0,
        "热度": 0,
        "专业性": 0
      },
      "totalScore": 0,
      "rating": "A+",
      "suggestedPrice": 9.99,
      "issues": ["发现的问题列表"],
      "recommendations": ["改进建议列表"]
    }
  ],
  "summary": {
    "total": 5,
    "aPlus": 0,
    "a": 0,
    "bPlus": 0,
    "b": 0,
    "cPlus": 0,
    "c": 0,
    "d": 0
  }
}
```

**待审核的文件**：
$BATCH_FILES

请仔细审核每个 skill，给出公正的评分和详细的建议。完成后，将报告保存到指定位置。
EOF

  # 启动子代理执行审核任务
  clawdbot sessions_spawn \
    --task "$(cat $TASK_FILE)" \
    --label "skills-audit-batch-$BATCH_NUM" \
    --timeout-seconds 600 \
    --cleanup keep

  # 删除临时文件
  rm -f "$TASK_FILE"

  # 等待一段时间，避免同时启动太多子代理
  sleep 10
done

echo ""
echo "================================"
echo "✅ 所有审核任务已启动"
echo "📊 结果将保存到 $OUTPUT_DIR/"
echo ""
echo "使用以下命令查看子代理状态："
echo "clawdbot sessions_list --limit 20"
echo ""
