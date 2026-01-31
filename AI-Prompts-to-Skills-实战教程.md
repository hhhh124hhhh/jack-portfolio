# AI 提示词转 Skill 实战教程

> 从零开始打造自动化 AI 提示词收集、评估、转换和发布系统

**版本**: 1.0
**创建时间**: 2026-01-31
**目标**: 手把手教你建立完整的 AI 提示词商业化流程

---

## 📋 目录

- [第一部分：项目概览](#第一部分项目概览)
- [第二部分：数据收集（实战核心）](#第二部分数据收集实战核心)
- [第三部分：提示词转换](#第三部分提示词转换)
- [第四部分：发布到 ClawdHub](#第四部分发布到-clawdhub)
- [第五部分：经验教训](#第五部分经验教训)
- [附录：常见问题](#附录常见问题)

---

## 第一部分：项目概览

### 1.1 商业模式说明

#### 什么是 AI 提示词转 Skill？

**核心概念**：
- 从 Twitter/X、Reddit、GitHub 等平台收集高质量 AI 提示词
- 使用多维度评分系统评估提示词质量
- 自动转换为 Clawdbot Skill 格式
- 发布到 ClawdHub 平台售卖

**市场定位**：
- ❌ 不是卖原生提示词（像 PromptBase）
- ✅ 卖**可执行的、格式化的 Clawdbot Skills**
- ✅ 目标用户：Clawdbot 用户群体

#### 收入模型

**定价策略**（基于评分等级）：

| 等级 | 分数范围 | 定价 | 预期月销量 |
|------|---------|------|-----------|
| A+ | 90-100 | $9.99 | 30-50份 |
| A | 85-89 | $4.99 | 50-100份 |
| B+ | 80-84 | $2.99 | 100-200份 |
| B | 70-79 | $1.99 | 200-300份 |
| C+ | 60-69 | $0.99 | 300-500份 |
| C | 50-59 | 免费 | 不限量 |
| D | 0-49 | 不收录 | - |

**收入预测**：
- 保守估计（第1年）：$3,600
- 乐观估计（第1年）：$10,500

### 1.2 市场分析

#### 竞争对手分析

| 平台 | 定价模式 | 产品类型 | 我们的差异化 |
|------|---------|---------|-------------|
| PromptBase | 单次购买 $1.99-$9.99 | 原生提示词 | ✅ 自动转换为 Skill |
| LearnPrompting | 会员制 $15/月 | 教程课程 | ✅ 即用型产品 |
| SnackPrompt | 免费+订阅 | 社区分享 | ✅ 质量筛选 + 格式化 |
| FlowGPT | 免费为主 | 用户生成 | ✅ 专业评估 + 商业化 |

#### 目标用户画像

**主要用户群体**：
1. **Clawdbot 用户**（30%）
   - 已安装 Clawdbot
   - 需要扩展功能
   - 愿意付费提升效率

2. **AI 工具爱好者**（40%）
   - 尝试各种 AI 工具
   - 热衷于新技巧
   - 分享和使用高质量提示词

3. **专业创作者**（20%）
   - 内容创作者
   - 营销人员
   - 需要特定领域的 AI 辅助

4. **企业用户**（10%）
   - 寻找自动化解决方案
   - 需要稳定的 AI 工作流
   - 愿意为质量付费

### 1.3 技术架构

#### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     数据收集层                               │
├─────────────────────────────────────────────────────────────┤
│  Twitter/X  │  Reddit  │  GitHub  │  SearXNG  │  HN       │
│  (API/RSS)   │  (PRAW)  │  (API)   │  (本地)   │  (API)    │
└─────────────┬──────────┬──────────┬──────────┬────────────┘
              │          │          │          │
              ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────┐
│                    数据处理层                                │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 提取与   │→ │ 质量评估 │→ │ 去重与   │→ │ 分类与   │   │
│  │ 清洗     │  │ (5维度)  │  │ 合并     │  │ 标签     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Skill 转换层                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ 模板匹配 │→ │ 内容增强 │→ │ 格式化   │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    发布层                                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ 验证与   │→ │ 自动打包 │→ │ ClawdHub │                   │
│  │ 格式检查 │  │ (.skill) │  │ 发布     │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

#### 技术栈

**后端**：
- Python 3.9+
- Cron 定时任务
- GitHub Actions（可选）

**工具库**：
- `twitter-api-v2` - Twitter API 客户端
- `praw` - Reddit API 客户端
- `PyGithub` - GitHub API 客户端
- `requests` - HTTP 请求
- `clawdhub-cli` - ClawdHub 命令行工具

**数据存储**：
- 本地文件系统（JSONL 格式）
- Git 仓库（版本控制）

---

## 第二部分：数据收集（实战核心）

### 2.1 多数据源采集

#### 2.1.1 Twitter/X API 集成

**环境配置**：

```bash
# 1. 安装依赖
pip install twitter-api-v2 requests

# 2. 配置 API Key
export TWITTER_API_KEY="your_api_key_here"
export TWITTER_API_SECRET="your_api_secret_here"
export TWITTER_ACCESS_TOKEN="your_access_token_here"
export TWITTER_ACCESS_SECRET="your_access_secret_here"
```

**脚本示例**：`search-x-prompts.py`

```python
#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime

# Twitter API Key（从 ~/.bashrc 加载）
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY', '')

def search_x_prompts():
    """
    使用 Twitter API 搜索 AI 提示词
    注意：免费计划有速率限制
    """
    if not TWITTER_API_KEY:
        print("❌ Twitter API Key 未配置")
        return []

    # 搜索查询（使用标签过滤，提高质量）
    queries = [
        "#AIPrompts -is:retweet lang:en min_faves:10",
        "#promptengineering -is:retweet lang:en min_faves:10",
        "(#ChatGPT OR #ClaudeAI OR #GPT4) prompts -is:retweet lang:en min_faves:10",
        "Midjourney prompts -is:retweet lang:en",
        '"prompt template" AI -is:retweet lang:en',
        '"system prompt" LLM -is:retweet lang:en',
        '(Claude OR ChatGPT) act as -is:retweet lang:en min_faves:20',
        '"prompt engineering" guide tutorial -is:retweet lang:en min_faves:10'
    ]

    all_tweets = []

    for query in queries:
        try:
            # 使用 twitterapi.io 服务
            url = f"https://api.twitterapi.io/v2/search?query={query}&max_results=10"
            headers = {
                "Authorization": f"Bearer {TWITTER_API_KEY}",
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                tweets = data.get('data', [])
                all_tweets.extend(tweets)
                print(f"✅ 查询成功: {query} - 获取 {len(tweets)} 条推文")
            elif response.status_code == 429:
                print(f"⚠️ 速率限制: {query} - 请求过于频繁")
                break
            else:
                print(f"❌ 查询失败: {query} - {response.status_code}")

        except Exception as e:
            print(f"❌ 查询异常: {query} - {str(e)}")

    return all_tweets

def save_tweets(tweets, output_dir="/root/clawd/data/x-scraping"):
    """
    保存推文到文件
    """
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    output_file = os.path.join(output_dir, f"prompts-{today}.jsonl")

    with open(output_file, 'a', encoding='utf-8') as f:
        for tweet in tweets:
            # 标准化格式
            standardized = {
                'tweet_id': tweet.get('id'),
                'author_handle': tweet.get('username'),
                'author_followers': tweet.get('followers_count', 0),
                'content': tweet.get('text', ''),
                'likes': tweet.get('likes_count', 0),
                'retweets': tweet.get('retweets_count', 0),
                'replies': tweet.get('replies_count', 0),
                'quotes': tweet.get('quotes_count', 0),
                'created_at': tweet.get('created_at'),
                'url': f"https://twitter.com/i/web/status/{tweet.get('id')}",
                'source': 'twitter',
                'collected_at': datetime.now().isoformat()
            }
            f.write(json.dumps(standardized, ensure_ascii=False) + '\n')

    print(f"✅ 保存 {len(tweets)} 条推文到 {output_file}")

if __name__ == "__main__":
    tweets = search_x_prompts()
    save_tweets(tweets)
```

**执行脚本**：

```bash
# 添加执行权限
chmod +x /root/clawd/scripts/search-x-prompts.py

# 运行脚本
python3 /root/clawd/scripts/search-x-prompts.py
```

**预期输出**：
```
✅ 查询成功: #AIPrompts -is:retweet lang:en min_faves:10 - 获取 10 条推文
✅ 查询成功: #promptengineering -is:retweet lang:en min_faves:10 - 获取 10 条推文
⚠️ 速率限制: (#ChatGPT OR #ClaudeAI OR #GPT4) prompts -is:retweet lang:en min_faves:10 - 请求过于频繁
✅ 保存 20 条推文到 /root/clawd/data/x-scraping/prompts-20260131.jsonl
```

#### 2.1.2 Reddit 数据抓取

**环境配置**：

```bash
# 1. 安装依赖
pip install praw

# 2. 配置 Reddit API
# 访问 https://www.reddit.com/prefs/apps 创建应用
```

**脚本示例**：`collect-reddit-prompts.py`

```python
#!/usr/bin/env python3
import praw
import json
import os
from datetime import datetime

# Reddit API 配置
reddit = praw.Reddit(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="ClawdbotPromptCollector/1.0 by /u/your_username"
)

# 子版块配置
SUBREDDITS = {
    "ChatGPTPromptGenius": {"limit": 25, "score_threshold": 100},
    "PromptEngineering": {"limit": 25, "score_threshold": 50},
    "ChatGPT": {"limit": 50, "score_threshold": 500},
    "Claude": {"limit": 25, "score_threshold": 50},
}

def collect_reddit_prompts():
    """
    从 Reddit 收集 AI 提示词
    """
    all_posts = []

    for subreddit_name, config in SUBREDDITS.items():
        try:
            subreddit = reddit.subreddit(subreddit_name)

            # 获取热门帖子
            for post in subreddit.hot(limit=config["limit"]):
                # 过滤低质量内容
                if post.score < config["score_threshold"]:
                    continue

                # 提取提示词（从代码块或长文本）
                content = post.selftext or ""

                # 如果有评论，也检查评论
                if post.num_comments > 10:
                    comment_keywords = ["prompt", "here's", "try this", "i use"]
                    content += " " + " ".join([
                        comment.body
                        for comment in post.comments.list()[:10]
                        if any(kw in comment.body.lower() for kw in comment_keywords)
                    ])

                standardized = {
                    'post_id': post.id,
                    'author': str(post.author),
                    'content': content,
                    'title': post.title,
                    'score': post.score,
                    'upvotes': post.ups,
                    'num_comments': post.num_comments,
                    'url': f"https://reddit.com{post.permalink}",
                    'subreddit': subreddit_name,
                    'source': 'reddit',
                    'collected_at': datetime.now().isoformat()
                }

                all_posts.append(standardized)
                print(f"✅ 收集: r/{subreddit_name} - {post.title[:50]}...")

        except Exception as e:
            print(f"❌ 失败: r/{subreddit_name} - {str(e)}")

    return all_posts

def save_posts(posts, output_dir="/root/clawd/data/reddit"):
    """
    保存 Reddit 帖子到文件
    """
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    output_file = os.path.join(output_dir, f"prompts-{today}.jsonl")

    with open(output_file, 'a', encoding='utf-8') as f:
        for post in posts:
            f.write(json.dumps(post, ensure_ascii=False) + '\n')

    print(f"✅ 保存 {len(posts)} 条帖子到 {output_file}")

if __name__ == "__main__":
    posts = collect_reddit_prompts()
    save_posts(posts)
```

**执行脚本**：

```bash
python3 /root/clawd/scripts/collect-reddit-prompts.py
```

#### 2.1.3 GitHub Awesome Prompts 获取

**脚本示例**：`collect-github-prompts.py`

```python
#!/usr/bin/env python3
from github import Github
import json
import os
from datetime import datetime
import re

# GitHub Token（用于增加 API 限制）
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

# 高质量仓库列表
REPOS = [
    {"owner": "f", "repo": "awesome-chatgpt-prompts", "file": "README.md", "quality": 90},
    {"owner": "dair-ai", "repo": "Prompt-Engineering-Guide", "file": "README.md", "quality": 85},
    {"owner": "microsoft", "repo": "prompt-engine", "file": "README.md", "quality": 85},
]

def extract_prompts_from_readme(content):
    """
    从 README 中提取提示词
    """
    prompts = []

    # 匹配格式：- **Role**: Description
    role_pattern = r'-\s*\*\*([^*]+)\*\*:\s*(.+)'

    for match in re.finditer(role_pattern, content):
        role = match.group(1)
        description = match.group(2)

        prompts.append({
            'role': role.strip(),
            'description': description.strip(),
            'content': f"You are a {role}. {description}",
            'quality': 'high'
        })

    return prompts

def collect_github_prompts():
    """
    从 GitHub 收集提示词
    """
    g = Github(GITHUB_TOKEN)
    all_prompts = []

    for repo_config in REPOS:
        try:
            repo = g.get_repo(f"{repo_config['owner']}/{repo_config['repo']}")

            # 获取 README 文件
            readme = repo.get_contents(repo_config['file'])
            content = readme.decoded_content.decode('utf-8')

            # 提取提示词
            prompts = extract_prompts_from_readme(content)

            for prompt in prompts:
                standardized = {
                    'content': prompt['content'],
                    'role': prompt['role'],
                    'description': prompt['description'],
                    'source': 'github',
                    'repo': f"{repo_config['owner']}/{repo_config['repo']}",
                    'url': f"https://github.com/{repo_config['owner']}/{repo_config['repo']}",
                    'quality_score': repo_config['quality'],
                    'collected_at': datetime.now().isoformat()
                }
                all_prompts.append(standardized)

            print(f"✅ 收集: {repo_config['owner']}/{repo_config['repo']} - {len(prompts)} 条提示词")

        except Exception as e:
            print(f"❌ 失败: {repo_config['owner']}/{repo_config['repo']} - {str(e)}")

    return all_prompts

def save_prompts(prompts, output_dir="/root/clawd/data/github"):
    """
    保存提示词到文件
    """
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    output_file = os.path.join(output_dir, f"prompts-{today}.jsonl")

    with open(output_file, 'a', encoding='utf-8') as f:
        for prompt in prompts:
            f.write(json.dumps(prompt, ensure_ascii=False) + '\n')

    print(f"✅ 保存 {len(prompts)} 条提示词到 {output_file}")

if __name__ == "__main__":
    prompts = collect_github_prompts()
    save_prompts(prompts)
```

**执行脚本**：

```bash
export GITHUB_TOKEN="your_github_token_here"
python3 /root/clawd/scripts/collect-github-prompts.py
```

#### 2.1.4 专业网站爬取（SearXNG）

**使用自建 SearXNG 实例**（推荐）：

```bash
# SearXNG 已在 localhost:8080 运行
export SEARXNG_URL="http://localhost:8080"
```

**脚本示例**：`collect-searxng-prompts.py`

```python
#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime

SEARXNG_URL = os.environ.get('SEARXNG_URL', 'http://localhost:8080')

# 搜索关键词
SEARCH_KEYWORDS = [
    "AI prompt engineering tips 2026",
    "best ChatGPT prompts for work",
    "Claude AI prompt examples",
    "AI prompt templates free",
    "effective AI prompts guide",
    "Midjourney prompt guide",
    "GPT-4 system prompt examples",
]

def search_searxng(query):
    """
    使用 SearXNG 搜索
    """
    params = {
        'q': query,
        'format': 'json',
        'engines': 'google,duckduckgo,bing',  # 多搜索引擎
        'language': 'en',
        'time_range': None,  # 无时间限制
        'safesearch': 0,     # 不开启安全搜索
    }

    try:
        response = requests.get(
            f"{SEARXNG_URL}/search",
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            return results
        else:
            print(f"❌ 搜索失败: {query} - {response.status_code}")
            return []

    except Exception as e:
        print(f"❌ 搜索异常: {query} - {str(e)}")
        return []

def collect_web_prompts():
    """
    从网络搜索收集提示词
    """
    all_prompts = []

    for keyword in SEARCH_KEYWORDS:
        results = search_searxng(keyword)

        for result in results:
            # 提取提示词相关内容
            content = result.get('content', '')
            title = result.get('title', '')
            url = result.get('url', '')

            # 过滤掉非提示词内容
            if len(content) < 50:
                continue

            # 标准化格式
            standardized = {
                'content': content[:2000],  # 限制长度
                'title': title,
                'url': url,
                'score': result.get('score', 0),
                'source': 'searxng',
                'engine': result.get('engine', 'unknown'),
                'collected_at': datetime.now().isoformat()
            }

            all_prompts.append(standardized)

        print(f"✅ 搜索: {keyword} - 获取 {len(results)} 条结果")

    return all_prompts

def save_prompts(prompts, output_dir="/root/clawd/data/searxng"):
    """
    保存提示词到文件
    """
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    output_file = os.path.join(output_dir, f"prompts-{today}.jsonl")

    with open(output_file, 'a', encoding='utf-8') as f:
        for prompt in prompts:
            f.write(json.dumps(prompt, ensure_ascii=False) + '\n')

    print(f"✅ 保存 {len(prompts)} 条提示词到 {output_file}")

if __name__ == "__main__":
    prompts = collect_web_prompts()
    save_prompts(prompts)
```

**执行脚本**：

```bash
python3 /root/clawd/scripts/collect-searxng-prompts.py
```

### 2.2 数据质量评估

#### 2.2.1 5 维度评分系统详解

**评分维度**（100 分制）：

| 维度 | 权重 | 说明 | 评分标准 |
|------|------|------|---------|
| 🎯 实用性 | 30% | 具体使用场景、步骤、参数 | 10-15: 基本思路<br>16-25: 有步骤<br>26-30: 完整教程 |
| 🎨 创新性 | 20% | 方法独特性、角度新颖 | 10-15: 常见思路<br>16-18: 独特角度<br>19-20: 前所未见 |
| 📖 完整性 | 20% | 详细程度、示例数量 | 10-15: 部分信息<br>16-18: 大部分完整<br>19-20: 非常详细 |
| 🔥 热度 | 25% | 点赞、转发、评论数 | 标准化算法 |
| 👨‍💼 作者影响力 | 5% | 粉丝数、认证状态 | log10(followers) * 0.8 |

**实现代码**：`evaluate-prompts.py`

```python
#!/usr/bin/env python3
import json
import re
import math
from datetime import datetime
import os

def evaluate_practicality(content):
    """
    评估实用性（30分）
    """
    score = 0
    content_lower = content.lower()

    # 1. 长度评分（0-10分）
    length = len(content)
    if 50 <= length <= 500:
        score += 10
    elif length > 500:
        score += 8
    elif length < 30:
        score += 0
    else:
        score += 5

    # 2. 结构评分（0-10分）
    if '\n' in content:
        score += 3
    if '```' in content:
        score += 3
    if re.search(r'(step|步骤|首先|其次|最后)', content_lower):
        score += 4

    # 3. 具体性评分（0-10分）
    specific_keywords = ['specific', 'detailed', 'for example', 'such as', 'include',
                         '具体', '详细', '例如', '包括']
    for kw in specific_keywords:
        if kw in content_lower:
            score += 2
            if score >= 10:
                break

    return min(30, score)

def evaluate_innovation(content):
    """
    评估创新性（20分）
    """
    score = 10  # 基础分

    content_lower = content.lower()

    # 检查独特的角度或方法
    unique_patterns = [
        r'first\s+time', r'never\s+seen', r'unique',
        r'novel\s+approach', r'innovative', r'cutting\s+edge'
    ]

    for pattern in unique_patterns:
        if re.search(pattern, content_lower):
            score += 3
            break

    # 检查组合多个领域
    if re.search(r'(combine|merge|integrate|融合|结合)', content_lower):
        score += 2

    return min(20, score)

def evaluate_completeness(content):
    """
    评估完整性（20分）
    """
    score = 0

    # 1. 上下文说明（0-5分）
    context_keywords = ['context', 'background', 'assume', 'given',
                       '背景', '假设', '给定']
    for kw in context_keywords:
        if kw in content.lower():
            score += 2
            if score >= 5:
                break

    # 2. 示例数量（0-5分）
    example_count = content.count('example') + content.count('示例')
    score += min(5, example_count)

    # 3. 输出说明（0-5分）
    output_keywords = ['output', 'result', 'return',
                      '输出', '结果', '返回']
    for kw in output_keywords:
        if kw in content.lower():
            score += 2
            if score >= 15:
                break

    # 4. 参数说明（0-5分）
    if re.search(r'(parameter|argument|variable|参数|变量)', content.lower()):
        score += 5

    return min(20, score)

def evaluate_popularity(item):
    """
    评估热度（25分）
    """
    score = 0

    # 标准化算法
    metrics = item.get('metrics', {})

    # Twitter
    if 'likes' in item:
        score += min(15, item['likes'] / 100)
    if 'retweets' in item:
        score += min(5, item['retweets'] / 50)
    if 'comments' in item:
        score += min(5, item['comments'] / 20)

    # Reddit
    if 'score' in item:
        score += min(20, item['score'] / 100)
    if 'upvotes' in item:
        score += min(20, item['upvotes'] / 100)

    # Hacker News
    if 'points' in item:
        score += min(20, item['points'] / 20)

    return min(25, score)

def evaluate_influence(item):
    """
    评估作者影响力（5分）
    """
    followers = item.get('author_followers', 0)
    return min(5, math.log10(max(1, followers)) * 0.8)

def evaluate_prompt(item):
    """
    综合评分
    """
    content = item.get('content', '')

    # 各维度评分
    scores = {
        'practicality': evaluate_practicality(content),
        'innovation': evaluate_innovation(content),
        'completeness': evaluate_completeness(content),
        'popularity': evaluate_popularity(item),
        'influence': evaluate_influence(item)
    }

    # 加权总分
    total_score = (
        scores['practicality'] * 0.30 +
        scores['innovation'] * 0.20 +
        scores['completeness'] * 0.20 +
        scores['popularity'] * 0.25 +
        scores['influence'] * 0.05
    )

    # 确定等级
    if total_score >= 90:
        grade = 'A+'
    elif total_score >= 85:
        grade = 'A'
    elif total_score >= 80:
        grade = 'B+'
    elif total_score >= 70:
        grade = 'B'
    elif total_score >= 60:
        grade = 'C+'
    elif total_score >= 50:
        grade = 'C'
    else:
        grade = 'D'

    return {
        'total_score': round(total_score, 2),
        'grade': grade,
        'scores': scores,
        'evaluated_at': datetime.now().isoformat()
    }

def batch_evaluate(input_dir="/root/clawd/data", output_dir="/root/clawd/data/evaluation"):
    """
    批量评估
    """
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    output_file = os.path.join(output_dir, f"scored-prompts-{today}.jsonl")

    all_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.jsonl'):
                all_files.append(os.path.join(root, file))

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for input_file in all_files:
            with open(input_file, 'r', encoding='utf-8') as infile:
                for line in infile:
                    item = json.loads(line)

                    # 评估
                    evaluation = evaluate_prompt(item)

                    # 合并
                    evaluated_item = {**item, **evaluation}

                    # 保存
                    outfile.write(json.dumps(evaluated_item, ensure_ascii=False) + '\n')

    print(f"✅ 评估完成，保存到 {output_file}")

if __name__ == "__main__":
    batch_evaluate()
```

**执行脚本**：

```bash
python3 /root/clawd/scripts/evaluate-prompts.py
```

**预期输出**：
```
✅ 评估完成，保存到 /root/clawd/data/evaluation/scored-prompts-20260131.jsonl
```

**查看评分结果**：

```bash
# 查看高分提示词
jq -r 'select(.grade == "A+" or .grade == "A")' /root/clawd/data/evaluation/scored-prompts-20260131.jsonl | head -5

# 统计各等级数量
jq -r '.grade' /root/clawd/data/evaluation/scored-prompts-20260131.jsonl | sort | uniq -c
```

#### 2.2.2 AI 语义评估实现

**使用 Claude API 进行语义评估**：

```python
#!/usr/bin/env python3
import anthropic
import json
import os
from datetime import datetime

# Claude API Key
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

EVALUATION_PROMPT = """
你是一个专业的 AI 提示词质量评估专家。请从以下维度评估这个提示词的质量（0-100分）：

1. **实用性（30分）**：
   - 是否有具体的使用场景？
   - 是否有清晰的步骤说明？
   - 是否有必要的参数设置？

2. **创新性（20分）**：
   - 角度是否新颖独特？
   - 是否有独特的技巧或方法？
   - 是否组合了多个领域的知识？

3. **完整性（20分）**：
   - 上下文是否充分？
   - 是否有足够的示例？
   - 输出说明是否清晰？

4. **具体性（15分）**：
   - 是否避免了模糊的表述？
   - 是否使用了具体的例子？
   - 是否有明确的输出格式？

5. **清晰度（15分）**：
   - 逻辑是否清晰？
   - 是否有歧义？
   - 是否容易理解和执行？

**提示词内容**：
{prompt}

**请以 JSON 格式返回评分结果**：
{{
  "practicality": 分数,
  "innovation": 分数,
  "completeness": 分数,
  "specificity": 分数,
  "clarity": 分数,
  "total_score": 总分,
  "grade": "A+/A/B+/B/C+/C/D",
  "reasoning": "简短的评分理由",
  "suggestions": ["改进建议1", "改进建议2"]
}}
"""

def ai_evaluate_prompt(content):
    """
    使用 Claude 进行 AI 语义评估
    """
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": EVALUATION_PROMPT.format(prompt=content)
                }
            ]
        )

        # 提取 JSON 结果
        content_text = response.content[0].text
        result = json.loads(content_text)

        return {
            'ai_evaluated': True,
            'ai_evaluation': result,
            'evaluated_at': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"❌ AI 评估失败: {str(e)}")
        return {
            'ai_evaluated': False,
            'error': str(e)
        }

def batch_ai_evaluate(input_file, output_file):
    """
    批量 AI 评估
    """
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:

        for line in infile:
            item = json.loads(line)

            # 只评估高分提示词（≥60分）
            if item.get('total_score', 0) >= 60:
                print(f"🤖 AI 评估中: {item.get('content', '')[:50]}...")
                ai_result = ai_evaluate_prompt(item.get('content', ''))
                item = {**item, **ai_result}

            outfile.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ AI 评估完成，保存到 {output_file}")

if __name__ == "__main__":
    input_file = "/root/clawd/data/evaluation/scored-prompts-20260131.jsonl"
    output_file = "/root/clawd/data/evaluation/ai-scored-prompts-20260131.jsonl"

    batch_ai_evaluate(input_file, output_file)
```

**执行脚本**：

```bash
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
python3 /root/clawd/scripts/ai-evaluate-prompts.py
```

#### 2.2.3 去重和清洗流程

**去重脚本**：`deduplicate-prompts.py`

```python
#!/usr/bin/env python3
import json
import hashlib
from difflib import SequenceMatcher

def content_hash(content):
    """
    生成内容 hash
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def semantic_similarity(text1, text2, threshold=0.85):
    """
    计算语义相似度
    """
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def deduplicate_prompts(input_file, output_file, similarity_threshold=0.85):
    """
    去重
    """
    seen_hashes = set()
    unique_prompts = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            content = item.get('content', '')

            # 1. Hash 去重（完全相同）
            h = content_hash(content)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            # 2. 语义去重（相似）
            is_duplicate = False
            for existing in unique_prompts:
                existing_content = existing.get('content', '')
                similarity = semantic_similarity(content, existing_content)
                if similarity >= similarity_threshold:
                    # 保留评分更高的
                    if item.get('total_score', 0) > existing.get('total_score', 0):
                        unique_prompts.remove(existing)
                        unique_prompts.append(item)
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_prompts.append(item)

    # 保存去重结果
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in unique_prompts:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ 去重完成: {len(unique_prompts)} 条唯一提示词")

if __name__ == "__main__":
    input_file = "/root/clawd/data/evaluation/scored-prompts-20260131.jsonl"
    output_file = "/root/clawd/data/evaluation/deduplicated-prompts-20260131.jsonl"

    deduplicate_prompts(input_file, output_file)
```

**执行脚本**：

```bash
python3 /root/clawd/scripts/deduplicate-prompts.py
```

**清洗脚本**：`clean-prompts.py`

```python
#!/usr/bin/env python3
import json
import re

def clean_content(content):
    """
    清洗内容
    """
    # 1. 移除 HTML 标签
    content = re.sub(r'<[^>]+>', '', content)

    # 2. 移除多余的空白
    content = re.sub(r'\s+', ' ', content)
    content = content.strip()

    # 3. 移除特殊字符（保留基本标点）
    content = re.sub(r'[^\w\s.,!?;:\-\'"()]', '', content)

    # 4. 移除明显的垃圾内容
    spam_patterns = [
        r'click here', r'subscribe', r'follow me',
        r'buy now', r'sign up', r'limited time offer'
    ]
    for pattern in spam_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return None

    return content

def apply_filters(item):
    """
    应用过滤规则
    """
    content = item.get('content', '')
    score = item.get('total_score', 0)

    # 过滤规则
    if len(content) < 30:
        return False
    if len(content) > 2000:
        return False
    if score < 50:
        return False

    return True

def clean_prompts(input_file, output_file):
    """
    清洗提示词
    """
    cleaned = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)

            # 清洗内容
            cleaned_content = clean_content(item.get('content', ''))
            if not cleaned_content:
                continue

            # 应用过滤
            if not apply_filters(item):
                continue

            # 更新内容
            item['content'] = cleaned_content
            item['cleaned'] = True
            item['cleaned_at'] = datetime.now().isoformat()

            cleaned.append(item)

    # 保存清洗结果
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in cleaned:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ 清洗完成: {len(cleaned)} 条清洁提示词")

if __name__ == "__main__":
    from datetime import datetime

    input_file = "/root/clawd/data/evaluation/deduplicated-prompts-20260131.jsonl"
    output_file = "/root/clawd/data/evaluation/cleaned-prompts-20260131.jsonl"

    clean_prompts(input_file, output_file)
```

**执行脚本**：

```bash
python3 /root/clawd/scripts/clean-prompts.py
```

### 2.3 实战脚本使用

#### 2.3.1 Twitter 搜索实战

**步骤 1：配置环境**

```bash
# 加载 API Key
source ~/.bashrc

# 验证配置
echo $TWITTER_API_KEY
```

**步骤 2：运行搜索脚本**

```bash
# 创建日志目录
mkdir -p /root/clawd/logs

# 运行搜索（带日志）
python3 /root/clawd/scripts/search-x-prompts.py 2>&1 | tee /root/clawd/logs/twitter-search-$(date +%Y%m%d-%H%M%S).log
```

**步骤 3：查看结果**

```bash
# 查看最新的推文文件
ls -lt /root/clawd/data/x-scraping/ | head -3

# 查看推文内容
cat /root/clawd/data/x-scraping/prompts-20260131.jsonl | jq -r '.content' | head -5
```

**步骤 4：统计数据**

```bash
# 统计推文数量
wc -l /root/clawd/data/x-scraping/prompts-20260131.jsonl

# 统计点赞数分布
cat /root/clawd/data/x-scraping/prompts-20260131.jsonl | jq -r '.likes' | sort -n | uniq -c
```

#### 2.3.2 SearXNG 集成使用

**步骤 1：验证 SearXNG 状态**

```bash
# 检查 SearXNG 是否运行
docker ps | grep searxng

# 测试搜索
curl "http://localhost:8080/search?q=test&format=json" | jq .
```

**步骤 2：运行搜索脚本**

```bash
# 设置 SearXNG URL
export SEARXNG_URL="http://localhost:8080"

# 运行搜索
python3 /root/clawd/scripts/collect-searxng-prompts.py
```

**步骤 3：查看结果质量**

```bash
# 查看搜索结果
cat /root/clawd/data/searxng/prompts-20260131.jsonl | jq -r '.title, .score'

# 过滤高质量结果
cat /root/clawd/data/searxng/prompts-20260131.jsonl | jq 'select(.score > 50)' | head -20
```

#### 2.3.3 Cron 自动化任务配置

**配置 Cron 任务**：

```bash
# 编辑 crontab
crontab -e

# 添加以下任务

# 每 6 小时收集 Twitter 提示词
0 */6 * * * cd /root/clawd && python3 /root/clawd/scripts/search-x-prompts.py >> /root/clawd/logs/cron-twitter.log 2>&1

# 每 6 小时收集 Reddit 提示词
30 */6 * * * cd /root/clawd && python3 /root/clawd/scripts/collect-reddit-prompts.py >> /root/clawd/logs/cron-reddit.log 2>&1

# 每 4 小时搜索网络资源
0 */4 * * * cd /root/clawd && python3 /root/clawd/scripts/collect-searxng-prompts.py >> /root/clawd/logs/cron-searxng.log 2>&1

# 每 8 小时评估提示词
0 */8 * * * cd /root/clawd && python3 /root/clawd/scripts/evaluate-prompts.py >> /root/clawd/logs/cron-evaluate.log 2>&1

# 每天早上 9 点生成报告
0 9 * * * cd /root/clawd && bash /root/clawd/scripts/generate-daily-report.sh >> /root/clawd/logs/cron-report.log 2>&1
```

**查看 Cron 任务**：

```bash
# 列出当前 crontab
crontab -l

# 查看 Cron 日志
tail -f /root/clawd/logs/cron-*.log
```

**测试 Cron 任务**：

```bash
# 手动触发任务（测试）
cd /root/clawd && python3 /root/clawd/scripts/search-x-prompts.py

# 查看执行结果
ls -lt /root/clawd/data/x-scraping/
```

---

## 第三部分：提示词转换

### 3.1 提示词到 Skill 的自动转换流程

#### 3.1.1 Skill 结构说明

**标准 Skill 目录结构**：

```
skill-name/
├── SKILL.md           # 主文档（必需）
├── README.md          # 简介（可选）
├── examples/          # 示例（可选）
│   ├── example1.md
│   └── example2.md
├── references/        # 参考资料（可选）
│   └── prompts.md
├── config/            # 配置文件（可选）
│   └── settings.yaml
└── package.json       # 元数据（可选）
```

**SKILL.md 模板**：

```markdown
# Skill 名称

简短描述（1-2句）

## 描述
详细描述 Skill 的功能和用途

## 类别
[category]

## 使用方法
详细步骤...

## 示例
[examples]

## 最佳实践
[best practices]

## 依赖
[dependencies]

## 数据源
- 来源: [source]
- 原始链接: [url]
- 作者: [author]
- 采集时间: [date]
```

#### 3.1.2 自动转换脚本

**转换脚本**：`convert-prompt-to-skill.py`

```python
#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime
import shutil

# Skill 模板
SKILL_TEMPLATE = """# {skill_name}

{short_description}

## 描述
{description}

## 类别
{category}

## 评分
总分: {total_score}/100 ({grade})

## 使用方法
{usage}

## 示例
{examples}

## 最佳实践
{best_practices}

## 数据源
- 来源: {source}
- 原始链接: {url}
- 作者: {author}
- 采集时间: {collected_at}
- 评分时间: {evaluated_at}
"""

README_TEMPLATE = """# {skill_name}

{short_description}

## 安装

```bash
clawdhub install {skill_slug}
```

## 快速开始

{quick_start}

## 文档

详细文档请查看 [SKILL.md](./SKILL.md)

## 贡献

此 Skill 由 AI 自动生成，来源于：
- 原始来源: {source}
- 原始链接: {url}

## 许可

MIT License
"""

def generate_skill_name(content):
    """
    生成 Skill 名称
    """
    # 提取关键词
    keywords = re.findall(r'\b\w{4,}\b', content)

    # 选择前3个关键词
    top_keywords = keywords[:3]

    # 生成名称（kebab-case）
    skill_name = '-'.join([kw.lower() for kw in top_keywords])

    return skill_name[:50]  # 限制长度

def generate_skill_slug(name):
    """
    生成 Skill slug
    """
    # 小写，替换空格和特殊字符为连字符
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower())
    slug = slug.strip('-')

    return slug

def extract_category(content):
    """
    提取类别
    """
    content_lower = content.lower()

    # 分类规则
    categories = {
        'coding': ['code', 'python', 'javascript', 'programming', 'debug'],
        'writing': ['write', 'blog', 'article', 'content', 'copy'],
        'analysis': ['analyze', 'data', 'statistics', 'insight'],
        'creative': ['create', 'generate', 'art', 'image', 'design'],
        'education': ['teach', 'learn', 'explain', 'tutorial'],
        'business': ['marketing', 'sales', 'business', 'strategy']
    }

    for category, keywords in categories.items():
        if any(kw in content_lower for kw in keywords):
            return category

    return 'general'

def generate_usage(content):
    """
    生成使用方法
    """
    usage_lines = []

    # 提取步骤
    steps = re.findall(r'(?:step|步骤)\s*\d*:?\s*([^\n]+)', content, re.IGNORECASE)
    if steps:
        usage_lines.append("### 步骤\n")
        for i, step in enumerate(steps, 1):
            usage_lines.append(f"{i}. {step}\n")

    # 提取参数
    params = re.findall(r'(?:parameter|参数)\s*:?\s*([^\n]+)', content, re.IGNORECASE)
    if params:
        usage_lines.append("### 参数\n")
        for param in params:
            usage_lines.append(f"- {param}\n")

    return '\n'.join(usage_lines) if usage_lines else content

def generate_examples(content):
    """
    生成示例
    """
    examples = []

    # 提取代码块
    code_blocks = re.findall(r'```[\s\S]*?```', content)
    if code_blocks:
        examples.append("### 代码示例\n")
        examples.extend(code_blocks)
        examples.append("\n")

    # 提取 "For example" 后的内容
    for_examples = re.findall(r'(?:for example|例如)[:：]\s*([^\n]+)', content, re.IGNORECASE)
    if for_examples:
        examples.append("### 文本示例\n")
        for ex in for_examples:
            examples.append(f"- {ex}\n")

    return '\n'.join(examples) if examples else "暂无示例"

def generate_best_practices(content):
    """
    生成最佳实践
    """
    practices = []

    # 通用的最佳实践
    practices.append("- 根据具体需求调整提示词参数")
    practices.append("- 测试并优化提示词以获得最佳效果")
    practices.append("- 参考示例以理解正确的使用方式")
    practices.append("- 定期检查更新以获取改进和修复")

    # 从内容中提取特定建议
    tips = re.findall(r'(?:tip|建议|note)[:：]\s*([^\n]+)', content, re.IGNORECASE)
    practices.extend(tips)

    return '\n'.join(practices)

def convert_prompt_to_skill(item, output_dir="/root/clawd/generated-skills"):
    """
    转换提示词为 Skill
    """
    # 只转换高分提示词（≥70分）
    if item.get('total_score', 0) < 70:
        print(f"⏭️  跳过低分提示词: {item.get('total_score', 0)}")
        return None

    content = item.get('content', '')
    source = item.get('source', 'unknown')

    # 生成 Skill 名称
    skill_name = generate_skill_name(content)
    skill_slug = generate_skill_slug(skill_name)

    # 生成目录
    skill_dir = os.path.join(output_dir, skill_slug)
    os.makedirs(skill_dir, exist_ok=True)

    # 生成 SKILL.md
    skill_md = SKILL_TEMPLATE.format(
        skill_name=skill_name.title(),
        short_description=content[:100] + "...",
        description=content[:500],
        category=extract_category(content),
        total_score=item.get('total_score', 0),
        grade=item.get('grade', 'N/A'),
        usage=generate_usage(content),
        examples=generate_examples(content),
        best_practices=generate_best_practices(content),
        source=source,
        url=item.get('url', 'N/A'),
        author=item.get('author', item.get('author_handle', 'unknown')),
        collected_at=item.get('collected_at', 'N/A'),
        evaluated_at=item.get('evaluated_at', 'N/A')
    )

    with open(os.path.join(skill_dir, 'SKILL.md'), 'w', encoding='utf-8') as f:
        f.write(skill_md)

    # 生成 README.md
    readme_md = README_TEMPLATE.format(
        skill_name=skill_name.title(),
        short_description=content[:100] + "...",
        skill_slug=skill_slug,
        quick_start=content[:300],
        source=source,
        url=item.get('url', 'N/A')
    )

    with open(os.path.join(skill_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme_md)

    # 保存原始提示词到 references
    refs_dir = os.path.join(skill_dir, 'references')
    os.makedirs(refs_dir, exist_ok=True)

    with open(os.path.join(refs_dir, 'original-prompt.json'), 'w', encoding='utf-8') as f:
        json.dump(item, f, ensure_ascii=False, indent=2)

    print(f"✅ 生成 Skill: {skill_slug}")

    return skill_dir

def batch_convert(input_file, output_dir="/root/clawd/generated-skills"):
    """
    批量转换
    """
    os.makedirs(output_dir, exist_ok=True)

    count = 0
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)

            # 转换
            skill_dir = convert_prompt_to_skill(item, output_dir)

            if skill_dir:
                count += 1

    print(f"\n✅ 转换完成: {count} 个 Skills")

if __name__ == "__main__":
    input_file = "/root/clawd/data/evaluation/cleaned-prompts-20260131.jsonl"

    batch_convert(input_file)
```

**执行脚本**：

```bash
python3 /root/clawd/scripts/convert-prompt-to-skill.py
```

**预期输出**：
```
⏭️  跳过低分提示词: 45
⏭️  跳过低分提示词: 52
✅ 生成 Skill: prompt-engineering-guide
✅ 生成 Skill: content-creation-assistant
✅ 生成 Skill: code-generation-tool

✅ 转换完成: 3 个 Skills
```

### 3.2 手动优化和编辑技巧

#### 3.2.1 SKILL.md 优化

**优化要点**：

1. **标题清晰**
   - 使用简洁、描述性的标题
   - 避免过长的标题

2. **描述完整**
   - 第一段：简短描述（1-2句）
   - 第二段：详细功能说明
   - 第三段：适用场景

3. **使用方法明确**
   - 分步骤说明
   - 提供具体命令或示例
   - 标注必要参数

4. **示例丰富**
   - 至少 2-3 个示例
   - 涵盖常见使用场景
   - 包含预期输出

**优化示例**：

**优化前**：
```markdown
# Content Writer

Write content using AI.

## 描述
This skill helps you write content.

## 使用方法
Just ask it to write.
```

**优化后**：
```markdown
# Content Writer

专业的 AI 内容写作助手，支持博客、文章、营销文案等多种内容创作。

## 描述
Content Writer 是一个基于 AI 的内容创作工具，可以帮助你快速生成高质量的文字内容。它支持多种内容类型，包括博客文章、社交媒体文案、电子邮件、产品描述等。

### 主要功能
- 📝 博客文章生成
- 📧 电子邮件撰写
- 📱 社交媒体文案
- 📄 产品描述优化
- 🎯 营销内容创作

## 使用方法

### 基本使用
1. 确认 Skill 已安装
2. 在对话中直接提出写作需求
3. 指定内容类型和长度
4. 等待 AI 生成内容

### 示例命令
```
写一篇关于 AI 的 500 字博客文章
帮我写一封产品发布的电子邮件
为 Instagram 创作一段美食照片的文案
```

## 示例

### 示例 1：博客文章
**用户输入**：
```
写一篇关于"远程工作优势"的 500 字博客文章
```

**AI 输出**：
（生成的博客文章内容）

### 示例 2：电子邮件
**用户输入**：
```
帮我写一封给客户的感谢信，感谢他们购买我们的产品
```

**AI 输出**：
（生成的电子邮件内容）

## 最佳实践
- 📌 明确指定内容类型和长度
- 📌 提供足够的上下文信息
- 📌 可以要求 AI 使用特定风格（正式、幽默、专业等）
- 📌 对生成的内容进行人工审核和修改
- 📌 多次迭代优化内容质量
```

#### 3.2.2 添加依赖和配置

**添加 config/settings.yaml**：

```yaml
# Content Writer 配置

# 默认设置
defaults:
  content_type: "blog"      # 默认内容类型
  word_count: 500            # 默认字数
  tone: "professional"       # 默认语气

# 内容类型
content_types:
  blog:
    word_count: 500-1000
    tone: professional
  social_media:
    word_count: 50-200
    tone: casual
  email:
    word_count: 200-500
    tone: professional

# 语气选项
tones:
  professional: "专业、正式"
  casual: "轻松、友好"
  humorous: "幽默、有趣"
  creative: "创意、独特"
```

**添加 package.json**：

```json
{
  "name": "content-writer",
  "version": "1.0.0",
  "description": "专业的 AI 内容写作助手",
  "category": "writing",
  "author": "Clawdbot Community",
  "license": "MIT",
  "dependencies": [],
  "keywords": [
    "writing",
    "content",
    "blog",
    "email",
    "social-media"
  ],
  "rating": {
    "score": 85,
    "grade": "A"
  },
  "data_source": {
    "platform": "twitter",
    "url": "https://twitter.com/i/web/status/1234567890",
    "author": "@username",
    "collected_at": "2026-01-31T10:00:00Z"
  }
}
```

### 3.3 SKILL.md 最佳实践

#### 3.3.1 结构最佳实践

**标准结构**：

```markdown
# [Skill 名称]

[简短描述，1-2句话]

## 描述
[详细描述，包括功能、用途、适用场景]

## 类别
[category]

## 评分
总分: [score]/100 ([grade])

## 使用方法
[分步骤说明，包括命令示例]

## 示例
[至少2-3个示例，涵盖常见场景]

## 最佳实践
[使用技巧、注意事项]

## 依赖
[如果有依赖，列出依赖项]

## 数据源
- 来源: [source]
- 原始链接: [url]
- 作者: [author]
- 采集时间: [date]
```

#### 3.3.2 内容最佳实践

**1. 简洁明了**
- 使用简洁的语言
- 避免冗长的描述
- 直接给出解决方案

**2. 示例丰富**
- 提供具体的命令示例
- 展示预期输出
- 涵盖常见使用场景

**3. 结构清晰**
- 使用清晰的层级结构
- 使用列表和表格
- 添加适当的分隔符

**4. 错误处理**
- 说明常见的错误
- 提供解决方案
- 给出调试技巧

#### 3.3.3 版本控制最佳实践

**使用 Git 管理**：

```bash
# 初始化 Git 仓库
cd /root/clawd/generated-skills/skill-name
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Content Writer Skill v1.0.0"

# 添加远程仓库
git remote add origin https://github.com/your-username/your-repo.git

# 推送
git push -u origin master
```

**版本号管理**：

```json
{
  "version": "1.0.0",
  "changelog": [
    {
      "version": "1.0.0",
      "date": "2026-01-31",
      "changes": [
        "初始版本发布",
        "基于 Twitter 提示词自动生成"
      ]
    }
  ]
}
```

---

## 第四部分：发布到 ClawdHub

### 4.1 打包和格式化

#### 4.1.1 打包为 .skill 文件

**打包脚本**：`pack-skill.sh`

```bash
#!/bin/bash

SKILL_DIR="$1"
OUTPUT_DIR="/root/clawd/packed-skills"

if [ -z "$SKILL_DIR" ]; then
    echo "Usage: $0 <skill-directory>"
    exit 1
fi

if [ ! -d "$SKILL_DIR" ]; then
    echo "Error: Directory $SKILL_DIR does not exist"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 获取 Skill 名称
SKILL_NAME=$(basename "$SKILL_DIR")

# 打包为 .skill 文件
tar -czf "$OUTPUT_DIR/$SKILL_NAME.skill" -C "$SKILL_DIR" .

echo "✅ 打包完成: $OUTPUT_DIR/$SKILL_NAME.skill"
```

**执行打包**：

```bash
# 添加执行权限
chmod +x /root/clawd/scripts/pack-skill.sh

# 打包所有 Skills
for skill_dir in /root/clawd/generated-skills/*/; do
    bash /root/clawd/scripts/pack-skill.sh "$skill_dir"
done

# 查看打包结果
ls -lh /root/clawd/packed-skills/
```

**预期输出**：
```
✅ 打包完成: /root/clawd/packed-skills/content-writer.skill (4.2KB)
✅ 打包完成: /root/clawd/packed-skills/prompt-engineering-guide.skill (5.1KB)
✅ 打包完成: /root/clawd/packed-skills/code-generation-tool.skill (3.8KB)
```

#### 4.1.2 格式验证

**验证脚本**：`validate-skill.sh`

```bash
#!/bin/bash

SKILL_DIR="$1"

if [ -z "$SKILL_DIR" ]; then
    echo "Usage: $0 <skill-directory>"
    exit 1
fi

# 检查必需文件
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "❌ 错误: 缺少 SKILL.md"
    exit 1
fi

# 检查文件大小
if [ $(stat -f%z "$SKILL_DIR/SKILL.md" 2>/dev/null || stat -c%s "$SKILL_DIR/SKILL.md") -lt 100 ]; then
    echo "❌ 错误: SKILL.md 太小（<100 字节）"
    exit 1
fi

echo "✅ 格式验证通过: $SKILL_DIR"
```

**执行验证**：

```bash
chmod +x /root/clawd/scripts/validate-skill.sh

# 验证所有 Skills
for skill_dir in /root/clawd/generated-skills/*/; do
    bash /root/clawd/scripts/validate-skill.sh "$skill_dir"
done
```

### 4.2 ClawdHub CLI 使用

#### 4.2.1 安装 ClawdHub CLI

```bash
# 使用 ClawdHub Skill
clawdhub install clawdhub

# 或者全局安装
npm install -g @clawdhub/cli
```

#### 4.2.2 登录 ClawdHub

```bash
# 登录
clawdhub login

# 输入 token（从 https://clawdhub.com 获取）
```

#### 4.2.3 发布 Skill

**发布单个 Skill**：

```bash
# 发布
clawdhub publish /root/clawd/packed-skills/content-writer.skill \
    --slug "content-writer" \
    --version "1.0.0" \
    --name "Content Writer" \
    --description "专业的 AI 内容写作助手" \
    --category "writing" \
    --price "4.99" \
    --changelog "Initial release"
```

**批量发布**：

```bash
#!/bin/bash

# 批量发布脚本
for skill_file in /root/clawd/packed-skills/*.skill; do
    slug=$(basename "$skill_file" .skill)

    # 读取 package.json 获取元数据
    if [ -f "/root/clawd/generated-skills/$slug/package.json" ]; then
        name=$(jq -r '.name' "/root/clawd/generated-skills/$slug/package.json")
        version=$(jq -r '.version' "/root/clawd/generated-skills/$slug/package.json")
        category=$(jq -r '.category' "/root/clawd/generated-skills/$slug/package.json")
        description=$(jq -r '.description' "/root/clawd/generated-skills/$slug/package.json")
        score=$(jq -r '.rating.score' "/root/clawd/generated-skills/$slug/package.json")

        # 根据评分定价
        if [ "$score" -ge 90 ]; then
            price="9.99"
        elif [ "$score" -ge 85 ]; then
            price="4.99"
        elif [ "$score" -ge 80 ]; then
            price="2.99"
        elif [ "$score" -ge 70 ]; then
            price="1.99"
        elif [ "$score" -ge 60 ]; then
            price="0.99"
        else
            price="0.00"
        fi

        # 发布
        clawdhub publish "$skill_file" \
            --slug "$slug" \
            --version "$version" \
            --name "$name" \
            --description "$description" \
            --category "$category" \
            --price "$price" \
            --changelog "Auto-generated from prompt collection"

        echo "✅ 发布完成: $slug (价格: $price)"
    fi
done
```

**执行批量发布**：

```bash
chmod +x /root/clawd/scripts/batch-publish.sh
bash /root/clawd/scripts/batch-publish.sh
```

#### 4.2.4 管理已发布的 Skills

**查看已发布的 Skills**：

```bash
clawdhub list
```

**更新 Skill**：

```bash
clawdhub update content-writer \
    --version "1.1.0" \
    --changelog "优化了内容生成的质量"
```

**下架 Skill**：

```bash
clawdhub unpublish content-writer
```

### 4.3 定价策略应用

#### 4.3.1 定价矩阵

| 评分 | 分数范围 | 定价 | 策略 |
|------|---------|------|------|
| A+ | 90-100 | $9.99 | 高端定价，优质内容 |
| A | 85-89 | $4.99 | 中高端，专业内容 |
| B+ | 80-84 | $2.99 | 中端，实用内容 |
| B | 70-79 | $1.99 | 入门，基础内容 |
| C+ | 60-69 | $0.99 | 低价，补充内容 |
| C | 50-59 | 免费 | 免费，引流内容 |
| D | 0-49 | 不发布 | 低质量，不收录 |

#### 4.3.2 动态定价策略

**根据市场反馈调整价格**：

```python
#!/usr/bin/env python3
import json
import requests

def get_sales_data(skill_slug):
    """
    获取销售数据（假设 ClawdHub 提供 API）
    """
    response = requests.get(f"https://api.clawdhub.com/skills/{skill_slug}/sales")
    return response.json()

def adjust_price(skill_slug, current_sales, current_price):
    """
    根据销售数据调整价格
    """
    # 销量低，降价促销
    if current_sales < 10:
        new_price = max(current_price * 0.8, 0.99)
        return new_price

    # 销量高，保持价格
    if current_sales > 50:
        return current_price

    # 正常销量，保持原价
    return current_price

def update_pricing(skill_slug, new_price):
    """
    更新价格
    """
    response = requests.put(
        f"https://api.clawdhub.com/skills/{skill_slug}/price",
        json={"price": new_price}
    )

    if response.status_code == 200:
        print(f"✅ 价格已更新: {skill_slug} - ${new_price:.2f}")
    else:
        print(f"❌ 更新失败: {skill_slug}")

if __name__ == "__main__":
    # 示例：更新所有已发布 Skills 的价格
    skills = ["content-writer", "prompt-engineering-guide", "code-generation-tool"]

    for skill in skills:
        sales_data = get_sales_data(skill)
        current_price = sales_data.get('price', 4.99)
        current_sales = sales_data.get('sales', 0)

        new_price = adjust_price(skill, current_sales, current_price)

        if new_price != current_price:
            update_pricing(skill, new_price)
```

---

## 第五部分：经验教训

### 5.1 数据质量陷阱

#### 5.1.1 常见陷阱

**陷阱 1：过度依赖自动化**
- **问题**：完全依赖自动提取，导致大量低质量内容
- **教训**：自动化是辅助，不是替代。定期人工抽查 10-20 条结果。

**陷阱 2：忽视清洗**
- **问题**：直接使用原始数据，包含大量噪音
- **教训**：数据清洗比数据收集更重要。建立严格的过滤规则。

**陷阱 3：单一数据源**
- **问题**：只依赖 Twitter 或 Reddit，数据量有限
- **教训**：多数据源整合（Twitter、Reddit、GitHub、SearXNG 等）。

**陷阱 4：忽略上下文**
- **问题**：提取提示词时丢失了重要上下文
- **教训**：保留原始来源链接和完整上下文，便于验证。

#### 5.1.2 解决方案

**解决方案 1：建立质量监控**
```bash
# 每周人工抽查 50 条数据
python3 /root/clawd/scripts/weekly-quality-check.py
```

**解决方案 2：多轮清洗**
```bash
# 第一轮：过滤明显垃圾内容
python3 /root/clawd/scripts/clean-prompts.py

# 第二轮：去重
python3 /root/clawd/scripts/deduplicate-prompts.py

# 第三轮：AI 语义评估
python3 /root/clawd/scripts/ai-evaluate-prompts.py
```

**解决方案 3：数据源优先级**
```yaml
data_sources:
  tier1:  # 高质量
    - github
    - promptbase
  tier2:  # 中等质量
    - reddit
    - searxng
  tier3:  # 补充
    - twitter
```

### 5.2 API 限制解决方案

#### 5.2.1 Twitter API 限制

**问题**：
- 免费计划：每月 500,000 条推文
- 每 15 分钟：300 条请求
- 超限返回 429 错误

**解决方案**：

**方案 1：使用多个 API Key**
```python
TWITTER_API_KEYS = [
    "key1",
    "key2",
    "key3"
]

current_key_index = 0

def get_next_api_key():
    global current_key_index
    key = TWITTER_API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(TWITTER_API_KEYS)
    return key
```

**方案 2：使用 RSS 端点（Nitter）**
```python
import feedparser

# Nitter 实例
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.poast.org",
    "https://nitter.fdn.fr"
]

def fetch_twitter_rss(query):
    """
    使用 Nitter RSS 端点
    """
    url = f"{NITTER_INSTANCES[0]}/search?q={query}&f=tweets&src=typed_query"

    try:
        feed = feedparser.parse(url)
        return feed.entries
    except Exception as e:
        print(f"❌ RSS 获取失败: {str(e)}")
        return []
```

**方案 3：缓存和去重**
```python
import hashlib
import json
import os

CACHE_DIR = "/root/clawd/cache/twitter"

def get_cached_result(query):
    """
    获取缓存结果
    """
    cache_file = os.path.join(CACHE_DIR, hashlib.md5(query).hexdigest() + ".json")

    if os.path.exists(cache_file):
        # 检查缓存时间（24小时有效期）
        age = time.time() - os.path.getmtime(cache_file)
        if age < 86400:
            with open(cache_file) as f:
                return json.load(f)

    return None

def cache_result(query, data):
    """
    缓存结果
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, hashlib.md5(query).hexdigest() + ".json")

    with open(cache_file, 'w') as f:
        json.dump(data, f)
```

#### 5.2.2 Reddit API 限制

**问题**：
- 认证用户：60 请求/分钟
- 未认证：30 请求/分钟

**解决方案**：

**方案 1：使用多个账户**
```python
REDDIT_ACCOUNTS = [
    {"client_id": "id1", "client_secret": "secret1"},
    {"client_id": "id2", "client_secret": "secret2"}
]
```

**方案 2：限流**
```python
import time

def rate_limit_delay():
    """
    限流延迟
    """
    # 60 请求/分钟 = 1 请求/秒
    time.sleep(1)
```

### 5.3 自动化边界

#### 5.3.1 什么时候需要人工介入？

**需要人工介入的情况**：

1. **质量评估**
   - 评分在 60-70 之间的提示词
   - AI 评估结果不明确的内容
   - 争议性或敏感内容

2. **Skill 转换**
   - 复杂的多步骤提示词
   - 需要特定领域知识的提示词
   - 包含代码或配置文件的提示词

3. **发布决策**
   - 评分低于 60 的内容是否发布
   - 争议性内容是否发布
   - 重复内容如何处理

4. **定价策略**
   - 特殊技能的定价
   - 促销活动的决策
   - 市场反馈后的价格调整

#### 5.3.2 人工审核流程

**步骤 1：筛选需要审核的内容**

```bash
# 筛选 60-70 分的提示词
jq -r 'select(.total_score >= 60 and .total_score < 70)' \
    /root/clawd/data/evaluation/scored-prompts-20260131.jsonl > \
    /root/clawd/data/needs-review.jsonl
```

**步骤 2：人工审核**

```bash
# 查看需要审核的内容
cat /root/clawd/data/needs-review.jsonl | jq -r '.content' | less
```

**步骤 3：记录审核结果**

```json
{
  "content": "提示词内容",
  "total_score": 65,
  "human_review": {
    "approved": true,
    "reason": "虽然评分不高，但内容实用",
    "adjustments": {
      "total_score": 70,
      "grade": "B"
    },
    "reviewer": "jack happy",
    "reviewed_at": "2026-01-31T10:00:00Z"
  }
}
```

---

## 附录：常见问题

### Q1: Twitter API 速率限制怎么办？

**A**: 有几种解决方案：

1. **升级付费计划**：获得更高的 API 配额
2. **使用多个 API Key**：轮换使用不同的 key
3. **使用 RSS 端点**：通过 Nitter 实例获取数据（无 API key 限制）
4. **缓存和去重**：避免重复请求相同的内容

### Q2: 如何提高数据质量？

**A**:

1. **多轮清洗**：过滤、去重、AI 评估
2. **人工抽查**：定期人工验证 10-20 条结果
3. **多数据源**：整合多个高质量数据源
4. **调整评分权重**：根据市场反馈优化评分系统

### Q3: Skill 转换失败率高怎么办？

**A**:

1. **提高评分阈值**：只转换 70 分以上的提示词
2. **优化转换规则**：改进模板匹配和内容生成
3. **人工辅助**：对复杂提示词进行手动优化
4. **持续迭代**：根据转换结果调整算法

### Q4: 如何选择数据源？

**A**:

**Tier 1（高质量）**：
- GitHub awesome 仓库
- 专业提示词网站（PromptBase）

**Tier 2（中等质量）**：
- Reddit 高质量子版块
- 技术博客

**Tier 3（补充）**：
- Twitter/X
- SearXNG 网络搜索

### Q5: 如何监控自动化流程？

**A**:

1. **日志记录**：所有脚本都输出详细日志
2. **错误报警**：关键失败时发送通知（Slack/Feishu）
3. **定期报告**：生成每日/每周报告
4. **手动检查**：定期人工抽查结果

### Q6: 如何定价？

**A**:

根据评分定价：
- A+ (90-100): $9.99
- A (85-89): $4.99
- B+ (80-84): $2.99
- B (70-79): $1.99
- C+ (60-69): $0.99
- C (50-59): 免费
- D (0-49): 不发布

根据市场反馈动态调整价格。

### Q7: 如何避免版权问题？

**A**:

1. **注明来源**：在 SKILL.md 中注明原始来源和作者
2. **不直接复制**：基于提示词生成新的 Skill，而不是直接复制
3. **尊重许可**：检查原始内容的许可协议
4. **社区贡献**：鼓励用户贡献和反馈

### Q8: 如何提升 Skill 的下载量？

**A**:

1. **优化标题和描述**：使用清晰、吸引人的标题
2. **提供丰富的示例**：展示 Skill 的实际效果
3. **收集用户反馈**：根据反馈改进 Skill
4. **营销推广**：在社交媒体、社区推广 Skill
5. **免费试用**：提供免费 Skill 引流

---

## 总结

这份实战教程涵盖了从零开始建立完整的 AI 提示词商业化流程的所有关键步骤：

1. **数据收集**：多源采集（Twitter、Reddit、GitHub、SearXNG）
2. **质量评估**：5 维度评分系统 + AI 语义评估
3. **提示词转换**：自动转换为 Clawdbot Skill 格式
4. **发布到 ClawdHub**：打包、验证、发布、定价
5. **经验教训**：避免常见陷阱，处理 API 限制，人工介入边界

**关键要点**：
- ✅ 质量大于数量
- ✅ 自动化需要人工监控
- ✅ 多数据源整合提高质量
- ✅ 持续迭代和优化

**下一步行动**：
1. 配置环境（API keys、工具）
2. 运行数据收集脚本
3. 评估和清洗数据
4. 转换为 Skills
5. 发布到 ClawdHub

祝你在 AI 提示词商业化道路上取得成功！🚀

---

**文档版本**: 1.0
**创建时间**: 2026-01-31
**最后更新**: 2026-01-31
**作者**: Clawdbot Community
**许可**: MIT
