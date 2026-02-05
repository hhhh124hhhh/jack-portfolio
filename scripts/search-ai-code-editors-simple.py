#!/usr/bin/env python3
"""
简单的 AI 代码编辑器项目搜索（带延迟）
"""

import requests
import time

# GitHub API
GITHUB_API = "https://api.github.com"

# 搜索关键词
QUERIES = [
    "cursor",
    "windsurf",
    "opencodium",
    "zeditor"
    "replit",
    "gitpod",
    "codium",
    "v0",
    "bolt.new"
    "tabnine"
    "codeium"
    "sourcegraph"
    "jetbrains"
    "vscode"
]

def search_github(query, per_page=20):
    """使用 GitHub API 搜索仓库"""
    url = f"{GITHUB_API}/search/repositories"
    params = {
        'q': f"{query} in:name",
        'sort': 'stars',
        'order': 'desc',
        'per_page': per_page
    }
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Clawdbot-AI-Code-Editor-Search/1.0'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  搜索失败: {e}")
        return []

def main():
    print("=" * 80)
    print("🔍 搜索 AI 代码编辑器项目")
    print("=" * 80)
    print()

    all_repos = []

    # 搜索每个查询（添加延迟避免速率限制）
    for i, query in enumerate(QUERIES):
        print(f"[{i+1}/{len(QUERIES)}] 搜索: {query}...", end='', flush=True)

        repos = search_github(query, per_page=20)

        print(f" 找到 {len(repos)} 个结果")
        all_repos.extend(repos)

        # 添加 1 秒延迟避免速率限制
        if i < len(QUERIES) - 1:
            time.sleep(1)

    print()
    print(f"📊 总共找到 {len(all_repos)} 个仓库")
    print()

    # 去重（基于 full_name）
    seen = set()
    unique_repos = []
    for repo in all_repos:
        full_name = repo.get('full_name', '')
        if full_name and full_name not in seen:
            seen.add(full_name)
            unique_repos.append(repo)

    print(f"📊 去重后: {len(unique_repos)} 个唯一仓库")
    print()

    # 按星级排序
    sorted_repos = sorted(unique_repos, key=lambda x: x.get('stargazers_count', 0), reverse=True)

    # 显示 Top 50
    print("🏆 Top 50 AI 代码编辑器项目")
    print("=" * 80)
    print()

    print(f"{'排名':<6} {'项目名称':<45} {'Stars':<10} {'语言':<12}")
    print("-" * 80)

    for i, repo in enumerate(sorted_repos[:50], 1):
        name = repo.get('name', 'N/A')
        stars = repo.get('stargazers_count', 0)
        language = repo.get('language')

        # 处理 None 值
        if name is None:
            name = 'N/A'
        else:
            name = str(name)[:43]

        if language is None:
            language = 'N/A'
        else:
            language = str(language)[:12]

        print(f"{i:<6} {name:<45} {stars:<10} {language:<12}")

    print()
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
