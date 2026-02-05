#!/bin/bash

# ClawdHub Token 检测脚本
# 用途：检测 token 有效性，提供更新提醒

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置文件路径
CONFIG_FILE="$HOME/.config/clawdhub/config.json"
TOOLS_FILE="/root/clawd/TOOLS.md"
LOG_FILE="/root/clawd/memory/clawdhub-token-check.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查配置文件是否存在
check_config_file() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}✗ 配置文件不存在: $CONFIG_FILE${NC}"
        log "ERROR: 配置文件不存在"
        exit 1
    fi
}

# 提取当前 token
get_current_token() {
    jq -r '.token // empty' "$CONFIG_FILE" 2>/dev/null || echo ""
}

# 测试 token 是否有效
test_token() {
    local token=$1

    # 尝试执行 clawdhub search 命令测试
    if clawdhub search "test" --limit 1 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Token 有效${NC}"
        log "Token 有效: ${token:0:20}..."
        return 0
    else
        echo -e "${RED}✗ Token 无效${NC}"
        log "Token 无效: ${token:0:20}..."
        return 1
    fi
}

# 获取 token 更新建议
get_update_advice() {
    echo ""
    echo -e "${YELLOW}=== Token 更新指南 ===${NC}"
    echo ""
    echo "1. 访问 https://clawdhub.com"
    echo "2. 登录你的账户"
    echo "3. 进入设置/个人资料页面获取新的 token"
    echo "4. 运行以下命令更新配置："
    echo ""
    echo -e "${GREEN}cat > ~/.config/clawdhub/config.json << 'EOF'{\n  \"registry\": \"https://www.clawhub.ai/api\",\n  \"token\": \"你的新token\"\n}EOF${NC}"
    echo ""
    echo "或者运行："
    echo -e "${GREEN}clawdhub auth login${NC}"
    echo "   (需要浏览器环境)"
    echo ""
    echo "5. 更新 /root/clawd/TOOLS.md 中的 token 信息"
    echo ""
}

# 更新 TOOLS.md 记录
update_tools_md() {
    local token=$1
    local date=$(date '+%Y-%m-%d')

    # 备份原文件
    cp "$TOOLS_FILE" "${TOOLS_FILE}.backup.$(date +%s)"

    # 更新 token 信息 (使用临时文件)
    local temp_file=$(mktemp)
    awk -v token="$token" -v date="$date" '
        /^### ClawdHub Token/ { in_section=1 }
        in_section && /- \*\*Token:/ { $0 = "- **Token:** " token " (最新)\n  - 更新时间：" date ""; in_section=0 }
        in_section && /- \*\*旧 token/ { in_section=0 }
        { print }
    ' "$TOOLS_FILE" > "$temp_file"

    mv "$temp_file" "$TOOLS_FILE"

    log "已更新 TOOLS.md"
    echo -e "${GREEN}✓ 已更新 TOOLS.md${NC}"
}

# 主函数
main() {
    echo -e "${YELLOW}=== ClawdHub Token 检测 ===${NC}"
    echo ""

    # 创建日志目录
    mkdir -p "$(dirname "$LOG_FILE")"

    # 检查配置文件
    check_config_file

    # 获取当前 token
    local token=$(get_current_token)

    if [ -z "$token" ]; then
        echo -e "${RED}✗ 未找到 Token${NC}"
        log "ERROR: 未找到 token"
        get_update_advice
        exit 1
    fi

    echo "当前 Token: ${token:0:20}..."
    echo ""

    # 测试 token
    if test_token "$token"; then
        # Token 有效，询问是否更新记录
        echo ""
        read -p "是否要更新 TOOLS.md 记录？(y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            update_tools_md "$token"
        fi
        exit 0
    else
        # Token 无效
        get_update_advice

        # 询问是否更新 TOOLS.md 记录新 token
        echo -e "${YELLOW}是否现在输入新的 token？(y/n)${NC}"
        read -p "> " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "请输入新的 token: " new_token

            if [ -n "$new_token" ]; then
                # 更新配置文件
                jq --arg token "$new_token" '.token = $token' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
                mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"

                echo ""
                echo -e "${GREEN}✓ 配置已更新${NC}"
                log "Token 已更新: ${new_token:0:20}..."

                # 再次测试
                if test_token "$new_token"; then
                    update_tools_md "$new_token"
                    echo -e "${GREEN}✓ Token 更新成功！${NC}"
                else
                    echo -e "${RED}✗ 新 token 无效，请检查${NC}"
                fi
            fi
        fi

        exit 1
    fi
}

# 运行主函数
main
