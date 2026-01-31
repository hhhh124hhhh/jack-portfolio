# 自然语言命令解释器使用指南

这个工具允许你用自然语言与 Clawdbot 对话，它会自动理解你的需求并执行相应的命令。

## 功能特性

### 1. 批量处理 .skill 文件
`/root/clawd/scripts/batch-process-all-skills.sh` - 搜索并处理所有 `.skill` 文件

- 搜索多个目录（根目录、dist、generated-skills 等）
- 解析每个 `.skill` 文件的内容
- 提取名称、描述、分类等信息
- 生成 JSON 格式的元数据
- 生成汇总报告

**使用方法：**
```bash
bash /root/clawd/scripts/batch-process-all-skills.sh
```

**输出：**
- `/root/clawd/processed-skills/` - 每个技能的 JSON 文件
- `/root/clawd/processed-skills/report-*.json` - 汇总报告
- `/root/clawd/logs/batch-process-all-skills-*.log` - 日志文件

### 2. 自然语言命令解释器
`/root/clawd/scripts/nl-to-exec.sh` - 将自然语言需求转换为可执行命令

支持三种模式：

#### 交互式模式
```bash
bash /root/clawd/scripts/nl-to-exec.sh interactive
```
然后在提示符后输入你的需求，例如：
- "批量处理所有 skill 文件"
- "上传 skills 到 ClawdHub"
- "转换 prompts 为 skills"
- "搜索 X 上的 AI 提示词"
- "评估提示词质量"
- 输入 "exit" 退出

#### 命令行模式
```bash
bash /root/clawd/scripts/nl-to-exec.sh execute "你的需求"
```

#### 查看信息模式
```bash
# 查看当前上下文
bash /root/clawd/scripts/nl-to-exec.sh context

# 查看任务历史
bash /root/clawd/scripts/nl-to-exec.sh history
```

### 3. X 搜索工具
`/root/clawd/scripts/search-x-prompts.py` - 从 X (Twitter) 搜索 AI 提示词

**功能：**
- 搜索多个关键词（AI prompts、ChatGPT prompts、prompt engineering 等）
- 获取相关推文
- 从推文中提取提示词
- 保存到 JSONL 格式

**使用方法：**
```bash
python3 /root/clawd/scripts/search-x-prompts.py
```

**环境变量：**
- `TWITTER_API_KEY` - Twitter API 密钥

**输出：**
- `/root/clawd/data/prompts/x-search-results.jsonl` - 推文数据
- `/root/clawd/data/prompts/extracted-prompts.jsonl` - 提取的提示词
- `/root/clawd/data/prompts/x-search-report-*.json` - 搜索报告

### 4. 提示词评估工具
`/root/clawd/scripts/evaluate-prompts.py` - 评估提示词质量

**评估标准：**
- **长度** (20%): 提示词的长度是否合适
- **具体性** (20%): 是否包含具体的关键词
- **结构** (25%): 是否有清晰的结构（角色、任务、格式等）
- **清晰度** (20%): 表达是否清晰
- **创意性** (15%): 是否具有创意

**使用方法：**
```bash
python3 /root/clawd/scripts/evaluate-prompts.py
```

**输入：**
- 从 `/root/clawd/data/prompts/` 读取包含 "prompts" 的 JSONL 文件

**输出：**
- `/root/clawd/data/prompts/evaluated/evaluated-prompts-*.jsonl` - 评估结果
- `/root/clawd/data/prompts/evaluated/evaluation-report-*.json` - 评估报告

## 完整工作流程

### 方案 1：从零开始创建 Skills

1. **搜索 X 获取提示词**
```bash
python3 /root/clawd/scripts/search-x-prompts.py
```

2. **评估提示词质量**
```bash
python3 /root/clawd/scripts/evaluate-prompts.py
```

3. **转换为 Skills**
```bash
python3 /root/clawd/scripts/convert-prompts-to-skills.py
```

4. **批量处理所有 Skills**
```bash
bash /root/clawd/scripts/batch-process-all-skills.sh
```

5. **上传到 ClawdHub**
```bash
bash /root/clawd/scripts/batch-upload-skills-v3.sh
```

### 方案 2：使用自然语言命令

```bash
# 进入交互式模式
bash /root/clawd/scripts/nl-to-exec.sh interactive

# 然后依次输入：
# "搜索 X 上的 AI 提示词"
# "评估提示词质量"
# "转换 prompts 为 skills"
# "批量处理所有 skill 文件"
# "上传 skills 到 ClawdHub"
```

### 方案 3：逐个执行命令

```bash
bash /root/clawd/scripts/nl-to-exec.sh execute "搜索 X 上的 AI 提示词"
bash /root/clawd/scripts/nl-to-exec.sh execute "评估提示词质量"
bash /root/clawd/scripts/nl-to-exec.sh execute "转换 prompts 为 skills"
bash /root/clawd/scripts/nl-to-exec.sh execute "批量处理所有 skill 文件"
bash /root/clawd/scripts/nl-to-exec.sh execute "上传 skills 到 ClawdHub"
```

## 上下文记忆

自然语言解释器会维护上下文信息，包括：
- 用户偏好
- 之前的任务记录
- 学习到的模式

上下文存储在：`/root/clawd/memory/nl-exec/context.json`

查看上下文：
```bash
bash /root/clawd/scripts/nl-to-exec.sh context
```

## 故障排查

### 问题：命令执行失败
- 检查脚本是否有执行权限
- 确认依赖工具已安装
- 查看日志文件获取详细错误信息

### 问题：X 搜索失败
- 检查 `TWITTER_API_KEY` 环境变量是否设置
- 确认 API 密钥有效
- 检查网络连接

### 问题：自然语言无法识别
- 使用更明确的描述
- 尝试直接调用对应脚本
- 查看 `nl-to-exec.sh` 中的模式匹配规则

## 文件结构

```
/root/clawd/
├── scripts/
│   ├── batch-process-all-skills.sh    # 批量处理 .skill 文件
│   ├── nl-to-exec.sh                   # 自然语言命令解释器
│   ├── search-x-prompts.py            # X 搜索工具
│   ├── evaluate-prompts.py            # 提示词评估工具
│   ├── convert-prompts-to-skills.py   # 提示词转 Skills
│   └── batch-upload-skills-v3.sh     # 批量上传工具
├── processed-skills/                   # 处理后的技能元数据
├── memory/
│   └── nl-exec/                       # 自然语言解释器记忆
│       ├── context.json               # 上下文信息
│       ├── tasks/                     # 任务历史
│       └── sessions/                  # 会话记录
├── data/
│   └── prompts/                       # 提示词数据
│       ├── x-search-results.jsonl
│       ├── extracted-prompts.jsonl
│       └── evaluated/
│           ├── evaluated-prompts-*.jsonl
│           └── evaluation-report-*.json
└── logs/                              # 日志文件
```

## 高级用法

### 自定义搜索关键词
编辑 `search-x-prompts.py` 中的 `SEARCH_QUERIES` 列表。

### 调整质量评分标准
编辑 `evaluate-prompts.py` 中的 `QUALITY_CRITERIA` 字典。

### 添加新的自然语言命令
编辑 `nl-to-exec.sh` 中的 `execute_simple_command()` 函数，添加新的 case 分支。

## 示例输出

### 批量处理输出
```
✅ 成功: 61
⚠️  跳过: 0
❌ 失败: 0
📦 总计: 61
```

### 评估报告
```json
{
  "timestamp": "2026-01-31T10:06:15+08:00",
  "total_evaluated": 150,
  "quality_distribution": {
    "high": 45,
    "medium": 78,
    "low": 27
  },
  "average_score": 72.35
}
```

## 贡献

欢迎改进这些工具！
