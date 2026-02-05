#!/usr/bin/env node

/**
 * 修复去重数据库 Bug
 * 问题: pending_conversion 可能为负数
 * 解决方案: 添加边界检查并重置数据库
 */

const fs = require('fs');
const path = require('path');

const DEDUP_DB_PATH = '/root/clawd/data/dedup/processed-tweets.json';
const BACKUP_PATH = '/root/clawd/data/dedup/processed-tweets.json.backup';

console.log('🔧 修复去重数据库 Bug\n');

// 1. 备份当前数据库
if (fs.existsSync(DEDUP_DB_PATH)) {
  fs.copyFileSync(DEDUP_DB_PATH, BACKUP_PATH);
  console.log('✓ 已备份当前数据库到:', BACKUP_PATH);
}

// 2. 读取数据库
let db;
try {
  const data = fs.readFileSync(DEDUP_DB_PATH, 'utf8');
  db = JSON.parse(data);
} catch (error) {
  console.error('✗ 读取数据库失败:', error.message);
  process.exit(1);
}

// 3. 诊断问题
console.log('\n📊 当前数据库状态:');
console.log('  版本:', db.version);
console.log('  最后更新:', db.last_updated);
console.log('  已收集推文:', db.collected_tweets.length);
console.log('  已转换 Skill:', db.converted_skills.length);

const pendingBefore = db.collected_tweets.length - db.converted_skills.length;
console.log('  待转换推文 (旧算法):', pendingBefore);

// 4. 修复 bug
if (!db.collected_tweets || !Array.isArray(db.collected_tweets)) {
  console.log('\n⚠️  collected_tweets 不是有效数组，重新初始化');
  db.collected_tweets = [];
}

if (!db.converted_skills || !Array.isArray(db.converted_skills)) {
  console.log('\n⚠️  converted_skills 不是有效数组，重新初始化');
  db.converted_skills = [];
}

// 5. 计算正确的待转换推文数（使用 Math.max 避免负数）
const pendingAfter = Math.max(0, db.collected_tweets.length - db.converted_skills.length);
console.log('  待转换推文 (修复后):', pendingAfter);

// 6. 修复不一致问题
if (db.converted_skills.length > 0 && db.collected_tweets.length === 0) {
  console.log('\n⚠️  发现数据不一致: 有转换记录但没有收集记录');

  const convertedCount = db.converted_skills.length;
  const collected = db.converted_skills.map(url => ({
    url: url,
    collected_at: '2026-01-30T00:00:00.000Z', // 未知时间
    note: '从 converted_skills 恢复'
  }));

  // 将转换的推文添加到已收集列表
  db.collected_tweets = collected;

  console.log(`✓ 已恢复 ${convertedCount} 条推文到 collected_tweets`);
}

// 7. 更新时间戳
db.last_updated = new Date().toISOString();
db.version = "1.1"; // 升级版本号

// 8. 保存修复后的数据库
try {
  fs.writeFileSync(DEDUP_DB_PATH, JSON.stringify(db, null, 2), 'utf8');
  console.log('\n✓ 数据库已保存并修复');
} catch (error) {
  console.error('\n✗ 保存数据库失败:', error.message);
  process.exit(1);
}

// 9. 显示修复后的状态
console.log('\n📊 修复后状态:');
console.log('  版本:', db.version);
console.log('  最后更新:', db.last_updated);
console.log('  已收集推文:', db.collected_tweets.length);
console.log('  已转换 Skill:', db.converted_skills.length);
console.log('  待转换推文:', Math.max(0, db.collected_tweets.length - db.converted_skills.length));

console.log('\n✅ 修复完成！');
console.log('\n下一步:');
console.log('  1. 验证修复: node /root/clawd/scripts/dedup-manager.js stats');
console.log('  2. 如有问题，恢复备份: cp', BACKUP_PATH, DEDUP_DB_PATH);
