#!/usr/bin/env python3
"""
教程生成器 - 自动记录易错点和优化点
功能：
1. 记录易错点和优化点
2. 调用 coding-agent (Claude) 生成教程
3. 管理教程目录和索引
"""

import json
import os
from datetime import datetime

# 配置
TUTORIALS_DIR = "/root/clawd/tutorials"
INDEX_FILE = f"{TUTORIALS_DIR}/index.json"
DATE = datetime.now().strftime("%Y-%m-%d")

def ensure_dir(path):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)

def load_index():
    """加载教程索引"""
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"tutorials": []}

def save_index(index):
    """保存教程索引"""
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

def add_to_index(tutorial_info):
    """添加教程到索引"""
    index = load_index()
    index["tutorials"].append(tutorial_info)
    save_index(index)

def create_tutorial(issue, mistake, solution, explanation, tags=None):
    """创建教程"""
    ensure_dir(TUTORIALS_DIR)

    # 生成 ID
    tutorial_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    tutorial_file = f"{TUTORIALS_DIR}/{tutorial_id}.md"

    # 教程元数据
    tutorial_info = {
        "id": tutorial_id,
        "title": f"{issue} - {mistake[:30]}",
        "issue": issue,
        "mistake": mistake,
        "date": DATE,
        "file": tutorial_file,
        "tags": tags or []
    }

    # 教程模板
    tutorial_template = f"""# {tutorial_info['title']}

**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分类**: {issue}
**标签**: {', '.join(tags or [])}

---

## 🚨 问题描述

{issue}

## ❌ 常见错误

{mistake}

## ✅ 正确做法

{solution}

## 💡 详细解释

{explanation}

## 📚 相关资源

- **学习路径**: OpenClaw 官方文档
- **相关教程**: 查看其他教程
- **最佳实践**: 遵循社区约定

---

*本教程由 Clawdbot 自动生成*
*来源: {datetime.now().strftime('%Y-%m-%d')} 的实际经验*
"""

    # 保存教程
    with open(tutorial_file, 'w', encoding='utf-8') as f:
        f.write(tutorial_template)

    # 更新索引
    add_to_index(tutorial_info)

    return tutorial_info

def generate_tutorial_with_claude(issue, mistake, solution, tags=None):
    """调用 Claude 生成详细教程"""
    # 提示词
    prompt = f"""你是一个技术文档专家。请根据以下信息，生成一份详细的技术教程。

**问题类别**: {issue}
**常见错误**: {mistake}
**正确做法**: {solution}

要求：
1. 生成详细的步骤说明
2. 包含代码示例（如果适用）
3. 添加故障排除部分
4. 解释为什么这样做是正确的
5. 添加相关学习资源

教程格式：
- 问题描述
- 常见错误及原因
- 正确做法（详细步骤）
- 详细解释
- 故障排除
- 相关资源
- 最佳实践

请用中文编写，格式清晰，易于理解。
"""

    # 这里应该调用 coding-agent
    # 但为了简化，我们先返回基本的教程信息
    explanation = f"""
这个问题的根源在于：

1. **问题分析**: {mistake}

2. **为什么这样做**: {solution}

3. **最佳实践**:
   - 遵循官方文档
   - 参考社区经验
   - 测试和验证

4. **学习要点**:
   - 理解底层原理
   - 掌握正确方法
   - 避免常见陷阱
"""

    return explanation

def list_tutorials():
    """列出所有教程"""
    index = load_index()
    return index["tutorials"]

def search_tutorials(keyword):
    """搜索教程"""
    index = load_index()
    results = []

    for tutorial in index["tutorials"]:
        content = " ".join([
            tutorial.get('title', ''),
            tutorial.get('issue', ''),
            tutorial.get('mistake', ''),
            ' '.join(tutorial.get('tags', []))
        ]).lower()

        if keyword.lower() in content:
            results.append(tutorial)

    return results

def main():
    """主函数 - 交互式创建教程"""
    print("=" * 60)
    print("📚 教程生成器")
    print("=" * 60)
    print()

    print("今天的易错点和优化点：")
    print()

    # 今天的教程列表
    tutorials = [
        {
            "issue": "会话上下文溢出",
            "mistake": "配置了 memoryFlush.softThresholdTokens=8000，但实际使用到 109k tokens 才溢出，自动压缩没有生效",
            "solution": "设置合理的软阈值（50k）和硬阈值（80k），配置自动备份机制，每2小时备份重点信息到记忆系统",
            "tags": ["会话管理", "上下文", "配置", "最佳实践"]
        },
        {
            "issue": "会话重置前备份",
            "mistake": "直接重置会话会丢失所有对话历史和重要信息",
            "solution": "在重置前创建备份脚本，提取决策、问题、任务等关键信息到 memory/ 目录，确保重要信息不丢失",
            "tags": ["会话管理", "备份", "记忆系统"]
        },
        {
            "issue": "Cron 任务添加",
            "mistake": "使用 jq 合并 JSON 时出错，因为 jobs.json 的结构是 {{\"jobs\": [...], \"version\": 1}}，直接合并会破坏结构",
            "solution": "使用 Python 脚本读取、添加新任务、写回，确保 JSON 结构完整",
            "tags": ["cron", "配置", "Python", "JSON"]
        },
        {
            "issue": "API 调用方式",
            "mistake": "尝试用 curl POST /api/sessions/agent:main:main/reset 重置会话，返回 'Method Not Allowed'",
            "solution": "使用 gateway restart 命令或 sessions_reset 工具，而不是直接调用 API",
            "tags": ["API", "会话管理", "最佳实践"]
        }
    ]

    for i, t in enumerate(tutorials, 1):
        print(f"{i}. {t['issue']}")
        print(f"   错误: {t['mistake'][:60]}...")
        print()

    print("是否生成这些教程？(y/n): ", end="")
    choice = input().strip().lower()

    if choice == 'y':
        for t in tutorials:
            print(f"\n生成教程: {t['issue']}")
            explanation = generate_tutorial_with_claude(
                t['issue'], t['mistake'], t['solution'], t['tags']
            )
            tutorial_info = create_tutorial(
                t['issue'], t['mistake'], t['solution'],
                explanation, t['tags']
            )
            print(f"✅ 已保存: {tutorial_info['file']}")

        print(f"\n总共生成了 {len(tutorials)} 个教程")
        print(f"📁 教程目录: {TUTORIALS_DIR}")
    else:
        print("取消生成")

if __name__ == "__main__":
    main()
