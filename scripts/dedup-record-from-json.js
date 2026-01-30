#!/usr/bin/env node

/**
 * 从 Twitter 搜索报告 JSON 中提取推文并记录到去重数据库
 */

const fs = require('fs');
const path = require('path');

// 加载去重管理模块
const dedupPath = '/root/clawd/scripts/dedup-manager.js';
if (!fs.existsSync(dedupPath)) {
  console.error('Error: dedup-manager.js not found');
  process.exit(1);
}

const {
  recordTweets,
  getDedupStats
} = require(dedupPath);

/**
 * 从 Twitter 报告中提取推文
 */
function extractTweetsFromReport(reportPath) {
  try {
    if (!fs.existsSync(reportPath)) {
      console.error(`Error: Report file not found: ${reportPath}`);
      process.exit(1);
    }

    const data = JSON.parse(fs.readFileSync(reportPath, 'utf8'));

    // 检查数据格式
    let tweets = [];

    if (data.tweets && Array.isArray(data.tweets)) {
      tweets = data.tweets;
    } else if (Array.isArray(data)) {
      tweets = data;
    } else {
      console.error('Error: Unknown data format in report');
      process.exit(1);
    }

    return tweets;
  } catch (error) {
    console.error(`Error parsing report: ${error.message}`);
    process.exit(1);
  }
}

/**
 * 主函数
 */
function main() {
  const reportPath = process.argv[2];

  if (!reportPath) {
    console.error('Usage: node dedup-record-from-json.js <report-file.json>');
    process.exit(1);
  }

  console.log(`Loading report: ${reportPath}`);

  // 提取推文
  const tweets = extractTweetsFromReport(reportPath);
  console.log(`Found ${tweets.length} tweets in report`);

  if (tweets.length === 0) {
    console.log('No tweets to record');
    return;
  }

  // 记录到去重数据库
  console.log('Recording tweets to dedup database...');
  const result = recordTweets(tweets);

  // 显示结果
  console.log('\n去重记录结果:');
  console.log(`  新推文: ${result.new} 条`);
  console.log(`  重复推文: ${result.duplicate} 条`);

  // 更新统计信息
  const stats = getDedupStats();
  console.log('\n当前数据库状态:');
  console.log(`  总已收集: ${stats.total_collected} 条`);
  console.log(`  已转换 Skill: ${stats.total_converted} 条`);
  console.log(`  待转换: ${stats.pending_conversion} 条`);
}

// 运行
if (require.main === module) {
  main();
}

module.exports = { extractTweetsFromReport };
