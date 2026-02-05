#!/bin/bash

# ============================================
# Twitter 自动搜索脚本
# 功能：搜索 Twitter AI 提示词并生成报告
# 频率：每 6 小时执行一次（通过 cron）
# ============================================

set -e  # 遇到错误立即退出

# 配置变量
SEARCH_QUERY='#AIPrompts OR #promptengineering OR "AI prompt engineering" OR "ChatGPT prompts" OR "Claude prompts"'
MAX_RESULTS=50
REPORT_DIR="/root/clawd/ai-prompt-marketplace/reports"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H%M)
REPORT_FILE="$REPORT_DIR/twitter-report-${DATE}-${TIME}.json"
SUMMARY_FILE="$REPORT_DIR/twitter-summary-${DATE}-${TIME}.md"
LOG_FILE="$REPORT_DIR/execution.log"

# 创建目录
mkdir -p "$REPORT_DIR"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Starting Twitter search automation"
log "=========================================="

# 加载 Twitter API key
if [ -f ~/.bashrc ]; then
    # 直接获取 API key 而不是 source 整个文件
    export TWITTER_API_KEY=$(grep "^export TWITTER_API_KEY=" ~/.bashrc | cut -d'"' -f2)
fi

if [ -z "$TWITTER_API_KEY" ]; then
    log "ERROR: TWITTER_API_KEY not found in environment"
    exit 1
fi

log "Twitter API key loaded"

# 执行搜索（使用改进版脚本 - 更配额友好）
log "Searching Twitter for: $SEARCH_QUERY"
log "Max results: $MAX_RESULTS"
log "Using improved search script with language and engagement filtering"

# 执行搜索并提取 JSON 输出（过滤掉 stderr 和其他输出）
# 改进版脚本自带语言过滤（默认英语）和互动过滤
python3 /root/clawd/skills/twitter-search-skill/scripts/twitter_search_improved.py \
    "$TWITTER_API_KEY" \
    "$SEARCH_QUERY" \
    --max-results "$MAX_RESULTS" \
    --query-type Top \
    --lang en \
    --min-likes 10 \
    --format json > "$REPORT_FILE" 2>> "$LOG_FILE"

# 检查结果
if [ $? -eq 0 ]; then
    # 提取统计数据
    if command -v jq &> /dev/null; then
        TOTAL_TWEETS=$(jq -r '.total_tweets // 0' "$REPORT_FILE" 2>/dev/null || echo "0")
    else
        TOTAL_TWEETS=$(python3 -c "import json; data=json.load(open('$REPORT_FILE')); print(data.get('total_tweets', 0))")
    fi

    log "Search completed successfully: $TOTAL_TWEETS tweets found"

    # 去重记录：将新推文记录到去重数据库
    log "Recording tweets to dedup database..."
    DEDUP_RESULT=$(node /root/clawd/scripts/dedup-record-from-json.js "$REPORT_FILE" 2>&1)
    log "$DEDUP_RESULT"

    # 生成 Markdown 摘要
    log "Generating markdown summary..."
    export DATE="$DATE"
    export TIME="$TIME"
    python3 <<'PYTHON_SCRIPT'
import json
import sys
from datetime import datetime

try:
    report_file = "/root/clawd/ai-prompt-marketplace/reports/twitter-report-{date}-{time}.json".format(
        date="{DATE}",
        time="{TIME}"
    )

    # 从环境变量获取文件名
    import os
    date = os.environ.get('DATE', '2026-01-30')
    time = os.environ.get('TIME', '0830')

    report_file = f"/root/clawd/ai-prompt-marketplace/reports/twitter-report-{date}-{time}.json"

    with open(report_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stats = data.get('statistics', {})
    total = data.get('total_tweets', 0)
    fetched = data.get('fetched_at', '')
    query = data.get('query', 'N/A')
    query_type = data.get('query_type', 'N/A')

    md = f"""# Twitter AI 提示词搜索报告

## 📊 基本信息

- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **搜索查询**: {query}
- **查询类型**: {query_type}
- **推文总数**: {total}
- **抓取时间**: {fetched}

## 📈 互动统计

| 指标 | 总数 |
|------|------|
| 总点赞数 | {stats.get('total_engagement', {}).get('likes', 0):,} |
| 总转发数 | {stats.get('total_engagement', {}).get('retweets', 0):,} |
| 总回复数 | {stats.get('total_engagement', {}).get('replies', 0):,} |
| 总引用数 | {stats.get('total_engagement', {}).get('quotes', 0):,} |
| 总浏览数 | {stats.get('total_engagement', {}).get('views', 0):,} |

## 📊 平均指标

| 指标 | 平均值 |
|------|--------|
| 平均点赞/推文 | {stats.get('averages', {}).get('likes_per_tweet', 0):.2f} |
| 平均转发/推文 | {stats.get('averages', {}).get('retweets_per_tweet', 0):.2f} |
| 平均回复/推文 | {stats.get('averages', {}).get('replies_per_tweet', 0):.2f} |

## 🔥 热门标签 (Top 10)
"""

    for tag, count in list(stats.get('top_hashtags', {}).items())[:10]:
        md += f"- #{tag}: {count}次\n"

    md += "\n## 👤 热门提及 (Top 10)\n"
    for mention, count in list(stats.get('top_mentions', {}).items())[:10]:
        md += f"- @{mention}: {count}次\n"

    md += "\n## 🌍 语言分布\n"
    for lang, count in list(stats.get('language_distribution', {}).items())[:5]:
        percentage = (count / total * 100) if total > 0 else 0
        md += f"- {lang}: {count}条 ({percentage:.1f}%)\n"

    md += "\n## 📊 回复率\n"
    md += f"- 回复推文占比: {stats.get('reply_ratio', 0):.1f}%\n"

    # 高价值内容分析
    md += "\n## 💡 高价值内容分析\n"

    if total > 0:
        tweets = data.get('tweets', [])

        # 高互动推文（点赞 > 500）
        high_engagement = [t for t in tweets if t.get('metrics', {}).get('likes', 0) > 500]

        if high_engagement:
            md += f"\n### 🔥 高互动推文（点赞 > 500）\n\n"
            for i, tweet in enumerate(high_engagement[:5], 1):
                author = tweet.get('author', {})
                metrics = tweet.get('metrics', {})
                md += f"""
#### {i}. 高互动推文

- **作者**: @{author.get('username', 'unknown')} ({author.get('name', 'N/A')})
- **粉丝数**: {author.get('followers', 0):,}
- **认证**: {'✅' if author.get('verified', False) else '❌'}
- **互动数据**:
  - 点赞: {metrics.get('likes', 0):,}
  - 转发: {metrics.get('retweets', 0):,}
  - 回复: {metrics.get('replies', 0):,}
  - 浏览: {metrics.get('views', 0):,}
- **链接**: {tweet.get('url', 'N/A')}
- **内容预览**: {tweet.get('text', '')[:200]}...

---

"""

        # 实用 prompt 模板（包含 "prompt" 或 "template" 等关键词）
        prompt_tweets = [t for t in tweets if any(k in t.get('text', '').lower() for k in ['prompt', 'template', '框架', 'framework'])]

        if prompt_tweets:
            md += f"\n### 📝 实用 Prompt 模板 (识别到 {len(prompt_tweets)} 条)\n\n"
            for i, tweet in enumerate(prompt_tweets[:3], 1):
                md += f"""
#### {i}. Prompt 模板

- **作者**: @{tweet.get('author', {}).get('username', 'unknown')}
- **互动**: {tweet.get('metrics', {}).get('likes', 0):,} 点赞
- **链接**: {tweet.get('url', 'N/A')}
- **内容**: {tweet.get('text', '')[:300]}...

---

"""

        # 教程类内容（包含 "guide", "tutorial", "教程", "指南" 等关键词）
        tutorial_tweets = [t for t in tweets if any(k in t.get('text', '').lower() for k in ['guide', 'tutorial', 'how to', '教程', '指南', 'learn'])]

        if tutorial_tweets:
            md += f"\n### 📚 教程/指南类内容 (识别到 {len(tutorial_tweets)} 条)\n\n"
            for i, tweet in enumerate(tutorial_tweets[:3], 1):
                md += f"""
#### {i}. 教程/指南

- **作者**: @{tweet.get('author', {}).get('username', 'unknown')}
- **互动**: {tweet.get('metrics', {}).get('likes', 0):,} 点赞
- **链接**: {tweet.get('url', 'N/A')}
- **内容**: {tweet.get('text', '')[:300]}...

---

"""

        # 热门作者分析
        md += "\n## 👥 热门作者分析\n\n"

        top_authors = stats.get('top_authors_by_followers', [])[:5]
        if top_authors:
            md += "### 粉丝数 Top 5\n\n"
            for i, author in enumerate(top_authors, 1):
                md += f"{i}. **@{author['username']}** ({author.get('name', 'N/A')})\n"
                md += f"   - 粉丝数: {author['followers']:,}\n"
                md += f"   - 认证: {'✅' if author.get('verified') else '❌'}\n"
                md += f"   - 推文数: {author['tweet_count']}\n\n"

        most_active = stats.get('most_active_authors', [])[:5]
        if most_active:
            md += "### 最活跃作者 Top 5\n\n"
            for i, author in enumerate(most_active, 1):
                md += f"{i}. **@{author['username']}** ({author.get('name', 'N/A')})\n"
                md += f"   - 推文数: {author['tweet_count']}\n"
                md += f"   - 粉丝数: {author['followers']:,}\n\n"

    # 转换建议
    md += "\n## 🎯 Skill 转换建议\n\n"

    if total > 0:
        tweets = data.get('tweets', [])

        # 评估转换潜力
        high_potential = []
        medium_potential = []
        low_potential = []

        for tweet in tweets:
            text = tweet.get('text', '').lower()
            metrics = tweet.get('metrics', {})

            # 评估标准
            score = 0
            reasons = []

            # 互动量
            if metrics.get('likes', 0) > 500:
                score += 3
                reasons.append("高互动")
            elif metrics.get('likes', 0) > 200:
                score += 1
                reasons.append("中等互动")

            # 内容类型
            if any(k in text for k in ['prompt', 'template', '模板', '框架']):
                score += 2
                reasons.append("包含模板")
            if any(k in text for k in ['guide', 'tutorial', '教程', 'how to']):
                score += 1
                reasons.append("教程内容")
            if any(k in text for k in ['json', 'format', '格式', '结构']):
                score += 1
                reasons.append("结构化")

            # 长度
            if len(text) > 200:
                score += 1
                reasons.append("内容详细")

            if score >= 4:
                high_potential.append((tweet, reasons, score))
            elif score >= 2:
                medium_potential.append((tweet, reasons, score))
            else:
                low_potential.append((tweet, reasons, score))

        md += f"### 高优先级转换 (⭐⭐⭐⭐⭐) - {len(high_potential)} 条\n\n"

        if high_potential:
            for i, (tweet, reasons, score) in enumerate(high_potential[:5], 1):
                author = tweet.get('author', {})
                metrics = tweet.get('metrics', {})
                md += f"""
#### {i}. 高价值内容

- **作者**: @{author.get('username', 'unknown')}
- **评分**: {score}/5
- **理由**: {', '.join(reasons)}
- **互动**: {metrics.get('likes', 0):,} 点赞
- **链接**: {tweet.get('url', 'N/A')}
- **内容**: {tweet.get('text', '')[:250]}...

---

"""
        else:
            md += "暂未识别到高优先级内容\n\n"

        md += f"\n### 中优先级转换 (⭐⭐⭐) - {len(medium_potential)} 条\n\n"
        if medium_potential:
            for i, (tweet, reasons, score) in enumerate(medium_potential[:3], 1):
                md += f"{i}. @{tweet.get('author', {}).get('username', 'unknown')} - {', '.join(reasons)} ({tweet.get('url', 'N/A')})\n"

    md += f"""

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*下次更新: 约3小时后*
"""

    summary_file = f"/root/clawd/ai-prompt-marketplace/reports/twitter-summary-{date}-{time}.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"Summary generated: {summary_file}")

except Exception as e:
    print(f"Error generating summary: {str(e)}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT

    if [ $? -eq 0 ]; then
        log "Markdown summary generated: $SUMMARY_FILE"
    else
        log "WARNING: Failed to generate markdown summary"
    fi

    # 提交到 Git
    log "Committing to git repository..."
    cd /root/clawd/ai-prompt-marketplace

    git add reports/
    git add TWITTER_AUTOMATION_PLAN.md 2>/dev/null || true
    git commit -m "Twitter search report - $DATE $TIME

- Total tweets: $TOTAL_TWEETS
- Query: $SEARCH_QUERY
- Report: twitter-report-${DATE}-${TIME}.json
- Summary: twitter-summary-${DATE}-${TIME}.md" || log "No changes to commit"

    git push origin master 2>&1 | tee -a "$LOG_FILE" || log "WARNING: Git push failed or already up to date"

    log "Report committed and pushed to repository"

    # 输出执行摘要
    echo ""
    echo "=========================================="
    echo "执行摘要"
    echo "=========================================="
    echo "✅ 搜索成功完成"
    echo "📊 推文总数: $TOTAL_TWEETS"
    echo "📄 JSON 报告: $REPORT_FILE"
    echo "📝 Markdown 摘要: $SUMMARY_FILE"
    echo "🔗 Git 状态: 已提交并推送"
    echo "=========================================="

else
    log "ERROR: Twitter search failed"
    exit 1
fi

log "Script completed successfully"
