#!/bin/bash
# Achievement System Uninstallation Script

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
INSTALL_DIR="/usr/local/lib/achievement-system"
BIN_DIR="/usr/local/bin"
DATA_DIR="$HOME/.local/share/achievement-system"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}  成就系统卸载脚本${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用 sudo 运行此脚本${NC}"
    exit 1
fi

# 警告
echo -e "${RED}警告: 此操作将删除以下内容:${NC}"
echo -e "  ${YELLOW}$INSTALL_DIR${NC}"
echo -e "  ${YELLOW}$BIN_DIR/ach${NC}"
echo -e "  ${YELLOW}$DATA_DIR${NC} (用户数据)"
echo ""

read -p "确定要卸载吗？(yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}取消卸载${NC}"
    exit 0
fi

# 删除文件
echo -e "${YELLOW}删除文件...${NC}"

if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo -e "${GREEN}✓ 已删除: $INSTALL_DIR${NC}"
fi

if [ -f "$BIN_DIR/ach" ]; then
    rm -f "$BIN_DIR/ach"
    echo -e "${GREEN}✓ 已删除: $BIN_DIR/ach${NC}"
fi

if [ -d "$DATA_DIR" ]; then
    rm -rf "$DATA_DIR"
    echo -e "${GREEN}✓ 已删除: $DATA_DIR${NC}"
fi

# 完成
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}  卸载完成！${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
