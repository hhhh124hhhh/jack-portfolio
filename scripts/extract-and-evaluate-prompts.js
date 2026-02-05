#!/usr/bin/env node

/**
 * 提示词收集和评估脚本
 * 从搜索结果中提取高质量提示词，使用 searxng-integrated-pipeline.js 进行质量评估
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const SEARCH_RESULTS_DIR = '/root/clawd/data/search-results';
const PROMPTS_COLLECTION_DIR = '/root/clawd/data/prompts-collection';
const PIPELINE_SCRIPT = '/root/clawd/scripts/searxng-integrated-pipeline.js';

/**
 * 语义验证函数 - 检查文本是否看起来像有效的 AI 提示词
 * @param {string} text - 要验证的文本
 * @returns {boolean}
 */
function isLikelyPrompt(text) {
  // 长度检查：至少 50 个字符
  if (text.length < 50) {
    return false;
  }

  // 关键词验证：必须包含 AI 提示词相关关键词
  const promptKeywords = [
    'act', 'generate', 'write', 'create', 'role', 'task',
    'provide', 'analyze', 'explain', 'review', 'assess',
    'transform', 'convert', 'optimize', 'improve', 'design',
    'develop', 'implement', 'evaluate', 'summarize', 'translate'
  ];

  const lowerText = text.toLowerCase();
  const hasKeyword = promptKeywords.some(kw => lowerText.includes(kw));

  if (!hasKeyword) {
    return false;
  }

  // 格式验证：不应该只是简单的标题或描述
  // 检查是否包含句子结构（有完整的思想，不只是关键词）
  const hasStructure = /[.!?]/.test(text) || /\n/.test(text);

  return hasStructure;
}

/**
 * 提取提示词模板（修复版本）
 * 只匹配提示词专用格式，添加语义验证
 * @param {string} content - 内容文本
 * @returns {string[]}
 */
function extractPromptTemplates(content) {
  const prompts = [];

  // 匹配角色扮演提示词: "You are a ..." / "Act as a ..." / "Imagine you are..."
  const rolePatterns = [
    /You are (?:a|an|the) [^.!?]+(?: [^.!?]+){1,}[.!?]/gi,
    /Act as (?:a|an|the) [^.!?]+(?: [^.!?]+){1,}[.!?]/gi,
    /Imagine you are (?:a|an|the) [^.!?]+(?: [^.!?]+){1,}[.!?]/gi
  ];

  for (const pattern of rolePatterns) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      const prompt = match[0].trim();
      if (isLikelyPrompt(prompt) && !prompts.includes(prompt)) {
        prompts.push(prompt);
      }
    }
  }

  // 匹配请求生成提示词: "Please generate..." / "Please write..." / "Please create..."
  // 注意：顺序很重要 - 先匹配带 "Please" 的模式，再匹配不带 "Please" 的
  const generatePatterns = [
    /Please generate [^.!?]+(?: [^.!?]+){1,}[.!?]/gi,
    /Please write [^.!?]+(?: [^.!?]+){1,}[.!?]/gi,
    /Please create [^.!?]+(?: [^.!?]+){1,}[.!?]/gi
    // 移除了不带 "Please" 的模式，避免重复提取
  ];

  for (const pattern of generatePatterns) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      const prompt = match[0].trim();
      if (isLikelyPrompt(prompt) && !prompts.includes(prompt)) {
        prompts.push(prompt);
      }
    }
  }

  // 匹配明确标注的提示词: "Prompt: ..." / "System prompt: ..."
  const labeledPatterns = [
    /Prompt[:\s]+[\s\S]{50,500}/gi,
    /System prompt[:\s]+[\s\S]{50,500}/gi,
    /AI prompt[:\s]+[\s\S]{50,500}/gi
  ];

  for (const pattern of labeledPatterns) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      const prompt = match[0].trim();
      // 标签后的内容
      const promptContent = prompt.replace(/^(Prompt|System prompt|AI prompt)[:\s]+/i, '');
      if (isLikelyPrompt(promptContent) && !prompts.includes(promptContent)) {
        prompts.push(promptContent);
      }
    }
  }

  return prompts;
}

/**
 * 分析搜索结果并提取提示词
 * @param {Object} searchResult - 搜索结果对象
 * @returns {Object}
 */
function analyzeSearchResult(searchResult) {
  const { title, url, content, query } = searchResult;

  // 提取提示词
  const prompts = extractPromptTemplates(content + ' ' + title);

  // 计算质量分数
  let qualityScore = 50;

  // 内容长度加权
  if (content.length > 200) qualityScore += 10;
  if (content.length > 500) qualityScore += 10;

  // 关键词检查
  const qualityKeywords = [
    'best', 'practice', 'guide', 'template', 'example',
    'prompt', 'effective', 'writing', 'technique'
  ];

  const hasQualityKeyword = qualityKeywords.some(kw =>
    title.toLowerCase().includes(kw) || content.toLowerCase().includes(kw)
  );

  if (hasQualityKeyword) qualityScore += 15;

  // 包含提示词
  if (prompts.length > 0) qualityScore += 15;

  qualityScore = Math.min(100, qualityScore);

  return {
    title,
    url,
    query,
    content: content.substring(0, 500),
    prompts: prompts.slice(0, 5), // 最多保留 5 个提示词
    qualityScore,
    extractedAt: new Date().toISOString()
  };
}

/**
 * 从所有搜索结果中提取提示词
 * @returns {Array}
 */
function extractFromAllResults() {
  console.log('📝 从搜索结果中提取提示词...\n');

  const allAnalyses = [];

  const files = fs.readdirSync(SEARCH_RESULTS_DIR).filter(f =>
    f.endsWith('.json') && f !== 'search-summary.json'
  );

  for (const file of files) {
    console.log(`处理: ${file}`);

    try {
      const data = JSON.parse(
        fs.readFileSync(path.join(SEARCH_RESULTS_DIR, file), 'utf8')
      );

      const analyses = (data.results || []).map(r => analyzeSearchResult(r));
      allAnalyses.push(...analyses);

      console.log(`  ✓ 提取了 ${analyses.length} 条分析\n`);
    } catch (error) {
      console.error(`  ✗ 错误: ${error.message}\n`);
    }
  }

  return allAnalyses;
}

/**
 * 过滤高质量提示词
 * @param {Array} analyses - 所有分析结果
 * @returns {Array}
 */
function filterHighQuality(analyses) {
  console.log('\n🔍 过滤高质量提示词...\n');

  // 按质量分数排序
  const sorted = analyses.sort((a, b) => b.qualityScore - a.qualityScore);

  // 过滤高质量项 (分数 >= 60)
  const highQuality = sorted.filter(a => a.qualityScore >= 60);

  console.log(`  总项数: ${sorted.length}`);
  console.log(`  高质量项 (>=60): ${highQuality.length}`);

  return highQuality;
}

/**
 * 使用 searxng-integrated-pipeline.js 进行质量评估
 * @param {Array} items - 高质量项
 * @returns {Promise<Array>}
 */
async function evaluateWithPipeline(items) {
  console.log('\n📊 使用 pipeline 进行质量评估...\n');

  const evaluated = [];

  for (let i = 0; i < Math.min(items.length, 20); i++) {
    const item = items[i];
    console.log(`[${i + 1}/${Math.min(items.length, 20)}] 评估: ${item.title.substring(0, 40)}...`);

    try {
      // 创建评估内容 (结合 title 和 content)
      const evalContent = `${item.title}\n\n${item.content}`;

      // 运行原创性检查
      const originalityResult = await runPipelineCommand(
        'check-originality',
        evalContent.substring(0, 1000)
      );

      // 运行质量增强
      const keywords = item.query.split(' ').slice(0, 2).join(' ');
      const qualityResult = await runPipelineCommand(
        'quality-augment',
        keywords
      );

      // 运行去重检查
      const duplicateResult = await runPipelineCommand(
        'check-duplicate',
        item.title
      );

      // 合并评估结果
      const evaluatedItem = {
        ...item,
        originalityCheck: originalityResult,
        qualityAugment: qualityResult,
        duplicateCheck: duplicateResult
      };

      // 计算综合评分
      evaluatedItem.overallScore = calculateOverallScore(evaluatedItem);

      evaluated.push(evaluatedItem);

      console.log(`  ✓ 原创性: ${originalityResult.results?.originalityScore || 'N/A'}`);
      console.log(`  ✓ 综合评分: ${evaluatedItem.overallScore}\n`);

    } catch (error) {
      console.error(`  ✗ 评估失败: ${error.message}\n`);
    }
  }

  return evaluated;
}

/**
 * 运行 pipeline 命令
 * @param {string} command - 命令
 * @param {string} input - 输入内容
 * @returns {Promise<Object>}
 */
function runPipelineCommand(command, input) {
  return new Promise((resolve, reject) => {
    // 使用临时文件传递输入内容
    const tempFile = path.join('/tmp', `pipeline-input-${Date.now()}.txt`);
    fs.writeFileSync(tempFile, input, 'utf8');

    const cmd = `node ${PIPELINE_SCRIPT} ${command} "$(cat ${tempFile})" --output json`;

    exec(cmd, { timeout: 60000, maxBuffer: 10 * 1024 * 1024, shell: '/bin/bash' }, (error, stdout, stderr) => {
      // 清理临时文件
      try { fs.unlinkSync(tempFile); } catch(e) {}

      if (error) {
        reject(new Error(stderr || error.message));
        return;
      }

      try {
        // 只取最后一行（JSON 输出）
        const lines = stdout.trim().split('\n');
        const lastLine = lines[lines.length - 1];
        const result = JSON.parse(lastLine);
        resolve(result);
      } catch (parseError) {
        reject(new Error(`解析失败: ${parseError.message}`));
      }
    });
  });
}

/**
 * 计算综合评分
 * @param {Object} item - 评估项
 * @returns {number}
 */
function calculateOverallScore(item) {
  const originalityScore = item.originalityCheck?.results?.originalityScore || 50;
  const qualityScore = item.qualityScore || 50;
  const duplicateRisk = item.duplicateCheck?.results?.duplicateRisk || 0;

  const uniquenessScore = 100 - duplicateRisk;

  // 权重: 原创性 40%, 质量 40%, 独特性 20%
  const overall =
    originalityScore * 0.4 +
    qualityScore * 0.4 +
    uniquenessScore * 0.2;

  return Math.round(overall);
}

/**
 * 保存评估结果
 * @param {Array} evaluated - 评估结果
 */
function saveEvaluatedPrompts(evaluated) {
  console.log('\n💾 保存评估结果...\n');

  const timestamp = new Date().toISOString().split('T')[0];
  const outputFile = path.join(PROMPTS_COLLECTION_DIR, `evaluated-prompts-${timestamp}.jsonl`);

  // 按 overallScore 排序
  const sorted = evaluated.sort((a, b) => b.overallScore - a.overallScore);

  // 写入 JSONL 格式
  const lines = sorted.map(item => JSON.stringify(item)).join('\n');
  fs.writeFileSync(outputFile, lines, 'utf8');

  console.log(`✓ 保存了 ${sorted.length} 条评估结果`);
  console.log(`✓ 文件: ${outputFile}`);

  // 生成摘要报告
  const summary = {
    timestamp: new Date().toISOString(),
    totalEvaluated: sorted.length,
    highQualityCount: sorted.filter(i => i.overallScore >= 70).length,
    mediumQualityCount: sorted.filter(i => i.overallScore >= 50 && i.overallScore < 70).length,
    lowQualityCount: sorted.filter(i => i.overallScore < 50).length,
    topPrompts: sorted.slice(0, 10).map(i => ({
      title: i.title,
      url: i.url,
      overallScore: i.overallScore
    }))
  };

  const summaryFile = path.join(PROMPTS_COLLECTION_DIR, `evaluation-summary-${timestamp}.json`);
  fs.writeFileSync(summaryFile, JSON.stringify(summary, null, 2), 'utf8');

  console.log(`✓ 摘要: ${summaryFile}`);

  return { outputFile, summaryFile, summary };
}

/**
 * 主函数
 */
async function main() {
  console.log('='.repeat(80));
  console.log('🔄 AI 提示词收集和评估流程');
  console.log('='.repeat(80));
  console.log();

  // 确保输出目录存在
  if (!fs.existsSync(PROMPTS_COLLECTION_DIR)) {
    fs.mkdirSync(PROMPTS_COLLECTION_DIR, { recursive: true });
  }

  // 1. 提取提示词
  const allAnalyses = extractFromAllResults();

  // 2. 过滤高质量
  const highQuality = filterHighQuality(allAnalyses);

  // 3. 使用 pipeline 评估
  const evaluated = await evaluateWithPipeline(highQuality);

  // 4. 保存结果
  const { outputFile, summaryFile, summary } = saveEvaluatedPrompts(evaluated);

  console.log('\n' + '='.repeat(80));
  console.log('✅ 评估完成！');
  console.log('='.repeat(80));
  console.log();
  console.log(`📊 统计:`);
  console.log(`  总评估项: ${summary.totalEvaluated}`);
  console.log(`  高质量 (>=70): ${summary.highQualityCount}`);
  console.log(`  中等质量 (50-69): ${summary.mediumQualityCount}`);
  console.log(`  低质量 (<50): ${summary.lowQualityCount}`);
  console.log();
  console.log(`📁 输出文件:`);
  console.log(`  评估结果: ${outputFile}`);
  console.log(`  摘要报告: ${summaryFile}`);
  console.log();
}

main().catch(console.error);
