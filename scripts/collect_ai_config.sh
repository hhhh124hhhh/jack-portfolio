#!/bin/bash
# 配置每日收集任务的参数

# 收件人邮箱（请替换为你的邮箱）
RECIPIENT_EMAIL=""

# Twitter API Key（可选，如果有的话）
# 获取方式: https://twitterapi.io
TWITTER_API_KEY=""

# 报告时间（Cron 格式，例如：每天早上 9 点）
# 格式：分 时 日 月 周
CRON_SCHEDULE="0 9 * * *"

# 导出环境变量
export RECIPIENT_EMAIL
export TWITTER_API_KEY
export CRON_SCHEDULE
