#!/bin/bash
#
# AI 提示词自动化漏斗模型 - 完整工作流（含搜索）
#
# 功能：
# 1. 使用 SearXNG 搜索高质量 AI 提示词
# 2. 自动分类（4 种类型）
# 3. 分类评分（差异化评分）
# 4. 质量筛选（4 种规则）
# 5. 内容补充（4 种策略）
# 6. Skill 转换（多模板）
#

set -e

PROJECT_ROOT="/root/clawd"
SEARCH_SCRIPT="$PROJECT_ROOT/scripts/collect-prompts-via-searxng.py"
CLASSIFY_SCRIPT="$PROJECT_ROOT/skills/ai-prompt-workflow/scripts/classify-content.py"
SCORE_SCRIPT="$PROJECT_ROOT/skills/ai-prompt-workflow/scripts/score-content.py"
FILTER_SCRIPT="$PROJECT_ROOT/skills/ai-prompt-workflow/scripts/filter-quality.py"
ENHANCE_SCRIPT="$PROJECT_ROOT/skills/ai-prompt-workflow/scripts/enhance-content.py"
CONVERT_SCRIPT="$PROJECT_ROOT/scripts/convert-prompts-to-skills.py"

DATA_DIR="$PROJECT_ROOT/data/prompts"
LOG_FILE="$DATA_DIR/logs/workflow-with-search.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
QUALITY_THRESHOLD=60
TEST_MODE=false
VERBOSE=false

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --quality-threshold)
            QUALITY_THRESHOLD="$2"
            shift 2
            ;;
        --test-mode)
            TEST_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --quality-threshold N  质量阈值（默认：60）"
            echo "  --test-mode          测试模式（不发布）"
            echo "  --verbose             详细输出"
            echo "  --help               显示此帮助信息"
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

# 确保日志目录存在
mkdir -p "$DATA_DIR/logs"

log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] [${GREEN}SUCCESS${NC}] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] [${RED}ERROR${NC}] $1" | tee -a "$LOG_FILE"
}

echo "=========================================="
echo "  AI 提示词自动化漏斗模型 - 完整工作流（含搜索）"
echo "=========================================="
echo ""
log_info "配置："
log_info "  - 质量阈值：$QUALITY_THRESHOLD"
log_info "  - 测试模式：$TEST_MODE"
log_info "  - 详细输出：$VERBOSE"
echo ""

# ========== Phase 1: 数据搜索层 ==========
START_TIME=$(date +%s)
log_info "========== Phase 1: 数据搜索层 =========="

if [ "$TEST_MODE" = true ]; then
    log_info "[TEST MODE] 跳过数据搜索"
else
    log_info "开始数据搜索..."
    python3 "$SEARCH_SCRIPT" || {
        log_error "数据搜索失败"
        exit 1
    }
    log_success "数据搜索完成"
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
log_success "Phase 1: 数据搜索层 完成（耗时：$DURATION 秒）"
START_TIME=$END_TIME
echo ""

# ========== Phase 2: 自动分类层 ==========
log_info "========== Phase 2: 自动分类层 =========="
log_info "开始自动分类..."

cd "$PROJECT_ROOT"
python3 "$CLASSIFY_SCRIPT" || {
    log_error "自动分类失败"
    exit 1
}

log_success "自动分类完成"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
log_success "Phase 2: 自动分类层 完成（耗时：$DURATION 秒）"
START_TIME=$END_TIME
echo ""

# ========== Phase 3: 分类评分层 ==========
log_info "========== Phase 3: 分类评分层 =========="
log_info "开始分类评分..."

python3 "$SCORE_SCRIPT" || {
    log_error "分类评分失败"
    exit 1
}

log_success "分类评分完成"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
log_success "Phase 3: 分类评分层 完成（耗时：$DURATION 秒）"
START_TIME=$END_TIME
echo ""

# ========== Phase 4: 质量筛选层 ==========
log_info "========== Phase 4: 质量筛选层 =========="
log_info "开始质量筛选..."

python3 "$FILTER_SCRIPT" || {
    log_error "质量筛选失败"
    exit 1
}

log_success "质量筛选完成"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
log_success "Phase 4: 质量筛选层 完成（耗时：$DURATION 秒）"
START_TIME=$END_TIME
echo ""

# ========== Phase 5: 内容补充层 ==========
log_info "========== Phase 5: 内容补充层 =========="
log_info "开始内容补充..."

python3 "$ENHANCE_SCRIPT" || {
    log_error "内容补充失败"
    exit 1
}

log_success "内容补充完成"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
log_success "Phase 5: 内容补充层 完成（耗时：$DURATION 秒）"
START_TIME=$END_TIME
echo ""

# ========== Phase 6: Skill 转换层 ==========
log_info "========== Phase 6: Skill 转换层 =========="

if [ "$TEST_MODE" = true ]; then
    log_info "[TEST MODE] 跳过 Skill 转换"
else
    log_info "开始 Skill 转换..."

    cd "$PROJECT_ROOT/skills/prompt-to-skill-converter"
    python3 "$CONVERT_SCRIPT" || {
        log_error "Skill 转换失败"
        exit 1
    }

    log_success "Skill 转换完成"
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
log_success "Phase 6: Skill 转换层 完成（耗时：$DURATION 秒）"
echo ""

# ========== 总结 ==========
log_success "========== 工作流完成 =========="
log_info "日志文件：$LOG_FILE"
echo ""
log_info "数据目录："
log_info "  - 搜索数据：$DATA_DIR/collected/"
log_info "  - 分类数据：$DATA_DIR/classified/"
log_info "  - 评分数据：$DATA_DIR/scored/"
log_info "  - 筛选数据：$DATA_DIR/filtered/"
log_info "  - 补充数据：$DATA_DIR/enhanced/"
log_info "  - 转换数据：$DATA_DIR/converted/"
echo ""
echo "=========================================="
