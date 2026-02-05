#!/usr/bin/env python3
"""
Simple test script to verify SearXNG JSON API works
"""

import json
import requests

url = "http://127.0.0.1:8080/search"

params = {
    'q': 'AI prompt engineering tips site:twitter.com OR site:x.com',
    'format': 'json',
    'language': 'en'
}

try:
    print("Making request to SearXNG...")
    response = requests.get(url, params=params, timeout=30)
    print(f"Status code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nSuccess! Found {len(data.get('results', []))} results")
        for i, r in enumerate(data.get('results', [])[:3]):
            print(f"\n{i+1}. {r.get('title', '')[:80]}")
            print(f"   URL: {r.get('url', '')}")
    else:
        print(f"Error: {response.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")
