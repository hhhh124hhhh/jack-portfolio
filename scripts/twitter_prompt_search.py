#!/usr/bin/env python3
"""
Twitter High-Value Prompt Search
Searches for AI prompt engineering tweets with high engagement
"""

import os
import json
import time
import re
from datetime import datetime
import requests

# Load API key from environment
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')

if not TWITTER_API_KEY:
    print("Error: TWITTER_API_KEY not found in environment")
    exit(1)

# Twitter API v2 endpoints
SEARCH_URL = "https://api.twitterapi.io/twitter/tweet/search"

# Search keywords
KEYWORDS = [
    "AI prompt engineering tips",
    "best ChatGPT prompts",
    "Claude prompt examples",
    "AI workflow automation",
    "prompt templates 2026"
]

def clean_prompt_text(text):
    """Extract clean prompt text from tweet"""
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove mentions
    text = re.sub(r'@\w+', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def evaluate_prompt_value(text, likes):
    """Evaluate prompt value on A/B/C scale"""
    score = 0

    # Check for specific indicators
    if 'step' in text.lower() or '步骤' in text:
        score += 2
    if 'example' in text.lower() or '示例' in text or '例子' in text:
        score += 2
    if 'template' in text.lower() or '模板' in text:
        score += 2
    if 'prompt:' in text.lower() or '提示词:' in text:
        score += 3
    if '```' in text or '"""' in text or "'''" in text:
        score += 2  # Code block indicates actual prompt

    # Engagement bonus
    if likes > 100:
        score += 1
    if likes > 500:
        score += 1

    # Length check (longer tweets likely have more content)
    if len(text) > 200:
        score += 1
    if len(text) > 400:
        score += 1

    # Grade assignment
    if score >= 7:
        return 'A'
    elif score >= 4:
        return 'B'
    else:
        return 'C'

def search_twitter(query, max_results=50):
    """Search Twitter for tweets matching query"""
    headers = {
        'X-API-Key': TWITTER_API_KEY,
        'Content-Type': 'application/json'
    }

    params = {
        'query': query,
        'max_results': max_results,
        'sort_order': 'relevancy',
        'tweet_fields': ['created_at', 'public_metrics', 'author_id']
    }

    try:
        response = requests.get(SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching for '{query}': {e}")
        return None

def process_results(data, query):
    """Process search results and filter high-value tweets"""
    if not data or 'data' not in data:
        return []

    results = []

    for tweet in data['data']:
        likes = tweet.get('public_metrics', {}).get('like_count', 0)

        # Filter by likes > 50
        if likes <= 50:
            continue

        text = tweet.get('text', '')
        cleaned_text = clean_prompt_text(text)

        # Check if it contains actual prompt content
        # Look for indicators of prompt content
        prompt_indicators = [
            'prompt:', '提示词:', 'Act as', '扮演', 'You are', '你是',
            'template:', '模板:', 'step 1', '第一步',
            '"""', "'''", '```', 'example', '示例'
        ]

        has_prompt = any(indicator.lower() in text.lower() for indicator in prompt_indicators)

        if not has_prompt:
            continue

        # Evaluate value
        grade = evaluate_prompt_value(text, likes)

        result = {
            'tweet_id': tweet.get('id'),
            'query': query,
            'text': text,
            'cleaned_text': cleaned_text,
            'likes': likes,
            'retweets': tweet.get('public_metrics', {}).get('retweet_count', 0),
            'replies': tweet.get('public_metrics', {}).get('reply_count', 0),
            'created_at': tweet.get('created_at'),
            'author_id': tweet.get('author_id'),
            'url': f"https://twitter.com/i/web/status/{tweet.get('id')}",
            'grade': grade,
            'scraped_at': datetime.now().isoformat()
        }

        results.append(result)

    return results

def save_results(results, output_file):
    """Save results to JSONL file"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')

    print(f"✓ Saved {len(results)} results to {output_file}")

def main():
    print("🐦 Twitter High-Value Prompt Search")
    print("=" * 50)

    all_results = []
    rate_limit_delay = 15  # Delay between searches to avoid rate limiting

    for keyword in KEYWORDS:
        print(f"\n🔍 Searching: '{keyword}'")
        data = search_twitter(keyword)

        if data:
            results = process_results(data, keyword)
            all_results.extend(results)
            print(f"  Found {len(results)} high-value tweets")

            # Show top results for this keyword
            if results:
                print("\n  Top tweets:")
                for i, r in enumerate(sorted(results, key=lambda x: x['likes'], reverse=True)[:3], 1):
                    print(f"    {i}. [{r['grade']}] ❤️ {r['likes']} | {r['cleaned_text'][:80]}...")
        else:
            print("  No results found")

        # Delay to avoid rate limiting
        if keyword != KEYWORDS[-1]:
            print(f"  ⏳ Waiting {rate_limit_delay}s to avoid rate limiting...")
            time.sleep(rate_limit_delay)

    # Sort by grade and likes
    all_results.sort(key=lambda x: (x['grade'], x['likes']), reverse=True)

    # Generate output filename
    date_str = datetime.now().strftime('%Y%m%d')
    output_file = f'/root/clawd/data/x-scraping/high-value-prompts-{date_str}.jsonl'

    # Save results
    if all_results:
        save_results(all_results, output_file)

        # Print summary
        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print("=" * 50)
        print(f"Total high-value tweets found: {len(all_results)}")
        print(f"Grade A: {sum(1 for r in all_results if r['grade'] == 'A')}")
        print(f"Grade B: {sum(1 for r in all_results if r['grade'] == 'B')}")
        print(f"Grade C: {sum(1 for r in all_results if r['grade'] == 'C')}")

        print("\n🏆 TOP 5 HIGHEST RATED PROMPTS:")
        for i, r in enumerate(all_results[:5], 1):
            print(f"\n{i}. Grade: {r['grade']} | ❤️ {r['likes']} | 🔄 {r['retweets']}")
            print(f"   URL: {r['url']}")
            print(f"   Text: {r['cleaned_text'][:200]}...")
    else:
        print("\n❌ No high-value tweets found matching criteria")

if __name__ == '__main__':
    main()
