#!/bin/bash
# ClawdHub 技能统计跟踪脚本
# 获取并记录本地技能的下载量和星数

set -e

# 配置
API_URL="https://www.clawhub.ai/api/v1/skills"
REGISTRY="https://www.clawhub.ai/api"
MEMORY_DIR="/root/clawd/memory/clawdhub-stats"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%s)

# 创建目录
mkdir -p "$MEMORY_DIR"

# 输出文件
OUTPUT_FILE="$MEMORY_DIR/stats-$DATE.json"
TEMP_FILE="/tmp/clawdhub-skills-$TIMESTAMP.json"

echo "=== ClawdHub 技能统计跟踪 ==="
echo "时间: $(date)"
echo ""

# 获取所有技能数据
echo "正在获取 ClawdHub 技能数据..."
if ! curl -s "$API_URL" -H "Accept: application/json" -o "$TEMP_FILE"; then
    echo "❌ 错误: 无法获取 ClawdHub 数据"
    exit 1
fi

if ! python3 -m json.tool "$TEMP_FILE" > /dev/null 2>&1; then
    echo "❌ 错误: 返回的 JSON 格式无效"
    cat "$TEMP_FILE"
    exit 1
fi

echo "✓ 成功获取技能数据"
echo ""

# 获取本地技能列表
LOCAL_SKILLS=()
if [ -d "/root/clawd/skills" ]; then
    for dir in /root/clawd/skills/*/; do
        if [ -d "$dir" ]; then
            slug=$(basename "$dir")
            LOCAL_SKILLS+=("$slug")
        fi
    done
fi

if [ -d "/root/.clawdbot/skills" ]; then
    for dir in /root/.clawdbot/skills/*/; do
        if [ -d "$dir" ]; then
            slug=$(basename "$dir")
            LOCAL_SKILLS+=("$slug")
        fi
    done
fi

# 去重
LOCAL_SKILLS=($(echo "${LOCAL_SKILLS[@]}" | tr ' ' '\n' | sort -u))

echo "找到 ${#LOCAL_SKILLS[@]} 个本地技能"
echo ""

# 生成本地技能列表的 JSON 数组
LOCAL_SKILLS_JSON=$(printf '%s\n' "${LOCAL_SKILLS[@]}" | jq -R . | jq -s .)

# 提取本地技能的统计信息
python3 << PYTHON_SCRIPT
import json
import sys
from datetime import datetime
from pathlib import Path

# 读取数据
with open('$TEMP_FILE', 'r') as f:
    data = json.load(f)

all_skills = data.get('items', [])
local_slugs = $LOCAL_SKILLS_JSON

# 提取本地技能统计
local_skills_stats = []
for skill in all_skills:
    slug = skill.get('slug', '')
    if slug in local_slugs:
        stats = skill.get('stats', {})
        local_skills_stats.append({
            'slug': slug,
            'displayName': skill.get('displayName', ''),
            'summary': skill.get('summary', ''),
            'downloads': stats.get('downloads', 0),
            'stars': stats.get('stars', 0),
            'comments': stats.get('comments', 0),
            'versions': stats.get('versions', 0),
            'updatedAt': skill.get('updatedAt', 0)
        })

# 排序
by_downloads = sorted(local_skills_stats, key=lambda x: x['downloads'], reverse=True)
by_stars = sorted(local_skills_stats, key=lambda x: x['stars'], reverse=True)

# 输出结果
result = {
    'timestamp': datetime.now().isoformat(),
    'date': '$DATE',
    'localSkills': local_skills_stats,
    'topByDownloads': by_downloads[:5],
    'topByStars': by_stars[:5]
}

# 保存到文件
with open('$OUTPUT_FILE', 'w') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(json.dumps(result, indent=2, ensure_ascii=False))
PYTHON_SCRIPT

echo ""
echo "✓ 统计信息已保存到: $OUTPUT_FILE"
echo ""

# 清理临时文件
rm -f "$TEMP_FILE"

# 生成人类可读的报告
python3 << REPORT_SCRIPT
import json

with open('$OUTPUT_FILE', 'r') as f:
    data = json.load(f)

print("=" * 60)
print("本地技能统计报告")
print("=" * 60)
print(f"时间: {data['timestamp']}")
print(f"总技能数: {len(data['localSkills'])}")
print()

# 下载量 Top 5
print("📥 下载量 Top 5:")
print("-" * 60)
for i, skill in enumerate(data['topByDownloads'], 1):
    print(f"{i}. {skill['displayName']} ({skill['slug']})")
    print(f"   下载量: {skill['downloads']} | 星数: {skill['stars']}")
    if skill['summary']:
        print(f"   {skill['summary'][:80]}...")
    print()

# 星数 Top 5
print("⭐ 星数 Top 5:")
print("-" * 60)
for i, skill in enumerate(data['topByStars'], 1):
    print(f"{i}. {skill['displayName']} ({skill['slug']})")
    print(f"   星数: {skill['stars']} | 下载量: {skill['downloads']}")
    if skill['summary']:
        print(f"   {skill['summary'][:80]}...")
    print()

# 所有技能总览
print("📊 所有本地技能:")
print("-" * 60)
for skill in sorted(data['localSkills'], key=lambda x: x['downloads'], reverse=True):
    print(f"• {skill['displayName']}: {skill['downloads']} 下载, {skill['stars']} 星")

print("=" * 60)
REPORT_SCRIPT
