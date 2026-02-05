# Clawdbot Skills - 高质量 AI 技能与信息搜集

## 项目概述

这是一个双轨项目，专注于创建高质量的 AI 技能和智能化的信息搜集解决方案。

### 核心理念

**从实战中学到的教训**：
1. **Skill ≠ 提示词** - Skill 是完整的解决方案（工具 + 脚本 + 配置 + 文档）
2. **质量 > 数量** - 20 个高质量手动创建的技能 >>> 1000 个低质量自动抓取
3. **搜索的局限性** - 关键词搜索无法理解语义，需要多策略、智能化搜索

---

## 子项目

### 1. AI 提示词 Skills（活跃）

**定位**：手动创建高质量 AI 提示词技能

**核心成果**：
- ✅ 已创建 20 个高质量 Skills
- ✅ 100% 发布成功率（20/20）
- ✅ 覆盖电商视频、Sora2、Google Veo、电商图片生成

**数据对比**：

| 方法 | 数量 | 质量 | 成功率 |
|------|------|------|--------|
| 网络搜索抓取 | 1033 条 | 8.0/100 | 0% |
| 手动创建 | 20 条 | 高质量 | 100% |

**已发布的 Skills**：

**电商视频生成**（5 个）：
- product-showcase-video（产品展示视频）
- marketing-promo-video（营销推广视频）
- social-media-story-video（社媒故事视频）
- unboxing-experience-video（开箱体验视频）
- before-after-transformation-video（前后对比视频）

**Sora2 视频**（5 个）：
- cinematic-product-film（电影级产品影片）
- animated-product-explainer（动画产品解说）
- lifestyle-scene-video（生活场景视频）
- brand-story-video（品牌故事视频）
- product-tutorial-video（产品教程视频）

**Google Veo 视频**（5 个）：
- quick-demo-video（快速演示视频）
- seasonal-campaign-video（季节活动视频）
- a-b-test-variations（A/B 测试变体）
- testimonial-montage（用户评价合集）
- product-comparison-video（产品对比视频）

**电商图片生成**（5 个）：
- product-studio-shot（产品工作室拍摄）
- lifestyle-product-shot（生活产品拍摄）
- product-detail-shot（产品细节拍摄）
- seasonal-product-image（季节产品图片）
- social-media-carousel（社媒轮播图集）

**关键成功因素**：
1. 高质量、精心设计
2. 针对市场需求
3. 可直接使用（开箱即用）
4. 完整的使用说明和示例
5. 基于真实场景

**后续计划**：
- [ ] 观察用户反馈
- [ ] 收集改进建议
- [ ] 迭代优化提示词
- [ ] 扩展更多类别（如果这些受欢迎）
- [ ] 长期目标：创建 100-200 个高质量提示词

---

### 2. 信息搜集项目（新）

**定位**：独立的信息搜集项目，整合多种搜索工具和策略

**核心能力**：
- 多策略搜索（关键词、语义、迭代）
- 智能结果处理（提取、清理、评估）
- 工作流集成（AI 研究、市场调研、社交媒体分析）

**搜索工具整合**：

#### SearXNG Search 🔍
- **用途**：隐私保护的元搜索引擎
- **场景**：AI 研究、市场调研、新闻收集、趋势追踪

#### Firecrawl Search 🔥
- **用途**：网页搜索和抓取 API
- **场景**：抓取网站（包括 JS-heavy 页面）、爬取整个站点、提取结构化数据

#### Twitter Search 🐦
- **用途**：Twitter 社交媒体搜索和数据分析
- **场景**：社交媒体趋势分析、情感分析、影响者识别、社交监听

**改进方向**：
- [ ] 语义搜索（向量搜索）
- [ ] 迭代搜索（根据结果优化）
- [ ] 智能推荐

**项目文档**：[projects/info-search/README.md](projects/info-search/README.md)

---

### 3. ~~AI 提示词自动化转换~~（已停止）

**状态**：❌ 已停止

**原因**：
- 网络搜索抓取 0% 成功率
- 公共网络上没有高质量提示词
- 搜索成本高、效果差
- 手动创建更有效

**禁用的脚本**（保留记录）：
- disabled.collect-prompts-via-searxng.py
- disabled.collect-prompts-via-firecrawl.py
- disabled.collect-all-sources-prompts-v2.sh
- disabled.auto_twitter_search.sh
- disabled.search-github-prompt-markets.py
- disabled.full-prompt-workflow.sh

**经验总结**：参见 [projects/info-search/docs/lessons.md](projects/info-search/docs/lessons.md)

---

## 项目结构

```
/root/clawd/
├── skills/                          # Skills 目录
│   ├── manual-prompts/              # 手动创建的提示词 Skills（20 个）
│   ├── searxng/                    # SearXNG 搜索技能（保留）
│   ├── firecrawl-search/            # Firecrawl 搜索技能（保留）
│   └── twitter-search-skill/        # Twitter 搜索技能（保留）
│
├── projects/                        # 子项目
│   └── info-search/                # 信息搜集项目（新）
│       ├── README.md
│       ├── docs/lessons.md
│       ├── strategies/
│       ├── processors/
│       └── workflows/
│
├── scripts/                         # 工具脚本
│   ├── create-manual-prompts.py     # 创建手动提示词
│   ├── convert-manual-prompts-to-skills.py  # 转换为 Skills
│   ├── publish-manual-skills.sh     # 发布到 ClawdHub
│   └── disabled.*.sh              # 已禁用的脚本（保留记录）
│
├── data/                           # 数据目录
│   └── manual-prompts/             # 手动提示词数据
│
└── memory/                         # 记忆和日志
    ├── 2026-02-05.md              # 每日记录
    └── ai-research/               # AI 研究数据
```

## 核心教训

### 1. Skill 不仅仅是提示词

**错误认知**：Skill = 提示词

**正确理解**：Skill = 完整的解决方案
```
Skill = 工具 + 脚本 + 配置 + 文档 + 提示词
```

### 2. 光靠提示词转换 skill 还是不够

**错误方式**：找到提示词 → 转换 → 发布

**正确方式**：理解需求 → 设计方案 → 实现工具 → 测试 → 发布

### 3. 搜索都是关键词搜索，很有可能没有涵盖所要搜索的内容

**局限性**：
- 关键词搜索无法理解语义
- 高质量提示词是商业机密，不会公开发布
- 需要语义搜索、多策略搜索、迭代搜索

**改进方向**：
- [ ] 语义搜索（向量搜索）
- [ ] 多策略搜索（关键词 + 语义）
- [ ] 迭代搜索（根据结果优化）

## 技术栈

- **Clawdbot Skills**: 技能框架
- **ClawdHub CLI**: 发布工具
- **Python**: 主要开发语言
- **SearXNG**: 隐私保护的元搜索引擎
- **Firecrawl**: 网页搜索和抓取 API
- **Twitter API**: 社交媒体搜索和数据分析
- **Mozilla Readability**: 内容提取算法

## 使用说明

### 创建手动提示词

```bash
# 1. 创建提示词
python3 /root/clawd/scripts/create-manual-prompts.py

# 2. 转换为 Skills
python3 /root/clawd/scripts/convert-manual-prompts-to-skills.py

# 3. 发布到 ClawdHub
bash /root/clawd/scripts/publish-manual-skills.sh
```

### 信息搜集

```bash
# AI 研究搜索（每天早上自动执行）
# 搜索结果保存到 memory/ai-research/

# 使用 SearXNG 搜索
uv run /root/clawd/skills/searxng/scripts/searxng.py search "query"

# 使用 Firecrawl 搜索
firecrawl_search "query" --limit 10

# 使用 Twitter 搜索
twitter_search "query" --limit 100
```

## 商业模式

1. **免费技能**: 吸引用户，建立品牌
2. **付费技能**: 高质量、专业领域技能
3. **订阅套餐**: 批量访问技能库
4. **企业定制**: 为企业开发专属技能

## 开发阶段

### AI 提示词 Skills
- [x] 手动创建 20 个高质量 Skills
- [x] 发布到 ClawdHub（100% 成功率）
- [ ] 观察用户反馈
- [ ] 收集改进建议
- [ ] 迭代优化提示词
- [ ] 扩展更多类别

### 信息搜集项目
- [x] 项目初始化
- [x] 核心文档编写
- [ ] 完成基础工作流
- [ ] 实现语义搜索
- [ ] 实现迭代搜索

### ~~AI 提示词自动化转换~~
- [x] 项目初始化
- [x] 多种搜索尝试（SearXNG、Firecrawl、GitHub、Twitter）
- [x] 验证搜索无效（0% 成功率）
- [x] 决策停止自动化转换
- [x] 转向手动创建高质量提示词

## GitHub Repository

https://github.com/hhhh124hhhh/Clawdbot-Skills-Converter

## 许可证

MIT License - 开源核心，商业变现

---

*项目更新时间：2026-02-05*
*基于实战经验：质量 > 数量，手动创建 > 自动抓取*
