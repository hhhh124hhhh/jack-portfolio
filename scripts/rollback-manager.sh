#!/bin/bash
# 回滚管理工具

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

ROLLBACK_LOG="/root/clawd/logs/rollback-history.jsonl"
WORKSPACE="/root/clawd"

# 显示帮助
show_help() {
    cat << EOF
回滚管理工具

用法:
  $0 [命令] [选项]

命令:
  list              列出所有回滚记录
  show <id>         显示指定记录详情
  rollback <id>     回滚到指定的发布
  clean             清理超过保留期的记录
  status            显示回滚系统状态

示例:
  $0 list                    # 查看最近 10 条记录
  $0 rollback last           # 回滚到最近一次发布
  $0 rollback 5              # 回滚到第 5 条记录
  $0 clean                   # 清理过期记录

EOF
}

# 列出所有回滚记录
list_records() {
    local limit=${1:-10}

    echo "=========================================="
    echo "回滚历史记录 (最近 $limit 条)"
    echo "=========================================="
    echo ""

    if [ ! -f "$ROLLBACK_LOG" ]; then
        echo -e "${YELLOW}⚠️  没有回滚记录${NC}"
        return 0
    fi

    local count=0
    tail -n "$limit" "$ROLLBACK_LOG" | while IFS= read -r line; do
        count=$((count + 1))
        local timestamp=$(echo "$line" | jq -r '.timestamp')
        local skill=$(echo "$line" | jq -r '.skill')
        local version=$(echo "$line" | jq -r '.version')
        local env=$(echo "$line" | jq -r '.environment')
        local score=$(echo "$line" | jq -r '.score')
        local commit=$(echo "$line" | jq -r '.git_commit')

        echo -e "${BLUE}[$count]${NC} $(echo "$timestamp" | cut -d'T' -f1 | cut -d'-' -f2-3) $(echo "$timestamp" | cut -d'T' -f2 | cut -d':' -f1-2)"
        echo "   技能: $skill v$version"
        echo "   环境: $env | 评分: $score"
        echo "   Commit: ${commit:0:7}"
        echo ""
    done

    local total=$(wc -l < "$ROLLBACK_LOG" 2>/dev/null || echo "0")
    echo "总记录数: $total"
}

# 显示指定记录详情
show_record() {
    local id=$1

    if [ -z "$id" ]; then
        echo -e "${RED}❌ 请指定记录 ID${NC}"
        exit 1
    fi

    if [ "$id" == "last" ]; then
        id=$(tail -1 "$ROLLBACK_LOG")
    else
        id=$(tail -n "$id" "$ROLLBACK_LOG" | head -1)
    fi

    if [ -z "$id" ]; then
        echo -e "${RED}❌ 记录不存在${NC}"
        exit 1
    fi

    echo "=========================================="
    echo "发布记录详情"
    echo "=========================================="
    echo ""
    echo "$id" | jq '.'
}

# 执行回滚
do_rollback() {
    local id=$1

    if [ -z "$id" ]; then
        echo -e "${RED}❌ 请指定要回滚到的记录 ID${NC}"
        exit 1
    fi

    echo ""
    read -p "确定要执行回滚吗？这将撤销最近的发布。(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消回滚"
        exit 0
    fi

    echo ""
    echo -e "${YELLOW}⚠️  开始回滚...${NC}"

    if [ "$id" == "last" ]; then
        id=$(tail -1 "$ROLLBACK_LOG")
    else
        id=$(tail -n "$id" "$ROLLBACK_LOG" | head -1)
    fi

    local skill=$(echo "$id" | jq -r '.skill')
    local commit=$(echo "$id" | jq -r '.git_commit')

    if [ "$commit" == "unknown" ]; then
        echo -e "${RED}❌ 无法回滚: 没有 Git commit 信息${NC}"
        exit 1
    fi

    cd "$WORKSPACE"

    echo "切换到 commit: ${commit:0:7}"
    if git checkout "$commit"; then
        echo -e "${GREEN}✅ 回滚成功${NC}"
        echo ""
        echo "当前状态:"
        git log -1 --oneline
    else
        echo -e "${RED}❌ 回滚失败${NC}"
        exit 1
    fi
}

# 清理过期记录
clean_records() {
    local window_days=$(jq -r '.rollback.window_days' /root/clawd/automation-config.json 2>/dev/null || echo "7")

    echo "清理超过 $window_days 天的回滚记录..."

    if [ ! -f "$ROLLBACK_LOG" ]; then
        echo "没有记录需要清理"
        return 0
    fi

    local temp_file="/tmp/rollback-cleaned.jsonl"
    local cutoff_date=$(date -d "$window_days days ago" -Iseconds 2>/dev/null || date -v-${window_days}d -Iseconds)

    local kept=0
    local removed=0

    while IFS= read -r line; do
        local timestamp=$(echo "$line" | jq -r '.timestamp')
        if [ "$timestamp" \> "$cutoff_date" ]; then
            echo "$line" >> "$temp_file"
            kept=$((kept + 1))
        else
            removed=$((removed + 1))
        fi
    done < "$ROLLBACK_LOG"

    mv "$temp_file" "$ROLLBACK_LOG"

    echo -e "${GREEN}✅ 清理完成${NC}"
    echo "保留: $kept 条"
    echo "删除: $removed 条"
}

# 显示系统状态
show_status() {
    echo "=========================================="
    echo "回滚系统状态"
    echo "=========================================="
    echo ""

    # 配置
    local window_days=$(jq -r '.rollback.window_days' /root/clawd/automation-config.json 2>/dev/null || echo "7")
    local auto_rollback=$(jq -r '.rollback.auto_rollback_on_failure' /root/clawd/automation-config.json 2>/dev/null || echo "false")

    echo "配置:"
    echo "  保留窗口: $window_days 天"
    echo "  自动回滚: $auto_rollback"
    echo ""

    # 记录统计
    if [ -f "$ROLLBACK_LOG" ]; then
        local total=$(wc -l < "$ROLLBACK_LOG")
        local today=$(date +%Y-%m-%d)
        local today_count=$(grep "$today" "$ROLLBACK_LOG" | wc -l)

        echo "记录统计:"
        echo "  总记录: $total"
        echo "  今日: $today_count"
        echo ""
    else
        echo "记录统计: 无记录"
        echo ""
    fi

    # 最近发布
    echo "最近发布:"
    if [ -f "$ROLLBACK_LOG" ]; then
        tail -1 "$ROLLBACK_LOG" | jq -r '"  \(.skill) v\(.version) | \(.timestamp | split(\"T\")[0] | split(\"-\")[1,2])"'
    else
        echo "  无"
    fi
}

# 主函数
main() {
    case "${1:-help}" in
        list)
            list_records "${2:-10}"
            ;;
        show)
            show_record "$2"
            ;;
        rollback)
            do_rollback "$2"
            ;;
        clean)
            clean_records
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知命令: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
