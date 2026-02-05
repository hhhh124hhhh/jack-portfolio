#!/usr/bin/env python3
"""收集 AI 提示词数据并通过 Clawdbot 发送 Slack 报告"""

import json
import os
import subprocess
from datetime import datetime

SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://localhost:8080")
OUTPUT_FILE = "/root/clawd/data/prompts/collected.jsonl"
SLACK_CHANNEL_ID = "C0ABSK92X4G"  # 你的 Slack 频道 ID

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

    # 添加 TOP 3 高质量结果
    top_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)[:3]

    for i, result in enumerate(top_results, 1):
        message += f"\n*{i}. {result.get('title', 'N/A')}*\n"
        message += f"🔗 {result.get('url', '')}\n"

        if result.get('content'):
            preview = result['content'][:150] + "..." if len(result['content']) > 150 else result['content']
            message += f"_{preview}_\n"

    message += f"\n💾 *数据文件*: `/root/clawd/data/prompts/collected.jsonl`"

    return message

def send_slack_message(message: str):
    """通过 Clawdbot 发送 Slack 消息"""
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
            timeout=30
        )

        if result.returncode == 0:
            print("✅ Slack 消息发送成功")
        else:
            print(f"❌ Slack 消息发送失败: {result.stderr}")
    except Exception as e:
        print(f"❌ 发送错误: {e}")

def main():
    timestamp = datetime.now().isoformat()
    all_results = []

    print(f"\n{'='*50}")
    print(f"🤖 AI 提示词收集任务开始")
    print(f"{'='*50}\n")

    for keyword in KEYWORDS:
        print(f"🔍 搜索: {keyword}")
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
            print(f"  [{idx}] {result.get('title', 'N/A')[:50]}")

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

    print(f"\n✅ 收集完成！")
    print(f"📁 新数据: {len(all_results)} 条")
    print(f"📊 总数据量: {len(all_data)} 条")

    # 发送 Slack 报告
    if all_results:
        print(f"\n📤 发送 Slack 报告...")
        slack_message = format_slack_message(all_results)
        send_slack_message(slack_message)
    else:
        print(f"\n⚠️  本次未收集到新数据，跳过 Slack 消息")

if __name__ == "__main__":
    main()
