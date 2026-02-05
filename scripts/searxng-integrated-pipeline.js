#!/usr/bin/env node

/**
 * SearXNG 集成管道脚本
 *
 * 为 AI 提示词抓取 → 评估 → 转换流程提供三个关键检查点：
 * 1. check-originality: 验证内容原创性
 * 2. quality-augment: 质量评估增强
 * 3. check-duplicate: 避免重复技能
 *
 * @see /root/clawd/scripts/tweet-to-skill-converter.js
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const http = require('https');

// ========== 配置 ==========

const SEARXNG_URL = 'http://localhost:8080';
const SEARXNG_SCRIPT = '/root/clawd/skills/searxng/scripts/searxng.py';
const CACHE_DIR = '/root/clawd/data/searxng-cache';
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24小时缓存有效期
const USE_HTTP_DIRECT = true; // 使用直接HTTP请求（更可靠）

const CONFIG = {
  // 原创性检查配置
  originality: {
    resultCount: 5,
    minSimilarityThreshold: 0.7, // 相似度阈值
    scoreWeight: {
      contentMatch: 0.6,
      titleMatch: 0.4
    }
  },

  // 质量评估配置
  quality: {
    resultCount: 8,
    minRelevanceScore: 0.3
  },

  // 去重检查配置
  duplicate: {
    webResultCount: 5,
    clawdHubResultCount: 5,
    similarityThreshold: 0.6
  },

  // 默认搜索参数
  search: {
    timeout: 30000, // 30秒超时
    retries: 2,
    language: 'auto',
    format: 'json'
  }
};

// ========== 类型定义 (JSDoc) ==========

/**
 * @typedef {Object} SearchResult
 * @property {string} title - 结果标题
 * @property {string} url - 结果URL
 * @property {string} content - 结果内容摘要
 * @property {string} engine - 搜索引擎
 * @property {number} score - 相关性得分
 * @property {string} [thumbnail] - 缩略图URL
 */

/**
 * @typedef {Object} CacheEntry
 * @property {string} query - 搜索查询
 * @property {SearchResult[]} results - 搜索结果
 * @property {number} timestamp - 缓存时间戳
 */

/**
 * @typedef {Object} OriginalityResult
 * @property {number} originalityScore - 原创性评分 (0-100)
 * @property {number} similarityScore - 相似度评分 (0-100)
 * @property {SearchResult[]} similarContent - 相似内容列表
 * @property {string} recommendation - 建议: 'proceed', 'caution', 'skip'
 */

/**
 * @typedef {Object} QualityAugmentResult
 * @property {SearchResult[]} backgroundInfo - 背景信息
 * @property {SearchResult[]} bestPractices - 最佳实践
 * @property {string[]} qualityAssessment - 质量评估建议
 */

/**
 * @typedef {Object} DuplicateResult
 * @property {boolean} isDuplicate - 是否重复
 * @property {number} duplicateRisk - 重复风险 (0-100)
 * @property {SearchResult[]} similarSkills - 相似技能列表
 * @property {string[]} differentiationSuggestions - 差异化建议
 */

// ========== 缓存管理 ==========

/**
 * 初始化缓存目录
 */
function initCache() {
  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
  }
}

/**
 * 生成缓存键
 * @param {string} query - 搜索查询
 * @param {string} [category] - 搜索类别
 * @returns {string} - 缓存键
 */
function getCacheKey(query, category = 'general') {
  const hash = crypto
    .createHash('md5')
    .update(`${query}:${category}`)
    .digest('hex');
  return path.join(CACHE_DIR, `${hash}.json`);
}

/**
 * 从缓存读取结果
 * @param {string} query - 搜索查询
 * @param {string} [category] - 搜索类别
 * @returns {CacheEntry|null}
 */
function getFromCache(query, category = 'general') {
  try {
    const cachePath = getCacheKey(query, category);
    if (!fs.existsSync(cachePath)) {
      return null;
    }

    const data = JSON.parse(fs.readFileSync(cachePath, 'utf8'));
    const age = Date.now() - data.timestamp;

    if (age > CACHE_TTL) {
      // 缓存过期，删除
      fs.unlinkSync(cachePath);
      return null;
    }

    console.log(`✓ 缓存命中: ${query.substring(0, 50)}...`);
    return data;
  } catch (error) {
    console.warn(`缓存读取失败: ${error.message}`);
    return null;
  }
}

/**
 * 保存结果到缓存
 * @param {string} query - 搜索查询
 * @param {SearchResult[]} results - 搜索结果
 * @param {string} [category] - 搜索类别
 */
function saveToCache(query, results, category = 'general') {
  try {
    const cachePath = getCacheKey(query, category);
    const data = {
      query,
      results,
      timestamp: Date.now()
    };
    fs.writeFileSync(cachePath, JSON.stringify(data, null, 2));
  } catch (error) {
    console.warn(`缓存保存失败: ${error.message}`);
  }
}

// ========== SearXNG 搜索 ==========

/**
 * 执行 SearXNG 搜索
 * @param {string} query - 搜索查询
 * @param {Object} options - 搜索选项
 * @returns {Promise<SearchResult[]>}
 */
async function searchSearXNG(query, options = {}) {
  const {
    numResults = CONFIG.quality.resultCount,
    category = 'general',
    language = CONFIG.search.language,
    timeRange = null
  } = options;

  // 检查缓存
  const cached = getFromCache(query, category);
  if (cached) {
    return cached.results;
  }

  let results = [];

  // 优先使用HTTP直接搜索（更可靠）
  if (USE_HTTP_DIRECT) {
    try {
      results = await searchSearXNGHTTP(query, options);
      if (results.length > 0) {
        saveToCache(query, results, category);
        return results;
      }
    } catch (error) {
      console.warn(`HTTP搜索失败，尝试命令行方式: ${error.message}`);
    }
  }

  // 备用方案：使用命令行搜索
  let command = `uv run ${SEARXNG_SCRIPT} search ${JSON.stringify(query)} -n ${numResults} --format json`;

  if (category !== 'general') {
    command += ` --category ${category}`;
  }

  if (language !== 'auto') {
    command += ` --language ${language}`;
  }

  if (timeRange) {
    command += ` --time-range ${timeRange}`;
  }

  console.log(`🔍 命令行搜索: ${query.substring(0, 50)}${query.length > 50 ? '...' : ''}`);

  // 执行搜索（带重试）
  let attempts = 0;
  const maxAttempts = CONFIG.search.retries + 1;

  while (attempts < maxAttempts) {
    try {
      const result = await executeCommand(command, CONFIG.search.timeout);
      const data = JSON.parse(result);

      if (data.error) {
        throw new Error(data.error);
      }

      results = (data.results || []).map(normalizeSearchResult);

      // 保存到缓存
      saveToCache(query, results, category);

      console.log(`✓ 命令行搜索完成: ${results.length} 个结果`);
      return results;
    } catch (error) {
      attempts++;
      if (attempts < maxAttempts) {
        console.warn(`搜索失败，重试 (${attempts}/${maxAttempts}): ${error.message}`);
        await sleep(1000); // 等待1秒后重试
      } else {
        console.error(`搜索失败: ${error.message}`);
        return results; // 返回已有结果（可能是空的）
      }
    }
  }

  return results;
}

/**
 * 标准化搜索结果
 * @param {Object} raw - 原始搜索结果
 * @returns {SearchResult}
 */
function normalizeSearchResult(raw) {
  return {
    title: raw.title || 'Untitled',
    url: raw.url || '',
    content: raw.content || '',
    engine: raw.engine || 'unknown',
    score: raw.score || 0,
    thumbnail: raw.thumbnail || '',
    publishedDate: raw.publishedDate || null
  };
}

/**
 * 执行 Shell 命令
 * @param {string} command - 命令
 * @param {number} timeout - 超时时间（毫秒）
 * @returns {Promise<string>}
 */
function executeCommand(command, timeout = CONFIG.search.timeout) {
  return new Promise((resolve, reject) => {
    exec(command, { timeout, maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
      if (error) {
        if (error.killed && error.signal === 'SIGTERM') {
          reject(new Error('Command timeout'));
        } else {
          reject(new Error(stderr || error.message));
        }
      } else {
        resolve(stdout);
      }
    });
  });
}

/**
 * 通过curl直接搜索SearXNG（更可靠的方法）
 * @param {string} query - 搜索查询
 * @param {Object} options - 搜索选项
 * @returns {Promise<SearchResult[]>}
 */
async function searchSearXNGHTTP(query, options = {}) {
  const {
    numResults = CONFIG.quality.resultCount,
    category = 'general',
    language = CONFIG.search.language,
    timeRange = null
  } = options;

  // 构建URL参数
  const params = new URLSearchParams({
    q: query,
    format: 'json',
    language: language,
    categories: category
  });

  if (timeRange) {
    params.append('time_range', timeRange);
  }

  const url = `${SEARXNG_URL}/search?${params.toString()}`;

  console.log(`🔍 curl搜索: ${query.substring(0, 50)}${query.length > 50 ? '...' : ''}`);

  return new Promise((resolve, reject) => {
    // 使用curl进行HTTP请求
    exec(`curl -s -k "${url}"`, { timeout: CONFIG.search.timeout, maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(`curl请求失败: ${stderr || error.message}`));
        return;
      }

      try {
        const parsed = JSON.parse(stdout);
        const results = (parsed.results || []).map(normalizeSearchResult);
        console.log(`✓ curl搜索完成: ${results.length} 个结果`);
        resolve(results);
      } catch (parseError) {
        reject(new Error(`解析响应失败: ${parseError.message}`));
      }
    });
  });
}

/**
 * 异步睡眠
 * @param {number} ms - 毫秒
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ========== 文本相似度计算 ==========

/**
 * 计算文本相似度（简单的词重叠算法）
 * @param {string} text1 - 文本1
 * @param {string} text2 - 文本2
 * @returns {number} - 相似度 (0-1)
 */
function calculateSimilarity(text1, text2) {
  const words1 = new Set(text1.toLowerCase().split(/\s+/).filter(w => w.length > 2));
  const words2 = new Set(text2.toLowerCase().split(/\s+/).filter(w => w.length > 2));

  if (words1.size === 0 || words2.size === 0) {
    return 0;
  }

  const intersection = new Set([...words1].filter(x => words2.has(x)));
  const union = new Set([...words1, ...words2]);

  return intersection.size / union.size;
}

/**
 * 摘要文本（提取关键词）
 * @param {string} text - 输入文本
 * @param {number} maxLength - 最大长度
 * @returns {string} - 摘要
 */
function summarizeText(text, maxLength = 200) {
  // 简单实现：取前 maxLength 个字符
  const cleaned = text.replace(/\s+/g, ' ').trim();
  return cleaned.length > maxLength
    ? cleaned.substring(0, maxLength) + '...'
    : cleaned;
}

// ========== 检查 1: 原创性验证 ==========

/**
 * 检查内容原创性
 * @param {string} content - 内容文本
 * @returns {Promise<OriginalityResult>}
 */
async function checkOriginality(content) {
  console.log('\n📝 原创性检查...\n');

  // 提取关键短语用于搜索
  const keyPhrases = extractKeyPhrases(content, 3);

  if (keyPhrases.length === 0) {
    return {
      originalityScore: 50,
      similarityScore: 0,
      similarContent: [],
      recommendation: 'caution'
    };
  }

  // 搜索相似内容
  const allSimilarContent = [];
  for (const phrase of keyPhrases) {
    const results = await searchSearXNG(`"${phrase}"`, {
      numResults: CONFIG.originality.resultCount,
      timeRange: 'month' // 最近一个月
    });
    allSimilarContent.push(...results);
  }

  // 去重相似内容
  const uniqueContent = removeDuplicates(allSimilarContent, 'url');

  // 计算相似度
  let maxSimilarity = 0;
  const scoredContent = [];

  for (const item of uniqueContent) {
    const titleSimilarity = calculateSimilarity(content, item.title);
    const contentSimilarity = calculateSimilarity(content, item.content);

    const weightedSimilarity =
      titleSimilarity * CONFIG.originality.scoreWeight.titleMatch +
      contentSimilarity * CONFIG.originality.scoreWeight.contentMatch;

    if (weightedSimilarity > 0.1) { // 只保留有一定相似度的结果
      scoredContent.push({
        ...item,
        similarity: weightedSimilarity
      });

      if (weightedSimilarity > maxSimilarity) {
        maxSimilarity = weightedSimilarity;
      }
    }
  }

  // 按相似度排序
  scoredContent.sort((a, b) => b.similarity - a.similarity);
  const topSimilarContent = scoredContent.slice(0, 5);

  // 计算原创性评分
  const originalityScore = Math.max(0, Math.round(100 - (maxSimilarity * 100)));
  const similarityScore = Math.round(maxSimilarity * 100);

  // 给出建议
  let recommendation;
  if (similarityScore < 30) {
    recommendation = 'proceed';
  } else if (similarityScore < 60) {
    recommendation = 'caution';
  } else {
    recommendation = 'skip';
  }

  console.log(`✓ 原创性评分: ${originalityScore}/100`);
  console.log(`✓ 相似度评分: ${similarityScore}/100`);
  console.log(`✓ 建议: ${recommendation}\n`);

  return {
    originalityScore,
    similarityScore,
    similarContent: topSimilarContent.map(item => ({
      title: item.title,
      url: item.url,
      relevance: item.similarity
    })),
    recommendation
  };
}

/**
 * 从文本中提取关键短语
 * @param {string} text - 输入文本
 * @param {number} count - 提取数量
 * @returns {string[]}
 */
function extractKeyPhrases(text, count = 3) {
  // 简单实现：提取较长的词组
  const sentences = text.split(/[.!?]/).filter(s => s.trim().length > 10);
  const phrases = [];

  for (const sentence of sentences) {
    const words = sentence.trim().split(/\s+/);
    if (words.length >= 3) {
      phrases.push(words.slice(0, Math.min(words.length, 6)).join(' '));
      if (phrases.length >= count) break;
    }
  }

  return phrases.slice(0, count);
}

// ========== 检查 2: 质量评估增强 ==========

/**
 * 增强质量评估
 * @param {string} topic - 主题或关键词
 * @returns {Promise<QualityAugmentResult>}
 */
async function qualityAugment(topic) {
  console.log('\n📊 质量评估增强...\n');

  // 搜索背景信息
  const backgroundInfo = await searchSearXNG(
    `${topic} guide tutorial best practices`,
    {
      numResults: CONFIG.quality.resultCount,
      timeRange: 'year'
    }
  );

  // 搜索最佳实践
  const bestPractices = await searchSearXNG(
    `${topic} best practices examples`,
    {
      numResults: CONFIG.quality.resultCount,
      timeRange: 'year'
    }
  );

  // 过滤低质量结果
  const filteredBackground = backgroundInfo.filter(
    r => r.content.length > 50 && r.score >= CONFIG.quality.minRelevanceScore
  );

  const filteredPractices = bestPractices.filter(
    r => r.content.length > 50 && r.score >= CONFIG.quality.minRelevanceScore
  );

  // 生成质量评估建议
  const qualityAssessment = generateQualityAssessment(
    filteredBackground,
    filteredPractices
  );

  console.log(`✓ 找到 ${filteredBackground.length} 条背景信息`);
  console.log(`✓ 找到 ${filteredPractices.length} 条最佳实践`);
  console.log(`✓ 生成 ${qualityAssessment.length} 条评估建议\n`);

  return {
    backgroundInfo: filteredBackground,
    bestPractices: filteredPractices,
    qualityAssessment
  };
}

/**
 * 生成质量评估建议
 * @param {SearchResult[]} backgroundInfo - 背景信息
 * @param {SearchResult[]} bestPractices - 最佳实践
 * @returns {string[]}
 */
function generateQualityAssessment(backgroundInfo, bestPractices) {
  const suggestions = [];

  if (backgroundInfo.length === 0) {
    suggestions.push('⚠️ 缺乏相关背景信息，建议补充内容来源');
  } else {
    suggestions.push('✓ 已找到充分的背景信息支持');
  }

  if (bestPractices.length >= 3) {
    suggestions.push('✓ 已参考多个最佳实践来源，内容质量较高');
  } else if (bestPractices.length > 0) {
    suggestions.push('ℹ️ 建议补充更多最佳实践案例');
  } else {
    suggestions.push('⚠️ 未找到相关最佳实践，建议深入调研');
  }

  // 根据内容长度给出建议
  if (backgroundInfo.some(r => r.content.length < 100)) {
    suggestions.push('ℹ️ 部分参考内容较简短，建议寻找更详细资源');
  }

  return suggestions;
}

// ========== 检查 3: 去重检查 ==========

/**
 * 检查是否重复
 * @param {string} skillNameOrDesc - 技能名称或描述
 * @returns {Promise<DuplicateResult>}
 */
async function checkDuplicate(skillNameOrDesc) {
  console.log('\n🔍 去重检查...\n');

  // 在网上搜索相似内容
  const webResults = await searchSearXNG(
    `${skillNameOrDesc} clawdbot skill`,
    {
      numResults: CONFIG.duplicate.webResultCount
    }
  );

  // 生成搜索关键词
  const keywords = extractKeywords(skillNameOrDesc, 3);

  // 搜索关键词组合
  const keywordResults = [];
  for (const keyword of keywords) {
    const results = await searchSearXNG(
      `"${keyword}" AI tool automation`,
      {
        numResults: 3
      }
    );
    keywordResults.push(...results);
  }

  // 合并所有结果
  const allResults = [...webResults, ...keywordResults];
  const uniqueResults = removeDuplicates(allResults, 'url');

  // 计算重复风险
  let maxSimilarity = 0;
  const scoredResults = [];

  for (const result of uniqueResults) {
    const titleSim = calculateSimilarity(skillNameOrDesc, result.title);
    const contentSim = calculateSimilarity(skillNameOrDesc, result.content);
    const combinedSim = (titleSim + contentSim) / 2;

    if (combinedSim > 0.1) {
      scoredResults.push({
        ...result,
        similarity: combinedSim
      });

      if (combinedSim > maxSimilarity) {
        maxSimilarity = combinedSim;
      }
    }
  }

  // 按相似度排序
  scoredResults.sort((a, b) => b.similarity - a.similarity);
  const topSimilar = scoredResults.slice(0, 5);

  // 判断是否重复
  const isDuplicate = maxSimilarity > CONFIG.duplicate.similarityThreshold;
  const duplicateRisk = Math.round(maxSimilarity * 100);

  // 生成差异化建议
  const differentiationSuggestions = generateDifferentiationSuggestions(
    skillNameOrDesc,
    topSimilar
  );

  console.log(`✓ 重复风险: ${duplicateRisk}%`);
  console.log(`✓ 建议操作: ${isDuplicate ? '避免重复' : '可以继续'}\n`);

  return {
    isDuplicate,
    duplicateRisk,
    similarSkills: topSimilar.map(r => ({
      title: r.title,
      url: r.url,
      relevance: r.similarity
    })),
    differentiationSuggestions
  };
}

/**
 * 从文本中提取关键词
 * @param {string} text - 输入文本
 * @param {number} count - 提取数量
 * @returns {string[]}
 */
function extractKeywords(text, count = 5) {
  // 简单实现：提取较长单词
  const words = text
    .toLowerCase()
    .split(/\s+/)
    .filter(w => w.length > 4 && !/^(the|and|with|from|this|that|have)$/.test(w));

  const unique = [...new Set(words)];
  return unique.slice(0, count);
}

/**
 * 生成差异化建议
 * @param {string} skillName - 技能名称
 * @param {SearchResult[]} similarItems - 相似项
 * @returns {string[]}
 */
function generateDifferentiationSuggestions(skillName, similarItems) {
  const suggestions = [];

  if (similarItems.length === 0) {
    suggestions.push('✓ 未发现相似技能，可以继续开发');
    return suggestions;
  }

  // 分析现有技能的特点
  const existingKeywords = new Set();
  for (const item of similarItems) {
    const keywords = extractKeywords(item.title, 3);
    keywords.forEach(k => existingKeywords.add(k));
  }

  // 找出独特的角度
  const skillKeywords = extractKeywords(skillName, 10);
  const uniqueKeywords = skillKeywords.filter(k => !existingKeywords.has(k));

  if (uniqueKeywords.length > 0) {
    suggestions.push(`💡 独特角度: ${uniqueKeywords.slice(0, 3).join(', ')}`);
  } else {
    suggestions.push('💡 建议: 寻找更具体的应用场景或使用案例');
  }

  suggestions.push('💡 建议: 添加更详细的步骤说明或参数配置');
  suggestions.push('💡 建议: 提供实际使用示例或输出演示');

  return suggestions;
}

// ========== 辅助函数 ==========

/**
 * 数组去重
 * @param {Array} array - 输入数组
 * @param {string} key - 去重键
 * @returns {Array}
 */
function removeDuplicates(array, key) {
  const seen = new Set();
  return array.filter(item => {
    const value = item[key];
    if (seen.has(value)) {
      return false;
    }
    seen.add(value);
    return true;
  });
}

// ========== 命令行接口 ==========

/**
 * 主函数 - 命令行入口
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const input = args[1];

  initCache();

  if (!command || !input) {
    printUsage();
    process.exit(1);
  }

  // 解析选项
  const options = parseOptions(args.slice(2));

  let result;
  const timestamp = new Date().toISOString();

  try {
    switch (command) {
      case 'check-originality':
        result = await checkOriginality(input);
        outputResult({
          stage: 'check-originality',
          timestamp,
          input,
          results: result
        }, options.output);
        break;

      case 'quality-augment':
        result = await qualityAugment(input);
        outputResult({
          stage: 'quality-augment',
          timestamp,
          input,
          results: result
        }, options.output);
        break;

      case 'check-duplicate':
        result = await checkDuplicate(input);
        outputResult({
          stage: 'check-duplicate',
          timestamp,
          input,
          results: result
        }, options.output);
        break;

      case 'full-pipeline':
        result = await runFullPipeline(input);
        outputResult({
          stage: 'full-pipeline',
          timestamp,
          input,
          results: result
        }, options.output);
        break;

      default:
        console.error(`未知命令: ${command}`);
        printUsage();
        process.exit(1);
    }
  } catch (error) {
    console.error('错误:', error.message);
    process.exit(1);
  }
}

/**
 * 运行完整管道
 * @param {string} input - 输入内容
 * @returns {Promise<Object>}
 */
async function runFullPipeline(input) {
  console.log('🚀 运行完整检查管道...\n');

  // 并行执行所有检查
  const [originality, quality, duplicate] = await Promise.all([
    checkOriginality(input),
    qualityAugment(extractKeywords(input, 2).join(' ')),
    checkDuplicate(input)
  ]);

  // 综合评估
  const overallScore = calculateOverallScore({
    originality,
    quality,
    duplicate
  });

  console.log('\n📊 综合评估:');
  console.log(`   原创性: ${originality.originalityScore}/100`);
  console.log(`   资源质量: ${Math.min(100, quality.backgroundInfo.length * 10 + quality.bestPractices.length * 5)}/100`);
  console.log(`   独特性: ${100 - duplicate.duplicateRisk}/100`);
  console.log(`   综合得分: ${overallScore}/100`);
  console.log(`   最终建议: ${overallScore >= 70 ? '✓ 推荐发布' : overallScore >= 50 ? '⚠️ 需要改进' : '✗ 不建议发布'}\n`);

  return {
    originality,
    quality,
    duplicate,
    overallScore,
    recommendation: overallScore >= 70 ? 'proceed' : overallScore >= 50 ? 'review' : 'reject'
  };
}

/**
 * 计算综合评分
 * @param {Object} results - 各项检查结果
 * @returns {number}
 */
function calculateOverallScore({ originality, quality, duplicate }) {
  const weights = {
    originality: 0.4,
    quality: 0.3,
    uniqueness: 0.3
  };

  const qualityScore = Math.min(
    100,
    quality.backgroundInfo.length * 10 + quality.bestPractices.length * 5
  );

  const uniquenessScore = 100 - duplicate.duplicateRisk;

  return Math.round(
    originality.originalityScore * weights.originality +
    qualityScore * weights.quality +
    uniquenessScore * weights.uniqueness
  );
}

/**
 * 解析命令行选项
 * @param {string[]} args - 选项数组
 * @returns {Object}
 */
function parseOptions(args) {
  const options = {
    output: 'json'
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--output' || arg === '-o') {
      options.output = args[++i];
    } else if (arg === '--help' || arg === '-h') {
      printUsage();
      process.exit(0);
    }
  }

  return options;
}

/**
 * 输出结果
 * @param {Object} data - 结果数据
 * @param {string} format - 输出格式 (json|pretty)
 */
function outputResult(data, format = 'json') {
  if (format === 'pretty') {
    console.log('\n' + JSON.stringify(data, null, 2));
  } else {
    console.log(JSON.stringify(data));
  }
}

/**
 * 打印使用说明
 */
function printUsage() {
  console.log(`
SearXNG 集成管道 - AI 提示词质量检查工具

用法:
  node searxng-integrated-pipeline.js <command> <input> [options]

命令:
  check-originality <text>     验证内容原创性
  quality-augment <topic>     质量评估增强
  check-duplicate <skill>      检查技能重复
  full-pipeline <content>      运行完整检查管道

选项:
  --output, -o <format>      输出格式: json (默认) 或 pretty
  --help, -h                 显示此帮助信息

示例:
  # 检查原创性
  node searxng-integrated-pipeline.js check-originality "AI prompt for image generation"

  # 质量评估
  node searxng-integrated-pipeline.js quality-augment "prompt engineering"

  # 检查重复
  node searxng-integrated-pipeline.js check-duplicate "Image Generator Skill"

  # 完整检查
  node searxng-integrated-pipeline.js full-pipeline "Create stunning AI images with text prompts"

输出格式 (JSON):
  {
    "stage": "check-originality",
    "timestamp": "2026-01-30T14:48:44Z",
    "input": "...",
    "results": {
      "originalityScore": 85,
      "similarContent": [...],
      "recommendation": "proceed"
    }
  }
`);
}

// ========== 模块导出 ==========

/**
 * 作为模块使用时导出的 API
 */
if (require.main === module) {
  main();
} else {
  module.exports = {
    checkOriginality,
    qualityAugment,
    checkDuplicate,
    runFullPipeline,
    searchSearXNG,
    initCache,
    calculateSimilarity
  };
}
