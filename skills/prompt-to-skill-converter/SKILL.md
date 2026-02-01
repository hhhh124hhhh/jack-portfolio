---
name: prompt-to-skill-converter
description: "Automated workflow to discover AI prompts from X (Twitter), evaluate their commercial potential, and convert high-quality prompts into Clawdbot Skills using Claude's skill creation methodology. Use when building a profitable skills marketplace by mining social media for prompt patterns and turning them into distributable skills. The workflow includes: (1) searching X for AI prompts using keywords and engagement filters, (2) analyzing prompt quality and commercial viability, (3) transforming prompts into structured SKILL.md files, (4) packaging skills for ClawdHub distribution, and (5) publishing to the marketplace."
---

# Prompt To Skill Converter

## Overview

Automated workflow for discovering AI prompts from X (Twitter) and converting them into commercial Clawdbot Skills. Uses Claude's skill creation methodology to transform tweet content into properly structured, distributable skills with automatic packaging and marketplace publishing.

## Core Workflow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. Search X    │───▶│  2. Evaluate    │───▶│  3. Convert     │
│     for Prompts │    │  & Filter       │    │  to Skill       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  5. Publish to  │◀───│  4. Package     │◀───│     Test        │
│  ClawdHub       │    │  for Distrib.   │    │     Skill       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

1. **Twitter API Key**: Configure in `~/.bashrc` (see twitter-search skill)
2. **ClawdHub Token**: Set up for publishing (already configured: `clh_6aVBxdBkWmSOoZN9tUDX1nABYZFMqO_ARPUbHbkboj4`)
3. **Python 3+**: Required for automation scripts
4. **Skill Creation Scripts**: Available from skill-creator (`init_skill.py`, `package_skill.py`)

## Step 1: Search X for AI Prompts

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

Publish packaged skills to the marketplace.

### Publishing Workflow

```bash
# Login to ClawdHub (first time only)
clawdhub login
# Enter token: clh_6aVBxdBkWmSOoZN9tUDX1nABYZFMqO_ARPUbHbkboj4

# Publish skill
clawdhub publish <skill-name>.skill
```

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
clawdhub publish <skill-name>.skill
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

## Resources

### Required Skills
- **twitter-search-skill**: For prompt discovery
- **skill-creator**: For skill creation framework

### External Dependencies
- **Twitter API Key**: From twitterapi.io
- **ClawdHub Token**: Already configured

### Documentation
- Skill Creator Guide: `/usr/lib/node_modules/clawdbot/skills/skill-creator/SKILL.md`
- ClawdHub CLI: Run `clawdhub --help`
- Twitter Search Skill: `/root/clawd/skills/twitter-search-skill/SKILL.md`
