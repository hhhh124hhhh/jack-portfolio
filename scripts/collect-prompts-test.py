#!/usr/bin/env python3
"""测试使用 SearXNG 收集 AI 提示词数据"""

import json
import os
from datetime import datetime
import subprocess

SEARXNG_URL = "http://localhost:8080"
OUTPUT_FILE = "/root/clawd/data/prompts/collected.jsonl"

KEYWORDS = [
    "AI prompt engineering tips",
    "ChatGPT prompts",
    "Claude prompts",
    "best AI prompts 2026",
    "prompt templates"
]

def search_searxng(query: str, limit: int = 5) -> dict:
    """使用 SearXNG 搜索"""
    env = os.environ.copy()
    env["SEARXNG_URL"] = SEARXNG_URL

    result = subprocess.run(
        ["python3", "/root/clawd/skills/searxng/scripts/searxng.py", "search", query, "-n", str(limit), "--format", "json"],
        capture_output=True,
        text=True,
        env=env
    )

    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        print(f"Error searching for '{query}': {result.stderr}")
        return {"results": []}

def main():
    timestamp = datetime.now().isoformat()
    all_results = []

    for keyword in KEYWORDS:
        print(f"\n🔍 搜索: {keyword}")
        data = search_searxng(keyword, limit=5)

        for idx, result in enumerate(data.get("results", []), 1):
            entry = {
                "timestamp": timestamp,
                "search_query": keyword,
                "result_index": idx,
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "engine": result.get("engine", ""),
                "score": result.get("score", 0)
            }
            all_results.append(entry)
            print(f"  [{idx}] {result.get('title', 'N/A')}")

    # 保存到 JSONL 文件
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # 如果文件存在，先读取现有内容
    existing_entries = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    existing_entries.append(json.loads(line))

    # 合并新旧数据
    all_data = existing_entries + all_results

    # 写回文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for entry in all_data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"\n✅ 完成！共收集 {len(all_results)} 条新数据")
    print(f"📁 保存到: {OUTPUT_FILE}")
    print(f"📊 总数据量: {len(all_data)} 条")

    # 简单的质量评估
    print(f"\n📈 质量评估:")
    avg_score = sum(r.get("score", 0) for r in all_results) / len(all_results) if all_results else 0
    print(f"  - 平均相关性分数: {avg_score:.2f}")
    print(f"  - 有完整内容的: {sum(1 for r in all_results if r.get('content'))} 条")
    print(f"  - 有 URL 的: {sum(1 for r in all_results if r.get('url'))} 条")

if __name__ == "__main__":
    main()
