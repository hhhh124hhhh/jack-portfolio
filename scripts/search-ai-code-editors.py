#!/usr/bin/env python3
"""
搜索 AI 代码编辑器项目（修复版）
"""

import requests
from datetime import datetime

# GitHub API
GITHUB_API = "https://api.github.com"

# 搜索关键词 - 专门搜索 AI 代码编辑器
QUERIES = [
    "cursor",
    "windsurf",
    "opencodium",
    "zeditor",
    "bolt.new",
    "replit",
    "gitpod ai",
    "codium",
    "v0.dev",
    "codeium ai",
    "continue",
    "cursor alternative",
    "ai code editor",
    "ai ide"
]

def search_github_api(query, per_page=20):
    """使用 GitHub REST API 搜索"""
    url = f"{GITHUB_API}/search/repositories"
    params = {
        'q': f"{query} in:name",
        'sort': 'stars',
        'order': 'desc',
        'per_page': per_page
    }
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'Clawdbot-AI-Editor-Search/1.0'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  搜索失败: {e}")
        return []

def extract_repo_info(repo):
    """提取仓库信息（健壮版）"""
    name = repo.get('name', 'N/A')
    stars = repo.get('stargazers_count', 0)
    forks = repo.get('forks_count', 0)
    language = repo.get('language')
    description = repo.get('description', '')
    url = repo.get('html_url', '')
    full_name = repo.get('full_name', '')
    owner = repo.get('owner', {})

    # 处理 owner
    if isinstance(owner, dict):
        owner_login = owner.get('login', 'N/A')
    else:
        owner_login = str(owner) if owner else 'N/A'

    # 处理 language
    if language is None:
        language = 'N/A'
    else:
        language = str(language)[:15]

    # 处理 description
    if description is None:
        description = ''
    else:
        description = str(description)[:120]

    return {
        'name': name[:60],
        'full_name': full_name,
        'url': url,
        'stars': stars,
        'forks': forks,
        'description': description,
        'language': language,
        'owner': owner_login
    }

def calculate_editor_score(repo):
    """计算 AI 编辑器相关分数（健壮版）"""
    score = 0
    name = repo.get('name', '').lower()
    description = repo.get('description', '')
    language = repo.get('language')
    stars = repo.get('stargazers_count', 0)

    # AI 编辑器关键词
    ai_keywords = [
        'editor', 'ide', 'code editor', 'ai editor',
        'cursor', 'windsurf', 'opencodium', 'zed', 'replit',
        'bolt.new', 'gitpod', 'codium', 'v0.dev',
        'codeium', 'continue', 'tabnine', 'codeium ai',
        'ai coding', 'ai assisted', 'ai integrated',
        'copilot alternative', 'cursor alternative', 'ai autocomplete',
        'pair programming', 'ai development', 'code completion'
    ]

    # 检查名称和描述
    text = name + ' ' + (str(description) if description else '')
    text = text.lower()

    for keyword in ai_keywords:
        if keyword in text:
            score += 30
            break  # 找到一个就够了

    # 星级评分（对数刻度）
    if stars > 0:
        import math
        score += min(40, math.log2(stars) * 2)

    # 语言相关（通常是 TypeScript, Rust, JavaScript, Python）
    if language:
        language_lower = str(language).lower()
        editor_langs = ['typescript', 'rust', 'javascript', 'python', 'go', 'cpp', 'java']
        if any(lang in language_lower for lang in editor_langs):
            score += 15

    # 是否提及"IDE"或"终端"
    if description:
        desc_lower = description.lower()
        if 'ide' in desc_lower or 'terminal' in desc_lower:
            score += 10

    return min(100, score)

def main():
    print("=" * 80)
    print("🔍 搜索 AI 代码编辑器项目（修复版）")
    print("=" * 80)
    print()

    all_repos = []

    # 搜索每个查询
    for i, query in enumerate(QUERIES):
        print(f"[{i+1}/{len(QUERIES)}] 搜索: '{query}'...", end='', flush=True)

        repos = search_github_api(query, per_page=20)

        print(f" 找到 {len(repos)} 个结果")
        all_repos.extend(repos)

        # 添加延迟避免速率限制
        if i < len(QUERIES) - 1:
            import time
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

    # 筛选：只保留分数 >= 50 的项目
    high_score_repos = [repo for repo in unique_repos if repo.get('ai_editor_score', 0) >= 50]

    print(f"📊 高质量 AI 编辑器项目: {len(high_score_repos)} 个")
    print()

    # 按分数排序
    sorted_repos = sorted(high_score_repos, key=lambda x: x.get('ai_editor_score', 0), reverse=True)

    # 显示 Top 50
    print("🏆 Top 50 AI 代码编辑器项目")
    print("=" * 80)
    print()

    print(f"{'排名':<6} {'项目名称':<55} {'Stars':<10} {'分數':<10}")
    print("-" * 80)

    for i, repo in enumerate(sorted_repos[:50], 1):
        name = repo.get('name', 'N/A')[:53]
        stars = repo.get('stars', 0)
        score = repo.get('ai_editor_score', 0)
        language = repo.get('language', 'N/A')[:8]

        print(f"{i:<6} {name:<55} {stars:<10} {score:<10}")

    # 保存到文件
    timestamp = datetime.now().strftime('%Y-%m-%d')
    output_file = f"/root/clawd/reports/ai-code-editor-ranking-{timestamp}.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# AI 代码编辑器项目榜单\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**搜索方法**: GitHub REST API\n")
        f.write(f"**搜索查询**: {', '.join(QUERIES)}\n")
        f.write(f"**总项目数**: {len(sorted_repos)}\n")
        f.write(f"**筛选条件**: AI 编辑器分数 >= 50\n")
        f.write(f"**Top 项目数**: 50\n")
        f.write("---\n\n")
        f.write("## 🏆 Top 50 AI 代码编辑器项目\n\n")
        f.write("| 排名 | 项目 | Stars | 分數 | 语言 |\n")
        f.write("|------|------|-------|------|------|\n")

        for i, repo in enumerate(sorted_repos[:50], 1):
            name = repo.get('name', '')
            stars = repo.get('stars', 0)
            score = repo.get('ai_editor_score', 0)
            language = repo.get('language', '')
            url = repo.get('url', '')

            f.write(f"| {i} | {name} | {stars} | {score} | {language} |\n")

    print()
    print("=" * 80)
    print(f"✅ 报告已保存: {output_file}")

    return sorted_repos, output_file

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️ 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
