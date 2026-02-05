#!/usr/bin/env python3
"""快速统计报告版（无搜索，优化超时）"""

import json
import os
import subprocess
from datetime import datetime
from collections import Counter

OUTPUT_FILE = "/root/clawd/data/prompts/collected.jsonl"
SLACK_CHANNEL_ID = "D0AB0J4QLAH"
SLACK_TIMEOUT = 20  # Slack 发送需要约 10 秒，设置 20 秒超时

def load_data() -> list:
    """加载数据"""
    if not os.path.exists(OUTPUT_FILE):
        return []

    entries = []
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries

def format_stats_report(data: list) -> str:
    """生成统计报告"""
    if not data:
        return """📊 *AI 提示词数据报告*

📁 暂无数据

运行收集脚本获取数据！"""

    total = len(data)
    queries = Counter(item.get("search_query", "unknown") for item in data)
    recent = sorted(data, key=lambda x: x.get("timestamp", ""), reverse=True)[:3]
    high_quality = [d for d in data if d.get("score", 0) > 0.5]

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    report = f"""📊 *AI 提示词数据报告* - {timestamp}

📈 *数据统计*
• 总数据量: {total} 条
• 高质量数据: {len(high_quality)} 条
• 独特关键词: {len(queries)} 个

🔍 *热门关键词*
"""

    for query, count in queries.most_common(3):
        report += f"• {query}: {count} 条\n"

    report += f"""
⭐ *最新 3 条*
"""

    for i, item in enumerate(recent, 1):
        title = item.get('title', 'N/A')[:45]
        score = item.get('score', 0)
        report += f"{i}. {title} ({score:.1f})\n"

    report += f"""
💾 数据文件: `/root/clawd/data/prompts/collected.jsonl`
"""

    return report

def send_slack_message(message: str):
    """发送 Slack 消息（带超时）"""
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
            timeout=SLACK_TIMEOUT
        )

        if result.returncode == 0:
            print("✅ Slack 消息发送成功")
            return True
        else:
            print(f"❌ Slack 失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  Slack 超时 (>{SLACK_TIMEOUT}s)")
        return False
    except Exception as e:
        print(f"❌ 发送错误: {e}")
        return False

def main():
    print(f"\n📊 快速统计报告")
    print(f"{'='*40}\n")

    print("📂 加载数据...", end='', flush=True)
    data = load_data()
    print(f" ✓ {len(data)} 条")

    if not data:
        print("⚠️  无数据，跳过发送")
        return

    print("📤 生成报告...", end='', flush=True)
    report = format_stats_report(data)
    print(" ✓")

    print("📤 发送 Slack (预计 ~10秒)...", end='', flush=True)
    success = send_slack_message(report)

    if success:
        print("\n✅ 完成！")
    else:
        print("\n❌ 发送失败")

if __name__ == "__main__":
    main()
