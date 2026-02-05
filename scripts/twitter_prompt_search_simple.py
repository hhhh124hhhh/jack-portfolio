#!/usr/bin/env python3
"""
Twitter High-Value Prompt Search - Simplified
Uses SearXNG to find Twitter/X posts about AI prompts
"""

import os
import json
import re
import time
from datetime import datetime
import requests

# SearXNG URL
SEARXNG_URL = "http://127.0.0.1:8080"

# Search keywords
KEYWORDS = [
    "AI prompt engineering tips site:twitter.com OR site:x.com",
    "best ChatGPT prompts site:twitter.com OR site:x.com",
    "Claude prompt examples site:twitter.com OR site:x.com",
    "AI workflow automation site:twitter.com OR site:x.com",
    "prompt templates 2026 site:twitter.com OR site:x.com"
]

def clean_prompt_text(text):
    """Extract clean prompt text from tweet"""
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = ' '.join(text.split())
    return text

def evaluate_prompt_value(text):
    """Evaluate prompt value on A/B/C scale"""
    score = 0

    if 'step' in text.lower() or '步骤' in text:
        score += 2
    if 'example' in text.lower() or '示例' in text or '例子' in text:
        score += 2
    if 'template' in text.lower() or '模板' in text:
        score += 2
    if 'prompt:' in text.lower() or '提示词:' in text:
        score += 3
    if '```' in text or '"""' in text or "'''" in text:
        score += 2
    if 'act as' in text.lower() or '扮演' in text.lower():
        score += 2
    if 'you are' in text.lower() or '你是' in text.lower():
        score += 2

    if len(text) > 200:
        score += 1
    if len(text) > 400:
        score += 1

    if score >= 7:
        return 'A'
    elif score >= 4:
        return 'B'
    else:
        return 'C'

def search_searxng(query):
    """Search using SearXNG"""
    params = {
        'q': query,
        'format': 'json',
        'language': 'en'
    }

    try:
        response = requests.get(SEARXNG_URL + '/search', params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def process_result(result, query):
    """Process a single result"""
    url = result.get('url', '')
    title = result.get('title', '')
    content = result.get('content', '')

    # Check if it's Twitter/X
    if not ('twitter.com' in url or 'x.com' in url):
        return None

    # Extract tweet ID
    tweet_id_match = re.search(r'/status/(\d+)', url)
    if not tweet_id_match:
        return None

    text = title + ' ' + content
    cleaned_text = clean_prompt_text(text)

    # Check for prompt indicators
    prompt_indicators = [
        'prompt:', '提示词:', 'act as', '扮演', 'you are', '你是',
        'template:', '模板:', 'step 1', '第一步',
        '"""', "'''", '```', 'example', '示例'
    ]

    has_prompt = any(indicator.lower() in text.lower() for indicator in prompt_indicators)

    if not has_prompt:
        return None

    grade = evaluate_prompt_value(text)

    return {
        'tweet_id': tweet_id_match.group(1),
        'query': query,
        'text': text,
        'cleaned_text': cleaned_text,
        'likes': None,
        'url': url,
        'grade': grade,
        'scraped_at': datetime.now().isoformat()
    }

def main():
    print("🌐 Twitter High-Value Prompt Search")
    print("=" * 50)

    all_results = []

    for keyword in KEYWORDS:
        print(f"\n🔍 Searching: '{keyword}'")
        data = search_searxng(keyword)

        if data and 'results' in data:
            results = data['results']
            print(f"  Found {len(results)} total results")

            for i, result in enumerate(results[:15]):  # Top 15 per query
                processed = process_result(result, keyword)
                if processed:
                    all_results.append(processed)
                    print(f"    ✓ Found: {processed['grade']} | {processed['cleaned_text'][:50]}...")
        else:
            print("  No results")

        time.sleep(2)

    # Sort and deduplicate
    all_results.sort(key=lambda x: (x['grade'], len(x['text'])), reverse=True)

    seen_ids = set()
    unique_results = []
    for r in all_results:
        if r['tweet_id'] not in seen_ids:
            seen_ids.add(r['tweet_id'])
            unique_results.append(r)

    all_results = unique_results

    # Save to file
    date_str = datetime.now().strftime('%Y%m%d')
    output_file = f'/root/clawd/data/x-scraping/high-value-prompts-{date_str}.jsonl'

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for result in all_results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')

    print(f"\n✓ Saved {len(all_results)} results to {output_file}")

    # Print summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"Total: {len(all_results)}")
    print(f"Grade A: {sum(1 for r in all_results if r['grade'] == 'A')}")
    print(f"Grade B: {sum(1 for r in all_results if r['grade'] == 'B')}")
    print(f"Grade C: {sum(1 for r in all_results if r['grade'] == 'C')}")

    print("\n🏆 TOP PROMPTS:")
    for i, r in enumerate(all_results[:10], 1):
        print(f"\n{i}. [{r['grade']}] {r['url']}")
        print(f"   {r['cleaned_text'][:150]}...")

if __name__ == '__main__':
    main()
