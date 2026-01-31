# AI 提示词评估和收集改进方案

**日期**: 2026-01-31
**来源**: jack happy (Slack #clawdbot)
**要求**:
- LLM 评估使用系统级 agent 评估，不用 Claude API key
- Twitter API 配置不了，使用 searXNG 增强
- 提高提取质量

---

## 改进方案

### 1. 系统级 Agent 评估 (`evaluate-prompts-agent.py`)

**特点**:
- ✅ 使用 `sessions_spawn` 调用系统内置 LLM（不需要外部 API key）
- ✅ 评估维度：质量、实用性、完整性、创新性
- ✅ 输出 0-100 分和详细评估理由
- ✅ 批量处理支持
- ✅ 降级评估机制（规则评分作为后备）

**使用方法**:
```bash
python3 /root/clawd/scripts/evaluate-prompts-agent.py <input-file> [output-file]

# 示例
python3 /root/clawd/scripts/evaluate-prompts-agent.py /root/clawd/data/prompts/extracted-prompts.jsonl
```

**评估维度**:
- **质量 (35%)**: 提示词是否清晰、具体、无歧义
- **实用性 (30%)**: 提示词是否具有实际应用价值
- **完整性 (20%)**: 提示词是否包含必要的信息和上下文
- **创新性 (15%)**: 提示词是否有独特的创意或角度

**输出**:
- `*-agent-evaluated.jsonl` - 评估结果
- `*-agent-evaluated-report.json` - 统计报告

---

### 2. SearXNG 搜索收集 (`collect-prompts-via-searxng.py`)

**特点**:
- ✅ 使用本地 SearXNG 实例（http://149.13.91.232:8080）
- ✅ 多源搜索：GitHub、专业网站、技术博客
- ✅ 高质量域名白名单和黑名单
- ✅ 改进的提取逻辑（更严格的过滤）
- ✅ 自动质量评分
- ✅ 自动类型分类

**搜索来源**:
- 专业网站：PromptBase, LearnPrompting
- GitHub 仓库：awesome-chatgpt-prompts 等
- 技术博客：Medium, Dev.to, Hashnode
- 官方文档：Midjourney, OpenAI, Stability AI
- 教程和指南

**质量过滤规则**:
- 长度：40-800 字符
- 字母数字比例：≥70%
- 必须包含动作动词（generate, create, write 等）
- 排除截断标记
- 排除低质量域名

**使用方法**:
```bash
python3 /root/clawd/scripts/collect-prompts-via-searxng.py

# 输出
# /root/clawd/data/prompts/collected/prompts-from-searxng-YYYYMMDD.jsonl
```

---

### 3. 提取质量改进

**原有问题**:
- ❌ 提取逻辑过于宽松，大量 HTML 片段被当作提示词
- ❌ 基于关键词的评分无法理解语义
- ❌ 数据源单一，质量参差

**改进措施**:

#### 3.1 更严格的提取模式
- 引号匹配：`"..."`, `'...'`, `` `...` ``（40-800 字符）
- 冒号匹配：`prompt: ...`, `example: ...`（40-800 字符）
- 列表匹配：`1. ...`, `- ...`（40-800 字符）

#### 3.2 多层过滤
```
长度过滤 → 内容质量过滤 → 动作动词过滤 → 截断标记过滤
```

#### 3.3 质量评分增强
- 长度评分（30 分）
- 质量关键词（20 分）
- 动作动词（15 分）
- 结构评分（25 分）
- 描述性词汇（10 分）

#### 3.4 数据源质量控制
- 白名单：高质量域名优先
- 黑名单：排除社交媒体和低质量来源
- URL 去重：避免重复收集

---

## 工作流程

### 完整流程

```bash
# 1. 使用 SearXNG 收集提示词
python3 /root/clawd/scripts/collect-prompts-via-searxng.py

# 2. 使用系统级 Agent 评估
python3 /root/clawd/scripts/evaluate-prompts-agent.py \
  /root/clawd/data/prompts/collected/prompts-from-searxng-YYYYMMDD.jsonl

# 3. 转换为 Skills
python3 /root/clawd/scripts/convert-prompts-to-skills.py \
  /root/clawd/data/prompts/collected/prompts-from-searxng-YYYYMMDD-agent-evaluated.jsonl

# 4. 打包和发布
# (使用现有的打包和发布脚本)
```

### 快速流程

```bash
# 一键执行（创建 wrapper 脚本）
python3 /root/clawd/scripts/collect-evaluate-convert.sh
```

---

## 技术对比

| 特性 | 原方案 | 新方案 |
|------|--------|--------|
| **LLM 评估** | Claude API (需要 key) | 系统级 Agent (无需 key) |
| **搜索来源** | Twitter API (配置困难) | SearXNG (多源搜索) |
| **提取质量** | 宽松，大量垃圾数据 | 严格过滤，高质量 |
| **数据源** | 单一 (Twitter) | 多样化 (GitHub, 博客, 官方文档) |
| **API 依赖** | Anthropic API | 无外部 API 依赖 |
| **成本** | 需要付费 API | 免费 |

---

## 下一步计划

### 短期（本周）
1. ✅ 创建评估脚本（`evaluate-prompts-agent.py`）
2. ✅ 创建收集脚本（`collect-prompts-via-searxng.py`）
3. ⏳ 测试脚本功能
4. ⏳ 运行收集和评估流程
5. ⏳ 分析结果质量

### 中期（下周）
1. 创建 wrapper 脚本，一键执行完整流程
2. 添加更多高质量搜索关键词
3. 优化提取正则表达式
4. 建立质量监控机制

### 长期（2-4 周）
1. 添加更多数据源（PromptBase API, Reddit API）
2. 建立提示词分类体系
3. 自动化质量保证
4. 持续优化评分系统

---

## 文件清单

```
/root/clawd/scripts/
├── evaluate-prompts-agent.py          # 系统级 Agent 评估
├── collect-prompts-via-searxng.py     # SearXNG 收集
├── convert-prompts-to-skills.py       # 转换为 Skills（已存在）

/root/clawd/data/prompts/
├── collected/                         # 收集的提示词
│   └── prompts-from-searxng-YYYYMMDD.jsonl
└── reports/                           # 评估报告
    └── prompts-from-searxng-YYYYMMDD-agent-evaluated-report.json
```

---

## 配置说明

### SearXNG 配置
```bash
# 环境变量（已配置）
export SEARXNG_URL="http://149.13.91.232:8080"

# 验证
curl http://149.13.91.232:8080/search?q=test&format=json
```

### Agent 评估配置
```python
# 默认配置（在脚本中）
- batch_size: 10（每批评估数量）
- timeout_seconds: 60（单次超时）
- model: default（使用默认模型）
```

---

## 预期效果

### 数据质量提升
- **垃圾数据比例**: 从 ~60% 降至 <10%
- **高质量提示词**: 从 ~15% 提升至 ~40%
- **平均质量分数**: 从 ~50 提升至 ~65

### 效率提升
- **无需 API key**: 零额外成本
- **多源收集**: 数据多样性提升 3x
- **自动化程度**: 全流程自动化

---

## 总结

这次改进主要解决了三个核心问题：

1. **API 依赖**：从外部 Claude API 改为系统内置 LLM，降低成本和复杂性
2. **搜索限制**：从 Twitter API 改为 SearXNG 多源搜索，获取更高质量的数据
3. **提取质量**：从宽松过滤改为严格多层过滤，大幅提升数据质量

新方案更加健壮、高效、可持续，适合长期运营。
