#!/usr/bin/env python3
"""
Hacker News AI 相关内容收集脚本
从 Hacker News 获取 AI 相关的文章和讨论
"""

import json
import requests
from datetime import datetime
from typing import List, Dict

# 配置
HN_API = "https://hn.algolia.com/api/v1"
SEARCH_QUERIES = [
    "prompt engineering",
    "ChatGPT prompt",
    "AI prompt template",
    "LLM prompt",
    "prompt best practices"
]

OUTPUT_FILE = "/root/clawd/data/prompts/hacker-news-ai.jsonl"
MIN_SCORE = 10  # 最少 10 分（HN 评分）

def search_hn(query: str, limit: int = 20) -> List[Dict]:
    """搜索 Hacker News"""
    url = f"{HN_API}/search"
    params = {
        "query": query,
        "hitsPerPage": limit,
        "tags": "story"  # 只获取故事
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        hits = data.get("hits", [])
        articles = []
        
        for hit in hits:
            articles.append({
                "id": hit.get("objectID", ""),
                "title": hit.get("title", ""),
                "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                "author": hit.get("author", ""),
                "points": hit.get("points", 0),
                "num_comments": hit.get("num_comments", 0),
                "created_at": hit.get("created_at", ""),
                "query": query
            })
        
        return articles
    except Exception as e:
        print(f"⚠️  搜索 '{query}' 失败: {e}")
        return []

def extract_prompt_from_text(text: str) -> str:
    """尝试从文本中提取 prompt"""
    if not text:
        return ""
    
    # HN 文章通常没有完整 prompt，返回空或标题
    # 但如果有代码块，可以提取
    import re
    code_blocks = re.findall(r'```[\s\S]*?```', text)
    
    if code_blocks:
        return code_blocks[0]
    
    return ""

def is_prompt_related(article: Dict) -> bool:
    """检查是否为 prompt 相关内容"""
    title = article.get("title", "").lower()
    url = article.get("url", "").lower()
    
    # Prompt 相关关键词
    prompt_keywords = [
        "prompt", "template", "example", "guide",
        "prompt engineering", "prompt template",
        "llm prompt", "gpt prompt"
    ]
    
    for keyword in prompt_keywords:
        if keyword in title or keyword in url:
            return True
    
    return False

def calculate_quality_score(article: Dict) -> int:
    """计算文章质量分数（0-100）"""
    score = 0
    
    # HN 评分
    points = article.get("points", 0)
    if points > 0:
        score += min(30, points)
    
    # 评论数
    comments = article.get("num_comments", 0)
    score += min(20, comments * 0.5)
    
    # 标题长度
    title = article.get("title", "")
    if 50 < len(title) < 100:
        score += 10
    
    # URL 是否包含相关关键词
    url = article.get("url", "")
    if "github.com" in url or "medium.com" in url or "substack.com" in url:
        score += 10
    
    # 搜索词的相关性
    query = article.get("query", "").lower()
    if "prompt" in query:
        score += 10
    if "engineering" in query:
        score += 10
    
    return min(100, score)

def main():
    print(f"\n{'='*60}")
    print(f"🔍 Hacker News AI 内容收集")
    print(f"{'='*60}\n")
    
    all_articles = []
    
    # 搜索所有查询
    for query in SEARCH_QUERIES:
        print(f"🔎 '{query}'...", end='', flush=True)
        
        articles = search_hn(query, limit=10)
        
        # 过滤 prompt 相关内容
        prompt_articles = [a for a in articles if is_prompt_related(a)]
        
        print(f" {len(prompt_articles)} 条相关文章")
        
        # 评分
        for article in prompt_articles:
            article["quality_score"] = calculate_quality_score(article)
        
        all_articles.extend(prompt_articles)
    
    print(f"\n📊 总共收集: {len(all_articles)} 条文章")
    
    if not all_articles:
        print("⚠️  没有收集到数据")
        return
    
    # 统计
    avg_score = sum(a.get("quality_score", 0) for a in all_articles) / len(all_articles)
    queries_count = {}
    for a in all_articles:
        query = a.get("query", "unknown")
        queries_count[query] = queries_count.get(query, 0) + 1
    
    print(f"\n📈 质量统计:")
    print(f"  平均分数: {avg_score:.1f}")
    print(f"  高质量（≥80）: {sum(1 for a in all_articles if a.get('quality_score', 0) >= 80)} 条")
    print(f"  中等质量（≥60）: {sum(1 for a in all_articles if a.get('quality_score', 0) >= 60)} 条")
    
    print(f"\n🔍 查询分布:")
    for query, count in queries_count.items():
        print(f"  '{query}': {count} 条")
    
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
    
    # 去重
    existing_ids = {e["id"] for e in existing_entries}
    new_entries = [e for e in all_articles if e["id"] not in existing_ids]
    
    all_data = existing_entries + new_entries
    
    # 写回文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for entry in all_data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"\n💾 数据保存:")
    print(f"  新增: {len(new_entries)} 条")
    print(f"  总计: {len(all_data)} 条")
    print(f"  文件: {OUTPUT_FILE}")
    
    # 显示 Top 10
    print(f"\n🏆 Top 10 文章:")
    top_articles = sorted(all_articles, key=lambda x: x.get("quality_score", 0), reverse=True)[:10]
    
    for i, article in enumerate(top_articles, 1):
        print(f"\n{i}. [{article.get('quality_score', 0)}] {article.get('title', 'N/A')[:60]}...")
        print(f"   来源: Hacker News | 作者: @{article.get('author', 'N/A')}")
        print(f"   评分: {article.get('points', 0)} | 评论: {article.get('num_comments', 0)}")
        print(f"   链接: {article.get('url', 'N/A')}")
    
    print(f"\n{'='*60}")
    print(f"✅ Hacker News 收集完成！")
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
