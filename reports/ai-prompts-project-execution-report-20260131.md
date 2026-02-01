# AI 提示词转 Skill 项目执行报告

**日期**: 2026-01-31
**状态**: ⚠️ 需要改进
**执行时间**: 约 30 分钟

---

## 📊 执行摘要

| 方案 | 状态 | 结果 |
|------|------|------|
| SearXNG 收集脚本 | ✅ 已运行 | ❌ 数据质量极差（88% 垃圾数据） |
| Agent 评估脚本 | ⚠️ 运行中 | ❌ 技术问题（sessions_spawn 调用失败） |
| 提取质量增强 | ✅ 已实现 | ❌ 过于宽松，大量 HTML 片段 |

**核心问题**：预期效果未达成，垃圾数据比例仍高达 88%，无高质量数据。

---

## 🔍 详细分析

### 1. SearXNG 收集脚本 (`collect-prompts-via-searxng.py`)

#### ✅ 成功部分
- 脚本成功运行，执行搜索流程
- 成功连接到 SearXNG 实例 (http://149.13.91.232:8080)
- 正确执行了多个搜索查询
- 数据保存到文件：`/root/clawd/data/prompts/collected/test-prompts-20260131-152033.jsonl`

#### ❌ 失败部分

**问题 1：大量网站返回 403 错误**
```
403 Client Error: Forbidden for url:
- https://docs.midjourney.com/hc/en-us/articles/...
- https://stable-diffusion-art.com/prompt-guide/
- https://shifton.com/blog/dall-e-3/
- https://nightcafe.studio/blogs/...
- https://blog.csdn.net/weixin_48534929/article/...
```

**问题 2：提取质量极差**
- **收集总数**: 25 条提示词
- **高质量 (≥70)**: 0 条 (0%)
- **中等 (50-69)**: 3 条 (12%)
- **低质量 (<50)**: 22 条 (88%) ⚠️

**问题 3：提取的都是句子片段，不是真正的提示词**

示例分析：

1. **低质量示例** (Score: 35)
   ```
   Engineering Guide | Prompt Engineering Guide 🚀 Master building AI workflows and agents with Claude Code
   ```
   → 这是网页标题，不是提示词

2. **低质量示例** (Score: 25)
   ```
   engineering is not just about designing and developing prompts
   ```
   → 这是文章中的一句话，被截断了

3. **唯一还算有用的示例** (Score: 45)
   ```
   Write a short story about a young woman who discovers a magical portal in her attic.
   ```
   → 这是一个真正的提示词，但质量分数仍被低估

**问题 4：数据类型分布不平衡**
- text-generation: 13 条 (52%)
- general: 9 条 (36%)
- image-generation: 3 条 (12%)
- video-generation: 0 条 (0%)

#### 根本原因分析

1. **SearXNG 搜索结果本身质量不高**
   - 搜索返回的主要是教程和博客页面
   - 不是专门的提示词数据库
   - 缺少高质量提示词聚合站点

2. **正则提取模式过于宽松**
   - 引号匹配：匹配到页面标题、导航链接等
   - 冒号匹配：匹配到页面中的普通文本
   - 列表匹配：匹配到目录、菜单等

3. **网站反爬虫机制**
   - Cloudflare 保护
   - User-Agent 检测
   - 频率限制

4. **质量评分规则不够准确**
   - 过分依赖关键词匹配
   - 无法理解语义和上下文
   - 长度评分权重过高

---

### 2. Agent 评估脚本 (`evaluate-prompts-agent.py`)

#### ✅ 成功部分
- 脚本成功加载配置和数据
- 批量处理逻辑正确
- 降级评估机制已实现

#### ❌ 失败部分

**问题：sessions_spawn 调用失败**

日志显示：
```
2026-01-31 15:43:09,940 - ERROR - JSON 解析失败: Expecting value: line 1 column 1 (char 0)
```

**根本原因**：
1. `sessions_spawn` 命令的调用方式不正确
2. 命令返回的输出不是 JSON 格式
3. 子进程执行可能没有返回结果到 stdout
4. `sessions_spawn` 是一个异步命令，需要等待会话完成

**技术问题**：
```python
# 当前实现（错误）
cmd = [
    'clawdbot',
    'sessions',
    'spawn',
    '--task', prompt,
    '--timeout', str(self.config.timeout_seconds),
    '--cleanup', 'delete'
]

result = subprocess.run(cmd, capture_output=True, text=True, ...)
```

**问题分析**：
- `sessions_spawn` 是一个异步命令，不会立即返回评估结果
- 结果会通过消息传递到主会话，不是 stdout
- 需要使用不同的 API 或等待机制

---

### 3. 提取质量增强

#### ✅ 已实现
- 多层过滤规则（长度、字母数字比例、动作动词）
- 域名白名单和黑名单
- URL 去重机制
- 自动类型分类

#### ❌ 仍存在的问题
1. 过滤规则仍然过于宽松
2. 无法有效区分"标题/导航"和"真正的提示词"
3. HTML 清理逻辑不完善
4. 缺少上下文感知能力

---

## 🎯 预期效果 vs 实际效果

| 指标 | 预期效果 | 实际效果 | 差距 |
|------|----------|----------|------|
| 垃圾数据比例 | <10% | 88% | ❌ -88% |
| 高质量提示词 | 40% | 0% | ❌ -40% |
| 平均质量分数 | 65 | ~35 | ❌ -30 |

**结论**: 当前方案完全未达到预期目标。

---

## 🔧 改进建议

### 优先级 P0（立即修复）

#### 1. 修复 Agent 评估脚本

**问题**: sessions_spawn 调用失败

**解决方案 A**: 使用 `sessions_send` API
```python
# 需要调用 Clawdbot 的 Python API
from clawdbot_api import sessions_spawn

result = sessions_spawn(
    task=evaluation_prompt,
    timeout_seconds=60,
    cleanup='delete'
)
```

**解决方案 B**: 使用 REST API
```python
import requests

response = requests.post(
    'http://localhost:port/api/sessions/spawn',
    json={
        'task': evaluation_prompt,
        'timeout': 60,
        'cleanup': 'delete'
    }
)
result = response.json()
```

**解决方案 C**: 简化方案 - 使用规则评分
```python
# 暂时使用增强版规则评分
# 参考 evaluate-prompts.py 的评分逻辑
# 等待 sessions_spawn API 文档完善后再实现
```

#### 2. 改进 SearXNG 收集策略

**问题**: 数据质量极差

**解决方案**:
1. **更换数据源**：使用专门收集提示词的网站
   - PromptBase API (有付费 API)
   - OpenPrompt GitHub 仓库
   - awesome-chatgpt-prompts 仓库（直接克隆）

2. **改进提取逻辑**：
   ```python
   # 只从特定模式中提取
   patterns = [
       r'(?m)^Example: (.+)$',
       r'(?m)^Prompt: (.+)$',
       r'(?m)```\n(.+)\n```',  # 代码块
   ]
   ```

3. **添加人工验证步骤**：
   - 先收集候选数据
   - 输出到终端供快速浏览
   - 让用户标记"保留/删除"

### 优先级 P1（短期优化）

#### 3. 使用 GitHub 作为主要数据源

**优势**:
- 无反爬虫
- 有完整的 JSON 文件
- 社区审核过质量

**实现**:
```bash
# 克隆 awesome-chatgpt-prompts
git clone https://github.com/f/awesome-chatgpt-prompts.git

# 解析 README.md 或 prompts.json
# 转换为标准格式
```

#### 4. 添加数据源多样性

- Reddit r/ChatGPT
- Discord 提示词社区
- 专业 Prompt Engineering 博客

### 优先级 P2（长期改进）

#### 5. 建立提示词质量评估数据集

- 手动标注 100 个高质量提示词
- 手动标注 100 个低质量提示词
- 训练简单的分类器
- 用于后续自动评分

#### 6. 实现增量收集

- 记录已处理的 URL
- 定期检查更新
- 只处理新内容

---

## 📁 相关文件

### 脚本
- `/root/clawd/scripts/evaluate-prompts-agent.py` - Agent 评估脚本（需要修复）
- `/root/clawd/scripts/collect-prompts-via-searxng.py` - SearXNG 收集脚本（已运行）
- `/root/clawd/scripts/convert-prompts-to-skills.py` - 转换脚本（未运行）

### 数据
- `/root/clawd/data/prompts/collected/test-prompts-20260131-152033.jsonl` - 收集的数据（低质量）
- `/root/clawd/reports/p0-implementation-report.md` - P0 实现报告
- `/root/clawd/data/prompts/evaluation-and-collection-improvement.md` - 改进方案文档

### 日志
- `/root/clawd/logs/collect-prompts-searxng.log` - 收集日志
- `/root/clawd/logs/evaluate-prompts-agent.log` - 评估日志

---

## 🎓 经验教训

### 技术层面
1. **不要低估反爬虫的难度**：403 错误非常普遍
2. **SearXNG 不是万能的**：搜索结果质量取决于数据源
3. **sessions_spawn 调用需要正确的 API**：不能直接用 subprocess
4. **正则提取非常脆弱**：HTML 结构变化会导致失效

### 数据质量层面
1. **数据源比算法更重要**：垃圾进，垃圾出
2. **规则评分无法理解语义**：需要真正的 LLM 评估
3. **手动验证必不可少**：至少初期需要人工审核

### 项目管理层面
1. **先验证再开发**：应该先用小数据验证 SearXNG 搜索质量
2. **分阶段实现**：应该先搞定评估，再搞收集
3. **快速反馈循环**：应该在 10 条数据上测试，而不是批量处理

---

## 📅 下一步行动计划

### 立即行动（今天）
1. ✅ 修复 sessions_spawn 调用问题（使用简化方案）
2. ✅ 尝试从 GitHub 克隆 awesome-chatgpt-prompts
3. ✅ 手动验证几个高质量数据源

### 本周目标
1. 找到可靠的高质量数据源
2. 修复评估脚本
3. 收集至少 100 条高质量提示词

### 下周目标
1. 实现 Agent 评估（或找到替代方案）
2. 建立自动质量检查机制
3. 开始转换为 Skills

---

## 📊 总结

**当前状态**: ❌ 方案未达预期，需要重大调整

**核心问题**:
1. 数据源质量差（88% 垃圾数据）
2. Agent 评估脚本技术问题未解决
3. 提取逻辑需要大幅改进

**关键成功因素**:
1. **数据源** > 算法
2. **人工验证** > 自动化
3. **快速迭代** > 完美方案

**建议**: 暂停当前流程，优先解决数据源问题和评估脚本问题。

---

**报告生成时间**: 2026-01-31 15:50
**报告生成者**: Clawdbot AI Agent
**版本**: 1.0
