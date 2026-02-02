---
name: prompt-to-skill-converter
description: "Automated end-to-end workflow to discover AI prompts from multiple sources (Twitter/X, Reddit, GitHub, Hacker News, SearXNG, Firecrawl), evaluate their commercial potential, and convert high-quality prompts into Clawdbot Skills using Claude's skill creation methodology. Use when building a profitable skills marketplace by mining social media, code repositories, and web content for prompt patterns and turning them into distributable skills. The workflow includes: (1) collecting prompts from diverse sources (Twitter API, Reddit API, GitHub search, Hacker News, SearXNG metasearch, Firecrawl web scraping), (2) analyzing prompt quality and commercial viability, (3) transforming prompts into structured SKILL.md files, (4) packaging skills for ClawdHub distribution, and (5) publishing to the marketplace with registry configuration."
---

# Prompt To Skill Converter

## Overview

**转换发布层** - 自动化工作流，将高质量提示词转换为 Clawdbot Skills 并发布到 ClawdHub。

**架构定位**：
```
┌─────────────────────┐
│ x-prompt-hunter     │ ← 数据发现层（去重+评估）
└─────────┬───────────┘
        │ 高质量提示词
        ▼
┌─────────────────────┐
│ prompt-to-skill-    │ ← 转换发布层（SKILL.md + ClawdHub）
│ converter          │
└─────────────────────┘
```

**注意**：此技能依赖 **x-prompt-hunter** 数据发现层。建议先使用 x-prompt-hunter 进行提示词去重和评估，然后使用本技能进行转换和发布。

## Core Workflow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. Load High   │───▶│  2. Convert     │───▶│  3. Package     │
│  Quality Prompts│    │  to Skills      │    │  & Test        │
│  (from x-       │    │                 │    │                 │
│   prompt-hunter)│    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐    ┌─────────────────┌─────────────────┐
│  5. Publish to  │◀───│  4. Validate     │◀───│  Quality Check  │
│  ClawdHub       │    │  & Document     │    │                 │
│  (with --registry)│   │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Data Sources

### Recommended Workflow (Two-Stage Architecture)

**Stage 1: Data Discovery & Quality Control (x-prompt-hunter)**
```bash
# 使用 x-prompt-hunter 进行去重和评估
cd /root/clawd/skills/x-prompt-hunter

# 完整流程：抓取 → 去重 → 评估 → 生成报告
python3 main.py pipeline --query "AI prompts" --limit 100 --evaluate-limit 30

# 高质量提示词输出到: data/prompts_deduplicated.json
# 评估结果输出到: data/evaluation_results.json
```

**Stage 2: Conversion & Publishing (prompt-to-skill-converter)**
```bash
# 加载高质量提示词并转换为 Skills
cd /root/clawd/skills/prompt-to-skill-converter

# 转换为 Skills
python3 scripts/convert-prompts-to-skills.py \
  --input /root/clawd/skills/x-prompt-hunter/data/evaluation_results.json \
  --quality-threshold 80

# 打包并发布
python3 /usr/lib/node_modules/clawdbot/skills/skill-creator/scripts/package_skill.py /root/clawd/skills/<skill-name>
clawdhub publish <skill-name>.skill --registry https://www.clawhub.ai/api
```

### Legacy Data Sources (Direct Collection)

**注意**：以下收集方法为遗留功能，建议优先使用 **x-prompt-hunter** 的数据发现层。

**Social Media:**
- **Twitter/X**: Real-time prompt discovery via API (bird CLI)
- **Reddit**: Community-driven prompt collections and discussions

**Developer Platforms:**
- **GitHub**: Prompt libraries in code repositories, README files, issues

**News & Discussion:**
- **Hacker News**: Tech-focused prompt discussions and resources

**Web Search & Scraping:**
- **SearXNG**: Privacy-respecting metasearch across multiple engines
- **Firecrawl**: AI-powered web scraping for JavaScript-heavy sites

### One-Command Full Workflow (Legacy)

**注意**：此为遗留工作流，建议使用上述两阶段架构。

```bash
# Run complete workflow (collect → evaluate → convert → package → publish)
bash scripts/full-prompt-workflow.sh

# With options:
bash scripts/full-prompt-workflow.sh --quality-threshold 60 --test-mode
```

This script integrates all components automatically and provides end-to-end automation.

## Prerequisites

### API Keys & Tokens
1. **Twitter API Key**: Configure in `~/.bashrc` (see twitter-search skill) - Used for Twitter/X prompt collection
2. **Reddit API Credentials**: Required for Reddit data collection (create app at reddit.com/prefs/apps)
3. **GitHub Personal Access Token**: For GitHub API access (optional, increases rate limits)
4. **ClawdHub Token**: Set up for publishing (already configured: `clh_Ki_M1Xiws5Qzi83gqdZhYG3jXSuZOnEfQOxhaRsjHcw`)
   - **Important**: Registry URL must be `https://www.clawhub.ai/api`

### Software Requirements
5. **Python 3.8+**: Required for automation scripts
6. **SearXNG Instance**: Local or remote metasearch instance (optional, see searxng skill)
7. **Firecrawl API Key**: For advanced web scraping (optional, see firecrawl skill)
8. **Skill Creation Scripts**: Available from skill-creator (`init_skill.py`, `package_skill.py`)

### CLI Tools
- **bird CLI**: `npm install -g @sugarcube/cli` (for Twitter API)
- **ClawdHub CLI**: Included with Clawdbot (for publishing)

## Step 1: Collect Prompts from Multiple Sources

Collect AI prompts from diverse sources for comprehensive coverage and quality.

### Source 1: Twitter/X (Social Media)

Use the twitter-search skill to discover high-quality prompts with engagement metrics.

### Search Queries

Use these patterns to find prompts:

```bash
# AI prompts in general
./scripts/run_search_improved.sh --smart-query prompts --lang en --min-likes 20 --min-retweets 10 --max-results 200

# Specific prompt types
./scripts/run_search_improved.sh "\"prompt engineering\" OR \"ChatGPT prompts\" OR \"Claude prompts\"" \
  --lang en --min-likes 30 --min-retweets 15 --max-results 100

# Prompt libraries/resources
./scripts/run_search_improved.sh "prompt library OR \"prompt collection\" OR \"prompt template\"" \
  --lang en --min-likes 15 --max-results 150
```

### Data Collection Strategy

**What to look for:**
- Prompt templates with clear structure
- Actionable prompts with specific outputs
- Domain-specific prompts (coding, writing, design, etc.)
- High engagement (likes/retweets) indicates quality/demand
- Reposted or "saved" prompts suggest value

**Red flags:**
- Generic/vague prompts
- Prompts requiring paid tools
- NSFW or unethical content
- Overly long prompts (>500 words)
- Prompts requiring manual setup

**Output:** Save results to JSON file for analysis
```bash
./scripts/run_search_improved.sh --smart-query prompts --format json > /tmp/prompts.json
```

### 🔥 改进方案：使用 collect-prompts-twitter.sh

推荐使用改进的 Twitter 收集脚本，它提供更好的数据质量和自动化程度：

```bash
# 运行改进的 Twitter 收集脚本
bash scripts/collect-prompts-twitter.sh

# 数据自动保存到：/root/clawd/data/prompts/twitter-prompts.jsonl

# 查看收集的数据
cat /root/clawd/data/prompts/twitter-prompts.jsonl | jq '.'
```

**优势：**
- ✅ 自动提取提示词（无需手动筛选）
- ✅ 包含完整的互动数据（点赞、转发、评论）
- ✅ 中英文双语搜索覆盖
- ✅ 智能数据处理和去重
- ✅ JSONL 格式便于后续处理

**数据示例：**
```json
{
  "timestamp": "2026-02-01T12:00:00",
  "source": "twitter",
  "search_query": "AI prompt engineering",
  "tweet_id": "1234567890",
  "tweet_url": "https://twitter.com/user/status/1234567890",
  "author_name": "AI Researcher",
  "author_handle": "airesearcher",
  "text": "Here's a great prompt for coding assistants...",
  "prompts_found": 2,
  "prompts": ["prompt 1", "prompt 2"],
  "likes": 150,
  "retweets": 45,
  "replies": 23
}
```

### Source 2: Reddit (Community Content)

Collect prompts from Reddit communities focused on AI, prompt engineering, and specific domains.

```bash
# Run Reddit collection script
bash scripts/collect-prompts-reddit.sh

# Data saved to: /root/clawd/data/prompts/reddit-prompts.jsonl
```

**Target Subreddits:**
- r/ChatGPT, r/PromptEngineering, r/artificial
- Domain-specific: r/datasets, r/MachineLearning, r/LocalLLaMA

**Advantages:**
- Community-vetted quality (upvotes = engagement)
- Detailed discussions and refinements
- Diverse perspectives and use cases

### Source 3: GitHub (Developer Resources)

Search for prompt libraries and prompt-related code repositories.

```bash
# Run GitHub collection script
bash scripts/collect-prompts-github.sh

# Data saved to: /root/clawd/data/prompts/github-prompts.jsonl
```

**Search Patterns:**
- Repository names: "prompt-library", "awesome-prompts", "prompt-templates"
- File patterns: `README.md`, `prompts.md`, `PROMPTS.md`
- Code comments and documentation

**Advantages:**
- High-quality, developer-focused prompts
- Well-documented and structured
- Often includes usage examples

### Source 4: Hacker News (Tech Discussions)

Extract prompts from HN discussions and comments.

```bash
# Run Hacker News collection script
bash scripts/collect-prompts-hn.sh

# Data saved to: /root/clawd/data/prompts/hn-prompts.jsonl
```

**Search Criteria:**
- Stories with "prompt" or "prompt engineering"
- Comments mentioning prompt techniques
- Show HN discussions about AI tools

**Advantages:**
- Tech-savvy audience
- Informed discussions
- Trend detection

### Source 5: SearXNG (Metasearch)

Use privacy-respecting metasearch to find prompt-related content across multiple search engines.

```bash
# Run SearXNG collection script
bash scripts/collect-prompts-searxng.sh

# Data saved to: /root/clawd/data/prompts/searxng-prompts.jsonl
```

**Configuration:**
```bash
# Set SearXNG instance URL (in .env.d/)
export SEARXNG_URL=http://localhost:8080

# Or use a public instance
export SEARXNG_URL=https://searx.be
```

**Advantages:**
- No API rate limits
- Multiple search engines in one query
- Privacy-focused
- Customizable search filters

### Source 6: Firecrawl (Advanced Web Scraping)

Use AI-powered web scraping for JavaScript-heavy sites and complex web pages.

```bash
# Run Firecrawl collection script
bash scripts/collect-prompts-firecrawl.sh

# Data saved to: /root/clawd/data/prompts/firecrawl-prompts.jsonl
```

**Configuration:**
```bash
# Set Firecrawl API key (in .env.d/)
export FIRECRAWL_API_KEY=your_api_key_here
```

**Advantages:**
- Handles JavaScript-rendered content
- Bypasses anti-bot measures
- Extracts clean, LLM-ready data
- Supports crawling entire sites

**Use Cases:**
- Scrape prompt library websites
- Extract prompts from documentation sites
- Collect from specialized AI platforms

### Unified Collection Workflow

For comprehensive collection, use the integrated multi-source collector:

```bash
# Collect from all configured sources
bash scripts/collect-prompts-all.sh

# Or run the full workflow (includes collection)
bash scripts/full-prompt-workflow.sh --collect-only
```

**Output:** All sources save to unified format in `/root/clawd/data/prompts/`

## Step 2: Evaluate & Filter Prompts

Load the captured prompts and evaluate them against commercial viability criteria.

### Evaluation Criteria

Use the evaluation framework in `references/evaluation-criteria.md`:

1. **Clarity & Completeness** (1-10):
   - Clear objective?
   - Complete instructions?
   - Easy to follow?

2. **Uniqueness** (1-10):
   - Novel approach?
   - Different from existing skills?
   - Solves a real problem?

3. **Market Potential** (1-10):
   - High engagement?
   - Reusable workflow?
   - Clear audience?

4. **Technical Feasibility** (1-10):
   - Can be automated?
   - Within Clawdbot capabilities?
   - Reasonable complexity?

**Scoring Threshold:** Only convert prompts with total score ≥ 30/40

### Evaluation Process

```python
# Load and evaluate prompts
python3 scripts/evaluate_prompts.py /tmp/prompts.json --threshold 30
```

This script:
- Loads the JSON data
- Applies evaluation criteria
- Scores each prompt
- Outputs ranked list with scores
- Filters by threshold

**Output:** `/tmp/evaluated_prompts.json` with scores and rankings

## Step 3: Convert to Skill Structure

For each high-scoring prompt, use Claude to transform it into a proper Clawdbot Skill structure.

### Manual Conversion Workflow (Interactive)

For the first few conversions, work interactively to establish patterns:

```bash
# Initialize a new skill
python3 /usr/lib/node_modules/clawdbot/skills/skill-creator/scripts/init_skill.py <skill-name> --path /root/clawd/skills

# Claude will:
# 1. Analyze the original prompt
# 2. Extract the core workflow
# 3. Design the skill structure (task-based, workflow-based, etc.)
# 4. Write SKILL.md with proper frontmatter and instructions
# 5. Create necessary scripts/ or references/ as needed
```

### Conversion Guidelines

When transforming a prompt into a skill:

**1. Identify the Core Pattern**
- What is the prompt doing?
- What tools/resources are used?
- What are the inputs and outputs?

**2. Choose Skill Structure**
- **Task-Based**: If prompt provides multiple operations
- **Workflow-Based**: If prompt is a sequential process
- **Reference/Guidelines**: If prompt is about standards/templates

**3. Write Frontmatter**
- `name`: Descriptive, kebab-case (e.g., `email-drafter`)
- `description`: Include what it does + when to use it + trigger scenarios

**4. Draft SKILL.md Body**
- Overview: 1-2 sentences
- Workflow/Tasks: Step-by-step instructions
- Examples: Concrete use cases
- Resources: Link to scripts/references as needed

**5. Create Supporting Resources**
- `scripts/`: Automatable code
- `references/`: Documentation to load on-demand
- `assets/`: Templates or output files

### Conversion Template

Use the template in `references/conversion-template.md` as a starting point:

```markdown
---
name: [skill-name]
description: [What it does + when to use it + trigger scenarios]
---

# [Skill Title]

## Overview
[Brief explanation]

## [Structure: Workflow / Tasks / Guidelines]
[Step-by-step instructions or task categories]

## Quick Start
[How to use immediately]

## Resources (as needed)
### scripts/
[Scripts and their purpose]

### references/
[Reference documentation]
```

## Step 4: Package & Test

Once SKILL.md and resources are complete, package the skill for distribution.

### Packaging

```bash
# Validate and package
python3 /usr/lib/node_modules/clawdbot/skills/skill-creator/scripts/package_skill.py /root/clawd/skills/<skill-name>
```

This:
- Validates the skill structure
- Checks frontmatter format
- Creates `.skill` file (zip)
- Reports any errors

### Testing

Before publishing, test the skill:

1. **Load the skill**: Open a new session and use it
2. **Test workflows**: Follow the steps in SKILL.md
3. **Verify outputs**: Ensure expected results
4. **Check edge cases**: Try unusual inputs
5. **Document issues**: Fix before publishing

### Troubleshooting

**Packaging fails?**
- Check YAML frontmatter format
- Ensure `name` and `description` are present
- Verify SKILL.md is valid markdown

**Testing reveals bugs?**
- Update SKILL.md instructions
- Fix scripts if needed
- Re-package and re-test

## Step 5: Publish to ClawdHub

Publish packaged skills to the marketplace with proper registry configuration.

### Publishing Workflow

```bash
# Login to ClawdHub (first time only)
clawdhub login
# Enter token: clh_Ki_M1Xiws5Qzi83gqdZhYG3jXSuZOnEfQOxhaRsjHcw

# Publish skill with explicit registry URL (recommended)
clawdhub publish <skill-name>.skill --registry https://www.clawhub.ai/api
```

### Important: Registry Configuration

**Critical**: Always specify the registry URL when publishing:

```bash
# ✅ Correct: Explicit registry
clawdhub publish my-skill.skill --registry https://www.clawhub.ai/api

# ❌ Wrong: May publish to wrong registry
clawdhub publish my-skill.skill
```

**Why This Matters:**
- ClawdHub has changed registry URLs over time
- Using explicit `--registry` ensures publication to the correct destination
- Old URLs like `clawdhub.com` or `clawhub.ai` may redirect incorrectly

### Publishing Script (Automation)

The automated publishing script includes proper registry configuration:

```bash
# Use the automated publishing script
bash scripts/batch-upload-skills-v3.sh

# This script:
# - Scans for packaged skills
# - Validates each .skill file
# - Publishes with --registry https://www.clawhub.ai/api
# - Generates a detailed report
```

**Script Features:**
- ✅ Batch publishing of multiple skills
- ✅ Automatic registry URL injection
- ✅ Error handling and retry logic
- ✅ Progress tracking and logging
- ✅ Report generation

### Skill Metadata Preparation

Before publishing, prepare skill metadata:

1. **Category**: Choose appropriate category
   - `productivity`, `development`, `design`, `business`, etc.

2. **Tags**: Add relevant tags
   - `ai`, `automation`, `prompts`, `workflow`, etc.

3. **Price**: Set pricing (free/paid)
   - Start with free for testing
   - Adjust based on demand

4. **Description**: Write compelling marketplace description
   - Focus on value/benefits
   - Include use case examples
   - Mention features

### Post-Publishing

- Monitor download stats
- Collect user feedback
- Update based on suggestions
- Version control changes

## Automation Scripts

### scripts/collect-prompts-twitter.sh 🔥

改进的 Twitter/X 提示词收集脚本（最新版本）：

```bash
bash scripts/collect-prompts-twitter.sh
```

**特性：**
- 使用 Twitter API 进行数据收集（通过 bird CLI）
- 中英文双语搜索（12 个查询词）
- 自动提取提示词（代码块、引用文本、指令）
- 记录互动数据（点赞、转发、评论）
- 智能数据处理和去重
- 保存为 JSONL 格式便于后续处理

**数据输出：**
- 文件：`/root/clawd/data/prompts/twitter-prompts.jsonl`
- 格式：每行一个 JSON 对象
- 包含字段：timestamp, source, tweet_id, tweet_url, author_name, author_handle, text, prompts_found, prompts, likes, retweets, replies

**搜索查询：**
- 英文：AI prompt engineering, ChatGPT prompts, Claude prompts, midjourney prompts, AI art prompts, prompt engineering tips, best AI prompts, prompt templates
- 中文：AI 提示词, ChatGPT 指令, AI 绘画提示词, 提示词工程

**依赖：**
- bird CLI：`npm install -g @sugarcube/cli`
- Python 3
- TWITTER_API_KEY 环境变量（已配置）

### scripts/collect_prompts.py

Automates prompt discovery from X:

```bash
python3 scripts/collect_prompts.py --query "prompts" --max-results 200 --output /tmp/prompts.json
```

**Features:**
- Uses twitter-search skill internally
- Applies engagement filters automatically
- Saves structured JSON output
- Supports scheduled runs (cron)

### scripts/collect_prompts_enhanced.py 🔥

增强版 AI 提示词收集系统（最新推荐版本）：

```bash
# 基本使用（使用默认配置）
python3 scripts/collect_prompts_enhanced.py

# 指定输出目录
python3 scripts/collect_prompts_enhanced.py --output-dir /custom/path

# 快速测试模式（2 个查询，每个最多 3 个结果）
python3 scripts/collect_prompts_enhanced.py --quick-test

# 查看帮助
python3 scripts/collect_prompts_enhanced.py --help
```

**Phase 1 核心特性：**
- ✅ **扩展的搜索关键词库**：50+ 查询组合
- ✅ **智能关键词组合策略**：自动生成有效查询
- ✅ **高级搜索结果过滤**：基于域名、URL 模式
- ✅ **增强的提示词提取算法**：改进的正则表达式
- ✅ **中英文双语搜索**：覆盖更广的内容源
- ✅ **自动分类和质量评分**：0-100 分质量评估
- ✅ **完整的错误处理**：日志记录和优雅退出
- ✅ **并发处理支持**：最多 3 个并发请求
- ✅ **JSONL 格式输出**：便于后续处理

**数据输出：**
- 文件：`/root/clawd/data/prompts/collected/prompts-enhanced-{timestamp}.jsonl`
- 格式：每行一个 JSON 对象
- 包含字段：
  - `timestamp`: 收集时间
  - `query`: 搜索查询
  - `url`: 来源 URL
  - `domain`: 域名
  - `content`: 提取的内容
  - `prompts`: 提取的提示词列表
  - `prompt_count`: 提示词数量
  - `type`: 提示词类型（image-generation, text-generation, video-generation, general）
  - `quality_score`: 质量分数（0-100）
  - `is_truncated`: 是否被截断

**搜索关键词分类：**
- 基础关键词组合（prompt + AI + type + action）
- 专业提示词网站（PromptBase, LearnPrompting 等）
- 平台特定提示词（Midjourney, DALL-E, Stable Diffusion）
- 任务特定查询（代码、写作、设计等）
- 质量导向查询（best, top, high-quality）

**依赖：**
- Python 3.8+
- `requests` 库
- SearXNG 实例（环境变量 `SEARXNG_URL`）

**配置：**
- `SEARXNG_URL`: SearXNG 服务地址（默认：http://localhost:8080）
- `MAX_RESULTS_PER_QUERY`: 每个查询的最大结果数（默认：10）
- `MAX_WORKERS`: 并发工作线程数（默认：3）
- `REQUEST_DELAY`: 请求延迟（默认：1.5 秒）

**改进点（相比旧脚本）：**
1. 更准确的提示词提取（减少导航栏、页脚干扰）
2. 更智能的质量评分算法
3. 更好的错误处理和日志记录
4. 支持快速测试模式
5. 自动分类提示词类型
6. 检测提示词截断

**使用建议：**
- 首次使用建议先用 `--quick-test` 验证配置
- 根据测试结果调整查询词和过滤规则
- 将收集的提示词用于后续的评估和转换流程

### scripts/evaluate_prompts.py

Scores and ranks prompts:

```bash
python3 scripts/evaluate_prompts.py /tmp/prompts.json --threshold 30 --output /tmp/ranked.json
```

**Features:**
- Loads JSON data from collection
- Applies scoring criteria
- Filters by threshold
- Outputs ranked list

### scripts/convert-prompts-to-skills.py 🔥

将收集的提示词批量转换为 Clawdbot Skills：

```bash
# 基本使用（使用默认输入文件）
python3 scripts/convert-prompts-to-skills.py

# 指定输入文件
python3 scripts/convert-prompts-to-skills.py --input /path/to/prompts.jsonl

# 指定质量阈值（只转换高质量提示词）
python3 scripts/convert-prompts-to-skills.py --quality-threshold 60

# 指定输出目录
python3 scripts/convert-prompts-to-skills.py --output-dir /root/clawd/skills

# 查看帮助
python3 scripts/convert-prompts-to-skills.py --help
```

**核心功能：**
- ✅ **批量转换**：处理 JSONL 格式的提示词数据
- ✅ **智能分类**：根据提示词类型自动分类
- ✅ **质量过滤**：只转换高质量提示词
- ✅ **自动命名**：生成符合规范的 skill 名称
- ✅ **SKILL.md 生成**：自动创建结构化的技能文档
- ✅ **进度跟踪**：显示转换进度和统计信息
- ✅ **错误处理**：跳过无效提示词，记录错误日志

**转换流程：**
1. 读取输入文件（JSONL 格式）
2. 解析每个提示词对象
3. 根据质量分数过滤（默认阈值：50）
4. 生成唯一的 skill 名称（kebab-case）
5. 创建 skill 目录结构
6. 生成 SKILL.md 文件（包含 frontmatter 和内容）
7. 记录转换结果到日志

**输出结构：**
```
/root/clawd/skills/
├── example-prompt-skill/
│   ├── SKILL.md
│   └── (optional scripts/ or references/)
├── another-prompt-skill/
│   ├── SKILL.md
│   └── (optional scripts/ or references/)
...
```

**生成的 SKILL.md 包含：**
- `name`: skill 名称（kebab-case）
- `description`: 基于 prompt 内容自动生成
- Overview: 简要说明
- Workflow: 使用步骤
- Examples: 使用示例
- Resources: 相关资源（如有）

**配置选项：**
- `--input`: 输入文件路径（默认：自动查找最新的 prompts 文件）
- `--output-dir`: 输出目录（默认：/root/clawd/skills）
- `--quality-threshold`: 质量阈值（默认：50）
- `--dry-run`: 预览模式，不实际创建文件

**使用示例：**

```bash
# 1. 使用 enhanced 收集脚本收集提示词
python3 scripts/collect_prompts_enhanced.py

# 2. 转换为 skills（只转换质量 >= 60 的提示词）
python3 scripts/convert-prompts-to-skills.py --quality-threshold 60

# 3. 预览模式（查看会创建哪些 skills，但不实际创建）
python3 scripts/convert-prompts-to-skills.py --dry-run

# 4. 查看转换统计
python3 scripts/convert-prompts-to-skills.py --stats
```

**输出统计：**
- 处理的提示词总数
- 转换成功的 skills 数
- 跳过的提示词数（质量不足）
- 错误数
- 转换耗时

**依赖：**
- Python 3.8+
- `json`、`pathlib`、`re` 等标准库
- 已收集的提示词数据（JSONL 格式）

**注意事项：**
- 生成的 SKILL.md 需要人工审查和优化
- 建议先使用 `--dry-run` 预览
- 转换后需要使用 `package_skill.py` 打包
- 发布前需要充分测试

### scripts/batch_convert.py

Batch converts high-scoring prompts to skills (semi-automated):

```bash
python3 scripts/batch_convert.py /tmp/ranked.json --interactive
```

**Features:**
- Iterates through ranked prompts
- Initializes skill for each
- Generates initial SKILL.md draft
- Requires human review before packaging

**Note:** Full automation is not recommended - Claude should guide conversion interactively for quality.

## Reference Documentation

### references/evaluation-criteria.md

Detailed rubric for scoring prompts:

```markdown
# Prompt Evaluation Criteria

## Scoring Guide

### Clarity & Completeness (10 points)
- 10: Crystal clear, complete, no ambiguity
- 8-9: Minor ambiguities, mostly complete
- 5-7: Some missing steps, moderately clear
- 3-4: Vague, incomplete
- 1-2: Confusing, unusable

### Uniqueness (10 points)
- 10: Novel, unlike any existing skill
- 8-9: Unique approach to common problem
- 5-7: Good but not groundbreaking
- 3-4: Similar to existing skills
- 1-2: Duplicate or generic

### Market Potential (10 points)
- 10: High demand, viral engagement
- 8-9: Clear niche audience
- 5-7: Moderate interest
- 3-4: Small audience
- 1-2: Little/no demand

### Technical Feasibility (10 points)
- 10: Easily automatable, fits Clawdbot perfectly
- 8-9: Requires some tools, feasible
- 5-7: Complex but possible
- 3-4: Very difficult, may not work
- 1-2: Impossible or requires external services

## Total Score Calculation
Total = Clarity + Uniqueness + Market + Feasibility (max 40)

**Threshold**: 30/40 (75%) recommended for conversion
```

### references/conversion-template.md

Standardized template for converting prompts to skills.

### references/skill-naming-conventions.md

Guidelines for naming skills consistently:

```markdown
# Skill Naming Conventions

## General Rules
- Use kebab-case (lowercase with hyphens)
- Max 3-5 words
- Be descriptive but concise
- Avoid generic names (e.g., "ai-helper")
- Use domain-specific terms when appropriate

## Examples

✅ Good Names:
- email-drafter
- code-reviewer
- twitter-scanner
- prompt-optimizer

❌ Bad Names:
- AI-helper (too generic)
- the-best-email-writer (too long)
- CodeReviewTool (not kebab-case)
- skill123 (not descriptive)
```

## Best Practices

### Quality Over Quantity

- **1 great skill > 10 mediocre skills**
- Focus on high-scoring prompts only
- Test thoroughly before publishing
- Update regularly based on feedback

### Interactive vs. Automated

**What should be automated:**
- Prompt collection from X
- Initial scoring and filtering
- Skill initialization
- Packaging

**What should be interactive (Claude-guided):**
- Quality evaluation judgments
- Skill structure design
- SKILL.md writing
- Resource creation

### Iterative Improvement

1. Start with manual conversion to understand patterns
2. Document successful conversion patterns
3. Gradually automate repeatable steps
4. Always review AI-generated content
5. Learn from published skills' performance

## Integration with Cron

Schedule regular prompt discovery:

```bash
# Add to crontab
crontab -e

# Daily prompt collection at 9 AM
0 9 * * * cd /root/clawd/skills/prompt-to-skill-converter && python3 scripts/collect_prompts.py --query "prompts" --max-results 200 --output /tmp/prompts_$(date +\%Y\%m\%d).json
```

## Example: End-to-End Workflow

### Traditional Manual Workflow

```bash
# 1. Collect prompts
python3 scripts/collect_prompts.py --query "prompts" --max-results 200 --output /tmp/prompts.json

# 2. Evaluate
python3 scripts/evaluate_prompts.py /tmp/prompts.json --threshold 30 --output /tmp/ranked.json

# 3. Convert (interactive)
python3 scripts/batch_convert.py /tmp/ranked.json --interactive

# 4. For each created skill:
python3 /usr/lib/node_modules/clawdbot/skills/skill-creator/scripts/package_skill.py /root/clawd/skills/<skill-name>

# 5. Publish
clawdhub publish <skill-name>.skill --registry https://www.clawhub.ai/api
```

### Full Automated Workflow (Recommended) 🔥

Use the integrated workflow script for complete automation:

```bash
# Run complete workflow with default settings
bash scripts/full-prompt-workflow.sh

# With custom quality threshold
bash scripts/full-prompt-workflow.sh --quality-threshold 70

# Test mode (no publishing)
bash scripts/full-prompt-workflow.sh --test-mode

# Verbose output
bash scripts/full-prompt-workflow.sh --verbose

# Show help
bash scripts/full-prompt-workflow.sh --help
```

**What It Does:**

1. **Phase 1: Data Collection**
   - Collects from all configured sources (Twitter, Reddit, GitHub, HN, SearXNG, Firecrawl)
   - Saves unified JSONL format to `/root/clawd/data/prompts/collected/`
   - Removes duplicates across sources

2. **Phase 2: Evaluation & Filtering**
   - Applies quality scoring (0-100)
   - Filters by threshold (default: 60)
   - Categorizes prompts by type

3. **Phase 3: Conversion to Skills**
   - Generates unique skill names
   - Creates SKILL.md files with proper structure
   - Generates supporting documentation

4. **Phase 4: Packaging**
   - Validates each skill
   - Creates `.skill` packages
   - Checks for errors

5. **Phase 5: Publishing**
   - Publishes to ClawdHub with `--registry https://www.clawhub.ai/api`
   - Generates detailed report
   - Skips if test mode enabled

**Output:**

```
/root/clawd/
├── data/prompts/
│   ├── collected/           # Collected data (JSONL)
│   └── processed/           # Processed and filtered
├── skills/                  # Generated skills
│   ├── prompt-skill-1/
│   │   └── SKILL.md
│   └── prompt-skill-2/
│       └── SKILL.md
├── reports/
│   └── workflow-<timestamp>.txt
```

**Report Contents:**
- Collection statistics (per source)
- Quality distribution
- Skills created
- Packaging results
- Publishing status
- Errors and warnings

**Schedule with Cron:**

```bash
# Run daily at 9 AM
0 9 * * * cd /root/clawd && bash scripts/full-prompt-workflow.sh

# Run every 6 hours
0 */6 * * * cd /root/clawd && bash scripts/full-prompt-workflow.sh --quality-threshold 70

# Run weekly on Monday 8 AM
0 8 * * 1 cd /root/clawd && bash scripts/full-prompt-workflow.sh --test-mode
```

## Troubleshooting

### Twitter API Issues
- Verify API key in `~/.bashrc`
- Check rate limits
- Try reduced result count

### Low-Quality Prompts
- Adjust evaluation thresholds
- Refine search queries
- Add more engagement filters

### Packaging Errors
- Check YAML syntax
- Verify frontmatter fields
- Ensure SKILL.md is not empty

### Publishing Failures
- Verify ClawdHub token
- Check internet connection
- Validate .skill file format
- **Important**: Ensure `--registry https://www.clawhub.ai/api` is specified

## scripts/full-prompt-workflow.sh 🔥

完整的端到端自动化工作流脚本，整合了数据收集、评估、转换、打包和发布。

### 功能概述

此脚本提供了一键式自动化，将整个提示词转换为 Skill 的流程整合为一个命令：

```bash
bash scripts/full-prompt-workflow.sh [OPTIONS]
```

### 命令选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--quality-threshold` | 60 | 质量阈值（0-100），只转换高于此分数的提示词 |
| `--test-mode` | false | 测试模式，不实际发布到 ClawdHub |
| `--verbose` | false | 详细输出模式 |
| `--dry-run` | false | 预览模式，不执行任何操作 |
| `--help` | - | 显示帮助信息 |

### 工作流阶段

**Phase 1: 数据收集**
- 收集来自 Twitter, Reddit, GitHub, HN, SearXNG, Firecrawl 的提示词
- 保存到 `/root/clawd/data/prompts/collected/`
- 自动去重

**Phase 2: 评估和过滤**
- 应用质量评分（0-100）
- 根据阈值过滤
- 保存到 `/root/clawd/data/prompts/processed/`

**Phase 3: 转换为 Skills**
- 生成 SKILL.md 文件
- 创建 skill 目录结构
- 保存到 `/root/clawd/skills/`

**Phase 4: 打包**
- 验证每个 skill
- 创建 `.skill` 包
- 检查完整性

**Phase 5: 发布**
- 发布到 ClawdHub（带 `--registry https://www.clawhub.ai/api`）
- 生成详细报告
- 测试模式下跳过

### 使用示例

```bash
# 基本使用
bash scripts/full-prompt-workflow.sh

# 提高质量阈值
bash scripts/full-prompt-workflow.sh --quality-threshold 80

# 测试模式（不发布）
bash scripts/full-prompt-workflow.sh --test-mode --verbose
```

### 输出报告

生成结构化报告到 `/root/clawd/reports/workflow-<timestamp>.txt`，包含：

- 每个阶段的统计信息
- 收集的提示词数量
- 质量分布
- 创建的 skills 数量
- 发布状态
- 错误和警告

### Cron 集成

```bash
# 每天早上 9 点运行
0 9 * * * cd /root/clawd && bash scripts/full-prompt-workflow.sh >> /root/clawd/logs/cron-workflow.log 2>&1
```

## Resources

### Required Skills
- **twitter-search-skill**: For Twitter/X prompt discovery
- **skill-creator**: For skill creation framework
- **searxng**: For privacy-respecting metasearch
- **firecrawl-scraper**: For advanced web scraping
- **twitter-reader**: For fetching Twitter post content
- **firecrawl**: For web search and scraping via Firecrawl API

### External Dependencies
- **Twitter API Key**: From twitterapi.io (configured in `~/.bashrc`)
- **Reddit API Credentials**: From reddit.com/prefs/apps (for Reddit data collection)
- **GitHub Personal Access Token**: From github.com/settings/tokens (optional, increases rate limits)
- **SearXNG Instance**: Local or remote metasearch instance (optional)
- **Firecrawl API Key**: From firecrawl.dev (optional, for advanced scraping)
- **ClawdHub Token**: Already configured (`clh_Ki_M1Xiws5Qzi83gqdZhYG3jXSuZOnEfQOxhaRsjHcw`)
  - **Registry URL**: `https://www.clawhub.ai/api` (critical for publishing)

### CLI Tools
- **bird CLI**: `npm install -g @sugarcube/cli` (for Twitter API)
- **ClawdHub CLI**: Included with Clawdbot (for publishing)
- **Python 3.8+**: Required for automation scripts

### Documentation
- Skill Creator Guide: `/usr/lib/node_modules/clawdbot/skills/skill-creator/SKILL.md`
- ClawdHub CLI: Run `clawdhub --help`
- Twitter Search Skill: `/root/clawd/skills/twitter-search-skill/SKILL.md`
