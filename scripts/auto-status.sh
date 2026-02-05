#!/bin/bash
# 自动化系统状态检查工具

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

CONFIG_FILE="/root/clawd/automation-config.json"
WORKSPACE="/root/clawd"

echo -e "${PURPLE}========================================${NC}"
echo -e "${PURPLE}自动化系统状态检查${NC}"
echo -e "${PURPLE}========================================${NC}"
echo ""

# ==================== 1. 配置检查 ====================
echo -e "${BLUE}1. 配置检查${NC}"
echo ""

if [ -f "$CONFIG_FILE" ]; then
    enabled=$(jq -r '.pipeline.enabled' "$CONFIG_FILE")
    schedule=$(jq -r '.pipeline.schedule' "$CONFIG_FILE")
    min_score=$(jq -r '.quality.min_score_for_publish' "$CONFIG_FILE")

    echo "  配置文件: ${GREEN}✅${NC} 存在"
    echo "  流水线状态: $([ "$enabled" == "true" ] && echo -e "${GREEN}启用${NC}" || echo -e "${RED}禁用${NC}")"
    echo "  调度: $schedule"
    echo "  发布阈值: $min_score 分"
else
    echo -e "  配置文件: ${RED}❌ 不存在${NC}"
fi
echo ""

# ==================== 2. Cron 检查 ====================
echo -e "${BLUE}2. Cron 任务检查${NC}"
echo ""

cron_count=$(crontab -l 2>/dev/null | grep -c "full-auto-pipeline.sh")
if [ -z "$cron_count" ]; then cron_count=0; fi

if [ "$cron_count" -gt 0 ] 2>/dev/null; then
    echo -e "  Cron 状态: ${GREEN}✅ 已配置${NC}"
    echo "  任务数: $cron_count"
    crontab -l 2>/dev/null | grep "full-auto-pipeline.sh" | sed 's/^/    /'
else
    echo -e "  Cron 状态: ${YELLOW}⚠️  未配置${NC}"
fi
echo ""

# ==================== 3. 目录检查 ====================
echo -e "${BLUE}3. 目录检查${NC}"
echo ""

for dir in "$WORKSPACE/reports" "$WORKSPACE/logs" "$WORKSPACE/dist" "$WORKSPACE/test-dist"; do
    if [ -d "$dir" ]; then
        file_count=$(find "$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  $dir: ${GREEN}✅${NC} ($file_count 文件)"
    else
        echo -e "  $dir: ${RED}❌ 不存在${NC}"
    fi
done
echo ""

# ==================== 4. 认证检查 ====================
echo -e "${BLUE}4. 认证检查${NC}"
echo ""

if command -v clawdhub &> /dev/null; then
    if clawdhub whoami &> /dev/null; then
        user=$(clawdhub whoami 2>/dev/null | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
        echo -e "  ClawdHub: ${GREEN}✅ 已登录${NC} ($user)"
    else
        echo -e "  ClawdHub: ${YELLOW}⚠️  未登录${NC}"
    fi
else
    echo -e "  ClawdHub: ${RED}❌ 未安装${NC}"
fi

if [ -f ~/.bashrc ] && grep -q "TWITTER_API_KEY" ~/.bashrc; then
    echo -e "  Twitter API: ${GREEN}✅ 已配置${NC}"
else
    echo -e "  Twitter API: ${YELLOW}⚠️  未配置${NC}"
fi
echo ""

# ==================== 5. 最近执行检查 ====================
echo -e "${BLUE}5. 最近执行记录${NC}"
echo ""

recent_logs=$(ls -t /root/clawd/logs/pipeline-*.log 2>/dev/null | head -3)
if [ -z "$recent_logs" ]; then
    echo "  暂无执行记录"
else
    echo "$recent_logs" | while read log_file; do
        log_name=$(basename "$log_file")
        log_time=$(echo "$log_name" | sed 's/pipeline-//' | sed 's/.log//')
        if tail -1 "$log_file" | grep -q "流水线执行完成"; then
            status="${GREEN}✅ 成功${NC}"
        else
            status="${RED}❌ 失败${NC}"
        fi
        echo "  $log_time: $status"
    done
fi
echo ""

# ==================== 6. 数据统计 ====================
echo -e "${BLUE}6. 数据统计${NC}"
echo ""

total_prompts=0
find /root/clawd/data/prompts -name "*.jsonl" -type f 2>/dev/null | while read -r file; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file" 2>/dev/null || echo "0")
        total_prompts=$((total_prompts + lines))
    fi
done

if [ "$total_prompts" -gt 0 ]; then
    echo "  收集的提示词: $total_prompts 条"
else
    echo "  收集的提示词: 暂无"
fi

generated_skills=$(find /root/clawd/test-dist -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "  生成的 Skills: $generated_skills"

published_skills=$(find /root/clawd/dist -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "  发布的 Skills: $published_skills"
echo ""

# ==================== 7. 回滚状态 ====================
echo -e "${BLUE}7. 回滚系统${NC}"
echo ""

rollback_log="/root/clawd/logs/rollback-history.jsonl"
if [ -f "$rollback_log" ]; then
    rollback_count=$(wc -l < "$rollback_log" | tr -d ' ')
    echo "  回滚记录: $rollback_count 条"
    if [ "$rollback_count" -gt 0 ]; then
        last_rollback=$(tail -1 "$rollback_log" | jq -r '.timestamp')
        echo "  最近记录: $last_rollback"
    fi
else
    echo "  回滚记录: 暂无"
fi
echo ""

# ==================== 总结 ====================
echo -e "${BLUE}========================================${NC}"

issues=0
[ -f "$CONFIG_FILE" ] || issues=$((issues + 1))
[ "$cron_count" -gt 0 ] || issues=$((issues + 1))
command -v clawdhub &> /dev/null && clawdhub whoami &> /dev/null || issues=$((issues + 1))

if [ $issues -eq 0 ]; then
    echo -e "${GREEN}✅ 系统状态良好${NC}"
else
    echo -e "${YELLOW}⚠️  发现 $issues 个问题，建议处理${NC}"
fi

echo -e "${BLUE}========================================${NC}"
echo ""
echo "常用命令:"
echo "  查看回滚记录: bash /root/clawd/scripts/rollback-manager.sh list"
echo "  手动运行流水线: bash /root/clawd/scripts/full-auto-pipeline.sh"
echo "  查看执行日志: tail -f /root/clawd/logs/pipeline-*.log"
echo "  设置 Cron 任务: bash /root/clawd/scripts/setup-auto-pipeline.sh"
echo ""
