---
name: ai-prompt-workflow
description: "整合的 AI 提示词自动化工作流 - 一键完成从数据发现到发布的完整流程。集成 x-prompt-hunter（语义去重 + LLM 评估 + Langfuse 追踪）和 prompt-to-skill-converter（转换 + 打包 + 发布）。支持 GitHub、HuggingFace、Twitter、Reddit、Hacker News、SearXNG、Firecrawl 等多源数据抓取，自动评估质量，转换为 Clawdbot Skills 并发布到 ClawdHub。"
metadata:
  {
    "clawdbot": {
      "emoji": "🔄",
      "requires": {
        "bins": ["python3"],
        "env": [
          "ANTHROPIC_API_KEY",
          "LANGFUSE_PUBLIC_KEY",
          "LANGFUSE_SECRET_KEY",
          "GITHUB_TOKEN",
          "HUGGINGFACE_TOKEN",
          "TWITTER_API_KEY",
          "CLAWDHUB_TOKEN"
        ]
      },
      "primaryEnv": "ANTHROPIC_API_KEY"
    }
  }
---

# AI Prompt Workflow - 整合的自动化工作流

**一键完成从提示词发现到技能发布的全流程自动化。**

## 概述

本技能整合了两个核心技能，提供端到端的自动化解决方案：

```
┌─────────────────────────────────────────────────────────┐
│  Stage 1: 数据发现 (x-prompt-hunter)                   │
│  • 多源抓取 (GitHub, HuggingFace, Twitter, Reddit...)  │
│  • 语义去重 (sentence-transformers)                     │
│  • LLM 评估 (Claude API: 创新性/实用性/清晰度/可复用性)  │
│  • Langfuse 追踪 (质量趋势报告)                         │
└────────────────────┬────────────────────────────────────┘
                     │ 高质量提示词（带评分）
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 2: 转换发布 (prompt-to-skill-converter)          │
│  • 质量过滤 (只转换高分提示词)                           │
│  • 生成 SKILL.md                                         │
│  • 打包 .skill 文件                                      │
│  • 发布到 ClawdHub                                       │
└─────────────────────────────────────────────────────────┘
```

## 快速开始

### 一键执行完整流程

```bash
# 基本使用（默认参数）
bash /root/clawd/scripts/integrated-prompt-workflow.sh

# 自定义参数
bash /root/clawd/scripts/integrated-prompt-workflow.sh \
  --query "creative writing" \
  --limit 50 \
  --evaluate-limit 20 \
  --quality-threshold 80

# 测试模式（不发布）
bash /root/clawd/scripts/integrated-prompt-workflow.sh --test-mode
```

### 定时任务（Cron）

```bash
# 每天早上 9 点运行
0 9 * * * cd /root/clawd && bash scripts/integrated-prompt-workflow.sh >> logs/cron-integrated.log 2>&1
```

## 命令选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--query` | "AI prompts" | 搜索查询关键词 |
| `--limit` | 50 | 每个数据源的抓取限制 |
| `--evaluate-limit` | 30 | LLM 评估的提示词数量限制 |
| `--quality-threshold` | 70 | 质量阈值（0-100），只转换高于此分数的提示词 |
| `--test-mode` | false | 测试模式，不实际发布到 ClawdHub |
| `--help` | - | 显示帮助信息 |

## 工作流详解

### Stage 1: 数据发现（x-prompt-hunter）

**数据源：**
- ✅ **GitHub**: 从优质仓库抓取提示词
- ✅ **HuggingFace**: 访问高质量提示词数据集
- ✅ **Twitter/X**: 实时提示词发现（通过 bird CLI）
- ✅ **Reddit**: 社区驱动提示词集合
- ✅ **Hacker News**: 技术导向的提示词讨论
- ✅ **SearXNG**: 隐私保护的元搜索引擎
- ✅ **Firecrawl**: AI 驱动的网页抓取（处理 JavaScript 重型站点）

**核心功能：**

#### 1. 语义去重 🔄
- 使用 `sentence-transformers` 计算提示词之间的语义相似度
- 默认相似度阈值 0.85，可配置
- 自动过滤重复或高度相似的提示词
- 保存详细的去重记录用于追踪

**用途：**
- 清理重复的提示词库
- 提高提示词集合的多样性
- 减少冗余存储和计算

#### 2. LLM 评估 ⚖️
- 使用 **Claude API** 进行专业评估
- 四大评估维度：
  - **创新性** (1-10分)：独特性和创造性
  - **实用性** (1-10分)：实际应用价值
  - **清晰度** (1-10分)：表达明确性
  - **可复用性** (1-10分)：场景适应性
- 批量评估功能
- 生成详细的质量报告

**评分规则：**
- 总分 = 创新性 + 实用性 + 清晰度 + 可复用性（满分 40）
- 高质量提示词：总分 ≥ 30/40（75%）

#### 3. Langfuse 质量追踪 📊
- 实时追踪每次评估的详细数据
- 生成质量趋势报告
- 对比不同时间段的质量指标
- 支持自定义指标和分析

**用途：**
- 监控提示词质量变化
- 追踪系统性能
- 生成可视化报告

### Stage 2: 转换发布（prompt-to-skill-converter）

#### 1. 质量过滤
- 只转换评分 ≥ 质量阈值的提示词
- 确保发布的都是高质量技能

#### 2. 生成 SKILL.md
- 自动生成结构化的技能文档
- 包含 frontmetadata（名称、描述）
- 概述、工作流程、使用示例

#### 3. 打包 .skill 文件
- 使用 skill-creator 的 `package_skill.py` 打包
- 验证技能结构完整性
- 检查 frontmatter 格式

#### 4. 发布到 ClawdHub
- 自动发布到 ClawdHub 市场
- 使用正确的 registry URL: `https://www.clawhub.ai/api`
- 生成发布报告

## 输出文件

### 数据文件
- **x-prompt-hunter 输出**:
  - `data/prompts.json` - 抓取的原始提示词
  - `data/prompts_deduplicated.json` - 去重后的提示词
  - `data/evaluation_results.json` - LLM 评估结果
  - `data/deduplication_log.json` - 去重日志
  - `data/langfuse_reports/` - Langfuse 报告

- **生成的 Skills**:
  - `/root/clawd/skills/<skill-name>/SKILL.md` - 生成的技能文档
  - `/root/clawd/skills/<skill-name>/<skill-name>.skill` - 打包文件

### 报告文件
- **工作流报告**:
  - `/root/clawd/reports/integrated-workflow-report-YYYYMMDD-HHMM.md` - 整合工作流报告

### 日志文件
- **运行日志**:
  - `/root/clawd/logs/integrated-prompt-workflow.log` - 整合脚本运行日志

## 输出示例

### 报告文件内容

```markdown
# 整合的 AI 提示词自动化流程报告

**生成时间**: 2026-02-02 10:30:00

## 📊 流程统计

| 阶段 | 工具 | 状态 | 详情 |
|------|------|------|------|
| Stage 1 | x-prompt-hunter | ✅ 完成 | 30 个提示词已评估 |
| Stage 2.1 | prompt-to-skill-converter | ✅ 完成 | 15 个 Skill 已转换 |
| Stage 2.2 | skill-creator | ✅ 完成 | 打包完成 |
| Stage 2.3 | ClawdHub | ✅ 完成 | 12 成功, 3 失败 |

## 🔍 数据详情

**Stage 1: 数据发现（x-prompt-hunter）**
- 查询: AI prompts
- 数据源: GitHub, HuggingFace
- 评估限制: 30 个
- 已评估: 30 个

**Stage 2: 转换和发布（prompt-to-skill-converter）**
- 质量阈值: 80
- 已转换: 15 个 Skill
- 已发布: 12 个
- 发布失败: 3 个

## 📈 质量指标

- **语义去重**: ✅ x-prompt-hunter 自动执行
- **LLM 评估**: ✅ Claude API 评分（创新性、实用性、清晰度、可复用性）
- **Langfuse 追踪**: ✅ 质量趋势记录
- **质量过滤**: ✅ 只转换评分 ≥ 80 的提示词
```

### 通知示例

```
📊 **整合工作流完成！**

**Stage 1: 数据发现（x-prompt-hunter）**
• 查询: AI prompts
• 评估提示词: 30 个
• 特性: 语义去重 + LLM 评估 + Langfuse 追踪

**Stage 2: 转换发布（prompt-to-skill-converter）**
• 质量阈值: 80
• 转换 Skills: 15 个
• ClawdHub 发布: 12 成功

**报告**: /root/clawd/reports/integrated-workflow-report-20260202-103000.md
**详情**: 查看日志: /root/clawd/logs/integrated-prompt-workflow.log
🚀 **下一个周期**: 明天 9:00
📱 **通知**: 已发送到 Feishu 和 Slack
```

## 主要优势

### 整合前 vs 整合后

| 特性 | 整合前 | 整合后 |
| ------ | --- | ------ |
| 命令数量 | 2+ | 1 ✅ |
| 语义去重 | 可选 | *强制* ✅ |
| LLM 评估 | 可选 | *强制* ✅ |
| 统一报告 | 无 | *自动生成* ✅ |
| Git 提交 | 手动 | *自动* ✅ |
| 通知机制 | 无 | *自动* ✅ |
| 测试模式 | 无 | *有* ✅ |
| 多源数据 | 分散 | *整合* ✅ |

### 核心优势

1. **一键自动化**: 一个命令完成从发现到发布的全流程
2. **智能去重**: 语义相似度计算，避免重复内容
3. **专业评估**: Claude API 多维度质量评估
4. **质量追踪**: Langfuse 实时追踪质量趋势
5. **自动通知**: 双平台通知（Slack + Feishu）
6. **Git 自动化**: 自动提交和推送变更
7. **灵活配置**: 支持自定义查询、阈值、限制等参数
8. **测试模式**: 支持测试运行，不实际发布

## 安装依赖

### Python 依赖

```bash
cd /root/clawd/skills/ai-prompt-workflow
pip install -r requirements.txt
```

**主要依赖：**
- `sentence-transformers` - 语义相似度计算
- `PyGithub` - GitHub API
- `datasets` - HuggingFace 数据集
- `anthropic` - Claude API
- `langfuse` - 质量追踪
- `pyyaml` - 配置管理

### CLI 工具

```bash
# bird CLI (用于 Twitter API)
npm install -g @sugarcube/cli

# ClawdHub CLI (已包含在 Clawdbot 中)
```

## 环境变量配置

在 `~/.bashrc` 或 `.env.d/` 文件中配置以下变量：

```bash
# GitHub API (用于抓取 GitHub 提示词)
export GITHUB_TOKEN="your_github_token"

# HuggingFace Token (用于访问数据集)
export HUGGINGFACE_TOKEN="your_huggingface_token"

# Claude API (必需，用于评估功能)
export ANTHROPIC_API_KEY="your_anthropic_api_key"

# Langfuse (用于质量追踪)
export LANGFUSE_PUBLIC_KEY="your_public_key"
export LANGFUSE_SECRET_KEY="your_secret_key"

# SearXNG (可选，用于元搜索)
export SEARXNG_URL="http://localhost:8080"

# Firecrawl API (可选，用于高级网页抓取)
export FIRECRAWL_API_KEY="your_api_key_here"

# ClawdHub Token (用于发布)
export CLAWDHUB_TOKEN="clh_Ki_M1Xiws5Qzi83gqdZhYG3jXSuZOnEfQOxhaRsjHcw"

# Twitter API Key (用于 Twitter 收集)
export TWITTER_API_KEY="your_twitter_api_key"
```

**获取 API 密钥：**
- GitHub: Settings → Developer settings → Personal access tokens
- HuggingFace: Account settings → Access tokens
- Anthropic: https://console.anthropic.com/
- Langfuse: https://cloud.langfuse.com/
- Firecrawl: https://firecrawl.dev/
- ClawdHub: 已配置（`clh_Ki_M1Xiws5Qzi83gqdZhYG3jXSuZOnEfQOxhaRsjHcw`）
- Twitter: twitterapi.io

## 配置文件

### x-prompt-hunter config.yaml

位置：`/root/clawd/skills/x-prompt-hunter/config.yaml`

```yaml
# 语义去重配置
semantic_dedup:
  enabled: true
  model_name: "all-MiniLM-L6-v2"
  similarity_threshold: 0.85
  log_file: "data/deduplication_log.json"

# GitHub 配置
github:
  enabled: true
  token: ""  # 从环境变量读取
  repos:
    - "f/awesome-chatgpt-prompts"
  output_file: "data/github_prompts.json"

# HuggingFace 配置
huggingface:
  enabled: true
  datasets:
    - "Gustavosta/Stable-Diffusion-Prompts"
  output_file: "data/hf_prompts.json"

# LLM 评估配置
llm_judge:
  enabled: true
  provider: "anthropic"
  model: "claude-3-5-sonnet-20241022"
  output_file: "data/evaluation_results.json"

# Langfuse 追踪配置
langfuse:
  enabled: true
  project_name: "prompt-hunter"
  output_dir: "data/langfuse_reports"
```

## 高级用法

### 场景1：只进行数据发现（不发布）

```bash
# 只运行 Stage 1
cd /root/clawd/skills/x-prompt-hunter
python3 main.py pipeline --query "AI prompts" --limit 100 --evaluate-limit 50

# 查看评估结果
cat /root/clawd/skills/x-prompt-hunter/data/evaluation_results.json | jq '.'
```

### 场景2：手动审查后再发布

```bash
# 1. 运行数据发现
bash /root/clawd/scripts/integrated-prompt-workflow.sh --test-mode

# 2. 手动审查生成的 Skills
ls -la /root/clawd/skills/ | tail -20

# 3. 手动编辑 SKILL.md
nano /root/clawd/skills/example-skill/SKILL.md

# 4. 手动打包和发布
python3 /usr/lib/node_modules/clawdbot/skills/skill-creator/scripts/package_skill.py /root/clawd/skills/example-skill
clawdhub publish example-skill.skill --registry https://www.clawhub.ai/api
```

### 场景3：调整质量阈值

```bash
# 更严格的质量控制
bash /root/clawd/scripts/integrated-prompt-workflow.sh \
  --quality-threshold 85 \
  --query "system prompts"

# 更宽松的质量控制（更多内容）
bash /root/clawd/scripts/integrated-prompt-workflow.sh \
  --quality-threshold 60 \
  --query "creative writing"
```

### 场景4：专注于特定数据源

修改 `config.yaml` 禁用某些数据源：

```yaml
# 只使用 GitHub
github:
  enabled: true
huggingface:
  enabled: false
```

### 场景5：监控质量趋势

```bash
# 对比本周与上周的质量
cd /root/clawd/skills/x-prompt-hunter
python3 main.py report --type comparison --days1 7 --days2 14

# 查看趋势报告
python3 main.py report --type trend --days 30
```

## 故障排查

### 问题1：sentence-transformers 模型下载慢

**解决：** 预先下载模型或使用镜像
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple sentence-transformers
```

### 问题2：Claude API 评估失败

**检查：**
1. `ANTHROPIC_API_KEY` 是否正确设置
2. API key 是否有足够余额
3. 查看日志 `/root/clawd/logs/integrated-prompt-workflow.log`

### 问题3：Langfuse 追踪失败

**检查：**
1. Langfuse 公钥和私钥是否正确
2. 网络连接是否正常
3. 查看 Langfuse 控制台

### 问题4：ClawdHub 发布失败

**检查：**
1. ClawdHub token 是否有效
2. Registry URL 是否正确：`https://www.clawhub.ai/api`
3. .skill 文件格式是否正确
4. 查看日志获取详细错误信息

### 问题5：没有达到质量阈值的提示词

**解决：**
1. 降低质量阈值（如从 80 降到 60）
2. 增加数据源或调整查询关键词
3. 检查评估结果，查看评分分布

```bash
# 查看评分分布
cd /root/clawd/skills/x-prompt-hunter
cat data/evaluation_results.json | jq '.[] | .total_score' | sort -n | uniq -c
```

## 性能优化建议

1. **批量评估**：调整 `--evaluate-limit` 和 `--batch-size` 以平衡速度和API成本
2. **限制抓取**：合理设置 `--limit` 避免过量数据
3. **去重阈值**：在 `config.yaml` 中调整 `similarity_threshold`
4. **增量更新**：定期运行而非全量抓取
5. **并发处理**：在 `collect_prompts_enhanced.py` 中调整 `MAX_WORKERS`

## 监控和维护

### 检查日志

```bash
# 查看最新日志
tail -f /root/clawd/logs/integrated-prompt-workflow.log

# 查看错误
grep ERROR /root/clawd/logs/integrated-prompt-workflow.log
```

### 查看报告

```bash
# 查看最新报告
ls -lt /root/clawd/reports/integrated-workflow-report-*.md | head -1

# 查看报告内容
cat /root/clawd/reports/integrated-workflow-report-*.md
```

### Git 状态

```bash
# 查看自动提交的变更
cd /root/clawd
git log --oneline -10

# 查看最新提交
git show HEAD
```

## 与其他技能的关系

### 依赖技能

- **skill-creator**: 用于打包技能
- **skill-creator**: 用于初始化技能结构
- **skill-lookup**: 用于发现现有技能，避免重复
- **skill-manager**: 用于管理技能版本和依赖

### 相关技能

- **twitter-search**: Twitter 搜索和收集（集成）
- **searxng**: 隐私保护的元搜索（集成）
- **firecrawl**: 高级网页抓取（集成）

## 最佳实践

### 质量优先原则

- **1 个高质量 skill > 10 个低质量 skill**
- 设置合理的质量阈值（建议 70-80）
- 人工审查自动生成的 SKILL.md
- 测试每个 skill 的功能

### 渐进式自动化

1. **初始阶段**：手动运行，理解流程
2. **测试阶段**：使用 `--test-mode` 验证
3. **自动化阶段**：设置 cron 定时任务
4. **优化阶段**：根据反馈调整参数

### 迭代改进

1. 监控发布技能的用户反馈
2. 查看 Langfuse 质量趋势
3. 调整评估标准和阈值
4. 优化提示词收集策略
5. 更新转换模板

## 安全和隐私

### 数据安全

- **不要** 在代码中硬编码 API 密钥
- 使用环境变量或 `.env` 文件
- 定期轮换 API 密钥
- 限制 API 密钥的权限范围

### 内容安全

- **不要** 转换包含敏感信息的提示词
- **不要** 发布可能违反服务条款的内容
- 人工审查自动生成的内容
- 遵守 ClawdHub 的内容政策

## 示例使用场景

### 场景1：建立 AI 写作技能库

```bash
# 每天收集创意写作提示词
bash /root/clawd/scripts/integrated-prompt-workflow.sh \
  --query "creative writing prompts" \
  --limit 100 \
  --evaluate-limit 50 \
  --quality-threshold 75

# 查看生成的写作技能
ls -la /root/clawd/skills/ | grep writing
```

### 场景2：代码辅助技能自动化

```bash
# 收集编程相关的提示词
bash /root/clawd/scripts/integrated-prompt-workflow.sh \
  --query "programming prompts code assistant" \
  --limit 80 \
  --evaluate-limit 40 \
  --quality-threshold 80
```

### 场景3：AI 艺术提示词库

```bash
# 收集图像生成提示词
bash /root/clawd/scripts/integrated-prompt-workflow.sh \
  --query "AI art prompts midjourney dalle" \
  --limit 100 \
  --evaluate-limit 60 \
  --quality-threshold 70
```

## 更新日志

### v1.0.0 (2026-02-02)
- ✅ 整合 x-prompt-hunter 和 prompt-to-skill-converter
- ✅ 一键执行完整流程
- ✅ 支持自定义参数
- ✅ 自动生成报告
- ✅ Git 自动提交
- ✅ 双平台通知（Slack + Feishu）
- ✅ 测试模式支持

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可

MIT License
