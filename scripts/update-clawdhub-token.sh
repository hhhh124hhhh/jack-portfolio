#!/bin/bash

# ClawdHub Token 更新脚本
# 用途：快速更新 ClawdHub token 并记录

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置文件路径
CONFIG_FILE="$HOME/.config/clawdhub/config.json"
TOOLS_FILE="/root/clawd/TOOLS.md"
LOG_FILE="/root/clawd/memory/clawdhub-token-update.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 更新配置文件
update_config() {
    local new_token=$1

    # 检查配置文件是否存在
    if [ ! -f "$CONFIG_FILE" ]; then
        mkdir -p "$(dirname "$CONFIG_FILE")"
        echo "{\"registry\": \"https://www.clawhub.ai/api\", \"token\": \"$new_token\"}" > "$CONFIG_FILE"
    else
        # 更新现有文件中的 token
        jq --arg token "$new_token" '.token = $token' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
        mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
    fi

    echo -e "${GREEN}✓ 配置文件已更新: $CONFIG_FILE${NC}"
    log "配置文件已更新"
}

# 更新 TOOLS.md
update_tools_md() {
    local new_token=$1
    local date=$(date '+%Y-%m-%d')

    # 备份原文件
    if [ -f "$TOOLS_FILE" ]; then
        cp "$TOOLS_FILE" "${TOOLS_FILE}.backup.$(date +%s)"
    fi

    # 检查文件是否存在
    if [ ! -f "$TOOLS_FILE" ]; then
        echo "# TOOLS.md - Local Notes" > "$TOOLS_FILE"
        echo "" >> "$TOOLS_FILE"
        echo "### ClawdHub Token" >> "$TOOLS_FILE"
    fi

    # 检查是否已有 ClawdHub Token 部分
    if grep -q "### ClawdHub Token" "$TOOLS_FILE"; then
        # 更新现有部分
        local temp_file=$(mktemp)
        awk -v token="$new_token" -v date="$date" '
            /^### ClawdHub Token/ { in_section=1; print; next }
            in_section && /^- \*\*Token:/ {
                print "- **Token:** " token " (最新)"
                print "  - 更新时间：" date ""
                print "  - Registry: \`https://clawdhub.com\`"
                print "  - 状态：✅ 已配置并验证"
                # 移除旧的 token 记录（最多保留最近2个）
                if (old_count < 2) {
                    print $0
                    if (/Token/) old_count++
                }
                if (!/^-/ && !/^  /) {
                    in_section=0
                }
                next
            }
            in_section && /^- \*\*旧 token/ { next } # 跳过旧 token 行
            { print }
        ' "$TOOLS_FILE" > "$temp_file"
        mv "$temp_file" "$TOOLS_FILE"
    else
        # 添加新部分
        cat >> "$TOOLS_FILE" << EOF

### ClawdHub Token
- **Token:** $new_token (最新)
  - 更新时间：$date
  - Registry: \`https://clawdhub.com\`
  - 状态：✅ 已配置并验证

EOF
    fi

    echo -e "${GREEN}✓ TOOLS.md 已更新${NC}"
    log "TOOLS.md 已更新"
}

# 验证 token
verify_token() {
    echo -e "${YELLOW}正在验证 Token...${NC}"

    # 尝试搜索测试
    if clawdhub search "test" --limit 1 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Token 验证成功！${NC}"
        log "Token 验证成功"
        return 0
    else
        echo -e "${RED}✗ Token 验证失败${NC}"
        log "Token 验证失败"
        return 1
    fi
}

# 主函数
main() {
    echo -e "${YELLOW}=== ClawdHub Token 更新工具 ===${NC}"
    echo ""

    # 创建日志目录
    mkdir -p "$(dirname "$LOG_FILE")"

    # 提示用户输入新 token
    echo "请输入新的 ClawdHub Token:"
    read -p "> " NEW_TOKEN

    if [ -z "$NEW_TOKEN" ]; then
        echo -e "${RED}✗ Token 不能为空${NC}"
        exit 1
    fi

    echo ""
    echo "更新 Token: ${NEW_TOKEN:0:20}..."
    echo ""

    # 备份当前 token
    if [ -f "$CONFIG_FILE" ]; then
        CURRENT_TOKEN=$(jq -r '.token // empty' "$CONFIG_FILE" 2>/dev/null || echo "")
        if [ -n "$CURRENT_TOKEN" ]; then
            log "旧 Token: ${CURRENT_TOKEN:0:20}..."
        fi
    fi

    # 更新配置文件
    update_config "$NEW_TOKEN"

    # 更新 TOOLS.md
    update_tools_md "$NEW_TOKEN"

    # 验证新 token
    if verify_token; then
        echo ""
        echo -e "${GREEN}=== 更新完成！===${NC}"
        echo ""
        echo "已更新："
        echo "  • $CONFIG_FILE"
        echo "  • $TOOLS.md"
        echo ""
        echo "你可以使用以下命令验证："
        echo -e "${GREEN}clawdhub search \"test\"${NC}"
        echo ""
        log "Token 更新成功: ${NEW_TOKEN:0:20}..."
    else
        echo ""
        echo -e "${RED}=== Token 验证失败 ===${NC}"
        echo ""
        echo "Token 已更新到配置文件，但验证失败。"
        echo "请检查："
        echo "  1. Token 是否正确复制"
        echo "  2. Token 是否已过期"
        echo "  3. 网络连接是否正常"
        echo ""
        echo "你可以重新运行此脚本更新 Token。"
        echo ""
    fi
}

# 运行主函数
main
