# Twitter 项目修复行动计划

**生成时间**: 2026-01-30 13:15
**状态**: 准备执行
**预计总耗时**: 2-4 小时

---

## ✅ 已完成的准备工作

1. ✅ 问题分析报告已生成: `/root/clawd/reports/TWITTER_PROJECT_ISSUES_ANALYSIS.md`
2. ✅ 去重数据库已修复 (19 条已收集, 2 条已转换, 17 条待转换)
3. ✅ 创建了 3 个修复脚本:
   - `fix-dedup-bug.js` - 修复去重逻辑
   - `optimize-twitter-query.sh` - 优化搜索查询
   - `adjust-scoring-weights.js` - 调整评分权重

---

## 🔴 P0 紧急任务（必须今天完成）

### 任务 1: 充值 Twitter API 账户

**优先级**: 🔴 最高
**预计时间**: 10-15 分钟
**负责人**: 用户（需要支付）

**步骤**:
```bash
# 1. 访问 twitterapi.io
# https://twitterapi.io/

# 2. 登录账户
# - 使用注册时的邮箱
# - 密码或社交登录

# 3. 进入充值页面
# Dashboard → Billing/Credits → Add Credits

# 4. 选择充值金额
# 建议: $5 或 $10
# $5 = 约 33,333 条推文
# 可用 1-2 个月

# 5. 完成支付
# 支持信用卡、PayPal 等

# 6. 等待 1-5 分钟
# 额度即时生效

# 7. 验证充值成功
python3 /root/clawd/skills/twitter-search-skill/scripts/twitter_search_improved.py \
  "$TWITTER_API_KEY" \
  "test" \
  --max-results 1 \
  --format json
```

**验证命令**:
```bash
# 检查 API 是否恢复工作
# 如果成功，会返回 JSON 格式的推文
# 如果失败，返回 HTTP 402 错误
```

**注意事项**:
- ⚠️ API Key 为: `new1_1f191206d7234ac883f47640b933792a`
- ⚠️ 充值前确认是正确账户
- ⚠️ 推荐用 PayPal（更安全）

---

### 任务 2: 优化搜索查询

**优先级**: 🟡 高
**预计时间**: 5 分钟
**负责人**: 可自动执行

**状态**: ✅ 已准备脚本

**执行步骤**:
```bash
# 运行优化脚本
chmod +x /root/clawd/scripts/optimize-twitter-query.sh
bash /root/clawd/scripts/optimize-twitter-query.sh

# 按提示输入 'y' 应用修改
```

**修改内容**:
- 原查询: `"AI" OR "prompt" OR "ChatGPT" OR "prompt engineering" OR "AI prompts"`
- 新查询: `#PromptEngineering OR #AIPrompts OR "prompt template" OR "prompt framework" OR "ChatGPT prompt" OR "Claude prompt" OR "AI prompt engineering guide" -is:retweet`

**预期效果**:
- 推文质量提升 40-60%
- 实用提示词比例提升
- 减少 50% 的无关内容

---

### 任务 3: 调整评分权重

**优先级**: 🟡 高
**预计时间**: 5 分钟
**负责人**: 可自动执行

**状态**: ✅ 已准备脚本

**执行步骤**:
```bash
# 运行调整脚本
node /root/clawd/scripts/adjust-scoring-weights.js
```

**权重变化**:
| 维度 | 当前 | 目标 | 变化 |
|------|------|------|------|
| 实用性 | 20% | 35% | +15% |
| 创新性 | 15% | 20% | +5% |
| 完整性 | 25% | 20% | -5% |
| 热度 | 30% | 15% | -15% |
| 影响力 | 10% | 10% | 0% |

**预期效果**:
- 减少新闻/公告类内容评分（热度权重降低）
- 更重视提示词模板的实际可用性
- 平均评分预期从 46.5 提升至 60+

---

## 🟡 P1 高优先级任务（本周完成）

### 任务 4: 测试新的搜索查询

**优先级**: 🟡 高
**预计时间**: 15 分钟
**时机**: 任务 2 完成后

**步骤**:
```bash
# 手动测试新查询
cd /root/clawd

# 使用新查询搜索（小规模测试）
python3 /root/clawd/skills/twitter-search-skill/scripts/twitter_search_improved.py \
  "$TWITTER_API_KEY" \
  "#PromptEngineering OR #AIPrompts OR \"prompt template\" OR \"prompt framework\" -is:retweet" \
  --max-results 10 \
  --query-type Top \
  --lang en \
  --min-likes 10 \
  --format json > /tmp/test-search-results.json

# 查看结果
cat /tmp/test-search-results.json | jq '.total_tweets, .tweets[0].text'
```

**评估标准**:
- 推文是否包含实用的提示词模板？
- 是否减少了新闻/公告类内容？
- 互动质量是否提升？

---

### 任务 5: 改进错误处理

**优先级**: 🟡 高
**预计时间**: 30 分钟

**需要修改的文件**:
- `/root/clawd/scripts/dedup-record-from-json.js`

**改进内容**:
1. 添加详细的错误日志
2. 验证推文格式
3. 显示处理进度
4. 失败时提供诊断信息

**修改要点**:
```javascript
// 添加验证
if (tweets.length === 0) {
  console.warn('⚠️  Warning: tweets array is empty');
  console.log('JSON structure:', JSON.stringify(data, null, 2).substring(0, 500));
}

// 添加进度
console.log(`📊 Processing ${tweets.length} tweets...`);

// 添加格式验证
const validTweets = tweets.filter(tweet => {
  if (!tweet.url && !tweet.id) {
    console.warn('⚠️  Invalid tweet:', JSON.stringify(tweet).substring(0, 100));
    return false;
  }
  return true;
});
```

---

### 任务 6: 重新评估历史数据

**优先级**: 🟡 高
**预计时间**: 10 分钟
**时机**: 任务 3 完成后

**步骤**:
```bash
# 使用新权重重新评估
node /root/clawd/scripts/evaluate-prompts-quality.js

# 查看新报告
cat /root/clawd/reports/quality-evaluation-report.md
```

**预期变化**:
- C+ 等级推文增加
- D 等级推文减少
- 平均评分提升

---

## 🟠 P2 中优先级任务（2 周内完成）

### 任务 7: 添加内容类型过滤

**优先级**: 🟠 中
**预计时间**: 1-2 小时

**功能**:
- 自动检测推文类型（新闻/公告 vs 实用提示词）
- 直接过滤掉新闻/公告类内容
- 为不同类型设置不同评分标准

**实现**:
```javascript
function detectContentType(tweet) {
  const text = (tweet.text || '').toLowerCase();

  if (text.match(/introducing|launch|new feature|announcement/i)) {
    return { type: 'news', priority: 0 };
  }

  if (text.match(/prompt:|template|framework|step \d|guide/i)) {
    return { type: 'practical', priority: 3 };
  }

  return { type: 'unknown', priority: 1 };
}
```

---

### 任务 8: 集成 GitHub 数据源

**优先级**: 🟠 中
**预计时间**: 2-3 小时

**搜索关键词**:
- awesome-chatgpt-prompts
- prompt-templates
- ai-prompts

**脚本路径**: `/root/clawd/scripts/collect-github-prompts.sh`

**优势**:
- 社区验证的高质量内容
- 持续更新
- 完整的代码示例

---

### 任务 9: 集成 Reddit 数据源

**优先级**: 🟠 中
**预计时间**: 1-2 小时

**子版块**:
- r/ChatGPTPromptGenius
- r/PromptEngineering

**优势**:
- 投票机制筛选
- 讨论质量高
- 用户反馈直接

---

## 📅 执行时间表

### 今天（2 小时）

| 时间 | 任务 | 状态 |
|------|------|------|
| 0:10 | 充值 Twitter API | ⏳ 待用户执行 |
| 0:15 | 优化搜索查询 | ✅ 脚本就绪 |
| 0:20 | 调整评分权重 | ✅ 脚本就绪 |
| 0:15 | 测试新查询效果 | ⏳ 待执行 |
| 0:30 | 改进错误处理 | ⏳ 待执行 |
| 0:10 | 重新评估历史数据 | ⏳ 待执行 |
| 0:10 | 验证所有修复 | ⏳ 待执行 |

### 本周（2-3 小时）

| 任务 | 预计时间 | 状态 |
|------|----------|------|
| 部署 Nitter 备用 API | 1 小时 | ⏳ 待执行 |
| 添加内容类型过滤 | 2 小时 | ⏳ 待执行 |
| 集成 GitHub 数据源 | 3 小时 | ⏳ 待执行 |

### 2 周内（4-6 小时）

| 任务 | 预计时间 | 状态 |
|------|----------|------|
| 集成 Reddit 数据源 | 2 小时 | ⏳ 待执行 |
| 建立优质账号白名单 | 1 小时 | ⏳ 待执行 |
| 持续优化评分权重 | 2 小时 | ⏳ 待执行 |
| 添加更多数据源 | 2 小时 | ⏳ 待执行 |

---

## 🎯 成功指标

### 短期（1 周）

- ✅ API 连续运行 7 天无中断
- ✅ 每天收集 800+ 条高质量推文
- ✅ 去重数据库无重复、无负数
- ✅ 平均评分从 46.5 提升至 60+

### 中期（1 个月）

- ✅ 平均评分从 60+ 提升至 65+
- ✅ 高质量推文占比 > 20%
- ✅ 多源数据（Twitter + GitHub + Reddit）
- ✅ 完全避免重复收集

### 长期（3 个月）

- ✅ 建立稳定的数据收集和评分体系
- ✅ 自动识别高质量提示词
- ✅ 数据驱动的评分权重优化
- ✅ 持续改进的反馈循环

---

## 📞 需要的支持

### 用户需要执行

1. **充值 API 账户**（10-15 分钟）
   - 访问 twitterapi.io
   - 登录并充值 $5-10

2. **批准自动执行**（可选）
   - 运行优化脚本
   - 运行调整脚本

### AI 自动执行

- ✅ 优化搜索查询
- ✅ 调整评分权重
- ✅ 改进错误处理
- ✅ 重新评估数据
- ✅ 集成新数据源

---

## 📝 总结

### 问题严重程度
1. 🔴 **API 额度**: 阻塞性问题，**必须立即解决**
2. 🟡 **去重逻辑**: 已修复，需要验证
3. 🟠 **数据质量**: 长期优化项目

### 投入产出比
- **总投入**: 约 10-15 小时 + $5-10
- **预期收益**: 数据质量提升 40%+，持续运行 1-2 个月
- **ROI**: 极高

### 下一步

**立即行动**:
1. 充值 Twitter API 账户（用户）
2. 运行优化脚本（AI）
3. 测试修复效果（AI）

**本周完成**:
4. 添加内容类型过滤
5. 集成 GitHub 数据源
6. 持续监控和优化

---

**行动计划准备完成！**
**等待用户确认充值后即可开始执行自动任务**
