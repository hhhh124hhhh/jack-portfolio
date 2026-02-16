---
name: seedance-2-prompt
version: 1.0.0
description: Seedance 2.0 AI 视频生成模型提示词生成和管理工具
author: Seedance Team
category: video-generation
tags: [seedance, video, prompt, ai-generation]
---

# Seedance 2.0 视频提示词 Skill

专业的 Seedance 2.0 AI 视频生成模型提示词生成和管理工具。

## 核心功能

- **交互式提示词生成** - 通过交互式对话引导用户生成完整的视频提示词
- **提示词优化** - 优化用户输入的提示词，根据万能公式补充缺失元素
- **模板库管理** - 存储和管理 24 个预设模板，按类型和难度分类
- **高质量示例展示** - 展示高质量提示词示例，包含结构分析
- **提示词变体生成** - 为同一场景生成多个优化版本
- **🌐 在线搜索** - 搜索最新的 Seedance 2.0 提示词，获取灵感和参考
- **📥 模板更新** - 从网络获取最新模板，更新本地模板库

## 万能公式

```
主体 + 动作 + 场景 + 光影 + 镜头语言 + 风格 + 画质 + 约束
```

## 视频类型

1. `photo-realistic` - 超逼真视频生成
2. `character-consistency` - 角色与场景一致性
3. `camera-movement` - 高级运镜动作
4. `creative-effects` - 创意视觉特效
5. `storytelling` - 剧情发展与延伸
6. `audio-sync` - 音频与语音合成
7. `one-shot` - 一镜到底
8. `emotion-performance` - 情绪演绎

## 难度级别

- `BEGINNER` - 初学者（简单描述，基础元素）
- `INTERMEDIATE` - 中级（增加光影和镜头）
- `ADVANCED` - 高级（完整的万能公式）
- `EXPERT` - 专家（极致细节和专业术语）

## 使用方法

### 命令行工具

```bash
# 生成提示词
python scripts/prompt_generator.py

# 优化提示词
python scripts/prompt_optimizer.py

# 浏览示例
python scripts/examples.py

# 浏览模板
python scripts/template_library.py

# 在线搜索提示词
python scripts/search_online.py "雨天城市街道" -t photo-realistic -d INTERMEDIATE -n 10

# 更新模板库
python scripts/update_templates.py --search "最新 Seedance 2.0 提示词"
```

### Python API

#### 生成提示词

```python
from scripts.prompt_generator import generate_prompt

result = generate_prompt(
    scene="一位年轻女性在花园里散步",
    style="梦幻",
    difficulty="INTERMEDIATE",
    video_type="photo-realistic"
)

print(result['prompt'])
print(result['elements'])
print(result['variants'])
```

#### 优化提示词

```python
from scripts.prompt_optimizer import optimize_prompt

result = optimize_prompt(
    user_prompt="一位女士在花园里",
    difficulty="INTERMEDIATE"
)

print(result['optimized_prompt'])
print(result['suggestions'])
print(result['score'])
```

#### 补全万能公式

```python
from scripts.prompt_optimizer import complete_formula_prompt

result = complete_formula_prompt(
    user_prompt="一位女士在花园里",
    difficulty="ADVANCED"
)

print(result['completed'])
```

#### 生成变体

```python
from scripts.prompt_optimizer import generate_variants

variants = generate_variants(
    prompt="一位女士在花园里散步",
    count=3,
    difficulty="INTERMEDIATE"
)

for v in variants:
    print(v['variant'])
    print(v['changes'])
```

#### 查询模板

```python
from scripts.template_library import TemplateLibrary

lib = TemplateLibrary()

# 获取所有模板
templates = lib.get_all_templates()

# 按类型查询
templates = lib.get_templates_by_type("photo-realistic")

# 按难度查询
templates = lib.get_templates_by_difficulty("INTERMEDIATE")

# 按类型和难度查询
templates = lib.get_templates_by_type_and_difficulty("photo-realistic", "INTERMEDIATE")

# 搜索模板
templates = lib.search_templates("花园")

# 获取单个模板
template = lib.get_template_by_id("photo-realistic-beginner-1")

# 保存自定义模板
lib.save_custom_template({
    "id": "my-custom-template",
    "name": "我的自定义模板",
    "video_type": "photo-realistic",
    "difficulty": "INTERMEDIATE",
    "prompt": "我的提示词内容...",
    "tags": ["自定义", "测试"],
    "duration": "5-10s"
})
```

#### 在线搜索提示词

```python
from scripts.search_online import search_prompts

# 基本搜索
results = search_prompts("雨天城市街道")

# 按视频类型搜索
results = search_prompts(
    query="人物肖像",
    video_type="photo-realistic",
    max_results=10
)

# 按难度搜索
results = search_prompts(
    query="复杂场景",
    difficulty="ADVANCED",
    max_results=5
)

# 组合搜索
results = search_prompts(
    query="城市夜景",
    video_type="photo-realistic",
    difficulty="INTERMEDIATE",
    max_results=10
)

# 查看结果
for prompt in results:
    print(f"标题: {prompt['title']}")
    print(f"提示词: {prompt['prompt']}")
    print(f"类型: {prompt['video_type']}")
    print(f"难度: {prompt['difficulty']}")
    print(f"来源: {prompt['search_source']}")
    print()
```

#### 生成提示词（使用在线搜索）

```python
from scripts.prompt_generator import PromptGenerator

generator = PromptGenerator()

# 基本生成（不使用在线搜索）
result = generator.generate_prompt(
    scene="一位年轻女性在花园里散步",
    style="梦幻",
    difficulty="INTERMEDIATE",
    video_type="photo-realistic"
)

# 使用在线搜索生成
result = generator.generate_prompt_with_search(
    scene="一位年轻女性在花园里散步",
    style="梦幻",
    difficulty="INTERMEDIATE",
    video_type="photo-realistic",
    online_search=True,  # 启用在线搜索
    max_online_results=5
)

# 查看在线搜索结果
if result['online_used']:
    print(f"找到 {len(result['online_results'])} 个相关提示词")
    for online_prompt in result['online_results']:
        print(f"  - {online_prompt['title']}")
```

#### 更新模板库

```python
from scripts.update_templates import TemplateUpdater

updater = TemplateUpdater()

# 从搜索更新模板
templates = updater.fetch_templates_from_search("最新 Seedance 2.0 提示词")
count = updater.update_local_templates(templates)

print(f"更新了 {count} 个模板")
```

#### 浏览示例

```python
from scripts.examples import ExamplesLibrary

lib = ExamplesLibrary()

# 按类型获取示例
examples = lib.get_examples_by_type("photo-realistic")

# 按难度获取示例
examples = lib.get_examples_by_difficulty("INTERMEDIATE")

# 获取精选示例
examples = lib.get_featured_examples(10)

# 搜索示例
examples = lib.search_examples("花园")

# 获取单个示例
example = lib.get_example_by_id("photo-realistic-beginner-1")

# 显示示例详情
lib.display_example(example)

# 交互式浏览
lib.interactive_browse()
```

## 完整工作流示例

```python
#!/usr/bin/env python3
from scripts.prompt_generator import PromptGenerator
from scripts.prompt_optimizer import PromptOptimizer
from scripts.examples import ExamplesLibrary

# 1. 生成提示词
print("=== 生成提示词 ===")
generator = PromptGenerator()
result = generator.generate_prompt(
    scene="一位年轻女性在花园里散步",
    style="梦幻",
    difficulty="INTERMEDIATE",
    video_type="photo-realistic"
)
print(f"生成提示词: {result['prompt']}\n")

# 2. 优化提示词
print("=== 优化提示词 ===")
optimizer = PromptOptimizer()
optimized = optimizer.optimize_prompt(result['prompt'], difficulty="INTERMEDIATE")
print(f"优化后提示词: {optimized['optimized_prompt']}")
print(f"评分: {optimized['score']['total']}/100\n")

# 3. 查看示例
print("=== 查看示例 ===")
examples_lib = ExamplesLibrary()
example = examples_lib.get_example_by_id("photo-realistic-beginner-1")
examples_lib.display_example(example)
```

## 输出格式

所有提示词结果均以 JSON 格式返回，包含：

- `prompt` - 完整提示词文本
- `elements` - 万能公式元素字典
- `variants` - 提示词变体列表
- `video_type` - 视频类型
- `difficulty` - 难度级别
- `recommended_duration` - 推荐时长
- `score` - 评分（仅优化器）
- `suggestions` - 优化建议（仅优化器）

## 数据统计

- **模板数量**: 24 个预设模板
- **视频类型**: 8 种类型
- **难度级别**: 4 个级别
- **示例质量**: 每个示例包含完整元素分析

## 扩展开发

### 添加新模板

编辑 `references/templates.md` 或通过 API 保存自定义模板。

### 扩展视频类型

在 `scripts/prompt_generator.py` 的 `VIDEO_TYPES` 字典中添加新类型。

## 详细文档

更多信息请参考：
- `references/templates.md` - 24 个模板的完整文档
- `references/video-types.md` - 视频类型详细说明
- `references/difficulty-levels.md` - 难度级别详细说明
- `references/examples.md` - 示例和使用指南

## 版本信息

- **版本**: 1.0.0
- **发布日期**: 2026-02-14
- **兼容性**: Seedance 2.0 AI 视频生成模型
