#!/usr/bin/env python3
"""
Twitter High-Value Prompt Search - Via Web Search
Uses web search to find Twitter/X posts about AI prompts
"""

import os
import json
import re
import time
from datetime import datetime
import requests

# SearXNG URL from environment
SEARXNG_URL = os.getenv('SEARXNG_URL', 'http://127.0.0.1:8080')

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
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove mentions
    text = re.sub(r'@\w+', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def evaluate_prompt_value(text, score):
    """Evaluate prompt value on A/B/C scale based on search ranking and content"""
    points = 0

    # Check for specific indicators
    if 'step' in text.lower() or '步骤' in text:
        points += 2
    if 'example' in text.lower() or '示例' in text or '例子' in text:
        points += 2
    if 'template' in text.lower() or '模板' in text:
        points += 2
    if 'prompt:' in text.lower() or '提示词:' in text:
        points += 3
    if '```' in text or '"""' in text or "'''" in text:
        points += 2  # Code block indicates actual prompt
    if 'act as' in text.lower() or '扮演' in text.lower():
        points += 2
    if 'you are' in text.lower() or '你是' in text.lower():
        points += 2

    # Search score bonus (higher search rank = better)
    if score > 0.8:
        points += 3
    elif score > 0.6:
        points += 2
    elif score > 0.4:
        points += 1

    # Length check (longer tweets likely have more content)
    if len(text) > 200:
        points += 1
    if len(text) > 400:
        points += 1

    # Grade assignment
    if points >= 7:
        return 'A'
    elif points >= 4:
        return 'B'
    else:
        return 'C'

def search_searxng(query):
    """Search using SearXNG"""
    url = f"{SEARXNG_URL}/search"

    params = {
        'q': query,
        'format': 'json',
        'engines': 'google,bing,duckduckgo',
        'language': 'en',
        'pageno': 1
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error searching SearXNG: {e}")
        return None

def extract_tweet_info(result):
    """Extract tweet info from search result"""
    url = result.get('url', '')

    # Check if it's a Twitter/X URL
    if not ('twitter.com' in url or 'x.com' in url):
        return None

    # Extract tweet ID
    tweet_id_match = re.search(r'/status/(\d+)', url)
    if not tweet_id_match:
        return None

    tweet_id = tweet_id_match.group(1)

    return {
        'url': url,
        'tweet_id': tweet_id,
        'title': result.get('title', ''),
        'content': result.get('content', ''),
        'score': result.get('score', 0),
        'engine': result.get('engine', '')
    }

def process_result(tweet_info, query):
    """Process a single tweet result"""
    text = tweet_info['title'] + ' ' + tweet_info['content']
    cleaned_text = clean_prompt_text(text)

    # Check if it contains actual prompt content
    prompt_indicators = [
        'prompt:', '提示词:', 'Act as', '扮演', 'You are', '你是',
        'template:', '模板:', 'step 1', '第一步',
        '"""', "'''", '```', 'example', '示例'
    ]

    has_prompt = any(indicator.lower() in text.lower() for indicator in prompt_indicators)

    if not has_prompt:
        return None

    # Evaluate value (use search score as proxy for engagement)
    grade = evaluate_prompt_value(text, tweet_info['score'])

    return {
        'tweet_id': tweet_info['tweet_id'],
        'query': query,
        'text': text,
        'cleaned_text': cleaned_text,
        'likes': None,  # Not available from web search
        'retweets': None,
        'replies': None,
        'created_at': None,
        'url': tweet_info['url'],
        'grade': grade,
        'search_score': tweet_info['score'],
        'scraped_at': datetime.now().isoformat()
    }

def save_results(results, output_file):
    """Save results to JSONL file"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')

    print(f"✓ Saved {len(results)} results to {output_file}")

def main():
    print("🌐 Twitter High-Value Prompt Search (via Web Search)")
    print("=" * 60)

    all_results = []

    for keyword in KEYWORDS:
        print(f"\n🔍 Searching: '{keyword}'")
        data = search_searxng(keyword)

        if data and 'results' in data:
            results = data['results']
            print(f"  Found {len(results)} total results")

            # Process results
            for i, result in enumerate(results[:10]):  # Top 10 per query
                tweet_info = extract_tweet_info(result)
                if tweet_info:
                    processed = process_result(tweet_info, keyword)
                    if processed:
                        all_results.append(processed)
                        print(f"    ✓ Found high-value tweet: {processed['grade']} | {processed['cleaned_text'][:60]}...")
        else:
            print("  No results found")

        # Small delay between searches
        if keyword != KEYWORDS[-1]:
            time.sleep(2)

    # Sort by grade and search score
    all_results.sort(key=lambda x: (x['grade'], x.get('search_score', 0)), reverse=True)

    # Remove duplicates by tweet_id
    seen_ids = set()
    unique_results = []
    for r in all_results:
        if r['tweet_id'] not in seen_ids:
            seen_ids.add(r['tweet_id'])
            unique_results.append(r)

    all_results = unique_results

    # Generate output filename
    date_str = datetime.now().strftime('%Y%m%d')
    output_file = f'/root/clawd/data/x-scraping/high-value-prompts-{date_str}.jsonl'

    # Save results
    if all_results:
        save_results(all_results, output_file)

        # Print summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"Total high-value tweets found: {len(all_results)}")
        print(f"Grade A: {sum(1 for r in all_results if r['grade'] == 'A')}")
        print(f"Grade B: {sum(1 for r in all_results if r['grade'] == 'B')}")
        print(f"Grade C: {sum(1 for r in all_results if r['grade'] == 'C')}")

        print("\n🏆 ALL FOUND PROMPTS:")
        for i, r in enumerate(all_results, 1):
            print(f"\n{i}. Grade: {r['grade']} | Score: {r.get('search_score', 0):.2f}")
            print(f"   URL: {r['url']}")
            print(f"   Text: {r['cleaned_text'][:300]}...")
    else:
        print("\n❌ No high-value tweets found matching criteria")

if __name__ == '__main__':
    main()
