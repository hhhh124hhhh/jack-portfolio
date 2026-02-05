# 信息搜集项目

## 项目概述

这是一个独立的信息搜集项目，整合多种搜索工具和策略，提供智能化的信息搜集解决方案。

## 项目定位

**为什么单独成项目？**

### 教训总结

**1. Skill 不仅仅是提示词**
- ❌ 错误认知：Skill = 提示词
- ✅ 正确理解：Skill = 完整的解决方案
  - 工具 + 脚本 + 配置 + 文档 + 提示词

**2. 光靠提示词转换 skill 还是不够**
- ❌ 错误方式：找到提示词 → 转换 → 发布
- ✅ 正确方式：理解需求 → 设计方案 → 实现工具 → 测试 → 发布

**3. 搜索都是关键词搜索，很有可能没有涵盖所要搜索的内容**
- ❌ 局限性：关键词搜索无法理解语义
- ✅ 改进方向：
  - 语义搜索（向量搜索）
  - 多策略搜索（关键词 + 语义）
  - 迭代搜索（根据结果优化）

## 核心能力

### 1. 多策略搜索

#### 关键词搜索
- SearXNG（隐私保护的元搜索引擎）
- Firecrawl（网页搜索和抓取）
- Twitter Search（社交媒体搜索）

#### 语义搜索（计划中）
- 向量数据库集成
- 语义相似度搜索
- 自然语言查询

#### 迭代搜索（计划中）
- 根据初步结果优化搜索词
- 自动扩展搜索策略
- 多轮搜索和结果合并

### 2. 智能结果处理

#### 内容提取
- readability-lxml（Mozilla Readability 算法）
- trafilatura（备用方案）
- Jina AI Reader（3 层回退）

#### 数据清理
- 去重
- 去噪
- 结构化

#### 质量评估
- 内容完整性
- 信息丰富度
- 来源可靠性

### 3. 工作流集成

#### AI 研究搜索
- 每天早上自动搜索
- 保存到 memory/ai-research/
- 生成分析报告

#### 市场调研
- 竞品分析
- 趋势追踪
- 报告生成

#### 社交媒体分析
- Twitter 搜索和情感分析
- 趋势识别
- 影响者发现

## 项目结构

```
info-search/
├── README.md                    # 项目文档
├── WORKFLOWS.md                  # 工作流文档
├── strategies/                   # 搜索策略
│   ├── keyword-search.sh         # 关键词搜索
│   ├── semantic-search.py        # 语义搜索（计划中）
│   └── iterative-search.py       # 迭代搜索（计划中）
├── processors/                  # 结果处理
│   ├── extract-content.py        # 内容提取
│   ├── clean-data.py            # 数据清理
│   └── evaluate-quality.py      # 质量评估
├── workflows/                   # 工作流
│   ├── ai-research.sh           # AI 研究搜索
│   ├── market-research.sh       # 市场调研
│   └── social-analysis.sh       # 社交媒体分析
└── docs/                        # 文档
    ├── architecture.md          # 架构文档
    └── lessons.md              # 经验总结
```

## 使用方式

### AI 研究搜索

```bash
# 搜索 AI 相关信息
./workflows/ai-research.sh "Claude AI updates"

# 保存结果到 memory/ai-research/
```

### 市场调研

```bash
# 调研竞品
./workflows/market-research.sh "competitor analysis"

# 生成报告
```

### 社交媒体分析

```bash
# 分析 Twitter 趋势
./workflows/social-analysis.sh "#AI trends"

# 生成分析报告
```

## 核心技能集成

### 1. SearXNG Search 🔍
- **用途**：隐私保护的元搜索引擎
- **优势**：不依赖外部 API，支持多搜索引擎

### 2. Firecrawl Search 🔥
- **用途**：网页搜索和抓取 API
- **优势**：3 层回退策略，高成功率

### 3. Twitter Search 🐦
- **用途**：Twitter 社交媒体搜索和数据分析
- **优势**：高级搜索语法，深度分析

## 未来规划

### 短期（1-2 周）
- [ ] 完成基础工作流（AI 研究、市场调研、社交媒体）
- [ ] 整合现有的搜索技能
- [ ] 编写完整文档

### 中期（1-2 月）
- [ ] 实现语义搜索（向量搜索）
- [ ] 实现迭代搜索（多轮优化）
- [ ] 添加更多数据源

### 长期（3-6 月）
- [ ] 建立知识图谱
- [ ] 实现智能推荐
- [ ] 支持自定义工作流

## 经验总结

### 从这个项目中学到的

**1. Skill ≠ 提示词**
- Skill 是完整的解决方案
- 需要工具、脚本、配置、文档
- 提示词只是其中一部分

**2. 搜索的局限性**
- 关键词搜索无法理解语义
- 需要多种搜索策略
- 需要智能的结果处理

**3. 信息搜集的价值**
- 信息搜集本身就是一个独立领域
- 需要专门的工具和方法
- 可以成为有价值的产品

## 相关资源

- SearXNG 官网：https://searxng.org
- Firecrawl 官网：https://firecrawl.dev
- Twitter API：https://twitterapi.io
- Mozilla Readability：https://github.com/mozilla/readability
- Trafilatura：https://github.com/adbar/trafilatura

## 许可证

MIT License

---

*项目创建时间：2026-02-05*
*基于经验总结：Skill 不仅仅是提示词，信息搜集需要专门的解决方案*
