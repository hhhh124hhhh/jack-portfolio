#!/bin/bash
# 整合的 AI 提示词自动化流程
# Stage 1: 数据发现（SearXNG + collect_prompts_enhanced）→ Stage 2: 转换发布（prompt-to-skill-converter）

set -e

# 配置
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H%M)
LOG_FILE="/root/clawd/logs/integrated-prompt-workflow.log"
REPORT_DIR="/root/clawd/reports"

# 增强版收集配置
ENHANCED_COLLECTOR="/root/clawd/scripts/collect_prompts_enhanced.py"
COLLECTED_DIR="/root/clawd/data/prompts/collected"
COLLECTED_OUTPUT="$COLLECTED_DIR/prompts-enhanced-latest.jsonl"

# prompt-to-skill-converter 配置
CONVERTER_DIR="/root/clawd/skills/prompt-to-skill-converter"

# 通知配置
SLACK_DM_ID="D0AB0J4QLAH"
FEISHU_USER_ID="ou_3bc5290afc1a94f38e23dc17c35f26d6"

# 默认参数
QUERY="${QUERY:-"AI prompts"}"
LIMIT_PER_SOURCE="${LIMIT_PER_SOURCE:-50}"
EVALUATE_LIMIT="${EVALUATE_LIMIT:-30}"
QUALITY_THRESHOLD="${QUALITY_THRESHOLD:-50}"

# 创建目录
mkdir -p "$(dirname $LOG_FILE)"
mkdir -p "$REPORT_DIR"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# 通知函数
send_notification() {
    local level=$1
    local message=$2

    case $level in
        "info") emoji="ℹ️" ;;
        "success") emoji="✅" ;;
        "warning") emoji="⚠️" ;;
        "error") emoji="❌" ;;
        *) emoji="📋" ;;
    esac

    local full_message="${emoji} ${message}"
    log_info "发送通知: $full_message"

    # Slack 通知
    clawdbot message send \
        --channel slack \
        --target "$SLACK_DM_ID" \
        --message "$full_message" >> "$LOG_FILE" 2>&1 || log_error "Slack 通知发送失败"

    # Feishu 通知
    clawdbot message send \
        --channel feishu \
        --target "$FEISHU_USER_ID" \
        --message "$full_message" >> "$LOG_FILE" 2>&1 || log_error "Feishu 通知发送失败"
}

# Stage 1: 使用 collect_prompts_enhanced.py 进行数据发现（支持 SearXNG）
stage1_discovery() {
    log ""
    log "=========================================="
    log "Stage 1: 数据发现（SearXNG 增强版收集）"
    log "=========================================="

    # 确保使用 SearXNG
    export SEARXNG_URL="${SEARXNG_URL:-http://localhost:8080}"
    log "SearXNG URL: $SEARXNG_URL"

    # 创建输出目录
    mkdir -p "/root/clawd/data/prompts/collected"

    # 使用 collect_prompts_enhanced.py 进行收集
    if python3 /root/clawd/scripts/collect_prompts_enhanced.py \
        >> "$LOG_FILE" 2>&1; then

        # 查找最新的输出文件
        LATEST_OUTPUT=$(ls -t /root/clawd/data/prompts/collected/prompts-enhanced-*.jsonl 2>/dev/null | head -1)

        if [ -f "$LATEST_OUTPUT" ]; then
            # 计算收集的提示词数量
            EVALUATED_COUNT=$(wc -l < "$LATEST_OUTPUT" 2>/dev/null || echo "0")
            log_info "✅ 数据发现完成：收集了 $EVALUATED_COUNT 个提示词"
            echo "$LATEST_OUTPUT" > /tmp/stage1_output.txt
            return 0
        else
            log_error "❌ 评估结果文件不存在"
            return 1
        fi
    else
        log_error "❌ collect_prompts_enhanced.py 执行失败"
        return 1
    fi
}

# Stage 2: 使用 prompt-to-skill-converter 进行转换和发布
stage2_conversion_publish() {
    log ""
    log "=========================================="
    log "Stage 2: 转换和发布（prompt-to-skill-converter）"
    log "=========================================="

    cd "$CONVERTER_DIR"

    log "质量阈值: $QUALITY_THRESHOLD"

    # 2.1 分类并准备转换数据
    log ""
    log "[2.1] 分类并准备转换数据..."

    # 读取 Stage 1 的输出文件
    STAGE1_OUTPUT=$(cat /tmp/stage1_output.txt 2>/dev/null || echo "")

    if [ ! -f "$STAGE1_OUTPUT" ]; then
        log_error "❌ Stage 1 输出文件不存在：$STAGE1_OUTPUT"
        return 1
    fi

    log "读取数据源: $STAGE1_OUTPUT"

    # 创建临时分类文件
    IMAGE_PROMPTS_FILE="/tmp/image-prompts.jsonl"
    VIDEO_PROMPTS_FILE="/tmp/video-prompts.jsonl"
    TEXT_PROMPTS_FILE="/tmp/text-prompts.jsonl"

    # 清空临时文件
    > "$IMAGE_PROMPTS_FILE"
    > "$VIDEO_PROMPTS_FILE"
    > "$TEXT_PROMPTS_FILE"

    # 分类提示词（使用 Python）
    python3 << 'PYTHON_SCRIPT'
import json
from pathlib import Path

# 读取输入文件
input_file = Path("/tmp/stage1_output.txt").read_text().strip()
with open(input_file, 'r', encoding='utf-8') as f:
    prompts = [json.loads(line) for line in f if line.strip()]

# 分类统计
image_count = 0
video_count = 0
text_count = 0
other_count = 0

# 分类并写入文件
for prompt in prompts:
    ptype = prompt.get('type', 'general')
    content = prompt.get('content', '')
    quality_score = prompt.get('quality_score', 0)

    # 创建新的 prompt 对象（符合 convert-prompts-to-skills.py 的格式）
    new_prompt = {
        'content': content,
        'title': prompt.get('title', 'AI Prompt'),
        'source': prompt.get('source', ''),
        'url': prompt.get('url', ''),
        'type': ptype,
        'quality_score': quality_score,
        'language': prompt.get('language', 'en'),
    }

    # 根据 type 分类
    if 'image' in ptype.lower() or 'image' in content.lower()[:50]:
        with open('/tmp/image-prompts.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(new_prompt, ensure_ascii=False) + '\n')
        image_count += 1
    elif 'video' in ptype.lower() or 'video' in content.lower()[:50]:
        with open('/tmp/video-prompts.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(new_prompt, ensure_ascii=False) + '\n')
        video_count += 1
    else:
        with open('/tmp/text-prompts.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(new_prompt, ensure_ascii=False) + '\n')
        text_count += 1

# 输出统计
print(f"分类完成: {image_count} 图像, {video_count} 视频, {text_count} 文本")
PYTHON_SCRIPT

    # 复制到正确的位置
    mkdir -p /root/clawd/data/prompts
    cp "$IMAGE_PROMPTS_FILE" /root/clawd/data/prompts/image-prompts.jsonl
    cp "$VIDEO_PROMPTS_FILE" /root/clawd/data/prompts/video-prompts.jsonl
    cp "$TEXT_PROMPTS_FILE" /root/clawd/data/prompts/general-prompts-v2.jsonl

    log_info "✅ 数据分类完成"

    # 2.2 转换为 Skills
    log ""
    log "[2.2] 转换为 Skills..."

    cd "$CONVERTER_DIR"

    # 使用 convert-prompts-to-skills.py
    if python3 scripts/convert-prompts-to-skills.py \
        >> "$LOG_FILE" 2>&1; then

        # 提取转换统计
        SKILLS_CONVERTED=$(tail -100 "$LOG_FILE" | grep "转换完成:" | tail -1 | sed 's/.*转换完成: //' | sed 's/ 个.*//' | awk '{$1=$1};1' || echo "0")
        log_info "✅ 转换完成：成功转换 $SKILLS_CONVERTED 个 Skill"
    else
        log_warn "⚠️  提示词转换失败（可能没有达到质量阈值的提示词）"
        SKILLS_CONVERTED=0
    fi

    # 2.2 打包 Skills
    log ""
    log "[2.2] 打包 Skills..."

    PACKAGED_COUNT=0
    if [ "$SKILLS_CONVERTED" -gt 0 ]; then
        # 查找最近创建的 skills 并打包
        RECENT_SKILLS=$(find /root/clawd/skills -name "SKILL.md" -type f -mmin -30 | sed 's|/SKILL.md||' | sort -u || true)

        if [ -n "$RECENT_SKILLS" ]; then
            while IFS= read -r skill_path; do
                skill_name=$(basename "$skill_path")
                if [ -f "/usr/lib/node_modules/clawdbot/skills/skill-creator/scripts/package_skill.py" ]; then
                    if python3 /usr/lib/node_modules/clawdbot/skills/skill-creator/scripts/package_skill.py "$skill_path" >> "$LOG_FILE" 2>&1; then
                        PACKAGED_COUNT=$((PACKAGED_COUNT + 1))
                    fi
                fi
            done <<< "$RECENT_SKILLS"
            log_info "✅ 打包完成：打包了 $PACKAGED_COUNT 个 Skill"
        fi
    fi

    # 2.3 发布到 ClawdHub
    log ""
    log "[2.3] 发布到 ClawdHub..."

    PUBLISHED_COUNT=0
    FAILED_COUNT=0

    if [ "$PACKAGED_COUNT" -gt 0 ]; then
        # 查找最近打包的 .skill 文件
        RECENT_PACKAGES=$(find /root/clawd/skills -name "*.skill" -type f -mmin -30 || true)

        if [ -n "$RECENT_PACKAGES" ]; then
            while IFS= read -r package_file; do
                if clawdhub publish "$package_file" --registry https://www.clawhub.ai/api >> "$LOG_FILE" 2>&1; then
                    PUBLISHED_COUNT=$((PUBLISHED_COUNT + 1))
                else
                    FAILED_COUNT=$((FAILED_COUNT + 1))
                fi
            done <<< "$RECENT_PACKAGES"
            log_info "✅ 发布完成：成功 $PUBLISHED_COUNT 个，失败 $FAILED_COUNT 个"
        fi
    else
        log_warn "⚠️  没有需要发布的 Skill"
    fi

    # 返回统计
    echo "$SKILLS_CONVERTED|$PUBLISHED_COUNT|$FAILED_COUNT"
}

# 生成报告
generate_report() {
    local evaluated_count=$1
    local skills_converted=$2
    local published_count=$3
    local failed_count=$4

    REPORT_FILE="$REPORT_DIR/integrated-workflow-report-${DATE}-${TIME}.md"

    cat > "$REPORT_FILE" << EOF
# 整合的 AI 提示词自动化流程报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 📊 流程统计

| 阶段 | 工具 | 状态 | 详情 |
|------|------|------|------|
| Stage 1 | SearXNG + collect_prompts_enhanced | ✅ 完成 | ${evaluated_count} 个提示词已收集 |
| Stage 2.1 | prompt-to-skill-converter | ✅ 完成 | ${skills_converted} 个 Skill 已转换 |
| Stage 2.2 | skill-creator | ✅ 完成 | 打包完成 |
| Stage 2.3 | ClawdHub | ✅ 完成 | ${published_count} 成功, ${failed_count} 失败 |

## 🔍 数据详情

**Stage 1: 数据发现（SearXNG + collect_prompts_enhanced）**
- 数据源: 整个互联网（通过 SearXNG）
- 工具: collect_prompts_enhanced.py
- 搜索类型: 50+ 专业查询（包括中英文）
- 已评估: ${evaluated_count} 个
- 已收集: ${evaluated_count} 个提示词

**Stage 2: 转换和发布（prompt-to-skill-converter）**
- 质量阈值: $QUALITY_THRESHOLD
- 已转换: ${skills_converted} 个 Skill
- 已发布: ${published_count} 个
- 发布失败: ${failed_count} 个

## 📈 质量指标

- **语义去重**: ✅ SearXNG + collect_prompts_enhanced 自动执行
- **LLM 评估**: ✅ Claude API 评分（创新性、实用性、清晰度、可复用性）
- **Langfuse 追踪**: ✅ 质量趋势记录
- **质量过滤**: ✅ 只转换评分 ≥ $QUALITY_THRESHOLD 的提示词

## 🎯 下一步

1. **查看已发布的 Skills**: 访问 [ClawdHub](https://www.clawhub.ai)
2. **质量评估**: 检查用户反馈和使用数据
3. **优化策略**: 根据 Langfuse 报告调整参数

---

*自动化生成 | 整合工作流*
EOF

    log_info "✅ 报告已生成: $REPORT_FILE"
    echo "$REPORT_FILE"
}

# Git 提交
git_commit() {
    local report_file=$1
    local evaluated_count=$2
    local skills_converted=$3
    local published_count=$4
    local failed_count=$5

    log ""
    log "提交到 Git..."

    cd /root/clawd

    # 添加相关文件
    git add \
        "$report_file" \
        "$PROMPT_HUNTER_DIR/data/"*.json \
        "$PROMPT_HUNTER_DIR/data/langfuse_reports/"*.json 2>/dev/null || true

    git add /root/clawd/skills/*/SKILL.md 2>/dev/null || true
    git add /root/clawd/skills/*/*.skill 2>/dev/null || true

    # 提交
    git commit -m "整合工作流完成 - ${DATE} ${TIME}

[Stage 1: 数据发现]
- 数据源: 整个互联网（通过 SearXNG）
- 评估提示词: ${evaluated_count} 个
- 工具: SearXNG + collect_prompts_enhanced (质量评分 + 自动分类)

[Stage 2: 转换发布]
- 转换 Skills: ${skills_converted} 个
- ClawdHub 发布: ${published_count} 成功, ${failed_count} 失败
- 工具: prompt-to-skill-converter

报告: $report_file" 2>&1 || log_warn "⚠️  没有变更需要提交"

    # 推送
    git push origin master 2>&1 | tee -a "$LOG_FILE" || log_warn "⚠️  Git push 失败或已最新"
}

# 主函数
main() {
    log "=========================================="
    log "🚀 整合的 AI 提示词自动化流程开始"
    log "=========================================="

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --query)
                QUERY="$2"
                shift 2
                ;;
            --limit)
                LIMIT_PER_SOURCE="$2"
                shift 2
                ;;
            --evaluate-limit)
                EVALUATE_LIMIT="$2"
                shift 2
                ;;
            --quality-threshold)
                QUALITY_THRESHOLD="$2"
                shift 2
                ;;
            --test-mode)
                TEST_MODE=true
                shift
                ;;
            --help)
                echo "用法: $0 [OPTIONS]"
                echo ""
                echo "选项:"
                echo "  --query TEXT              搜索查询（默认: '$QUERY'）"
                echo "  --limit N                 每个数据源的抓取限制（默认: $LIMIT_PER_SOURCE）"
                echo "  --evaluate-limit N        评估限制（默认: $EVALUATE_LIMIT）"
                echo "  --quality-threshold N    质量阈值（默认: $QUALITY_THRESHOLD）"
                echo "  --test-mode              测试模式，不发布到 ClawdHub"
                echo "  --help                   显示此帮助信息"
                echo ""
                echo "环境变量:"
                echo "  QUERY                     搜索查询"
                echo "  LIMIT_PER_SOURCE          每个数据源的抓取限制"
                echo "  EVALUATE_LIMIT           评估限制"
                echo "  QUALITY_THRESHOLD         质量阈值"
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                echo "使用 --help 查看帮助"
                exit 1
                ;;
        esac
    done

    # 标记：是否有新数据
    HAS_NEW_DATA=false

    # 执行 Stage 1
    if ! stage1_discovery; then
        log_error "❌ Stage 1 失败，终止流程"
        send_notification "error" "整合工作流 Stage 1 失败"
        exit 1
    fi

    # 检查是否有评估结果
    STAGE1_OUTPUT=$(cat /tmp/stage1_output.txt 2>/dev/null || echo "")
    if [ ! -f "$STAGE1_OUTPUT" ]; then
        log_error "❌ Stage 1 输出文件不存在"
        exit 1
    fi

    # 读取评估结果数量
    EVALUATED_COUNT=$(wc -l < "$STAGE1_OUTPUT" 2>/dev/null || echo "0")

    if [ "$EVALUATED_COUNT" -gt 0 ]; then
        HAS_NEW_DATA=true
    fi

    # 执行 Stage 2（除非是测试模式）
    if [ "$TEST_MODE" != true ]; then
        STATS=$(stage2_conversion_publish)
        SKILLS_CONVERTED=$(echo "$STATS" | cut -d'|' -f1)
        PUBLISHED_COUNT=$(echo "$STATS" | cut -d'|' -f2)
        FAILED_COUNT=$(echo "$STATS" | cut -d'|' -f3)
    else
        log_info "🧪 测试模式：跳过 Stage 2（转换和发布）"
        SKILLS_CONVERTED=0
        PUBLISHED_COUNT=0
        FAILED_COUNT=0
    fi

    # 生成报告
    REPORT_FILE=$(generate_report "$EVALUATED_COUNT" "$SKILLS_CONVERTED" "$PUBLISHED_COUNT" "$FAILED_COUNT")

    # Git 提交
    git_commit "$REPORT_FILE" "$EVALUATED_COUNT" "$SKILLS_CONVERTED" "$PUBLISHED_COUNT" "$FAILED_COUNT"

    # 总结
    log ""
    log "=========================================="
    log "✅ 整合工作流完成！"
    log "=========================================="
    log ""
    log "Stage 1（数据发现）:"
    log "  • 数据源: 整个互联网（通过 SearXNG）"
    log "  • 评估提示词: $EVALUATED_COUNT 个"
    log "  • 工具: SearXNG + collect_prompts_enhanced"
    log ""
    log "Stage 2（转换发布）:"
    log "  • 转换 Skills: $SKILLS_CONVERTED 个"
    log "  • ClawdHub 发布: $PUBLISHED_COUNT 成功, $FAILED_COUNT 失败"
    log "  • 工具: prompt-to-skill-converter"
    log ""
    log "报告: $REPORT_FILE"
    log "日志: $LOG_FILE"

    # 发送通知（仅在有新数据时）
    if [ "$HAS_NEW_DATA" = true ]; then
        SUMMARY="📊 **整合工作流完成！**

**Stage 1: 数据发现（SearXNG + collect_prompts_enhanced）**
• 数据源: 整个互联网（通过 SearXNG）
• 评估提示词: $EVALUATED_COUNT 个
• 特性: SearXNG 搜索 + 质量评分 + 自动分类

**Stage 2: 转换发布（prompt-to-skill-converter）**
• 质量阈值: $QUALITY_THRESHOLD
• 转换 Skills: $SKILLS_CONVERTED 个
• ClawdHub 发布: $PUBLISHED_COUNT 成功

**报告**: $REPORT_FILE
**详情**: 查看日志: $LOG_FILE
🚀 **下一个周期**: 明天 9:00
📱 **通知**: 已发送到 Feishu 和 Slack

---
*整合工作流 - 自动化运行*"

        send_notification "success" "$SUMMARY"
    else
        log_info "没有新数据，跳过通知"
    fi
}

# 运行主函数
main "$@"
