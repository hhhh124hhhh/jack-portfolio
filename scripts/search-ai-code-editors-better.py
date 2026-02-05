#!/usr/bin/env python3
"""
搜索 AI 代码编辑器项目（Cursor、Windsurf、OpenCodium 风格）
"""

import requests
from datetime import datetime

# GitHub API
GITHUB_API = "https://api.github.com"

# 更精确的搜索关键词
QUERIES = [
    # 搜索 Claude 相关的代码编辑器
    "claude code editor",
    "claude editor ide",
    "claude coding assistant",
    "claude terminal",
    
    # 搜索 Cursor 类似的项目
    "cursor alternative",
    "cursor like editor",
    "ai code editor cursor",
    
    # 搜索 Windsurf 类似的项目
    "windsurf alternative",
    "ai code editor windsurf",
    "ai coding editor",
    
    # 搜索 OpenCodium/Zed 类似的项目
    "opencodium alternative",
    "ai code editor ide",
    "ai coding terminal",
    
    # 搜索 Replit/Bolt.New 类似的项目
    "replit alternative",
    "bolt.new alternative",
    "ai web ide",
    
    # 搜索一般性的 AI 编辑器
    "ai powered code editor",
    "ai integrated ide",
    "llm powered editor",
    "ai programming assistant",
    
    # 搜索具体的 AI 编辑器项目
    "cursor ide",
    "windsurf",
    "opencodium",
    "tabnine",
    "replit",
    "bolt.new",
    "codium",
    "jetbrains ai",
    "codeium"
    "codeium editor"
]

def search_github(query, per_page=30):
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

def extract_repo_info(repo):
    """提取仓库信息"""
    name = repo.get('name', 'N/A')
    stars = repo.get('stargazers_count', 0)
    forks = repo.get('forks_count', 0)
    language = repo.get('language')
    description = repo.get('description', '')
    url = repo.get('html_url', '')
    owner = repo.get('owner', {}).get('login', 'N/A')

    # 处理 None 值
    if language is None:
        language = 'N/A'
    else:
        language = str(language)[:15]

    if description is None:
        description = ''
    else:
        description = str(description)[:100]

    return {
        'name': name[:60],
        'full_name': repo.get('full_name', ''),
        'url': url,
        'stars': stars,
        'forks': forks,
        'description': description,
        'language': language,
        'owner': owner
    }

def calculate_relevance_score(repo):
    """计算相关性分数（0-100）"""
    score = 0
    name = repo.get('name', '').lower()
    description = repo.get('description', '').lower()
    stars = repo.get('stargazers_count', 0)
    language = repo.get('language')

    # AI 编辑器关键词
    ai_editor_keywords = [
        'code editor', 'ide', 'coding assistant', 'ai powered',
        'llm powered', 'cursor', 'windsurf', 'opencodium', 'replit',
        'bolt.new', 'tabnine', 'codeium', 'jetbrains', 'copilot',
        'ai terminal', 'ai coding', 'programming editor'
    ]

    # 检查名称和描述
    text = name + ' ' + description
    for keyword in ai_editor_keywords:
        if keyword in text:
            score += 20
            break

    # 星级评分（对数刻度）
    if stars > 0:
        import math
        score += min(30, math.log2(stars) * 3)

    # 是否包含"editor"或"IDE"
    if 'editor' in name or 'ide' in name or 'editor' in description or 'ide' in description:
        score += 15

    # 是否包含"code"或"coding"
    if 'code' in name or 'coding' in name or 'code' in description or 'coding' in description:
        score += 15

    # 语言相关性（通常是 TypeScript, Rust, Python, JavaScript, Go）
    editor_languages = ['typescript', 'rust', 'python', 'javascript', 'go', 'cpp', 'java', 'kotlin', 'swift']
    if language and str(language).lower() in editor_languages:
        score += 10

    # 活跃度（forks）
    forks = repo.get('forks_count', 0)
    score += min(10, math.log2(forks + 1) * 2)

    return min(100, score)

def main():
    print("=" * 80)
    print("🔍 搜索 AI 代码编辑器项目（Cursor、Windsurf、OpenCodium 风格）")
    print("=" * 80)
    print()

    all_repos = []

    # 搜索多个查询
    for i, query in enumerate(QUERIES):
        print(f"[{i+1}/{len(QUERIES)}] 搜索: '{query}'...", end='', flush=True)
        
        repos = search_github(query, per_page=25)
        
        print(f" ✓ 找到 {len(repos)} 个结果")
        all_repos.extend(repos)
        
        # 添加延迟避免速率限制
        if i < len(QUERIES) - 1:
            import time
            time.sleep(0.5)

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

    # 计算相关性分数
    for repo in unique_repos:
        repo['relevance_score'] = calculate_relevance_score(repo)

    # 按相关性分数排序
    sorted_repos = sorted(unique_repos, key=lambda x: x.get('relevance_score', 0), reverse=True)

    # 筛选高质量项目（分数 >= 50）
    high_quality_repos = [repo for repo in sorted_repos if repo.get('relevance_score', 0) >= 50]

    print(f"📊 高质量项目: {len(high_quality_repos)} 个")
    print()

    # 显示 Top 50
    print("🏆 Top 50 AI 代码编辑器项目")
    print("=" * 80)
    print()

    print(f"{'排名':<6} {'项目名称':<45} {'Stars':<10} {'语言':<12} {'相关性'}")
    print("-" * 80)

    for i, repo in enumerate(high_quality_repos[:50], 1):
        name = repo.get('name', 'N/A')[:43]
        stars = repo.get('stars', 0)
        language = repo.get('language', 'N/A')[:10]
        relevance = repo.get('relevance_score', 0)

        print(f"{i:<6} {name:<45} {stars:<10} {language:<12} {relevance:.0f}")

    print()
    print("=" * 80)

    # 保存到文件
    timestamp = datetime.now().strftime('%Y-%m-%d')
    output_file = f"/root/clawd/reports/ai-code-editor-ranking-{timestamp}.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# AI 代码编辑器项目榜单\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**筛选条件**: 相关性分数 >= 50\n")
        f.write(f"**总项目数**: {len(sorted_repos)}\n")
        f.write(f"**高质量项目**: {len(high_quality_repos)}\n")
        f.write("---\n\n")
        f.write("## 🏆 Top 50 AI 代码编辑器项目\n\n")
        f.write("| 排名 | 项目 | Stars | 相关性 | 语言 | 描述 |\n")
        f.write("|------|------|-------|--------|------|------|\n")

        for i, repo in enumerate(high_quality_repos[:50], 1):
            name = repo.get('name', '')
            stars = repo.get('stars', 0)
            relevance = repo.get('relevance_score', 0)
            language = repo.get('language', '')
            description = repo.get('description', '')[:60]
            url = repo.get('url', '')

            # 清理描述中的特殊字符
            description = description.replace('|', '\\|').replace('\n', ' ')

            f.write(f"| {i} | {name} | {stars} | {relevance:.0f} | {language} | {description} | {url} |\n")

    print(f"✅ 报告已保存: {output_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
