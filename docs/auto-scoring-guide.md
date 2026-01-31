# 全自动化评分系统 - 使用说明

## 🎯 系统概述

这是一个智能化的 AI 提示词质量评估系统，能够：
1. **自动评分**: 定期运行质量评估，计算 5 维度得分
2. **自动优化**: 根据评分结果自动调整权重
3. **智能决策**: 检测评分过低时，建议优化搜索策略
4. **历史追踪**: 记录每次评估和权重调整，追踪优化效果

## 📊 评分维度

| 维度 | 默认权重 | 说明 |
|------|---------|------|
| 实用性 | 35% | 是否包含实用的提示词、模板或指南 |
| 创新性 | 20% | 内容是否有独特性、新颖性和前瞻性 |
| 完整性 | 20% | 内容是否完整、清晰、易于理解 |
| 热度 | 15% | 基于点赞、转发、回复等互动指标 |
| 影响力 | 10% | 基于粉丝数、认证状态等 |

## 🚀 快速开始

### 1. 手动运行评分系统

```bash
# 基础评分
node /root/clawd/scripts/evaluate-prompts-quality.js

# 全自动化评分系统（包含权重优化）
node /root/clawd/scripts/auto-scoring-system.js

# 智能评分系统（包含搜索策略优化建议）
bash /root/clawd/scripts/intelligent-auto-scoring.sh
```

### 2. 查看报告

```bash
# 最新评估报告
cat /root/clawd/reports/quality-evaluation-report.md

# 最新自动化报告
ls -t /root/clawd/reports/auto-scoring/auto-scoring-report-*.md | head -1 | xargs cat

# 查看权重历史
cat /root/clawd/reports/auto-scoring/history/weight-history.jsonl | jq .
```

### 3. Cron 任务

系统已配置自动运行，每 6 小时执行一次：

```json
{
  "id": "intelligent-auto-scoring",
  "name": "智能自动化评分系统",
  "schedule": "0 */6 * * *",  // 每 6 小时
  "enabled": true
}
```

## 🎛️ 权重优化策略

系统会根据评分结果自动调整权重：

### 策略 1: 平均分过低 (lowAverage)
- **触发条件**: 平均分 < 60
- **调整**: 实用性 +5%, 完整性 -5%, 热度 -5%
- **目的**: 提高实用性权重，更重视提示词的实际可用性

### 策略 2: 平均分过高 (highAverage)
- **触发条件**: 平均分 > 75
- **调整**: 热度 -5%, 影响力 +5%
- **目的**: 降低热度权重，减少新闻/公告类内容影响

### 策略 3: 高质量占比过低 (lowHighQuality)
- **触发条件**: 高质量占比 < 10%
- **调整**: 实用性 +5%, 创新性 +5%, 完整性 -5%, 热度 -5%
- **目的**: 更重视创新和实用性

## 📝 搜索策略优化

当评分持续过低时，系统会建议优化搜索策略：

### 当前问题
- 平均分: 37.7（目标: 65）
- 高质量占比: 0%（目标: 15%）
- 主要原因: 搜索查询过于宽泛，抓取了太多新闻/公告类内容

### 优化建议

1. **使用更精确的查询**
   ```bash
   "AI prompt" template OR framework OR guide
   ChatGPT prompt "step by step" tutorial
   prompt engineering examples "how to"
   ```

2. **过滤新闻类内容**
   ```bash
   -launched -released -announcing -"new feature"
   ```

3. **关注专业账号**
   - 创建白名单账号列表
   - 优先抓取提示词工程专家

4. **设置最小互动阈值**
   - 最小点赞数: 50
   - 最小转发数: 10
   - 最小收藏数: 5

### 应用优化

```bash
# 查看优化建议
cat /root/clawd/reports/auto-scoring/optimization-suggestion-*.md

# 手动应用优化（需要编辑搜索脚本）
nano /root/clawd/scripts/auto_twitter_search.sh
```

## 📊 报告解读

### 评估报告包含

1. **基本信息**
   - 评估推文数
   - 平均评分
   - 高质量占比

2. **评分分布**
   - 各等级（A+ 到 D）的数量和占比

3. **Top 10 推文**
   - 详细评分明细
   - 各维度得分和原因

4. **权重历史**
   - 最近 5 次调整记录
   - 优化效果追踪

### 等级划分

| 等级 | 分数范围 | 说明 |
|------|---------|------|
| A+ | 90-100 | 优秀，可直接转换为 Skill |
| A | 85-89 | 很好，建议转换为 Skill |
| B+ | 80-84 | 良好，可转换为 Skill |
| B | 70-79 | 中等，需要人工审核 |
| C+ | 60-69 | 及格，需要修改 |
| C | 50-59 | 较差，需要大改 |
| D | 0-49 | 不合格，不建议使用 |

## 🔧 配置调整

### 修改评分阈值

编辑 `/root/clawd/scripts/auto-scoring-system.js`:

```javascript
const CONFIG = {
  thresholds: {
    targetAverageScore: 65,      // 目标平均分
    minAverageScore: 60,          // 最低平均分
    maxAverageScore: 75,          // 最高平均分
    highQualityTarget: 15,        // 目标高质量占比 %
    minHighQuality: 10,           // 最低高质量占比 %
    maxHighQuality: 25            // 最高高质量占比 %
  },
  // ...
};
```

### 修改权重策略

编辑 `/root/clawd/scripts/auto-scoring-system.js`:

```javascript
weightAdjustmentStrategies: {
  lowAverage: {
    utility: 0.40,
    innovation: 0.20,
    completeness: 0.15,
    engagement: 0.15,
    influence: 0.10
  },
  // ...
}
```

### 修改评分维度规则

编辑 `/root/clawd/scripts/evaluate-prompts-quality.js`，找到对应的评估函数（如 `evaluateUtility`），调整评分规则。

## 📈 使用建议

1. **定期查看报告**: 每周查看一次评分趋势
2. **人工抽样审核**: 验证评分准确性
3. **持续优化搜索**: 根据评分反馈调整搜索策略
4. **建立白名单**: 记录高质量内容来源账号
5. **监控权重变化**: 确保权重优化方向正确

## 🐛 故障排查

### 问题: 评分脚本执行失败

```bash
# 检查脚本权限
ls -l /root/clawd/scripts/auto-scoring-system.js

# 添加执行权限
chmod +x /root/clawd/scripts/auto-scoring-system.js

# 手动测试
node /root/clawd/scripts/auto-scoring-system.js
```

### 问题: Cron 任务未运行

```bash
# 查看 Cron 配置
cat /root/.clawdbot/cron/jobs.json | jq '.jobs[] | select(.id=="intelligent-auto-scoring")'

# 检查运行状态
cat /root/.clawdbot/cron/jobs.json | jq '.jobs[] | select(.id=="intelligent-auto-scoring") | .state'

# 重启 Gateway
clawdbot gateway restart
```

### 问题: 评分始终过低

可能原因：
1. 搜索查询不精确
2. 抓取内容不相关
3. 评分规则需要调整

解决方法：
1. 查看优化建议报告
2. 手动审核 Top 10 推文
3. 调整搜索策略
4. 考虑调整评分规则

## 📞 支持

如有问题，查看：
- 评估日志: `/root/clawd/reports/quality-evaluation-report.md`
- 自动化日志: `/root/clawd/reports/auto-scoring/auto-scoring-report-*.md`
- 权重历史: `/root/clawd/reports/auto-scoring/history/weight-history.jsonl`

---

**系统版本**: v1.0
**最后更新**: 2026-01-30
