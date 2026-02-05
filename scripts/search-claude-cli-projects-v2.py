#!/usr/bin/env python3
"""
搜索 GitHub 上的 Claude 相关 CLI 项目（修复版）
"""

import requests
from datetime import datetime
import time

# GitHub API
GITHUB_API = "https://api.github.com"

# 搜索查询
QUERIES = [
    "claude",
    "claude terminal",
    "claude code",
    "claude assistant",
    "claude ai",
    "anthropic",
    "anthropic cli"
]

def search_github(query, per_page=30):
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
    name = repo.get('name', 'N/A')
    stars = repo.get('stargazers_count', 0)
    language = repo.get('language')
    
    # 处理 None 值
    if language is None:
        language = 'N/A'
    else:
        language = str(language)[:12]
    
    description = repo.get('description', '')
    if description is None:
        description = ''
    else:
        description = str(description)[:40]
    
    url = repo.get('html_url', '')
    
    return {
        'name': name[:50],
        'full_name': repo.get('full_name', ''),
        'url': url,
        'stars': stars,
        'description': description,
        'language': language
    }

def main():
    print("=" * 80)
    print("🔍 搜索 GitHub 上的 Claude 相关 CLI 项目（广泛搜索）")
    print("=" * 80)
    print()

    all_repos = []

    # 搜索多个查询
    for i, query in enumerate(QUERIES):
        print(f"[{i+1}/{len(QUERIES)}] 搜索: '{query}'...", end='', flush=True)
        
        repos = search_github(query, per_page=30)
        
        print(f" ✓ 找到 {len(repos)} 个结果")
        all_repos.extend(repos)
    
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
    
    # 显示 Top 50
    print("🏆 Top 50 Claude 相关 CLI 项目")
    print("=" * 80)
    print()
    
    print(f"{'排名':<6} {'项目名称':<50} {'Stars':<10} {'语言':<12} {'描述'}")
    print("-" * 80)
    
    for i, repo in enumerate(sorted_repos[:50], 1):
        name = repo['name']
        stars = repo['stars']
        language = repo['language']
        description = repo['description']
        
        print(f"{i:<6} {name:<50} {stars:<10} {language:<12} {description}")
    
    # 保存到文件
    timestamp = datetime.now().strftime('%Y-%m-%d')
    output_file = f"/root/clawd/reports/claude-cli-ranking-{timestamp}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Claude 相关 CLI 项目榜单\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**搜索方法**: GitHub API\n")
        f.write(f"**搜索查询**: {', '.join(QUERIES)}\n")
        f.write(f"**总项目数**: {len(sorted_repos)}\n")
        f.write("---\n\n")
        f.write("## 🏆 Top 50 项目\n\n")
        f.write("| 排名 | 项目 | Stars | 语言 | 链接 |\n")
        f.write("|------|------|-------|-------|------|\n")
        
        for i, repo in enumerate(sorted_repos[:50], 1):
            name = repo['name']
            stars = repo['stars']
            language = repo['language']
            url = repo['url']
            
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
