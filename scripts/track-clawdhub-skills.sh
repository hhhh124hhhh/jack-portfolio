#!/bin/bash
# ClawdHub Skills 追踪脚本
# 功能: 每天深夜检查用户上传的 skills 在 clawdhub explore 中的表现
# 作者: jack happy

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="${SCRIPT_DIR}/../memory"
TRACKING_DIR="${MEMORY_DIR}/clawdhub-tracking"
LOG_FILE="${TRACKING_DIR}/tracking.log"
REPORT_FILE="${TRACKING_DIR}/daily-report-$(date +%Y%m%d).txt"
REGISTRY="https://www.clawhub.ai/api"

# 确保目录存在
mkdir -p "${TRACKING_DIR}"

# 用户上传的 skills 列表（会自动检测新发布的）
USER_SKILLS_FILE="${TRACKING_DIR}/user-skills.json"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

# 读取用户 skills
get_user_skills() {
    if [[ -f "${USER_SKILLS_FILE}" ]]; then
        cat "${USER_SKILLS_FILE}"
    else
        echo "[]"
    fi
}

# 更新用户 skills 列表
update_user_skills() {
    local new_skills=(
        "ai-music-prompts"
        "game-character-gen"
        "ai-video-gen-tools"
        "brand-creative-suite"
    )

    # 读取现有 skills
    local existing=$(get_user_skills)

    # 合并新 skills
    echo "${new_skills[@]}" | jq -R 'split(" ") | map({slug: .})' > "${USER_SKILLS_FILE}.tmp"

    if [[ -s "${USER_SKILLS_FILE}" ]]; then
        # 合并去重
        jq -s 'add | unique_by(.slug)' "${USER_SKILLS_FILE}" "${USER_SKILLS_FILE}.tmp" > "${USER_SKILLS_FILE}"
    else
        mv "${USER_SKILLS_FILE}.tmp" "${USER_SKILLS_FILE}"
    fi

    rm -f "${USER_SKILLS_FILE}.tmp"
}

# 检查 skills 在 explore 中的表现
check_skills_performance() {
    log "开始检查 ClawdHub skills 表现..."

    # 获取最新的 skills 列表（前 50 个）
    log "获取 clawdhub explore 数据..."
    local explore_output=$(clawdhub explore --registry "${REGISTRY}" 2>&1)

    # 保存 explore 输出
    echo "${explore_output}" > "${TRACKING_DIR}/explore-$(date +%Y%m%d-%H%M%S).log"

    # 解析用户 skills 的位置
    local user_skills=$(get_user_skills)
    local skill_count=$(echo "${user_skills}" | jq 'length')

    log "正在检查 ${skill_count} 个 skills..."

    echo "=== ClawdHub Skills 日报 ===" > "${REPORT_FILE}"
    echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "${REPORT_FILE}"
    echo "" >> "${REPORT_FILE}"

    local found_count=0
    local ranked_skills=()

    while IFS= read -r skill; do
        local slug=$(echo "${skill}" | jq -r '.slug')
        local skill_name="${slug}"

        # 在 explore 输出中查找这个 skill
        local skill_line=$(echo "${explore_output}" | grep -E "^${slug}\s+" || true)

        if [[ -n "${skill_line}" ]]; then
            # 找到了，解析位置
            local position=$(echo "${explore_output}" | grep -n "^${slug}\s+" | head -1 | cut -d: -f1)
            local time_ago=$(echo "${skill_line}" | awk '{for(i=3;i<=NF;i++) printf $i" "; print ""}')

            found_count=$((found_count + 1))
            ranked_skills+=("${position}|${slug}|${time_ago}")

            log "✓ 找到 ${slug} (位置 #${position}, ${time_ago})"
        else
            log "✗ 未找到 ${slug}"
        fi
    done < <(echo "${user_skills}" | jq -c '.[]')

    echo "" >> "${REPORT_FILE}"
    echo "总共有 ${skill_count} 个 skills，找到 ${found_count} 个" >> "${REPORT_FILE}"
    echo "" >> "${REPORT_FILE}"

    # 按 position 排序
    IFS=$'\n' sorted_skills=($(sort -n <<<"${ranked_skills[*]}"))
    unset IFS

    if [[ ${#sorted_skills[@]} -gt 0 ]]; then
        echo "=== 受欢迎度排名 ===" >> "${REPORT_FILE}"
        echo "" >> "${REPORT_FILE}"

        for ranked_skill in "${sorted_skills[@]}"; do
            IFS='|' read -r position slug time_ago <<< "${ranked_skill}"
            echo "#${position} - ${slug}" >> "${REPORT_FILE}"
            echo "  更新时间: ${time_ago}" >> "${REPORT_FILE}"

            # 分析受欢迎度
            if [[ ${position} -le 5 ]]; then
                echo "  🔥 热门: 前 5 名！" >> "${REPORT_FILE}"
            elif [[ ${position} -le 10 ]]; then
                echo "  ⭐ 热门: 前 10 名" >> "${REPORT_FILE}"
            elif [[ ${position} -le 20 ]]; then
                echo "  👍 良好: 前 20 名" >> "${REPORT_FILE}"
            elif [[ ${position} -le 30 ]]; then
                echo "  ✓ 一般: 前 30 名" >> "${REPORT_FILE}"
            else
                echo "  💭 需要关注" >> "${REPORT_FILE}"
            fi

            echo "" >> "${REPORT_FILE}"
        done
    else
        echo "⚠️ 没有找到任何 skills 在最新列表中" >> "${REPORT_FILE}"
    fi

    # 趋势分析（需要历史数据）
    echo "=== 趋势分析 ===" >> "${REPORT_FILE}"
    echo "" >> "${REPORT_FILE}"

    # 查找最近几天的报告
    local recent_reports=$(find "${TRACKING_DIR}" -name "daily-report-*.txt" -type f -mtime -7 | sort -r | head -6)

    if [[ $(echo "${recent_reports}" | wc -l) -gt 1 ]]; then
        echo "最近 7 天表现:" >> "${REPORT_FILE}"

        for report in ${recent_reports}; do
            local report_date=$(basename "${report}" | sed 's/daily-report-//' | sed 's/.txt//')
            local report_found=$(grep "找到" "${report}" | awk '{print $5}' || echo "0")

            echo "  ${report_date}: ${report_found} 个 skills 在列表中" >> "${REPORT_FILE}"
        done
    else
        echo "数据不足，需要更多天数的记录" >> "${REPORT_FILE}"
    fi

    echo "" >> "${REPORT_FILE}"
    echo "=== 建议 ===" >> "${REPORT_FILE}"
    echo "" >> "${REPORT_FILE}"

    # 根据数据给出建议
    if [[ ${found_count} -eq 0 ]]; then
        echo "⚠️ 所有 skills 都不在最新列表中" >> "${REPORT_FILE}"
        echo "建议:" >> "${REPORT_FILE}"
        echo "- 检查 skills 是否有更新可以发布" >> "${REPORT_FILE}"
        echo "- 考虑优化 skills 的描述和关键词" >> "${REPORT_FILE}"
        echo "- 在社区宣传你的 skills" >> "${REPORT_FILE}"
    elif [[ ${found_count} -lt $((skill_count / 2)) ]]; then
        echo "📊 部分 skills 表现不佳" >> "${REPORT_FILE}"
        echo "建议:" >> "${REPORT_FILE}"
        echo "- 重点关注排名靠后的 skills" >> "${REPORT_FILE}"
        echo "- 考虑添加新功能或改进文档" >> "${REPORT_FILE}"
    else
        echo "✅ 大部分 skills 表现良好" >> "${REPORT_FILE}"
        echo "建议:" >> "${REPORT_FILE}"
        echo "- 继续保持，定期更新" >> "${REPORT_FILE}"
        echo "- 考虑开发新的 skills" >> "${REPORT_FILE}"
    fi

    log "报告已生成: ${REPORT_FILE}"
}

# 发送报告到 Slack
send_report_to_slack() {
    log "发送报告到 Slack..."

    local report_content=$(cat "${REPORT_FILE}")

    # 使用 message 工具发送
    # 这里假设已经配置了 Slack
    # 实际发送需要在 Clawdbot 环境中调用 message 工具

    log "报告内容已准备好，等待发送..."
    echo "${report_content}"
}

# 主函数
main() {
    log "=== ClawdHub Skills 追踪脚本启动 ==="

    # 更新用户 skills 列表
    update_user_skills

    # 检查 skills 表现
    check_skills_performance

    # 发送报告
    send_report_to_slack

    log "=== 追踪脚本完成 ==="
}

# 执行
main "$@"
