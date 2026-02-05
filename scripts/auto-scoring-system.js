#!/usr/bin/env node

/**
 * 全自动化提示词评分系统
 * 
 * 功能：
 * 1. 自动运行质量评估
 * 2. 分析评分分布，判断是否需要调整权重
 * 3. 根据分析结果自动优化权重
 * 4. 生成详细报告并发送到 Slack
 * 5. 记录权重历史，追踪优化效果
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 配置
const CONFIG = {
  // 评估脚本路径
  evaluationScript: '/root/clawd/scripts/evaluate-prompts-quality.js',
  
  // 输出目录
  outputDir: '/root/clawd/reports/auto-scoring',
  historyDir: '/root/clawd/reports/auto-scoring/history',
  
  // Slack 配置
  slackChannel: '#clawdbot',
  
  // 权重优化阈值
  thresholds: {
    targetAverageScore: 65,      // 目标平均分
    minAverageScore: 60,          // 最低平均分
    maxAverageScore: 75,          // 最高平均分
    highQualityTarget: 15,        // 目标高质量占比（B+及以上）%
    minHighQuality: 10,           // 最低高质量占比 %
    maxHighQuality: 25            // 最高高质量占比 %
  },
  
  // 权重调整策略
  weightAdjustmentStrategies: {
    // 平均分太低 → 提高实用性权重
    lowAverage: {
      utility: 0.40,      // +5%
      innovation: 0.20,
      completeness: 0.15, // -5%
      engagement: 0.15,   // -5%
      influence: 0.10
    },
    // 平均分太高 → 降低热度权重
    highAverage: {
      utility: 0.35,
      innovation: 0.20,
      completeness: 0.20,
      engagement: 0.10,   // -5%
      influence: 0.15     // +5%
    },
    // 高质量太少 → 提高创新性和实用性
    lowHighQuality: {
      utility: 0.40,      // +5%
      innovation: 0.25,   // +5%
      completeness: 0.15, // -5%
      engagement: 0.10,   // -5%
      influence: 0.10
    },
    // 默认权重（当前）
    default: {
      utility: 0.35,
      innovation: 0.20,
      completeness: 0.20,
      engagement: 0.15,
      influence: 0.10
    }
  }
};

/**
 * 日志函数
 */
function log(level, message) {
  const timestamp = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
  const levels = { INFO: '📋', SUCCESS: '✅', WARNING: '⚠️', ERROR: '❌' };
  console.log(`${levels[level] || '📋'} [${timestamp}] ${message}`);
}

/**
 * 创建必要的目录
 */
function ensureDirectories() {
  [CONFIG.outputDir, CONFIG.historyDir].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      log('INFO', `创建目录: ${dir}`);
    }
  });
}

/**
 * 加载历史权重记录
 */
function loadWeightHistory() {
  const historyPath = path.join(CONFIG.historyDir, 'weight-history.jsonl');
  const history = [];

  if (fs.existsSync(historyPath)) {
    const lines = fs.readFileSync(historyPath, 'utf8').split('\n').filter(Boolean);
    lines.forEach(line => {
      try {
        history.push(JSON.parse(line));
      } catch (e) {
        // 忽略无效行
      }
    });
  }

  return history;
}

/**
 * 保存权重记录
 */
function saveWeightRecord(record) {
  const historyPath = path.join(CONFIG.historyDir, 'weight-history.jsonl');
  const line = JSON.stringify(record) + '\n';
  fs.appendFileSync(historyPath, line, 'utf8');
}

/**
 * 分析评估结果
 */
function analyzeEvaluation(resultsPath) {
  log('INFO', '分析评估结果...');

  if (!fs.existsSync(resultsPath)) {
    throw new Error(`评估结果文件不存在: ${resultsPath}`);
  }

  const evaluations = JSON.parse(fs.readFileSync(resultsPath, 'utf8'));

  if (evaluations.length === 0) {
    throw new Error('评估结果为空');
  }

  // 计算统计数据
  const total = evaluations.length;
  const scores = evaluations.map(e => e.totalScore);
  const averageScore = scores.reduce((sum, s) => sum + s, 0) / total;

  // 等级分布
  const byGrade = {};
  evaluations.forEach(e => {
    byGrade[e.grade] = (byGrade[e.grade] || 0) + 1;
  });

  // 高质量推文（B+及以上）
  const highQualityCount = (byGrade['A+'] || 0) + (byGrade['A'] || 0) + (byGrade['B+'] || 0);
  const highQualityPercent = (highQualityCount / total * 100);

  // 各维度平均分
  const dimensionAverages = {
    utility: 0,
    innovation: 0,
    completeness: 0,
    engagement: 0,
    influence: 0
  };

  evaluations.forEach(e => {
    Object.keys(dimensionAverages).forEach(dim => {
      dimensionAverages[dim] += e.scores[dim].score;
    });
  });

  Object.keys(dimensionAverages).forEach(dim => {
    dimensionAverages[dim] = (dimensionAverages[dim] / total).toFixed(1);
  });

  const analysis = {
    timestamp: new Date().toISOString(),
    total,
    averageScore: parseFloat(averageScore.toFixed(1)),
    gradeDistribution: byGrade,
    highQualityCount,
    highQualityPercent: parseFloat(highQualityPercent.toFixed(1)),
    dimensionAverages
  };

  log('SUCCESS', `分析完成: 平均分 ${analysis.averageScore}, 高质量 ${analysis.highQualityPercent}%`);
  
  return analysis;
}

/**
 * 判断是否需要调整权重
 */
function shouldAdjustWeights(analysis) {
  const reasons = [];
  let strategy = null;

  // 检查平均分
  if (analysis.averageScore < CONFIG.thresholds.minAverageScore) {
    reasons.push(`平均分过低 (${analysis.averageScore} < ${CONFIG.thresholds.minAverageScore})`);
    strategy = 'lowAverage';
  } else if (analysis.averageScore > CONFIG.thresholds.maxAverageScore) {
    reasons.push(`平均分过高 (${analysis.averageScore} > ${CONFIG.thresholds.maxAverageScore})`);
    strategy = 'highAverage';
  }

  // 检查高质量占比
  if (analysis.highQualityPercent < CONFIG.thresholds.minHighQuality) {
    reasons.push(`高质量占比过低 (${analysis.highQualityPercent}% < ${CONFIG.thresholds.minHighQuality}%)`);
    if (!strategy) strategy = 'lowHighQuality';
  }

  return {
    shouldAdjust: reasons.length > 0,
    reasons,
    strategy: strategy || 'default'
  };
}

/**
 * 获取当前权重
 */
function getCurrentWeights() {
  const scriptContent = fs.readFileSync(CONFIG.evaluationScript, 'utf8');
  
  const weightsMatch = scriptContent.match(/weights:\s*\{([^}]+)\}/s);
  if (!weightsMatch) {
    throw new Error('无法解析当前权重配置');
  }

  const weightsText = weightsMatch[1];
  const utilityMatch = weightsText.match(/utility:\s*([\d.]+)/);
  const innovationMatch = weightsText.match(/innovation:\s*([\d.]+)/);
  const completenessMatch = weightsText.match(/completeness:\s*([\d.]+)/);
  const engagementMatch = weightsText.match(/engagement:\s*([\d.]+)/);
  const influenceMatch = weightsText.match(/influence:\s*([\d.]+)/);

  return {
    utility: utilityMatch ? parseFloat(utilityMatch[1]) : 0,
    innovation: innovationMatch ? parseFloat(innovationMatch[1]) : 0,
    completeness: completenessMatch ? parseFloat(completenessMatch[1]) : 0,
    engagement: engagementMatch ? parseFloat(engagementMatch[1]) : 0,
    influence: influenceMatch ? parseFloat(influenceMatch[1]) : 0
  };
}

/**
 * 应用新的权重
 */
function applyNewWeights(newWeights) {
  log('INFO', '应用新权重...');

  const scriptPath = CONFIG.evaluationScript;
  const backupPath = scriptPath + '.auto-backup';
  
  // 备份原脚本
  fs.copyFileSync(scriptPath, backupPath);
  log('INFO', `已备份到: ${backupPath}`);

  let content = fs.readFileSync(scriptPath, 'utf8');

  // 替换权重
  Object.keys(newWeights).forEach(key => {
    const regex = new RegExp(`${key}:\\s*[\\d.]+`);
    if (regex.test(content)) {
      content = content.replace(regex, `${key}: ${newWeights[key]}`);
      log('INFO', `  ${key}: ${newWeights[key]}`);
    }
  });

  // 保存修改
  fs.writeFileSync(scriptPath, content, 'utf8');
  log('SUCCESS', '权重已更新');
}

/**
 * 生成自动化报告
 */
function generateReport(analysis, currentWeights, decision) {
  const timestamp = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
  
  let report = `# 全自动化评分系统报告

## 📊 基本信息

- **生成时间**: ${timestamp}
- **评估推文数**: ${analysis.total}
- **平均评分**: ${analysis.averageScore}
- **高质量占比**: ${analysis.highQualityPercent}% (${analysis.highQualityCount} 条)

## 📈 当前权重

| 维度 | 权重 | 说明 |
|------|------|------|
| 实用性 (Utility) | ${(currentWeights.utility * 100).toFixed(0)}% | 是否包含实用的提示词、模板或指南 |
| 创新性 (Innovation) | ${(currentWeights.innovation * 100).toFixed(0)}% | 内容是否有独特性、新颖性和前瞻性 |
| 完整性 (Completeness) | ${(currentWeights.completeness * 100).toFixed(0)}% | 内容是否完整、清晰、易于理解 |
| 热度 (Engagement) | ${(currentWeights.engagement * 100).toFixed(0)}% | 基于点赞、转发、回复等互动指标 |
| 作者影响力 (Influence) | ${(currentWeights.influence * 100).toFixed(0)}% | 基于粉丝数、认证状态等 |

## 📊 评分分布

| 等级 | 分数范围 | 数量 | 占比 |
|------|----------|------|------|
| A+ | 90-100 | ${analysis.gradeDistribution['A+'] || 0} | ${(((analysis.gradeDistribution['A+'] || 0) / analysis.total) * 100).toFixed(1)}% |
| A | 85-89 | ${analysis.gradeDistribution['A'] || 0} | ${(((analysis.gradeDistribution['A'] || 0) / analysis.total) * 100).toFixed(1)}% |
| B+ | 80-84 | ${analysis.gradeDistribution['B+'] || 0} | ${(((analysis.gradeDistribution['B+'] || 0) / analysis.total) * 100).toFixed(1)}% |
| B | 70-79 | ${analysis.gradeDistribution['B'] || 0} | ${(((analysis.gradeDistribution['B'] || 0) / analysis.total) * 100).toFixed(1)}% |
| C+ | 60-69 | ${analysis.gradeDistribution['C+'] || 0} | ${(((analysis.gradeDistribution['C+'] || 0) / analysis.total) * 100).toFixed(1)}% |
| C | 50-59 | ${analysis.gradeDistribution['C'] || 0} | ${(((analysis.gradeDistribution['C'] || 0) / analysis.total) * 100).toFixed(1)}% |
| D | 0-49 | ${analysis.gradeDistribution['D'] || 0} | ${(((analysis.gradeDistribution['D'] || 0) / analysis.total) * 100).toFixed(1)}% |

## 🎯 目标与实际

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 平均评分 | ${CONFIG.thresholds.targetAverageScore} | ${analysis.averageScore} | ${analysis.averageScore >= CONFIG.thresholds.minAverageScore && analysis.averageScore <= CONFIG.thresholds.maxAverageScore ? '✅' : '⚠️'} |
| 高质量占比 | ${CONFIG.thresholds.highQualityTarget}% | ${analysis.highQualityPercent}% | ${analysis.highQualityPercent >= CONFIG.thresholds.minHighQuality ? '✅' : '⚠️'} |

## 📊 各维度平均分

| 维度 | 平均分 | 说明 |
|------|--------|------|
| 实用性 | ${analysis.dimensionAverages.utility} / 100 | 提示词实用性 |
| 创新性 | ${analysis.dimensionAverages.innovation} / 100 | 内容创新性 |
| 完整性 | ${analysis.dimensionAverages.completeness} / 100 | 内容完整性 |
| 热度 | ${analysis.dimensionAverages.engagement} / 100 | 互动热度 |
| 影响力 | ${analysis.dimensionAverages.influence} / 100 | 作者影响力 |

## 🔧 权重调整决策

`;

  if (decision.shouldAdjust) {
    report += `### ⚠️ 需要调整权重

**原因**:
${decision.reasons.map(r => `- ${r}`).join('\n')}

**调整策略**: ${decision.strategy}

**建议新权重**:
`;
    const suggestedWeights = CONFIG.weightAdjustmentStrategies[decision.strategy];
    Object.keys(suggestedWeights).forEach(key => {
      const change = suggestedWeights[key] - currentWeights[key];
      const changeText = change > 0 ? `+${(change * 100).toFixed(0)}%` : `${(change * 100).toFixed(0)}%`;
      report += `- ${key}: ${suggestedWeights[key]} (${changeText})\n`;
    });
  } else {
    report += `### ✅ 权重保持不变

当前评分结果符合预期，无需调整权重。

**当前权重表现良好**:
- 平均评分在合理范围 (${CONFIG.thresholds.minAverageScore}-${CONFIG.thresholds.maxAverageScore})
- 高质量占比达标 (>= ${CONFIG.thresholds.minHighQuality}%)
`;
  }

  report += `
## 📝 权重历史

最近 5 次权重调整记录（最新优先）:

`;

  const history = loadWeightHistory().slice(-5).reverse();
  if (history.length === 0) {
    report += `（无历史记录）\n`;
  } else {
    history.forEach((record, idx) => {
      const date = new Date(record.timestamp).toLocaleString('zh-CN', { 
        timeZone: 'Asia/Shanghai', 
        hour12: false 
      });
      report += `\n### ${idx + 1}. ${date}\n`;
      report += `- 平均分: ${record.analysis.averageScore}\n`;
      report += `- 高质量占比: ${record.analysis.highQualityPercent}%\n`;
      if (record.adjusted) {
        report += `- ✅ 已调整权重: ${record.strategy}\n`;
      } else {
        report += `- ✅ 权重保持不变\n`;
      }
    });
  }

  report += `
---

**报告生成时间**: ${timestamp}
**系统版本**: v1.0
`;

  return report;
}

/**
 * 发送到 Slack
 */
function sendToSlack(report, analysis) {
  log('INFO', '生成 Slack 消息...');

  // 提取关键信息
  const summary = `
🎯 全自动化评分系统报告

📊 **评估结果**:
• 总推文数: ${analysis.total}
• 平均评分: ${analysis.averageScore}
• 高质量占比: ${analysis.highQualityPercent}% (${analysis.highQualityCount} 条)

📈 **评分分布**:
• A+: ${analysis.gradeDistribution['A+'] || 0} | A: ${analysis.gradeDistribution['A'] || 0} | B+: ${analysis.gradeDistribution['B+'] || 0}
• B: ${analysis.gradeDistribution['B'] || 0} | C+: ${analysis.gradeDistribution['C+'] || 0} | C: ${analysis.gradeDistribution['C'] || 0} | D: ${analysis.gradeDistribution['D'] || 0}

🎯 **目标达成**:
• 平均评分: ${analysis.averageScore >= CONFIG.thresholds.minAverageScore && analysis.averageScore <= CONFIG.thresholds.maxAverageScore ? '✅' : '⚠️'} (目标: ${CONFIG.thresholds.targetAverageScore})
• 高质量占比: ${analysis.highQualityPercent >= CONFIG.thresholds.minHighQuality ? '✅' : '⚠️'} (目标: ${CONFIG.thresholds.highQualityTarget}%)

📊 **当前权重**:
• 实用性: ${(getCurrentWeights().utility * 100).toFixed(0)}% | 创新性: ${(getCurrentWeights().innovation * 100).toFixed(0)}%
• 完整性: ${(getCurrentWeights().completeness * 100).toFixed(0)}% | 热度: ${(getCurrentWeights().engagement * 100).toFixed(0)}% | 影响力: ${(getCurrentWeights().influence * 100).toFixed(0)}%

📄 完整报告: /root/clawd/reports/quality-evaluation-report.md
`;

  try {
    // 使用 message tool 发送到 Slack
    // 注意：这里我们只是生成消息文本，实际发送会在主流程中完成
    return summary;
  } catch (error) {
    log('ERROR', `发送 Slack 失败: ${error.message}`);
    return null;
  }
}

/**
 * 主函数
 */
async function main() {
  log('INFO', '全自动化评分系统启动\n');
  console.log('='.repeat(60));

  try {
    // 1. 创建必要的目录
    ensureDirectories();

    // 2. 运行评估脚本
    log('INFO', '运行质量评估...');
    console.log('='.repeat(60));
    try {
      execSync(`node ${CONFIG.evaluationScript}`, { stdio: 'inherit' });
    } catch (error) {
      throw new Error(`评估脚本执行失败: ${error.message}`);
    }
    console.log('='.repeat(60));

    // 3. 分析评估结果
    const resultsPath = '/root/clawd/reports/quality-evaluation-results.json';
    const analysis = analyzeEvaluation(resultsPath);

    // 4. 获取当前权重
    const currentWeights = getCurrentWeights();
    log('INFO', `当前权重: ${JSON.stringify(currentWeights)}`);

    // 5. 判断是否需要调整权重
    const decision = shouldAdjustWeights(analysis);
    
    if (decision.shouldAdjust) {
      log('WARNING', `需要调整权重: ${decision.reasons.join(', ')}`);
      
      // 应用新的权重
      const newWeights = CONFIG.weightAdjustmentStrategies[decision.strategy];
      applyNewWeights(newWeights);
      decision.adjusted = true;
      decision.newWeights = newWeights;
    } else {
      log('SUCCESS', '当前权重表现良好，无需调整');
      decision.adjusted = false;
    }

    // 6. 保存权重记录
    saveWeightRecord({
      timestamp: new Date().toISOString(),
      analysis,
      currentWeights,
      decision: {
        shouldAdjust: decision.shouldAdjust,
        reasons: decision.reasons,
        strategy: decision.strategy,
        adjusted: decision.adjusted
      },
      newWeights: decision.newWeights
    });

    // 7. 生成详细报告
    const report = generateReport(analysis, currentWeights, decision);
    const reportPath = path.join(CONFIG.outputDir, `auto-scoring-report-${new Date().getTime()}.md`);
    fs.writeFileSync(reportPath, report, 'utf8');
    log('SUCCESS', `报告已保存: ${reportPath}`);

    // 8. 生成 Slack 摘要
    const slackSummary = sendToSlack(report, analysis);

    console.log('='.repeat(60));
    log('SUCCESS', '全自动化评分系统执行完成！');
    
    console.log(`\n📊 评估结果:`);
    console.log(`   平均评分: ${analysis.averageScore}`);
    console.log(`   高质量占比: ${analysis.highQualityPercent}%`);
    
    if (decision.shouldAdjust) {
      console.log(`\n🔧 权重已调整 (${decision.strategy})`);
    } else {
      console.log(`\n✅ 权重保持不变`);
    }

    console.log(`\n📄 报告: ${reportPath}`);

    // 返回 Slack 摘要，供外部发送
    return slackSummary;

  } catch (error) {
    log('ERROR', `执行失败: ${error.message}`);
    console.error(error.stack);
    process.exit(1);
  }
}

// 运行主函数
if (require.main === module) {
  main().then(slackSummary => {
    if (slackSummary) {
      console.log(`\n${slackSummary}`);
    }
  }).catch(error => {
    console.error(error);
    process.exit(1);
  });
}

module.exports = { main, analyzeEvaluation, shouldAdjustWeights };
