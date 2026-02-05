#!/bin/bash
# 检查环境变量配置

echo "======================================"
echo "环境变量检查"
echo "======================================"
echo ""

# 检查必需的环境变量
check_var() {
    local var_name=$1
    local required=$2

    if [ -z "${!var_name}" ]; then
        if [ "$required" = "required" ]; then
            echo "❌ $var_name 未设置（必需）"
            return 1
        else
            echo "⚠️  $var_name 未设置（可选）"
            return 0
        fi
    else
        echo "✅ $var_name 已设置"
        return 0
    fi
}

# 必需变量
check_var "ANTHROPIC_API_KEY" "required"
check_var "CLAWDHUB_TOKEN" "required"

echo ""

# 可选变量
check_var "GITHUB_TOKEN" "optional"
check_var "HUGGINGFACE_TOKEN" "optional"
check_var "TWITTER_API_KEY" "optional"
check_var "SEARXNG_URL" "optional"
check_var "FIRECRAWL_API_KEY" "optional"
check_var "LANGFUSE_PUBLIC_KEY" "optional"
check_var "LANGFUSE_SECRET_KEY" "optional"

echo ""
echo "======================================"
echo "Python 依赖检查"
echo "======================================"
echo ""

# 检查 Python 依赖
check_python_module() {
    local module=$1
    local required=$2

    if python3 -c "import $module" 2>/dev/null; then
        echo "✅ $module 已安装"
        return 0
    else
        if [ "$required" = "required" ]; then
            echo "❌ $module 未安装（必需）"
            return 1
        else
            echo "⚠️  $module 未安装（可选）"
            return 0
        fi
    fi
}

# 必需模块
check_python_module "yaml" "required"

# 可选模块
check_python_module "sentence_transformers" "optional"
check_python_module "anthropic" "optional"
check_python_module "langfuse" "optional"

echo ""
echo "======================================"
echo "CLI 工具检查"
echo "======================================"
echo ""

# 检查 CLI 工具
check_command() {
    local cmd=$1
    local required=$2

    if command -v $cmd >/dev/null 2>&1; then
        echo "✅ $cmd 已安装"
        return 0
    else
        if [ "$required" = "required" ]; then
            echo "❌ $cmd 未安装（必需）"
            return 1
        else
            echo "⚠️  $cmd 未安装（可选）"
            return 0
        fi
    fi
}

# 可选命令
check_command "bird" "optional"
check_command "clawdhub" "optional"

echo ""
echo "======================================"
echo "配置检查完成"
echo "======================================"
echo ""
echo "提示："
echo "1. 如果有必需项未设置，请配置环境变量"
echo "2. 如果有必需项未安装，请运行: pip install -r /root/clawd/skills/ai-prompt-workflow/requirements.txt"
echo "3. 首次使用建议先运行: bash /root/clawd/scripts/integrated-prompt-workflow.sh --test-mode"
