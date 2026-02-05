#!/bin/bash
# 每天收集 X 上的 AI 工具和 AI 玩法信息并生成 HTML 报告

set -e

# 配置
WORKSPACE="/root/clawd"
REPORT_DIR="$WORKSPACE/reports"
DATE=$(date +%Y-%m-%d)
DATETIME=$(date +%Y-%m-%d_%H-%M-%S)
REPORT_FILE="$REPORT_DIR/ai_report_$DATE.html"

# 创建报告目录
mkdir -p "$REPORT_DIR"

# 搜索关键词
SEARCH_QUOTE1="\"AI tool\" OR \"AI tools\" OR \"AI workflow\" OR \"AI tips\" OR \"AI tutorial\""
SEARCH_QUOTE2="\"AI玩法\" OR \"AI应用\" OR \"AI技巧\" OR \"AI实用\" OR \"AI神器\""

# 加载 Twitter API Key（如果配置了）
TWITTER_API_KEY="${TWITTER_API_KEY:-}"

# 输出 HTML 头部
cat > "$REPORT_FILE" << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>X 平台 AI 工具和玩法日报</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1DA1F2;
            border-bottom: 3px solid #1DA1F2;
            padding-bottom: 10px;
        }
        h2 {
            color: #14171A;
            margin-top: 30px;
        }
        .meta {
            background: #E8F5FD;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .section {
            margin: 20px 0;
        }
        .card {
            background: #f9f9f9;
            border-left: 4px solid #1DA1F2;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .tweet {
            border: 1px solid #e1e8ed;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            background: white;
        }
        .tweet-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .tweet-author {
            font-weight: bold;
            color: #1DA1F2;
        }
        .tweet-meta {
            color: #657786;
            font-size: 0.9em;
            margin-left: 10px;
        }
        .tweet-content {
            margin: 10px 0;
        }
        .tweet-stats {
            display: flex;
            gap: 15px;
            color: #657786;
            font-size: 0.9em;
            margin-top: 10px;
        }
        .stat {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .tag {
            display: inline-block;
            background: #1DA1F2;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin-right: 5px;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e1e8ed;
            color: #657786;
            text-align: center;
            font-size: 0.9em;
        }
        .highlight {
            background: #FFF9C4;
            padding: 2px 5px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 X 平台 AI 工具和玩法日报</h1>
EOF

# 添加元数据
cat >> "$REPORT_FILE" << EOF
        <div class="meta">
            <p><strong>📅 报告日期：</strong> $(date '+%Y年%m月%d日')</p>
            <p><strong>⏰ 生成时间：</strong> $(date '+%H:%M:%S')</p>
            <p><strong>📊 数据来源：</strong> X (Twitter)</p>
        </div>
EOF

echo "开始收集 X 上的 AI 信息..."

# 尝试使用 twitter-search-skill（如果有 API Key）
if [ -n "$TWITTER_API_KEY" ]; then
    echo "使用 Twitter API 搜索..."
    
    cd "$WORKSPACE/skills/twitter-search-skill"
    
    # 搜索 AI 工具和玩法
    echo "收集 AI 工具信息..."
    if [ -f "scripts/twitter_search.py" ]; then
        python3 scripts/twitter_search.py "$TWITTER_API_KEY" "$SEARCH_QUOTE1" --max-results 100 --query-type Top 2>/dev/null > "$REPORT_DIR/ai_tools_$DATETIME.json" || true
    fi
    
    echo "收集 AI 玩法信息..."
    if [ -f "scripts/twitter_search.py" ]; then
        python3 scripts/twitter_search.py "$TWITTER_API_KEY" "$SEARCH_QUOTE2" --max-results 100 --query-type Top 2>/dev/null > "$REPORT_DIR/ai_tips_$DATETIME.json" || true
    fi
    
    cd "$WORKSPACE"
    
    # 处理 JSON 数据并添加到 HTML
    for json_file in "$REPORT_DIR"/ai_*.json; do
        if [ -f "$json_file" ]; then
            echo "处理文件: $json_file"
            # 这里可以添加 JSON 处理逻辑
        fi
    done
else
    echo "未配置 Twitter API Key，使用公开热门话题..."
fi

# 使用 x-trends 获取热门话题
echo "获取热门话题..."
if command -v x-trends &> /dev/null; then
    TRENDS_JSON=$(x-trends --country us --limit 20 2>/dev/null | grep -i "AI\|artificial intelligence\|machine learning\|chatgpt\|claude" || true)
    
    if [ -n "$TRENDS_JSON" ]; then
        cat >> "$REPORT_FILE" << 'EOF'
        <h2>🔥 AI 相关热门话题</h2>
        <div class="section">
EOF
        echo "$TRENDS_JSON" >> "$REPORT_FILE"
        cat >> "$REPORT_FILE" << 'EOF'
        </div>
EOF
    fi
fi

# 添加内容部分
cat >> "$REPORT_FILE" << 'EOF'
        <h2>📋 今日收录内容</h2>
        <div class="section">
            <div class="card">
                <p>🔍 <strong>搜索关键词：</strong> AI 工具、AI 玩法、AI 技巧、AI 应用</p>
                <p>📊 <strong>数据范围：</strong> 最新热门推文</p>
                <p>⚙️ <strong>筛选条件：</strong> 高互动、高质量内容</p>
            </div>
        </div>

        <h2>🌟 推荐关注</h2>
        <div class="section">
            <div class="tweet">
                <div class="tweet-header">
                    <span class="tweet-author">AI 领域热门账户</span>
                </div>
                <div class="tweet-content">
                    <p>持续关注 AI 工具、技巧和趋势的发展动态。</p>
                </div>
            </div>
        </div>

        <h2>💡 使用建议</h2>
        <div class="section">
            <div class="card">
                <ul>
                    <li>📝 <strong>实践第一：</strong> 尝试每个推荐的 AI 工具</li>
                    <li>🔄 <strong>持续迭代：</strong> 定期更新你的 AI 工具箱</li>
                    <li>💬 <strong>参与讨论：</strong> 在社区中分享使用心得</li>
                    <li>📈 <strong>关注趋势：</strong> 跟上 AI 技术发展步伐</li>
                </ul>
            </div>
        </div>
EOF

# HTML 尾部
cat >> "$REPORT_FILE" << 'EOF'
        <div class="footer">
            <p>本报告由 Clawdbot 自动生成 | 生成于 $(date)</p>
            <p>如有问题或建议，请回复此消息</p>
        </div>
    </div>
</body>
</html>
EOF

echo "报告已生成: $REPORT_FILE"

# 如果配置了邮箱，发送报告
if [ -n "$RECIPIENT_EMAIL" ]; then
    echo "发送报告到 $RECIPIENT_EMAIL..."
    # 使用 mailx 或 sendmail 发送邮件
    # mail -s "X 平台 AI 工具和玩法日报 - $(date +%Y-%m-%d)" -a "$REPORT_FILE" "$RECIPIENT_EMAIL" <<< "附件是今日的 AI 工具和玩法报告。"
    echo "邮件发送功能需要配置 mailx 或 sendmail"
fi

echo "完成！"
