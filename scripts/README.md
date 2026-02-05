# AI Prompts Skill - 工具脚本

这个目录包含用于 AI 提示词转换为 Skill 项目的核心工具。

## 脚本说明

### 1. github-repo-scraper.py
抓取 GitHub 上关于 AI prompts 的仓库。

**功能：**
- 搜索 AI prompts 相关仓库（关键词：ai-prompts, prompt-engineering, chatgpt-prompts 等）
- 过滤条件：至少 100 stars，最近 6 个月有更新
- 输出到：`/root/clawd/data/github-repos.json`

**使用方法：**
```bash
# 设置 GitHub Token（推荐，可避免 API 限流）
export GITHUB_TOKEN=your_token_here

# 运行脚本
python3 /root/clawd/scripts/github-repo-scraper.py
```

### 2. prompt-evaluator.py
评估 AI 提示词的质量。

**评估维度（每个 1-5 分）：**
1. 清晰度 - 提示词是否明确、无歧义
2. 具体性 - 是否提供具体参数和约束
3. 结构化 - 是否有清晰的格式和组织
4. 实用性 - 是否可以实际使用
5. 创新性 - 是否有独特价值

**评分阈值：**
- 优秀：≥20 分
- 良好：15-19 分
- 一般：10-14 分
- 较差：<10 分

**使用方法：**
```bash
# 设置 API Key（必需）
export ANTHROPIC_API_KEY=your_key_here
# 或使用 OpenAI
export OPENAI_API_KEY=your_key_here

# 运行脚本（独立测试）
python3 /root/clawd/scripts/prompt-evaluator.py
```

### 3. run-evaluation.py
完整的评估流程：抓取仓库 → 提取提示词 → 质量评估 → 生成报告。

**输出文件：**
- `/root/clawd/data/github-repos.json` - 抓取的仓库数据
- `/root/clawd/data/evaluation-results.json` - 评估结果
- `/root/clawd/data/evaluation-report.md` - 评估报告（Markdown）

**使用方法：**
```bash
# 设置必需的环境变量
export GITHUB_TOKEN=your_github_token_here
export ANTHROPIC_API_KEY=your_anthropic_api_key_here

# 运行完整流程
python3 /root/clawd/scripts/run-evaluation.py
```

## 安装依赖

```bash
cd /root/clawd/scripts
pip install -r requirements.txt
```

## 环境变量配置

创建 `.env` 文件（可选）：
```bash
cp /root/clawd/scripts/.env.example /root/clawd/scripts/.env
# 编辑 .env 文件，填入你的 API 密钥
```

## 数据目录结构

```
/root/clawd/data/
├── github-repos.json          # 抓取的 GitHub 仓库
├── extracted-prompts.json     # 从仓库提取的提示词
├── evaluation-results.json    # 评估结果
├── evaluation-report.md       # 评估报告
├── scraper.log                # 抓取脚本日志
├── evaluator.log              # 评估脚本日志
└── pipeline.log               # 流程执行日志
```

## 技术说明

### GitHub API 限制
- 未认证：60 requests/hour
- 已认证：5,000 requests/hour

建议设置 `GITHUB_TOKEN` 以避免限流。

### LLM API 调用
- 每个提示词评估约消耗 500-1000 tokens
- 建议使用 Claude Haiku 或 GPT-3.5-turbo（性价比高）
- 批量评估时会自动添加延迟以避免限流

## 故障排除

### 问题：GitHub API 限流
**解决方案：** 设置 `GITHUB_TOKEN` 环境变量

### 问题：LLM API 调用失败
**解决方案：**
- 检查 `ANTHROPIC_API_KEY` 或 `OPENAI_API_KEY` 是否正确
- 确认 API 密钥有足够的配额
- 检查网络连接

### 问题：未找到任何提示词
**解决方案：**
- 检查仓库是否有 README
- 某些仓库可能需要登录才能访问
- 尝试调整过滤条件（修改脚本中的参数）

## 开发说明

### 添加新的评估维度
编辑 `prompt-evaluator.py` 中的 `evaluation_dimensions` 字典。

### 修改搜索关键词
编辑 `github-repo-scraper.py` 中的 `keywords` 列表。

### 自定义报告格式
编辑 `prompt-evaluator.py` 中的 `generate_report` 方法。

## 日志

所有脚本都会输出日志到：
- 终端（stdout/stderr）
- `/root/clawd/data/` 目录下的日志文件

查看日志：
```bash
tail -f /root/clawd/data/pipeline.log
```

## 许可证

MIT License
