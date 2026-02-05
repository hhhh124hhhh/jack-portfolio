#!/usr/bin/env node

/**
 * 简化版提示词提取脚本
 * 直接从搜索结果中提取提示词，准备转换为 Skills
 */

const fs = require('fs');
const path = require('path');

const SEARCH_RESULTS_DIR = '/root/clawd/data/search-results';
const PROMPTS_OUTPUT_DIR = '/root/clawd/data/prompts-collection';

/**
 * 提取提示词
 * @param {string} content - 内容文本
 * @returns {string[]}
 */
function extractPromptTemplates(content) {
  const prompts = [];

  // 匹配引号中的提示词
  const quotePattern = /['"`]([^'"`]{30,300})['"`]/g;
  let match;
  while ((match = quotePattern.exec(content)) !== null) {
    const prompt = match[1].trim();
    // 过滤掉过于简短或非提示词的内容
    if (prompt.length > 30 &&
        !prompt.includes('http') &&
        !prompt.includes('www') &&
        /[a-zA-Z]/.test(prompt) &&
        !prompts.includes(prompt)) {
      prompts.push(prompt);
    }
  }

  // 匹配角色扮演提示词
  const rolePatterns = [
    /Act as (a|an) ([^.!?]{20,150})/gi,
    /You are (a|an) ([^.!?]{20,150})/gi,
    /Imagine you are (a|an) ([^.!?]{20,150})/gi,
    /扮演 ([^。！？]{20,150})/g,
    /你是一个 ([^。！？]{20,150})/g
  ];

  for (const pattern of rolePatterns) {
    while ((match = pattern.exec(content)) !== null) {
      const prompt = match[0].trim();
      if (prompt.length > 20 && prompt.length < 200 && !prompts.includes(prompt)) {
        prompts.push(prompt);
      }
    }
  }

  // 匹配命令式提示词
  const commandPatterns = [
    /Write (a|an) ([^.!?]{20,150})/gi,
    /Generate (a|an) ([^.!?]{20,150})/gi,
    /Create (a|an) ([^.!?]{20,150})/gi,
    /请写 (a|an)? ([^。！？]{20,150})/g,
    /生成 ([^。！？]{20,150})/g,
    /创建 ([^。！？]{20,150})/g
  ];

  for (const pattern of commandPatterns) {
    while ((match = pattern.exec(content)) !== null) {
      const prompt = match[0].trim();
      if (prompt.length > 20 && prompt.length < 200 && !prompts.includes(prompt)) {
        prompts.push(prompt);
      }
    }
  }

  // 去重
  const uniquePrompts = [...new Set(prompts)];

  // 按长度排序，优先选择中等长度的提示词
  return uniquePrompts.sort((a, b) => {
    const idealLength = 80;
    const diffA = Math.abs(a.length - idealLength);
    const diffB = Math.abs(b.length - idealLength);
    return diffA - diffB;
  }).slice(0, 10); // 每个结果最多提取 10 个提示词
}

/**
 * 分析搜索结果
 * @param {Object} searchResult - 搜索结果对象
 * @param {string} query - 查询字符串
 * @returns {Object}
 */
function analyzeSearchResult(searchResult, query) {
  const { title, url, content, score } = searchResult;

  // 提取提示词
  const prompts = extractPromptTemplates(content + ' ' + title);

  // 计算质量分数
  let qualityScore = 40;

  // 内容长度加权
  if (content.length > 200) qualityScore += 5;
  if (content.length > 500) qualityScore += 5;

  // 相关性评分
  if (score > 0.8) qualityScore += 10;
  else if (score > 0.5) qualityScore += 5;

  // 关键词检查
  const qualityKeywords = [
    'prompt', 'template', 'example', 'guide', 'best',
    'effective', 'writing', 'technique', 'pattern', 'structure'
  ];

  const keywordCount = qualityKeywords.filter(kw =>
    (title + content).toLowerCase().includes(kw)
  ).length;

  qualityScore += Math.min(keywordCount * 3, 20);

  // 包含提示词
  if (prompts.length > 0) qualityScore += 15;

  qualityScore = Math.min(100, qualityScore);

  return {
    title: title ? title.substring(0, 100) : 'Untitled',
    url,
    content: content ? content.substring(0, 300) : '',
    prompts: prompts.slice(0, 5),
    qualityScore,
    extractedAt: new Date().toISOString()
  };
}

/**
 * 分类提示词
 * @param {Object} item - 分析项
 * @param {string} query - 查询字符串
 * @returns {string}
 */
function categorizePrompt(item, query) {
  const { title } = item;
  const lowerQuery = (query || '').toLowerCase();

  if (lowerQuery.includes('image') || lowerQuery.includes('midjourney') ||
      lowerQuery.includes('stable diffusion') || lowerQuery.includes('dall-e')) {
    return 'image-generation';
  }

  if (lowerQuery.includes('writing') || lowerQuery.includes('content')) {
    return 'writing';
  }

  if (lowerQuery.includes('chatgpt') || lowerQuery.includes('llm')) {
    return 'chatgpt';
  }

  if (lowerQuery.includes('engineering') || lowerQuery.includes('best practice')) {
    return 'engineering';
  }

  return 'general';
}

/**
 * 主函数
 */
function main() {
  console.log('='.repeat(80));
  console.log('🔄 AI 提示词提取（简化版）');
  console.log('='.repeat(80));
  console.log();

  // 确保输出目录存在
  if (!fs.existsSync(PROMPTS_OUTPUT_DIR)) {
    fs.mkdirSync(PROMPTS_OUTPUT_DIR, { recursive: true });
  }

  const allPrompts = {
    'image-generation': [],
    'writing': [],
    'chatgpt': [],
    'engineering': [],
    'general': []
  };

  const files = fs.readdirSync(SEARCH_RESULTS_DIR).filter(f =>
    f.endsWith('.json') && f !== 'search-summary.json'
  );

  let totalResults = 0;
  let totalPrompts = 0;

  for (const file of files) {
    console.log(`处理: ${file}`);

    try {
      const data = JSON.parse(
        fs.readFileSync(path.join(SEARCH_RESULTS_DIR, file), 'utf8')
      );

      const results = data.results || [];
      const query = data.query || '';
      totalResults += results.length;

      for (const result of results) {
        const analysis = analyzeSearchResult(result, query);

        // 只保留质量分数 >= 50 的项
        if (analysis.qualityScore >= 50 && analysis.prompts.length > 0) {
          const category = categorizePrompt(analysis, query);
          allPrompts[category].push(analysis);
          totalPrompts += analysis.prompts.length;
        }
      }

      console.log(`  ✓ 处理了 ${results.length} 条结果\n`);

    } catch (error) {
      console.error(`  ✗ 错误: ${error.message}\n`);
    }
  }

  // 按质量分数排序
  for (const category in allPrompts) {
    allPrompts[category].sort((a, b) => b.qualityScore - a.qualityScore);
    allPrompts[category] = allPrompts[category].slice(0, 50); // 每个类别最多 50 条
  }

  // 保存为 JSONL 格式
  const timestamp = new Date().toISOString().split('T')[0];

  for (const category in allPrompts) {
    const outputFile = path.join(PROMPTS_OUTPUT_DIR, `${category}-prompts-${timestamp}.jsonl`);

    if (allPrompts[category].length > 0) {
      const lines = allPrompts[category].map(item => JSON.stringify(item)).join('\n');
      fs.writeFileSync(outputFile, lines, 'utf8');
      console.log(`✓ ${category}: ${allPrompts[category].length} 条 -> ${outputFile}`);
    }
  }

  // 保存合并的提示词（适合转换工具使用的格式）
  const mergedPrompts = [];

  for (const category in allPrompts) {
    for (const item of allPrompts[category]) {
      for (const prompt of item.prompts) {
        mergedPrompts.push({
          content: prompt,
          title: item.title,
          source: category,
          url: item.url,
          quality_score: item.qualityScore,
          extracted_at: item.extractedAt
        });
      }
    }
  }

  // 按质量分数排序
  mergedPrompts.sort((a, b) => b.quality_score - a.quality_score);

  // 保存为 JSONL（匹配 convert-prompts-to-skills.py 的输入格式）
  const mergedFile = path.join(PROMPTS_OUTPUT_DIR, `all-prompts-${timestamp}.jsonl`);
  const mergedLines = mergedPrompts.map(p => JSON.stringify(p)).join('\n');
  fs.writeFileSync(mergedFile, mergedLines, 'utf8');

  // 生成摘要
  const summary = {
    timestamp: new Date().toISOString(),
    totalResults,
    totalPrompts,
    categories: {
      'image-generation': allPrompts['image-generation'].length,
      'writing': allPrompts['writing'].length,
      'chatgpt': allPrompts['chatgpt'].length,
      'engineering': allPrompts['engineering'].length,
      'general': allPrompts['general'].length
    },
    mergedPrompts: mergedPrompts.length,
    outputFile: mergedFile,
    outputDir: PROMPTS_OUTPUT_DIR
  };

  const summaryFile = path.join(PROMPTS_OUTPUT_DIR, `extraction-summary-${timestamp}.json`);
  fs.writeFileSync(summaryFile, JSON.stringify(summary, null, 2), 'utf8');

  console.log();
  console.log('='.repeat(80));
  console.log('✅ 提取完成！');
  console.log('='.repeat(80));
  console.log();
  console.log(`📊 统计:`);
  console.log(`  处理结果: ${totalResults} 条`);
  console.log(`  提取提示词: ${totalPrompts} 个`);
  console.log();
  console.log(`📁 分类:`);
  console.log(`  图像生成: ${summary.categories['image-generation']} 条`);
  console.log(`  写作: ${summary.categories['writing']} 条`);
  console.log(`  ChatGPT: ${summary.categories['chatgpt']} 条`);
  console.log(`  提示工程: ${summary.categories['engineering']} 条`);
  console.log(`  通用: ${summary.categories['general']} 条`);
  console.log();
  console.log(`📦 合并提示词: ${summary.mergedPrompts} 个`);
  console.log(`📁 输出目录: ${PROMPTS_OUTPUT_DIR}`);
  console.log();
}

main();
