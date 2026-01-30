#!/usr/bin/env node

/**
 * Twitter 推文去重管理系统
 * 防止重复收集和转换相同推文的 Skill
 */

const fs = require('fs');
const path = require('path');

// 去重数据库路径
const DEDUP_DB_PATH = '/root/clawd/data/dedup/processed-tweets.json';

/**
 * 加载去重数据库
 */
function loadDedupDB() {
  try {
    if (!fs.existsSync(DEDUP_DB_PATH)) {
      // 创建默认数据库
      const defaultDB = {
        version: "1.0",
        last_updated: new Date().toISOString(),
        collected_tweets: [],
        converted_skills: []
      };
      fs.writeFileSync(DEDUP_DB_PATH, JSON.stringify(defaultDB, null, 2), 'utf8');
      return defaultDB;
    }

    const data = fs.readFileSync(DEDUP_DB_PATH, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Error loading dedup database:', error.message);
    return {
      version: "1.0",
      last_updated: new Date().toISOString(),
      collected_tweets: [],
      converted_skills: []
    };
  }
}

/**
 * 保存去重数据库
 */
function saveDedupDB(db) {
  db.last_updated = new Date().toISOString();
  fs.writeFileSync(DEDUP_DB_PATH, JSON.stringify(db, null, 2), 'utf8');
}

/**
 * 从推文中提取唯一标识符
 * 优先使用 URL，其次使用 ID
 */
function getTweetIdentifier(tweet) {
  if (tweet.url) {
    return tweet.url;
  }
  if (tweet.id) {
    return `twitter:${tweet.id}`;
  }
  throw new Error('Tweet must have either url or id');
}

/**
 * 检查推文是否已收集
 * @param {Object} tweet - 推文对象，包含 url 或 id
 * @returns {boolean}
 */
function isTweetCollected(tweet) {
  const db = loadDedupDB();
  const identifier = getTweetIdentifier(tweet);
  return db.collected_tweets.includes(identifier);
}

/**
 * 记录新收集的推文
 * @param {Object} tweet - 推文对象
 * @returns {boolean} - true 如果是新的，false 如果已存在
 */
function recordTweet(tweet) {
  const db = loadDedupDB();
  const identifier = getTweetIdentifier(tweet);

  if (db.collected_tweets.includes(identifier)) {
    return false; // 已存在
  }

  db.collected_tweets.push(identifier);
  saveDedupDB(db);
  return true; // 新记录
}

/**
 * 批量记录推文
 * @param {Array} tweets - 推文数组
 * @returns {Object} - { new: number, duplicate: number }
 */
function recordTweets(tweets) {
  const db = loadDedupDB();
  let newCount = 0;
  let duplicateCount = 0;

  for (const tweet of tweets) {
    try {
      const identifier = getTweetIdentifier(tweet);

      if (db.collected_tweets.includes(identifier)) {
        duplicateCount++;
      } else {
        db.collected_tweets.push(identifier);
        newCount++;
      }
    } catch (error) {
      console.warn('Warning: Failed to process tweet:', error.message);
    }
  }

  saveDedupDB(db);
  return { new: newCount, duplicate: duplicateCount };
}

/**
 * 检查推文是否已转换为 Skill
 * @param {Object} tweet - 推文对象
 * @returns {boolean}
 */
function isTweetConverted(tweet) {
  const db = loadDedupDB();
  const identifier = getTweetIdentifier(tweet);
  return db.converted_skills.includes(identifier);
}

/**
 * 记录转换的 Skill
 * @param {Object} tweet - 推文对象
 * @param {string} skillName - 生成的 Skill 文件名
 * @returns {boolean}
 */
function recordConvertedSkill(tweet, skillName) {
  const db = loadDedupDB();
  const identifier = getTweetIdentifier(tweet);

  if (db.converted_skills.includes(identifier)) {
    return false; // 已转换
  }

  db.converted_skills.push(identifier);
  saveDedupDB(db);
  return true; // 新记录
}

/**
 * 获取数据库统计信息
 */
function getDedupStats() {
  const db = loadDedupDB();
  return {
    version: db.version,
    last_updated: db.last_updated,
    total_collected: db.collected_tweets.length,
    total_converted: db.converted_skills.length,
    pending_conversion: db.collected_tweets.length - db.converted_skills.length
  };
}

/**
 * 清理旧的记录（可选）
 * @param {number} days - 保留最近 N 天的记录
 */
function cleanupOldRecords(days = 30) {
  const db = loadDedupDB();
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);

  // 简单实现：清理所有记录（可以根据需要改进）
  console.log(`Cleanup: Would remove records older than ${days} days`);
  // 实际实现需要为每条记录添加时间戳
  return db;
}

/**
 * 导出为命令行工具
 */
if (require.main === module) {
  const command = process.argv[2];
  const args = process.argv.slice(3);

  switch (command) {
    case 'stats':
      const stats = getDedupStats();
      console.log('去重数据库统计：');
      console.log(`  版本: ${stats.version}`);
      console.log(`  最后更新: ${stats.last_updated}`);
      console.log(`  已收集推文: ${stats.total_collected}`);
      console.log(`  已转换 Skill: ${stats.total_converted}`);
      console.log(`  待转换推文: ${stats.pending_conversion}`);
      break;

    case 'check':
      const checkUrl = args[0];
      if (!checkUrl) {
        console.error('Usage: dedup check <url>');
        process.exit(1);
      }
      const collected = isTweetCollected({ url: checkUrl });
      const converted = isTweetConverted({ url: checkUrl });
      console.log(`推文 ${checkUrl}:`);
      console.log(`  已收集: ${collected ? '是' : '否'}`);
      console.log(`  已转换: ${converted ? '是' : '否'}`);
      break;

    case 'record':
      const recordUrl = args[0];
      if (!recordUrl) {
        console.error('Usage: dedup record <url>');
        process.exit(1);
      }
      const isNew = recordTweet({ url: recordUrl });
      console.log(`${isNew ? '✓ 新记录' : '✗ 已存在'}: ${recordUrl}`);
      break;

    case 'help':
    default:
      console.log(`
Twitter 推文去重管理系统

用法:
  node dedup-manager.js <command> [options]

命令:
  stats              显示数据库统计信息
  check <url>         检查推文状态（是否已收集/转换）
  record <url>        记录新推文
  help                显示此帮助信息

示例:
  node dedup-manager.js stats
  node dedup-manager.js check https://x.com/username/status/12345
  node dedup-manager.js record https://x.com/username/status/12345
`);
      break;
  }
}

// 导出函数供其他模块使用
module.exports = {
  loadDedupDB,
  saveDedupDB,
  getTweetIdentifier,
  isTweetCollected,
  recordTweet,
  recordTweets,
  isTweetConverted,
  recordConvertedSkill,
  getDedupStats,
  cleanupOldRecords
};
