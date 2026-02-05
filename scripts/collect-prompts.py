#!/usr/bin/env python3
"""
AI Prompts Collector
定期收集 AI 提示词相关信息
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("/root/clawd/data/prompts")
COLLECTED_FILE = DATA_DIR / "collected.jsonl"

# 创建目录
DATA_DIR.mkdir(parents=True, exist_ok=True)

def run_clawdbot_eval(js_code):
    """运行 clawdbot eval 命令"""
    try:
        result = subprocess.run(
            ["clawdbot", "eval", js_code],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.stdout:
            return json.loads(result.stdout)
        return None
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        print(f"Error running clawdbot eval: {e}")
        return None

def search_prompts():
    """搜索 AI prompts 相关内容"""
    print("🔍 Searching for AI prompts...")

    queries = [
        "AI prompt engineering tips",
        "ChatGPT prompts",
        "Claude prompts",
        "best AI prompts 2026",
        "prompt templates"
    ]

    results = []
    for query in queries:
        print(f"  - {query}")
        js_code = f'await tool("web_search", {{ query: "{query}", count: 5 }})'
        data = run_clawdbot_eval(js_code)

        if data and 'results' in data:
            results.append({
                "query": query,
                "result_count": len(data.get('results', [])),
                "results": data.get('results', [])
            })
        else:
            results.append({
                "query": query,
                "result_count": 0,
                "error": "No results or error"
            })

    return results

def main():
    """主函数"""
    print("🚀 Starting AI Prompts Collection...")
    print(f"📅 Date: {datetime.utcnow().isoformat()}")

    # 搜索 AI prompts
    search_results = search_prompts()

    # 构建数据对象
    data = {
        "type": "search",
        "timestamp": datetime.utcnow().isoformat(),
        "queries_count": len(search_results),
        "data": search_results
    }

    # 保存到文件
    with open(COLLECTED_FILE, 'a') as f:
        f.write(json.dumps(data) + '\n')

    print(f"✅ Saved to {COLLECTED_FILE}")
    print(f"✨ Collection complete! ({len(search_results)} queries)")

if __name__ == "__main__":
    main()
