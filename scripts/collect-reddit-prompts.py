#!/usr/bin/env python3
"""
Reddit AI 提示词收集脚本
从 r/prompts, r/ChatGPT, r/artificial 等子版块收集高质量 prompt
"""

import json
import requests
from datetime import datetime
from collections import Counter

# 配置
SUBREDDITS = [
    "prompts",
    "ChatGPT",
    "artificial",
    "machinelearning",
    "LanguageTechnology"
]

MAX_POSTS_PER_SUBREDDIT = 25  # 每个 subreddit 最多 25 条
OUTPUT_FILE = "/root/clawd/data/prompts/reddit-prompts.jsonl"
MIN_UPVOTES = 5  # 最少 5 个赞

# Reddit API (不需要 API key，使用公共 API）
REDDIT_API = "https://www.reddit.com"

def get_hot_posts(subreddit: str, limit: int = MAX_POSTS_PER_SUBREDDIT) -> list:
    """获取热门帖子"""
    url = f"{REDDIT_API}/r/{subreddit}/hot.json?limit={limit}"
    headers = {
        "User-Agent": "Clawdbot-Prompt-Collector/1.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        posts = []
        for item in data.get("data", {}).get("children", []):
            post = item.get("data", {})
            posts.append({
                "id": post.get("id"),
                "title": post.get("title", ""),
                "selftext": post.get("selftext", ""),
                "url": post.get("url", ""),
                "permalink": f"{REDDIT_API}{post.get('permalink', '')}",
                "author": post.get("author", ""),
                "subreddit": subreddit,
                "upvotes": post.get("ups", 0),
                "num_comments": post.get("num_comments", 0),
                "created_utc": post.get("created_utc", 0),
                "link_flair_text": post.get("link_flair_text", ""),
                "is_self": post.get("is_self", False)
            })
        return posts
    except Exception as e:
        print(f"⚠️  获取 {subreddit} 失败: {e}")
        return []

def is_prompt_related(post: dict) -> bool:
    """检查是否为 prompt 相关内容"""
    title = post.get("title", "").lower()
    text = post.get("selftext", "").lower()

    # Prompt 相关关键词
    prompt_keywords = [
        "prompt", "template", "system message",
        "instruction", "guideline", "example",
        "prompt engineering", "llm prompt"
    ]

    # 检查标题或内容是否包含关键词
    for keyword in prompt_keywords:
        if keyword in title or keyword in text:
            return True

    return False

def extract_prompt_from_post(post: dict) -> str:
    """从帖子中提取 prompt 内容"""
    text = post.get("selftext", "")
    if not text:
        return ""

    # 尝试提取代码块
    import re
    code_blocks = re.findall(r'```[\s\S]*?```', text)
    if code_blocks:
        return code_blocks[0]

    # 尝试提取引号中的内容
    if '""' in text or "'''" in text:
        if '""' in text:
            parts = text.split('""')
            if len(parts) > 1:
                return parts[1]
        else:
            parts = text.split("'''")
            if len(parts) > 1:
                return parts[1]

    # 返回主要内容（前 1000 字符）
    return text[:1000]

def calculate_quality_score(post: dict) -> int:
    """计算内容质量分数（0-100）"""
    score = 0

    # 点赞数评分（对数刻度，避免极端值）
    upvotes = post.get("upvotes", 0)
    if upvotes > 0:
        score += min(30, (upvotes ** 0.5) * 2)

    # 评论数评分
    comments = post.get("num_comments", 0)
    score += min(20, comments * 0.5)

    # 文本长度评分
    text = post.get("selftext", "")
    if len(text) > 100:
        score += 10
    if len(text) > 500:
        score += 10

    # 是否包含代码块
    if '```' in text or '``' in text:
        score += 20

    # 标题长度
    title = post.get("title", "")
    if 50 < len(title) < 200:
        score += 5

    # 是否是 self post（文本帖）
    if post.get("is_self", False):
        score += 10

    # 标签
    flair = (post.get("link_flair_text") or "").lower()
    if "prompt" in flair or "template" in flair:
        score += 10

    return min(100, score)

def main():
    print(f"\n{'='*60}")
    print(f"🔍 Reddit AI 提示词收集 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    all_posts = []

    # 收集所有 subreddits 的帖子
    for subreddit in SUBREDDITS:
        print(f"📂 r/{subreddit}...", end='', flush=True)

        posts = get_hot_posts(subreddit)
        print(f" {len(posts)} 条")

        # 过滤和评分
        for post in posts:
            # 过滤低质量帖子
            if post.get("upvotes", 0) < MIN_UPVOTES:
                continue

            # 检查是否为 prompt 相关
            if not is_prompt_related(post):
                continue

            # 计算质量分数
            quality_score = calculate_quality_score(post)

            # 提取 prompt 内容
            prompt_content = extract_prompt_from_post(post)

            # 标准化数据
            entry = {
                "source": "reddit",
                "source_id": f"reddit-{post['id']}",
                "title": post.get("title", ""),
                "content": prompt_content or post.get("selftext", "")[:1000],
                "full_text": post.get("selftext", ""),
                "url": post.get("permalink", ""),
                "author": post.get("author", ""),
                "metrics": {
                    "upvotes": post.get("upvotes", 0),
                    "comments": post.get("num_comments", 0),
                    "created_utc": post.get("created_utc", 0)
                },
                "subreddit": subreddit,
                "flair": post.get("link_flair_text", ""),
                "quality_score": quality_score,
                "collected_at": datetime.now().isoformat()
            }

            all_posts.append(entry)

    print(f"\n📊 总共收集: {len(all_posts)} 条高质量 prompt")

    if not all_posts:
        print("⚠️  没有收集到数据")
        return

    # 按质量分数排序
    all_posts.sort(key=lambda x: x["quality_score"], reverse=True)

    # 统计信息
    avg_score = sum(p["quality_score"] for p in all_posts) / len(all_posts)
    subreddits_count = Counter(p["subreddit"] for p in all_posts)

    print(f"\n📈 质量统计:")
    print(f"  平均分数: {avg_score:.1f}")
    print(f"  分数 >= 80: {sum(1 for p in all_posts if p['quality_score'] >= 80)} 条")
    print(f"  分数 >= 60: {sum(1 for p in all_posts if p['quality_score'] >= 60)} 条")

    print(f"\n📂 来源分布:")
    for sub, count in subreddits_count.most_common():
        print(f"  r/{sub}: {count} 条")

    # 保存数据
    import os
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # 追加到现有文件
    existing_entries = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    existing_entries.append(json.loads(line))

    # 合并并去重（基于 source_id）
    existing_ids = {e["source_id"] for e in existing_entries}
    new_entries = [e for e in all_posts if e["source_id"] not in existing_ids]

    all_data = existing_entries + new_entries

    # 写回文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for entry in all_data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f"\n💾 数据保存:")
    print(f"  新增: {len(new_entries)} 条")
    print(f"  总计: {len(all_data)} 条")
    print(f"  文件: {OUTPUT_FILE}")

    # 生成简要报告
    print(f"\n🏆 Top 10 Prompt:")
    for i, post in enumerate(all_posts[:10], 1):
        print(f"\n{i}. [{post['quality_score']}] {post['title'][:60]}...")
        print(f"   来源: r/{post['subreddit']} | 作者: @{post['author']}")
        print(f"   赞数: {post['metrics']['upvotes']} | 评论: {post['metrics']['comments']}")
        print(f"   链接: {post['url']}")

    print(f"\n{'='*60}")
    print(f"✅ Reddit 收集完成！")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
