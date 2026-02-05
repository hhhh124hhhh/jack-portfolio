# AI Prompt Workflow

**整合的 AI 提示词自动化工作流** - 一键完成从数据发现到技能发布的完整流程。

## 🚀 快速开始

### 一键执行

```bash
# 基本使用
bash /root/clawd/scripts/integrated-prompt-workflow.sh

# 自定义参数
bash /root/clawd/scripts/integrated-prompt-workflow.sh \
  --query "AI prompts" \
  --limit 50 \
  --evaluate-limit 30 \
  --quality-threshold 80

# 测试模式（不发布）
bash /root/clawd/scripts/integrated-prompt-workflow.sh --test-mode
```

### 定时任务

```bash
# 每天早上 9 点运行
0 9 * * * cd /root/clawd && bash scripts/integrated-prompt-workflow.sh >> logs/cron-integrated.log 2>&1
```

## 📋 前置要求

### 1. 安装 Python 依赖

```bash
cd /root/clawd/skills/ai-prompt-workflow
pip install -r requirements.txt
```

### 2. 安装 CLI 工具

```bash
# bird CLI (用于 Twitter API)
npm install -g @sugarcube/cli

# ClawdHub CLI (已包含在 Clawdbot 中)
```

### 3. 配置环境变量

在 `~/.bashrc` 或 `.env.d/` 文件中配置：

```bash
# 必需
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export CLAWDHUB_TOKEN="clh_Ki_M1Xiws5Qzi83gqdZhYG3jXSuZOnEfQOxhaRsjHcw"

# 可选（用于数据收集）
export GITHUB_TOKEN="your_github_token"
export HUGGINGFACE_TOKEN="your_huggingface_token"
export TWITTER_API_KEY="your_twitter_api_key"
export SEARXNG_URL="http://localhost:8080"
export FIRECRAWL_API_KEY="your_api_key_here"

# 可选（用于质量追踪）
export LANGFUSE_PUBLIC_KEY="your_public_key"
export LANGFUSE_SECRET_KEY="your_secret_key"
```

重新加载环境变量：

```bash
source ~/.bashrc
```

## 🎯 工作流程

```
Stage 1: 数据发现
├─ 多源抓取（GitHub, HuggingFace, Twitter, Reddit, HN, SearXNG, Firecrawl）
├─ 语义去重（sentence-transformers）
├─ LLM 评估（Claude API: 创新性/实用性/清晰度/可复用性）
└─ Langfuse 追踪（质量趋势）
      ↓
Stage 2: 转换发布
├─ 质量过滤（只转换高分提示词）
├─ 生成 SKILL.md
├─ 打包 .skill 文件
└─ 发布到 ClawdHub
      ↓
报告和通知
├─ 生成整合报告
├─ Git 自动提交
└─ 双平台通知（Slack + Feishu）
```

## 📊 命令选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--query` | "AI prompts" | 搜索查询关键词 |
| `--limit` | 50 | 每个数据源的抓取限制 |
| `--evaluate-limit` | 30 | LLM 评估的提示词数量限制 |
| `--quality-threshold` | 70 | 质量阈值（0-100） |
| `--test-mode` | false | 测试模式，不发布到 ClawdHub |
| `--help` | - | 显示帮助信息 |

## 📁 输出文件

### 数据文件
- `data/evaluation_results.json` - LLM 评估结果
- `data/langfuse_reports/` - Langfuse 质量报告

### 生成的 Skills
- `/root/clawd/skills/<skill-name>/SKILL.md` - 生成的技能文档
- `/root/clawd/skills/<skill-name>/<skill-name>.skill` - 打包文件

### 报告和日志
- `/root/clawd/reports/integrated-workflow-report-YYYYMMDD-HHMM.md` - 工作流报告
- `/root/clawd/logs/integrated-prompt-workflow.log` - 运行日志

## 🔍 查看结果

```bash
# 查看最新报告
ls -lt /root/clawd/reports/integrated-workflow-report-*.md | head -1
cat $(ls -t /root/clawd/reports/integrated-workflow-report-*.md | head -1)

# 查看日志
tail -f /root/clawd/logs/integrated-prompt-workflow.log

# 查看生成的 skills
ls -la /root/clawd/skills/ | tail -20
```

## ⚙️ 配置

### x-prompt-hunter 配置

编辑 `/root/clawd/skills/x-prompt-hunter/config.yaml`：

```yaml
semantic_dedup:
  enabled: true
  similarity_threshold: 0.85

llm_judge:
  model: "claude-3-5-sonnet-20241022"
  batch_size: 10
```

## 🛠️ 故障排查

### 问题：模型下载慢

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple sentence-transformers
```

### 问题：API 评估失败

1. 检查 `ANTHROPIC_API_KEY` 是否设置
2. 检查 API 余额
3. 查看日志：`tail -f /root/clawd/logs/integrated-prompt-workflow.log`

### 问题：发布失败

1. 检查 `CLAWDHUB_TOKEN` 是否有效
2. 验证 registry URL：`https://www.clawhub.ai/api`
3. 查看 `.skill` 文件格式

## 📚 文档

详细文档请查看 [SKILL.md](SKILL.md)

## 🔗 相关技能

- **x-prompt-hunter**: 数据发现层
- **prompt-to-skill-converter**: 转换发布层
- **skill-creator**: 技能创建框架
- **skill-manager**: 技能管理工具

## 📄 许可

MIT License
