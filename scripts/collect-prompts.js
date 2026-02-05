#!/usr/bin/env node

/**
 * AI Prompts Collector Script
 *
 * This script collects AI prompt-related information by searching
 * for various keywords and saving the results to a JSONL file.
 *
 * Usage: node collect-prompts.js
 *
 * Environment variables:
 *   BRAVE_API_KEY - Your Brave Search API key (required)
 *   OUTPUT_FILE   - Output file path (default: ../data/prompts/collected.jsonl)
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Configuration
const BRAVE_API_KEY = process.env.BRAVE_API_KEY;
const OUTPUT_FILE = process.env.OUTPUT_FILE || path.join(__dirname, '../data/prompts/collected.jsonl');

// Search queries
const SEARCH_QUERIES = [
  'AI prompt engineering tips',
  'ChatGPT prompts',
  'Claude prompts',
  'best AI prompts 2026',
  'prompt templates'
];

const RESULTS_PER_QUERY = 5;

/**
 * Make a request to Brave Search API
 */
function braveSearch(query, count = 5) {
  return new Promise((resolve, reject) => {
    const params = new URLSearchParams({
      q: query,
      count: count.toString()
    });

    const options = {
      hostname: 'api.search.brave.com',
      path: `/res/v1/web/search?${params.toString()}`,
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': BRAVE_API_KEY
      }
    };

    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json);
        } catch (error) {
          reject(new Error(`Failed to parse API response: ${error.message}`));
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.end();
  });
}

/**
 * Format search results
 */
function formatSearchResults(query, apiResponse) {
  const results = [];

  if (apiResponse.web && apiResponse.web.results) {
    for (const result of apiResponse.web.results) {
      results.push({
        title: result.title || '',
        url: result.url || '',
        snippet: result.description || result.snippet || '',
        published: result.published_date || null
      });
    }
  }

  return {
    type: 'search',
    timestamp: new Date().toISOString(),
    query: query,
    result_count: results.length,
    results: results
  };
}

/**
 * Append a JSONL entry to file
 */
function appendJsonl(filePath, data) {
  const line = JSON.stringify(data) + '\n';
  fs.appendFileSync(filePath, line, 'utf8');
}

/**
 * Main function
 */
async function main() {
  console.log('🔍 AI Prompts Collector');
  console.log('========================\n');

  // Check API key
  if (!BRAVE_API_KEY) {
    console.error('❌ Error: BRAVE_API_KEY environment variable is required');
    console.error('   Run: export BRAVE_API_KEY=your_key_here');
    console.error('   Or add to ~/.bashrc or ~/.zshrc');
    process.exit(1);
  }

  // Ensure output directory exists
  const outputDir = path.dirname(OUTPUT_FILE);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
    console.log(`📁 Created directory: ${outputDir}`);
  }

  console.log(`📝 Output file: ${OUTPUT_FILE}\n`);
  console.log(`🔑 API Key: ${BRAVE_API_KEY.substring(0, 8)}...\n`);

  let totalResults = 0;
  let successCount = 0;
  let errorCount = 0;

  for (const query of SEARCH_QUERIES) {
    console.log(`🔎 Searching: "${query}"`);

    try {
      const response = await braveSearch(query, RESULTS_PER_QUERY);
      const formatted = formatSearchResults(query, response);

      // Append to JSONL file
      appendJsonl(OUTPUT_FILE, formatted);

      console.log(`   ✓ Found ${formatted.result_count} results`);
      totalResults += formatted.result_count;
      successCount++;
    } catch (error) {
      console.error(`   ✗ Error: ${error.message}`);
      errorCount++;

      // Save error entry
      const errorEntry = {
        type: 'error',
        timestamp: new Date().toISOString(),
        query: query,
        error: error.message
      };
      appendJsonl(OUTPUT_FILE, errorEntry);
    }

    // Small delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.log('\n' + '='.repeat(40));
  console.log('✅ Collection Complete!');
  console.log(`   Successful queries: ${successCount}/${SEARCH_QUERIES.length}`);
  console.log(`   Failed queries: ${errorCount}/${SEARCH_QUERIES.length}`);
  console.log(`   Total results: ${totalResults}`);
  console.log(`   Output: ${OUTPUT_FILE}`);
}

// Run
if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = { braveSearch, formatSearchResults, appendJsonl };
