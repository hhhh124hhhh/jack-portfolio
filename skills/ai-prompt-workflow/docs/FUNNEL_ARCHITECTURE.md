# AI 提示词自动化漏斗模型架构文档

## 版本信息

| 项目 | 内容 |
|------|------|
| 文档版本 | 0.1.0 |
| 创建日期 | 2026-02-04 |
| 最后更新 | 2026-02-04 |
| 文档状态 | 框架草案 |
| 作者 | AI Architecture Team |

## 文档目的

本文档描述了 AI 提示词自动化漏斗模型的整体架构设计，旨在构建一个自动化的提示词处理流水线，从原始数据收集到最终技能转换，实现对高质量提示词的自动识别、分类、评估和转换。

本文档面向系统架构师、开发工程师、产品经理和技术决策者，提供架构概览、设计原则、技术选型和实现路径。

---

# 目录

## 第一部分：概述
- [1.1 背景与动机](#11-背景与动机)
- [1.2 核心问题与挑战](#12-核心问题与挑战)
- [1.3 设计目标](#13-设计目标)

## 第二部分：整体架构
- [2.1 系统架构图](#21-系统架构图)
- [2.2 技术栈选型](#22-技术栈选型)
- [2.3 设计原则](#23-设计原则)
- [2.4 数据流设计](#24-数据流设计)

## 第三部分：内容分类体系
- [3.1 Prompt（提示词）](#31-prompt提示词)
- [3.2 Workflow（工作流）](#32-workflow工作流)
- [3.3 Industry Knowledge（行业经验）](#33-industry-knowledge行业经验)
- [3.4 Guide/Best Practice（指南）](#34-guidebest-practice指南)

## 第四部分：漏斗模型详解

### Layer 1: 数据收集层
- [4.1.1 数据源定义](#411-数据源定义)
- [4.1.2 数据采集策略](#412-数据采集策略)
- [4.1.3 数据预处理](#413-数据预处理)
- [4.1.4 数据存储与去重](#414-数据存储与去重)

### Layer 2: 自动分类层
- [4.2.1 分类模型设计](#421-分类模型设计)
- [4.2.2 特征提取](#422-特征提取)
- [4.2.3 分类规则引擎](#423-分类规则引擎)
- [4.2.4 分类结果验证](#424-分类结果验证)

### Layer 3: 分类评分层
- [4.3.1 评分指标体系](#431-评分指标体系)
- [4.3.2 评分算法选择](#432-评分算法选择)
- [4.3.3 多维度评分](#433-多维度评分)
- [4.3.4 评分阈值设计](#434-评分阈值设计)

### Layer 4: 质量筛选层
- [4.4.1 质量标准定义](#441-质量标准定义)
- [4.4.2 筛选规则配置](#442-筛选规则配置)
- [4.4.3 人工审核机制](#443-人工审核机制)
- [4.4.4 筛选结果反馈](#444-筛选结果反馈)

### Layer 5: 内容补充层
- [4.5.1 缺失信息识别](#451-缺失信息识别)
- [4.5.2 内容增强策略](#452-内容增强策略)
- [4.5.3 结构化处理](#453-结构化处理)
- [4.5.4 补充质量评估](#454-补充质量评估)

### Layer 6: Skill 转换层
- [4.6.1 Skill 模板设计](#461-skill-模板设计)
- [4.6.2 转换规则引擎](#462-转换规则引擎)
- [4.6.3 验证与测试](#463-验证与测试)
- [4.6.4 发布与版本管理](#464-发布与版本管理)

## 第五部分：系统集成与部署
- [5.1 系统集成方案](#51-系统集成方案)
- [5.2 部署架构](#52-部署架构)
- [5.3 监控与告警](#53-监控与告警)
- [5.4 扩展性与维护](#54-扩展性与维护)

## 第六部分：附录
- [附录A：术语表](#附录a术语表)
- [附录B：参考资料](#附录b参考资料)
- [附录C：配置示例](#附录c配置示例)
- [附录D：最佳实践](#附录d最佳实践)

---

# 第一部分：概述

## 1.1 背景与动机

[待填充] 描述 AI 提示词自动化系统的背景、市场需求和技术发展趋势。

## 1.2 核心问题与挑战

[待填充] 列出系统需要解决的核心问题和面临的技术挑战。

## 1.3 设计目标

[待填充] 明确系统的设计目标和成功指标。

---

# 第二部分：整体架构

## 2.1 系统架构图

### 2.1.1 漏斗模型总览

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI 提示词自动化漏斗模型                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: 数据收集层 (Data Collection Layer)                      │
│  ├─ 数据源接入 (Web APIs, 文件, 数据库)                            │
│  ├─ 数据采集调度 (定时触发, 实时推送)                              │
│  ├─ 原始数据存储                                                  │
│  └─ 数据预处理与清洗                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: 自动分类层 (Auto Classification Layer)                  │
│  ├─ Prompt/Workflow/Industry/Guide 分类                          │
│  ├─ 特征提取 (NLP, 规则匹配, 模式识别)                             │
│  ├─ 分类模型推理 (ML 模型, 规则引擎)                              │
│  └─ 分类结果存储与索引                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: 分类评分层 (Classification Scoring Layer)              │
│  ├─ 相关性评分                                                    │
│  ├─ 质量评分 (清晰度, 完整性, 实用性)                             │
│  ├─ 创新性评分                                                    │
│  └─ 综合评分计算                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: 质量筛选层 (Quality Filtering Layer)                   │
│  ├─ 评分阈值筛选                                                  │
│  ├─ 重复内容去重                                                  │
│  ├─ 不合规内容过滤                                                │
│  └─ 人工审核队列                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5: 内容补充层 (Content Enhancement Layer)                 │
│  ├─ 元数据提取与补充                                              │
│  ├─ 标签生成 (自动标签, 手动标签)                                 │
│  ├─ 示例添加                                                      │
│  └─ 格式标准化                                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 6: Skill 转换层 (Skill Transformation Layer)             │
│  ├─ Skill 模板匹配                                                │
│  ├─ 参数映射与转换                                                │
│  ├─ Skill 文件生成                                                │
│  └─ 发布到 ClawdHub                                              │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1.2 数据流图

```mermaid
graph LR
    A[数据源] --> B[数据收集层]
    B --> C[自动分类层]
    C --> D[分类评分层]
    D --> E[质量筛选层]
    E --> F[内容补充层]
    F --> G[Skill 转换层]
    G --> H[ClawdHub]

    style A fill:#e1f5e1
    style B fill:#fff4e1
    style C fill:#e1f0ff
    style D fill:#f0e1ff
    style E fill:#ffe1f0
    style F fill:#e1ffff
    style G fill:#ffffe1
    style H fill:#f5f5f5
```

## 2.2 技术栈选型

[待填充] 详细描述各层的技术选型，包括：
- 编程语言与框架
- 数据存储方案
- AI/ML 模型选择
- 任务调度系统
- 消息队列与事件总线
- 部署与容器化方案

## 2.3 设计原则

[待填充] 描述系统的核心设计原则，如：
- 模块化与解耦
- 可扩展性
- 可维护性
- 数据质量优先
- 自动化优先
- 人工审核兜底

## 2.4 数据流设计

[待填充] 详细描述数据在各层之间的流动方式、格式转换、存储策略等。

---

# 第三部分：内容分类体系

## 3.1 Prompt（提示词）

[待填充] 定义 Prompt 类型内容的特征、识别标准、处理流程。

## 3.2 Workflow（工作流）

[待填充] 定义 Workflow 类型内容的特征、识别标准、处理流程。

## 3.3 Industry Knowledge（行业经验）

[待填充] 定义 Industry Knowledge 类型内容的特征、识别标准、处理流程。

## 3.4 Guide/Best Practice（指南）

[待填充] 定义 Guide/Best Practice 类型内容的特征、识别标准、处理流程。

---

# 第四部分：漏斗模型详解

## Layer 1: 数据收集层

### 4.1.1 数据源定义
[待填充]

### 4.1.2 数据采集策略
[待填充]

### 4.1.3 数据预处理
[待填充]

### 4.1.4 数据存储与去重
[待填充]

---

## Layer 2: 自动分类层

### 4.2.1 分类模型设计
[待填充]

### 4.2.2 特征提取
[待填充]

### 4.2.3 分类规则引擎
[待填充]

### 4.2.4 分类结果验证
[待填充]

---

## Layer 3: 分类评分层

### 4.3.1 评分指标体系
[待填充]

### 4.3.2 评分算法选择
[待填充]

### 4.3.3 多维度评分
[待填充]

### 4.3.4 评分阈值设计
[待填充]

---

## Layer 4: 质量筛选层

### 4.4.1 质量标准定义
[待填充]

### 4.4.2 筛选规则配置
[待填充]

### 4.4.3 人工审核机制
[待填充]

### 4.4.4 筛选结果反馈
[待填充]

---

## Layer 5: 内容补充层

### 4.5.1 缺失信息识别
[待填充]

### 4.5.2 内容增强策略
[待填充]

### 4.5.3 结构化处理
[待填充]

### 4.5.4 补充质量评估
[待填充]

---

## Layer 6: Skill 转换层

### 4.6.1 Skill 模板设计
[待填充]

### 4.6.2 转换规则引擎
[待填充]

### 4.6.3 验证与测试
[待填充]

### 4.6.4 发布与版本管理
[待填充]

---

# 第五部分：系统集成与部署

## 5.1 系统集成方案
[待填充]

## 5.2 部署架构
[待填充]

## 5.3 监控与告警
[待填充]

## 5.4 扩展性与维护
[待填充]

---

# 第六部分：附录

## 附录A：术语表

| 术语 | 英文 | 定义 |
|------|------|------|
| 提示词 | Prompt | [待定义] |
| 工作流 | Workflow | [待定义] |
| 技能 | Skill | [待定义] |
| 漏斗模型 | Funnel Model | [待定义] |

## 附录B：参考资料

[待填充] 列出相关的技术文档、论文、博客文章等。

## 附录C：配置示例

[待填充] 提供关键配置文件的示例。

## 附录D：最佳实践

[待填充] 总结开发、部署、运维过程中的最佳实践。

---

**文档结束**

# 第一部分：概述

## 1.1 背景与动机

### 市场背景

随着大语言模型（LLM）的快速发展，AI 提示词工程（Prompt Engineering）已成为 AI 应用的核心技能之一。优质的提示词能够显著提升 AI 模型的输出质量，提高工作效率。

**当前市场现状**：
- GitHub 上有数千个提示词相关仓库（如 awesome-chatgpt-prompts）
- Twitter/X 上每天有数万条关于 AI 提示词的讨论
- Reddit 社区（r/ChatGPT, r/ChatGPTcoding）积累了大量用户贡献的提示词
- 各种 AI 工具平台开始集成提示词库功能

**用户需求**：
- 开发者需要快速找到高质量提示词
- 企业需要将内部经验标准化为可复用的技能
- 个人希望收集和管理自己的提示词资产
- 市场需要将优质提示词变现的渠道

### Clawdbot 技能生态

Clawdbot 是一个开放式的 AI 助手平台，支持第三方开发者贡献技能（Skills）。用户可以通过 ClawdHub 发现、安装和使用各种技能。

**当前痛点**：
1. **高质量提示词稀缺**：ClawdHub 上的技能数量有限，需要持续补充
2. **自动化程度低**：手动收集、评估、转换提示词的效率低下
3. **质量参差不齐**：缺乏统一的评估标准和筛选机制
4. **类型单一**：仅关注"提示词"，忽略了工作流、行业经验、指南等有价值的内容

### 商业机会

通过自动化流程，将互联网上的优质内容（提示词、工作流、行业经验、指南）转换为 Clawdbot 技能，并在 ClawdHub 上发布，形成：

- **内容资产化**：将分散的互联网内容转化为可复用的技能资产
- **规模化生产**：自动化流程支持批量处理，降低人力成本
- **商业化变现**：通过 ClawdHub 平台实现技能分发和收益

---

## 1.2 核心问题与挑战

### 问题 1：内容识别困难

**现象**：
- 收集了 362 个"提示词"样本
- 经过评估，其中 90% 不是真正的"提示词"
- 实际包括：提示词指南、工作流程、行业经验、方法论等

**影响**：
- 使用统一的评分标准（为提示词设计）导致评分偏低
- 平均质量得分仅 29.5/100
- 0 个样本达到高质量阈值（≥70）

### 问题 2：评分标准不适用

**当前评分维度**（4 维度，满分 40 分）：
- 创新性（Creativity）：25%
- 实用性（Practicality）：25%
- 清晰度（Clarity）：25%
- 可复用性（Reusability）：25%

**问题**：
- 这个评分标准是为"提示词"设计的
- 对"工作流"、"行业经验"、"指南"不适用
- 例如：工作流的"创新性"不重要，"完整性"更重要

### 问题 3：质量阈值设置不当

**原设置**：
- 质量阈值：70 分（满分 100）
- 目标：只发布高质量技能

**实际情况**：
- 362 个样本中，0 个达到 70 分
- 最高分仅 69 分
- 平均分 29.5 分

**调整**：
- 质量阈值降低到 50 分
- 可以转换 11 个样本（3%）
- 更符合当前数据质量分布

### 问题 4：内容不完整

**现象**：
- 很多收集的内容是"残缺"的
- 缺少必要信息：使用场景、示例代码、参数说明
- 无法直接转换为可用的 Skill

**解决方案**：
- 通过联网搜索补充资料
- 通过工具调用验证和增强
- 人工审核兜底

### 问题 5：技术实现挑战

**大任务处理**：
- 生成完整的架构文档（预计 5000+ 行）
- 子代理因上下文溢出失败
- 需要分步执行或手动生成

**系统限制**：
- OpenClaw 会话启动时自动加载记忆（90k tokens）
- 可用上下文仅 41k tokens
- 大任务容易导致上下文溢出

---

## 1.3 设计目标

### 核心目标

**目标 1：构建自动化的内容处理流水线**

从原始数据收集到最终技能转换，实现端到端的自动化：

```
数据源收集 → 自动分类 → 分类评分 → 质量筛选 → 内容补充 → 技能转换 → 发布
```

**目标 2：提高内容质量和转化率**

- 区分 4 种内容类型：Prompt、Workflow、Industry Knowledge、Guide
- 针对每种类型使用不同的评分标准
- 通过内容补充层提升内容完整性
- 目标转化率：从 0% → 10%+

**目标 3：规模化生产技能**

- 支持多数据源接入（GitHub, Reddit, Twitter, Hacker News, SearXNG）
- 每日增量收集和处理
- 自动发布到 ClawdHub
- 目标产能：每天发布 10+ 个高质量技能

**目标 4：建立质量控制体系**

- 多维度评分机制
- 阈值筛选 + 人工审核
- 质量指标监控和反馈
- 持续优化评分标准

### 技术目标

**目标 1：模块化架构**

- 6 层漏斗模型，每层职责清晰
- 层与层之间松耦合
- 支持独立扩展和替换

**目标 2：可扩展性**

- 支持新增数据源（插件化）
- 支持新增内容类型
- 支持新增评分维度
- 支持新增技能模板

**目标 3：可维护性**

- 清晰的代码结构
- 完善的文档和注释
- 统一的日志和监控
- 易于调试和故障排查

**目标 4：可观测性**

- 每层的输入输出可追踪
- 性能指标可监控（延迟、成功率、转化率）
- 错误和异常可告警
- 支持回滚和回溯

### 业务目标

**目标 1：建立内容资产库**

- 收集和整理优质内容
- 建立分类和标签体系
- 形成可复用的内容资产

**目标 2：丰富 ClawdHub 技能生态**

- 提供更多高质量技能
- 覆盖更多领域和场景
- 吸引更多用户和开发者

**目标 3：实现商业化变现**

- 通过 ClawdHub 平台分发技能
- 探索收费模式和订阅模式
- 建立收益分成机制

**目标 4：形成竞争优势**

- 独特的自动化流程
- 高质量的内容来源
- 持续更新的内容库
- 难以复制的核心能力

---

## 成功指标

### 量化指标

| 指标 | 当前值 | 目标值 | 测量周期 |
|------|--------|--------|----------|
| 每日收集内容数 | 362 | 500+ | 每天 |
| 内容转化率 | 0% → 3% | 10%+ | 每周 |
| 每日发布技能数 | 0 | 10+ | 每天 |
| 平均质量得分 | 29.5 | 50+ | 每周 |
| 高质量技能占比（≥70） | 0% | 20% | 每月 |
| 技能下载/使用数 | 0 | 1000+ | 每月 |
| 技能评分 | N/A | 4.0+ | 每月 |

### 质量指标

- **分类准确率**：自动分类的准确率 ≥ 85%
- **评分一致性**：人工评分与自动评分的相关性 ≥ 0.8
- **内容完整性**：发布的内容 100% 包含必要信息
- **用户满意度**：技能评分 ≥ 4.0/5.0

---

**第一部分：概述 - 完成时间：2026-02-04 23:20**

# 第三部分：内容分类体系

## 概述

经过对收集的 362 个样本进行分析，我们发现 90% 的内容不是传统意义上的"提示词"（单个可直接使用的指令），而是：

1. **提示词指南/教程**：教用户如何编写提示词
2. **工作流程**：多步骤的执行流程，需要联网、工具调用
3. **行业经验**：特定领域的专业知识和最佳实践
4. **方法论/框架**：理论框架和系统性指南

因此，我们需要建立**4 种内容分类体系**，针对每种类型设计不同的评分标准和处理流程。

---

## 3.1 Prompt（提示词）

### 定义

**Prompt**：可直接用于 AI 模型的单个或一组指令，能够独立完成任务或解决问题。

### 特征识别

**文本特征**：
- 包含明确的指令（如"请..."、"你是一个..."、"生成..."）
- 长度通常在 50-500 字之间
- 结构简洁，没有过多的解释性文字
- 包含角色设定（role）+ 任务（task）+ 输出格式（output format）

**示例特征**：
```
你是一位资深的产品经理。请分析以下用户需求，输出产品需求文档（PRD），
包括：需求背景、功能列表、验收标准、优先级排序。
```

### 识别标准

**判定为 Prompt 的条件**（满足 3 条及以上）：
- [ ] 包含明确的任务指令
- [ ] 包含角色设定
- [ ] 长度在 50-500 字之间
- [ ] 没有解释性文字（如"这是一个..."、"首先..."）
- [ ] 可以独立执行，不需要额外上下文

### 处理流程

```
原始内容 → 特征提取 → 判断是否为 Prompt → 是 → 评分 → 转换
                                    ↓
                                   否 → 重新分类
```

### 评分标准（满分 100）

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 实用性 | 50% | 是否能解决实际问题？是否常用？ |
| 清晰度 | 30% | 指令是否明确？是否有歧义？ |
| 独特性 | 20% | 是否有创新？是否与其他提示词重复？ |

**评分示例**：
- 实用性（50 分）：
  - 高（40-50）：解决常见问题，可复用性强
  - 中（30-39）：解决特定问题，有一定使用场景
  - 低（<30）：过于小众或无实际意义
- 清晰度（30 分）：
  - 高（24-30）：指令明确，无歧义
  - 中（18-23）：基本清晰，部分模糊
  - 低（<18）：指令模糊，难以理解
- 独特性（20 分）：
  - 高（16-20）：创新性强，独特
  - 中（12-15）：有一定特色，但不独特
  - 低（<12）：与常见提示词重复

---

## 3.2 Workflow（工作流）

### 定义

**Workflow**：多步骤的执行流程，通常需要联网、工具调用、或多个 AI 交互。

### 特征识别

**文本特征**：
- 包含步骤说明（如"第一步..."、"然后..."、"最后..."）
- 包含条件判断（如"如果...则..."）
- 可能包含伪代码、代码片段
- 长度通常在 200-2000 字之间
- 需要多个工具或服务配合

**示例特征**：
```
1. 使用搜索引擎找到相关论文
2. 使用 AI 总结论文内容
3. 提取关键观点和结论
4. 生成摘要报告
5. 可选：发送到邮箱或 Slack
```

### 识别标准

**判定为 Workflow 的条件**（满足 3 条及以上）：
- [ ] 包含明确的步骤说明
- [ ] 需要 2+ 个步骤
- [ ] 需要联网或工具调用
- [ ] 包含条件判断或分支
- [ ] 长度在 200-2000 字之间

### 处理流程

```
原始内容 → 特征提取 → 判断是否为 Workflow → 是 → 评分 → 内容补充 → 转换
                                        ↓
                                       否 → 重新分类
```

**内容补充**：
- 补充每一步的具体操作方法
- 补充工具和 API 的使用说明
- 补充错误处理和重试机制
- 补充示例代码

### 评分标准（满分 100）

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 完整性 | 30% | 流程是否完整？是否有遗漏的步骤？ |
| 可扩展性 | 20% | 是否可以扩展？是否可以修改？ |
| 实用性 | 30% | 是否能解决实际问题？是否常用？ |
| 可复用性 | 20% | 是否可以重复使用？是否可移植？ |

**评分示例**：
- 完整性（30 分）：
  - 高（24-30）：流程完整，每一步都有清晰说明
  - 中（18-23）：基本完整，部分步骤模糊
  - 低（<18）：流程不完整，缺少关键步骤
- 可扩展性（20 分）：
  - 高（16-20）：容易扩展和修改
  - 中（12-15）：可以扩展，但有一定限制
  - 低（<12）：难以扩展或修改
- 实用性（30 分）：
  - 高（24-30）：解决实际问题，使用场景多
  - 中（18-23）：有一定实用性，但场景有限
  - 低（<18）：实用性低，难以落地
- 可复用性（20 分）：
  - 高（16-20）：可以重复使用，可移植
  - 中（12-15）：可以复用，但需要调整
  - 低（<12）：难以复用或移植

---

## 3.3 Industry Knowledge（行业经验）

### 定义

**Industry Knowledge**：特定领域的专业知识、经验总结、最佳实践。

### 特征识别

**文本特征**：
- 包含特定领域的专业术语
- 包含经验总结或教训
- 包含最佳实践或反模式
- 长度通常在 300-3000 字之间
- 内容系统性较强

**示例特征**：
```
作为一名资深前端工程师，我总结了以下 10 条性能优化经验：

1. 使用代码分割（Code Splitting）
   - 按路由分割
   - 按功能分割
   - 使用 React.lazy 和 Suspense

2. 优化图片加载
   - 使用 WebP 格式
   - 实现懒加载
   - 使用 CDN

...
```

### 识别标准

**判定为 Industry Knowledge 的条件**（满足 3 条及以上）：
- [ ] 包含特定领域的专业术语
- [ ] 包含经验总结或最佳实践
- [ ] 内容系统性较强（有结构）
- [ ] 长度在 300-3000 字之间
- [ ] 包含多个知识点

### 处理流程

```
原始内容 → 特征提取 → 判断是否为 Industry Knowledge → 是 → 评分 → 内容补充 → 转换
                                                 ↓
                                                否 → 重新分类
```

**内容补充**：
- 补充背景知识和上下文
- 补充代码示例或案例
- 补充参考资料和链接
- 补充常见问题和解答

### 评分标准（满分 100）

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 专业深度 | 40% | 是否有深度？是否专业？是否有独特见解？ |
| 实用性 | 40% | 是否能解决实际问题？是否有可操作性？ |
| 系统性 | 20% | 是否有结构？是否完整？是否成体系？ |

**评分示例**：
- 专业深度（40 分）：
  - 高（32-40）：有深度，专业，有独特见解
  - 中（24-31）：有一定深度，但不深入
  - 低（<24）：浅显，缺乏深度
- 实用性（40 分）：
  - 高（32-40）：能解决实际问题，可操作性强
  - 中（24-31）：有一定实用性，但操作困难
  - 低（<24）：实用性低，难以落地
- 系统性（20 分）：
  - 高（16-20）：有结构，完整，成体系
  - 中（12-15）：有一定结构，但不完整
  - 低（<12）：结构混乱，不成体系

---

## 3.4 Guide/Best Practice（指南）

### 定义

**Guide/Best Practice**：理论框架、方法论、系统性指南。

### 特征识别

**文本特征**：
- 包含理论或框架
- 包含方法论或原则
- 包含系统性指导
- 长度通常在 500-5000 字之间
- 内容抽象性较强

**示例特征**：
```
如何设计一个高质量的产品需求文档（PRD）？

一、PRD 的核心要素
1. 需求背景
2. 目标用户
3. 功能列表
4. 优先级排序
5. 验收标准

二、编写原则
1. 清晰明确
2. 可量化
3. 可测试
4. 可追溯
...
```

### 识别标准

**判定为 Guide 的条件**（满足 3 条及以上）：
- [ ] 包含理论或框架
- [ ] 包含方法论或原则
- [ ] 包含系统性指导
- [ ] 长度在 500-5000 字之间
- [ ] 内容抽象性较强

### 处理流程

```
原始内容 → 特征提取 → 判断是否为 Guide → 是 → 评分 → 内容补充 → 转换
                                     ↓
                                    否 → 重新分类
```

**内容补充**：
- 补充理论依据
- 补充实践案例
- 补充工具和模板
- 补充常见问题和解答

### 评分标准（满分 100）

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 指导性 | 40% | 是否有指导价值？是否可操作？ |
| 结构性 | 30% | 结构是否清晰？是否逻辑严密？ |
| 实用性 | 30% | 是否能解决实际问题？是否有可操作性？ |

**评分示例**：
- 指导性（40 分）：
  - 高（32-40）：有很强的指导价值，可操作
  - 中（24-31）：有一定指导价值，但操作困难
  - 低（<24）：指导价值低，难以操作
- 结构性（30 分）：
  - 高（24-30）：结构清晰，逻辑严密
  - 中（18-23）：结构基本清晰，逻辑一般
  - 低（<18）：结构混乱，逻辑不清
- 实用性（30 分）：
  - 高（24-30）：能解决实际问题，可操作性强
  - 中（18-23）：有一定实用性，但操作困难
  - 低（<18）：实用性低，难以落地

---

## 3.5 分类边界处理

### 混合类型的内容

**问题**：很多内容同时符合多种类型。

**处理策略**：
1. **优先级排序**：Prompt > Workflow > Industry Knowledge > Guide
2. **主要特征判断**：根据内容的主体特征判断
3. **多标签**：允许内容有多个标签（主要标签 + 次要标签）

**示例**：
- 内容："如何编写高质量的提示词（包含 10 个技巧和 3 个示例）"
  - 主要特征：Guide（方法论）
  - 次要特征：Prompt（包含示例）
  - 分类：Guide（主要） + Prompt（次要）

### 不确定的内容

**问题**：有些内容难以明确分类。

**处理策略**：
1. **低置信度标记**：置信度 < 0.7，标记为"不确定"
2. **人工审核**：不确定的内容进入人工审核队列
3. **反馈学习**：人工审核结果用于优化分类模型

---

## 3.6 分类准确率提升

### 多数投票

**方法**：使用多个模型或多次分类，取多数结果。

**实现**：
```
results = []
for i in range(3):
    result = classify(content)
    results.append(result)

final_result = majority_vote(results)
```

**优点**：减少单次分类的随机误差

### 人工审核反馈循环

**流程**：
1. 自动分类
2. 人工审核（抽样或低置信度）
3. 记录人工分类结果
4. 训练分类模型
5. 持续优化

### 持续学习

**方法**：
- 定期（每周）收集人工审核结果
- 更新分类模型
- 调整分类规则
- 监控分类准确率

---

**第三部分：内容分类体系 - 完成时间：2026-02-04 23:25**

# 第四部分：漏斗模型详解

---

## Layer 1: 数据收集层

### 概述

数据收集层是漏斗模型的第一层，负责从多个数据源收集原始内容，并进行初步的预处理和去重。

### 核心目标

1. **多源数据采集**：支持多种数据源（GitHub, Reddit, Twitter, Hacker News, SearXNG）
2. **增量采集**：每日定时采集，避免重复
3. **数据清洗**：去除低质量、无关、重复内容
4. **标准化存储**：统一数据格式，便于后续处理

---

## 4.1.1 数据源定义

### 数据源清单

#### 1. GitHub（优先级：高）

**采集范围**：
- 优质提示词仓库（如 awesome-chatgpt-prompts）
- AI 工具仓库的 README 和文档
- 开源项目的提示词示例

**采集频率**：每日一次

**采集策略**：
- 监控仓库更新（Star 数 > 100）
- 使用 GitHub API 获取最新内容
- 重点关注 README、docs/ 目录

**数据格式**：
```json
{
  "id": "github_001",
  "title": "awesome-chatgpt-prompts",
  "content": "内容...",
  "type": "auto-detect",
  "source": "github",
  "url": "https://github.com/f/awesome-chatgpt-prompts",
  "metadata": {
    "repo": "f/awesome-chatgpt-prompts",
    "star_count": 123456,
    "updated_at": "2026-02-04T00:00:00Z"
  },
  "collected_at": "2026-02-04T00:00:00Z"
}
```

#### 2. Reddit（优先级：高）

**采集范围**：
- r/ChatGPT（提示词分享）
- r/ChatGPTcoding（编程提示词）
- r/OpenAI（AI 相关讨论）
- r/MachineLearning（机器学习讨论）

**采集频率**：每 6 小时一次

**采集策略**：
- 使用 Reddit API 获取热门帖子
- 筛选高赞帖子（> 50 upvotes）
- 提取评论中的有价值内容

**数据格式**：
```json
{
  "id": "reddit_001",
  "title": "I created a prompt for generating marketing copy",
  "content": "内容...",
  "type": "auto-detect",
  "source": "reddit",
  "url": "https://reddit.com/r/ChatGPT/comments/...",
  "metadata": {
    "subreddit": "ChatGPT",
    "author": "username",
    "upvotes": 123,
    "comments_count": 45
  },
  "collected_at": "2026-02-04T00:00:00Z"
}
```

#### 3. Twitter/X（优先级：中）

**采集范围**：
- AI 提示词相关话题（#ChatGPT, #promptengineering）
- 知名 AI 专家的推文
- 实时热点讨论

**采集频率**：每 2 小时一次

**采集策略**：
- 使用 Twitter API 搜索
- 筛选高互动推文（> 100 likes）
- 提取推文内容和附件

**数据格式**：
```json
{
  "id": "twitter_001",
  "title": "New prompt for code review",
  "content": "内容...",
  "type": "auto-detect",
  "source": "twitter",
  "url": "https://twitter.com/username/status/...",
  "metadata": {
    "author": "username",
    "likes": 456,
    "retweets": 78,
    "replies": 23
  },
  "collected_at": "2026-02-04T00:00:00Z"
}
```

#### 4. Hacker News（优先级：中）

**采集范围**：
- AI 相关热门讨论
- 技术博客文章
- 开源项目推荐

**采集频率**：每 12 小时一次

**采集策略**：
- 使用 Hacker News API 获取热门帖子
- 筛选 AI 相关话题（关键词匹配）
- 提取文章内容和评论

**数据格式**：
```json
{
  "id": "hn_001",
  "title": "The Art of Prompt Engineering",
  "content": "内容...",
  "type": "auto-detect",
  "source": "hackernews",
  "url": "https://news.ycombinator.com/item?id=...",
  "metadata": {
    "author": "username",
    "points": 234,
    "comments_count": 123
  },
  "collected_at": "2026-02-04T00:00:00Z"
}
```

#### 5. SearXNG（优先级：高）

**采集范围**：
- AI 提示词博客文章
- 技术教程和指南
- 行业报告和案例

**采集频率**：每日一次

**采集策略**：
- 使用 SearXNG 搜索 AI 提示词相关关键词
- 筛选高质量来源（官方博客、知名技术网站）
- 使用 web_fetch 提取文章内容

**关键词列表**：
- "ChatGPT prompt"
- "prompt engineering"
- "AI prompt template"
- "prompt best practices"
- "prompt framework"

**数据格式**：
```json
{
  "id": "searxng_001",
  "title": "A Complete Guide to Prompt Engineering",
  "content": "内容...",
  "type": "auto-detect",
  "source": "searxng",
  "url": "https://example.com/blog/prompt-engineering",
  "metadata": {
    "search_query": "prompt engineering",
    "domain": "example.com",
    "fetch_date": "2026-02-04T00:00:00Z"
  },
  "collected_at": "2026-02-04T00:00:00Z"
}
```

#### 6. HuggingFace（优先级：低）

**采集范围**：
- 提示词数据集
- Prompt template 库

**采集频率**：每周一次

**采集策略**：
- 监控 HuggingFace Dataset Hub
- 筛选提示词相关数据集
- 下载数据集内容

**数据格式**：
```json
{
  "id": "hf_001",
  "title": "ChatGPT Prompt Dataset",
  "content": "内容...",
  "type": "auto-detect",
  "source": "huggingface",
  "url": "https://huggingface.co/datasets/...",
  "metadata": {
    "dataset": "username/prompt-dataset",
    "downloads": 12345,
    "likes": 678
  },
  "collected_at": "2026-02-04T00:00:00Z"
}
```

---

## 4.1.2 数据采集策略

### 采集调度

**定时任务（Cron）**：

```yaml
# GitHub 每日采集
- name: github-collect
  schedule: "0 2 * * *"  # 每天凌晨 2 点
  source: github
  
# Reddit 每 6 小时采集
- name: reddit-collect
  schedule: "0 */6 * * *"  # 每 6 小时
  source: reddit
  
# Twitter 每 2 小时采集
- name: twitter-collect
  schedule: "0 */2 * * *"  # 每 2 小时
  source: twitter
  
# Hacker News 每 12 小时采集
- name: hn-collect
  schedule: "0 */12 * * *"  # 每 12 小时
  source: hackernews
  
# SearXNG 每日采集
- name: searxng-collect
  schedule: "0 3 * * *"  # 每天凌晨 3 点
  source: searxng
  
# HuggingFace 每周采集
- name: hf-collect
  schedule: "0 4 * * 0"  # 每周日凌晨 4 点
  source: huggingface
```

### 增量采集

**策略**：只采集新内容，避免重复

**实现**：
```python
# 记录上次采集时间
last_collect_time = load_last_collect_time(source)

# 采集新内容
new_items = collect(source, since=last_collect_time)

# 更新采集时间
update_last_collect_time(source, current_time)
```

### 失败重试

**重试策略**：
- 指数退避（Exponential Backoff）
- 最多重试 3 次
- 重试间隔：30s, 60s, 120s

**实现**：
```python
def collect_with_retry(source, max_retries=3):
    for attempt in range(max_retries):
        try:
            return collect(source)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 30 * (2 ** attempt)  # 30s, 60s, 120s
            sleep(wait_time)
```

---

## 4.1.3 数据预处理

### 格式验证

**必填字段检查**：
```python
required_fields = ["id", "title", "content", "type", "source"]

def validate_data(data):
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    return True, None
```

### 内容清洗

**去除低质量内容**：
- 过滤太短的内容（< 50 字）
- 过滤纯英文或纯中文（除非特定场景）
- 过滤纯代码（除非有说明）
- 过滤纯链接（无实际内容）

**实现**：
```python
def clean_content(data):
    content = data["content"]
    
    # 过滤太短
    if len(content) < 50:
        return False, "Content too short"
    
    # 过滤纯链接
    if re.match(r'^https?://\S+$', content.strip()):
        return False, "Content is just a URL"
    
    # 去除多余空白
    content = re.sub(r'\s+', ' ', content.strip())
    data["content"] = content
    
    return True, None
```

### 内容提取

**HTML 内容提取**：
- 使用 web_fetch 提取文章正文
- 去除广告、导航、页脚等无关内容
- 保留标题、正文、代码块

**Markdown 格式化**：
- 将 HTML 转换为 Markdown
- 保留代码块和表格
- 清理格式混乱的部分

---

## 4.1.4 数据存储与去重

### 数据存储格式

**文件格式**：JSONL（每行一个 JSON 对象）

**文件结构**：
```
/root/clawd/data/prompts/
├── collected/
│   ├── prompts-2026-02-01.jsonl
│   ├── prompts-2026-02-02.jsonl
│   └── prompts-2026-02-03.jsonl
└── processed/
    ├── prompts-processed-2026-02-01.jsonl
    └── prompts-processed-2026-02-02.jsonl
```

### 去重策略

#### 1. MD5 去重（精确去重）

**方法**：计算内容的 MD5 哈希值，相同哈希值视为重复

**实现**：
```python
import hashlib

def compute_md5(content):
    return hashlib.md5(content.encode()).hexdigest()

# 去重
seen_md5 = set()
unique_items = []
for item in items:
    md5 = compute_md5(item["content"])
    if md5 not in seen_md5:
        seen_md5.add(md5)
        unique_items.append(item)
```

#### 2. 语义去重（模糊去重）

**方法**：使用嵌入模型（Embedding）计算语义相似度

**实现**：
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_embedding(content):
    return model.encode(content)

def semantic_deduplicate(items, threshold=0.95):
    embeddings = [compute_embedding(item["content"]) for item in items]
    
    unique_items = []
    seen_embeddings = []
    
    for item, embedding in zip(items, embeddings):
        if not seen_embeddings:
            unique_items.append(item)
            seen_embeddings.append(embedding)
        else:
            similarities = cosine_similarity(
                [embedding],
                seen_embeddings
            )[0]
            max_similarity = max(similarities)
            
            if max_similarity < threshold:
                unique_items.append(item)
                seen_embeddings.append(embedding)
    
    return unique_items
```

### 去重统计

**记录去重结果**：
```json
{
  "date": "2026-02-04",
  "total_collected": 500,
  "md5_duplicates": 50,
  "semantic_duplicates": 30,
  "unique_items": 420,
  "deduplication_rate": "16%"
}
```

---

## Layer 1 技术实现

### 技术栈

- **Python**：主要编程语言
- **Requests**：HTTP 请求
- **BeautifulSoup**：HTML 解析
- **Sentence-Transformers**：语义去重
- **APScheduler**：定时任务调度
- **JSON**：数据存储格式

### 核心脚本

**主脚本**：`/root/clawd/scripts/collect-prompts.py`

**功能**：
- 调度各数据源的采集任务
- 协调去重和存储
- 生成采集报告

**使用方法**：
```bash
# 手动采集
python3 /root/clawd/scripts/collect-prompts.py

# 测试模式
python3 /root/clawd/scripts/collect-prompts.py --test-mode

# 指定数据源
python3 /root/clawd/scripts/collect-prompts.py --source github
```

### 配置文件

**配置文件**：`/root/clawd/config/prompts-collector.yaml`

**示例**：
```yaml
data_sources:
  github:
    enabled: true
    frequency: daily
    repos:
      - f/awesome-chatgpt-prompts
      - dair-ai/Prompt-Engineering-Guide
      
  reddit:
    enabled: true
    frequency: "6h"
    subreddits:
      - ChatGPT
      - ChatGPTcoding
      - OpenAI
      
  twitter:
    enabled: true
    frequency: "2h"
    keywords:
      - "#ChatGPT"
      - "#promptengineering"
      
  searxng:
    enabled: true
    frequency: daily
    keywords:
      - "ChatGPT prompt"
      - "prompt engineering"
      
deduplication:
  md5_enabled: true
  semantic_enabled: true
  semantic_threshold: 0.95
  embedding_model: all-MiniLM-L6-v2

storage:
  data_dir: /root/clawd/data/prompts/collected
  file_format: jsonl
  max_file_size: 100MB
```

---

## Layer 1 监控指标

| 指标 | 定义 | 目标值 | 测量周期 |
|------|------|--------|----------|
| 每日采集数量 | 每天采集的内容总数 | 500+ | 每天 |
| 去重率 | 去重的内容比例 | < 20% | 每周 |
| 采集成功率 | 采集任务的成功率 | ≥ 95% | 每天 |
| 数据质量通过率 | 通过预处理的内容比例 | ≥ 80% | 每周 |
| 增量采集比例 | 新内容占比（非重复） | ≥ 70% | 每周 |

---

## Layer 1 错误处理

### 错误分类

| 错误类型 | 描述 | 处理策略 |
|---------|------|----------|
| 网络错误 | API 连接失败、超时 | 重试 3 次，记录日志 |
| API 错误 | API 返回错误（401, 429, 500） | 根据错误码处理，延迟重试 |
| 数据错误 | 数据格式错误、缺失字段 | 标记为无效，记录日志 |
| 解析错误 | HTML 解析失败 | 跳过该条目，记录日志 |

### 错误记录

**错误日志**：`/root/clawd/logs/collect-prompts-errors.log`

**格式**：
```
2026-02-04T00:00:00Z ERROR [github] API rate limit exceeded, retrying in 60s
2026-02-04T00:01:00Z ERROR [reddit] Failed to parse post: reddit_123, missing field 'content'
2026-02-04T00:02:00Z WARNING [twitter] Low quality content filtered: twitter_456, length: 30
```

---

**Layer 1: 数据收集层 - 完成时间：2026-02-04 23:30**

# Layer 2: 自动分类层

### 概述

自动分类层是漏斗模型的第二层，负责将收集的内容自动分类为 4 种类型：Prompt、Workflow、Industry Knowledge、Guide。

### 核心目标

1. **高准确率**：分类准确率 ≥ 85%
2. **高置信度**：置信度 ≥ 0.7 的占比 ≥ 80%
3. **可解释性**：提供分类理由，便于人工审核
4. **持续优化**：通过人工反馈不断优化模型

---

## 4.2.1 分类模型设计

### 模型选择

**主要模型**：Claude 3.5 Sonnet（通过 API）

**理由**：
- 理解能力强，适合分类任务
- 支持多轮对话，便于解释分类理由
- API 稳定，响应速度快

**备选模型**：
- GPT-4：理解能力强，但成本高
- Sentence-Transformers：速度快，但准确率较低
- BERT：平衡速度和准确率，但需要训练

### 分类架构

```
原始内容 → 特征提取 → LLM 分类 → 置信度计算 → 结果输出
             ↓                                            ↓
         规则匹配                                     规则验证
```

**流程说明**：
1. **特征提取**：提取文本特征（长度、结构、关键词）
2. **规则匹配**：使用规则引擎快速分类
3. **LLM 分类**：使用 Claude API 进行深度分类
4. **置信度计算**：计算分类的置信度
5. **规则验证**：验证分类结果是否符合规则

---

## 4.2.2 特征提取

### 文本特征

**长度特征**：
```python
features = {
    "content_length": len(content),
    "word_count": len(content.split()),
    "sentence_count": len(re.split(r'[.!?]+', content)),
    "paragraph_count": len(content.split('\n\n'))
}
```

**结构特征**：
```python
features.update({
    "has_steps": bool(re.search(r'(第一|第二步|step 1|1\.)', content)),
    "has_code": bool(re.search(r'```', content)),
    "has_bullets": bool(re.search(r'^\s*[-*]', content, re.MULTILINE)),
    "has_numbers": bool(re.search(r'\d+\.', content))
})
```

**关键词特征**：
```python
prompt_keywords = ["请", "生成", "你是一个", "扮演"]
workflow_keywords = ["步骤", "流程", "然后", "最后"]
industry_keywords = ["经验", "最佳实践", "优化", "性能"]
guide_keywords = ["指南", "教程", "方法", "原则"]

features.update({
    "prompt_keyword_count": sum(1 for k in prompt_keywords if k in content),
    "workflow_keyword_count": sum(1 for k in workflow_keywords if k in content),
    "industry_keyword_count": sum(1 for k in industry_keywords if k in content),
    "guide_keyword_count": sum(1 for k in guide_keywords if k in content)
})
```

### 元数据特征

```python
features.update({
    "source": metadata.get("source"),
    "has_url": bool(url),
    "has_author": bool(metadata.get("author"))
})
```

---

## 4.2.3 分类规则引擎

### 规则优先级

**规则 1：快速规则（优先级最高）**

```python
def classify_by_rules(content):
    # Prompt 规则
    if re.search(r'你是一个.*请.*', content):
        return "Prompt", 0.95, "包含角色设定和任务指令"
    
    # Workflow 规则
    if re.search(r'第一步.*第二步.*第三步', content):
        return "Workflow", 0.90, "包含明确的步骤说明"
    
    # Industry 规则
    if re.search(r'(经验|最佳实践|优化).*\d+.*条', content):
        return "Industry Knowledge", 0.85, "包含经验总结"
    
    # Guide 规则
    if re.search(r'(指南|教程|方法)', content):
        return "Guide", 0.80, "包含方法论或指导"
    
    return None, 0.0, None
```

**规则 2：关键词规则（优先级中等）**

```python
def classify_by_keywords(content, features):
    keyword_scores = {
        "Prompt": features["prompt_keyword_count"] * 0.3,
        "Workflow": features["workflow_keyword_count"] * 0.3,
        "Industry Knowledge": features["industry_keyword_count"] * 0.3,
        "Guide": features["guide_keyword_count"] * 0.3
    }
    
    max_type = max(keyword_scores, key=keyword_scores.get)
    max_score = keyword_scores[max_type]
    
    if max_score > 0.6:
        confidence = min(0.9, 0.6 + max_score * 0.3)
        reason = f"关键词匹配：{max_type} 相关词出现 {max_score:.2f} 次"
        return max_type, confidence, reason
    
    return None, 0.0, None
```

**规则 3：LLM 规则（优先级最低）**

```python
def classify_by_llm(content, features):
    prompt = f"""
请将以下内容分类为 4 种类型之一：Prompt、Workflow、Industry Knowledge、Guide。

内容：
{content}

请返回 JSON 格式：
{{
    "type": "分类类型",
    "confidence": 置信度（0-1 之间的浮点数），
    "reason": "分类理由"
}}
"""
    
    response = call_claude_api(prompt)
    return response["type"], response["confidence"], response["reason"]
```

---

## 4.2.4 分类结果验证

### 验证规则

**规则 1：长度验证**

```python
def validate_by_length(content, classification, confidence):
    content_length = len(content)
    
    # Prompt 通常较短
    if classification == "Prompt" and content_length > 1000:
        confidence *= 0.8  # 降低置信度
    
    # Guide 通常较长
    if classification == "Guide" and content_length < 300:
        confidence *= 0.7
    
    return confidence
```

**规则 2：结构验证**

```python
def validate_by_structure(content, classification, confidence):
    has_steps = bool(re.search(r'(第一|第二步|step)', content))
    has_code = bool(re.search(r'```', content))
    
    # Workflow 应该有步骤
    if classification == "Workflow" and not has_steps:
        confidence *= 0.6
    
    # Industry 可能有代码示例
    if classification == "Industry Knowledge" and not has_code:
        confidence *= 0.8
    
    return confidence
```

**规则 3：置信度验证**

```python
def validate_by_confidence(classification, confidence):
    # 低置信度标记为不确定
    if confidence < 0.7:
        return "uncertain", confidence
    # 中等置信度需要人工审核
    elif confidence < 0.9:
        return "needs_review", confidence
    # 高置信度直接采用
    else:
        return "high_confidence", confidence
```

---

## Layer 2 技术实现

### 技术栈

- **Python**：主要编程语言
- **Claude API**：LLM 分类
- **Regex**：规则匹配
- **Pandas**：数据处理

### 核心脚本

**主脚本**：`/root/clawd/skills/ai-prompt-workflow/scripts/classify-content.py`

**功能**：
- 读取采集的内容
- 提取特征
- 应用规则引擎
- 调用 LLM 分类
- 验证分类结果
- 输出分类结果

**使用方法**：
```bash
# 分类所有内容
python3 classify-content.py --input /root/clawd/data/prompts/collected/prompts-2026-02-04.jsonl

# 分类单个内容
python3 classify-content.py --content "你是一位资深产品经理..."

# 测试模式
python3 classify-content.py --test-mode
```

### 分类 Prompt 设计

**Prompt 模板**：
```python
CLASSIFICATION_PROMPT = """
你是一个内容分类专家。请将以下内容分类为 4 种类型之一：

1. **Prompt（提示词）**：可直接用于 AI 模型的单个或一组指令
   - 特征：包含明确的指令、角色设定、任务说明
   - 示例："你是一位资深产品经理。请分析以下需求..."

2. **Workflow（工作流）**：多步骤的执行流程，需要联网或工具调用
   - 特征：包含步骤说明、条件判断、多个操作
   - 示例："第一步：搜索论文，第二步：总结内容..."

3. **Industry Knowledge（行业经验）**：特定领域的专业知识和经验总结
   - 特征：包含专业术语、经验总结、最佳实践
   - 示例："作为一名资深前端工程师，我总结了 10 条性能优化经验..."

4. **Guide/Best Practice（指南）**：理论框架、方法论、系统性指导
   - 特征：包含理论、方法论、系统性指导
   - 示例："如何设计高质量的产品需求文档？一、核心要素..."

内容：
{content}

请返回 JSON 格式：
{{
    "type": "分类类型",
    "confidence": 置信度（0-1 之间的浮点数），
    "reason": "分类理由（详细说明为什么选择这个类型）"
}}
"""
```

---

## Layer 2 监控指标

| 指标 | 定义 | 目标值 | 测量周期 |
|------|------|--------|----------|
| 分类准确率 | 人工审核的正确率 | ≥ 85% | 每周 |
| 高置信度占比 | 置信度 ≥ 0.9 的占比 | ≥ 80% | 每天 |
| 不确定分类占比 | 置信度 < 0.7 的占比 | ≤ 10% | 每天 |
| 规则引擎命中率 | 通过规则引擎分类的比例 | ≥ 70% | 每天 |
| LLM 分类比例 | 通过 LLM 分类的比例 | ≤ 30% | 每天 |

---

## Layer 2 错误处理

### 错误分类

| 错误类型 | 描述 | 处理策略 |
|---------|------|----------|
| LLM API 错误 | Claude API 调用失败 | 降级到规则分类，记录日志 |
| 分类失败 | 所有规则和 LLM 都无法分类 | 标记为"不确定"，进入人工审核 |
| 置信度过低 | 分类结果置信度 < 0.5 | 标记为"不确定"，进入人工审核 |
| 格式错误 | LLM 返回格式不符合预期 | 重试 3 次，失败则降级 |

---

## Layer 2 持续优化

### 反馈收集

**人工审核结果**：
```json
{
  "id": "content_123",
  "auto_classification": "Prompt",
  "auto_confidence": 0.85,
  "manual_classification": "Workflow",
  "manual_confidence": 0.95,
  "auditor": "username",
  "audited_at": "2026-02-04T00:00:00Z"
}
```

### 模型优化

**定期优化**（每周）：
1. 收集人工审核结果
2. 分析分类错误的模式
3. 调整规则引擎
4. 更新分类 Prompt

### A/B 测试

**测试方法**：
- 随机抽取 10% 的内容
- 使用新规则分类
- 对比新旧规则的准确率
- 优胜劣汰

---

**Layer 2: 自动分类层 - 完成时间：2026-02-04 23:35**

# Layer 3: 分类评分层

### 概述

分类评分层是漏斗模型的第三层，负责根据内容类型使用不同的评分标准，对内容进行质量评估。

### 核心目标

1. **差异化评分**：针对 4 种内容类型使用不同的评分标准
2. **多维度评估**：每个维度都有明确的评分标准
3. **评分一致性**：人工评分与自动评分的相关性 ≥ 0.8
4. **持续优化**：通过人工反馈不断优化评分模型

---

## 4.3.1 评分指标体系

### Prompt 评分标准（满分 100）

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 实用性 | 50% | 是否能解决实际问题？是否常用？ |
| 清晰度 | 30% | 指令是否明确？是否有歧义？ |
| 独特性 | 20% | 是否有创新？是否与其他提示词重复？ |

**评分细则**：

**实用性（50 分）**：
- 高（40-50 分）：
  - 解决常见问题（如代码生成、文档写作、数据分析）
  - 使用场景广泛
  - 可复用性强
- 中（30-39 分）：
  - 解决特定问题
  - 有一定使用场景
  - 可复用性一般
- 低（< 30 分）：
  - 过于小众（如生成特定格式的诗歌）
  - 使用场景有限
  - 难以复用

**清晰度（30 分）**：
- 高（24-30 分）：
  - 指令明确，无歧义
  - 输出格式清晰
  - 易于理解和修改
- 中（18-23 分）：
  - 指令基本清晰
  - 部分内容模糊
  - 需要补充说明
- 低（< 18 分）：
  - 指令模糊，难以理解
  - 输出格式不明确
  - 需要大量修改

**独特性（20 分）**：
- 高（16-20 分）：
  - 创新性强，独特
  - 与常见提示词有明显差异
  - 有独特的视角或方法
- 中（12-15 分）：
  - 有一定特色
  - 与常见提示词有差异
  - 但不够独特
- 低（< 12 分）：
  - 与常见提示词重复
  - 缺乏创新
  - 类似内容很多

---

### Workflow 评分标准（满分 100）

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 完整性 | 30% | 流程是否完整？是否有遗漏的步骤？ |
| 可扩展性 | 20% | 是否可以扩展？是否可以修改？ |
| 实用性 | 30% | 是否能解决实际问题？是否常用？ |
| 可复用性 | 20% | 是否可以重复使用？是否可移植？ |

**评分细则**：

**完整性（30 分）**：
- 高（24-30 分）：
  - 流程完整，每一步都有清晰说明
  - 包含所有必要的步骤
  - 无遗漏
- 中（18-23 分）：
  - 流程基本完整
  - 部分步骤模糊
  - 需要补充
- 低（< 18 分）：
  - 流程不完整
  - 缺少关键步骤
  - 难以执行

**可扩展性（20 分）**：
- 高（16-20 分）：
  - 容易扩展和修改
  - 提供扩展点
  - 支持自定义
- 中（12-15 分）：
  - 可以扩展
  - 但有一定限制
  - 需要修改代码
- 低（< 12 分）：
  - 难以扩展
  - 硬编码
  - 难以修改

**实用性（30 分）**：
- 高（24-30 分）：
  - 解决实际问题
  - 使用场景多
  - 可操作性强
- 中（18-23 分）：
  - 有一定实用性
  - 但场景有限
  - 操作困难
- 低（< 18 分）：
  - 实用性低
  - 难以落地
  - 没有实际价值

**可复用性（20 分）**：
- 高（16-20 分）：
  - 可以重复使用
  - 可移植到不同场景
  - 通用性强
- 中（12-15 分）：
  - 可以复用
  - 但需要调整
  - 通用性一般
- 低（< 12 分）：
  - 难以复用
  - 场景特定
  - 难以移植

---

### Industry Knowledge 评分标准（满分 100）

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 专业深度 | 40% | 是否有深度？是否专业？是否有独特见解？ |
| 实用性 | 40% | 是否能解决实际问题？是否有可操作性？ |
| 系统性 | 20% | 是否有结构？是否完整？是否成体系？ |

**评分细则**：

**专业深度（40 分）**：
- 高（32-40 分）：
  - 有深度，专业
  - 有独特见解
  - 包含行业最佳实践
- 中（24-31 分）：
  - 有一定深度
  - 但不够深入
  - 缺乏独特见解
- 低（< 24 分）：
  - 浅显
  - 缺乏深度
  - 重复常见内容

**实用性（40 分）**：
- 高（32-40 分）：
  - 能解决实际问题
  - 可操作性强
  - 有明确的实施步骤
- 中（24-31 分）：
  - 有一定实用性
  - 但操作困难
  - 缺乏实施步骤
- 低（< 24 分）：
  - 实用性低
  - 难以落地
  - 缺乏可操作性

**系统性（20 分）**：
- 高（16-20 分）：
  - 有结构，完整
  - 成体系
  - 逻辑严密
- 中（12-15 分）：
  - 有一定结构
  - 但不完整
  - 逻辑一般
- 低（< 12 分）：
  - 结构混乱
  - 不成体系
  - 逻辑不清

---

### Guide 评分标准（满分 100）

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 指导性 | 40% | 是否有指导价值？是否可操作？ |
| 结构性 | 30% | 结构是否清晰？是否逻辑严密？ |
| 实用性 | 30% | 是否能解决实际问题？是否有可操作性？ |

**评分细则**：

**指导性（40 分）**：
- 高（32-40 分）：
  - 有很强的指导价值
  - 可操作性强
  - 有明确的行动指南
- 中（24-31 分）：
  - 有一定指导价值
  - 但操作困难
  - 缺乏行动指南
- 低（< 24 分）：
  - 指导价值低
  - 难以操作
  - 缺乏实用性

**结构性（30 分）**：
- 高（24-30 分）：
  - 结构清晰
  - 逻辑严密
  - 易于理解
- 中（18-23 分）：
  - 结构基本清晰
  - 逻辑一般
  - 部分内容混乱
- 低（< 18 分）：
  - 结构混乱
  - 逻辑不清
  - 难以理解

**实用性（30 分）**：
- 高（24-30 分）：
  - 能解决实际问题
  - 可操作性强
  - 有明确的实施步骤
- 中（18-23 分）：
  - 有一定实用性
  - 但操作困难
  - 缺乏实施步骤
- 低（< 18 分）：
  - 实用性低
  - 难以落地
  - 缺乏可操作性

---

## 4.3.2 评分算法选择

### 主要算法

**算法 1：LLM 评分（主要）**

使用 Claude API 进行评分，理解能力强，适合复杂内容。

**算法 2：规则评分（辅助）**

使用规则引擎快速评分，适合简单内容。

**算法 3：混合评分（推荐）**

结合 LLM 和规则，既保证准确率，又提高效率。

---

## 4.3.3 多维度评分

### LLM 评分 Prompt

**Prompt 模板**：
```python
SCORING_PROMPT_TEMPLATE = """
你是一个内容质量评估专家。请对以下内容进行评分。

内容类型：{content_type}
内容：
{content}

评分标准：
{scoring_criteria}

请对每个维度进行评分（1-10 分），并计算总分。

请返回 JSON 格式：
{{
    "scores": {{
        "{dimension_1}": 分数（1-10），
        "{dimension_2}": 分数（1-10），
        "{dimension_3}": 分数（1-10）
    }},
    "total_score": 总分（0-100），
    "reasoning": "评分理由（详细说明每个维度的得分原因）"
}}
"""
```

**使用示例**：
```python
def score_by_llm(content, content_type):
    scoring_criteria = get_scoring_criteria(content_type)
    prompt = SCORING_PROMPT_TEMPLATE.format(
        content_type=content_type,
        content=content,
        scoring_criteria=scoring_criteria
    )
    
    response = call_claude_api(prompt)
    return response["total_score"], response["reasoning"]
```

---

## 4.3.4 评分阈值设计

### 阈值设置

**质量等级**：
- **高质量**：≥ 70 分（直接转换）
- **中质量**：50-69 分（内容补充后转换）
- **低质量**：< 50 分（丢弃或标记）

**内容类型调整**：

| 内容类型 | 高质量阈值 | 中质量阈值 | 低质量阈值 |
|---------|-----------|-----------|-----------|
| Prompt | 70 | 50-69 | < 50 |
| Workflow | 65 | 45-64 | < 45 |
| Industry | 70 | 50-69 | < 50 |
| Guide | 75 | 55-74 | < 55 |

**说明**：
- Prompt 和 Industry 要求较高（≥ 70）
- Workflow 要求稍低（≥ 65），因为可以通过补充完善
- Guide 要求最高（≥ 75），因为需要系统性

---

## Layer 3 技术实现

### 核心脚本

**主脚本**：`/root/clawd/skills/ai-prompt-workflow/scripts/score-content.py`

**功能**：
- 读取分类后的内容
- 根据内容类型选择评分标准
- 调用 LLM 评分
- 计算总分
- 输出评分结果

**使用方法**：
```bash
# 评分所有内容
python3 score-content.py --input /root/clawd/data/prompts/classified/

# 评分单个内容
python3 score-content.py --content "你是一位资深产品经理..." --type Prompt

# 测试模式
python3 score-content.py --test-mode
```

### 评分标准配置

**配置文件**：`/root/clawd/config/scoring-standards.yaml`

**示例**：
```yaml
content_types:
  Prompt:
    dimensions:
      - name: 实用性
        weight: 0.5
        description: 是否能解决实际问题？是否常用？
        high_score: [40, 50]
        medium_score: [30, 39]
        low_score: [0, 29]
      - name: 清晰度
        weight: 0.3
        description: 指令是否明确？是否有歧义？
        high_score: [24, 30]
        medium_score: [18, 23]
        low_score: [0, 17]
      - name: 独特性
        weight: 0.2
        description: 是否有创新？是否与其他提示词重复？
        high_score: [16, 20]
        medium_score: [12, 15]
        low_score: [0, 11]
    thresholds:
      high: 70
      medium: 50
      
  Workflow:
    dimensions:
      - name: 完整性
        weight: 0.3
        description: 流程是否完整？是否有遗漏的步骤？
        high_score: [24, 30]
        medium_score: [18, 23]
        low_score: [0, 17]
      - name: 可扩展性
        weight: 0.2
        description: 是否可以扩展？是否可以修改？
        high_score: [16, 20]
        medium_score: [12, 15]
        low_score: [0, 11]
      - name: 实用性
        weight: 0.3
        description: 是否能解决实际问题？是否常用？
        high_score: [24, 30]
        medium_score: [18, 23]
        low_score: [0, 17]
      - name: 可复用性
        weight: 0.2
        description: 是否可以重复使用？是否可移植？
        high_score: [16, 20]
        medium_score: [12, 15]
        low_score: [0, 11]
    thresholds:
      high: 65
      medium: 45
```

---

## Layer 3 监控指标

| 指标 | 定义 | 目标值 | 测量周期 |
|------|------|--------|----------|
| 评分准确率 | 人工评分与自动评分的相关性 | ≥ 0.8 | 每周 |
| 评分一致性 | 同一内容多次评分的标准差 | ≤ 5 | 每周 |
| 高质量占比 | ≥ 70 分的内容占比 | ≥ 10% | 每周 |
| 中质量占比 | 50-69 分的内容占比 | ≥ 20% | 每周 |
| 低质量占比 | < 50 分的内容占比 | ≤ 70% | 每周 |

---

## Layer 3 持续优化

### 反馈收集

**人工评分结果**：
```json
{
  "id": "content_123",
  "auto_score": 65,
  "auto_reasoning": "实用性中等，清晰度高，独特性低",
  "manual_score": 70,
  "manual_reasoning": "实用性高，清晰度高，独特性中等",
  "auditor": "username",
  "audited_at": "2026-02-04T00:00:00Z"
}
```

### 模型优化

**定期优化**（每周）：
1. 收集人工评分结果
2. 分析评分差异
3. 调整评分标准
4. 更新评分 Prompt

### A/B 测试

**测试方法**：
- 随机抽取 10% 的内容
- 使用新评分标准评分
- 对比新旧标准的相关性
- 优胜劣汰

---

**Layer 3: 分类评分层 - 完成时间：2026-02-04 23:40**

# Layer 4: 质量筛选层

### 概述

质量筛选层是漏斗模型的第四层，负责根据评分结果筛选高质量内容，过滤低质量内容。

### 核心目标

1. **高效筛选**：快速识别高质量内容
2. **低误杀率**：高质量内容的误杀率 < 5%
3. **高通过率**：中质量内容的通过率 ≥ 90%
4. **可控性**：支持人工干预和调整

---

## 4.4.1 质量标准定义

### 质量等级

根据评分结果，将内容分为 3 个等级：

| 质量等级 | 评分范围 | 处理策略 | 说明 |
|---------|---------|---------|------|
| **高质量** | ≥ 70 | 直接转换 | 无需修改，可直接转换为 Skill |
| **中质量** | 50-69 | 内容补充后转换 | 需要补充信息，然后转换 |
| **低质量** | < 50 | 丢弃或标记 | 丢弃或进入人工审核队列 |

### 内容类型调整

不同的内容类型使用不同的阈值：

| 内容类型 | 高质量阈值 | 中质量阈值 | 低质量阈值 |
|---------|-----------|-----------|-----------|
| Prompt | 70 | 50-69 | < 50 |
| Workflow | 65 | 45-64 | < 45 |
| Industry | 70 | 50-69 | < 50 |
| Guide | 75 | 55-74 | < 55 |

**说明**：
- Prompt 和 Industry 要求较高（≥ 70）
- Workflow 要求稍低（≥ 65），因为可以通过补充完善
- Guide 要求最高（≥ 75），因为需要系统性

---

## 4.4.2 筛选规则配置

### 规则 1：阈值筛选

**规则**：根据评分阈值筛选内容

**实现**：
```python
def filter_by_threshold(content, content_type, score):
    thresholds = {
        "Prompt": {"high": 70, "medium": 50},
        "Workflow": {"high": 65, "medium": 45},
        "Industry Knowledge": {"high": 70, "medium": 50},
        "Guide": {"high": 75, "medium": 55}
    }
    
    th = thresholds.get(content_type, thresholds["Prompt"])
    
    if score >= th["high"]:
        return "high", "直接转换"
    elif score >= th["medium"]:
        return "medium", "内容补充后转换"
    else:
        return "low", "丢弃或人工审核"
```

### 规则 2：去重筛选

**规则**：过滤重复或相似的内容

**实现**：
```python
def filter_by_duplicate(content, existing_contents, threshold=0.95):
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    content_embedding = model.encode(content["content"])
    
    for existing in existing_contents:
        existing_embedding = model.encode(existing["content"])
        similarity = cosine_similarity(
            [content_embedding],
            [existing_embedding]
        )[0][0]
        
        if similarity >= threshold:
            return False, f"与内容 {existing['id']} 相似度 {similarity:.2f}"
    
    return True, None
```

### 规则 3：合规性筛选

**规则**：过滤不合规内容

**不合规内容**：
- 包含敏感词（暴力、色情、政治等）
- 包含恶意链接或代码
- 纯广告或推销
- 无实际内容

**实现**：
```python
def filter_by_compliance(content):
    import re
    
    # 敏感词列表
    sensitive_words = [
        "暴力", "色情", "政治", "赌博",
        "诈骗", "洗钱", "黑客", "病毒"
    ]
    
    # 检查敏感词
    for word in sensitive_words:
        if word in content["content"]:
            return False, f"包含敏感词：{word}"
    
    # 检查恶意链接
    if re.search(r'(bit\.ly|tinyurl\.com|short\.link)', content.get("url", "")):
        return False, "包含短链接"
    
    # 检查纯广告
    if re.search(r'(立即购买|限时优惠|点击领取)', content["content"]):
        return False, "包含广告内容"
    
    return True, None
```

### 规则 4：完整性筛选

**规则**：过滤内容不完整的条目

**不完整内容**：
- 内容长度 < 50 字
- 缺少必要的字段
- 内容为空或只有空白字符

**实现**：
```python
def filter_by_completeness(content):
    # 检查长度
    if len(content["content"]) < 50:
        return False, f"内容太短：{len(content['content'])} 字符"
    
    # 检查必填字段
    required_fields = ["id", "title", "content", "type", "source"]
    for field in required_fields:
        if field not in content or not content[field]:
            return False, f"缺少必填字段：{field}"
    
    # 检查内容是否为空
    if not content["content"].strip():
        return False, "内容为空"
    
    return True, None
```

---

## 4.4.3 人工审核机制

### 审核队列

**触发条件**：
1. 低置信度分类（< 0.7）
2. 评分在阈值边缘（±5 分）
3. 去重发现相似但不确定是否重复
4. 规则冲突（不同规则给出相反结果）

**队列优先级**：

| 优先级 | 触发条件 | 处理时限 |
|--------|---------|---------|
| **P0（紧急）** | 高质量内容但规则冲突 | 4 小时 |
| **P1（高）** | 中质量内容，阈值边缘 | 24 小时 |
| **P2（中）** | 低置信度分类 | 48 小时 |
| **P3（低）** | 低质量内容，可能误杀 | 7 天 |

### 审核接口

**Slack 通知**：
```python
def send_to_slack_queue(content, priority, reason):
    from slack_sdk import WebClient
    
    client = WebClient(token=os.environ["SLACK_TOKEN"])
    
    message = f"""
*人工审核请求 - 优先级 {priority}*

内容 ID: {content['id']}
内容类型: {content['type']}
评分: {content['score']}
原因: {reason}

内容摘要:
{content['content'][:200]}...

操作按钮:
- 通过：/approve {content['id']}
- 拒绝：/reject {content['id']}
- 跳过：/skip {content['id']}
"""
    
    client.chat_postMessage(
        channel="#clawdbot-review",
        text=message,
        mrkdwn=True
    )
```

### 审核结果反馈

**记录审核结果**：
```json
{
  "id": "content_123",
  "auto_decision": "medium",
  "auto_score": 65,
  "manual_decision": "high",
  "manual_score": 70,
  "reason": "内容质量优于自动评估",
  "auditor": "username",
  "audited_at": "2026-02-05T00:00:00Z"
}
```

**用于模型优化**：
1. 分析审核差异
2. 调整评分标准
3. 优化规则引擎
4. 更新分类模型

---

## 4.4.4 筛选结果反馈

### 筛选统计

**每日统计**：
```json
{
  "date": "2026-02-05",
  "total_filtered": 500,
  "by_quality": {
    "high": 50,
    "medium": 200,
    "low": 250
  },
  "by_rule": {
    "threshold": 450,
    "duplicate": 20,
    "compliance": 15,
    "completeness": 15
  },
  "to_manual_review": 10,
  "rejected": 200
}
```

### 筛选报告

**报告内容**：
1. 筛选结果统计
2. 高质量内容列表
3. 中质量内容列表
4. 人工审核队列
5. 拒绝原因分析

**生成报告**：
```python
def generate_filtering_report(date):
    stats = load_filtering_stats(date)
    
    report = f"""
# 质量筛选报告 - {date}

## 筛选统计

- 总筛选数: {stats['total_filtered']}
- 高质量: {stats['by_quality']['high']} ({stats['by_quality']['high'] / stats['total_filtered'] * 100:.1f}%)
- 中质量: {stats['by_quality']['medium']} ({stats['by_quality']['medium'] / stats['total_filtered'] * 100:.1f}%)
- 低质量: {stats['by_quality']['low']} ({stats['by_quality']['low'] / stats['total_filtered'] * 100:.1f}%)

## 规则应用

- 阈值筛选: {stats['by_rule']['threshold']}
- 去重筛选: {stats['by_rule']['duplicate']}
- 合规性筛选: {stats['by_rule']['compliance']}
- 完整性筛选: {stats['by_rule']['completeness']}

## 人工审核

- 待审核: {stats['to_manual_review']}
  - P0: {stats['by_priority']['P0']}
  - P1: {stats['by_priority']['P1']}
  - P2: {stats['by_priority']['P2']}
  - P3: {stats['by_priority']['P3']}

## 拒绝原因分析

- 评分过低: {stats['rejection_reasons']['low_score']}
- 内容重复: {stats['rejection_reasons']['duplicate']}
- 不合规: {stats['rejection_reasons']['compliance']}
- 内容不完整: {stats['rejection_reasons']['incomplete']}
"""
    
    return report
```

---

## Layer 4 技术实现

### 技术栈

- **Python**：主要编程语言
- **Sentence-Transformers**：语义去重
- **Slack SDK**：人工审核通知
- **Pandas**：数据分析和统计

### 核心脚本

**主脚本**：`/root/clawd/skills/ai-prompt-workflow/scripts/filter-quality.py`

**功能**：
- 读取评分后的内容
- 应用筛选规则
- 筛选高质量内容
- 发送到人工审核队列
- 生成筛选报告

**使用方法**：
```bash
# 筛选所有内容
python3 filter-quality.py --input /root/clawd/data/prompts/scored/

# 筛选单个内容
python3 filter-quality.py --content "..." --type Prompt --score 65

# 测试模式
python3 filter-quality.py --test-mode
```

### 配置文件

**配置文件**：`/root/clawd/config/quality-filter.yaml`

**示例**：
```yaml
quality_thresholds:
  Prompt:
    high: 70
    medium: 50
  Workflow:
    high: 65
    medium: 45
  Industry Knowledge:
    high: 70
    medium: 50
  Guide:
    high: 75
    medium: 55

filtering_rules:
  threshold:
    enabled: true
    priority: 1
  duplicate:
    enabled: true
    similarity_threshold: 0.95
    priority: 2
  compliance:
    enabled: true
    sensitive_words:
      - 暴力
      - 色情
      - 政治
    priority: 3
  completeness:
    enabled: true
    min_length: 50
    priority: 4

manual_review:
  enabled: true
  slack_channel: "#clawdbot-review"
  priorities:
    P0:
      description: "紧急"
      timeout_hours: 4
    P1:
      description: "高"
      timeout_hours: 24
    P2:
      description: "中"
      timeout_hours: 48
    P3:
      description: "低"
      timeout_hours: 168
```

---

## Layer 4 监控指标

| 指标 | 定义 | 目标值 | 测量周期 |
|------|------|--------|----------|
| 高质量占比 | ≥ 阈值的内容占比 | ≥ 10% | 每周 |
| 中质量占比 | 50-69 分的内容占比 | ≥ 40% | 每周 |
| 低质量占比 | < 50 分的内容占比 | ≤ 50% | 每周 |
| 误杀率 | 高质量内容被拒绝的比例 | < 5% | 每周 |
| 人工审核处理率 | 24 小时内处理的比例 | ≥ 80% | 每天 |
| 去重率 | 重复内容的比例 | < 5% | 每周 |

---

## Layer 4 错误处理

### 错误分类

| 错误类型 | 描述 | 处理策略 |
|---------|------|----------|
| 规则冲突 | 不同规则给出相反结果 | 人工审核 |
| 评分异常 | 评分超出范围或缺失 | 重新评分 |
| 去重失败 | 语义去重失败 | 跳过去重，标记为不确定 |
| 审核超时 | 人工审核超时 | 降级处理（直接拒绝或接受） |

---

## Layer 4 持续优化

### 规则调优

**定期调优**（每周）：
1. 分析筛选结果统计
2. 评估规则效果
3. 调整阈值和规则
4. A/B 测试新规则

### 反馈循环

**流程**：
1. 收集人工审核结果
2. 分析审核差异
3. 优化评分标准
4. 更新筛选规则

---

**Layer 4: 质量筛选层 - 完成时间：2026-02-05 07:15**

# Layer 5: 内容补充层

### 概述

内容补充层是漏斗模型的第五层，负责为中质量内容（50-69 分）补充缺失信息，提升内容完整性和可用性。

### 核心目标

1. **智能补充**：自动识别缺失信息并补充
2. **高准确率**：补充信息的准确率 ≥ 90%
3. **可验证性**：补充的内容可验证和追溯
4. **人工兜底**：自动补充失败时人工介入

---

## 4.5.1 缺失信息识别

### Prompt 缺失信息

**必需信息**：
- [x] 角色设定
- [x] 任务描述
- [x] 输出格式
- [ ] 示例
- [ ] 参数说明
- [ ] 使用场景

**识别方法**：
```python
def identify_missing_prompt_info(content):
    missing = []
    
    # 检查角色设定
    if not re.search(r'(你是一位|你是|role:|act as)', content, re.IGNORECASE):
        missing.append("角色设定")
    
    # 检查任务描述
    if not re.search(r'(请|生成|分析|创建)', content, re.IGNORECASE):
        missing.append("任务描述")
    
    # 检查输出格式
    if not re.search(r'(输出|格式|format:|output:)', content, re.IGNORECASE):
        missing.append("输出格式")
    
    # 检查示例
    if not re.search(r'(示例|example|for example:)', content, re.IGNORECASE):
        missing.append("示例")
    
    return missing
```

---

### Workflow 缺失信息

**必需信息**：
- [x] 步骤说明
- [ ] 工具说明
- [ ] 参数说明
- [ ] 错误处理
- [ ] 示例代码

**识别方法**：
```python
def identify_missing_workflow_info(content):
    missing = []
    
    # 检查步骤说明
    if not re.search(r'(第一步|第二步|step 1|step 2)', content, re.IGNORECASE):
        missing.append("步骤说明")
    
    # 检查工具说明
    if not re.search(r'(使用|调用|tool:|api:)', content, re.IGNORECASE):
        missing.append("工具说明")
    
    # 检查参数说明
    if not re.search(r'(参数|parameter:|arg:|options:)', content, re.IGNORECASE):
        missing.append("参数说明")
    
    # 检查错误处理
    if not re.search(r'(错误|异常|error|exception|try|catch)', content, re.IGNORECASE):
        missing.append("错误处理")
    
    return missing
```

---

### Industry Knowledge 缺失信息

**必需信息**：
- [x] 专业术语
- [ ] 背景知识
- [ ] 代码示例
- [ ] 最佳实践
- [ ] 常见问题

**识别方法**：
```python
def identify_missing_industry_info(content):
    missing = []
    
    # 检查背景知识
    if not re.search(r'(背景|context|introduction|overview)', content, re.IGNORECASE):
        missing.append("背景知识")
    
    # 检查代码示例
    if not re.search(r'```', content):
        missing.append("代码示例")
    
    # 检查最佳实践
    if not re.search(r'(最佳实践|best practice|recommended)', content, re.IGNORECASE):
        missing.append("最佳实践")
    
    # 检查常见问题
    if not re.search(r'(常见问题|faq|troubleshooting|issue)', content, re.IGNORECASE):
        missing.append("常见问题")
    
    return missing
```

---

### Guide 缺失信息

**必需信息**：
- [x] 理论框架
- [ ] 方法论
- [ ] 实施步骤
- [ ] 工具和模板
- [ ] 案例研究

**识别方法**：
```python
def identify_missing_guide_info(content):
    missing = []
    
    # 检查方法论
    if not re.search(r'(方法论|method|approach|framework)', content, re.IGNORECASE):
        missing.append("方法论")
    
    # 检查实施步骤
    if not re.search(r'(实施|部署|步骤|step)', content, re.IGNORECASE):
        missing.append("实施步骤")
    
    # 检查工具和模板
    if not re.search(r'(工具|模板|tool|template)', content, re.IGNORECASE):
        missing.append("工具和模板")
    
    # 检查案例研究
    if not re.search(r'(案例|example|case study|use case)', content, re.IGNORECASE):
        missing.append("案例研究")
    
    return missing
```

---

## 4.5.2 内容增强策略

### 策略 1：联网搜索补充

**适用场景**：补充背景知识、最佳实践、案例研究

**实现**：
```python
def enhance_by_web_search(content, missing_info):
    from searxng import search
    
    enhanced_content = content
    
    for info in missing_info:
        # 生成搜索查询
        query = f"{content['title']} {info}"
        
        # 搜索相关内容
        results = search(query, n=5)
        
        if results:
            # 提取第一个结果的内容
            best_result = results[0]
            additional_content = web_fetch(best_result["url"])
            
            # 补充到内容中
            if additional_content:
                enhanced_content += f"\n\n## {info}\n\n{additional_content[:1000]}"
    
    return enhanced_content
```

---

### 策略 2：工具调用补充

**适用场景**：补充代码示例、API 使用说明、参数说明

**实现**：
```python
def enhance_by_tool_calls(content, missing_info):
    enhanced_content = content
    
    # 补充代码示例
    if "代码示例" in missing_info:
        # 调用代码生成工具
        code_example = generate_code_example(content)
        if code_example:
            enhanced_content += f"\n\n## 代码示例\n\n```python\n{code_example}\n```"
    
    # 补充 API 使用说明
    if "工具说明" in missing_info:
        api_docs = fetch_api_docs(content)
        if api_docs:
            enhanced_content += f"\n\n## API 使用说明\n\n{api_docs}"
    
    # 补充参数说明
    if "参数说明" in missing_info:
        params = extract_parameters(content)
        param_docs = generate_param_docs(params)
        if param_docs:
            enhanced_content += f"\n\n## 参数说明\n\n{param_docs}"
    
    return enhanced_content
```

---

### 策略 3：LLM 生成补充

**适用场景**：补充示例、使用场景、最佳实践

**实现**：
```python
def enhance_by_llm(content, missing_info, content_type):
    enhanced_content = content
    
    for info in missing_info:
        # 生成补充内容
        prompt = f"""
请为以下{content_type}生成{info}：

标题：{content['title']}
内容：
{content['content']}

请生成详细、准确、实用的{info}。
"""
        
        additional_content = call_claude_api(prompt)
        
        if additional_content:
            enhanced_content += f"\n\n## {info}\n\n{additional_content}"
    
    return enhanced_content
```

---

### 策略 4：规则模板补充

**适用场景**：补充标准化的格式、结构

**实现**：
```python
# Prompt 模板
PROMPT_TEMPLATE = """
# {title}

{original_content}

## 使用场景

{usage_scenarios}

## 参数说明

{parameters}

## 示例

{examples}
"""

# Workflow 模板
WORKFLOW_TEMPLATE = """
# {title}

{original_content}

## 前置条件

{prerequisites}

## 工具和依赖

{tools_and_deps}

## 错误处理

{error_handling}

## 示例代码

{example_code}
"""

def enhance_by_template(content, content_type, missing_info):
    if content_type == "Prompt":
        template = PROMPT_TEMPLATE
    elif content_type == "Workflow":
        template = WORKFLOW_TEMPLATE
    else:
        return content
    
    # 填充模板
    filled_template = template.format(
        title=content["title"],
        original_content=content["content"],
        usage_scenarios=generate_usage_scenarios(content),
        parameters=extract_parameters(content),
        examples=generate_examples(content),
        prerequisites=generate_prerequisites(content),
        tools_and_deps=extract_tools(content),
        error_handling=generate_error_handling(content),
        example_code=generate_example_code(content)
    )
    
    return filled_template
```

---

## 4.5.3 结构化处理

### 格式标准化

**目标**：统一格式，便于转换

**标准化规则**：
1. 使用 Markdown 格式
2. 标题层级清晰（H1, H2, H3）
3. 代码块使用 ```language 标记
4. 列表使用 - 或 1.
5. 表格使用 Markdown 表格语法

**实现**：
```python
def standardize_format(content):
    # 转换为 Markdown
    from markdownify import markdownify
    markdown_content = markdownify(content)
    
    # 标准化标题
    markdown_content = re.sub(r'^(#+)\s*', r'\1 ', markdown_content, flags=re.MULTILINE)
    
    # 标准化代码块
    markdown_content = re.sub(r'```\s*([^`]+)\s*```', r'```\1```', markdown_content)
    
    # 标准化列表
    markdown_content = re.sub(r'^\s*[\d\-\*]+\.?\s*', '- ', markdown_content, flags=re.MULTILINE)
    
    return markdown_content
```

---

### 元数据提取

**提取内容元数据**：
- 关键词
- 标签
- 分类
- 语言

**实现**：
```python
def extract_metadata(content, content_type):
    metadata = {}
    
    # 提取关键词
    keywords = extract_keywords(content["content"])
    metadata["keywords"] = keywords
    
    # 提取标签
    tags = generate_tags(content["title"], content["content"])
    metadata["tags"] = tags
    
    # 分类
    metadata["type"] = content_type
    
    # 语言
    language = detect_language(content["content"])
    metadata["language"] = language
    
    return metadata
```

---

## 4.5.4 补充质量评估

### 补充前后对比

**对比指标**：
- 内容长度
- 完整性评分
- 实用性评分
- 可用性评分

**实现**：
```python
def evaluate_enhancement(original_content, enhanced_content):
    # 评分原始内容
    original_score = score_content(original_content)
    
    # 评分补充后内容
    enhanced_score = score_content(enhanced_content)
    
    # 计算提升
    improvement = {
        "length": len(enhanced_content) - len(original_content),
        "completeness": enhanced_score["completeness"] - original_score["completeness"],
        "practicality": enhanced_score["practicality"] - original_score["practicality"],
        "usability": enhanced_score["usability"] - original_score["usability"]
    }
    
    return improvement
```

---

### 质量阈值检查

**检查补充后是否达到高质量阈值**：

```python
def check_quality_threshold(enhanced_content, content_type):
    thresholds = {
        "Prompt": 70,
        "Workflow": 65,
        "Industry Knowledge": 70,
        "Guide": 75
    }
    
    score = score_content(enhanced_content)
    threshold = thresholds.get(content_type, 70)
    
    if score["total"] >= threshold:
        return True, "已达到高质量阈值"
    else:
        return False, f"未达到高质量阈值，当前评分：{score['total']}，阈值：{threshold}"
```

---

## Layer 5 技术实现

### 技术栈

- **Python**：主要编程语言
- **SearXNG**：联网搜索
- **Claude API**：LLM 生成
- **BeautifulSoup**：HTML 解析
- **Markdownify**：HTML 转 Markdown

### 核心脚本

**主脚本**：`/root/clawd/skills/ai-prompt-workflow/scripts/enhance-content.py`

**功能**：
- 识别缺失信息
- 应用增强策略
- 结构化处理
- 评估补充质量

**使用方法**：
```bash
# 补充所有中质量内容
python3 enhance-content.py --input /root/clawd/data/prompts/filtered/

# 补充单个内容
python3 enhance-content.py --content "..." --type Prompt --score 55

# 测试模式
python3 enhance-content.py --test-mode
```

### 配置文件

**配置文件**：`/root/clawd/config/content-enhancement.yaml`

**示例**：
```yaml
enhancement_strategies:
  web_search:
    enabled: true
    max_results: 5
    max_content_length: 1000
    priority: 1
    
  tool_calls:
    enabled: true
    tools:
      - code_generator
      - api_doc_fetcher
      - param_generator
    priority: 2
    
  llm_generation:
    enabled: true
    model: "claude-3-5-sonnet"
    max_length: 2000
    priority: 3
    
  template:
    enabled: true
    templates_dir: /root/clawd/templates/
    priority: 4

quality_thresholds:
  Prompt: 70
  Workflow: 65
  Industry Knowledge: 70
  Guide: 75

metadata_extraction:
  enabled: true
  extract_keywords: true
  generate_tags: true
  detect_language: true
```

---

## Layer 5 监控指标

| 指标 | 定义 | 目标值 | 测量周期 |
|------|------|--------|----------|
| 补充成功率 | 自动补充成功的比例 | ≥ 90% | 每天 |
| 补充准确率 | 补充内容的准确率 | ≥ 90% | 每周 |
| 质量提升率 | 补充后评分提升的比例 | ≥ 30% | 每周 |
| 达到高质量阈值 | 补充后达到高质量的比例 | ≥ 50% | 每周 |
| 人工介入率 | 需要人工介入的比例 | ≤ 10% | 每天 |

---

## Layer 5 错误处理

### 错误分类

| 错误类型 | 描述 | 处理策略 |
|---------|------|----------|
| 搜索失败 | 联网搜索失败或无结果 | 尝试其他策略，标记为待人工补充 |
| 工具调用失败 | 工具 API 调用失败 | 降级到 LLM 生成，标记为待验证 |
| LLM 生成失败 | LLM API 调用失败 | 尝试规则模板，标记为待人工补充 |
| 质量下降 | 补充后质量下降 | 回滚到原始内容，标记为待人工补充 |

---

## Layer 5 持续优化

### 策略优化

**定期优化**（每周）：
1. 分析补充成功率
2. 评估补充质量
3. 优化补充策略
4. A/B 测试新策略

### 反馈循环

**流程**：
1. 收集人工审核结果
2. 分析补充效果
3. 优化补充 Prompt
4. 更新补充策略

---

**Layer 5: 内容补充层 - 完成时间：2026-02-05 07:20**

# Layer 6: Skill 转换层

### 概述

Skill 转换层是漏斗模型的最后一层，负责将高质量内容转换为 Clawdbot Skill 格式，并发布到 ClawdHub。

### 核心目标

1. **高准确率**：转换的 Skill 100% 可用
2. **高质量**：转换的 Skill 符合 Clawdbot 规范
3. **自动化**：全自动转换和发布
4. **可追溯**：记录转换过程和版本

---

## 4.6.1 Skill 模板设计

### Skill 文件结构

```
skill-name/
├── SKILL.md              # 技能文档（必需）
├── scripts/              # 脚本目录（可选）
│   └── script.py
├── templates/            # 模板目录（可选）
│   └── template.txt
└── metadata.json         # 元数据（可选）
```

### SKILL.md 模板

```markdown
# Skill 名称

简短描述（1-2 句话）

## 功能描述

详细描述技能的功能、适用场景、使用方法。

## 使用方法

### 触发词

`技能触发词`

### 使用示例

`示例1`
`示例2`

## 技术实现

### 依赖

- Python 3.x
- 第三方库（如果有）

### 环境变量

- `ENV_VAR`: 环境变量说明

## 作者

作者名 / 组织

## 许可证

MIT
```

---

### Prompt 类型 Skill 模板

**示例**：
```markdown
# Prompt: 产品需求文档生成器

使用 AI 快速生成产品需求文档（PRD）

## 功能描述

该技能可以帮助产品经理快速生成标准的产品需求文档，包括需求背景、目标用户、功能列表、验收标准、优先级排序等。

## 使用方法

### 触发词

`生成PRD` 或 `write PRD`

### 使用示例

`生成PRD：一个在线教育平台的课程推荐功能`

输出：
```
# 产品需求文档（PRD）

## 1. 需求背景

在线教育平台需要为用户提供个性化的课程推荐功能，提高用户粘性和学习效果。

## 2. 目标用户

- 在校学生（18-25岁）
- 职场人士（25-40岁）
- 终身学习者（40+岁）

## 3. 功能列表

### 3.1 基础推荐
- 基于用户画像推荐课程
- 推荐历史记录

### 3.2 个性化推荐
- 学习进度分析
- 兴趣偏好识别
- 难度自适应

### 3.3 交互优化
- 推荐理由展示
- 用户反馈收集
- 推荐结果调整

## 4. 验收标准

- [ ] 推荐准确率 ≥ 80%
- [ ] 推荐响应时间 < 1s
- [ ] 用户满意度 ≥ 4.0/5.0

## 5. 优先级排序

P0: 基础推荐
P1: 个性化推荐
P2: 交互优化
```

## 技术实现

### 依赖

- 无特殊依赖

### 环境变量

- 无

## 作者

Momo (Clawdbot Team)

## 许可证

MIT
```

---

### Workflow 类型 Skill 模板

**示例**：
```markdown
# Workflow: 论文自动分析

自动化论文分析流程，包括摘要、关键点提取、结论总结

## 功能描述

该技能可以自动分析学术论文，生成结构化的摘要、提取关键观点和结论，并生成可读性强的总结报告。

## 使用方法

### 触发词

`分析论文` 或 `analyze paper`

### 使用示例

`分析论文：https://arxiv.org/abs/2101.00001`

输出：
```
# 论文分析报告

## 基本信息

- 标题：Attention Is All You Need
- 作者：Ashish Vaswani et al.
- 发表时间：2017
- 期刊：NIPS

## 摘要

本文提出了 Transformer 模型，一种基于自注意力机制的序列到序列模型...

## 关键点

1. 自注意力机制可以并行计算，提高训练效率
2. Transformer 完全基于注意力，不需要 RNN 或 CNN
3. 多头注意力可以学习不同的表示子空间

## 结论

Transformer 在机器翻译任务上取得了新的 SOTA，证明了自注意力机制的有效性。

## 相关工作

- [引用论文1]
- [引用论文2]
```

## 技术实现

### 依赖

- Python 3.x
- requests
- beautifulsoup4
- sentence-transformers

### 环境变量

- `ARXIV_API_KEY`: ArXiv API 密钥（可选）

## 工作流程

1. 搜索论文
2. 下载论文 PDF
3. 提取文本内容
4. 使用 LLM 分析论文
5. 生成结构化报告

## 作者

Momo (Clawdbot Team)

## 许可证

MIT
```

---

### Industry Knowledge 类型 Skill 模板

**示例**：
```markdown
# Industry: 前端性能优化最佳实践

前端性能优化的系统化知识和最佳实践

## 功能描述

该技能包含前端性能优化的核心知识点、优化技巧、代码示例和常见问题解答，帮助开发者提升 Web 应用性能。

## 使用方法

### 触发词

`前端优化` 或 `frontend performance`

### 使用示例

`前端优化：如何优化图片加载？`

输出：
```
# 图片加载优化

## 1. 使用现代图片格式

### WebP
- 压缩率高（比 JPEG 高 30%）
- 支持透明度和动画
- 浏览器支持：Chrome, Firefox, Edge, Safari

### AVIF
- 压缩率更高（比 WebP 高 20%）
- 浏览器支持：Chrome, Firefox, Edge

## 2. 实现懒加载

```html
<img src="placeholder.jpg" data-src="image.jpg" loading="lazy" alt="图片描述">
```

```javascript
// 代码示例
document.addEventListener("DOMContentLoaded", function() {
  const lazyImages = [].slice.call(document.querySelectorAll("img.lazy"));

  if ("IntersectionObserver" in window) {
    const lazyImageObserver = new IntersectionObserver(function(entries, observer) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          const lazyImage = entry.target;
          lazyImage.src = lazyImage.dataset.src;
          lazyImage.classList.remove("lazy");
          lazyImageObserver.unobserve(lazyImage);
        }
      });
    });

    lazyImages.forEach(function(lazyImage) {
      lazyImageObserver.observe(lazyImage);
    });
  }
});
```

## 3. 使用 CDN

```html
<img src="https://cdn.example.com/image.jpg" alt="图片描述">
```

## 4. 优化图片大小

- 使用 tinypng.com 压缩图片
- 调整图片分辨率（不超显示尺寸）
- 使用合适的图片格式（照片用 JPEG，图标用 PNG）

## 常见问题

**Q: 懒加载会影响 SEO 吗？**
A: 不会。现代搜索引擎可以正确解析懒加载的图片。

**Q: WebP 在 Safari 中不显示怎么办？**
A: 使用 <picture> 标签提供回退格式：
```html
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="图片描述">
</picture>
```
```

## 技术实现

### 依赖

- Python 3.x

### 环境变量

- 无

## 知识结构

### 核心概念
- Performance API
- 渲染性能
- 网络性能
- 内存优化

### 优化技巧
- 代码分割
- 资源压缩
- 缓存策略
- 预加载

### 代码示例
- 性能监控代码
- 优化前后对比
- 实际应用案例

### 常见问题
- 性能问题诊断
- 工具使用指南
- 最佳实践建议

## 作者

Momo (Clawdbot Team)

## 许可证

MIT
```

---

### Guide 类型 Skill 模板

**示例**：
```markdown
# Guide: 敏捷开发方法论

敏捷开发的系统性指南和最佳实践

## 功能描述

该技能提供了敏捷开发的完整方法论，包括核心原则、实施步骤、工具推荐和案例研究，帮助团队快速上手敏捷开发。

## 使用方法

### 触发词

`敏捷开发` 或 `agile methodology`

### 使用示例

`敏捷开发：如何开始实施 Scrum？`

输出：
```
# Scrum 实施指南

## 1. 准备阶段

### 1.1 组建 Scrum Team
- Product Owner（产品负责人）
- Scrum Master（敏捷教练）
- Development Team（开发团队，3-9人）

### 1.2 准备工作环境
- 物理或虚拟白板
- 任务管理工具（Jira, Trello）
- 沟通工具（Slack, Teams）

## 2. 核心概念

### 2.1 事件
- Sprint Planning（迭代规划）
- Daily Scrum（每日站会）
- Sprint Review（迭代评审）
- Sprint Retrospective（迭代回顾）

### 2.2 产物
- Product Backlog（产品待办列表）
- Sprint Backlog（迭代待办列表）
- Increment（可交付增量）

### 2.3 角色
- Product Owner（产品负责人）
- Scrum Master（敏捷教练）
- Development Team（开发团队）

## 3. 实施步骤

### Step 1: 创建 Product Backlog
- 列出所有需求
- 按优先级排序
- 估算工作量（故事点）

### Step 2: 规划第一个 Sprint
- 选择高优先级需求
- 分配给团队
- 设定 Sprint Goal

### Step 3: 执行 Sprint（2-4周）
- 每日站会（15分钟）
- 跟踪进度
- 协作开发

### Step 4: Sprint Review
- 展示完成的工作
- 收集反馈
- 调整 Product Backlog

### Step 5: Sprint Retrospective
- 回顾迭代过程
- 识别改进点
- 制定行动计划

## 4. 工具推荐

- Jira：项目管理
- Trello：看板工具
- Confluence：文档管理
- Slack：团队沟通

## 5. 常见问题

**Q: Scrum 适用于所有项目吗？**
A: 不适用。Scrum 适用于需求变化快、需要快速迭代的项目。

**Q: Daily Scrum 时间太长怎么办？**
A: 限制在 15 分钟内，只回答 3 个问题：
1. 昨天做了什么？
2. 今天打算做什么？
3. 有什么阻碍？

## 案例研究

**案例 1：初创公司实施 Scrum**
- 背景：5 人团队，产品快速迭代
- 实施：每周 Sprint，每日站会
- 结果：迭代周期从 1 个月缩短到 1 周

**案例 2：大公司 Scrum 转型**
- 背景：100 人团队，瀑布开发
- 实施：分 3 个阶段转型，培训先行
- 结果：交付速度提升 40%，质量提升 30%
```

## 技术实现

### 依赖

- Python 3.x

### 环境变量

- 无

## 指南结构

### 理论框架
- 核心概念
- 基本原则
- 方法论

### 实施步骤
- 准备阶段
- 执行阶段
- 优化阶段

### 工具和模板
- 推荐工具
- 可用模板
- 配置文件

### 案例研究
- 成功案例
- 失败教训
- 最佳实践

## 作者

Momo (Clawdbot Team)

## 许可证

MIT
```

---

## 4.6.2 转换规则引擎

### 规则 1：内容类型映射

**映射关系**：

| 内容类型 | Skill 类型 | 模板 |
|---------|-----------|------|
| Prompt | Prompt Skill | `prompt-skill-template.md` |
| Workflow | Workflow Skill | `workflow-skill-template.md` |
| Industry Knowledge | Industry Skill | `industry-skill-template.md` |
| Guide | Guide Skill | `guide-skill-template.md` |

**实现**：
```python
def map_content_to_skill_type(content_type):
    mapping = {
        "Prompt": "prompt",
        "Workflow": "workflow",
        "Industry Knowledge": "industry",
        "Guide": "guide"
    }
    
    return mapping.get(content_type, "generic")
```

---

### 规则 2：内容提取和映射

**提取内容元素**：
- 标题 → Skill 名称
- 内容 → 功能描述
- 分类 → 标签
- 评分 → 质量标记
- 元数据 → 作者信息

**实现**：
```python
def extract_skill_info(content):
    skill_info = {
        "name": generate_skill_name(content["title"]),
        "description": generate_skill_description(content["content"]),
        "tags": generate_tags(content),
        "quality_mark": f"Quality Score: {content['score']}/100",
        "author": "Momo (Clawdbot Team)",
        "license": "MIT"
    }
    
    return skill_info
```

---

### 规则 3：内容格式化

**格式化规则**：
1. 使用 Markdown 格式
2. 标题层级清晰（H1, H2, H3）
3. 代码块使用 ```language 标记
4. 列表使用 - 或 1.
5. 表格使用 Markdown 表格语法

**实现**：
```python
def format_content_for_skill(content):
    # 标准化格式
    formatted = standardize_format(content["content"])
    
    # 添加标题
    formatted = f"# {content['title']}\n\n{formatted}"
    
    # 添加质量标记
    formatted += f"\n\n---\n\n*Quality Score: {content['score']}/100*"
    
    return formatted
```

---

## 4.6.3 验证与测试

### 验证 1：格式验证

**检查项**：
- [x] SKILL.md 文件存在
- [x] Markdown 格式正确
- [x] 标题层级正确
- [x] 代码块语法正确

**实现**：
```python
def validate_skill_format(skill_path):
    errors = []
    
    # 检查 SKILL.md 存在
    if not os.path.exists(os.path.join(skill_path, "SKILL.md")):
        errors.append("SKILL.md not found")
        return False, errors
    
    # 读取 SKILL.md
    with open(os.path.join(skill_path, "SKILL.md"), "r") as f:
        content = f.read()
    
    # 检查 Markdown 格式
    try:
        import markdown
        markdown.markdown(content)
    except Exception as e:
        errors.append(f"Invalid Markdown: {e}")
        return False, errors
    
    # 检查标题层级
    if not re.search(r'^#\s+', content, re.MULTILINE):
        errors.append("Missing H1 title")
    
    # 检查代码块语法
    code_blocks = re.findall(r'```(\w+)', content)
    for lang in code_blocks:
        if lang not in ["python", "bash", "javascript", "yaml", "json"]:
            errors.append(f"Unknown code language: {lang}")
    
    return True, errors
```

---

### 验证 2：内容验证

**检查项**：
- [x] 功能描述完整
- [x] 使用方法清晰
- [x] 技术实现说明完整
- [x] 作者信息正确

**实现**：
```python
def validate_skill_content(skill_path):
    errors = []
    
    # 读取 SKILL.md
    with open(os.path.join(skill_path, "SKILL.md"), "r") as f:
        content = f.read()
    
    # 检查功能描述
    if not re.search(r'## 功能描述', content, re.IGNORECASE):
        errors.append("Missing 功能描述 section")
    
    # 检查使用方法
    if not re.search(r'## 使用方法', content, re.IGNORECASE):
        errors.append("Missing 使用方法 section")
    
    # 检查技术实现
    if not re.search(r'## 技术实现', content, re.IGNORECASE):
        errors.append("Missing 技术实现 section")
    
    # 检查作者
    if not re.search(r'## 作者', content, re.IGNORECASE):
        errors.append("Missing 作者 section")
    
    return True, errors
```

---

### 验证 3：功能测试

**测试项**：
- [x] 技能可加载
- [x] 技能可执行
- [x] 输出结果正确
- [x] 无错误和异常

**实现**：
```python
def test_skill_functionality(skill_path):
    errors = []
    
    # 加载技能
    try:
        skill = load_skill(skill_path)
    except Exception as e:
        errors.append(f"Failed to load skill: {e}")
        return False, errors
    
    # 测试技能执行
    try:
        result = execute_skill(skill, test_input="test")
        if not result or "error" in str(result).lower():
            errors.append(f"Skill execution failed: {result}")
    except Exception as e:
        errors.append(f"Skill execution error: {e}")
        return False, errors
    
    return True, errors
```

---

## 4.6.4 发布与版本管理

### 发布流程

**步骤 1：准备发布包**

```python
def prepare_release_package(skill_path, version):
    # 创建发布目录
    release_dir = f"{skill_path}/releases/v{version}"
    os.makedirs(release_dir, exist_ok=True)
    
    # 打包文件
    import shutil
    shutil.copytree(skill_path, f"{release_dir}/skill-name")
    
    # 创建压缩包
    import zipfile
    with zipfile.ZipFile(f"{release_dir}/skill-v{version}.zip", "w") as zipf:
        for root, dirs, files in os.walk(f"{release_dir}/skill-name"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, release_dir)
                zipf.write(file_path, arcname)
    
    return release_dir
```

---

**步骤 2：发布到 ClawdHub**

```python
def publish_to_clawdhub(skill_path, version):
    # 加载 ClawdHub token
    import os
    clawdhub_token = os.environ.get("CLAWDHUB_TOKEN")
    
    # 发布到 ClawdHub
    import subprocess
    result = subprocess.run([
        "clawdhub", "publish",
        "--token", clawdhub_token,
        "--skill", skill_path,
        "--version", version,
        "--registry", "https://www.clawhub.ai/api"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Publish failed: {result.stderr}")
    
    return True
```

---

### 版本管理

**版本号规则**：`MAJOR.MINOR.PATCH`

- **MAJOR**：不兼容的 API 变更
- **MINOR**：向后兼容的功能新增
- **PATCH**：向后兼容的问题修正

**示例**：
- `1.0.0`：初始发布
- `1.1.0`：新增功能
- `1.1.1`：bug 修复
- `2.0.0`：重大变更

---

**版本历史记录**：

```json
{
  "skill_name": "Prompt: PRD Generator",
  "versions": [
    {
      "version": "1.0.0",
      "release_date": "2026-02-05T00:00:00Z",
      "changes": [
        "初始发布",
        "支持基本 PRD 生成"
      ]
    },
    {
      "version": "1.1.0",
      "release_date": "2026-02-10T00:00:00Z",
      "changes": [
        "新增用户画像功能",
        "优化输出格式",
        "添加更多示例"
      ]
    }
  ]
}
```

---

## Layer 6 技术实现

### 技术栈

- **Python**：主要编程语言
- **ClawdHub CLI**：发布工具
- **Git**：版本管理
- **Zipfile**：打包工具

### 核心脚本

**主脚本**：`/root/clawd/skills/ai-prompt-workflow/scripts/convert-to-skill.py`

**功能**：
- 读取高质量内容
- 选择合适的 Skill 模板
- 转换内容为 Skill 格式
- 验证和测试
- 发布到 ClawdHub

**使用方法**：
```bash
# 转换所有高质量内容
python3 convert-to-skill.py --input /root/clawd/data/prompts/enhanced/

# 转换单个内容
python3 convert-to-skill.py --content "..." --type Prompt --score 75

# 测试模式
python3 convert-to-skill.py --test-mode
```

### 配置文件

**配置文件**：`/root/clawd/config/skill-conversion.yaml`

**示例**：
```yaml
skill_templates:
  prompt: /root/clawd/templates/prompt-skill-template.md
  workflow: /root/clawd/templates/workflow-skill-template.md
  industry: /root/clawd/templates/industry-skill-template.md
  guide: /root/clawd/templates/guide-skill-template.md

conversion_rules:
  content_type_mapping:
    Prompt: prompt
    Workflow: workflow
    "Industry Knowledge": industry
    Guide: guide
    
  format_rules:
    use_markdown: true
    standardize_headers: true
    add_quality_mark: true

validation:
  format_check: true
  content_check: true
  functionality_test: true

publishing:
  clawdhub_registry: https://www.clawhub.ai/api
  version_strategy: semantic  # MAJOR.MINOR.PATCH
  auto_publish: true
  create_release_package: true
```

---

## Layer 6 监控指标

| 指标 | 定义 | 目标值 | 测量周期 |
|------|------|--------|----------|
| 转换成功率 | 成功转换并发布的比例 | ≥ 95% | 每天 |
| 格式验证通过率 | 通过格式验证的比例 | 100% | 每天 |
| 内容验证通过率 | 通过内容验证的比例 | ≥ 98% | 每天 |
| 功能测试通过率 | 通过功能测试的比例 | ≥ 95% | 每天 |
| 发布成功率 | 成功发布到 ClawdHub 的比例 | ≥ 90% | 每天 |
| 技能下载量 | 已发布技能的总下载量 | 1000+/月 | 每月 |

---

## Layer 6 错误处理

### 错误分类

| 错误类型 | 描述 | 处理策略 |
|---------|------|----------|
| 模板选择失败 | 无法选择合适的模板 | 使用通用模板，人工审核 |
| 转换失败 | 内容转换失败 | 记录错误，跳过该条目 |
| 验证失败 | 验证不通过 | 修正内容，重新验证 |
| 发布失败 | 发布到 ClawdHub 失败 | 重试 3 次，失败则人工发布 |

---

## Layer 6 持续优化

### 模板优化

**定期优化**（每周）：
1. 收集用户反馈
2. 分析技能下载量
3. 优化模板设计
4. 测试新模板

### 发布流程优化

**定期优化**（每周）：
1. 分析发布成功率
2. 优化发布脚本
3. 提高发布速度

---

**Layer 6: Skill 转换层 - 完成时间：2026-02-05 07:25**

# 第二部分：整体架构

## 2.1 系统架构图

### 2.1.1 漏斗模型总览

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI 提示词自动化漏斗模型                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: 数据收集层 (Data Collection Layer)                      │
│  ├─ 数据源接入 (Web APIs, 文件, 数据库)                            │
│  ├─ 数据采集调度 (定时触发, 实时推送)                              │
│  ├─ 原始数据存储                                                  │
│  └─ 数据预处理与清洗                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: 自动分类层 (Auto Classification Layer)                  │
│  ├─ Prompt/Workflow/Industry/Guide 分类                          │
│  ├─ 特征提取 (NLP, 规则匹配, 模式识别)                             │
│  ├─ 分类模型推理 (ML 模型, 规则引擎)                              │
│  └─ 分类结果存储与索引                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: 分类评分层 (Classification Scoring Layer)              │
│  ├─ 相关性评分                                                    │
│  ├─ 质量评分 (清晰度, 完整性, 实用性)                             │
│  ├─ 创新性评分                                                    │
│  └─ 综合评分计算                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: 质量筛选层 (Quality Filtering Layer)                   │
│  ├─ 评分阈值筛选                                                  │
│  ├─ 重复内容去重                                                  │
│  ├─ 不合规内容过滤                                                │
│  └─ 人工审核队列                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5: 内容补充层 (Content Enhancement Layer)                 │
│  ├─ 元数据提取与补充                                              │
│  ├─ 标签生成 (自动标签, 手动标签)                                 │
│  ├─ 示例添加                                                      │
│  └─ 格式标准化                                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 6: Skill 转换层 (Skill Transformation Layer)             │
│  ├─ Skill 模板匹配                                                │
│  ├─ 参数映射与转换                                                │
│  ├─ Skill 文件生成                                                │
│  └─ 发布到 ClawdHub                                              │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1.2 数据流图

```mermaid
graph LR
    A[数据源] --> B[Layer 1: 数据收集]
    B --> C[Layer 2: 自动分类]
    C --> D[Layer 3: 分类评分]
    D --> E[Layer 4: 质量筛选]
    E --> F[Layer 5: 内容补充]
    F --> G[Layer 6: Skill 转换]
    G --> H[ClawdHub]

    style A fill:#e1f5e1
    style B fill:#fff4e1
    style C fill:#e1f0ff
    style D fill:#f0e1ff
    style E fill:#ffe1f0
    style F fill:#e1ffff
    style G fill:#ffffe1
    style H fill:#f5f5f5
```

### 2.1.3 系统组件图

```
┌─────────────────────────────────────────────────────────────────┐
│                        外部系统                               │
├─────────────────────────────────────────────────────────────────┤
│  GitHub API  │  Reddit API  │  Twitter API  │  Hacker News  │
│  SearXNG     │  HuggingFace │  Claude API   │  ClawdHub API │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AI 提示词自动化系统                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Layer 1      │  │ Layer 2      │  │ Layer 3      │        │
│  │ 数据收集      │  │ 自动分类      │  │ 分类评分      │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│         │                 │                 │                  │
│         └─────────────────┼─────────────────┘                  │
│                           │                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Layer 4      │  │ Layer 5      │  │ Layer 6      │        │
│  │ 质量筛选      │  │ 内容补充      │  │ Skill 转换   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│         │                 │                 │                  │
│         └─────────────────┼─────────────────┘                  │
│                           │                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ 数据存储      │  │ 消息队列      │  │ 监控告警      │        │
│  │ JSONL/SQLite│  │ Redis/RabbitMQ│  │ Prometheus   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        内部系统                               │
├─────────────────────────────────────────────────────────────────┤
│  OpenClaw    │  Memory Manager  │  Cron Scheduler  │  Scripts │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2.2 技术栈选型

### 编程语言与框架

| 组件 | 技术选型 | 原因 |
|------|---------|------|
| **主要语言** | Python 3.12+ | 生态丰富，易维护 |
| **Web 框架** | FastAPI | 高性能，异步支持 |
| **任务调度** | APScheduler | 灵活，易配置 |
| **数据处理** | Pandas | 强大的数据分析能力 |
| **NLP 处理** | spaCy, NLTK | 成熟的开源库 |
| **机器学习** | scikit-learn | 易用，性能好 |
| **LLM 集成** | Claude API | 理解能力强 |

---

### 数据存储方案

| 数据类型 | 存储方案 | 原因 |
|---------|---------|------|
| **原始数据** | JSONL | 易读写，易解析 |
| **结构化数据** | SQLite | 轻量，无需额外服务 |
| **缓存** | Redis | 高性能，支持过期 |
| **备份** | 文件系统 | 简单，可靠 |

**存储结构**：
```
/root/clawd/data/prompts/
├── collected/           # 原始数据
│   ├── prompts-2026-02-01.jsonl
│   └── prompts-2026-02-02.jsonl
├── classified/          # 分类结果
│   ├── classified-2026-02-01.jsonl
│   └── classified-2026-02-02.jsonl
├── scored/              # 评分结果
│   ├── scored-2026-02-01.jsonl
│   └── scored-2026-02-02.jsonl
├── filtered/            # 筛选结果
│   ├── filtered-2026-02-01.jsonl
│   └── filtered-2026-02-02.jsonl
├── enhanced/            # 补充结果
│   ├── enhanced-2026-02-01.jsonl
│   └── enhanced-2026-02-02.jsonl
└── converted/           # 转换结果
    ├── converted-2026-02-01.jsonl
    └── converted-2026-02-02.jsonl
```

---

### AI/ML 模型选择

| 功能 | 模型 | 原因 |
|------|------|------|
| **分类模型** | Claude 3.5 Sonnet | 理解能力强，支持对话 |
| **评分模型** | Claude 3.5 Sonnet | 评分准确，支持解释 |
| **去重模型** | Sentence-Transformers (all-MiniLM-L6-v2) | 速度快，效果好 |
| **内容生成** | Claude 3.5 Sonnet | 生成质量高 |

---

### 任务调度系统

| 功能 | 技术选型 | 原因 |
|------|---------|------|
| **定时任务** | APScheduler | 易配置，支持 Cron |
| **任务队列** | Redis Queue | 简单，可靠 |
| **任务监控** | 内置日志 | 易调试，易追踪 |

---

### 消息队列与事件总线

| 功能 | 技术选型 | 原因 |
|------|---------|------|
| **消息队列** | Redis Queue | 简单，无需额外服务 |
| **事件发布** | Redis Pub/Sub | 实时，可靠 |
| **任务协调** | 内部协调 | 简单，可控 |

---

### 部署与容器化方案

| 组件 | 技术选型 | 原因 |
|------|---------|------|
| **容器化** | Docker | 隔离，易部署 |
| **编排** | Docker Compose | 简单，易配置 |
| **服务管理** | systemd | 标准，可靠 |
| **日志** | 日志文件 + rsyslog | 简单，易查询 |
| **监控** | 内置监控 + 日志分析 | 实时，可追溯 |

---

## 2.3 设计原则

### 1. 模块化与解耦

**原则**：每个层独立，职责单一

**实现**：
- 层与层之间通过数据流通信
- 每层有独立的输入输出
- 易于测试和维护

---

### 2. 可扩展性

**原则**：易于扩展新功能

**实现**：
- 插件化数据源
- 可配置的评分标准
- 可扩展的 Skill 模板
- 易于添加新的内容类型

---

### 3. 可维护性

**原则**：代码清晰，易维护

**实现**：
- 清晰的目录结构
- 统一的代码风格
- 完善的文档和注释
- 完善的日志和错误处理

---

### 4. 数据质量优先

**原则**：质量重于数量

**实现**：
- 多维度评分
- 严格的质量筛选
- 人工审核兜底
- 持续优化评分标准

---

### 5. 自动化优先

**原则**：尽可能自动化

**实现**：
- 全自动采集
- 自动分类和评分
- 自动内容补充
- 自动转换和发布

---

### 6. 人工审核兜底

**原则**：自动化有极限，人工兜底

**实现**：
- 低置信度内容人工审核
- 阈值边缘内容人工审核
- 不确定内容人工审核
- 审核结果反馈优化

---

## 2.4 数据流设计

### 数据流总览

```
数据源 → Layer 1 → Layer 2 → Layer 3 → Layer 4 → Layer 5 → Layer 6 → ClawdHub
```

### 详细数据流

**Step 1：数据采集**（Layer 1）
```
GitHub API → 采集 → 存储 (JSONL)
Reddit API → 采集 → 存储 (JSONL)
Twitter API → 采集 → 存储 (JSONL)
SearXNG → 采集 → 存储 (JSONL)
```

**Step 2：自动分类**（Layer 2）
```
读取 (JSONL) → 特征提取 → 规则分类 → LLM 分类 → 输出 (JSONL)
```

**Step 3：分类评分**（Layer 3）
```
读取 (JSONL) → 根据类型评分 → 计算总分 → 输出 (JSONL)
```

**Step 4：质量筛选**（Layer 4）
```
读取 (JSONL) → 阈值筛选 → 去重筛选 → 合规筛选 → 输出 (JSONL)
```

**Step 5：内容补充**（Layer 5）
```
读取 (JSONL) → 识别缺失 → 联网补充 → LLM 生成 → 输出 (JSONL)
```

**Step 6：Skill 转换**（Layer 6）
```
读取 (JSONL) → 选择模板 → 转换内容 → 验证 → 发布 → ClawdHub
```

---

### 数据格式

**原始数据格式**（Layer 1 输出）：
```json
{
  "id": "github_001",
  "title": "Awesome ChatGPT Prompts",
  "content": "内容...",
  "type": "auto-detect",
  "source": "github",
  "url": "https://github.com/f/awesome-chatgpt-prompts",
  "metadata": {},
  "collected_at": "2026-02-05T00:00:00Z"
}
```

**分类数据格式**（Layer 2 输出）：
```json
{
  "id": "github_001",
  "title": "Awesome ChatGPT Prompts",
  "content": "内容...",
  "type": "Guide",
  "classification_confidence": 0.92,
  "classification_reason": "包含系统性指导和方法论",
  "source": "github",
  "classified_at": "2026-02-05T00:00:00Z"
}
```

**评分数据格式**（Layer 3 输出）：
```json
{
  "id": "github_001",
  "title": "Awesome ChatGPT Prompts",
  "content": "内容...",
  "type": "Guide",
  "scores": {
    "指导性": 35,
    "结构性": 25,
    "实用性": 25
  },
  "total_score": 85,
  "scoring_reason": "指导性强，结构清晰，实用性高",
  "scored_at": "2026-02-05T00:00:00Z"
}
```

**筛选数据格式**（Layer 4 输出）：
```json
{
  "id": "github_001",
  "title": "Awesome ChatGPT Prompts",
  "content": "内容...",
  "type": "Guide",
  "total_score": 85,
  "quality_level": "high",
  "filter_reason": "评分 ≥ 70",
  "filtered_at": "2026-02-05T00:00:00Z"
}
```

**补充数据格式**（Layer 5 输出）：
```json
{
  "id": "github_001",
  "title": "Awesome ChatGPT Prompts",
  "content": "内容...（已补充）",
  "type": "Guide",
  "total_score": 85,
  "enhanced_score": 88,
  "missing_info": ["案例研究"],
  "enhanced_fields": ["案例研究"],
  "enhanced_at": "2026-02-05T00:00:00Z"
}
```

**转换数据格式**（Layer 6 输出）：
```json
{
  "id": "github_001",
  "title": "Awesome ChatGPT Prompts",
  "content": "内容...",
  "type": "Guide",
  "total_score": 88,
  "skill_name": "Guide: ChatGPT Prompt Collection",
  "skill_version": "1.0.0",
  "skill_path": "/root/clawd/skills/chatgpt-prompt-collection/",
  "published": true,
  "clawdhub_url": "https://www.clawhub.ai/skills/chatgpt-prompt-collection",
  "converted_at": "2026-02-05T00:00:00Z"
}
```

---

**第二部分：整体架构 - 完成时间：2026-02-05 07:30**

# 第五部分：系统集成与部署

## 5.1 系统集成方案

### 与 OpenClaw 集成

**集成方式**：作为 OpenClaw 的 skill

**目录结构**：
```
/root/clawd/skills/ai-prompt-workflow/
├── SKILL.md                        # Skill 文档
├── scripts/                        # 脚本目录
│   ├── collect-prompts.py          # 数据收集
│   ├── classify-content.py          # 自动分类
│   ├── score-content.py             # 分类评分
│   ├── filter-quality.py           # 质量筛选
│   ├── enhance-content.py           # 内容补充
│   └── convert-to-skill.py        # Skill 转换
├── config/                         # 配置目录
│   ├── prompts-collector.yaml       # 数据收集配置
│   ├── classification.yaml           # 分类配置
│   ├── scoring-standards.yaml       # 评分标准配置
│   ├── quality-filter.yaml          # 质量筛选配置
│   ├── content-enhancement.yaml     # 内容补充配置
│   └── skill-conversion.yaml      # Skill 转换配置
└── templates/                      # 模板目录
    ├── prompt-skill-template.md
    ├── workflow-skill-template.md
    ├── industry-skill-template.md
    └── guide-skill-template.md
```

**集成配置**：
```yaml
# /root/clawd/skills/ai-prompt-workflow/metadata.yaml
name: ai-prompt-workflow
version: 1.0.0
description: AI 提示词自动化漏斗模型
author: Momo (Clawdbot Team)
primaryEnv:
  CLAUDE_API_KEY: "Claude API 密钥"
  CLAWDHUB_TOKEN: "ClawdHub Token"
triggers:
  - "收集提示词"
  - "分析提示词"
  - "转换提示词"
```

---

### 与 Memory Manager 集成

**集成方式**：使用 memory-manager 记忆

**使用场景**：
- 记录处理结果
- 记录错误和异常
- 记录优化建议

**实现**：
```python
from memory_manager import memorize

# 记录处理结果
memorize(
    "今日收集了 500 个提示词，转换为 50 个 Skill，发布到 ClawdHub",
    "general"
)

# 记录错误
memorize(
    "分类模型 API 失败，降级到规则分类",
    "debugging"
)
```

---

### 与 Cron 集成

**集成方式**：使用 cron 定时任务

**Cron 配置**：
```bash
# /etc/cron.d/clawdbot-ai-prompt-workflow

# 数据收集（每天凌晨 2 点）
0 2 * * * root cd /root/clawd && python3 /root/clawd/skills/ai-prompt-workflow/scripts/collect-prompts.py >> /root/clawd/logs/collect-prompts.log 2>&1

# 自动分类（每天凌晨 3 点）
0 3 * * * root cd /root/clawd && python3 /root/clawd/skills/ai-prompt-workflow/scripts/classify-content.py >> /root/clawd/logs/classify-content.log 2>&1

# 分类评分（每天凌晨 4 点）
0 4 * * * root cd /root/clawd && python3 /root/clawd/skills/ai-prompt-workflow/scripts/score-content.py >> /root/clawd/logs/score-content.log 2>&1

# 质量筛选（每天凌晨 5 点）
0 5 * * * root cd /root/clawd && python3 /root/clawd/skills/ai-prompt-workflow/scripts/filter-quality.py >> /root/clawd/logs/filter-quality.log 2>&1

# 内容补充（每天凌晨 6 点）
0 6 * * * root cd /root/clawd && python3 /root/clawd/skills/ai-prompt-workflow/scripts/enhance-content.py >> /root/clawd/logs/enhance-content.log 2>&1

# Skill 转换（每天凌晨 7 点）
0 7 * * * root cd /root/clawd && python3 /root/clawd/skills/ai-prompt-workflow/scripts/convert-to-skill.py >> /root/clawd/logs/convert-to-skill.log 2>&1
```

---

## 5.2 部署架构

### 部署环境

**环境要求**：
- OS: Linux (Ubuntu 20.04+ / CentOS 7+)
- Python: 3.12+
- 内存: ≥ 4GB
- 存储: ≥ 100GB

---

### 部署步骤

**Step 1：安装依赖**

```bash
# 安装 Python 依赖
pip3 install -r requirements.txt

# 安装系统依赖
apt-get install -y git curl wget redis-server
```

---

**Step 2：配置环境变量**

```bash
# /root/clawd/.env
export CLAUDE_API_KEY="your-claude-api-key"
export CLAWDHUB_TOKEN="your-clawdhub-token"
export CLAWDHUB_REGISTRY="https://www.clawhub.ai/api"
export SEARXNG_URL="http://localhost:8080"
```

---

**Step 3：初始化数据存储**

```bash
# 创建数据目录
mkdir -p /root/clawd/data/prompts/{collected,classified,scored,filtered,enhanced,converted}
mkdir -p /root/clawd/logs
mkdir -p /root/clawd/memory/backups
```

---

**Step 4：配置 Cron 任务**

```bash
# 复制 Cron 配置
cp /root/clawd/skills/ai-prompt-workflow/config/crontab /etc/cron.d/clawdbot-ai-prompt-workflow

# 重启 Cron
systemctl restart cron
```

---

**Step 5：验证部署**

```bash
# 测试数据收集
python3 /root/clawd/skills/ai-prompt-workflow/scripts/collect-prompts.py --test-mode

# 测试自动分类
python3 /root/clawd/skills/ai-prompt-workflow/scripts/classify-content.py --test-mode

# 测试分类评分
python3 /root/clawd/skills/ai-prompt-workflow/scripts/score-content.py --test-mode

# 测试质量筛选
python3 /root/clawd/skills/ai-prompt-workflow/scripts/filter-quality.py --test-mode

# 测试内容补充
python3 /root/clawd/skills/ai-prompt-workflow/scripts/enhance-content.py --test-mode

# 测试 Skill 转换
python3 /root/clawd/skills/ai-prompt-workflow/scripts/convert-to-skill.py --test-mode
```

---

## 5.3 监控与告警

### 监控指标

**系统级指标**：
- CPU 使用率
- 内存使用率
- 磁盘使用率
- 网络流量

**业务级指标**：
- 每日收集数量
- 分类准确率
- 评分分布
- 筛选通过率
- 转换成功率
- 发布成功率

**实现**：
```python
# /root/clawd/skills/ai-prompt-workflow/scripts/monitor.py

def collect_metrics():
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent
        },
        "business": {
            "daily_collected": count_daily_collected(),
            "classification_accuracy": calculate_classification_accuracy(),
            "score_distribution": calculate_score_distribution(),
            "filter_pass_rate": calculate_filter_pass_rate(),
            "conversion_success_rate": calculate_conversion_success_rate(),
            "publish_success_rate": calculate_publish_success_rate()
        }
    }
    
    return metrics

def save_metrics(metrics):
    with open("/root/clawd/data/metrics.jsonl", "a") as f:
        f.write(json.dumps(metrics) + "\n")
```

---

### 告警规则

**告警规则**：
1. **CPU 使用率 > 80%**：持续 5 分钟
2. **内存使用率 > 90%**：持续 5 分钟
3. **磁盘使用率 > 90%**：持续 5 分钟
4. **API 调用失败率 > 10%**：持续 10 分钟
5. **转换成功率 < 90%**：持续 1 小时

**实现**：
```python
def check_alerts(metrics):
    alerts = []
    
    # CPU 告警
    if metrics["system"]["cpu"] > 80:
        alerts.append({
            "level": "WARNING",
            "message": f"CPU 使用率过高: {metrics['system']['cpu']}%"
        })
    
    # 内存告警
    if metrics["system"]["memory"] > 90:
        alerts.append({
            "level": "CRITICAL",
            "message": f"内存使用率过高: {metrics['system']['memory']}%"
        })
    
    # 磁盘告警
    if metrics["system"]["disk"] > 90:
        alerts.append({
            "level": "CRITICAL",
            "message": f"磁盘使用率过高: {metrics['system']['disk']}%"
        })
    
    # 业务告警
    if metrics["business"]["conversion_success_rate"] < 0.9:
        alerts.append({
            "level": "WARNING",
            "message": f"转换成功率过低: {metrics['business']['conversion_success_rate'] * 100}%"
        })
    
    return alerts

def send_alerts(alerts):
    for alert in alerts:
        send_to_slack(alert["message"], level=alert["level"])
        send_to_feishu(alert["message"], level=alert["level"])
```

---

## 5.4 扩展性与维护

### 扩展性

**水平扩展**：
- 多实例部署
- 负载均衡
- 分布式任务队列

**垂直扩展**：
- 增加服务器配置
- 优化代码性能
- 使用缓存

---

### 维护策略

**日常维护**：
- 检查日志
- 监控指标
- 备份数据
- 更新依赖

**周常维护**：
- 分析性能
- 优化配置
- 更新模型
- 清理缓存

**月常维护**：
- 评估整体效果
- 调整评分标准
- 优化算法
- 规划新功能

---

# 第六部分：附录

## 附录A：术语表

| 术语 | 英文 | 定义 |
|------|------|------|
| 提示词 | Prompt | 可直接用于 AI 模型的单个或一组指令 |
| 工作流 | Workflow | 多步骤的执行流程，通常需要联网或工具调用 |
| 行业经验 | Industry Knowledge | 特定领域的专业知识和经验总结 |
| 指南 | Guide/Best Practice | 理论框架、方法论、系统性指导 |
| 技能 | Skill | Clawdbot 的功能单元，可以被用户调用 |
| 漏斗模型 | Funnel Model | 多层筛选和处理的数据处理流水线 |
| 分类 | Classification | 将内容分类为不同类型的过程 |
| 评分 | Scoring | 对内容质量进行评估的过程 |
| 筛选 | Filtering | 根据评分结果筛选内容的过程 |
| 补充 | Enhancement | 补充缺失信息，提升内容质量的过程 |
| 转换 | Transformation | 将内容转换为 Skill 格式的过程 |
| ClawdHub | ClawdHub | Clawdbot 的技能发布和分发平台 |

---

## 附录B：参考资料

**技术文档**：
- Claude API 文档: https://docs.anthropic.com
- OpenAI API 文档: https://platform.openai.com
- SearXNG 文档: https://docs.searxng.org
- ClawdHub API 文档: https://www.clawhub.ai/api/docs

**学术论文**：
- Prompt Engineering 论文: https://arxiv.org/abs/2101.00103
- Language Model 论文: https://arxiv.org/abs/1706.03762

**开源项目**：
- awesome-chatgpt-prompts: https://github.com/f/awesome-chatgpt-prompts
- prompt-engineering-guide: https://github.com/dair-ai/Prompt-Engineering-Guide

---

## 附录C：配置示例

### 数据收集配置

```yaml
# /root/clawd/config/prompts-collector.yaml

data_sources:
  github:
    enabled: true
    frequency: daily
    repos:
      - f/awesome-chatgpt-prompts
      - dair-ai/Prompt-Engineering-Guide
      
  reddit:
    enabled: true
    frequency: "6h"
    subreddits:
      - ChatGPT
      - ChatGPTcoding
      
  searxng:
    enabled: true
    frequency: daily
    keywords:
      - "ChatGPT prompt"
      - "prompt engineering"

deduplication:
  md5_enabled: true
  semantic_enabled: true
  semantic_threshold: 0.95
  embedding_model: all-MiniLM-L6-v2

storage:
  data_dir: /root/clawd/data/prompts/collected
  file_format: jsonl
  max_file_size: 100MB
```

---

### 分类配置

```yaml
# /root/clawd/config/classification.yaml

classification_model:
  type: llm
  model: claude-3-5-sonnet
  confidence_threshold: 0.7

content_types:
  Prompt:
    keywords: ["请", "生成", "你是一个", "扮演"]
  Workflow:
    keywords: ["步骤", "流程", "然后", "最后"]
  Industry:
    keywords: ["经验", "最佳实践", "优化", "性能"]
  Guide:
    keywords: ["指南", "教程", "方法", "原则"]

classification_rules:
  priority:
    - rules
    - keywords
    - llm
    
  rules:
    - condition: "你是一个.*请.*"
      type: "Prompt"
      confidence: 0.95
```

---

### 评分标准配置

```yaml
# /root/clawd/config/scoring-standards.yaml

content_types:
  Prompt:
    dimensions:
      - name: 实用性
        weight: 0.5
        high_score: [40, 50]
        medium_score: [30, 39]
        low_score: [0, 29]
      - name: 清晰度
        weight: 0.3
        high_score: [24, 30]
        medium_score: [18, 23]
        low_score: [0, 17]
      - name: 独特性
        weight: 0.2
        high_score: [16, 20]
        medium_score: [12, 15]
        low_score: [0, 11]
    thresholds:
      high: 70
      medium: 50
      
  Workflow:
    dimensions:
      - name: 完整性
        weight: 0.3
        high_score: [24, 30]
        medium_score: [18, 23]
        low_score: [0, 17]
      - name: 可扩展性
        weight: 0.2
        high_score: [16, 20]
        medium_score: [12, 15]
        low_score: [0, 11]
      - name: 实用性
        weight: 0.3
        high_score: [24, 30]
        medium_score: [18, 23]
        low_score: [0, 17]
      - name: 可复用性
        weight: 0.2
        high_score: [16, 20]
        medium_score: [12, 15]
        low_score: [0, 11]
    thresholds:
      high: 65
      medium: 45
```

---

## 附录D：最佳实践

### 开发最佳实践

1. **代码风格**：遵循 PEP 8
2. **文档**：完善代码注释和文档
3. **错误处理**：完善的错误处理和日志
4. **测试**：编写单元测试和集成测试
5. **版本控制**：使用 Git 管理版本

---

### 部署最佳实践

1. **环境隔离**：使用虚拟环境
2. **配置管理**：使用配置文件
3. **日志管理**：完善的日志记录
4. **监控告警**：实时监控和告警
5. **备份恢复**：定期备份和恢复测试

---

### 运维最佳实践

1. **性能优化**：定期优化性能
2. **安全加固**：定期更新依赖
3. **数据备份**：定期备份数据
4. **容量规划**：提前规划容量
5. **故障处理**：制定故障处理预案

---

**第五部分和第六部分 - 完成时间：2026-02-05 07:35**
