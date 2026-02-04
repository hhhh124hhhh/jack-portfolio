# Memory Manager - 记忆管理系统

统一管理和查询所有记忆内容，包括核心记忆和扩展 memory skills。

## 功能

### 1. 列出所有 Memory Skills
\`\`\`python
memory_skills_list()
\`\`\`

返回所有可用的 memory skills 列表。

### 2. 搜索记忆内容
\`\`\`python
memory_search(keyword, skill_name=None)
\`\`\`

**参数**：
- keyword: 搜索关键词
- skill_name: 可选，指定搜索某个 skill

**示例**：
\`\`\`
memory_search("AI 提示词评分")
memory_search("Slack 连接", "memory-debugging")
\`\`\`

### 3. 获取特定章节
\`\`\`python
memory_get(skill_name, section=None)
\`\`\`

**参数**：
- skill_name: memory skill 名称
- section: 可选，章节名称

**示例**：
\`\`\`
memory_get("memory-projects")
memory_get("memory-projects", "ai-prompts")
memory_get("memory-tech-infra", "searxng")
\`\`\`

### 4. 智能加载
\`\`\`python
memory_smart_load(context)
\`\`\`

根据当前上下文自动加载相关的 memory skills。

## Memory Skills 列表

### 核心记忆
- **MEMORY.md** - 核心记忆（用户信息、重要项目、配置）
- 自动加载，约 3.5K

### 扩展记忆 Skills
1. **memory-projects** - AI 提示词商业计划、评分系统
2. **memory-tech-infra** - 技术基础设施（SearXNG、Gateway）
3. **memory-debugging** - 调试经验记录
4. **memory-solutions** - 问题解决方案（上下文溢出等）

## 使用示例

### 查找 AI 提示词评分系统
\`\`\`
# 方式 1：搜索
memory_search("AI 提示词评分系统")

# 方式 2：直接获取
memory_get("memory-projects")
\`\`\`

### 查找 Slack 调试经验
\`\`\`
# 方式 1：搜索
memory_search("Slack 连接问题")

# 方式 2：直接获取
memory_get("memory-debugging", "slack")
\`\`\`

### 查找上下文溢出解决方案
\`\`\`
memory_search("上下文溢出")
\`\`\`

## 最佳实践

1. **优先搜索**：使用 memory_search() 快速找到相关内容
2. **精确获取**：知道具体位置时，使用 memory_get()
3. **智能加载**：复杂任务时，使用 memory_smart_load()
4. **避免重复**：搜索前先检查 MEMORY.md 中的索引
5. **自动记忆**：重要信息及时记录（决策、配置、解决方案）

## 实际实现

### CLI 工具
**路径**: `/root/clawd/scripts/memory-manager.py`

#### 使用示例
```bash
# 列出所有 memory skills
$ python3 /root/clawd/scripts/memory-manager.py list
✅ 找到 5 个 memory skills:
  MEMORY.md (core, 6448 bytes)
  memory-tech-infra (extended, 1697 bytes)
  ...

# 搜索记忆内容
$ python3 /root/clawd/scripts/memory-manager.py search "AI 提示词"
✅ 找到 6 条匹配结果:
  1. [MEMORY.md:14]
     ### 🎯 AI 提示词转 Skill 商业计划...
  ...

# 自动记忆
$ python3 /root/clawd/scripts/memory-manager.py memorize "决定使用 SearXNG 作为主要搜索引擎"
✅ 已记忆到: /root/clawd/memory/2026-02-03.md (类型: decision)

# 更新索引
$ python3 /root/clawd/scripts/memory-manager.py index
✅ Daily memory 索引已创建:
  文件数: 9
  总行数: 1608
  最新: 2026-02-03
  索引: /root/clawd/memory/daily-index.json
```

### Python API

#### 初始化
```python
from memory_manager import MemoryManager, auto_memorize, create_daily_memory_index

manager = MemoryManager()
```

#### 列出 Skills
```python
skills = manager.memory_skills_list()
for skill in skills:
    print(f"{skill['name']}: {skill['type']}")
```

#### 搜索
```python
results = manager.memory_search("AI 提示词")
for result in results:
    print(f"[{result['name']}:{result['line']}] {result['content']}")
```

#### 获取内容
```python
# 获取整个 skill
content = manager.memory_get("memory-projects")

# 获取特定章节
content = manager.memory_get("memory-projects", "ai-prompts")
```

#### 智能加载
```python
context = "我要调试 Slack 连接问题"
related = manager.memory_smart_load(context)
# 返回: ["MEMORY.md", "memory-debugging"]
```

#### 自动记忆
```python
# 记录决策
file = auto_memorize("决定使用 SearXNG 作为主要搜索引擎", type="decision")

# 记录配置
file = auto_memorize("SEARXNG_URL=http://localhost:8080", type="config")

# 记录解决方案
file = auto_memorize("解决上下文溢出：使用子代理", type="solution")
```

#### 创建索引
```python
index = create_daily_memory_index()
print(f"总文件: {index['total_files']}")
print(f"总行数: {index['summary']['total_lines']}")
```

### Daily Memory 索引

#### 索引格式
```json
{
  "updated_at": "2026-02-03T07:50:00+08:00",
  "total_files": 9,
  "files": [
    {
      "date": "2026-02-03",
      "file": "/root/clawd/memory/2026-02-03.md",
      "title": "2026-02-03",
      "lines": 100,
      "size": 1024,
      "modified": "2026-02-03T07:30:00+08:00"
    }
  ],
  "summary": {
    "latest_date": "2026-02-03",
    "total_lines": 1608,
    "total_size": 51200
  }
}
```

#### Cron 任务
- **ID**: daily-memory-index
- **时间**: 每天 00:00 (Asia/Shanghai)
- **功能**: 自动更新 daily memory 索引

### 使用指南
**文档**: `/root/clawd/skills/memory-manager/README.md`

包含：
1. 快速开始
2. Python API
3. Cron 任务
4. 最佳实践
5. 索引格式
6. 集成到 OpenClaw
7. 故障排除
8. 未来优化

## 版本历史
- 2026-02-02: 初始版本
- 2026-02-03: 实现完整功能（CLI 工具、自动记忆、索引）
