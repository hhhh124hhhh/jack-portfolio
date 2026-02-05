#!/usr/bin/env python3
"""快速版：只发送已收集数据的统计，不做搜索"""

import json
import os
import subprocess
from datetime import datetime
from collections import Counter

OUTPUT_FILE = "/root/clawd/data/prompts/collected.jsonl"
SLACK_CHANNEL_ID = "C0ABSK92X4G"

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

    # 按搜索词统计
    queries = Counter(item.get("search_query", "unknown") for item in data)

    # 最新数据
    recent = sorted(data, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]

    # 高质量数据（score > 0.5）
    high_quality = [d for d in data if d.get("score", 0) > 0.5]

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    report = f"""📊 *AI 提示词数据报告* - {timestamp}

📈 *数据统计*
• 总数据量: {total} 条
• 高质量数据: {len(high_quality)} 条
• 独特关键词: {len(queries)} 个

🔍 *热门关键词*
"""

    for query, count in queries.most_common(5):
        report += f"• {query}: {count} 条\n"

    report += f"""
⭐ *最新 5 条*
"""

    for i, item in enumerate(recent, 1):
        title = item.get('title', 'N/A')[:50]
        score = item.get('score', 0)
        report += f"{i}. {title} (评分: {score:.2f})\n"

    report += f"""
💾 *数据文件*: `/root/clawd/data/prompts/collected.jsonl`
📅 *最后更新*: {max(item.get('timestamp', '') for item in data)[:19] if data else '无'}
"""

    return report

def send_slack_message(message: str):
    """发送 Slack 消息"""
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
            timeout=10
        )

        if result.returncode == 0:
            print("✅ Slack 消息发送成功")
            return True
        else:
            print(f"❌ Slack 失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏱️  Slack 发送超时")
        return False
    except Exception as e:
        print(f"❌ 发送错误: {e}")
        return False

def main():
    print(f"\n📊 加载数据...")
    data = load_data()

    print(f"✓ 加载 {len(data)} 条记录")

    print(f"\n📤 生成报告...")
    report = format_stats_report(data)

    print(f"\n📤 发送 Slack 报告... ", end='', flush=True)
    success = send_slack_message(report)

    if success:
        print(f"\n✅ 完成！")
    else:
        print(f"\n❌ 发送失败")

if __name__ == "__main__":
    main()
