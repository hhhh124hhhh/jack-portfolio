#!/bin/bash
# Clawdbot 自动更新脚本
# 功能：检查更新、自动安装、重启服务

set -e

# 配置
LOG_FILE="/tmp/clawdbot-auto-update.log"
MAX_LOG_LINES=1000
FORCE_UPDATE=false
CONFIG_FILE="/root/clawd/scripts/auto-update-config.sh"

# 加载配置
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# 检查更新
check_updates() {
    log_info "检查 Clawdbot 更新..."

    # 获取当前版本
    CURRENT_VERSION=$(clawdbot --version 2>/dev/null || echo "unknown")
    log_info "当前版本: $CURRENT_VERSION"

    # 检查是否有新版本
    LATEST_VERSION=$(npm view clawdbot version 2>/dev/null || echo "unknown")
    log_info "最新版本: $LATEST_VERSION"

    if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
        log_info "已经是最新版本，无需更新"
        return 0
    else
        log_warn "发现新版本: $LATEST_VERSION"
        return 1
    fi
}

# 执行更新
do_update() {
    log_info "开始更新 Clawdbot..."

    # 停止旧服务
    log_info "停止旧服务..."
    pkill -f "clawdbot-gateway" || true
    sleep 2

    # 执行更新
    log_info "执行 npm update..."
    if npm update -g clawdbot >> "$LOG_FILE" 2>&1; then
        log_info "npm update 成功"
    else
        log_error "npm update 失败"
        return 1
    fi

    # 等待几秒
    sleep 3

    # 验证更新
    NEW_VERSION=$(clawdbot --version 2>/dev/null || echo "unknown")
    log_info "更新后版本: $NEW_VERSION"

    # 启动新服务
    log_info "启动新服务..."
    nohup clawdbot gateway start > /tmp/clawdbot-gateway.log 2>&1 &

    # 等待服务启动
    sleep 5

    # 检查服务状态
    if pgrep -f "clawdbot-gateway" > /dev/null; then
        log_info "服务启动成功"
        return 0
    else
        log_error "服务启动失败"
        return 1
    fi
}

# 清理旧日志
cleanup_logs() {
    if [ -f "$LOG_FILE" ]; then
        # 保留最后 N 行
        tail -n $MAX_LOG_LINES "$LOG_FILE" > "$LOG_FILE.tmp" 2>/dev/null || true
        mv "$LOG_FILE.tmp" "$LOG_FILE" 2>/dev/null || true
    fi
}

# 发送通知到 Feishu
send_notification() {
    local status=$1
    local message=$2

    if [ -n "$FEISHU_USER_ID" ]; then
        log_info "发送通知到 Feishu..."

        case $status in
            "success")
                emoji="✅"
                ;;
            "error")
                emoji="❌"
                ;;
            "warning")
                emoji="⚠️"
                ;;
        esac

        clawdbot message send \
            --channel feishu \
            --target "$FEISHU_USER_ID" \
            --message "$emoji $message" >> "$LOG_FILE" 2>&1 || true
    fi
}

# 发送通知到 Slack
send_slack_notification() {
    local status=$1
    local message=$2

    if [ -n "$SLACK_DM_ID" ]; then
        log_info "发送通知到 Slack..."

        case $status in
            "success")
                emoji="✅"
                ;;
            "error")
                emoji="❌"
                ;;
            "warning")
                emoji="⚠️"
                ;;
        esac

        clawdbot message send \
            --channel slack \
            --target "$SLACK_DM_ID" \
            --message "$emoji $message" >> "$LOG_FILE" 2>&1 || true
    fi
}

# 主函数
main() {
    log_info "=========================================="
    log_info "Clawdbot 自动更新脚本启动"
    log_info "=========================================="
    echo ""

    # 检查是否强制更新
    if [ "$FORCE_UPDATE" = true ]; then
        log_warn "强制更新模式"
        do_update
        exit_code=$?

        if [ $exit_code -eq 0 ]; then
            send_notification "success" "Clawdbot 强制更新成功！"
            send_slack_notification "success" "Clawdbot 强制更新成功！"
        else
            send_notification "error" "Clawdbot 强制更新失败！"
            send_slack_notification "error" "Clawdbot 强制更新失败！"
        fi

        exit $exit_code
    fi

    # 正常更新流程
    if check_updates; then
        log_info "无需更新"
        exit 0
    fi

    # 执行更新
    if do_update; then
        log_info "更新成功！"
        send_notification "success" "Clawdbot 已自动更新到最新版本！"
        send_slack_notification "success" "Clawdbot 已自动更新到最新版本！"

        # 清理日志
        cleanup_logs

        log_info "=========================================="
        log_info "自动更新完成"
        log_info "=========================================="

        exit 0
    else
        log_error "更新失败！"
        send_notification "error" "Clawdbot 自动更新失败，请手动检查！"
        send_slack_notification "error" "Clawdbot 自动更新失败，请手动检查！"

        log_info "=========================================="
        log_info "自动更新失败"
        log_info "=========================================="

        exit 1
    fi
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE_UPDATE=true
            shift
            ;;
        --help)
            echo "Clawdbot 自动更新脚本"
            echo ""
            echo "用法:"
            echo "  $0              # 检查并更新（如果有新版本）"
            echo "  $0 --force      # 强制更新（无论是否有新版本）"
            echo ""
            echo "环境变量:"
            echo "  FEISHU_USER_ID  # Feishu 用户 ID（用于发送通知）"
            echo "  SLACK_DM_ID      # Slack DM Channel ID（用于发送通知）"
            echo ""
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 --help 查看帮助"
            exit 1
            ;;
    esac
done

# 运行主函数
main
