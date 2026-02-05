#!/usr/bin/env python3
"""
Memory Manager - 记忆管理系统实现
统一管理和查询所有记忆内容
"""

import os
import re
import json
import glob
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# 配置
BASE_DIR = Path("/root/clawd")
MEMORY_DIR = BASE_DIR / "memory"
CORE_MEMORY_FILE = BASE_DIR / "MEMORY.md"
SKILLS_DIR = BASE_DIR / "skills" / "memory-modules"


class MemoryManager:
    """记忆管理器"""

    def __init__(self):
        self.base_dir = BASE_DIR
        self.memory_dir = MEMORY_DIR
        self.core_memory = CORE_MEMORY_FILE
        self.skills_dir = SKILLS_DIR

    def memory_skills_list(self) -> List[Dict[str, str]]:
        """列出所有 Memory Skills"""
        skills = []

        # 核心记忆
        if self.core_memory.exists():
            skills.append({
                "name": "MEMORY.md",
                "path": str(self.core_memory),
                "type": "core",
                "size": self.core_memory.stat().st_size
            })

        # 扩展 skills
        if self.skills_dir.exists():
            for skill_dir in self.skills_dir.iterdir():
                if skill_dir.is_dir():
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        skills.append({
                            "name": skill_dir.name,
                            "path": str(skill_file),
                            "type": "extended",
                            "size": skill_file.stat().st_size
                        })

        return skills

    def memory_search(self, keyword: str, skill_name: Optional[str] = None) -> List[Dict[str, any]]:
        """搜索记忆内容

        Args:
            keyword: 搜索关键词
            skill_name: 可选，指定搜索某个 skill

        Returns:
            匹配的结果列表
        """
        results = []

        # 确定搜索范围
        search_files = []
        if skill_name:
            # 搜索指定 skill
            if skill_name == "MEMORY.md":
                search_files.append(self.core_memory)
            else:
                skill_file = self.skills_dir / skill_name / "SKILL.md"
                if skill_file.exists():
                    search_files.append(skill_file)
        else:
            # 搜索所有记忆
            search_files.append(self.core_memory)
            if self.skills_dir.exists():
                for skill_dir in self.skills_dir.iterdir():
                    skill_file = skill_dir / "SKILL.md"
                    if skill_file.exists():
                        search_files.append(skill_file)

        # 搜索每个文件
        for file_path in search_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 搜索关键词
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if keyword.lower() in line.lower():
                        # 提取上下文（前后 2 行）
                        context_start = max(0, i - 3)
                        context_end = min(len(lines), i + 2)
                        context = '\n'.join(lines[context_start:context_end])

                        results.append({
                            "file": str(file_path),
                            "name": file_path.parent.name if file_path != self.core_memory else "MEMORY.md",
                            "line": i,
                            "content": line.strip(),
                            "context": context,
                            "match": keyword
                        })
            except Exception as e:
                continue

        return results

    def memory_get(self, skill_name: str, section: Optional[str] = None) -> str:
        """获取特定章节

        Args:
            skill_name: memory skill 名称
            section: 可选，章节名称

        Returns:
            章节内容
        """
        # 确定文件路径
        if skill_name == "MEMORY.md":
            file_path = self.core_memory
        else:
            file_path = self.skills_dir / skill_name / "SKILL.md"

        if not file_path.exists():
            return f"❌ 找不到记忆: {skill_name}"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if section:
                # 提取特定章节
                section_pattern = rf"## {section}.*?(?=## |\Z)"
                match = re.search(section_pattern, content, re.DOTALL)
                if match:
                    return match.group(0).strip()
                else:
                    return f"❌ 找不到章节: {section}"
            else:
                # 返回全部内容
                return content

        except Exception as e:
            return f"❌ 读取失败: {str(e)}"

    def memory_smart_load(self, context: str) -> List[str]:
        """根据上下文智能加载相关的 memory skills

        Args:
            context: 当前上下文描述

        Returns:
            相关的 memory skills 列表
        """
        context_lower = context.lower()
        related = []

        # 关键词映射
        keywords_map = {
            "memory-projects": ["项目", "商业计划", "ai 提示词", "评分", "成就系统", "moltbot"],
            "memory-tech-infra": ["searxng", "gateway", "技术", "配置", "docker", "api"],
            "memory-debugging": ["调试", "slack", "feishu", "连接", "错误", "问题"],
            "memory-solutions": ["解决方案", "上下文", "溢出", "优化", "性能", "记忆"]
        }

        # 匹配关键词
        for skill, keywords in keywords_map.items():
            if any(keyword in context_lower for keyword in keywords):
                related.append(skill)

        # 总是包含核心记忆
        related.insert(0, "MEMORY.md")

        return related


def create_daily_memory_index():
    """创建 daily memory 索引"""
    memory_dir = Path("/root/clawd/memory")
    index_file = memory_dir / "daily-index.json"

    if not memory_dir.exists():
        return {"error": "memory 目录不存在"}

    # 收集所有 daily memory 文件
    daily_files = []
    for file in memory_dir.glob("202?-??-??.md"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取标题（第一个 # 开头的行）
            title_match = re.search(r"^#+ (.+)$", content, re.MULTILINE)
            title = title_match.group(1) if title_match else file.name

            # 统计行数
            line_count = len(content.split('\n'))

            daily_files.append({
                "date": file.stem,
                "file": str(file),
                "title": title,
                "lines": line_count,
                "size": file.stat().st_size,
                "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })
        except Exception as e:
            continue

    # 按日期排序
    daily_files.sort(key=lambda x: x["date"], reverse=True)

    if not daily_files:
        return {"error": "没有找到 daily memory 文件"}

    # 保存索引
    index = {
        "updated_at": datetime.now().isoformat(),
        "total_files": len(daily_files),
        "files": daily_files,
        "summary": {
            "latest_date": daily_files[0]["date"],
            "total_lines": sum(f["lines"] for f in daily_files),
            "total_size": sum(f["size"] for f in daily_files)
        }
    }

    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    return index


def auto_memorize(message: str, type: str = "general") -> Optional[str]:
    """自动记忆重要信息

    Args:
        message: 要记录的信息
        type: 类型（decision, config, solution, general）

    Returns:
        记录的文件路径
    """
    memory_dir = Path("/root/clawd/memory")
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = memory_dir / f"{today}.md"

    # 类型映射到章节
    type_map = {
        "decision": "## 💡 决策",
        "config": "## ⚙️ 配置",
        "solution": "## ✅ 解决方案",
        "general": "## 📝 记录"
    }

    section = type_map.get(type, type_map["general"])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 写入文件
    with open(daily_file, 'a', encoding='utf-8') as f:
        f.write(f"\n\n{section}\n\n**时间**: {timestamp}\n\n{message}\n")

    return str(daily_file)


# CLI 接口
def main():
    import sys

    manager = MemoryManager()

    if len(sys.argv) < 2:
        print("用法:")
        print("  memory-manager.py list                    # 列出所有 memory skills")
        print("  memory-manager.py search <keyword>         # 搜索记忆")
        print("  memory-manager.py search <keyword> <skill> # 搜索指定 skill")
        print("  memory-manager.py get <skill>             # 获取 skill 内容")
        print("  memory-manager.py get <skill> <section>   # 获取章节")
        print("  memory-manager.py smart-load <context>     # 智能加载")
        print("  memory-manager.py index                    # 创建 daily memory 索引")
        print("  memory-manager.py memorize <message>       # 自动记忆")
        return

    command = sys.argv[1]

    if command == "list":
        skills = manager.memory_skills_list()
        print(f"✅ 找到 {len(skills)} 个 memory skills:\n")
        for skill in skills:
            print(f"  {skill['name']} ({skill['type']}, {skill['size']} bytes)")

    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ 需要搜索关键词")
            return

        keyword = sys.argv[2]
        skill_name = sys.argv[3] if len(sys.argv) > 3 else None

        results = manager.memory_search(keyword, skill_name)
        print(f"✅ 找到 {len(results)} 条匹配结果:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result['name']}:{result['line']}]")
            print(f"   {result['content'][:80]}...\n")

    elif command == "get":
        if len(sys.argv) < 3:
            print("❌ 需要 skill 名称")
            return

        skill_name = sys.argv[2]
        section = sys.argv[3] if len(sys.argv) > 3 else None

        content = manager.memory_get(skill_name, section)
        print(content)

    elif command == "smart-load":
        if len(sys.argv) < 3:
            print("❌ 需要上下文描述")
            return

        context = " ".join(sys.argv[2:])
        related = manager.memory_smart_load(context)
        print(f"✅ 建议加载的 memory skills:\n")
        for skill in related:
            print(f"  - {skill}")

    elif command == "index":
        index = create_daily_memory_index()
        if "error" in index:
            print(f"❌ {index['error']}")
            return
        print(f"✅ Daily memory 索引已创建:")
        print(f"  文件数: {index['total_files']}")
        print(f"  总行数: {index['summary']['total_lines']}")
        print(f"  最新: {index['summary']['latest_date']}")
        print(f"  索引: /root/clawd/memory/daily-index.json")

    elif command == "memorize":
        if len(sys.argv) < 3:
            print("❌ 需要记录的信息")
            return

        message = " ".join(sys.argv[2:])
        mem_type = "general"  # 默认类型

        # 自动检测类型
        if any(word in message.lower() for word in ["决定", "决策", "选择"]):
            mem_type = "decision"
        elif any(word in message.lower() for word in ["配置", "设置", "参数"]):
            mem_type = "config"
        elif any(word in message.lower() for word in ["解决", "修复", "方案"]):
            mem_type = "solution"

        file = auto_memorize(message, mem_type)
        print(f"✅ 已记忆到: {file} (类型: {mem_type})")


if __name__ == "__main__":
    main()
