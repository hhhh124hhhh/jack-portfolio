# AI Prompt Workflow - 变更日志

## v1.0.0 (2026-02-02)

### ✨ 新功能
- **整合 x-prompt-hunter 和 prompt-to-skill-converter**
  - 将两个独立技能整合为一个统一的工作流
  - 一键执行从数据发现到发布的完整流程

- **自动化流程**
  - Stage 1: 数据发现（多源抓取 + 语义去重 + LLM 评估 + Langfuse 追踪）
  - Stage 2: 转换发布（质量过滤 + 生成 SKILL.md + 打包 + 发布到 ClawdHub）
  - 自动生成整合报告
  - Git 自动提交和推送
  - 双平台通知（Slack + Feishu）

- **命令行选项**
  - `--query`: 自定义搜索查询
  - `--limit`: 每个数据源的抓取限制
  - `--evaluate-limit`: LLM 评估的提示词数量限制
  - `--quality-threshold`: 质量阈值（0-100）
  - `--test-mode`: 测试模式，不发布到 ClawdHub

- **数据源支持**
  - GitHub (通过 API)
  - HuggingFace (数据集)
  - Twitter/X (通过 bird CLI)
  - Reddit (社区内容)
  - Hacker News (技术讨论)
  - SearXNG (元搜索)
  - Firecrawl (高级网页抓取)

### 📚 文档
- **SKILL.md**: 完整的技能文档（12KB+）
  - 概述和快速开始
  - 工作流详解
  - 命令选项
  - 输出文件说明
  - 高级用法
  - 故障排查
  - 性能优化建议
  - 最佳实践

- **README.md**: 快速入门指南
  - 前置要求
  - 一键执行
  - 定时任务配置
  - 查看结果
  - 常见问题

- **examples.sh**: 使用示例脚本
  - 6 个实际使用场景
  - 定时任务示例
  - 查看结果命令

### 🔧 技术实现
- 整合脚本：`/root/clawd/scripts/integrated-prompt-workflow.sh`
- 依赖管理：`requirements.txt`
- 配置文件：x-prompt-hunter 的 `config.yaml`

### 📊 输出
- 数据文件：`data/evaluation_results.json`
- 质量报告：`data/langfuse_reports/`
- 生成的 Skills：`/root/clawd/skills/<skill-name>/`
- 工作流报告：`/root/clawd/reports/integrated-workflow-report-YYYYMMDD-HHMM.md`
- 运行日志：`/root/clawd/logs/integrated-prompt-workflow.log`

### 🎯 主要优势
- 命令数量：2+ → 1 ✅
- 语义去重：可选 → *强制* ✅
- LLM 评估：可选 → *强制* ✅
- 统一报告：无 → *自动生成* ✅
- Git 提交：手动 → *自动* ✅
- 通知机制：无 → *自动* ✅
- 测试模式：无 → *有* ✅

### 🚀 使用示例

#### 基本使用
```bash
bash /root/clawd/scripts/integrated-prompt-workflow.sh
```

#### 自定义参数
```bash
bash /root/clawd/scripts/integrated-prompt-workflow.sh \
  --query "creative writing" \
  --limit 50 \
  --evaluate-limit 20 \
  --quality-threshold 80
```

#### 测试模式
```bash
bash /root/clawd/scripts/integrated-prompt-workflow.sh --test-mode
```

#### 定时任务
```bash
# 每天早上 9 点运行
0 9 * * * cd /root/clawd && bash scripts/integrated-prompt-workflow.sh >> logs/cron-integrated.log 2>&1
```

### 📝 注意事项
1. 环境变量需要配置（`ANTHROPIC_API_KEY`, `CLAWDHUB_TOKEN` 等）
2. 首次使用建议先运行 `--test-mode` 验证流程
3. 根据需求调整质量阈值
4. 监控日志确保正常运行
5. 人工审查自动生成的 SKILL.md

### 🔗 相关技能
- **x-prompt-hunter**: 原始数据发现技能
- **prompt-to-skill-converter**: 原始转换发布技能
- **skill-creator**: 技能创建框架
- **skill-manager**: 技能管理工具

---

**版本**: v1.0.0
**发布日期**: 2026-02-02
**作者**: Momo (Clawdbot AI)
**许可**: MIT License
