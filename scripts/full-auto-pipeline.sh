#!/bin/bash
# 全自动化 AI 提示词到 Skill 转换流水线
# 方案 B: 完全自动化，带测试环境和回滚机制

set -e

# ==================== 配置区 ====================

# 目录配置
WORKSPACE="/root/clawd"
DIST_DIR="$WORKSPACE/dist"
TEST_DIR="$WORKSPACE/test-dist"
REPORT_DIR="$WORKSPACE/reports"
LOG_DIR="$WORKSPACE/logs"

# 质量阈值
MIN_SCORE_FOR_PUBLISH=90      # 最低发布分数
MIN_SCORE_FOR_TEST=70         # 测试环境最低分数
MAX_SKILLS_PER_RUN=5          # 每次最多发布数量（安全限制）

# Git 配置
GIT_REPO_URL="git@github.com:clawdbot/clawd-skills-published.git"
TEST_BRANCH="test-env"
PROD_BRANCH="master"

# 回滚配置
ROLLBACK_WINDOW_DAYS=7        # 保留最近 7 天的发布记录用于回滚
ROLLBACK_LOG="$LOG_DIR/rollback-history.jsonl"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# ==================== 工具函数 ====================

log() {
    local level=$1
    shift
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo -e "$msg" | tee -a "$LOG_FILE"
}

print_header() {
    echo ""
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}========================================${NC}"
}

print_section() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 创建目录
ensure_dirs() {
    mkdir -p "$DIST_DIR" "$TEST_DIR" "$REPORT_DIR" "$LOG_DIR"
}

# 初始化日志
init_log() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    LOG_FILE="$LOG_DIR/pipeline-${timestamp}.log"
    log "INFO" "全自动化流水线启动"
    log "INFO" "日志文件: $LOG_FILE"
}

# 记录发布历史（用于回滚）
record_publish() {
    local skill_name=$1
    local version=$2
    local env=$3
    local score=$4

    local record=$(cat << EOF
{
  "timestamp": "$(date -Iseconds)",
  "skill": "$skill_name",
  "version": "$version",
  "environment": "$env",
  "score": $score,
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')"
}
EOF
)

    echo "$record" >> "$ROLLBACK_LOG"
    log "INFO" "记录发布: $skill_name v$version (env=$env, score=$score)"
}

# 回滚到之前的状态
rollback() {
    local reason=$1
    print_error "触发回滚: $reason"
    log "ERROR" "触发回滚: $reason"

    # 查找最近的成功发布
    local last_record=$(tail -1 "$ROLLBACK_LOG" 2>/dev/null || echo "")
    if [ -z "$last_record" ]; then
        print_error "没有可回滚的历史记录"
        return 1
    fi

    local skill=$(echo "$last_record" | jq -r '.skill')
    local version=$(echo "$last_record" | jq -r '.version')
    local commit=$(echo "$last_record" | jq -r '.git_commit')

    print_warning "回滚到: $skill v$version (commit: ${commit:0:7})"

    # 切换到之前的 commit
    if [ "$commit" != "unknown" ]; then
        cd "$WORKSPACE"
        git checkout "$commit" || print_error "Git checkout 失败"
        print_success "回滚成功"
    fi

    # 发送回滚通知
    send_notification "🚨 回滚通知\n\n原因: $reason\n回滚到: $skill v$version\nCommit: ${commit:0:7}"

    exit 1
}

# 发送通知
send_notification() {
    local message=$1

    # 发送到 Slack
    if command -v clawdbot &> /dev/null; then
        clawdbot message send \
            --channel slack \
            --target "#clawdbot" \
            --message "$message" 2>/dev/null || true
    fi
}

# ==================== 流水线阶段 ====================

# 阶段 1: 数据收集
stage_1_collect() {
    print_section "阶段 1/5: 数据收集"

    log "INFO" "开始收集 AI 提示词..."

    if bash "$WORKSPACE/scripts/collect-multi-source-prompts.sh" >> "$LOG_FILE" 2>&1; then
        print_success "数据收集完成"
        return 0
    else
        print_error "数据收集失败"
        rollback "数据收集失败"
    fi
}

# 阶段 2: 质量评估
stage_2_evaluate() {
    print_section "阶段 2/5: 质量评估"

    log "INFO" "开始质量评估..."

    if node "$WORKSPACE/scripts/auto-scoring-system.js" >> "$LOG_FILE" 2>&1; then
        print_success "质量评估完成"

        # 分析评估结果
        local results_file="$WORKSPACE/reports/quality-evaluation-results.json"
        if [ -f "$results_file" ]; then
            local total=$(jq 'length' "$results_file")
            local high_quality=$(jq '[.[] | select(.totalScore >= '"$MIN_SCORE_FOR_PUBLISH"')] | length' "$results_file")
            local test_quality=$(jq '[.[] | select(.totalScore >= '"$MIN_SCORE_FOR_TEST"' and .totalScore < '"$MIN_SCORE_FOR_PUBLISH"')] | length' "$results_file")

            log "INFO" "评估结果: 总计 $total, 高质量 ($MIN_SCORE_FOR_PUBLISH+) $high_quality, 测试合格 ($MIN_SCORE_FOR_TEST+) $test_quality"

            echo "$total|$high_quality|$test_quality" > "$REPORT_DIR/evaluation-stats.txt"
        fi

        return 0
    else
        print_error "质量评估失败"
        rollback "质量评估失败"
    fi
}

# 阶段 3: 转换生成
stage_3_convert() {
    print_section "阶段 3/5: 转换生成"

    log "INFO" "开始转换高质量提示词为 Skills..."

    # 清理旧的输出
    rm -rf "$TEST_DIR"/*
    mkdir -p "$TEST_DIR"

    # 找出高分提示词并转换
    local results_file="$WORKSPACE/reports/quality-evaluation-results.json"
    if [ ! -f "$results_file" ]; then
        print_error "评估结果文件不存在"
        rollback "评估结果文件缺失"
    fi

    # 提取高分提示词
    local high_score_prompts=$(jq '[.[] | select(.totalScore >= '"$MIN_SCORE_FOR_TEST"')] | .[].id' "$results_file" | head -n "$MAX_SKILLS_PER_RUN")
    local count=0

    for prompt_id in $high_score_prompts; do
        # 去掉引号
        prompt_id=$(echo "$prompt_id" | tr -d '"')

        log "INFO" "转换提示词: $prompt_id"

        # 调用转换脚本
        if node "$WORKSPACE/scripts/tweet-to-skill-converter.js" --id "$prompt_id" --output "$TEST_DIR" >> "$LOG_FILE" 2>&1; then
            count=$((count + 1))
            log "INFO" "成功转换: $prompt_id"
        else
            log "WARNING" "转换失败: $prompt_id"
        fi
    done

    log "INFO" "转换完成: $count 个 Skills"
    print_success "转换完成: $count 个 Skills"

    # 记录生成的 Skills
    find "$TEST_DIR" -name "*.md" -type f | sort > "$REPORT_DIR/generated-skills.txt"

    return 0
}

# 阶段 4: 测试环境部署
stage_4_test_deploy() {
    print_section "阶段 4/5: 测试环境部署"

    log "INFO" "部署到测试环境..."

    # 检查是否有新生成的 Skills
    if [ ! -f "$REPORT_DIR/generated-skills.txt" ]; then
        print_warning "没有新生成的 Skills，跳过测试部署"
        return 0
    fi

    local skill_count=$(wc -l < "$REPORT_DIR/generated-skills.txt")
    if [ "$skill_count" -eq 0 ]; then
        print_warning "没有 Skills 需要测试，跳过"
        return 0
    fi

    log "INFO" "有 $skill_count 个 Skills 需要测试"

    # 初始化测试仓库（如果不存在）
    if [ ! -d "$WORKSPACE/.git" ]; then
        cd "$WORKSPACE"
        git init
        git config user.name "Clawdbot Auto"
        git config user.email "clawdbot@clawd.bot"
        log "INFO" "初始化 Git 仓库"
    fi

    # 创建测试分支
    cd "$WORKSPACE"
    git checkout -b "$TEST_BRANCH" 2>/dev/null || git checkout "$TEST_BRANCH"

    # 复制 Skills 到发布目录
    rm -rf "$DIST_DIR"/*
    cp -r "$TEST_DIR"/* "$DIST_DIR"/ 2>/dev/null || true

    # 提交到测试分支
    git add dist/
    git commit -m "Test deploy: $(date '+%Y-%m-%d %H:%M:%S')" || print_warning "没有变更需要提交"

    # 模拟测试（这里可以扩展为真正的测试）
    print_success "测试环境部署完成"
    log "INFO" "测试分支: $TEST_BRANCH"

    # 验证 Skills
    log "INFO" "验证 Skills..."

    local valid_skills=0
    local invalid_skills=0

    while IFS= read -r skill_file; do
        if [ -f "$skill_file" ]; then
            # 检查 SKILL.md 格式
            if grep -q "^name:" "$skill_file" && grep -q "^description:" "$skill_file"; then
                valid_skills=$((valid_skills + 1))
                log "INFO" "✅ Skill 有效: $(basename "$skill_file")"
            else
                invalid_skills=$((invalid_skills + 1))
                log "WARNING" "⚠️  Skill 无效: $(basename "$skill_file")"
            fi
        fi
    done < "$REPORT_DIR/generated-skills.txt"

    log "INFO" "验证结果: 有效 $valid_skills, 无效 $invalid_skills"

    if [ "$invalid_skills" -gt 0 ]; then
        print_warning "发现 $invalid_skills 个无效 Skills，建议人工审核"
    fi

    return 0
}

# 阶段 5: 生产环境发布
stage_5_publish() {
    print_section "阶段 5/5: 生产环境发布"

    # 只发布评分 >= MIN_SCORE_FOR_PUBLISH 的 Skills
    local results_file="$WORKSPACE/reports/quality-evaluation-results.json"
    if [ ! -f "$results_file" ]; then
        print_warning "评估结果文件不存在，跳过发布"
        return 0
    fi

    # 找出高评分提示词
    local high_score_count=$(jq '[.[] | select(.totalScore >= '"$MIN_SCORE_FOR_PUBLISH"')] | length' "$results_file")
    log "INFO" "高评分 ($MIN_SCORE_FOR_PUBLISH+) 提示词: $high_score_count"

    if [ "$high_score_count" -eq 0 ]; then
        print_warning "没有达到发布阈值的 Skills，跳过发布"
        return 0
    fi

    # 限制每次发布数量
    if [ "$high_score_count" -gt "$MAX_SKILLS_PER_RUN" ]; then
        print_warning "高评分 Skills ($high_score_count) 超过单次限制 ($MAX_SKILLS_PER_RUN)，只发布前 $MAX_SKILLS_PER_RUN 个"
        high_score_count=$MAX_SKILLS_PER_RUN
    fi

    print_warning "即将发布 $high_score_count 个 Skills 到生产环境"
    log "WARNING" "即将发布 $high_score_count 个 Skills"

    # 切换到生产分支
    cd "$WORKSPACE"
    git checkout "$PROD_BRANCH" 2>/dev/null || git checkout -b "$PROD_BRANCH"

    # 确保发布目录有正确的 Skills
    if [ ! -d "$DIST_DIR" ] || [ -z "$(ls -A $DIST_DIR)" ]; then
        print_error "发布目录为空，无法发布"
        rollback "发布目录为空"
    fi

    # 记录发布前状态
    local pre_publish_commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")

    # 调用自动发布脚本
    log "INFO" "开始发布到 ClawdHub..."
    if bash "$WORKSPACE/scripts/auto-publish-skills.sh" >> "$LOG_FILE" 2>&1; then
        print_success "发布成功"

        # 记录发布历史
        local skills_published=$(grep "✅ Successfully published" "$LOG_DIR/pipeline-"*.log | tail -"$high_score_count" || echo "")

        if [ -n "$skills_published" ]; then
            echo "$skills_published" | while read -r line; do
                local skill_name=$(echo "$line" | sed 's/.*Successfully published: //')
                record_publish "$skill_name" "1.0.0" "production" "90+"
            done
        fi

        # 提交到 Git
        git add dist/
        git commit -m "Publish: $(date '+%Y-%m-%d %H:%M:%S') - $high_score_count skills" || true
        git push origin "$PROD_BRANCH" 2>/dev/null || print_warning "Git push 失败"

        return 0
    else
        print_error "发布失败"
        rollback "ClawdHub 发布失败"
    fi
}

# 生成最终报告
generate_report() {
    print_section "生成最终报告"

    local report_file="$REPORT_DIR/pipeline-report-$(date +%Y%m%d-%H%M%S).md"

    # 获取统计数据
    local eval_stats=$(cat "$REPORT_DIR/evaluation-stats.txt" 2>/dev/null || echo "0|0|0")
    local total_prompts=$(echo "$eval_stats" | cut -d'|' -f1)
    local high_quality=$(echo "$eval_stats" | cut -d'|' -f2)
    local test_quality=$(echo "$eval_stats" | cut -d'|' -f3)

    local generated_skills=$(wc -l < "$REPORT_DIR/generated-skills.txt" 2>/dev/null || echo "0")
    local published_skills=$(grep "✅ Successfully published" "$LOG_FILE" | wc -l || echo "0")

    cat > "$report_file" << EOF
# 全自动化流水线执行报告

**执行时间**: $(date '+%Y-%m-%d %H:%M:%S')
**日志文件**: \`$LOG_FILE\`

---

## 📊 执行摘要

| 阶段 | 状态 | 结果 |
|------|------|------|
| 1. 数据收集 | ✅ | 完成 |
| 2. 质量评估 | ✅ | 完成 |
| 3. 转换生成 | ✅ | 完成 |
| 4. 测试部署 | ✅ | 完成 |
| 5. 生产发布 | ${published_skills:-✅} | 完成 |

---

## 🎯 质量统计

| 指标 | 数量 |
|------|------|
| 收集的提示词 | $total_prompts |
| 高质量 ($MIN_SCORE_FOR_PUBLISH+) | $high_quality |
| 测试合格 ($MIN_SCORE_FOR_TEST+) | $test_quality |
| 生成的 Skills | $generated_skills |
| 发布的 Skills | $published_skills |

---

## 🔧 配置参数

| 参数 | 值 |
|------|-----|
| 发布最低分数 | $MIN_SCORE_FOR_PUBLISH |
| 测试最低分数 | $MIN_SCORE_FOR_TEST |
| 单次发布限制 | $MAX_SKILLS_PER_RUN |
| 回滚窗口 | $ROLLBACK_WINDOW_DAYS 天 |

---

## 📝 生成的 Skills

$(cat "$REPORT_DIR/generated-skills.txt" 2>/dev/null | sed 's|^|- |' || echo "无")

---

## 🚀 发布记录

$(grep "✅ Successfully published" "$LOG_FILE" 2>/dev/null || echo "无")

---

## 🔄 回滚历史

$(tail -5 "$ROLLBACK_LOG" 2>/dev/null | while IFS= read -r line; do
    echo "\`\`\`json"
    echo "$line" | jq -r '"- \(.timestamp | split("T")[0]) | \(.skill) v\(.version) | score: \(.score)"'
    echo "\`\`\`"
done || echo "无")

---

**报告自动生成**
EOF

    print_success "报告已生成: $report_file"

    # 发送摘要通知
    local summary="✅ 全自动化流水线执行完成！

📊 **执行摘要**:
• 收集提示词: $total_prompts
• 高质量 ($MIN_SCORE_FOR_PUBLISH+): $high_quality
• 生成的 Skills: $generated_skills
• 发布的 Skills: $published_skills

📄 **完整报告**: $report_file"

    send_notification "$summary"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ 流水线执行完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "$summary"
}

# ==================== 主函数 ====================

main() {
    print_header "全自动化 AI 提示词 → Skill 转换流水线"

    # 初始化
    ensure_dirs
    init_log

    log "INFO" "配置参数:"
    log "INFO" "  - 发布最低分数: $MIN_SCORE_FOR_PUBLISH"
    log "INFO" "  - 测试最低分数: $MIN_SCORE_FOR_TEST"
    log "INFO" "  - 单次发布限制: $MAX_SKILLS_PER_RUN"
    log "INFO" "  - 回滚窗口: $ROLLBACK_WINDOW_DAYS 天"

    # 执行流水线
    stage_1_collect
    stage_2_evaluate
    stage_3_convert
    stage_4_test_deploy
    stage_5_publish

    # 生成报告
    generate_report

    log "INFO" "流水线执行完成"
}

# 执行主函数
main "$@"
