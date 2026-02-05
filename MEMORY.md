# MEMORY.md - 核心记忆

*记忆已备份，可以通过 memory-manager 查询历史记忆*
*备份目录：/root/clawd/memory/backups*

## 重要记忆

### Context Overflow 解决方案（2026-02-05 10:06）

**问题**：Context overflow: prompt too large for model

**解决方案**：使用 coding-agent 实现分段处理文件

**原因**：
- ✅ 快速高效
- ✅ 可以根据具体需求定制
- ✅ 已经有 Python 编程经验
- ✅ 灵活性高

**注意事项**：存入记忆 skill 不要占用上下文

### Slack 配置问题（2026-02-05 09:05）

**问题**：Slack 和 Feishu 通知发送失败

**错误信息**：
```
Invalid config at /root/.clawdbot/clawdbot.json:
- agents.defaults.compaction.memoryFlush: Unrecognized keys: "hardThresholdTokens", "keepRecentMessages"
```

**解决方案**：运行 `clawdbot doctor --fix`

### ClawdHub Token（2026-02-01）

**Token**: `clh_Ki_M1Xiws5Qzi83gqdZhYG3jXSuZOnEfQOxhaRsjHcw`
**Registry**: `https://www.clawhub.ai/api` ⚠️ 必须使用此 URL
**状态**: ✅ 已配置并验证
**最后检查**: 2026-02-05 07:04:04

### Twitter API（2026-02-05 10:10）

**状态**: ❌ 配额已用完

**错误信息**：
```
HTTP 402: {"error":"Unauthorized","message":"Credits is not enough.Please recharge"}
```

**影响**：所有 Twitter 搜索任务（4 个 cron 任务）失败

**解决方案**：
1. 禁用 Twitter 搜索任务（直到 API 问题解决）
2. Twitter API 配额充值
3. 使用备用方案（SearXNG、Reddit 等）

### 项目方向反思（2026-02-05 10:54）

**项目名称**：AI 内容自动化工作流（原：AI 提示词自动化）

**问题**：这条路可能不太好走通

**数据统计**：
- 收集数据：747 条
- 可转换数据：28 条
- 转换率：3.75%

**可能的原因**：
1. 可转换的高质量提示词本身就不多
2. 这条路的商业价值有限
3. 数据源质量问题（大部分是重复或低质量）

**建议的新方向**：
1. 专注于高质量来源（少而精）
2. 改变产品定位（手动挑选、深度优化）
3. 暂停这个项目，转向其他更有价值的工作

### Cron 脚本路径错误（2026-02-05 10:00）

**问题**：Twitter 搜索 cron 配置的脚本不存在

**错误配置**：
```json
"text": "Twitter 搜索（10:00）- ... 运行 /root/clawd/scripts/twitter-search-cron.sh"
```

**实际脚本**：`/root/clawd/scripts/auto_twitter_search.sh`

**影响**：所有 Twitter 搜索任务失败

**解决方案**：更新 cron jobs 配置中的所有 4 个任务的脚本路径

### AI 研究发现（2026-02-05 04:01）

**Claude AI 重磅更新**：
- Claude Cowork - AI 代理功能，虚拟助手
- Claude Sonnet 5 (Fennec) - SWE-Bench 82.1%
- Claude AI for Healthcare - 医疗健康
- Claude Legal Plugin - 法律领域

**OpenAI 动态**：
- GPT-4o 即将退役
- ChatGPT Health 上线
- GPT-5.2-Codex 发布

**多模态 AI 趋势**：
- 2026 年属于多模态 AI
- 多模态 AI 成为技术栈基础

---

## 搜索脚本不匹配问题（2026-02-05 10:58）

**问题**：`full-prompt-workflow.sh` 没有使用新架构的 4 层漏斗模型

**架构对比**：
- 新架构：收集 → 分类 → 评分 → 筛选 → 补充 → 转换 → 发布（6 层）
- 实际工作流：收集 → 转换 → 发布 → 报告（4 阶段）

**证据**：
- `scored/` 目录：有数据（492K）
- `enhanced/` 目录：空的（0 bytes）

**解决方案**：修改 `full-prompt-workflow.sh`，加入缺失的 4 层

### 上下文清理策略（2026-02-05 11:13）

**方案**：结合方案（定时 + 阈值）

**定时清理**：
- 每天 2 次（2:00, 14:00）
- Cron 配置：`/etc/cron.d/clawdbot-memory-flush`

**阈值清理**：
- 检查脚本：`/root/clawd/scripts/check-context-usage.sh`
- 阈值：50%
- 在 heartbeat 中自动触发

**清理脚本**：`/root/clawd/scripts/backup-and-flush-memory.sh`

---
