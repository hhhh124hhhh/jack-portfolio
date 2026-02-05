#!/usr/bin/env node

/**
 * AI 提示词批量搜索脚本
 * 搜索多个主题的提示词资源，并保存为 JSON 格式
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const SEARCH_QUERIES = [
  'prompt engineering best practices',
  'AI prompt templates examples',
  'ChatGPT prompt guide',
  'effective prompt writing techniques',
  'AI image generation prompts',
  'midjourney prompts examples',
  'stable diffusion prompt guide',
  'DALL-E 3 prompt tips',
  'LLM prompt templates',
  'AI writing prompts'
];

const OUTPUT_DIR = '/root/clawd/data/search-results';
const SEARXNG_URL = 'http://localhost:8080';

/**
 * 执行 SearXNG 搜索
 * @param {string} query - 搜索查询
 * @returns {Promise<Object>}
 */
async function searchSearXNG(query) {
  const params = new URLSearchParams({
    q: query,
    format: 'json',
    language: 'auto',
    categories: 'general'
  });

  const url = `${SEARXNG_URL}/search?${params.toString()}`;

  return new Promise((resolve, reject) => {
    exec(`curl -s -k "${url}"`, { timeout: 30000, maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
      if (error) {
        reject(new Error(`搜索失败: ${stderr || error.message}`));
        return;
      }

      try {
        const parsed = JSON.parse(stdout);
        resolve({
          query,
          results: parsed.results || [],
          totalResults: parsed.results?.length || 0
        });
      } catch (parseError) {
        reject(new Error(`解析失败: ${parseError.message}`));
      }
    });
  });
}

/**
 * 保存搜索结果
 * @param {Object} data - 搜索数据
 */
function saveResults(data) {
  const sanitizedQuery = data.query
    .replace(/[^a-zA-Z0-9]/g, '_')
    .substring(0, 50);

  const filename = `${sanitizedQuery}.json`;
  const filepath = path.join(OUTPUT_DIR, filename);

  fs.writeFileSync(filepath, JSON.stringify(data, null, 2), 'utf8');
  console.log(`  ✓ 保存: ${filename}`);
}

/**
 * 主函数
 */
async function main() {
  console.log('🔍 开始批量搜索 AI 提示词...\n');

  // 确保输出目录存在
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const allResults = [];
  let successCount = 0;
  let failCount = 0;

  for (const query of SEARCH_QUERIES) {
    console.log(`\n[${successCount + failCount + 1}/${SEARCH_QUERIES.length}] 搜索: "${query}"`);

    try {
      const result = await searchSearXNG(query);
      saveResults(result);

      allResults.push(result);

      console.log(`  ✓ 找到 ${result.totalResults} 个结果`);
      successCount++;
    } catch (error) {
      console.error(`  ✗ 错误: ${error.message}`);
      failCount++;
    }

    // 避免请求过快
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // 生成摘要报告
  console.log('\n\n📊 搜索完成！');
  console.log(`  成功: ${successCount}/${SEARCH_QUERIES.length}`);
  console.log(`  失败: ${failCount}/${SEARCH_QUERIES.length}`);

  // 保存汇总报告
  const summary = {
    timestamp: new Date().toISOString(),
    totalQueries: SEARCH_QUERIES.length,
    successCount,
    failCount,
    queries: SEARCH_QUERIES,
    totalResultsFound: allResults.reduce((sum, r) => sum + r.totalResults, 0)
  };

  const summaryPath = path.join(OUTPUT_DIR, 'search-summary.json');
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2), 'utf8');
  console.log(`  ✓ 汇总报告: ${summaryPath}`);

  console.log('\n✅ 所有结果已保存到:', OUTPUT_DIR);
}

main().catch(console.error);
