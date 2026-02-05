#!/bin/bash

# 备份并清理记忆，释放上下文空间
# 作者：Momo
# 创建日期：2026-02-05

set -e

# 配置
BACKUP_DIR="/root/clawd/memory/backups"
MEMORY_FILE="/root/clawd/MEMORY.md"
DAILY_MEMORY_DIR="/root/clawd/memory"
LOG_FILE="/root/clawd/logs/memory-flush.log"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# 创建目录
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "开始备份和清理记忆..."

# ========== 步骤 1：记录清理前的上下文占用 ==========
log "步骤 1：记录清理前的上下文占用"

BEFORE_SOUL_SIZE=$(wc -c < /root/clawd/SOUL.md 2>/dev/null || echo 0)
BEFORE_USER_SIZE=$(wc -c < /root/clawd/USER.md 2>/dev/null || echo 0)
BEFORE_MEMORY_SIZE=$(wc -c < "$MEMORY_FILE" 2>/dev/null || echo 0)
BEFORE_DAILY_COUNT=$(find "$DAILY_MEMORY_DIR" -name "*.md" -type f 2>/dev/null | wc -l)
BEFORE_DAILY_SIZE=$(du -sh "$DAILY_MEMORY_DIR" 2>/dev/null | cut -f1 || echo "0B")

# 估算 tokens（假设 1 token ≈ 4 字符）
BEFORE_SOUL_TOKENS=$((BEFORE_SOUL_SIZE / 4))
BEFORE_USER_TOKENS=$((BEFORE_USER_SIZE / 4))
BEFORE_MEMORY_TOKENS=$((BEFORE_MEMORY_SIZE / 4))
BEFORE_TOTAL_TOKENS=$((BEFORE_SOUL_TOKENS + BEFORE_USER_TOKENS + BEFORE_MEMORY_TOKENS))

log "清理前上下文占用："
log "  - SOUL.md: $BEFORE_SOUL_SIZE bytes ≈ $BEFORE_SOUL_TOKENS tokens"
log "  - USER.md: $BEFORE_USER_SIZE bytes ≈ $BEFORE_USER_TOKENS tokens"
log "  - MEMORY.md: $BEFORE_MEMORY_SIZE bytes ≈ $BEFORE_MEMORY_TOKENS tokens"
log "  - Daily memory: $BEFORE_DAILY_COUNT files, $BEFORE_DAILY_SIZE"
log "  - 总计 (不含 daily): $BEFORE_TOTAL_TOKENS tokens"

# ========== 步骤 2：备份 MEMORY.md ==========
log "步骤 2：备份 MEMORY.md"

if [ -f "$MEMORY_FILE" ]; then
    cp "$MEMORY_FILE" "$BACKUP_DIR/MEMORY.md.$TIMESTAMP"
    BACKUP_SIZE=$(wc -c < "$BACKUP_DIR/MEMORY.md.$TIMESTAMP")
    log "✅ MEMORY.md 备份到 $BACKUP_DIR/MEMORY.md.$TIMESTAMP ($BACKUP_SIZE bytes)"
else
    log "⚠️  MEMORY.md 不存在，跳过备份"
fi

# ========== 步骤 3：备份 daily memory ==========
log "步骤 3：备份 daily memory"

TODAY_FILE="$DAILY_MEMORY_DIR/$(date +%Y-%m-%d).md"
if [ -f "$TODAY_FILE" ]; then
    cp "$TODAY_FILE" "$BACKUP_DIR/daily-$(date +%Y%m%d).md.$TIMESTAMP"
    BACKUP_SIZE=$(wc -c < "$BACKUP_DIR/daily-$(date +%Y%m%d).md.$TIMESTAMP")
    log "✅ Daily memory 备份到 $BACKUP_DIR/daily-$(date +%Y%m%d).md.$TIMESTAMP ($BACKUP_SIZE bytes)"
else
    log "⚠️  今天的 daily memory 不存在，跳过备份"
fi

# ========== 步骤 4：清理 MEMORY.md ==========
log "步骤 4：清理 MEMORY.md"

cat > "$MEMORY_FILE" << 'EOF'
# MEMORY.md - 核心记忆

*记忆已备份，可以通过 memory-manager 查询历史记忆*
*备份目录：/root/clawd/memory/backups*

## 重要记忆

*此部分保留最重要的长期记忆，不会被清理*

EOF

AFTER_MEMORY_SIZE=$(wc -c < "$MEMORY_FILE")
log "✅ MEMORY.md 已清理（$AFTER_MEMORY_SIZE bytes）"

# ========== 步骤 5：清理 old daily memory（保留最近 1 天）==========
log "步骤 5：清理 old daily memory（保留最近 1 天）"

BEFORE_DAILY_COUNT=$(find "$DAILY_MEMORY_DIR" -name "*.md" -type f | wc -l)
BEFORE_DAILY_SIZE=$(du -sh "$DAILY_MEMORY_DIR" 2>/dev/null | cut -f1 || echo "0B")

# 保留最近 1 天的 daily memory
find "$DAILY_MEMORY_DIR" -name "*.md" -type f -mtime +1 -delete

AFTER_DAILY_COUNT=$(find "$DAILY_MEMORY_DIR" -name "*.md" -type f | wc -l)
AFTER_DAILY_SIZE=$(du -sh "$DAILY_MEMORY_DIR" 2>/dev/null | cut -f1 || echo "0B")
DELETED_COUNT=$((BEFORE_DAILY_COUNT - AFTER_DAILY_COUNT))

log "✅ Old daily memory 已清理（保留最近 1 天，删除了 $DELETED_COUNT 个文件）"

# ========== 步骤 6：记录清理后的上下文占用 ==========
log "步骤 6：记录清理后的上下文占用"

AFTER_SOUL_SIZE=$(wc -c < /root/clawd/SOUL.md 2>/dev/null || echo 0)
AFTER_USER_SIZE=$(wc -c < /root/clawd/USER.md 2>/dev/null || echo 0)
AFTER_MEMORY_SIZE=$(wc -c < "$MEMORY_FILE" 2>/dev/null || echo 0)
AFTER_DAILY_COUNT=$(find "$DAILY_MEMORY_DIR" -name "*.md" -type f 2>/dev/null | wc -l)
AFTER_DAILY_SIZE=$(du -sh "$DAILY_MEMORY_DIR" 2>/dev/null | cut -f1 || echo "0B")

AFTER_SOUL_TOKENS=$((AFTER_SOUL_SIZE / 4))
AFTER_USER_TOKENS=$((AFTER_USER_SIZE / 4))
AFTER_MEMORY_TOKENS=$((AFTER_MEMORY_SIZE / 4))
AFTER_TOTAL_TOKENS=$((AFTER_SOUL_TOKENS + AFTER_USER_TOKENS + AFTER_MEMORY_TOKENS))

log "清理后上下文占用："
log "  - SOUL.md: $AFTER_SOUL_SIZE bytes ≈ $AFTER_SOUL_TOKENS tokens"
log "  - USER.md: $AFTER_USER_SIZE bytes ≈ $AFTER_USER_TOKENS tokens"
log "  - MEMORY.md: $AFTER_MEMORY_SIZE bytes ≈ $AFTER_MEMORY_TOKENS tokens"
log "  - Daily memory: $AFTER_DAILY_COUNT files, $BEFORE_DAILY_SIZE → $AFTER_DAILY_SIZE"
log "  - 总计 (不含 daily): $AFTER_TOTAL_TOKENS tokens"
log "  - Daily memory 文件数: $BEFORE_DAILY_COUNT → $AFTER_DAILY_COUNT (删除 $DELETED_COUNT 个)"

# ========== 步骤 7：计算对比 ==========
log "步骤 7：计算对比"

SAVED_TOKENS=$((BEFORE_TOTAL_TOKENS - AFTER_TOTAL_TOKENS))
SAVED_PERCENT=$(echo "scale=1; $SAVED_TOKENS * 100 / $BEFORE_TOTAL_TOKENS" | bc)

AVAILABLE_BEFORE=$((131000 - BEFORE_TOTAL_TOKENS))
AVAILABLE_AFTER=$((131000 - AFTER_TOTAL_TOKENS))
IMPROVEMENT=$((AVAILABLE_AFTER - AVAILABLE_BEFORE))

log "对比结果："
log "  - 节省 tokens: $SAVED_TOKENS ($SAVED_PERCENT%)"
log "  - 清理前可用上下文: $AVAILABLE_BEFORE tokens"
log "  - 清理后可用上下文: $AVAILABLE_AFTER tokens"
log "  - 提升可用上下文: $IMPROVEMENT tokens ($(echo "scale=1; $IMPROVEMENT * 100 / $AVAILABLE_BEFORE" | bc)%)"

# ========== 完成 ==========
log "🎉 备份和清理完成！"
log "💡 下次会话启动时，上下文将更加宽松。"

# 记录到 daily memory
python3 /root/clawd/scripts/memory-manager.py memorize "记忆备份清理（$TIMESTAMP）：清理前 $BEFORE_TOTAL_TOKENS tokens，清理后 $AFTER_TOTAL_TOKENS tokens，节省 $SAVED_TOKENS tokens ($SAVED_PERCENT%)，可用上下文从 $AVAILABLE_BEFORE 提升到 $AVAILABLE_AFTER tokens（+$(echo "scale=1; $IMPROVEMENT * 100 / $AVAILABLE_BEFORE" | bc)%）" "general" 2>/dev/null || true

exit 0
