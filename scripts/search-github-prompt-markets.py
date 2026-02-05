#!/usr/bin/env python3
"""搜索 GitHub 上的提示词市场和相关项目"""

import json
import time
from datetime import datetime
from pathlib import Path
import logging
import requests

# 配置
OUTPUT_DIR = Path("/root/clawd/data/github-prompts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("github_prompts_search")

# SearXNG 配置
SEARXNG_URL = "http://localhost:8080"

# 搜索查询 - 聚焦 GitHub 提示词市场和库
SEARCH_QUERIES = [
    # 已知的 awesome prompt 项目
    "site:github.com \"awesome-chatgpt-prompts\"",
    "site:github.com \"awesome-prompts\"",
    "site:github.com \"prompt-library\"",
    "site:github.com \"prompt-collection\"",

    # 提示词市场相关
    "site:github.com \"prompt marketplace\"",
    "site:github.com \"prompt store\"",
    "site:github.com \"prompt base\"",

    # AI 提示词库
    "site:github.com \"Midjourney prompts\"",
    "site:github.com \"Stable Diffusion prompts\"",
    "site:github.com \"DALL-E prompts\"",
    "site:github.com \"ChatGPT prompts\"",

    # 视频生成提示词
    "site:github.com \"video generation prompts\"",
    "site:github.com \"Sora prompts\"",
    "site:github.com \"Runway ML prompts\"",
    "site:github.com \"Veo prompts\"",

    # 电商和商业
    "site:github.com \"e-commerce prompts\"",
    "site:github.com \"marketing prompts\"",
    "site:github.com \"product photography prompts\"",
]


def search_searxng(query: str, limit: int = 15) -> list:
    """使用 SearXNG 搜索"""
    try:
        params = {
            "q": query,
            "format": "json",
            "language": "auto",
            "engines": "brave,wikipedia",
        }

        response = requests.get(f"{SEARXNG_URL}/search", params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get('results', [])

        logger.info(f"  搜索结果: {len(results)} 条")

        return results[:limit]

    except Exception as e:
        logger.error(f"  搜索失败: {e}")
        return []


def extract_prompts_from_readme(url: str) -> dict:
    """从 GitHub README 提取提示词"""
    try:
        # 使用 GitHub API 获取 README
        api_url = url.replace("github.com", "api.github.com/repos")
        api_url = f"{api_url}/readme"

        # 简单的 HTML 抓取（如果 API 失败）
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        content = response.text

        # 尝试提取提示词相关的部分
        # 这只是一个简单的实现，实际可能需要更复杂的解析

        return {
            "url": url,
            "has_prompts": "prompt" in content.lower(),
            "content_length": len(content),
            "extracted": False
        }

    except Exception as e:
        logger.warning(f"  提取失败 {url}: {e}")
        return {
            "url": url,
            "has_prompts": False,
            "content_length": 0,
            "extracted": False
        }


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("搜索 GitHub 提示词市场")
    logger.info("=" * 50)

    results = []

    for i, query in enumerate(SEARCH_QUERIES, 1):
        logger.info(f"\n[{i}/{len(SEARCH_QUERIES)}] 搜索: {query}")

        # 搜索
        search_results = search_searxng(query)

        # 提取信息
        for result in search_results:
            url = result.get('url', '')
            title = result.get('title', '')
            snippet = result.get('content', '')

            # 只保留 GitHub URL
            if 'github.com' not in url:
                continue

            # 提取提示词
            prompt_info = extract_prompts_from_readme(url)

            item = {
                "query": query,
                "url": url,
                "title": title,
                "snippet": snippet,
                "has_prompts": prompt_info['has_prompts'],
                "content_length": prompt_info['content_length'],
                "timestamp": datetime.now().isoformat()
            }

            results.append(item)
            logger.info(f"  添加: {title[:50]}")

        # 避免请求过快
        time.sleep(2)

    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = OUTPUT_DIR / f"github-prompt-markets-{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "total_results": len(results),
            "queries_used": len(SEARCH_QUERIES),
            "results": results
        }, f, indent=2, ensure_ascii=False)

    logger.info(f"\n✅ 完成！共找到 {len(results)} 个相关项目")
    logger.info(f"保存到: {output_file}")

    # 统计
    has_prompts_count = sum(1 for r in results if r['has_prompts'])
    logger.info(f"包含提示词的项目: {has_prompts_count}/{len(results)}")


if __name__ == "__main__":
    main()
