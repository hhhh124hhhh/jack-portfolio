# AI 提示词转 Skill 完整自动化策略

**版本**: 2.0
**更新时间**: 2026-01-30
**状态**: 已实施

## 📊 当前状态评估

### ✅ 已完成
- [x] 基础数据收集脚本（Reddit, GitHub, Hacker News, SearXNG）
- [x] 推文到 Skill 转换工具
- [x] 自动发布到 ClawdHub 的脚本
- [x] 端到端工作流脚本（full-prompt-workflow.sh）
- [x] 2 个 Skills 成功发布到 ClawdHub
- [x] Cron 定时任务配置

### ⚠️ 存在问题
- [x] Twitter API key 已配置但需要验证
- [ ] 质量评估系统不够完善
- [ ] 缺乏数据去重机制
- [ ] 没有实时状态监控面板
- [ ] 缺乏错误恢复机制

### 🎯 目标
1. **数据收集效率**: 每天 800-1200 条高质量提示词
2. **转换成功率**: >70% 的收集内容可转换为 Skill
3. **发布成功率**: >90% 的生成的 Skill 能成功发布
4. **时间效率**: 全流程自动化，无需人工干预

## 🔄 完整自动化流程

### 阶段 1: 数据收集（多源并行）

#### 1.1 主要数据源（优先级排序）

**优先级 1 - Twitter/X**（每 6 小时）
- 使用 jina.ai API（无 API key 限制）
- 搜索策略：
  ```bash
  查询模板:
  - "AI prompt" OR "ChatGPT prompt" (min_likes: 50)
  - "Claude prompt" OR "prompt engineering" (min_likes: 30)
  - "#AIPrompts" OR "#promptengineering"
  - "best AI prompts" -is:retweet
  ```
- 输出: `/root/clawd/data/x-scraping/prompts-YYYYMMDD-HH.jsonl`
- 并发数: 3 个查询同时运行

**优先级 2 - Reddit**（每 6 小时）
- 子版块: r/ChatGPT, r/artificial, r/MachineLearning, r/LocalLLaMA
- 提取规则: 包含代码块、步骤说明、最佳实践
- 输出: `/root/clawd/data/prompts/reddit-prompts.jsonl`

**优先级 3 - SearXNG 搜索**（每 4 小时）
- 关键词轮换:
  ```python
  keywords = [
      "AI prompt engineering tips 2026",
      "effective ChatGPT prompts",
      "best AI prompts for [category]",
      "Claude AI prompt templates"
  ]
  ```
- 搜索引擎: Google, DuckDuckGo, Bing 聚合
- 输出: `/root/clawd/data/prompts/searxng-YYYYMMDD-HH.jsonl`

**优先级 4 - GitHub**（每 12 小时）
- 搜索: "prompt engineering", "awesome prompts", "ChatGPT prompts"
- 过滤: stars > 100, updated in 2025-2026
- 输出: `/root/clawd/data/prompts/github-awesome-prompts.jsonl`

**优先级 5 - Hacker News**（每 8 小时）
- 搜索: AI, prompt, LLM, ChatGPT
- 过滤: comments > 10, score > 50
- 输出: `/root/clawd/data/prompts/hacker-news-ai.jsonl`

#### 1.2 数据质量控制

**自动过滤规则**:
- ❌ 太短: < 50 字符
- ❌ 太长: > 2000 字符（除非包含代码）
- ❌ 纯链接: 无具体内容
- ❌ 重复: 基于 content hash 去重
- ❌ 低质量: 包含 "test", "demo", "example" 且无实质内容

**元数据提取**:
- 提取标签（如 #code, #writing, #analysis）
- 提取关键词（NLP 分析）
- 分类（技术类/创意类/教育类）

### 阶段 2: 智能质量评估（AI 驱动）

#### 2.1 多维度评分系统（100 分制）

**维度 1: 实用性（30 分）**
- 评分标准:
  - 10-15: 有基本思路但缺少细节
  - 16-25: 有步骤说明和参数
  - 26-30: 完整的教程，可直接使用

**维度 2: 创新性（20 分）**
- 评分标准:
  - 10-15: 常见思路，有轻微调整
  - 16-18: 独特角度或方法
  - 19-20: 前所未见的创新技巧

**维度 3: 完整性（20 分）**
- 评分标准:
  - 10-15: 部分信息
  - 16-18: 大部分信息完整
  - 19-20: 非常详细，多个示例

**维度 4: 热度（25 分）**
- 标准化算法:
  ```
  score = min(25, (likes * 0.5 + comments * 1.5 + shares * 2) / 10)
  ```

**维度 5: 作者影响力（5 分）**
- 粉丝数权重:
  ```
  score = min(5, log10(followers) * 0.8)
  ```

#### 2.2 评分等级定义

| 分数范围 | 等级 | 转换策略 | 定价建议 |
|---------|------|---------|---------|
| 90-100  | A+   | 必转换   | $9.99   |
| 80-89   | A    | 必转换   | $4.99   |
| 70-79   | B+   | 优先转换 | $2.99   |
| 60-69   | B    | 可转换   | $0.99   |
| 50-59   | C    | 存档备用 | 免费    |
| 0-49    | D    | 丢弃    | -       |

#### 2.3 自动优化

**动态调整评分权重**:
- 根据已发布 Skills 的下载量调整
- 用户反馈高的维度权重 +5%
- 低反馈的维度权重 -5%

**训练数据积累**:
- 记录所有评分结果
- 人工抽查 10% 的评分
- 用于优化评分算法

### 阶段 3: 智能 Skill 转换

#### 3.1 转换规则

**自动识别类型**:
1. **代码类** → 编程辅助 Skill
2. **写作类** → 内容创作 Skill
3. **分析类** → 数据分析 Skill
4. **创意类** → 艺术生成 Skill
5. **教育类** → 学习指导 Skill

**自动模板匹配**:
```javascript
// 伪代码
if (content.includes('```') && content.includes('python')) {
    type = 'coding';
    template = 'coding-assistant';
} else if (content.includes('write') || content.includes('blog')) {
    type = 'writing';
    template = 'content-creator';
} else if (content.includes('image') || content.includes('generate')) {
    type = 'creative';
    template = 'ai-image-generator';
}
```

#### 3.2 Skill 结构生成

**标准目录结构**:
```
skill-name/
├── SKILL.md          # 主文档
├── README.md         # 简介
├── examples/         # 示例
│   ├── example1.md
│   └── example2.md
├── prompts/          # 提示词模板
│   └── templates.json
└── package.json      # 元数据
```

**SKILL.md 内容**:
```markdown
# Skill 名称

## 描述
简短描述（1-2 句）

## 类别
[category]

## 评分
总分: 85/100 (A)

## 使用方法
详细步骤...

## 示例
[examples]

## 最佳实践
[best practices]

## 数据源
- 来源: Twitter/X
- 原始链接: [url]
- 作者: @username
- 采集时间: YYYY-MM-DD
```

#### 3.3 自动优化

**内容增强**:
- 补充缺失的示例
- 添加常见问题解答
- 生成测试用例

**格式标准化**:
- 统一标题层级
- 统一代码块语法高亮
- 统一术语命名

### 阶段 4: 自动发布到 ClawdHub

#### 4.1 发布流程

**预检查**:
```bash
# 1. 格式验证
clawdhub validate /path/to/skill

# 2. 重复检查
clawdhub search "skill name"

# 3. 评分检查
if score < 70; then
    # 标记为 "待审核"
    skip_publish = true
fi
```

**批量发布**:
```bash
for skill in /root/clawd/generated-skills/*/; do
    if [ ! -f "$skill/.published" ]; then
        clawdhub publish "$skill" \
            --slug "$(basename $skill)" \
            --version 1.0.0 \
            --changelog "Auto-generated from prompt collection"
    fi
done
```

**发布后操作**:
- 创建 `.published` 标记文件
- 记录发布 ID
- 生成发布报告

#### 4.2 错误处理

**发布失败重试**:
- 第一次失败: 1 小时后重试
- 第二次失败: 6 小时后重试
- 第三次失败: 标记为 "发布失败"，等待人工审核

**常见失败原因**:
- Slug 已存在 → 自动生成新 slug（加后缀）
- 格式错误 → 自动修复格式
- 评分不足 → 降级发布或暂存

### 阶段 5: 监控和报告

#### 5.1 实时监控指标

**数据收集监控**:
- 每日收集量
- 各数据源贡献比例
- 数据质量分布

**转换监控**:
- 转换成功率
- 各等级数量
- 转换耗时

**发布监控**:
- 发布成功率
- ClawdHub 下载量（如果有 API）
- 用户评分（如果有）

#### 5.2 报告类型

**每日报告**（每天 9:00）:
```
📊 **每日自动化报告** - YYYY-MM-DD

**数据收集**: 245 条
- Twitter: 120 (49%)
- Reddit: 45 (18%)
- SearXNG: 50 (20%)
- GitHub: 20 (8%)
- Hacker News: 10 (4%)

**质量评估**:
- A+ (90-100): 15 条 (6%)
- A (80-89): 25 条 (10%)
- B+ (70-79): 45 条 (18%)
- B (60-69): 80 条 (33%)
- C (50-59): 60 条 (25%)
- D (0-49): 20 条 (8%)

**Skill 转换**: 15 个
- A+ 转换: 15 个 (100%)
- A 转换: 25 个 (100%)
- B+ 转换: 30 个 (67%)

**ClawdHub 发布**: 18 个
- 成功: 16 个 (89%)
- 失败: 2 个 (11%)

⚠️ **待处理**:
- 3 个 Skill 发布失败，需要人工审核
- 15 个 B+ 级提示词等待转换
```

**每周报告**（每周一 9:00）:
- 趋势分析（收集量、转换率、发布成功率）
- Top 10 高质量 Skills
- 数据源效率对比
- 优化建议

**异常报警**（实时）:
- 某个数据源连续 3 次收集失败
- 转换成功率低于 50%
- 发布成功率低于 80%
- 发现重复发布

## 🛠️ 技术实现

### 脚本架构

```
/root/clawd/automation/
├── main.py                    # 主控脚本
├── config.yaml                # 配置文件
├── collectors/                # 数据收集器
│   ├── twitter_collector.py
│   ├── reddit_collector.py
│   ├── searxng_collector.py
│   ├── github_collector.py
│   └── hn_collector.py
├── evaluators/                # 评估器
│   ├── quality_evaluator.py
│   ├── deduplicator.py
│   └── category_classifier.py
├── converters/                # 转换器
│   ├── skill_converter.py
│   ├── template_matcher.py
│   └── content_enhancer.py
├── publishers/                # 发布器
│   ├── clawdhub_publisher.py
│   └── git_publisher.py
├── monitors/                  # 监控器
│   ├── metrics_collector.py
│   ├── report_generator.py
│   └── alert_system.py
└── utils/                     # 工具
    ├── logger.py
    ├── slack_notifier.py
    └── state_tracker.py
```

### 配置文件示例

```yaml
# config.yaml
automation:
  enabled: true
  log_level: INFO

data_collection:
  sources:
    twitter:
      enabled: true
      interval_hours: 6
      max_results: 100
      min_likes: 30
      queries:
        - "AI prompt" OR "ChatGPT prompt"
        - "Claude prompt" OR "prompt engineering"
        - "#AIPrompts" OR "#promptengineering"

    reddit:
      enabled: true
      interval_hours: 6
      subreddits:
        - ChatGPT
        - artificial
        - MachineLearning

    searxng:
      enabled: true
      interval_hours: 4
      url: "http://localhost:8080/search"
      engines: ["google", "duckduckgo", "bing"]
      keywords:
        - "AI prompt engineering tips 2026"
        - "effective ChatGPT prompts"

quality_evaluation:
  enabled: true
  min_score: 60  # C 及以上
  convert_threshold: 70  # B+ 及以上转换

  weights:
    practicality: 0.30
    innovation: 0.20
    completeness: 0.20
    popularity: 0.25
    influence: 0.05

skill_conversion:
  enabled: true
  interval_hours: 24
  min_score: 70

  templates:
    coding: coding-assistant
    writing: content-creator
    analysis: data-analyst
    creative: ai-image-generator
    education: learning-guide

publishing:
  enabled: true
  platform: clawdhub
  auto_publish_threshold: 70
  retry_delays: [3600, 21600]  # 1h, 6h

monitoring:
  enabled: true
  daily_report: true
  weekly_report: true
  alert_on_failure: true

notifications:
  slack:
    enabled: true
    channel: "#clawdbot"
    dm_id: "D0AB0J4QLAH"

  feishu:
    enabled: true
    user_id: "ou_3bc5290afc1a94f38e23dc17c35f26d6"

git:
  enabled: true
  auto_commit: true
  auto_push: true
  repo_path: "/root/clawd"
```

### 状态追踪

**数据库/JSON 文件**:
```json
{
  "last_collection": {
    "twitter": "2026-01-30T22:00:00Z",
    "reddit": "2026-01-30T22:00:00Z",
    "searxng": "2026-01-30T18:00:00Z"
  },
  "stats": {
    "total_collected": 1250,
    "total_converted": 85,
    "total_published": 78,
    "success_rate": 0.92
  },
  "failed_jobs": []
}
```

### 错误恢复

**自动重试机制**:
```python
MAX_RETRIES = 3
RETRY_DELAYS = [60, 300, 900]  # 1min, 5min, 15min

def run_with_retry(func, *args, **kwargs):
    for attempt, delay in enumerate(RETRY_DELAYS):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(delay)
```

**状态持久化**:
- 每个阶段完成后保存进度
- 脚本中断后可从断点恢复
- 避免重复处理相同数据

## 📈 优化计划

### 短期（1-2 周）

1. **Twitter 集成优化**
   - 测试 jina.ai API 稳定性
   - 优化搜索查询策略
   - 添加推文内容过滤

2. **评分系统调整**
   - 收集用户反馈
   - 调整权重参数
   - 添加人工审核样本

3. **转换质量提升**
   - 改进模板匹配算法
   - 增强内容分析能力
   - 添加更多模板类型

### 中期（1 个月）

1. **数据源扩展**
   - 集成更多数据源（Discord, Telegram）
   - 支持多语言内容
   - 添加内容去重算法升级

2. **AI 模型优化**
   - 使用 GPT-4 评估内容质量
   - 自动生成更好的 Skill 描述
   - 智能分类和标签

3. **商业化功能**
   - ClawdHub 下载量追踪
   - 用户反馈收集
   - A/B 测试不同定价

### 长期（3 个月）

1. **完全自动化**
   - 零人工干预
   - 自我优化能力
   - 智能异常处理

2. **多平台支持**
   - 支持更多技能市场
   - 跨平台同步
   - 统一数据分析

3. **社区建设**
   - 开源部分工具
   - 建立用户社区
   - 收集更多反馈

## 🎯 KPI 指标

### 数据收集
- 每日收集量: > 800 条
- 数据质量评分平均: > 65 分
- 去重后保留率: > 80%

### Skill 转换
- 转换成功率: > 70%
- A+ 级转换率: 100%
- 平均转换时间: < 5 秒/条

### ClawdHub 发布
- 发布成功率: > 90%
- 发布失败率: < 10%
- 重复发布率: 0%

### 整体效率
- 端到端耗时: < 30 分钟（收集 → 发布）
- 人工干预率: < 5%
- 系统稳定性: > 99.5% 可用性

## 📝 注意事项

### 安全性
- 保护 API keys 和敏感信息
- 避免重复发布相同内容
- 遵守各平台的使用条款

### 合规性
- 尊重原创内容版权
- 注明数据来源和作者
- 遵守 ClawdHub 的发布规则

### 可维护性
- 定期更新依赖包
- 监控日志文件大小
- 清理过期数据

---

**最后更新**: 2026-01-30
**负责人**: jack happy
**状态**: 实施中
