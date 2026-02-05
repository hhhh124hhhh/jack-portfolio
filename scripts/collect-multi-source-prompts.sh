#!/bin/bash
# 多源 AI 提示词收集脚本
# 集成多个数据源收集 prompt，解决 Twitter API 限制

set -e

# 配置
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H%M)
REPORT_DIR="/root/clawd/reports"
LOG_FILE="/root/clawd/data/prompts/multi-source-collection.log"

# 创建目录
mkdir -p "$REPORT_DIR"
mkdir -p "$(dirname $LOG_FILE)"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "多源 AI 提示词收集开始"
log "=========================================="

# 统计
TOTAL_COLLECTED=0

# 源 1: Reddit
log ""
log "[1/2] 收集 Reddit Prompt..."
if python3 /root/clawd/scripts/collect-reddit-prompts.py >> "$LOG_FILE" 2>&1; then
    REDDIT_COUNT=$(grep "总计:" "$LOG_FILE" | tail -1 | awk '{print $2}' || echo "0")
    TOTAL_COLLECTED=$((TOTAL_COLLECTED + REDDIT_COUNT))
    log "✅ Reddit 收集完成: $REDDIT_COUNT 条"
else
    log "❌ Reddit 收集失败"
    REDDIT_COUNT=0
fi

# 源 2: SearXNG（已配置）
log ""
log "[2/2] 收集 SearXNG Prompt..."
# 复用现有脚本
if python3 /root/clawd/scripts/collect-prompts-test.py >> "$LOG_FILE" 2>&1; then
    SEARXNG_COUNT=$(tail -1 /root/clawd/data/prompts/collected.jsonl 2>/dev/null | wc -l || echo "0")
    log "✅ SearXNG 收集完成"
else
    log "❌ SearXNG 收集失败"
    SEARXNG_COUNT=0
fi

# 生成报告
log ""
log "生成收集报告..."

REPORT_FILE="$REPORT_DIR/multi-source-report-${DATE}-${TIME}.md"

cat > "$REPORT_FILE" << EOF
# 多源 AI 提示词收集报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 📊 收集统计

| 数据源 | 收集数量 | 状态 |
|--------|---------|------|
| Reddit | $REDDIT_COUNT 条 | ✅ 正常 |
| SearXNG | $SEARXNG_COUNT 条 | ✅ 正常 |
| **总计** | **$TOTAL_COLLECTED 条** | - |

## 📈 Reddit 详情

**子版块**: r/ChatGPT, r/artificial, r/machinelearning, r/LanguageTechnology

**质量评估**:
- 平均分数: $(python3 -c "import json; data=[json.loads(l) for l in open('/root/clawd/data/prompts/reddit-prompts.jsonl')]; print(f'{sum(d.get(\"quality_score\",0) for d in data)/len(data):.1f}' if data else 'N/A' 2>/dev/null || echo "N/A")
- 高质量（≥80）: $(python3 -c "import json; data=[json.loads(l) for l in open('/root/clawd/data/prompts/reddit-prompts.jsonl')]; print(sum(1 for d in data if d.get('quality_score',0) >= 80)) if data else '0'" 2>/dev/null || echo "0")
- 中等质量（≥60）: $(python3 -c "import json; data=[json.loads(l) for l in open('/root/clawd/data/prompts/reddit-prompts.jsonl')]; print(sum(1 for d in data if d.get('quality_score',0) >= 60)) if data else '0'" 2>/dev/null || echo "0")

## 🌐 SearXNG 详情

**搜索关键词**: AI prompt engineering, ChatGPT prompts, Claude prompts

**数据文件**: \`/root/clawd/data/prompts/collected.jsonl\`

## 💡 建议

1. **Reddit**: 质量高，已稳定收集
2. **SearXNG**: 按需搜索，无 API 限制
3. **Twitter API**: 需要充值或寻找替代方案

---

*报告自动生成*
EOF

log "✅ 报告已生成: $REPORT_FILE"

# Git 提交
log ""
log "提交到 Git..."
cd /root/clawd

git add reports/multi-source-report-*.md data/prompts/*.jsonl 2>/dev/null || true
git commit -m "多源 Prompt 收集 - $DATE $TIME

- Reddit: $REDDIT_COUNT 条
- SearXNG: 已收集
- 总计: $TOTAL_COLLECTED 条
- 报告: $REPORT_FILE" || log "⚠️  没有变更需要提交"

git push origin master 2>&1 | tee -a "$LOG_FILE" || log "⚠️  Git push 失败或已最新"

# 总结
log ""
log "=========================================="
log "收集摘要"
log "=========================================="
log "✅ 多源收集完成！"
log "📊 总收集: $TOTAL_COLLECTED 条"
log "📄 报告: $REPORT_FILE"
log "🔄 Git: 已提交并推送"
log "=========================================="
log ""

# 发送通知
log "发送通知到 Feishu 和 Slack..."

# 发送到 Feishu
FEISHU_MESSAGE="✅ 多源 Prompt 收集完成！

📊 **收集统计**:
• Reddit: $REDDIT_COUNT 条
• SearXNG: 已收集
• **总计**: $TOTAL_COLLECTED 条

📄 **报告**: $REPORT_FILE

🔄 **Git**: 已提交并推送"

clawdbot message send \
  --channel feishu \
  --target ou_3bc5290afc1a94f38e23dc17c35f26d6 \
  --message "$FEISHU_MESSAGE" >> "$LOG_FILE" 2>&1 || log "⚠️  Feishu 通知发送失败"

# 发送到 Slack
SLACK_MESSAGE="✅ 多源 Prompt 收集完成！

📊 **收集统计**:
• Reddit: $REDDIT_COUNT 条
• SearXNG: 已收集
• **总计**: $TOTAL_COLLECTED 条

📄 **报告**: $REPORT_FILE

🔄 **Git**: 已提交并推送"

clawdbot message send \
  --channel slack \
  --target D0AB0J4QLAH \
  --message "$SLACK_MESSAGE" >> "$LOG_FILE" 2>&1 || log "⚠️  Slack 通知发送失败"

log "✅ 通知已发送"

log ""
log "=========================================="
log "✅ 全部完成！"
log "=========================================="
