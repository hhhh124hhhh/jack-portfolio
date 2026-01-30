#!/usr/bin/env node

/**
 * 从 Twitter 搜索结果 JSON 文件中提取推文并记录到去重数据库
 * 用途：集成到 auto_twitter_search.sh 中
 */

const fs = require('fs');
const path = require('path');

// 导入去重管理模块
const { recordTweets, getDedupStats } = require('./dedup-manager.js');

/**
 * 主函数
 */
async function main() {
  const jsonFilePath = process.argv[2];

  if (!jsonFilePath) {
    console.error('Usage: node dedup-record-from-json.js <twitter-report.json>');
    process.exit(1);
  }

  try {
    // 检查文件是否存在
    if (!fs.existsSync(jsonFilePath)) {
      console.error('✗ File not found:', jsonFilePath);
      process.exit(1);
    }

    // 读取 JSON 文件
    const data = JSON.parse(fs.readFileSync(jsonFilePath, 'utf8'));

    // 提取推文数组
    const tweets = data.tweets || [];

    if (tweets.length === 0) {
      console.log('✗ No tweets found in file');
      process.exit(0);
    }

    // 记录推文到去重数据库
    const result = recordTweets(tweets);

    // 输出结果
    console.log(`✓ Dedup: ${result.new} new, ${result.duplicate} duplicate tweets recorded`);

    // 可选：显示数据库统计
    const stats = getDedupStats();
    console.log(`✓ Total collected: ${stats.total_collected}, Total converted: ${stats.total_converted}, Pending: ${stats.pending_conversion}`);

  } catch (error) {
    console.error('✗ Error:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// 运行主函数
main().catch(error => {
  console.error('✗ Fatal error:', error.message);
  process.exit(1);
});
