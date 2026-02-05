#!/usr/bin/env python3
"""
搜索 AI 代码编辑器项目（超健壮版）
"""

import requests
from datetime import datetime
import time

# GitHub API
GITHUB_API = "https://api.github.com"

# 更精确的搜索关键词（减少查询避免速率限制）
QUERIES = [
    "cursor",
    "windsurf",
    "opencodium",
    "zed editor",
    "replit",
    "bolt.new",
    "tabnine",
    "codeium",
    "cursor alternative",
    "ai code editor"
    "ai ide"
    "claude code editor"
    "windsurf alternative"
    "cursor ide"
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
        'User-Agent': 'Clawdbot-AI-Editor-Search/1.0'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  搜索 '{query}' 失败: {e}")
        return []

def extract_repo_info(repo):
    """提取仓库信息（超健壮版）"""
    name = repo.get('name', 'N/A')
    stars = repo.get('stargazers_count', 0)
    forks = repo.get('forks_count', 0)
    language = repo.get('language')
    description = repo.get('description', '')
    url = repo.get('html_url', '')
    full_name = repo.get('full_name', '')
    updated_at = repo.get('updated_at', '')

    # 处理 language
    if language is None:
        language = 'N/A'
    else:
        language = str(language)[:15]

    # 处理 description
    if description is None:
        description = ''
    else:
        description = str(description)[:100]

    return {
        'name': name[:50],
        'full_name': full_name,
        'url': url,
        'stars': stars,
        'forks': forks,
        'description': description,
        'language': language,
        'updated_at': updated_at
    }

def calculate_editor_score(repo):
    """计算 AI 编辑器相关分数（0-100）"""
    score = 0
    name = repo.get('name', '').lower()
    description = repo.get('description', '')
    stars = repo.get('stars', 0)
    language = repo.get('language')

    # AI 编辑器关键词
    ai_keywords = [
        'editor', 'ide', 'code editor', 'ai editor',
        'cursor', 'windsurf', 'opencodium', 'zed', 'replit',
        'bolt.new', 'tabnine', 'codeium', 'continue', 'gitpod',
        'codium', 'v0.dev', 'ai programming', 'ai assisted',
        'copilot', 'programming tool', 'developer environment'
    ]

    # 检查名称
    text = name
    for keyword in ai_keywords:
        if keyword in text:
            score += 50
            break

    # 检查描述
    if description:
        desc_lower = description.lower()
        for keyword in ai_keywords:
            if keyword in desc_lower:
                score += 20

    # 星级评分
    if stars > 0:
        import math
        score += min(30, math.log2(stars) * 3)

    # 语言相关
    if language:
        editor_languages = ['typescript', 'rust', 'javascript', 'python', 'go', 'cpp', 'java', 'kotlin', 'swift']
        if any(lang in language.lower() for lang in editor_languages):
            score += 10

    # 是否提及"IDE"或"终端"
    if description:
        if 'ide' in description.lower() or 'terminal' in description.lower():
            score += 10

    return min(100, score)

def main():
    print("=" * 80)
    print("🔍 搜索 AI 代码编辑器项目（超健壮版）")
    print("=" * 80)
    print()

    all_repos = []

    # 搜索每个查询（添加更长的延迟）
    for i, query in enumerate(QUERIES):
        print(f"[{i+1}/{len(QUERIES)}] 搜索: '{query}'...", end='', flush=True)

        repos = search_github(query, per_page=15)

        print(f" 找到 {len(repos)} 个结果")
        all_repos.extend(repos)

        # 添加 1 秒延迟避免速率限制
        if i < len(QUERIES) - 1:
            time.sleep(1)

    print()
    print(f"📊 总共找到 {len(all_repos)} 个仓库")
    print()

    # 去重
    seen = set()
    unique_repos = []
    for repo in all_repos:
        full_name = repo.get('full_name', '')
        if full_name and full_name not in seen:
            seen.add(full_name)
            unique_repos.append(repo)

    print(f"📊 去重后: {len(unique_repos)} 个唯一仓库")
    print()

    # 计算编辑器分数
    for repo in unique_repos:
        repo['ai_editor_score'] = calculate_editor_score(repo)

    # 按分数排序
    sorted_repos = sorted(unique_repos, key=lambda x: x.get('ai_editor_score', 0), reverse=True)

    # 显示 Top 50
    print("🏆 Top 50 AI 代码编辑器项目")
    print("=" * 80)
    print()

    print(f"{'排名':<6} {'项目名称':<50} {'Stars':<10} {'分数':<10}")
    print("-" * 80)

    for i, repo in enumerate(sorted_repos[:50], 1):
        name = repo.get('name', 'N/A')[:48]
        stars = repo.get('stars', 0)
        score = repo.get('ai_editor_score', 0)

        print(f"{i:<6} {name:<50} {stars:<10} {score:<10}")

    # 保存到文件
    timestamp = datetime.now().strftime('%Y-%m-%d')
    output_file = f"/root/clawd/reports/ai-code-editor-ranking-{timestamp}.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# AI 代码编辑器项目榜单\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**搜索方法**: GitHub REST API\n")
        f.write(f"**搜索查询**: {', '.join(QUERIES)}\n")
        f.write(f"**总项目数**: {len(sorted_repos)}\n")
        f.write("---\n\n")
        f.write("## 🏆 Top 50 项目\n\n")
        f.write("| 排名 | 项目 | Stars | 分数 |\n")
        f.write("|------|------|-------|-------|\n")

        for i, repo in enumerate(sorted_repos[:50], 1):
            name = repo.get('name', '')
            stars = repo.get('stars', 0)
            score = repo.get('ai_editor_score', 0)
            url = repo.get('url', '')

            f.write(f"| {i} | {name} | {stars} | {score} | {url} |\n")

    print(f"\n✅ 报告已保存: {output_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
