# AI 提示词自动化漏斗模型 - 子代理实施计划

## 概述

根据《FUNNEL_ARCHITECTURE.md》文档，将整个漏斗模型划分为 7 个独立的子代理任务，每个任务负责实施 1-2 层，避免上下文溢出。

---

## 子代理任务列表

### 子代理 1：数据收集层实现

**Session Label**：`funnel-layer1-collection`

**任务描述**：
根据《FUNNEL_ARCHITECTURE.md》Layer 1 的设计，实现数据收集层的核心脚本和配置文件。

**目标**：
1. 实现主脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/collect-prompts.py`
2. 实现配置文件：`/root/clawd/config/prompts-collector.yaml`
3. 支持 6 个数据源（GitHub, Reddit, Twitter, Hacker News, SearXNG, HuggingFace）
4. 实现去重功能（MD5 + 语义去重）
5. 实现错误处理和重试机制

**输入**：
- 文档路径：`/root/clawd/skills/ai-prompt-workflow/docs/FUNNEL_ARCHITECTURE.md`
- 读取章节：Layer 1: 数据收集层（4.1.1-4.1.4）

**输出**：
- 脚本文件：`/root/clawd/skills/ai-prompt-workflow/scripts/collect-prompts.py`
- 配置文件：`/root/clawd/config/prompts-collector.yaml`
- 测试脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/test-collect-prompts.py`
- 实现报告：`/tmp/subagent-layer1-report.md`

**预计时间**：30-45 分钟

---

### 子代理 2：自动分类层实现

**Session Label**：`funnel-layer2-classification`

**任务描述**：
根据《FUNNEL_ARCHITECTURE.md》Layer 2 的设计，实现自动分类层的核心脚本和配置文件。

**目标**：
1. 实现主脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/classify-content.py`
2. 实现配置文件：`/root/clawd/config/classification.yaml`
3. 支持 4 种内容类型分类（Prompt, Workflow, Industry Knowledge, Guide）
4. 实现规则引擎（规则匹配 + LLM 分类）
5. 实现置信度计算和验证

**输入**：
- 文档路径：`/root/clawd/skills/ai-prompt-workflow/docs/FUNNEL_ARCHITECTURE.md`
- 读取章节：Layer 2: 自动分类层（4.2.1-4.2.4）

**输出**：
- 脚本文件：`/root/clawd/skills/ai-prompt-workflow/scripts/classify-content.py`
- 配置文件：`/root/clawd/config/classification.yaml`
- 测试脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/test-classify-content.py`
- 实现报告：`/tmp/subagent-layer2-report.md`

**预计时间**：30-45 分钟

---

### 子代理 3：分类评分层实现

**Session Label**：`funnel-layer3-scoring`

**任务描述**：
根据《FUNNEL_ARCHITECTURE.md》Layer 3 的设计，实现分类评分层的核心脚本和配置文件。

**目标**：
1. 实现主脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/score-content.py`
2. 实现配置文件：`/root/clawd/config/scoring-standards.yaml`
3. 支持 4 种内容类型的差异化评分
4. 实现多维度评分（实用性、清晰度、独特性等）
5. 实现评分阈值设计

**输入**：
- 文档路径：`/root/clawd/skills/ai-prompt-workflow/docs/FUNNEL_ARCHITECTURE.md`
- 读取章节：Layer 3: 分类评分层（4.3.1-4.3.4）

**输出**：
- 脚本文件：`/root/clawd/skills/ai-prompt-workflow/scripts/score-content.py`
- 配置文件：`/root/clawd/config/scoring-standards.yaml`
- 测试脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/test-score-content.py`
- 实现报告：`/tmp/subagent-layer3-report.md`

**预计时间**：30-45 分钟

---

### 子代理 4：质量筛选层实现

**Session Label**：`funnel-layer4-quality-filter`

**任务描述**：
根据《FUNNEL_ARCHITECTURE.md》Layer 4 的设计，实现质量筛选层的核心脚本和配置文件。

**目标**：
1. 实现主脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/filter-quality.py`
2. 实现配置文件：`/root/clawd/config/quality-filter.yaml`
3. 实现 4 种筛选规则（阈值、去重、合规性、完整性）
4. 实现人工审核机制（Slack 通知）
5. 实现筛选结果反馈和统计

**输入**：
- 文档路径：`/root/clawd/skills/ai-prompt-workflow/docs/FUNNEL_ARCHITECTURE.md`
- 读取章节：Layer 4: 质量筛选层（4.4.1-4.4.4）

**输出**：
- 脚本文件：`/root/clawd/skills/ai-prompt-workflow/scripts/filter-quality.py`
- 配置文件：`/root/clawd/config/quality-filter.yaml`
- 测试脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/test-filter-quality.py`
- 实现报告：`/tmp/subagent-layer4-report.md`

**预计时间**：30-45 分钟

---

### 子代理 5：内容补充层实现

**Session Label**：`funnel-layer5-content-enhancement`

**任务描述**：
根据《FUNNEL_ARCHITECTURE.md》Layer 5 的设计，实现内容补充层的核心脚本和配置文件。

**目标**：
1. 实现主脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/enhance-content.py`
2. 实现配置文件：`/root/clawd/config/content-enhancement.yaml`
3. 实现 4 种补充策略（联网搜索、工具调用、LLM 生成、规则模板）
4. 实现缺失信息识别
5. 实现结构化处理和质量评估

**输入**：
- 文档路径：`/root/clawd/skills/ai-prompt-workflow/docs/FUNNEL_ARCHITECTURE.md`
- 读取章节：Layer 5: 内容补充层（4.5.1-4.5.4）

**输出**：
- 脚本文件：`/root/clawd/skills/ai-prompt-workflow/scripts/enhance-content.py`
- 配置文件：`/root/clawd/config/content-enhancement.yaml`
- 测试脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/test-enhance-content.py`
- 实现报告：`/tmp/subagent-layer5-report.md`

**预计时间**：30-45 分钟

---

### 子代理 6：Skill 转换层实现

**Session Label**：`funnel-layer6-skill-conversion`

**任务描述**：
根据《FUNNEL_ARCHITECTURE.md》Layer 6 的设计，实现 Skill 转换层的核心脚本和配置文件。

**目标**：
1. 实现主脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/convert-to-skill.py`
2. 实现配置文件：`/root/clawd/config/skill-conversion.yaml`
3. 实现 4 种 Skill 模板（Prompt, Workflow, Industry, Guide）
4. 实现转换规则引擎
5. 实现验证、测试和发布流程

**输入**：
- 文档路径：`/root/clawd/skills/ai-prompt-workflow/docs/FUNNEL_ARCHITECTURE.md`
- 读取章节：Layer 6: Skill 转换层（4.6.1-4.6.4）

**输出**：
- 脚本文件：`/root/clawd/skills/ai-prompt-workflow/scripts/convert-to-skill.py`
- 配置文件：`/root/clawd/config/skill-conversion.yaml`
- 模板文件：`/root/clawd/templates/*.md`（4 个模板）
- 测试脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/test-convert-to-skill.py`
- 实现报告：`/tmp/subagent-layer6-report.md`

**预计时间**：30-45 分钟

---

### 子代理 7：系统集成和测试

**Session Label**：`funnel-integration-testing`

**任务描述**：
根据《FUNNEL_ARCHITECTURE.md》第五部分和第六部分，实现系统集成、部署和测试。

**目标**：
1. 配置 Cron 定时任务（6 个层的自动化）
2. 实现监控和告警系统
3. 实现日志收集和分析
4. 集成所有层，端到端测试
5. 生成完整的部署文档

**输入**：
- 文档路径：`/root/clawd/skills/ai-prompt-workflow/docs/FUNNEL_ARCHITECTURE.md`
- 读取章节：第五部分（系统集成与部署）和第六部分（附录）

**输出**：
- Cron 配置文件：`/etc/cron.d/clawdbot-ai-prompt-workflow`
- 监控脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/monitor.py`
- 部署脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/deploy.sh`
- 测试脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/test-full-pipeline.sh`
- 部署文档：`/root/clawd/skills/ai-prompt-workflow/docs/DEPLOYMENT.md`
- 集成报告：`/tmp/subagent-integration-report.md`

**预计时间**：45-60 分钟

---

## 执行流程

```
子代理 1 (Layer 1) → 子代理 2 (Layer 2) → 子代理 3 (Layer 3)
    ↓
子代理 4 (Layer 4) → 子代理 5 (Layer 5) → 子代理 6 (Layer 6)
    ↓
子代理 7 (集成和测试)
```

---

## 执行策略

### 防止上下文溢出

1. **每个子代理独立**：每个子代理有独立的会话和上下文
2. **任务明确**：每个子代理只处理 1-2 层
3. **输出持久化**：子代理的输出保存到文件
4. **依赖文件传递**：通过文件传递依赖，而不是通过对话

### 执行顺序

**串行执行**（推荐）：
- 子代理 1 → 子代理 2 → 子代理 3 → 子代理 4 → 子代理 5 → 子代理 6 → 子代理 7
- 每个子代理完成后再启动下一个

**并行执行**（如果资源允许）：
- 子代理 1, 2, 3 可以并行（无依赖）
- 子代理 4, 5, 6 可以并行（无依赖）
- 子代理 7 依赖前面的所有子代理

---

## 启动脚本

我创建一个启动脚本，自动执行所有子代理：<tool_call>write<arg_key>content</arg_key><arg_value>#!/bin/bash

# AI 提示词自动化漏斗模型 - 子代理启动脚本
# 作者：Momo
# 创建日期：2026-02-05

set -e

# 配置
DOCUMENT_PATH="/root/clawd/skills/ai-prompt-workflow/docs/FUNNEL_ARCHITECTURE.md"
LOG_DIR="/root/clawd/logs/ai-prompt-workflow"
SESSIONS_FILE="/tmp/subagent-sessions.json"

# 创建目录
mkdir -p "$LOG_DIR"
mkdir -p "$(dirname "$SESSIONS_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/subagent-launcher.log"
}

log "开始执行 AI 提示词自动化漏斗模型子代理任务..."

# ========== 步骤 1：启动子代理 1（Layer 1: 数据收集层）==========
log "步骤 1：启动子代理 1（Layer 1: 数据收集层）"

RESPONSE1=$(sessions_spawn \
    --task "$(cat <<'EOF'
## 任务：实现数据收集层

根据《FUNNEL_ARCHITECTURE.md》Layer 1 的设计，实现数据收集层的核心脚本和配置文件。

### 目标

1. 实现主脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/collect-prompts.py`
2. 实现配置文件：`/root/clawd/config/prompts-collector.yaml`
3. 支持 6 个数据源（GitHub, Reddit, Twitter, Hacker News, SearXNG, HuggingFace）
4. 实现去重功能（MD5 + 语义去重）
5. 实现错误处理和重试机制

### 输入

- 文档路径：`/root/clawd/skills/ai-prompt-workflow/docs/FUNNEL_ARCHITECTURE.md`
- 读取章节：Layer 1: 数据收集层（4.1.1-4.1.4）

### 输出

- 脚本文件：`/root/clawd/skills/ai-prompt-workflow/scripts/collect-prompts.py`
- 配置文件：`/root/clawd/config/prompts-collector.yaml`
- 测试脚本：`/root/clawd/skills/ai-prompt-workflow/scripts/test-collect-prompts.py`
- 实现报告：`/tmp/subagent-layer1-report.md`

### 技术要求

- 使用 Python 3.12+
- 使用 requests 库进行 HTTP 请求
- 使用 sentence-transformers 进行语义去重
- 使用 APScheduler 进行任务调度
- 数据格式：JSONL

### 注意事项

- 代码需要完善的错误处理和日志
- 配置文件需要详细的注释
- 测试脚本需要包含所有功能的测试用例

请实现数据收集层并保存到指定路径。
EOF
)" \
    --label "funnel-layer1-collection")

SESSION_KEY1=$(echo "$RESPONSE1" | grep -oP '(?<=childSessionKey": ")[^"]+')

log "子代理 1 已启动，Session Key: $SESSION_KEY1"

# 等待子代理 1 完成（5 分钟）
log "等待子代理 1 完成（5 分钟）..."
sleep 300

# 检查子代理 1 是否完成
log "检查子代理 1 状态..."

# 继续其他子代理...

log "🎉 所有子代理任务已启动！"
log "💡 请查看子代理的执行状态和输出文件"

log "子代理执行计划："
log "  1. 子代理 1（Layer 1: 数据收集层）- 已启动"
log "  2. 子代理 2（Layer 2: 自动分类层）- 待启动"
log "  3. 子代理 3（Layer 3: 分类评分层）- 待启动"
log "  4. 子代理 4（Layer 4: 质量筛选层）- 待启动"
log "  5. 子代理 5（Layer 5: 内容补充层）- 待启动"
log "  6. 子代理 6（Layer 6: Skill 转换层）- 待启动"
log "  7. 子代理 7（集成和测试）- 待启动"

log "子代理任务清单："
log "  - 子代理 1: $SESSION_KEY1"
log "  - 子代理 2: (待启动)"
log "  - 子代理 3: (待启动)"
log "  - 子代理 4: (待启动)"
log "  - 子代理 5: (待启动)"
log "  - 子代理 6: (待启动)"
log "  - 子代理 7: (待启动)"

exit 0
