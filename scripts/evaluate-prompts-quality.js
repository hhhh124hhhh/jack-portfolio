#!/usr/bin/env node

/**
 * AI 提示词质量评估系统
 * 从 Twitter 搜索结果中评估每条推文的质量，并进行等级划分
 */

const fs = require('fs');
const path = require('path');

// 默认配置
const DEFAULT_CONFIG = {
  inputFiles: [
    '/root/clawd/ai-prompt-marketplace/reports/twitter-report-2026-01-30-0835.json',
    '/root/clawd/ai-prompt-marketplace/reports/high-value-tweets.json'
  ],
  outputDir: '/root/clawd/reports',
  outputPath: '/root/clawd/reports/quality-evaluation-results.json',
  reportPath: '/root/clawd/reports/quality-evaluation-report.md',
  // 评分权重配置（调整为更适合当前数据集）
  weights: {
    utility: 0.20,      // 实用性 20%（降低，因为很多推文不含 prompt 模板）
    innovation: 0.15,   // 创新性 15%
    completeness: 0.25, // 完整性 25%（提高，新闻类内容也应获得一定分数）
    engagement: 0.30,   // 热度 30%（提高，高互动代表内容有价值）
    influence: 0.10    // 作者影响力 10%
  }
};

/**
 * 评估推文的实用性 (Utility)
 * 检查内容是否包含实用的提示词、模板或指南
 */
function evaluateUtility(tweet) {
  let score = 0;
  const text = (tweet.text || '').toLowerCase();
  const reasons = [];

  // 基础分：任何有价值的内容至少有 10 分
  score += 10;
  reasons.push('基础内容分');

  // 包含提示词模板
  if (text.includes('prompt:') || text.includes('template') || text.includes('框架') || text.includes('framework')) {
    score += 40;
    reasons.push('包含提示词模板');
  }

  // 包含 JSON 结构化数据
  if (text.includes('"type":') || text.includes('"prompt"') || text.includes('"instructions"')) {
    score += 30;
    reasons.push('包含结构化数据');
  }

  // 包含分步骤指南
  if (text.includes('step') || text.includes('步骤') || text.match(/\d+\./)) {
    score += 25;
    reasons.push('包含分步骤指南');
  }

  // 包含实用关键词
  const utilityKeywords = ['how to', 'how-to', 'guide', '教程', '技巧', '技巧', 'best practices', 'tips'];
  if (utilityKeywords.some(kw => text.includes(kw))) {
    score += 20;
    reasons.push('包含实用指南关键词');
  }

  // 可复制内容
  if (text.length > 100 && (text.includes('```') || text.includes('example') || text.includes('示例'))) {
    score += 15;
    reasons.push('包含可复制示例');
  }

  // AI 相关内容（即使不包含具体 prompt）
  const aiKeywords = ['ai', 'chatgpt', 'claude', 'gpt', 'gemini', 'llm'];
  if (aiKeywords.some(kw => text.includes(kw))) {
    score += 10;
    reasons.push('AI 相关内容');
  }

  return {
    score: Math.min(100, score),
    reasons
  };
}

/**
 * 评估推文的创新性 (Innovation)
 * 检查内容是否有独特性、新颖性和前瞻性
 */
function evaluateInnovation(tweet) {
  let score = 0;
  const text = (tweet.text || '').toLowerCase();
  const reasons = [];

  // 独特的组合或方法
  const innovationKeywords = ['new', 'novel', 'unique', '突破', '创新', 'revolutionary', 'game-changer'];
  if (innovationKeywords.some(kw => text.includes(kw))) {
    score += 25;
    reasons.push('使用创新性关键词');
  }

  // 跨领域应用
  const crossDomain = ['combine', 'integrate', 'fusion', '融合', '混合'];
  if (crossDomain.some(kw => text.includes(kw))) {
    score += 20;
    reasons.push('跨领域融合');
  }

  // 新技术或方法
  const newTech = ['gpt-4', 'claude 3', 'gemini', 'llama 3', 'multimodal', '多模态'];
  if (newTech.some(kw => text.includes(kw))) {
    score += 25;
    reasons.push('涉及最新技术');
  }

  // 原创性指标（低重复度）
  if (text.length > 200 && !text.includes('retweet') && !text.includes('转发')) {
    score += 20;
    reasons.push('原创内容');
  }

  // 探索性内容
  if (text.includes('experiment') || text.includes('实验') || text.includes('exploring')) {
    score += 10;
    reasons.push('探索性内容');
  }

  return {
    score: Math.min(100, score),
    reasons
  };
}

/**
 * 评估推文的完整性 (Completeness)
 * 检查内容是否完整、清晰、易于理解
 */
function evaluateCompleteness(tweet) {
  let score = 0;
  const text = (tweet.text || '').toLowerCase();
  const reasons = [];

  // 基础分：任何有实质内容的推文至少有 20 分
  if (text.length > 50) {
    score += 20;
    reasons.push('有实质内容');
  }

  // 内容长度适中
  if (text.length > 200 && text.length < 1000) {
    score += 20;
    reasons.push('内容长度适中');
  } else if (text.length >= 1000) {
    score += 10;
    reasons.push('内容详细');
  }

  // 结构清晰（有标题、列表等）
  if (text.includes('##') || text.match(/^[#•\-\*]\s+/m) || text.includes('•')) {
    score += 25;
    reasons.push('结构清晰');
  }

  // 包含示例或案例
  if (text.includes('example') || text.includes('for example') || text.includes('例如') || text.includes('案例')) {
    score += 20;
    reasons.push('包含示例');
  }

  // 说明清晰（不使用模糊表达）
  const vagueWords = ['maybe', 'perhaps', '可能', '也许', '大概'];
  const hasVagueWords = vagueWords.some(w => text.includes(w));
  if (!hasVagueWords && text.length > 50) {
    score += 15;
    reasons.push('表达清晰');
  }

  // 有总结或结论
  if (text.includes('conclusion') || text.includes('总结') || text.includes('key takeaway') || text.includes('要点')) {
    score += 20;
    reasons.push('包含总结');
  }

  // 新闻/公告类内容也应获得一定分数
  const newsKeywords = ['announcing', 'released', 'launch', '发布', '新功能', 'new feature', 'introducing'];
  if (newsKeywords.some(kw => text.includes(kw))) {
    score += 10;
    reasons.push('产品公告/新闻');
  }

  return {
    score: Math.min(100, score),
    reasons
  };
}

/**
 * 评估推文的热度 (Engagement)
 * 基于点赞、转发、回复、引用等互动指标
 */
function evaluateEngagement(tweet) {
  const metrics = tweet.metrics || {};
  const likes = metrics.likes || 0;
  const retweets = metrics.retweets || 0;
  const replies = metrics.replies || 0;
  const quotes = metrics.quotes || 0;
  const bookmarks = metrics.bookmarks || 0;
  const views = metrics.views || 0;

  let score = 0;
  const reasons = [];

  // 点赞评分（对数刻度，避免极端值影响）
  if (likes > 0) {
    const likeScore = Math.min(40, Math.log10(likes + 1) * 10);
    score += likeScore;
    reasons.push(`${likes} 点赞 (${likeScore.toFixed(1)}分)`);
  }

  // 转发评分
  if (retweets > 0) {
    const retweetScore = Math.min(30, Math.log10(retweets + 1) * 8);
    score += retweetScore;
    reasons.push(`${retweets} 转发 (${retweetScore.toFixed(1)}分)`);
  }

  // 回复和引用（讨论度）
  if (replies > 0 || quotes > 0) {
    const discussionScore = Math.min(20, Math.log10(replies + quotes + 1) * 7);
    score += discussionScore;
    reasons.push(`${replies + quotes} 讨论 (${discussionScore.toFixed(1)}分)`);
  }

  // 收藏（实用性强）
  if (bookmarks > 0) {
    const bookmarkScore = Math.min(10, Math.log10(bookmarks + 1) * 5);
    score += bookmarkScore;
    reasons.push(`${bookmarks} 收藏 (${bookmarkScore.toFixed(1)}分)`);
  }

  return {
    score: Math.min(100, score),
    reasons,
    rawMetrics: { likes, retweets, replies, quotes, bookmarks, views }
  };
}

/**
 * 评估作者的影响力 (Influence)
 * 基于粉丝数、认证状态等
 */
function evaluateInfluence(tweet) {
  const author = tweet.author || {};
  const followers = author.followers || 0;
  const verified = author.verified || false;
  const username = author.username || 'unknown';

  let score = 0;
  const reasons = [];

  // 认证账号
  if (verified) {
    score += 30;
    reasons.push('认证账号');
  }

  // 粉丝数评分
  if (followers > 0) {
    let followerScore;
    if (followers > 1000000) {
      followerScore = 40;
      reasons.push('粉丝数 > 100万');
    } else if (followers > 100000) {
      followerScore = 35;
      reasons.push('粉丝数 > 10万');
    } else if (followers > 10000) {
      followerScore = 30;
      reasons.push('粉丝数 > 1万');
    } else if (followers > 1000) {
      followerScore = 20;
      reasons.push('粉丝数 > 1千');
    } else if (followers > 100) {
      followerScore = 10;
      reasons.push('粉丝数 > 100');
    } else {
      followerScore = 5;
      reasons.push('粉丝数 < 100');
    }
    score += followerScore;
  }

  // 已知专家账号（基于域名或关键词）
  const expertKeywords = ['ai', 'openai', 'google', 'microsoft', 'anthropic', 'nvidia'];
  const isExpert = expertKeywords.some(kw => username.toLowerCase().includes(kw));
  if (isExpert) {
    score += 20;
    reasons.push('AI 领域专家账号');
  }

  return {
    score: Math.min(100, score),
    reasons,
    authorData: { username, followers, verified }
  };
}

/**
 * 计算总分和等级
 */
function calculateTotalScore(scores, weights) {
  const totalScore =
    scores.utility.score * weights.utility +
    scores.innovation.score * weights.innovation +
    scores.completeness.score * weights.completeness +
    scores.engagement.score * weights.engagement +
    scores.influence.score * weights.influence;

  // 四舍五入到整数
  const roundedScore = Math.round(totalScore);

  // 等级划分
  let grade;
  if (roundedScore >= 90) grade = 'A+';
  else if (roundedScore >= 85) grade = 'A';
  else if (roundedScore >= 80) grade = 'B+';
  else if (roundedScore >= 70) grade = 'B';
  else if (roundedScore >= 60) grade = 'C+';
  else if (roundedScore >= 50) grade = 'C';
  else grade = 'D';

  return {
    score: roundedScore,
    grade,
    breakdown: {
      utility: scores.utility.score * weights.utility,
      innovation: scores.innovation.score * weights.innovation,
      completeness: scores.completeness.score * weights.completeness,
      engagement: scores.engagement.score * weights.engagement,
      influence: scores.influence.score * weights.influence
    }
  };
}

/**
 * 主评估函数
 */
function evaluateTweet(tweet, weights) {
  // 评估各个维度
  const utility = evaluateUtility(tweet);
  const innovation = evaluateInnovation(tweet);
  const completeness = evaluateCompleteness(tweet);
  const engagement = evaluateEngagement(tweet);
  const influence = evaluateInfluence(tweet);

  // 计算总分
  const total = calculateTotalScore(
    { utility, innovation, completeness, engagement, influence },
    weights
  );

  return {
    tweetId: tweet.id,
    url: tweet.url,
    author: tweet.author?.username || 'unknown',
    text: tweet.text?.substring(0, 200) || '',
    scores: {
      utility: { ...utility, weighted: total.breakdown.utility },
      innovation: { ...innovation, weighted: total.breakdown.innovation },
      completeness: { ...completeness, weighted: total.breakdown.completeness },
      engagement: { ...engagement, weighted: total.breakdown.engagement },
      influence: { ...influence, weighted: total.breakdown.influence }
    },
    totalScore: total.score,
    grade: total.grade,
    metrics: engagement.rawMetrics,
    createdAt: tweet.created_at
  };
}

/**
 * 加载推文数据
 */
function loadTweets(inputFiles) {
  const allTweets = [];

  for (const filePath of inputFiles) {
    try {
      if (!fs.existsSync(filePath)) {
        console.warn(`⚠️  文件不存在: ${filePath}`);
        continue;
      }

      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

      if (data.tweets && Array.isArray(data.tweets)) {
        allTweets.push(...data.tweets);
        console.log(`✓ 已加载 ${filePath}: ${data.tweets.length} 条推文`);
      } else if (Array.isArray(data)) {
        allTweets.push(...data);
        console.log(`✓ 已加载 ${filePath}: ${data.length} 条推文`);
      } else {
        console.warn(`⚠️  未知的数据格式: ${filePath}`);
      }
    } catch (error) {
      console.error(`✗ 加载失败 ${filePath}: ${error.message}`);
    }
  }

  return allTweets;
}

/**
 * 生成评估报告
 */
function generateReport(evaluations, config) {
  const timestamp = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });

  // 统计数据
  const total = evaluations.length;
  const byGrade = {};
  evaluations.forEach(e => {
    byGrade[e.grade] = (byGrade[e.grade] || 0) + 1;
  });

  const averageScore = total > 0
    ? (evaluations.reduce((sum, e) => sum + e.totalScore, 0) / total).toFixed(1)
    : 0;

  let report = `# AI 提示词质量评估报告

## 📊 基本信息

- **生成时间**: ${timestamp}
- **评估推文数**: ${total}
- **平均评分**: ${averageScore}

## 🎯 评分标准

| 维度 | 权重 | 说明 |
|------|------|------|
| 实用性 (Utility) | 30% | 是否包含实用的提示词、模板或指南 |
| 创新性 (Innovation) | 20% | 内容是否有独特性、新颖性和前瞻性 |
| 完整性 (Completeness) | 20% | 内容是否完整、清晰、易于理解 |
| 热度 (Engagement) | 20% | 基于点赞、转发、回复等互动指标 |
| 作者影响力 (Influence) | 10% | 基于粉丝数、认证状态等 |

## 📈 评分分布

| 等级 | 分数范围 | 数量 | 占比 |
|------|----------|------|------|
| A+ | 90-100 | ${byGrade['A+'] || 0} | ${((byGrade['A+'] || 0) / total * 100).toFixed(1)}% |
| A | 85-89 | ${byGrade['A'] || 0} | ${((byGrade['A'] || 0) / total * 100).toFixed(1)}% |
| B+ | 80-84 | ${byGrade['B+'] || 0} | ${((byGrade['B+'] || 0) / total * 100).toFixed(1)}% |
| B | 70-79 | ${byGrade['B'] || 0} | ${((byGrade['B'] || 0) / total * 100).toFixed(1)}% |
| C+ | 60-69 | ${byGrade['C+'] || 0} | ${((byGrade['C+'] || 0) / total * 100).toFixed(1)}% |
| C | 50-59 | ${byGrade['C'] || 0} | ${((byGrade['C'] || 0) / total * 100).toFixed(1)}% |
| D | 0-49 | ${byGrade['D'] || 0} | ${((byGrade['D'] || 0) / total * 100).toFixed(1)}% |

## 🏆 Top 10 推文详情

`;

  // Top 10
  const top10 = evaluations.slice(0, 10);
  top10.forEach((item, index) => {
    const s = item.scores;
    report += `### ${index + 1}. @${item.author} - ${item.totalScore}分 [${item.grade}]

**链接**: ${item.url}

**内容预览**:
${item.text}...

**评分明细**:
- 实用性: ${s.utility.score.toFixed(0)}/100 (权重后: ${s.utility.weighted.toFixed(1)})
  - ${s.utility.reasons.join(', ') || '无'}
- 创新性: ${s.innovation.score.toFixed(0)}/100 (权重后: ${s.innovation.weighted.toFixed(1)})
  - ${s.innovation.reasons.join(', ') || '无'}
- 完整性: ${s.completeness.score.toFixed(0)}/100 (权重后: ${s.completeness.weighted.toFixed(1)})
  - ${s.completeness.reasons.join(', ') || '无'}
- 热度: ${s.engagement.score.toFixed(0)}/100 (权重后: ${s.engagement.weighted.toFixed(1)})
  - ${s.engagement.reasons.join(', ') || '无'}
- 作者影响力: ${s.influence.score.toFixed(0)}/100 (权重后: ${s.influence.weighted.toFixed(1)})
  - ${s.influence.reasons.join(', ') || '无'}

**互动数据**:
- 点赞: ${item.metrics.likes || 0}
- 转发: ${item.metrics.retweets || 0}
- 回复: ${item.metrics.replies || 0}
- 引用: ${item.metrics.quotes || 0}
- 收藏: ${item.metrics.bookmarks || 0}
- 浏览: ${item.metrics.views || 0}

---
`;
  });

  // 各等级代表
  report += `\n## 📊 各等级代表推文\n\n`;

  Object.keys(byGrade).forEach(grade => {
    const example = evaluations.find(e => e.grade === grade);
    if (example) {
      report += `### ${grade} 等级示例

- **作者**: @${example.author}
- **评分**: ${example.totalScore}
- **链接**: ${example.url}
- **内容**: ${example.text.substring(0, 150)}...

`;
    }
  });

  // 分析和建议
  report += `## 💡 分析与建议

### 评分分析

`;

  if (averageScore >= 70) {
    report += `- ✅ 平均评分较高 (${averageScore})，整体数据质量良好\n`;
  } else if (averageScore >= 50) {
    report += `- ⚠️  平均评分中等 (${averageScore})，需要优化搜索策略\n`;
  } else {
    report += `- ❌ 平均评分偏低 (${averageScore})，建议大幅调整搜索查询\n`;
  }

  const highQualityCount = (byGrade['A+'] || 0) + (byGrade['A'] || 0) + (byGrade['B+'] || 0);
  const highQualityPercent = (highQualityCount / total * 100).toFixed(1);

  report += `
- ✅ 高质量推文（A+、A、B+）：${highQualityCount} 条 (${highQualityPercent}%)
- ⚠️  需要改进的推文（C+、C、D）：${total - highQualityCount} 条 (${(100 - highQualityPercent).toFixed(1)}%)

### 改进建议

1. **搜索策略优化**:
   - 使用更精确的标签（如 #promptengineering, #AIPrompts）
   - 添加"template"、"framework"等关键词过滤
   - 关注专业 AI 提示词工程账号

2. **质量过滤建议**:
   - 设置最低点赞数阈值（如 min-likes=50）
   - 排除纯新闻类内容
   - 优先选择包含示例的推文

3. **后续工作**:
   - 定期调整评分权重以适应需求
   - 人工审核 Top 20 推文，验证评分准确性
   - 建立优质推文作者白名单

---

**报告生成时间**: ${timestamp}
**评估系统版本**: v1.0
`;

  return report;
}

/**
 * 主函数
 */
async function main() {
  console.log('🎯 AI 提示词质量评估系统\n');
  console.log('=' .repeat(60));

  // 加载配置
  const config = { ...DEFAULT_CONFIG };

  // 创建输出目录
  if (!fs.existsSync(config.outputDir)) {
    fs.mkdirSync(config.outputDir, { recursive: true });
  }

  // 加载推文数据
  console.log('\n📂 加载推文数据...\n');
  const tweets = loadTweets(config.inputFiles);
  console.log(`\n✓ 总共加载了 ${tweets.length} 条推文\n`);

  if (tweets.length === 0) {
    console.error('❌ 没有找到任何推文数据！');
    process.exit(1);
  }

  // 评估每条推文
  console.log('📊 开始评估...\n');
  const evaluations = [];
  for (const tweet of tweets) {
    const evaluation = evaluateTweet(tweet, config.weights);
    evaluations.push(evaluation);
  }

  // 按总分排序
  evaluations.sort((a, b) => b.totalScore - a.totalScore);

  console.log(`✓ 评估完成！\n`);

  // 统计信息
  const averageScore = (evaluations.reduce((sum, e) => sum + e.totalScore, 0) / evaluations.length).toFixed(1);
  const byGrade = {};
  evaluations.forEach(e => {
    byGrade[e.grade] = (byGrade[e.grade] || 0) + 1;
  });

  console.log('📈 评分统计:');
  console.log(`   平均评分: ${averageScore}`);
  console.log(`   A+: ${byGrade['A+'] || 0} 条`);
  console.log(`   A:  ${byGrade['A'] || 0} 条`);
  console.log(`   B+: ${byGrade['B+'] || 0} 条`);
  console.log(`   B:  ${byGrade['B'] || 0} 条`);
  console.log(`   C+: ${byGrade['C+'] || 0} 条`);
  console.log(`   C:  ${byGrade['C'] || 0} 条`);
  console.log(`   D:  ${byGrade['D'] || 0} 条\n`);

  // 保存评估结果（JSON）
  const outputPath = config.outputPath;
  fs.writeFileSync(outputPath, JSON.stringify(evaluations, null, 2), 'utf8');
  console.log(`✓ 评估结果已保存: ${outputPath}\n`);

  // 生成报告（Markdown）
  const reportPath = config.reportPath;
  const report = generateReport(evaluations, config);
  fs.writeFileSync(reportPath, report, 'utf8');
  console.log(`✓ 评估报告已生成: ${reportPath}\n`);

  console.log('=' .repeat(60));
  console.log('✅ 评估完成！');
  console.log(`\n📊 评估结果: ${outputPath}`);
  console.log(`📝 评估报告: ${reportPath}`);
}

// 运行主函数
main().catch(error => {
  console.error('❌ 错误:', error.message);
  console.error(error.stack);
  process.exit(1);
});
