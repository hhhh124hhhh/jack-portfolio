#!/bin/bash
# Achievement System Installation Script

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
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}  成就系统安装脚本${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用 sudo 运行此脚本${NC}"
    exit 1
fi

# 检查 Python
echo -e "${YELLOW}检查 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 已安装: $(python3 --version)${NC}"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}提示: pip3 未安装，正在安装...${NC}"
    apt-get update && apt-get install -y python3-pip
fi
echo -e "${GREEN}✓ pip3 已安装${NC}"

# 创建目录
echo -e "${YELLOW}创建目录...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$DATA_DIR"
echo -e "${GREEN}✓ 目录创建完成${NC}"

# 复制文件
echo -e "${YELLOW}复制文件...${NC}"
cp -r "$REPO_DIR/src" "$INSTALL_DIR/"
cp "$REPO_DIR/requirements.txt" "$INSTALL_DIR/"
echo -e "${GREEN}✓ 文件复制完成${NC}"

# 安装依赖
echo -e "${YELLOW}安装 Python 依赖...${NC}"
pip3 install --break-system-packages --ignore-installed -q -r "$INSTALL_DIR/requirements.txt"
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# 创建可执行命令
echo -e "${YELLOW}创建可执行命令...${NC}"
cat > "$BIN_DIR/ach" << 'EOF'
#!/bin/bash
# Achievement System CLI Wrapper

INSTALL_DIR="/usr/local/lib/achievement-system"
export PYTHONPATH="$INSTALL_DIR/src:$PYTHONPATH"

python3 -c "import sys; sys.path.insert(0, '$INSTALL_DIR/src'); from cli import cli; cli()" "$@"
EOF

chmod +x "$BIN_DIR/ach"
echo -e "${GREEN}✓ 可执行命令创建完成: $BIN_DIR/ach${NC}"

# 测试安装
echo -e "${YELLOW}测试安装...${NC}"
if command -v ach &> /dev/null; then
    echo -e "${GREEN}✓ ach 命令可用${NC}"
    echo ""
    echo -e "${BLUE}─────────────────────────────────${NC}"
    ach --version
    echo -e "${BLUE}─────────────────────────────────${NC}"
    echo ""
else
    echo -e "${RED}错误: ach 命令不可用${NC}"
    exit 1
fi

# 完成
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}  安装完成！${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "${BLUE}数据目录:${NC} $DATA_DIR"
echo -e "${BLUE}安装目录:${NC} $INSTALL_DIR"
echo -e "${BLUE}可执行文件:${NC} $BIN_DIR/ach"
echo ""
echo -e "${YELLOW}快速开始:${NC}"
echo -e "  ${GREEN}ach init${NC}    # 初始化成就系统"
echo -e "  ${GREEN}ach list${NC}    # 查看所有成就"
echo -e "  ${GREEN}ach status${NC}  # 查看当前进度"
echo -e "  ${GREEN}ach stats${NC}   # 查看统计信息"
echo -e "  ${GREEN}ach --help${NC}  # 查看帮助"
echo ""
echo -e "${YELLOW}卸载:${NC}"
echo -e "  ${RED}sudo rm -rf $INSTALL_DIR${NC}"
echo -e "  ${RED}sudo rm $BIN_DIR/ach${NC}"
echo -e "  ${RED}rm -rf $DATA_DIR${NC}"
echo ""
