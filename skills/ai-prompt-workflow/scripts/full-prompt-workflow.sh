#!/bin/bash
#
# AI 提示词自动化漏斗模型 - 完整工作流脚本
# 作者：Momo (Clawdbot Team)
# 创建日期：2026-02-05
#
# 功能：整合 6 层漏斗模型，实现端到端自动化
#
# 使用方法：
#   bash full-prompt-workflow.sh [OPTIONS]
#
# 选项：
#   --quality-threshold N   质量阈值（0-100），默认：60
#   --test-mode            测试模式，不发布
#   --verbose              详细输出
#   --dry-run              预览模式
#   --help                 显示帮助
#

set -e

# ========== 配置 ==========
PROJECT_ROOT="/root/clawd"
DATA_DIR="$PROJECT_ROOT/data/prompts"
LOG_DIR="$PROJECT_ROOT/logs/ai-prompt-workflow"
REPORT_DIR="$PROJECT_ROOT/reports/ai-prompt-workflow"

# 创建目录
mkdir -p "$LOG_DIR"
mkdir -p "$REPORT_DIR"
mkdir -p "$DATA_DIR"/{collected,classified,scored,filtered,enhanced,converted}

# 脚本路径
SCRIPT_DIR="$PROJECT_ROOT/skills/ai-prompt-workflow/scripts"
CLASSIFY_SCRIPT="$SCRIPT_DIR/classify-content.py"
SCORE_SCRIPT="$SCRIPT_DIR/score-content.py"
FILTER_SCRIPT="$SCRIPT_DIR/filter-quality.py"
ENHANCE_SCRIPT="$SCRIPT_DIR/enhance-content.py"

# 默认选项
QUALITY_THRESHOLD=60
TEST_MODE=false
VERBOSE=false
DRY_RUN=false

# ========== 解析参数 ==========
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
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            echo "AI 提示词自动化漏斗模型 - 完整工作流"
            echo ""
            echo "使用方法："
            echo "  bash $0 [OPTIONS]"
            echo ""
            echo "选项："
            echo "  --quality-threshold N   质量阈值（0-100），默认：60"
            echo "  --test-mode            测试模式，不发布"
            echo "  --verbose              详细输出"
            echo "  --dry-run              预览模式"
            echo "  --help                 显示帮助"
            exit 0
            ;;
        *)
            echo "未知选项：$1"
            echo "使用 --help 查看帮助"
            exit 1
            ;;
    esac
done

# ========== 日志函数 ==========
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_DIR/workflow.log"
}

log_info() {
    log "INFO" "$*"
}

log_success() {
    log "SUCCESS" "$*"
}

log_warning() {
    log "WARNING" "$*"
}

log_error() {
    log "ERROR" "$*"
}

# ========== 统计函数 ==========
START_TIME=$(date +%s)

start_phase() {
    local phase_name="$1"
    log_info "========== $phase_name =========="
    echo "$phase_name"
}

end_phase() {
    local phase_name="$1"
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    log_success "$phase_name 完成（耗时：$duration 秒）"
    START_TIME=$end_time
}

# ========== Phase 1: 数据收集 ==========
phase1_collect() {
    start_phase "Phase 1: 数据收集层"
    
    # 使用现有的 collect_prompts_enhanced.py
    cd "$PROJECT_ROOT/skills/prompt-to-skill-converter"
    
    log_info "开始数据收集..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] 跳过数据收集"
    else
        python3 scripts/collect_prompts_enhanced.py || {
            log_error "数据收集失败"
            return 1
        }
        log_success "数据收集完成"
    fi
    
    end_phase "Phase 1: 数据收集层"
}

# ========== Phase 2: 自动分类 ==========
phase2_classify() {
    start_phase "Phase 2: 自动分类层"
    
    log_info "开始自动分类..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] 跳过自动分类"
    else
        cd "$PROJECT_ROOT"
        python3 "$CLASSIFY_SCRIPT" || {
            log_error "自动分类失败"
            return 1
        }
        log_success "自动分类完成"
    fi
    
    end_phase "Phase 2: 自动分类层"
}

# ========== Phase 3: 分类评分 ==========
phase3_score() {
    start_phase "Phase 3: 分类评分层"
    
    log_info "开始分类评分..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] 跳过分类评分"
    else
        cd "$PROJECT_ROOT"
        python3 "$SCORE_SCRIPT" || {
            log_error "分类评分失败"
            return 1
        }
        log_success "分类评分完成"
    fi
    
    end_phase "Phase 3: 分类评分层"
}

# ========== Phase 4: 质量筛选 ==========
phase4_filter() {
    start_phase "Phase 4: 质量筛选层"
    
    log_info "开始质量筛选..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] 跳过质量筛选"
    else
        cd "$PROJECT_ROOT"
        python3 "$FILTER_SCRIPT" || {
            log_error "质量筛选失败"
            return 1
        }
        log_success "质量筛选完成"
    fi
    
    end_phase "Phase 4: 质量筛选层"
}

# ========== Phase 5: 内容补充 ==========
phase5_enhance() {
    start_phase "Phase 5: 内容补充层"
    
    log_info "开始内容补充..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] 跳过内容补充"
    else
        cd "$PROJECT_ROOT"
        python3 "$ENHANCE_SCRIPT" || {
            log_error "内容补充失败"
            return 1
        }
        log_success "内容补充完成"
    fi
    
    end_phase "Phase 5: 内容补充层"
}

# ========== Phase 6: Skill 转换 ==========
phase6_convert() {
    start_phase "Phase 6: Skill 转换层"
    
    log_info "开始 Skill 转换..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] 跳过 Skill 转换"
    else
        cd "$PROJECT_ROOT/skills/prompt-to-skill-converter"
        python3 scripts/convert-prompts-to-skills.py --quality-threshold "$QUALITY_THRESHOLD" || {
            log_error "Skill 转换失败"
            return 1
        }
        log_success "Skill 转换完成"
    fi
    
    end_phase "Phase 6: Skill 转换层"
}

# ========== 主流程 ==========
main() {
    local total_start_time=$(date +%s)
    
    log_info "========== AI 提示词自动化漏斗模型 - 完整工作流 =========="
    log_info "配置："
    log_info "  - 质量阈值：$QUALITY_THRESHOLD"
    log_info "  - 测试模式：$TEST_MODE"
    log_info "  - 详细输出：$VERBOSE"
    log_info "  - 预览模式：$DRY_RUN"
    log_info ""
    
    # 执行所有阶段
    phase1_collect || exit 1
    phase2_classify || exit 1
    phase3_score || exit 1
    phase4_filter || exit 1
    phase5_enhance || exit 1
    phase6_convert || exit 1
    
    # 计算总耗时
    local total_end_time=$(date +%s)
    local total_duration=$((total_end_time - total_start_time))
    
    log_info ""
    log_success "========== 工作流完成 =========="
    log_success "总耗时：$total_duration 秒"
    log_success "日志文件：$LOG_DIR/workflow.log"
    log_info ""
    log_info "数据目录："
    log_info "  - 收集数据：$DATA_DIR/collected/"
    log_info "  - 分类数据：$DATA_DIR/classified/"
    log_info "  - 评分数据：$DATA_DIR/scored/"
    log_info "  - 筛选数据：$DATA_DIR/filtered/"
    log_info "  - 补充数据：$DATA_DIR/enhanced/"
    log_info "  - 转换数据：$DATA_DIR/converted/"
}

# ========== 执行主流程 ==========
main
