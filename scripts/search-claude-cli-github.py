#!/usr/bin/env python3
"""
使用 GitHub API 搜索 Claude Code CLI 项目
"""

import requests
from datetime import datetime
import time

# GitHub API
GITHUB_API = "https://api.github.com"

# 搜索查询
QUERIES = [
    # 搜索名称包含 "claude" 和 "code" 的仓库
    "claude code",
    # 搜索名称包含 "claude" 和 "cli" 的仓库
    "claude cli",
    # 搜索名称包含 "claude" 和 "terminal" 的仓库
    "claude terminal",
    # 搜索名称包含 "claude" 和 "tool" 的仓库
    "claude tool"
]

def search_github(query, per_page=10):
    """使用 GitHub API 搜索仓库"""
    url = f"{GITHUB_API}/search/repositories"
    params = {
        'q': query + ' in:name',
        'sort': 'stars',
        'order': 'desc',
        'per_page': per_page
    }
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Clawdbot-Claude-Search/1.0'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  搜索失败: {e}")
        time.sleep(1)  # 避免速率限制
        return []

def extract_repo_info(repo):
    """提取仓库信息"""
    return {
        'name': repo.get('name', 'N/A'),
        'full_name': repo.get('full_name', 'N/A'),
        'url': repo.get('html_url', 'N/A'),
        'stars': repo.get('stargazers_count', 0),
        'description': repo.get('description', '')[:100] if repo.get('description') else '',
        'language': repo.get('language', 'N/A'),
        'owner': repo.get('owner', {}).get('login', 'N/A'),
        'created_at': repo.get('created_at', ''),
        'updated_at': repo.get('updated_at', '')
    }

def main():
    print("=" * 80)
    print("🔍 搜索 GitHub 上的 Claude Code CLI 项目")
    print("=" * 80)
    print()

    all_repos = []

    # 搜索多个查询
    for i, query in enumerate(QUERIES):
        print(f"[{i+1}/{len(QUERIES)}] 搜索: {query}...", end='', flush=True)
        
        repos = search_github(query, per_page=10)
        
        print(f" 找到 {len(repos)} 个结果")
        all_repos.extend(repos)
        
        # 稍微延迟避免速率限制
        if i < len(QUERIES) - 1:
            time.sleep(0.5)
    
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
    sorted_repos = sorted(unique_repos, key=lambda x: x.get('stars', 0), reverse=True)
    
    # 显示 Top 30
    print("🏆 Top 30 Claude Code CLI 项目")
    print("=" * 80)
    print()
    
    print(f"{'排名':<6} {'项目名称':<45} {'Stars':<10} {'语言':<12} {'链接'}")
    print("-" * 80)
    
    for i, repo in enumerate(sorted_repos[:30], 1):
        name = repo.get('name', 'N/A')[:43]
        stars = repo.get('stars', 0)
        language = repo.get('language', 'N/A')[:10]
        url = repo.get('url', 'N/A')
        
        print(f"{i:<6} {name:<45} {stars:<10} {language:<12} {url}")
    
    # 保存到文件
    timestamp = datetime.now().strftime('%Y-%m-%d')
    output_file = f"/root/clawd/reports/claude-cli-ranking-{timestamp}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Claude Code CLI 项目榜单\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**总项目数**: {len(sorted_repos)}\n")
        f.write(f"**搜索方法**: GitHub API\n\n")
        f.write("---\n\n")
        f.write("## 🏆 Top 30 项目\n\n")
        f.write("| 排名 | 项目 | Stars | 语言 | 链接 |\n")
        f.write("|------|------|-------|------|------|\n")
        
        for i, repo in enumerate(sorted_repos[:30], 1):
            name = repo.get('name', 'N/A')
            stars = repo.get('stars', 0)
            language = repo.get('language', 'N/A')
            url = repo.get('url', '')
            
            f.write(f"| {i} | {name} | {stars} | {language} | {url} |\n")
    
    print()
    print("=" * 80)
    print(f"✅ 报告已保存: {output_file}")
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
