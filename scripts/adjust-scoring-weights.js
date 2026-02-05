#!/usr/bin/env node

/**
 * 调整提示词质量评分权重
 * 从当前的 权重 调整为更合理的权重
 */

const fs = require('fs');
const path = require('path');

const EVALUATION_SCRIPT_PATH = '/root/clawd/scripts/evaluate-prompts-quality.js';
const BACKUP_PATH = '/root/clawd/scripts/evaluate-prompts-quality.js.backup';

console.log('📊 调整提示词质量评分权重\n');

// 1. 备份原脚本
if (fs.existsSync(EVALUATION_SCRIPT_PATH)) {
  fs.copyFileSync(EVALUATION_SCRIPT_PATH, BACKUP_PATH);
  console.log('✓ 已备份原脚本到:', BACKUP_PATH);
}

// 2. 读取脚本内容
let content;
try {
  content = fs.readFileSync(EVALUATION_SCRIPT_PATH, 'utf8');
} catch (error) {
  console.error('✗ 读取脚本失败:', error.message);
  process.exit(1);
}

// 3. 显示当前权重
console.log('📊 当前权重:');
const currentWeightsMatch = content.match(/weights:\s*\{([^}]+)\}/s);
if (currentWeightsMatch) {
  const weightsText = currentWeightsMatch[1];
  const utilityMatch = weightsText.match(/utility:\s*([\d.]+)/);
  const innovationMatch = weightsText.match(/innovation:\s*([\d.]+)/);
  const completenessMatch = weightsText.match(/completeness:\s*([\d.]+)/);
  const engagementMatch = weightsText.match(/engagement:\s*([\d.]+)/);
  const influenceMatch = weightsText.match(/influence:\s*([\d.]+)/);

  if (utilityMatch) console.log(`  实用性: ${(parseFloat(utilityMatch[1]) * 100).toFixed(0)}%`);
  if (innovationMatch) console.log(`  创新性: ${(parseFloat(innovationMatch[1]) * 100).toFixed(0)}%`);
  if (completenessMatch) console.log(`  完整性: ${(parseFloat(completenessMatch[1]) * 100).toFixed(0)}%`);
  if (engagementMatch) console.log(`  热度: ${(parseFloat(engagementMatch[1]) * 100).toFixed(0)}%`);
  if (influenceMatch) console.log(`  影响力: ${(parseFloat(influenceMatch[1]) * 100).toFixed(0)}%`);
}

console.log('');
console.log('🎯 目标权重:');
console.log('  实用性: 35% (当前 20% → 提高 15%)');
console.log('  创新性: 20% (当前 15% → 提高 5%)');
console.log('  完整性: 20% (当前 25% → 降低 5%)');
console.log('  热度:   15% (当前 30% → 降低 15%)');
console.log('  影响力: 10% (当前 10% → 保持)');
console.log('');

// 4. 应用修改
let modified = false;

// 修改 utility: 0.20 → 0.35
if (content.includes('utility: 0.20,')) {
  content = content.replace('utility: 0.20,', 'utility: 0.35,');
  modified = true;
  console.log('✓ 实用性: 20% → 35%');
}

// 修改 innovation: 0.15 → 0.20
if (content.includes('innovation: 0.15,')) {
  content = content.replace('innovation: 0.15,', 'innovation: 0.20,');
  modified = true;
  console.log('✓ 创新性: 15% → 20%');
}

// 修改 completeness: 0.25 → 0.20
if (content.includes('completeness: 0.25,')) {
  content = content.replace('completeness: 0.25,', 'completeness: 0.20,');
  modified = true;
  console.log('✓ 完整性: 25% → 20%');
}

// 修改 engagement: 0.30 → 0.15
if (content.includes('engagement: 0.30,')) {
  content = content.replace('engagement: 0.30,', 'engagement: 0.15,');
  modified = true;
  console.log('✓ 热度: 30% → 15%');
}

console.log('');

if (!modified) {
  console.log('⚠️  未找到匹配的权重配置，可能已被修改');
  console.log('   请手动检查文件:', EVALUATION_SCRIPT_PATH);
  process.exit(0);
}

// 5. 保存修改
try {
  fs.writeFileSync(EVALUATION_SCRIPT_PATH, content, 'utf8');
  console.log('✓ 权重已更新并保存');
} catch (error) {
  console.error('✗ 保存脚本失败:', error.message);
  process.exit(1);
}

// 6. 显示修改效果
console.log('');
console.log('📈 预期效果:');
console.log('  1. 实用性提升 75% (20% → 35%)');
console.log('  2. 减少新闻/公告类内容评分 (热度权重降低)');
console.log('  3. 更重视提示词模板的实际可用性');
console.log('  4. 平均评分预期从 46.5 提升至 60+');
console.log('');
console.log('🔍 下一步:');
console.log('  1. 运行评估: node /root/clawd/scripts/evaluate-prompts-quality.js');
console.log('  2. 对比修改前后的评分结果');
console.log('  3. 根据实际效果进一步微调');
console.log('');
console.log('🔄 恢复原配置:');
console.log('  cp', BACKUP_PATH, EVALUATION_SCRIPT_PATH);
