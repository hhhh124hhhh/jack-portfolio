#!/bin/bash
#
# 改进的提示词收集和转换工作流
# 使用 awesome-chatgpt-prompts 专用解析器和 LLM 辅助验证
#

set -e  # 遇到错误立即退出

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="/root/clawd/data/prompts/awesome-chatgpt"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_DIR="${DATA_DIR}/${TIMESTAMP}"

# 创建输出目录
mkdir -p "${OUTPUT_DIR}"

# 日志文件
LOG_FILE="${OUTPUT_DIR}/workflow.log"
exec 1> >(tee -a "${LOG_FILE}")
exec 2>&1

echo "=========================================="
echo "改进的提示词收集和转换工作流"
echo "开始时间: $(date)"
echo "=========================================="
echo ""

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 阶段 1: 从 awesome-chatgpt-prompts 提取
log_info "阶段 1: 从 awesome-chatgpt-prompts 提取提示词..."

RAW_OUTPUT="${OUTPUT_DIR}/01_raw_prompts.json"
python3 "${SCRIPT_DIR}/improved-prompt-extractor.py" \
    --output "${RAW_OUTPUT}" \
    --no-llm-validation

if [ ! -f "${RAW_OUTPUT}" ]; then
    log_error "提取失败，未生成输出文件"
    exit 1
fi

RAW_COUNT=$(jq '. | length' "${RAW_OUTPUT}")
log_success "✅ 提取了 ${RAW_COUNT} 个提示词"
echo ""

# 阶段 2: LLM 质量验证
log_info "阶段 2: 使用 LLM 验证提示词质量..."

VALIDATED_OUTPUT="${OUTPUT_DIR}/02_validated_prompts.json"
MIN_SCORE=35  # 最低总分要求（满分 50）

python3 "${SCRIPT_DIR}/llm-prompt-validator.py" \
    --input "${RAW_OUTPUT}" \
    --output "${VALIDATED_OUTPUT}" \
    --min-score ${MIN_SCORE} \
    --limit 50 \
    --batch-size 5

if [ ! -f "${VALIDATED_OUTPUT}" ]; then
    log_warning "LLM 验证失败，使用原始数据继续"
    VALIDATED_OUTPUT="${RAW_OUTPUT}"
else
    VALIDATED_COUNT=$(jq '. | length' "${VALIDATED_OUTPUT}")
    log_success "✅ 验证了 ${VALIDATED_COUNT} 个高质量提示词（score >= ${MIN_SCORE}）"
fi
echo ""

# 阶段 3: 转换为 Skills
log_info "阶段 3: 将高质量提示词转换为 Skills..."

# 使用现有的转换脚本
CONVERT_SCRIPT="/root/clawd/skills/prompt-to-skill-converter/scripts/convert-prompts-to-skills.py"

if [ ! -f "${CONVERT_SCRIPT}" ]; then
    log_warning "转换脚本不存在，跳过阶段 3"
else
    # 准备输入格式（将 LLM 验证结果转换为转换脚本期望的格式）
    CONVERT_INPUT="${OUTPUT_DIR}/03_for_conversion.jsonl"

    jq -r '.[] | {
        prompt: .prompt,
        role: .role,
        quality_score: (.total_score * 2),
        source: "awesome-chatgpt-prompts",
        validated: true
    } | @json' "${VALIDATED_OUTPUT}" > "${CONVERT_INPUT}"

    python3 "${CONVERT_SCRIPT}" \
        --input "${CONVERT_INPUT}" \
        --quality-threshold 70 \
        --output-dir "/root/clawd/skills"

    log_success "✅ Skills 转换完成"
fi
echo ""

# 阶段 4: 生成最终报告
log_info "阶段 4: 生成最终报告..."

REPORT_FILE="${OUTPUT_DIR}/final_report.txt"

cat > "${REPORT_FILE}" << EOF
========================================
改进的提示词收集和转换工作流报告
========================================

执行时间: $(date)
工作流目录: ${OUTPUT_DIR}

----------------------------------------
阶段统计
----------------------------------------

阶段 1: 提取
- 数据源: awesome-chatgpt-prompts
- 提取数量: ${RAW_COUNT}
- 输出文件: ${RAW_OUTPUT}

阶段 2: LLM 验证
- 最低分数要求: ${MIN_SCORE}/50
- 验证数量: ${VALIDATED_COUNT:-N/A}
- 输出文件: ${VALIDATED_OUTPUT}

----------------------------------------
质量分布
----------------------------------------

EOF

# 添加质量分布统计（如果存在验证结果）
if [ -f "${VALIDATED_OUTPUT}" ] && [ "${VALIDATED_OUTPUT}" != "${RAW_OUTPUT}" ]; then
    # 统计各分数段的数量
    echo "分数分布:" >> "${REPORT_FILE}"
    echo "  45-50: $(jq '[.[] | select(.total_score >= 45)] | length' ${VALIDATED_OUTPUT})" >> "${REPORT_FILE}"
    echo "  40-44: $(jq '[.[] | select(.total_score >= 40 and .total_score < 45)] | length' ${VALIDATED_OUTPUT})" >> "${REPORT_FILE}"
    echo "  35-39: $(jq '[.[] | select(.total_score >= 35 and .total_score < 40)] | length' ${VALIDATED_OUTPUT})" >> "${REPORT_FILE}"
    echo "  0-34:  $(jq '[.[] | select(.total_score < 35)] | length' ${VALIDATED_OUTPUT})" >> "${REPORT_FILE}"
    echo "" >> "${REPORT_FILE}"

    # 维度平均分
    echo "各维度平均分 (满分 10):" >> "${REPORT_FILE}"
    for dim in clarity completeness practicality innovation reusability; do
        avg=$(jq -r "[.[].${dim} | numbers] | add / length" "${VALIDATED_OUTPUT}")
        printf "  %-15s: %.2f\n" "${dim}" "${avg}" >> "${REPORT_FILE}"
    done
fi

# Top 10 提示词
cat >> "${REPORT_FILE}" << EOF

----------------------------------------
Top 10 高质量提示词
----------------------------------------

EOF

if [ -f "${VALIDATED_OUTPUT}" ]; then
    jq -r 'sort_by(.total_score) | reverse | .[:10][] | "\(.total_score)/50 - \(.role)\n  \(.prompt[:150]...")' "${VALIDATED_OUTPUT}" >> "${REPORT_FILE}"
fi

log_success "✅ 报告生成完成: ${REPORT_FILE}"
echo ""

# 打印摘要
cat << EOF

========================================
📊 工作流摘要
========================================

✅ 提取提示词: ${RAW_COUNT}
✅ 高质量提示词: ${VALIDATED_COUNT:-N/A}
📁 工作流目录: ${OUTPUT_DIR}
📄 最终报告: ${REPORT_FILE}

========================================

EOF

# 可选：发送通知到 Slack/Feishu
# 这里可以根据需要添加通知逻辑

log_success "🎉 工作流执行完成！"
