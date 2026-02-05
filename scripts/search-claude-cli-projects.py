#!/usr/bin/env python3
"""
搜索 GitHub 上的 Claude Code 命令行项目
"""

import requests
from datetime import datetime

# SearXNG API
SEARXNG_URL = "http://localhost:8080"

# 搜索查询
QUERIES = [
    "claude code CLI",
    "claude code command line interface",
    "claude terminal tool",
    "claude code assistant CLI",
    "claude coder CLI"
]

def search_searxng(query):
    """使用 SearXNG 搜索"""
    try:
        params = {
            'q': query,
            'engines': ['github'],
            'format': 'json',
            'categories': ['git']
        }
        response = requests.get(f"{SEARXNG_URL}/search", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])
    except Exception as e:
        print(f"搜索失败: {e}")
        return []

def extract_repo_info(repo):
    """提取仓库信息"""
    return {
        'name': repo.get('title', repo.get('repo', 'N/A')),
        'url': repo.get('url', repo.get('repo_url', 'N/A')),
        'stars': repo.get('content', {}).get('stars', 0),
        'description': repo.get('content', {}).get('description', ''),
        'language': repo.get('content', {}).get('language', ''),
        'last_updated': repo.get('last_updated', '')
    }

def main():
    print(f"\n{'='*60}")
    print(f"🔍 搜索 Claude Code CLI 项目")
    print(f"{'='*60}\n")

    all_repos = []

    # 搜索多个查询
    for query in QUERIES:
        print(f"🔎 搜索: {query}...", end='', flush=True)
        
        repos = search_searxng(query)
        
        print(f" 找到 {len(repos)} 个结果")
        all_repos.extend(repos)
    
    # 去重（基于 URL）
    seen = set()
    unique_repos = []
    for repo in all_repos:
        url = repo.get('url', '')
        if url and url not in seen:
            seen.add(url)
            unique_repos.append(repo)
    
    print(f"\n📊 找到 {len(unique_repos)} 个唯一项目\n")

    # 按星级排序
    sorted_repos = sorted(unique_repos, key=lambda x: x.get('stars', 0), reverse=True)
    
    # 显示 Top 20
    print("🏆 Top 20 Claude Code CLI 项目\n")
    print("=" * 80)
    
    print(f"{'排名':<6} {'项目名称':<40} {'Stars':<10} {'语言':<12} {'链接'}")
    print("-" * 80)
    
    for i, repo in enumerate(sorted_repos[:20], 1):
        name = repo.get('name', 'N/A')[:38]
        stars = repo.get('stars', 0)
        language = repo.get('language', 'N/A')[:10]
        url = repo.get('url', '')
        
        print(f"{i:<6} {name:<40} {stars:<10} {language:<12} {url}")
    
    # 保存到文件
    timestamp = datetime.now().strftime('%Y-%m-%d')
    output_file = f"/root/clawd/reports/claude-cli-ranking-{timestamp}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Claude Code CLI 项目榜单\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**总项目数**: {len(sorted_repos)}\n")
        f.write(f"**搜索方法**: SearXNG\n\n")
        f.write("---\n\n")
        f.write("## 🏆 Top 20 项目\n\n")
        f.write("| 排名 | 项目 | Stars | 语言 | 链接 |\n")
        f.write("|------|------|-------|------|------|\n")
        
        for i, repo in enumerate(sorted_repos[:20], 1):
            name = repo.get('name', 'N/A')
            stars = repo.get('stars', 0)
            language = repo.get('language', 'N/A')
            url = repo.get('url', '')
            
            f.write(f"| {i} | {name} | {stars} | {language} | {url} |\n")
    
    print(f"\n✅ 报告已保存: {output_file}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
