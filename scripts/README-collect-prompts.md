# AI Prompts Collector - 完整版

定期收集 AI 提示词相关信息，包括通用提示词、图像生成提示词、视频生成提示词。

## 概览

本系统集成了 **5 个数据源**，全面收集 AI 提示词：

| 数据源 | 覆盖范围 | 特色 |
|--------|---------|------|
| Reddit | 通用提示词 | 实时讨论，社区驱动 |
| GitHub | 精选提示词 | 高质量，结构化 |
| Hacker News | 技术讨论 | 深度内容，行业趋势 |
| SearXNG | 通用搜索 | 按需搜索，无限制 |
| **Visual AI** ⭐ | **生图+生视频** | **商业价值高，热门方向** |

## 快速开始

### 方式 1: 完整收集（推荐）

收集所有数据源，包括最新的 Visual AI 提示词：

```bash
cd /root/clawd/scripts
./collect-all-visual-ai.sh
```

**输出**:
- 所有数据源的最新提示词
- Visual AI 专用摘要报告
- 完整的收集报告

### 方式 2: 单独收集 Visual AI

只收集图像和视频生成提示词：

```bash
cd /root/clawd/scripts
python3 collect-visual-ai-prompts.py
```

**输出**:
- Midjourney、DALL-E 3、Stable Diffusion 提示词
- Veo、Kling、Runway、Pika 视频生成提示词
- 自动分类和质量评分
- Visual AI 摘要报告

### 方式 3: 旧版收集（仅通用提示词）

```bash
cd /root/clawd/scripts
./collect-all-sources-prompts.sh
```

## Visual AI 提示词收集 ⭐ NEW

### 覆盖平台

**图像生成**:
- Midjourney - 专业图像生成
- DALL-E 3 - 商业化程度高
- Stable Diffusion - 开源生态

**视频生成**:
- Veo - Google AI 视频
- Kling AI - 专业视频生成
- Runway - 创意视频工具
- Pika Labs - 轻量级视频生成

### 收集内容

1. **平台最佳实践** - 各平台的提示词技巧
2. **参数详解** - `--style`, `--ar`, `--no` 等参数使用
3. **风格模板** - 各种艺术风格的提示词
4. **行业应用** - 产品摄影、角色设计、游戏资产等
5. **视频提示** - 动画、转场、镜头运动等

### 数据结构

```json
{
  "type": "visual_ai_prompts",
  "timestamp": "2026-01-30T...",
  "total_results": 25,
  "total_prompts_extracted": 156,
  "image_prompts_count": 120,
  "video_prompts_count": 36,
  "data": {
    "midjourney": { ... },
    "dalle": { ... },
    "stable_diffusion": { ... },
    "video_generation": { ... },
    "artistic_styles": { ... }
  }
}
```

### 提示词分类

系统会自动分类提取的提示词：

- **类型**: 图像 / 视频 / 通用
- **风格**: 现实主义 / 艺术 / 动漫 / 3D / 电影感
- **平台**: Midjourney / DALL-E / Stable Diffusion / Veo / Kling / Runway / Pika
- **质量分数**: 0-100 评分

### 质量评分算法

基于多个维度计算质量分数：

- 标题质量（包含关键词）
- 片段丰富度（长度、内容）
- 来源权威性（GitHub、Reddit、YouTube 等）
- 参数引用（`--style`, `--ar` 等）
- 提示词示例（有具体例子）

高质量阈值: **≥70分**

## 数据文件位置

### Visual AI 数据
- `/root/clawd/data/prompts/visual-ai-prompts.jsonl` - 原始数据
- `/root/clawd/data/prompts/visual-ai-summary-YYYY-MM-DD.md` - 每日摘要

### 通用提示词数据
- `/root/clawd/data/prompts/reddit-prompts.jsonl` - Reddit 数据
- `/root/clawd/data/prompts/github-awesome-prompts.jsonl` - GitHub 数据
- `/root/clawd/data/prompts/hacker-news-ai.jsonl` - Hacker News 数据
- `/root/clawd/data/prompts/collected.jsonl` - SearXNG 数据

### 报告
- `/root/clawd/reports/all-visual-ai-report-YYYY-MM-DD-HHMM.md` - 完整报告

## 定时任务（可选）

### 每日自动收集（推荐）

编辑 crontab：

```bash
crontab -e
```

添加以下行之一：

**完整收集（推荐）**:
```
0 9 * * * cd /root/clawd/scripts && ./collect-all-visual-ai.sh >> /root/clawd/data/prompts/all-visual-ai-collection.log 2>&1
```

**仅 Visual AI**:
```
0 10 * * * cd /root/clawd/scripts && python3 collect-visual-ai-prompts.py >> /root/clawd/data/prompts/visual-ai-collection.log 2>&1
```

### 每日多次收集

例如，每天 9:00、14:00、20:00 收集：

```
0 9,14,20 * * * cd /root/clawd/scripts && python3 collect-visual-ai-prompts.py >> /root/clawd/data/prompts/visual-ai-collection.log 2>&1
```

## 商业价值 ⭐

基于收集的 Visual AI 提示词，可以创造以下商业机会：

### 1. 技能开发（ClawdHub 售卖）

**图像生成技能**:
- Midjourney 专业提示词生成器（$9.99-$29.99）
- DALL-E 3 产品展示自动化（$19.99-$49.99）
- Stable Diffusion 风格化技能（$14.99-$39.99）
- 特定行业专业技能（建筑、时尚、游戏）

**视频生成技能**:
- Veo 视频生成工作流（$24.99-$59.99）
- Kling AI 社交媒体视频自动化（$19.99-$49.99）
- 产品视频批量生成（$29.99-$69.99）
- TikTok/Reels 内容自动化（$14.99-$39.99）

**组合类技能**:
- 图像转视频完整工作流（$39.99-$89.99）
- 角色设计 + 动画生成（$49.99-$99.99）
- 产品展示一体化（图片+视频）（$34.99-$79.99）

### 2. 提示词模板服务

- **行业模板**: 建筑、时尚、游戏、电商、教育等
- **风格模板**: 摄影、绘画、动漫、3D、电影感等
- **场景模板**: 产品展示、角色设计、环境概念等

定价: $2.99-$19.99/模板包

### 3. 企业解决方案

- **批量生成**: 企业级批量图像/视频生成方案
- **定制化**: 根据品牌风格定制提示词
- **培训服务**: 提示词工程培训和认证

定价: $500-$5,000/项目

## 数据分析

### 查看最新收集数据

```bash
# Visual AI 数据
cat /root/clawd/data/prompts/visual-ai-prompts.jsonl | jq .

# 最新一条
tail -1 /root/clawd/data/prompts/visual-ai-prompts.jsonl | jq .

# 按类别统计
cat /root/clawd/data/prompts/visual-ai-prompts.jsonl | jq '.data | keys'
```

### 查看摘要报告

```bash
# 列出所有摘要
ls -lh /root/clawd/data/prompts/visual-ai-summary-*.md

# 查看最新摘要
cat /root/clawd/data/prompts/visual-ai-summary-$(date +%Y-%m-%d).md
```

### 统计提示词数量

```bash
# Visual AI 总提示词数
cat /root/clawd/data/prompts/visual-ai-prompts.jsonl | jq '[.[][][].extracted_prompts] | add | length'

# 按类型统计
cat /root/clawd/data/prompts/visual-ai-prompts.jsonl | jq '{image: .image_prompts_count, video: .video_prompts_count}'
```

### 高质量结果

```bash
# 查看质量分数 ≥70 的结果
cat /root/clawd/data/prompts/visual-ai-prompts.jsonl | jq '.data[][] | select(.results[] | .quality_score >= 70)'

# 提取高质量提示词
cat /root/clawd/data/prompts/visual-ai-prompts.jsonl | jq -r '.data[][] | .results[] | select(.quality_score >= 70) | .extracted_prompts[]' | head -20
```

## 技巧和最佳实践

### 提高收集质量

1. **定期运行**: 每天至少收集 1-2 次
2. **多时间点**: 在不同时间运行（9:00, 14:00, 20:00）
3. **持续积累**: 长期收集会积累大量有价值的数据
4. **定期分析**: 每周分析一次收集结果，识别趋势

### 数据使用

1. **提示词精选**: 从高质量结果中提取提示词
2. **技能开发**: 基于收集的提示词开发技能
3. **市场调研**: 分析热门平台和风格
4. **竞品分析**: 了解其他提示词产品的特点

### 自动化建议

1. **自动分类**: 利用收集的分类数据
2. **质量过滤**: 优先使用质量分数 ≥70 的结果
3. **去重**: 定期去重，避免重复处理
4. **备份**: 定期备份数据文件

## 故障排除

### "No module named 'xxx'"
安装缺失的 Python 模块：
```bash
pip3 install -r /root/clawd/scripts/requirements.txt
```

### "Permission denied"
添加执行权限：
```bash
chmod +x /root/clawd/scripts/*.sh
chmod +x /root/clawd/scripts/*.py
```

### "No results"
检查网络连接和搜索配置：
```bash
# 测试 clawdbot eval
clawdbot eval 'await tool("web_search", { query: "test", count: 1 })'
```

### "Git push failed"
检查 Git 配置和远程仓库：
```bash
cd /root/clawd
git remote -v
git status
```

## 更新日志

### 2026-01-30
- ⭐ **新增**: Visual AI 提示词收集功能
- ⭐ **新增**: 支持图像生成平台（Midjourney、DALL-E 3、Stable Diffusion）
- ⭐ **新增**: 支持视频生成平台（Veo、Kling、Runway、Pika）
- 🎨 **新增**: 自动提示词分类（类型、风格、平台）
- 📊 **新增**: 质量评分系统（0-100 分）
- 📄 **新增**: Visual AI 专用摘要报告
- 📦 **新增**: 完整收集脚本（5 个数据源）

## 贡献

如果有改进建议或发现问题，欢迎反馈！

## 许可证

MIT License
