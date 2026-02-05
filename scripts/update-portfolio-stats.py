#!/usr/bin/env python3
"""
自动更新个人主页统计数据
"""

import re
import json
from datetime import datetime
from pathlib import Path

# 配置
PORTFOLIO_DIR = Path("/root/clawd/jack-portfolio")
INDEX_FILE = PORTFOLIO_DIR / "index.html"
STATS_FILE = PORTFOLIO_DIR / "stats.json"


def load_stats():
    """加载当前统计数据"""
    if STATS_FILE.exists():
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "skills": 100,
            "automation_flows": 50,
            "community_participation": "30K+",
            "curiosity": "∞",
            "last_updated": None
        }


def calculate_skills():
    """计算技能数量"""
    # 从实际数据源计算
    # 这里简化处理，实际可以从多个源收集
    return 100


def calculate_automation_flows():
    """计算自动化流程数量"""
    # 检查 cron 任务、脚本等
    # 这里简化处理
    return 50


def get_community_participation():
    """获取社区参与度"""
    # 从 Moltbot 等社区获取数据
    return "30K+"


def update_html_stats(stats):
    """更新 HTML 中的统计数据"""
    if not INDEX_FILE.exists():
        print(f"❌ 找不到 index.html: {INDEX_FILE}")
        return False

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 更新统计数据
    content = re.sub(
        r'<div class="stat-number">(\d+)</div>\s*<div class="stat-label">AI 技能开发</div>',
        f'<div class="stat-number">{stats["skills"]}</div>\n                  <div class="stat-label">AI 技能开发</div>',
        content
    )

    content = re.sub(
        r'<div class="stat-number">(\d+)</div>\s*<div class="stat-label">自动化流程</div>',
        f'<div class="stat-number">{stats["automation_flows"]}</div>\n                  <div class="stat-label">自动化流程</div>',
        content
    )

    content = re.sub(
        r'<div class="stat-number">([^<]+)</div>\s*<div class="stat-label">Moltbot 社区参与</div>',
        f'<div class="stat-number">{stats["community_participation"]}</div>\n                  <div class="stat-label">Moltbot 社区参与</div>',
        content
    )

    content = re.sub(
        r'<div class="stat-number">([^<]+)</div>\s*<div class="stat-label">技术好奇心</div>',
        f'<div class="stat-number">{stats["curiosity"]}</div>\n                  <div class="stat-label">技术好奇心</div>',
        content
    )

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    return True


def main():
    """主函数"""
    print("📊 更新个人主页统计数据...")

    # 加载当前统计
    stats = load_stats()
    print(f"当前统计: {json.dumps(stats, indent=2)}")

    # 计算新统计
    new_stats = {
        "skills": calculate_skills(),
        "automation_flows": calculate_automation_flows(),
        "community_participation": get_community_participation(),
        "curiosity": stats["curiosity"],
        "last_updated": datetime.now().isoformat()
    }

    print(f"新统计: {json.dumps(new_stats, indent=2)}")

    # 检查是否有变化
    if stats == new_stats:
        print("✅ 统计数据无变化，无需更新")
        return

    # 更新 HTML
    if update_html_stats(new_stats):
        # 保存新统计
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_stats, f, indent=2, ensure_ascii=False)

        print("✅ 统计数据已更新")
    else:
        print("❌ 更新失败")


if __name__ == "__main__":
    main()
