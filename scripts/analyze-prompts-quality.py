#!/usr/bin/env python3
"""
分析提示词收集质量，识别问题并生成报告
"""

import json
from pathlib import Path
from collections import Counter
import re

DATA_FILE = Path("/root/clawd/data/prompts/collected/test-prompts-20260131-152033.jsonl")

# 读取数据
prompts = []
with open(DATA_FILE) as f:
    for line in f:
        prompts.append(json.loads(line))

print(f"总共收集了 {len(prompts)} 条提示词")
print()

# 1. 检查重复（基于 content）
content_hashes = {}
duplicates = []
for i, p in enumerate(prompts):
    content_hash = hash(p['content'])
    if content_hash in content_hashes:
        duplicates.append((content_hashes[content_hash], i))
    else:
        content_hashes[content_hash] = i

if duplicates:
    print(f"🔍 发现 {len(duplicates)} 组重复内容：")
    for dup_idx, dup2 in duplicates:
        p1 = prompts[dup_idx]
        p2 = prompts[dup2]
        print(f"  重复 #{dup_idx} 和 #{dup2}")
        print(f"    URL: {p1['url']}")
        print(f"    内容: {p1['content'][:50]}...")
        print()
else:
    print("✅ 没有发现完全重复的内容")
print()

# 2. 检查截断问题
truncated = []
for i, p in enumerate(prompts):
    content = p['content']
    # 检查是否以不完整的内容结尾
    if len(content) > 20 and content[-20:].count(' ') < 2:
        truncated.append(i)

if truncated:
    print(f"🔍 发现 {len(truncated)} 条可能截断的内容（索引）：{truncated[:10]}...")
    for idx in truncated[:3]:
        p = prompts[idx]
        print(f"\n  示例 #{idx}:")
        print(f"    URL: {p['url']}")
        print(f"    内容末尾: {p['content'][-100:]}")
else:
    print("✅ 没有发现明显的截断问题")
print()

# 3. 检查无关内容（导航栏、页脚）
# 导航栏常见词
nav_keywords = ['Home', 'About', 'GitHub', 'Discord', 'Login', 'Services', 'Contact', 'Privacy']
footer_keywords = ['Copyright', 'All rights reserved', 'Terms of Service', 'Privacy Policy']

unrelated = []
for i, p in enumerate(prompts):
    content = p['content']
    # 如果内容太短且包含导航关键词
    if len(content) < 100 and any(kw in content for kw in nav_keywords):
        unrelated.append((i, 'nav'))
    # 如果包含页脚关键词
    if any(kw in content for kw in footer_keywords):
        unrelated.append((i, 'footer'))

if unrelated:
    print(f"🔍 发现 {len(set(i for i, _ in unrelated))} 条可能无关的内容")
    nav_count = len(set(i for i, t in unrelated if t == 'nav'))
    footer_count = len(set(i for i, t in unrelated if t == 'footer'))
    print(f"  导航栏类: {nav_count} 条")
    print(f"  页脚类: {footer_count} 条")
    print("\n示例:")
    for idx, type_ in unrelated[:3]:
        p = prompts[idx]
        print(f"\n  #{idx} ({type_}):")
        print(f"    URL: {p['url']}")
        print(f"    内容: {p['content'][:80]}...")
else:
    print("✅ 没有发现明显的无关内容")
print()

# 4. 质量评分分析
scores = [p['quality_score'] for p in prompts]
avg_score = sum(scores) / len(scores)
print(f"📊 质量评分统计：")
print(f"  平均分: {avg_score:.1f}")
print(f"  最高分: {max(scores)}")
print(f"  最低分: {min(scores)}")
print(f"  评分分布: {sorted(Counter(scores).items())}")
print()

# 5. 长度分析
lengths = [len(p['content']) for p in prompts]
avg_length = sum(lengths) / len(lengths)
print(f"📏 内容长度统计：")
print(f"  平均长度: {avg_length:.0f} 字符")
print(f"  最长: {max(lengths)}")
print(f"  最短: {min(lengths)}")
print(f"  < 50 字符: {sum(1 for l in lengths if l < 50)} 条")
print(f"  > 500 字符: {sum(1 for l in lengths if l > 500)} 条")
print()

# 6. URL 统计
urls = [p['url'] for p in prompts]
url_counter = Counter(urls)
print(f"🌐 URL 统计：")
print(f"  唯一 URL: {len(url_counter)}")
print(f"  最常见 URL:")
for url, count in url_counter.most_common(5):
    print(f"    {url} ({count} 次)")
