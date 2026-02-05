#!/usr/bin/env python3
"""优化版：带超时和进度反馈的 Slack 报告"""

import json
import os
import subprocess
import requests
from datetime import datetime

SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://localhost:8080")
OUTPUT_FILE = "/root/clawd/data/prompts/collected.jsonl"
SLACK_CHANNEL_ID = "C0ABSK92X4G"

# 降低搜索次数和结果数，减少卡顿
KEYWORDS = [
    "ChatGPT prompts",
    "Claude prompts",
    "AI prompt engineering"
]

def search_searxng_direct(query: str, limit: int = 3, timeout: int = 15) -> dict:
    """直接使用 HTTP API，避免 subprocess 开销"""
    try:
        params = {
            "q": query,
            "format": "json",
            "engines": "google,bing,duckduckgo"
        }
        response = requests.get(
            f"{SEARXNG_URL}/search",
            params=params,
            timeout=timeout
        )
        return response.json()
    except requests.Timeout:
        print(f"⏱️  搜索超时: {query}")
        return {"results": []}
    except Exception as e:
        print(f"❌ 搜索错误 '{query}': {e}")
        return {"results": []}

def format_slack_message(results: list) -> str:
    """格式化 Slack 消息"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    avg_score = sum(r.get('score', 0) for r in results) / len(results) if results else 0

    message = f"""🤖 *AI 提示词收集报告* - {timestamp}

📊 *统计信息*
• 新收集: {len(results)} 条
• 平均分数: {avg_score:.2f}
• 有完整内容: {sum(1 for r in results if r.get('content'))} 条

"""

    # 只显示 TOP 2
    top_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)[:2]

    for i, result in enumerate(top_results, 1):
        title = result.get('title', 'N/A')[:60]
        message += f"\n*{i}. {title}*\n"
        message += f"🔗 {result.get('url', '')}\n"

    message += f"\n💾 *数据文件*: `/root/clawd/data/prompts/collected.jsonl`"

    return message

def send_slack_message(message: str, timeout: int = 10):
    """发送 Slack 消息，带超时"""
    try:
        result = subprocess.run(
            [
                "clawdbot", "message", "send",
                "--channel", "slack",
                "--target", SLACK_CHANNEL_ID,
                "--message", message
            ],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            print("✅ Slack 消息发送成功")
        else:
            print(f"❌ Slack 失败: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⏱️  Slack 发送超时")
    except Exception as e:
        print(f"❌ 发送错误: {e}")

def main():
    start_time = datetime.now()
    print(f"\n{'='*50}")
    print(f"🚀 开始收集 - {start_time.strftime('%H:%M:%S')}")
    print(f"{'='*50}\n")

    timestamp = datetime.now().isoformat()
    all_results = []

    for idx, keyword in enumerate(KEYWORDS, 1):
        print(f"[{idx}/{len(KEYWORDS)}] 🔍 {keyword}... ", end='', flush=True)

        data = search_searxng_direct(keyword, limit=3, timeout=10)

        results = data.get("results", [])
        print(f"✓ {len(results)} 条")

        for r_idx, result in enumerate(results, 1):
            entry = {
                "timestamp": timestamp,
                "search_query": keyword,
                "result_index": r_idx,
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "engine": result.get("engine", ""),
                "score": result.get("score", 0)
            }
            all_results.append(entry)

    # 保存数据
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    existing_entries = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    existing_entries.append(json.loads(line))

    all_data = existing_entries + all_results

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for entry in all_data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    elapsed = (datetime.now() - start_time).total_seconds()

    print(f"\n✅ 完成！耗时 {elapsed:.1f} 秒")
    print(f"📁 新数据: {len(all_results)} 条 | 总计: {len(all_data)} 条")

    # 发送 Slack（只有新数据时）
    if all_results:
        print(f"\n📤 发送 Slack 报告... ", end='', flush=True)
        slack_message = format_slack_message(all_results)
        send_slack_message(slack_message)
    else:
        print(f"\n⚠️  无新数据，跳过发送")

if __name__ == "__main__":
    main()
