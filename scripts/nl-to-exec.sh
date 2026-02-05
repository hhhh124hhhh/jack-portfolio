#!/bin/bash
# 自然语言转可执行指令工具
# 使用子代理处理用户需求，并维护上下文记忆

set -e

# 配置
MEMORY_DIR="/root/clawd/memory/nl-exec"
CONTEXT_FILE="$MEMORY_DIR/context.json"
TASKS_DIR="$MEMORY_DIR/tasks"
SESSIONS_DIR="$MEMORY_DIR/sessions"

# 创建必要的目录
mkdir -p "$MEMORY_DIR"
mkdir -p "$TASKS_DIR"
mkdir -p "$SESSIONS_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 初始化上下文
init_context() {
    if [ ! -f "$CONTEXT_FILE" ]; then
        cat > "$CONTEXT_FILE" << 'EOF'
{
  "user_preferences": {},
  "previous_tasks": [],
  "learned_patterns": {},
  "created_at": null,
  "last_updated": null
}
EOF
        # 更新时间戳
        local now=$(date -Iseconds)
        sed -i "s/\"created_at\": null/\"created_at\": \"$now\"/" "$CONTEXT_FILE"
        sed -i "s/\"last_updated\": null/\"last_updated\": \"$now\"/" "$CONTEXT_FILE"

        log "✓ 上下文文件已初始化"
    fi
}

# 加载上下文
load_context() {
    if [ -f "$CONTEXT_FILE" ]; then
        cat "$CONTEXT_FILE"
    else
        echo "{}"
    fi
}

# 更新上下文
update_context() {
    local key=$1
    local value=$2

    # 使用 Python 更新 JSON（更可靠）
    python3 << EOF
import json
from datetime import datetime

context_file = "$CONTEXT_FILE"

try:
    with open(context_file, 'r', encoding='utf-8') as f:
        context = json.load(f)
except:
    context = {}

context['$key'] = $value
context['last_updated'] = datetime.now().isoformat()

with open(context_file, 'w', encoding='utf-8') as f:
    json.dump(context, f, indent=2, ensure_ascii=False)
EOF

    log "✓ 上下文已更新: $key"
}

# 记录任务
record_task() {
    local task_input=$1
    local task_output=$2
    local status=$3
    local timestamp=$(date -Iseconds)

    local task_id=$(echo "$task_input" | md5sum | cut -d' ' -f1)
    local task_file="$TASKS_DIR/${task_id}.json"

    cat > "$task_file" << EOF
{
  "task_id": "$task_id",
  "input": "$task_input",
  "output": $task_output,
  "status": "$status",
  "created_at": "$timestamp"
}
EOF

    log "✓ 任务已记录: $task_id"
}

# 使用子代理处理自然语言请求
process_with_agent() {
    local user_input=$1
    local task_type=${2:-"general"}
    local label="nl-exec-$(date +%s)"

    log "🤖 启动子代理处理请求..."

    # 构造提示词
    local prompt="You are a task execution agent. Your job is to convert natural language requests into executable commands and execute them.

User Request: $user_input

Context from previous tasks:
$(load_context)

Instructions:
1. Analyze the user's request
2. Determine what needs to be done
3. Generate the appropriate command(s)
4. Execute the command(s)
5. Report the results back
6. Keep track of patterns for future use

Be precise and safe. If the request involves destructive operations, confirm before executing."

    # 使用 sessions_spawn 启动子代理
    local agent_output
    agent_output=$(clawdbot sessions spawn \
        --task "$prompt" \
        --label "$label" \
        --timeout-seconds 300 \
        --cleanup delete 2>&1)

    local exit_code=$?

    # 保存会话信息
    local session_file="$SESSIONS_DIR/${label}.txt"
    echo "$agent_output" > "$session_file"

    if [ $exit_code -eq 0 ]; then
        log "✓ 子代理执行成功"

        # 提取命令（简单实现）
        local commands=$(echo "$agent_output" | grep -E "^(Command|Executed):" | sed 's/^[^:]*: //' || echo "unknown")

        # 记录任务
        record_task "$user_input" "\"$(echo "$agent_output" | head -c 5000 | jq -Rs . 2>/dev/null || echo '{}')\"" "success"

        # 更新上下文
        update_context "last_task" "\"$task_type\""

        # 返回结果
        echo "$agent_output"
        return 0
    else
        log "✗ 子代理执行失败"

        # 记录失败任务
        record_task "$user_input" "\"Error: $(echo "$agent_output" | head -c 1000)\"" "failed"

        return 1
    fi
}

# 解析并执行简单命令（备用方案）
execute_simple_command() {
    local user_input=$1

    log "🔍 解析用户请求..."

    # 简单的模式匹配
    case "$user_input" in
        *"批量处理"*"skill"*)
            log "识别为: 批量处理 .skill 文件"
            echo "执行: bash /root/clawd/scripts/batch-process-all-skills.sh"
            bash /root/clawd/scripts/batch-process-all-skills.sh
            ;;
        *"上传"*"skill"*)
            log "识别为: 上传 skills 到 ClawdHub"
            echo "执行: bash /root/clawd/scripts/batch-upload-skills-v3.sh"
            bash /root/clawd/scripts/batch-upload-skills-v3.sh
            ;;
        *"转换"*"prompt"*)
            log "识别为: 转换 prompts 为 skills"
            echo "执行: python3 /root/clawd/scripts/convert-prompts-to-skills.py"
            python3 /root/clawd/scripts/convert-prompts-to-skills.py
            ;;
        *"搜索"*"X"*"AI提示词"*)
            log "识别为: 搜索 X 上的 AI 提示词"
            echo "执行: python3 /root/clawd/scripts/search-x-prompts.py"
            if [ -f "/root/clawd/scripts/search-x-prompts.py" ]; then
                python3 /root/clawd/scripts/search-x-prompts.py
            else
                log "✗ 脚本不存在，需要先创建"
                return 1
            fi
            ;;
        *"评估"*"提示词"*)
            log "识别为: 评估提示词质量"
            echo "执行: python3 /root/clawd/scripts/evaluate-prompts.py"
            if [ -f "/root/clawd/scripts/evaluate-prompts.py" ]; then
                python3 /root/clawd/scripts/evaluate-prompts.py
            else
                log "✗ 脚本不存在，需要先创建"
                return 1
            fi
            ;;
        *)
            log "⚠️  未能识别请求，使用子代理处理"
            return 2  # 返回 2 表示需要使用子代理
            ;;
    esac

    return $?
}

# 交互式模式
interactive_mode() {
    print_status "$MAGENTA" "🤖 自然语言命令解释器"
    print_status "$BLUE" "输入你的需求（输入 'exit' 退出）："
    echo ""

    while true; do
        echo -n "❯ "
        read -e user_input

        if [ -z "$user_input" ]; then
            continue
        fi

        if [ "$user_input" = "exit" ] || [ "$user_input" = "quit" ]; then
            break
        fi

        echo ""
        log "用户请求: $user_input"

        # 尝试简单命令
        execute_simple_command "$user_input"
        local result=$?

        if [ $result -eq 2 ]; then
            # 使用子代理
            process_with_agent "$user_input"
        elif [ $result -ne 0 ]; then
            print_status "$RED" "✗ 执行失败"
        fi

        echo ""
    done
}

# 显示上下文信息
show_context() {
    print_status "$BLUE" "📊 当前上下文："
    echo ""
    load_context | jq '.' 2>/dev/null || cat "$CONTEXT_FILE"
    echo ""
}

# 显示历史任务
show_history() {
    print_status "$BLUE" "📜 任务历史："
    echo ""

    local count=$(ls -1 "$TASKS_DIR"/*.json 2>/dev/null | wc -l)
    if [ $count -eq 0 ]; then
        print_status "$YELLOW" "没有历史任务"
    else
        ls -lt "$TASKS_DIR"/*.json | head -10 | while read -r line; do
            local task_file=$(echo "$line" | awk '{print $NF}')
            local task_info=$(cat "$task_file" | jq -r '{task_id, status, created_at}')
            echo "  • $(echo "$task_info" | jq -r '.task_id') - $(echo "$task_info" | jq -r '.status') ($(echo "$task_info" | jq -r '.created_at'))"
        done
    fi
    echo ""
}

# 主函数
main() {
    local mode=${1:-"interactive"}
    local user_input=${2:-""}

    # 初始化上下文
    init_context

    case "$mode" in
        "interactive")
            interactive_mode
            ;;
        "execute")
            if [ -z "$user_input" ]; then
                print_status "$RED" "错误: execute 模式需要提供用户输入"
                echo "用法: $0 execute \"你的需求\""
                exit 1
            fi

            # 尝试简单命令
            execute_simple_command "$user_input"
            local result=$?

            if [ $result -eq 2 ]; then
                # 使用子代理
                process_with_agent "$user_input"
            fi
            ;;
        "context")
            show_context
            ;;
        "history")
            show_history
            ;;
        *)
            print_status "$RED" "未知模式: $mode"
            echo ""
            echo "用法:"
            echo "  $0 interactive      # 交互式模式"
            echo "  $0 execute \"需求\"   # 执行单个需求"
            echo "  $0 context         # 显示上下文"
            echo "  $0 history         # 显示任务历史"
            exit 1
            ;;
    esac
}

main "$@"
