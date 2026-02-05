#!/usr/bin/env python3
"""
测试版本：只执行 2 个查询，用于快速验证
"""

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging
import requests

# 配置
DATA_DIR = Path("/root/clawd/data/prompts")
OUTPUT_DIR = DATA_DIR / "collected"
OUTPUT_FILE = OUTPUT_DIR / f"test-prompts-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
LOGS_DIR = Path("/root/clawd/logs")

# 创建目录
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# 日志配置
logger = logging.getLogger("test_collect_prompts")
logger.setLevel(logging.INFO)
log_handler = logging.FileHandler(LOGS_DIR / "test-collect-prompts.log", encoding='utf-8')
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(log_handler)
logger.addHandler(logging.StreamHandler())

# SearXNG 配置
SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8080")

# 测试用：只搜索 2 个查询
SEARCH_QUERIES = [
    "awesome-chatgpt-prompts github",
    "prompt engineering tutorial"
]

# 高质量域名白名单
HIGH_QUALITY_DOMAINS = {
    'github.com',
    'promptbase.com',
    'learnprompting.org',
}

# 低质量域名黑名单
LOW_QUALITY_DOMAINS = {
    'pinterest.com',
    'instagram.com',
    'tiktok.com',
    'facebook.com',
    'twitter.com',
}


def search_searxng(query: str, limit: int = 5) -> List[Dict]:
    """使用 SearXNG 搜索"""
    params = {
        "q": query,
        "format": "json",
        "categories": "general",
    }

    try:
        response = requests.get(
            f"{SEARXNG_URL}/search",
            params=params,
            timeout=30,
            verify=False
        )
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])[:limit]

        logger.info(f"搜索 '{query}': 找到 {len(results)} 个结果")

        return results

    except Exception as e:
        logger.error(f"搜索失败 '{query}': {e}")
        return []


def is_high_quality_url(url: str) -> bool:
    """判断 URL 是否来自高质量来源"""
    from urllib.parse import urlparse

    try:
        domain = urlparse(url).netloc.lower()

        # 检查黑名单
        if any(blacklisted in domain for blacklisted in LOW_QUALITY_DOMAINS):
            return False

        # 检查白名单
        if any(whitelisted in domain for whitelisted in HIGH_QUALITY_DOMAINS):
            return True

        # 默认允许
        return True

    except Exception:
        return True


def fetch_page_content(url: str, max_chars: int = 15000) -> Optional[str]:
    """获取页面内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        text = response.text

        # 移除 HTML 标签
        import html
        text = re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = html.unescape(text)

        # 清理空白
        text = re.sub(r'\s+', ' ', text).strip()

        return text[:max_chars]

    except Exception as e:
        logger.warning(f"获取页面失败 {url}: {e}")
        return None


def extract_prompts_from_content(content: str, max_prompts: int = 10) -> List[str]:
    """从内容中提取提示词"""
    prompts = []

    # 模式 1: 引号中的内容
    quote_patterns = [
        r'"([^"]{40,800})"',
        r"'([^']{40,800})'",
        r'`([^`]{40,800})`',
    ]

    for pattern in quote_patterns:
        matches = re.findall(pattern, content)
        prompts.extend(matches)

    # 模式 2: 冒号后面的描述性文本
    colon_patterns = [
        r'(?:prompt|Prompt|PROMPT|example|Example)[\s:]+([^.!?]{40,800})',
        r'(?:prompt|Prompt|PROMPT)\s*[:=]\s*([^\n]{40,800})',
    ]

    for pattern in colon_patterns:
        matches = re.findall(pattern, content)
        prompts.extend(matches)

    # 去重
    unique_prompts = list(dict.fromkeys(prompts))

    # 过滤质量
    filtered = []
    for p in unique_prompts:
        p_clean = p.strip()

        # 长度过滤
        if not (40 <= len(p_clean) <= 800):
            continue

        # 内容质量过滤
        alpha_ratio = sum(c.isalnum() or c.isspace() for c in p_clean) / len(p_clean)
        if alpha_ratio < 0.7:
            continue

        # 检查是否包含动作动词
        action_verbs = ['generate', 'write', 'create', 'design', 'build', 'make', 'act as', 'role', 'task']
        has_action = any(verb.lower() in p_clean.lower() for verb in action_verbs)
        if not has_action:
            continue

        filtered.append(p_clean)

    return filtered[:max_prompts]


def classify_prompt_type(prompt: str) -> str:
    """分类提示词类型"""
    prompt_lower = prompt.lower()

    image_keywords = [
        'image', 'photo', 'picture', 'portrait', 'painting', 'drawing',
        'illustration', 'midjourney', 'dall-e', 'stable diffusion',
        'render', 'visual', 'art', 'scene', 'landscape'
    ]

    video_keywords = [
        'video', 'animation', 'motion', 'animate', 'runway', 'pika',
        'kling', 'veo', 'clip', 'footage', 'film'
    ]

    text_keywords = [
        'write', 'essay', 'article', 'blog', 'content', 'story',
        'chatgpt', 'gpt', 'llm', 'text generation'
    ]

    image_score = sum(1 for kw in image_keywords if kw in prompt_lower)
    video_score = sum(1 for kw in video_keywords if kw in prompt_lower)
    text_score = sum(1 for kw in text_keywords if kw in prompt_lower)

    if video_score > image_score and video_score > text_score:
        return 'video-generation'
    elif image_score > text_score:
        return 'image-generation'
    elif text_score > 0:
        return 'text-generation'
    else:
        return 'general'


def calculate_quality_score(prompt: str) -> int:
    """计算提示词质量分数"""
    score = 0

    # 长度评分
    length = len(prompt)
    if 50 <= length <= 300:
        score += 30
    elif 301 <= length <= 500:
        score += 25
    elif 501 <= length <= 800:
        score += 15
    else:
        score += 5

    # 关键词评分
    quality_keywords = [
        'detailed', 'realistic', 'high quality', 'professional', 'creative',
        'specific', 'precise', 'clear', 'comprehensive', 'well-structured'
    ]
    score += min(20, sum(5 for kw in quality_keywords if kw in prompt.lower()))

    # 动作动词评分
    action_verbs = ['generate', 'create', 'write', 'design', 'build', 'make']
    score += min(15, sum(5 for verb in action_verbs if verb in prompt.lower()))

    # 结构评分
    if ',' in prompt:
        score += 10
    if ':' in prompt:
        score += 5
    if '\n' in prompt:
        score += 10

    return min(100, score)


def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("🔍 测试模式：使用 SearXNG 搜索 AI 提示词（仅 2 个查询）")
    logger.info("=" * 80)

    # 存储所有收集的提示词
    all_prompts = []
    seen_urls = set()

    # 遍历搜索查询
    for i, query in enumerate(SEARCH_QUERIES, 1):
        logger.info(f"\n[{i}/{len(SEARCH_QUERIES)}] 搜索: {query}")

        # 搜索
        results = search_searxng(query, limit=5)

        if not results:
            logger.warning(f"  没有找到结果")
            continue

        # 遍历结果
        for j, result in enumerate(results, 1):
            url = result.get('url', '')
            title = result.get('title', '')

            # 检查 URL 质量
            if not is_high_quality_url(url):
                logger.debug(f"  [{j}] 跳过低质量来源: {url}")
                continue

            # 检查是否已处理
            if url in seen_urls:
                logger.debug(f"  [{j}] 跳过已处理 URL: {url}")
                continue

            seen_urls.add(url)

            logger.info(f"  [{j}] 处理: {title}")
            logger.debug(f"      URL: {url}")

            # 获取页面内容
            content = fetch_page_content(url)

            if not content:
                logger.warning(f"      获取内容失败")
                continue

            # 提取提示词
            prompts = extract_prompts_from_content(content, max_prompts=10)

            if not prompts:
                logger.debug(f"      未找到提示词")
                continue

            logger.info(f"      找到 {len(prompts)} 个提示词")

            # 处理每个提示词
            for prompt in prompts:
                prompt_type = classify_prompt_type(prompt)
                quality_score = calculate_quality_score(prompt)

                prompt_data = {
                    'content': prompt,
                    'title': title,
                    'source': 'searxng',
                    'url': url,
                    'type': prompt_type,
                    'quality_score': quality_score,
                    'collected_at': datetime.now().isoformat(),
                    'search_query': query
                }

                all_prompts.append(prompt_data)

        # 搜索间隔
        time.sleep(2)

    # 保存结果
    logger.info(f"\n{'=' * 80}")
    logger.info(f"📊 测试完成！")
    logger.info(f"{'=' * 80}")
    logger.info(f"总共收集: {len(all_prompts)} 个提示词")

    # 写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for prompt in all_prompts:
            f.write(json.dumps(prompt, ensure_ascii=False) + '\n')

    logger.info(f"保存到: {OUTPUT_FILE}")

    # 统计信息
    type_counts = {}
    for prompt in all_prompts:
        ptype = prompt['type']
        type_counts[ptype] = type_counts.get(ptype, 0) + 1

    logger.info(f"\n类型分布:")
    for ptype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {ptype}: {count}")

    # 质量分布
    high_quality = sum(1 for p in all_prompts if p['quality_score'] >= 70)
    medium_quality = sum(1 for p in all_prompts if 50 <= p['quality_score'] < 70)
    low_quality = sum(1 for p in all_prompts if p['quality_score'] < 50)

    logger.info(f"\n质量分布:")
    logger.info(f"  高质量 (≥70): {high_quality}")
    logger.info(f"  中等 (50-69): {medium_quality}")
    logger.info(f"  低质量 (<50): {low_quality}")

    # 显示部分示例
    logger.info(f"\n📝 示例提示词（前 3 个）:")
    for i, prompt in enumerate(all_prompts[:3], 1):
        logger.info(f"\n{i}. [{prompt['type']}] 分数: {prompt['quality_score']}")
        logger.info(f"   {prompt['content'][:100]}...")
        logger.info(f"   来源: {prompt['url']}")

    logger.info(f"\n✅ 测试完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⏸️  用户中断")
    except Exception as e:
        logger.error(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
