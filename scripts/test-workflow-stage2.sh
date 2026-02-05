#!/bin/bash
# 测试 Stage 2：转换和发布（使用已有数据）

set -e

# 配置
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H%M)
LOG_FILE="/root/clawd/logs/test-workflow-stage2.log"
REPORT_DIR="/root/clawd/reports"

# prompt-to-skill-converter 配置
CONVERTER_DIR="/root/clawd/skills/prompt-to-skill-converter"

# 默认参数
QUALITY_THRESHOLD="${QUALITY_THRESHOLD:-50}"  # 降低阈值以获得更多数据

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

log ""
log "=========================================="
log "🚀 测试 Stage 2：转换和发布（使用已有数据）"
log "=========================================="
log ""
log "数据源: /root/clawd/data/prompts/collected/prompts-enhanced-20260202-1243.jsonl"
log "质量阈值: $QUALITY_THRESHOLD"
log ""

# 使用已有的数据文件
STAGE1_OUTPUT="/root/clawd/data/prompts/collected/prompts-enhanced-20260202-1243.jsonl"

if [ ! -f "$STAGE1_OUTPUT" ]; then
    log_error "❌ 数据文件不存在：$STAGE1_OUTPUT"
    exit 1
fi

log_info "✅ 数据文件存在"

# 计算收集的提示词数量
EVALUATED_COUNT=$(wc -l < "$STAGE1_OUTPUT" 2>/dev/null || echo "0")
log_info "✅ 找到 $EVALUATED_COUNT 个提示词"

# 保存到临时文件供 Stage 2 使用
echo "$STAGE1_OUTPUT" > /tmp/stage1_output.txt

# Stage 2: 使用 prompt-to-skill-converter 进行转换和发布
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
    exit 1
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
log_info "正在分类提示词..."
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
    elif 'text' in ptype.lower() or ptype == 'general':
        with open('/tmp/text-prompts.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(new_prompt, ensure_ascii=False) + '\n')
        text_count += 1
    else:
        other_count += 1

# 输出分类统计
print(f"✅ 分类完成")
print(f"  图像类: {image_count}")
print(f"  视频类: {video_count}")
print(f"  文本类: {text_count}")
print(f"  其他: {other_count}")
PYTHON_SCRIPT

# 2.2 转换为 Skills
log ""
log "[2.2] 转换为 Skills..."

CONVERT_SCRIPT="$CONVERTER_DIR/scripts/convert-prompts-to-skills.py"
if [ ! -f "$CONVERT_SCRIPT" ]; then
    log_error "❌ 转换脚本不存在：$CONVERT_SCRIPT"
    exit 1
fi

# 转换图像类
if [ -s "$IMAGE_PROMPTS_FILE" ]; then
    log "转换图像类提示词..."
    python3 "$CONVERT_SCRIPT" \
        --input "$IMAGE_PROMPTS_FILE" \
        --quality-threshold "$QUALITY_THRESHOLD" \
        --test-mode \
        >> "$LOG_FILE" 2>&1 && log_info "✅ 图像类转换完成" || log_error "❌ 图像类转换失败"
fi

# 转换视频类
if [ -s "$VIDEO_PROMPTS_FILE" ]; then
    log "转换视频类提示词..."
    python3 "$CONVERT_SCRIPT" \
        --input "$VIDEO_PROMPTS_FILE" \
        --quality-threshold "$QUALITY_THRESHOLD" \
        --test-mode \
        >> "$LOG_FILE" 2>&1 && log_info "✅ 视频类转换完成" || log_error "❌ 视频类转换失败"
fi

# 转换文本类
if [ -s "$TEXT_PROMPTS_FILE" ]; then
    log "转换文本类提示词..."
    python3 "$CONVERT_SCRIPT" \
        --input "$TEXT_PROMPTS_FILE" \
        --quality-threshold "$QUALITY_THRESHOLD" \
        --test-mode \
        >> "$LOG_FILE" 2>&1 && log_info "✅ 文本类转换完成" || log_error "❌ 文本类转换失败"
fi

log ""
log "=========================================="
log "✅ Stage 2 测试完成！"
log "=========================================="
log ""
log "查看日志: $LOG_FILE"
