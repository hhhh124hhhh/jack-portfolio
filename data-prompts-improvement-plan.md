# Clawdbot 提示词数据源改进方案

**创建日期**: 2026-01-31
**版本**: 1.0
**目标**: 提升提示词数据质量，优化数据收集策略，为技能转换提供高质量素材

---

## 📊 当前问题分析

### 1. Twitter/X 搜索问题

#### 问题详情
- **API 速率限制**: Twitter API 免费计划有严格的速率限制（429 错误）
- **Clawdbot 知名度低**: 搜索 "Clawdbot" 或相关关键词几乎没有结果
- **数据质量偏低**:
  - 多语言混合（英文 89%，西班牙语 11%）
  - 很多内容是推广性质的而非实用提示词
  - 提取逻辑过于简单，误提取率高
- **优质内容稀少**: 19 条推文中，真正可用于技能转换的高质量内容约 8 条（42%）

#### 数据统计（2026-01-29）
| 指标 | 数值 |
|------|------|
| 总推文数 | 19 |
| 高质量提示词 | ~8 条 (42%) |
| 平均互动量 | 1,258 点赞/条 |
| 语言分布 | 英文 89%，西班牙语 11% |

### 2. 搜索策略分析

#### 当前搜索关键词（`search-x-prompts.py`）
```python
SEARCH_QUERIES = [
    "AI prompts",
    "ChatGPT prompts",
    "prompt engineering",
    "Midjourney prompts",
    "AI art prompts",
    "GPT-4 prompts",
    "Claude prompts",
    "AI writing prompts"
]
```

#### 问题
1. **关键词过于宽泛**: "AI prompts" 会返回大量无关内容
2. **缺乏标签过滤**: 没有使用 #AIPrompts、#promptengineering 等精准标签
3. **没有排除噪音**: 没有排除推广内容、低质量账号
4. **单次请求量小**: 每个 query 只获取 10 条，受速率限制严重

### 3. 提示词提取逻辑问题

#### 当前提取逻辑（`extract_prompts_from_text`）
```python
def extract_prompts_from_text(text):
    prompts = []
    # 1. 代码块
    code_blocks = re.findall(r'```([\s\S]*?)```', text)
    # 2. 引号
    quotes = re.findall(r'"([^"]{20,})"', text)
    # 3. 冒号后内容
    colons = re.findall(r':\s*([A-Z][^.?!]{20,})', text)
    # 4. 特定标记
    specific = re.findall(r'(?:Prompt|prompt)[:：]\s*([^\n]{20,})', text)
    return list(set(prompts))
```

#### 问题
1. **误提取率高**: 引号和冒号模式会提取很多非提示词内容
2. **缺乏上下文判断**: 没有判断提取的内容是否真的是提示词
3. **质量评分缺失**: 提取的提示词没有质量评分机制
4. **去重不够**: 仅有简单的去重，没有语义去重

### 4. 现有数据源评估

| 数据源 | 数量 | 质量评分 | 问题 |
|--------|------|----------|------|
| Reddit | 14 条 | 53.5 (平均) | 403 错误（r/prompts），内容偏讨论 |
| Hacker News | 47 条 | 50.0 (平均) | 主要是文章链接，非直接提示词 |
| GitHub | 7 条 | 10.0 (平均) | 提取质量低，短内容多 |
| SearXNG | 76 条 | 0.95 相关性 | 需要二次处理 |
| Twitter | 19 条 | 42% 高质量 | 速率限制，内容质量不稳 |

---

## 🎯 改进目标

### 短期目标（1-2 周）
1. 优化 Twitter 搜索策略，提高单次请求效率
2. 改进提示词提取逻辑，降低误提取率
3. 添加新的高质量数据源
4. 建立基础的质量评估机制

### 中期目标（1 个月）
1. 建立多源数据融合系统
2. 实现自动化的质量评分和过滤
3. 构建提示词分类体系
4. 建立定期更新机制

### 长期目标（3 个月）
1. 建立社区贡献机制
2. 实现提示词 A/B 测试
3. 构建用户反馈闭环
4. 形成可持续的内容生态

---

## 💡 改进建议

### 1. 优化 Twitter 搜索策略

#### 1.1 使用精准标签过滤
```python
# 新的搜索查询（使用标签过滤）
SEARCH_QUERIES = [
    "#AIPrompts -is:retweet lang:en min_faves:10",
    "#promptengineering -is:retweet lang:en min_faves:10",
    "(#ChatGPT OR #ClaudeAI OR #GPT4) prompts -is:retweet lang:en min_faves:10",
    "Midjourney prompts -is:retweet lang:en",
    "\"prompt template\" AI -is:retweet lang:en",
    "\"system prompt\" LLM -is:retweet lang:en",
    "(Claude OR ChatGPT) act as -is:retweet lang:en min_faves:20",
    "\"prompt engineering\" guide tutorial -is:retweet lang:en min_faves:10"
]
```

#### 1.2 添加账号白名单
```python
# 高质量提示词账号
QUALITY_ACCOUNTS = [
    "KeorUnreal",      # AI 图像生成专家
    "MindBranches",    # Prompt engineering 教程
    "fchollet",        # AI 研究者
    "simonw",          # 技术博主
    "swyx",            # AI 社区领袖
    "yoheinakajima",   # AI 应用专家
    "BorisPowerAI"     # Claude 提示词专家
]

# 搜索特定账号的推文
ACCOUNT_QUERIES = [
    f"from:{account} (prompt OR prompt engineering OR #AIPrompts)"
    for account in QUALITY_ACCOUNTS
]
```

#### 1.3 使用 RSS 作为备选方案
```python
# Twitter RSS 端点（Nitter 实例）
RSS_FEEDS = [
    "https://nitter.net/search?q=%23AIPrompts&f=tweets&src=typed_query",
    "https://nitter.net/search?q=prompt%20engineering&f=tweets&src=typed_query",
    "https://nitter.net/search?q=%23promptengineering&f=tweets&src=typed_query"
]
```

#### 1.4 缓存和去重机制
```python
# 使用 Redis 或本地文件缓存
CACHE_DIR = "/root/clawd/cache/twitter"
CACHE_DURATION = 86400  # 24 小时

def get_cached_tweets(query):
    cache_file = os.path.join(CACHE_DIR, hashlib.md5(query).hexdigest() + ".json")
    if os.path.exists(cache_file):
        age = time.time() - os.path.getmtime(cache_file)
        if age < CACHE_DURATION:
            with open(cache_file) as f:
                return json.load(f)
    return None

def cache_tweets(query, tweets):
    cache_file = os.path.join(CACHE_DIR, hashlib.md5(query).hexdigest() + ".json")
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump(tweets, f)
```

### 2. 改进提示词提取逻辑

#### 2.1 增强的提取模式
```python
def extract_prompts_enhanced(text):
    prompts = []

    # 1. JSON 格式提示词（高置信度）
    json_prompts = re.findall(r'\{[^{}]*"prompt"[^{}]*\}', text, re.DOTALL)
    for p in json_prompts:
        try:
            data = json.loads(p)
            if 'prompt' in data:
                prompts.append((data['prompt'], 0.95))  # 高置信度
        except:
            pass

    # 2. 代码块（中高置信度）
    code_blocks = re.findall(r'```(?:prompt|json)?\s*([\s\S]*?)```', text)
    for cb in code_blocks:
        # 检查是否包含提示词关键词
        if any(kw in cb.lower() for kw in ['act as', 'you are', 'role', 'task']):
            prompts.append((cb, 0.85))

    # 3. 结构化提示词模式（中等置信度）
    structured_patterns = [
        r'(?:You are|Act as)\s+([^.!?]+)',
        r'(?:Role|Context|Task):\s*([^\n]+)',
        r'Step\s*\d+:\s*([^\n]+)',
    ]
    for pattern in structured_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if len(m) > 30:  # 足够长
                prompts.append((m, 0.70))

    # 4. 引用中的提示词（低置信度）
    quoted = re.findall(r'"([^"]{50,200})"', text)
    for q in quoted:
        # 检查是否包含提示词特征
        if any(kw in q.lower() for kw in ['please', 'help', 'write', 'create', 'generate']):
            prompts.append((q, 0.50))

    return prompts
```

#### 2.2 质量评分系统
```python
def calculate_prompt_quality(prompt, context=None):
    """
    提示词质量评分（0-100）
    """
    score = 50  # 基础分

    # 1. 长度评分
    length = len(prompt)
    if 50 <= length <= 500:
        score += 20
    elif length > 500:
        score += 10
    elif length < 30:
        score -= 30

    # 2. 结构评分
    if any(char in prompt for char in ['\n', '•', '-', '1.', '2.']):
        score += 15
    if re.search(r'(?i)(role|context|task|output|example|step)', prompt):
        score += 20

    # 3. 具体性评分
    concrete_indicators = ['specific', 'detailed', 'for example', 'such as', 'include']
    if any(ind in prompt.lower() for ind in concrete_indicators):
        score += 10

    # 4. 清晰度评分
    if not re.search(r'\.{2,}|…|etc\.|etc', prompt):
        score += 10
    if prompt.count('!') > 3:
        score -= 10

    # 5. 上下文评分
    if context:
        # 来源权重
        if context['source'] == 'twitter' and context.get('quality_score', 0) > 70:
            score += 15
        elif context['source'] == 'reddit' and context.get('metrics', {}).get('upvotes', 0) > 100:
            score += 10

    # 6. 技术术语评分
    tech_terms = ['claude', 'gpt', 'midjourney', 'stable diffusion', 'api', 'code', 'python']
    if any(term in prompt.lower() for term in tech_terms):
        score += 5

    return max(0, min(100, score))
```

#### 2.3 语义去重
```python
def semantic_deduplicate(prompts, threshold=0.85):
    """
    使用文本相似度进行语义去重
    """
    from difflib import SequenceMatcher

    unique_prompts = []
    for prompt, confidence in prompts:
        is_duplicate = False
        for existing, _ in unique_prompts:
            similarity = SequenceMatcher(None, prompt.lower(), existing.lower()).ratio()
            if similarity > threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_prompts.append((prompt, confidence))

    return unique_prompts
```

### 3. 添加新的高质量数据源

#### 3.1 Reddit 深度挖掘
```python
# 扩展 subreddit 列表
REDDIT_SUBREDDITS = {
    # 提示词专用
    "ChatGPTPromptGenius": {"limit": 25, "score_threshold": 100},
    "PromptEngineering": {"limit": 25, "score_threshold": 50},
    "promptengineering": {"limit": 25, "score_threshold": 50},

    # AI 相关
    "ChatGPT": {"limit": 50, "score_threshold": 500},
    "Claude": {"limit": 25, "score_threshold": 50},
    "artificial": {"limit": 50, "score_threshold": 100},
    "MachineLearning": {"limit": 25, "score_threshold": 50},

    # 垂直领域
    "LocalLLaMA": {"limit": 25, "score_threshold": 50},
    "StableDiffusion": {"limit": 25, "score_threshold": 100},
    "midjourney": {"limit": 25, "score_threshold": 100},

    # 编程相关
    "programming": {"limit": 25, "score_threshold": 200},
    "Python": {"limit": 25, "score_threshold": 200},
}

# 搜索查询优化
REDDIT_SEARCH_QUERIES = [
    "site:reddit.com/r/ChatGPTPromptGenius prompt",
    "site:reddit.com/r/PromptEngineering guide tutorial",
    "site:reddit.com/r/ChatGPT \"act as\"",
    "site:reddit.com/r/Claude prompts",
    "site:reddit.com/r/LocalLLaMA system prompt",
]
```

#### 3.2 GitHub 仓库挖掘
```python
# 高质量 GitHub 仓库
GITHUB_REPOS = [
    {
        "owner": "f",
        "repo": "awesome-chatgpt-prompts",
        "file": "README.md",
        "quality": 90
    },
    {
        "owner": "dair-ai",
        "repo": "Prompt-Engineering-Guide",
        "file": "README.md",
        "quality": 85
    },
    {
        "owner": "microsoft",
        "repo": "prompt-engine",
        "file": "README.md",
        "quality": 85
    },
    {
        "owner": "anthropics",
        "repo": "prompt-engineering-interactive-tutorial",
        "file": "README.md",
        "quality": 90
    },
    {
        "owner": "brexhq",
        "repo": "prompt-engineering",
        "file": "prompt_engineering.html",
        "quality": 80
    },
]

# GitHub 搜索查询
GITHUB_SEARCH_QUERIES = [
    "topic:prompt-templates language:python",
    "topic:prompt-engineering stars:>100",
    "topic:chatgpt-prompts",
    "filename:prompt.md",
    "filename:prompts.json",
]
```

#### 3.3 Medium/博客文章挖掘
```python
# 搜索高质量博客
BLOG_SOURCES = [
    # 官方文档
    "platform.openai.com",
    "docs.anthropic.com",
    "cloud.google.com",

    # 高质量技术博客
    "simonwillison.net",
    "mitchellh.com",
    "jina.ai",
    "huyenchip.com",

    # AI 专题博客
    "towardsdatascience.com",
    "deephunt.in",
    "ai.substack.com",
]

# 搜索查询
BLOG_QUERIES = [
    "site:towardsdatascience.com prompt engineering",
    "site:simonwillison.net prompt",
    "site:mitchellh.com prompt",
    "site:platform.openai.com prompt engineering guide",
    "prompt engineering tutorial 2026",
]
```

#### 3.4 YouTube 视频描述
```python
# YouTube 频道列表
YOUTUBE_CHANNELS = [
    "UC0vBXGSyV14uvJ4hkgDOy8w",  # AI Andrew
    "UCcTc3sNsKnHvhsMSjXJ8t4w",  # Two Minute Papers
    "UCF_bN_IpWtVJQP3m8O0T0fA",  -# Jeremy Howard
    "UCBJycsmduvYEL83R_U4JriQ",  # Marques Brownlee (AI videos)
    "UCrRLhI2A7WcXG9qFmJLk6nQ",  # AI Explained
]

# 搜索查询
YOUTUBE_QUERIES = [
    "prompt engineering tutorial",
    "ChatGPT prompts that work",
    "Claude AI best prompts",
    "Midjourney prompt guide",
]
```

#### 3.5 专门的 Prompt 平台
```python
# Prompt 市场/平台
PROMPT_PLATFORMS = [
    "promptbase.com",
    "prompts.chat",
    "flowgpt.com",
    "snackprompt.com",
    "ai-prompt-generator.com",
]
```

### 4. 数据质量控制

#### 4.1 多维度质量评分
```python
def comprehensive_quality_score(item):
    """
    综合质量评分（0-100）
    """
    scores = []

    # 1. 内容质量
    content_score = calculate_prompt_quality(item.get('content', ''))
    scores.append(('content', content_score, 0.4))

    # 2. 来源可信度
    source_weights = {
        'hacker_news': 85,
        'github': 80,
        'reddit': 70,
        'twitter': 60,
        'web': 50,
    }
    source_score = source_weights.get(item.get('source'), 50)
    scores.append(('source', source_score, 0.2))

    # 3. 互动指标
    if 'metrics' in item:
        metrics = item['metrics']
        if 'upvotes' in metrics:
            upvote_score = min(100, metrics['upvotes'] / 10)
            scores.append(('upvotes', upvote_score, 0.2))
        if 'points' in metrics:
            point_score = min(100, metrics['points'] / 10)
            scores.append(('points', point_score, 0.15))

    # 4. 新鲜度
    if 'created_at' in item:
        age_days = (datetime.now() - datetime.fromisoformat(item['created_at'])).days
        freshness_score = max(0, 100 - age_days * 0.5)  # 每天降低 0.5 分
        scores.append(('freshness', freshness_score, 0.05))

    # 加权平均
    total_score = sum(score * weight for _, score, weight in scores)

    return {
        'score': int(total_score),
        'components': {name: score for name, score, _ in scores}
    }
```

#### 4.2 自动过滤规则
```python
FILTER_RULES = {
    # 最小长度
    'min_length': 30,

    # 最大长度
    'max_length': 2000,

    # 最低质量分数
    'min_quality_score': 50,

    # 禁止内容
    'blocked_keywords': ['spam', 'buy now', 'click here', 'subscribe', 'follow me'],

    # 最小互动量
    'min_upvotes': 10,
    'min_points': 50,

    # 语言过滤
    'allowed_languages': ['en', 'zh', 'ja', 'ko'],  # 英文、中文、日文、韩文

    # 来源白名单
    'allowed_domains': [
        'github.com', 'reddit.com', 'news.ycombinator.com',
        'openai.com', 'anthropic.com', 'platform.openai.com'
    ]
}

def apply_filters(items, rules=FILTER_RULES):
    filtered = []
    for item in items:
        # 长度检查
        content = item.get('content', '')
        if len(content) < rules['min_length'] or len(content) > rules['max_length']:
            continue

        # 质量分数检查
        quality = comprehensive_quality_score(item)
        if quality['score'] < rules['min_quality_score']:
            continue

        # 关键词过滤
        if any(kw in content.lower() for kw in rules['blocked_keywords']):
            continue

        # 互动量检查
        metrics = item.get('metrics', {})
        if metrics.get('upvotes', 0) < rules['min_upvotes']:
            continue
        if metrics.get('points', 0) < rules['min_points']:
            continue

        filtered.append({**item, 'quality_score': quality['score']})

    return filtered
```

### 5. 数据分类和标签

#### 5.1 提示词分类体系
```python
PROMPT_CATEGORIES = {
    # 文本生成
    "text_generation": {
        "keywords": ["write", "generate", "create", "compose", "draft"],
        "subcategories": ["article", "story", "code", "email", "report"]
    },

    # 图像生成
    "image_generation": {
        "keywords": ["midjourney", "stable diffusion", "dall-e", "image", "photo", "art"],
        "subcategories": ["portrait", "landscape", "product", "logo", "abstract"]
    },

    # 视频生成
    "video_generation": {
        "keywords": ["video", "animation", "motion", "sora", "runway"],
        "subcategories": ["short", "animation", "realistic", "style"]
    },

    # 编程辅助
    "coding": {
        "keywords": ["code", "python", "javascript", "debug", "refactor"],
        "subcategories": ["generation", "explanation", "review", "optimization"]
    },

    # 数据分析
    "data_analysis": {
        "keywords": ["analyze", "chart", "graph", "statistics", "visualization"],
        "subcategories": ["insights", "correlation", "trends", "predictions"]
    },

    # 教育学习
    "education": {
        "keywords": ["teach", "explain", "learn", "tutorial", "guide"],
        "subcategories": ["concept", "step-by-step", "quiz", "example"]
    },

    # 创意写作
    "creative_writing": {
        "keywords": ["story", "poem", "narrative", "character", "dialogue"],
        "subcategories": ["fiction", "screenplay", "poetry", "script"]
    },

    # 商业应用
    "business": {
        "keywords": ["marketing", "sales", "business", "strategy", "proposal"],
        "subcategories": ["email", "pitch", "presentation", "report"]
    }
}

def classify_prompt(prompt):
    """
    自动分类提示词
    """
    prompt_lower = prompt.lower()
    scores = {}

    for category, info in PROMPT_CATEGORIES.items():
        score = 0
        for keyword in info['keywords']:
            if keyword in prompt_lower:
                score += 1
        scores[category] = score

    # 返回得分最高的分类
    best_category = max(scores.items(), key=lambda x: x[1])
    if best_category[1] > 0:
        return {
            'category': best_category[0],
            'confidence': best_category[1] / len(PROMPT_CATEGORIES[best_category[0]]['keywords']),
            'all_scores': scores
        }
    return {
        'category': 'general',
        'confidence': 0,
        'all_scores': scores
    }
```

#### 5.2 标签系统
```python
PROMPT_TAGS = {
    # 能力标签
    "capabilities": [
        "reasoning", "creativity", "analysis", "writing", "coding",
        "math", "multimodal", "search", "memory"
    ],

    # 复杂度标签
    "complexity": [
        "simple", "intermediate", "advanced", "expert"
    ],

    # 输出格式
    "output_format": [
        "text", "json", "markdown", "html", "code", "image", "video"
    ],

    # 用途标签
    "purpose": [
        "tutorial", "reference", "template", "example", "exercise"
    ],

    # 目标用户
    "target_audience": [
        "beginner", "intermediate", "advanced", "developer", "designer",
        "writer", "student", "business", "researcher"
    ],

    # 技术栈
    "tech_stack": [
        "chatgpt", "claude", "gpt4", "midjourney", "stable-diffusion",
        "python", "javascript", "langchain", "autogen"
    ]
}

def auto_tag_prompt(prompt):
    """
    自动打标签
    """
    prompt_lower = prompt.lower()
    tags = []

    for category, tag_list in PROMPT_TAGS.items():
        for tag in tag_list:
            # 检查标签是否在提示词中
            if tag.replace('-', ' ') in prompt_lower:
                tags.append((tag, category, 0.9))
            elif tag.replace('-', '') in prompt_lower:
                tags.append((tag, category, 0.7))

    return tags
```

---

## 🚀 实施步骤

### 第一阶段：立即行动（1-3 天）

#### 步骤 1.1：优化现有 Twitter 搜索脚本
**文件**: `/root/clawd/scripts/search-x-prompts.py`

**修改内容**:
1. 更新搜索查询，添加标签过滤
2. 添加账号白名单
3. 实现缓存机制
4. 添加错误重试和速率限制处理

**预期效果**:
- 单次请求获取高质量结果增加 50%
- 减少 API 调用次数 40%
- 降低 429 错误率

#### 步骤 1.2：创建新的数据收集脚本
**新文件**: `/root/clawd/scripts/collect-prompts-multi-source.py`

**功能**:
1. 整合所有数据源（Reddit, GitHub, Hacker News, Web）
2. 统一数据格式
3. 应用过滤规则
4. 自动分类和打标签

**预期效果**:
- 每次收集 100+ 条高质量提示词
- 数据一致性提升
- 分类准确率 > 80%

#### 步骤 1.3：建立质量评估模块
**新文件**: `/root/clawd/scripts/evaluate-prompts-v2.py`

**功能**:
1. 实现综合质量评分
2. 自动过滤低质量内容
3. 生成质量报告

**预期效果**:
- 低质量内容过滤率 > 70%
- 平均质量分数提升至 60+

### 第二阶段：短期优化（1-2 周）

#### 步骤 2.1：扩展 Reddit 数据源
**修改**: `/root/clawd/scripts/collect-reddit-prompts.py`

**新增内容**:
1. 添加 10+ 新 subreddit
2. 实现搜索查询（不仅是热门帖子）
3. 添加评论爬取（很多优质提示词在评论中）

**预期效果**:
- 每次获取 50+ 条新提示词
- 高质量提示词占比提升至 50%+

#### 步骤 2.2：深度挖掘 GitHub
**新文件**: `/root/clawd/scripts/collect-github-prompts.py`

**功能**:
1. 爬取 20+ 高质量仓库
2. 提取 markdown 中的提示词
3. 跟踪仓库更新

**预期效果**:
- 获取 100+ 条结构化提示词
- 建立持续的更新机制

#### 步骤 2.3：添加 YouTube 数据源
**新文件**: `/root/clawd/scripts/collect-youtube-prompts.py`

**功能**:
1. 爬取热门频道视频描述
2. 提取时间戳标记的提示词
3. 识别视频标题中的提示词

**预期效果**:
- 每月获取 50+ 条视频相关提示词
- 覆盖视频生成、教程等领域

### 第三阶段：中期建设（1 个月）

#### 步骤 3.1：构建数据融合系统
**新文件**: `/root/clawd/scripts/prompts-data-fusion.py`

**功能**:
1. 合并多源数据
2. 去重（语义去重）
3. 质量评分标准化
4. 分类和标签统一

**预期效果**:
- 建立统一的数据集（1000+ 条）
- 数据一致性 > 90%

#### 步骤 3.2：建立定期更新机制
**新文件**: `/root/clawd/scripts/update-prompts.sh`

**功能**:
1. 每日自动运行收集脚本
2. 每周生成质量报告
3. 每月数据备份

**配置**:
```bash
# Cron 任务
0 2 * * * /root/clawd/scripts/collect-prompts-multi-source.py >> /root/clawd/logs/daily-collect.log 2>&1
0 6 * * 0 /root/clawd/scripts/generate-quality-report.sh >> /root/clawd/logs/weekly-report.log 2>&1
0 8 1 * * /root/clawd/scripts/backup-prompts.sh >> /root/clawd/logs/monthly-backup.log 2>&1
```

**预期效果**:
- 自动化数据更新
- 减少人工干预

#### 步骤 3.3：创建提示词数据 API
**新文件**: `/root/clawd/scripts/prompts-api.py`

**功能**:
1. 提供 REST API 查询接口
2. 支持按分类、质量、来源筛选
3. 提供 JSON/CSV 导出

**预期效果**:
- 方便其他脚本调用
- 便于集成到技能转换流程

### 第四阶段：长期优化（3 个月）

#### 步骤 4.1：建立用户反馈机制
**新文件**: `/root/clawd/scripts/prompts-feedback.py`

**功能**:
1. 收集用户对提示词的反馈
2. 记录使用频率
3. 识别热门提示词

**预期效果**:
- 持续优化数据质量
- 识别用户需求

#### 步骤 4.2：实现 A/B 测试
**新文件**: `/root/clawd/scripts/prompts-ab-testing.py`

**功能**:
1. 对相似提示词进行对比
2. 记录使用效果
3. 选择最优版本

**预期效果**:
- 提升提示词质量
- 优化用户体验

#### 步骤 4.3：构建社区贡献系统
**新文件**: `/root/clawd/scripts/prompts-community.py`

**功能**:
1. 允许用户提交提示词
2. 自动审核和质量评分
3. 贡献者排名

**预期效果**:
- 持续获取新内容
- 建立用户社区

---

## 📈 预期效果

### 量化指标

| 指标 | 当前值 | 1 个月目标 | 3 个月目标 | 6 个月目标 |
|------|--------|------------|------------|------------|
| 高质量提示词数量 | ~50 | 500 | 2000 | 5000 |
| 平均质量分数 | 45 | 65 | 75 | 80 |
| 分类准确率 | N/A | 70% | 85% | 90% |
| 数据源数量 | 5 | 10 | 15 | 20 |
| 自动化程度 | 20% | 60% | 80% | 90% |
| 更新频率 | 临时 | 每周 | 每日 | 实时 |

### 质量改进

#### 短期（1 个月）
- ✅ Twitter 搜索效率提升 50%
- ✅ 提示词提取准确率提升至 70%
- ✅ 低质量内容过滤率 > 70%
- ✅ 新增 3 个高质量数据源

#### 中期（3 个月）
- ✅ 建立统一的数据集（1000+ 条）
- ✅ 实现自动化分类（准确率 > 85%）
- ✅ 构建完整的质量评估体系
- ✅ 数据覆盖主要提示词类别

#### 长期（6 个月）
- ✅ 形成可持续的内容生态
- ✅ 建立社区贡献机制
- ✅ 实现提示词 A/B 测试
- ✅ 支持多语言（英文、中文、日文）

### 技能转换效果

#### 当前问题
- 数据质量低导致技能转换失败率高
- 缺乏分类导致技能组织混乱
- 没有质量评分导致难以筛选

#### 改进后效果
- ✅ 技能转换成功率提升至 80%+
- ✅ 按类别自动组织技能
- ✅ 优先转换高质量提示词
- ✅ 快速识别可转换内容

---

## 🔧 技术实现细节

### 文件结构
```
/root/clawd/
├── scripts/
│   ├── search-x-prompts.py              # Twitter 搜索（已优化）
│   ├── collect-reddit-prompts.py        # Reddit 收集（已优化）
│   ├── collect-github-prompts.py        # GitHub 收集（新增）
│   ├── collect-youtube-prompts.py       # YouTube 收集（新增）
│   ├── collect-web-prompts.py           # Web 搜索收集（新增）
│   ├── collect-prompts-multi-source.py  # 多源整合（新增）
│   ├── evaluate-prompts-v2.py           # 质量评估（新增）
│   ├── classify-prompts.py              # 分类打标签（新增）
│   ├── prompts-data-fusion.py          # 数据融合（新增）
│   └── update-prompts.sh                # 定期更新（新增）
├── data/
│   └── prompts/
│       ├── raw/                         # 原始数据
│       ├── processed/                   # 处理后数据
│       ├── classified/                  # 分类数据
│       ├── high-quality/                # 高质量数据
│       └── metrics/                     # 质量指标
├── cache/
│   ├── twitter/                         # Twitter 缓存
│   ├── reddit/                          # Reddit 缓存
│   └── github/                          # GitHub 缓存
└── config/
    └── prompts-config.yaml              # 配置文件
```

### 配置文件
```yaml
# /root/clawd/config/prompts-config.yaml

data_sources:
  twitter:
    enabled: true
    rate_limit: 10  # requests per hour
    cache_duration: 86400  # 24 hours
    queries:
      - "#AIPrompts -is:retweet lang:en min_faves:10"
      - "#promptengineering -is:retweet lang:en min_faves:10"
    quality_accounts:
      - KeorUnreal
      - MindBranches
      - fchollet
      - simonw

  reddit:
    enabled: true
    subreddits:
      ChatGPTPromptGenius:
        limit: 25
        score_threshold: 100
      PromptEngineering:
        limit: 25
        score_threshold: 50
    search_queries:
      - "site:reddit.com/r/ChatGPTPromptGenius prompt"
      - "site:reddit.com/r/PromptEngineering guide tutorial"

  github:
    enabled: true
    repos:
      - owner: f
        repo: awesome-chatgpt-prompts
        quality: 90
      - owner: dair-ai
        repo: Prompt-Engineering-Guide
        quality: 85

quality_control:
  min_length: 30
  max_length: 2000
  min_quality_score: 50
  min_upvotes: 10
  min_points: 50

classification:
  enabled: true
  confidence_threshold: 0.6

automation:
  update_schedule: "daily"  # daily, weekly, monthly
  backup_enabled: true
  notification_enabled: true
```

---

## 📝 总结

### 核心改进点

1. **多源数据收集**
   - 从单一的 Twitter 扩展到 10+ 数据源
   - 包括 Reddit、GitHub、YouTube、Hacker News 等
   - 建立统一的收集和处理流程

2. **智能质量控制**
   - 多维度质量评分系统
   - 自动过滤低质量内容
   - 语义去重和重复检测

3. **自动分类和打标签**
   - 8 大主要类别
   - 多维度标签体系
   - 自动化分类准确率 > 80%

4. **持续更新机制**
   - 定时任务自动收集
   - 实时监控数据质量
   - 备份和版本管理

### 实施优先级

**P0（立即执行）**:
- 优化 Twitter 搜索策略
- 实现质量评分系统
- 添加 GitHub 数据源

**P1（1-2 周）**:
- 扩展 Reddit 数据源
- 实现自动分类
- 建立过滤规则

**P2（1 个月）**:
- 数据融合系统
- 定期更新机制
- 提示词 API

**P3（3 个月）**:
- 用户反馈机制
- A/B 测试
- 社区贡献系统

### 成功指标

- ✅ 高质量提示词数量：50 → 2000（40x）
- ✅ 平均质量分数：45 → 75（+67%）
- ✅ 分类准确率：N/A → 85%
- ✅ 自动化程度：20% → 80%
- ✅ 数据源数量：5 → 20
- ✅ 技能转换成功率：提升至 80%+

---

## 📚 参考资料

### 数据源
- [Reddit API](https://www.reddit.com/dev/api/)
- [GitHub API](https://docs.github.com/en/rest)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [Hacker News API](https://github.com/HackerNews/API)
- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api)

### 提示词工程
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Engineering Tutorial](https://github.com/anthropics/prompt-engineering-interactive-tutorial)
- [Microsoft Prompt Engine](https://github.com/microsoft/prompt-engine)

### 相关工具
- [Awesome ChatGPT Prompts](https://github.com/f/awesome-chatgpt-prompts)
- [Prompt Engineering Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)
- [Brex Prompt Engineering Guide](https://github.com/brexhq/prompt-engineering)

---

**文档版本**: 1.0
**最后更新**: 2026-01-31
**负责人**: Clawdbot 数据团队
**审核状态**: 待审核
