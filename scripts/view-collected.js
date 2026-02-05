#!/usr/bin/env node

/**
 * View Collected AI Prompts Data
 *
 * Usage:
 *   node view-collected.js                    # Show summary
 *   node view-collected.js --query "tips"     # Filter by query
 *   node view-collected.js --type error       # Show errors only
 *   node view-collected.js --json             # Raw JSON output
 */

const fs = require('fs');
const path = require('path');

const OUTPUT_FILE = path.join(__dirname, '../data/prompts/collected.jsonl');

/**
 * Read and parse JSONL file
 */
function readJsonl(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`❌ File not found: ${filePath}`);
    return [];
  }

  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.trim().split('\n').filter(line => line.trim());

  return lines.map(line => {
    try {
      return JSON.parse(line);
    } catch (error) {
      return { type: 'parse_error', raw: line, error: error.message };
    }
  });
}

/**
 * Display summary
 */
function displaySummary(entries) {
  if (entries.length === 0) {
    console.log('📭 No data found. Run the collector first.\n');
    return;
  }

  const searches = entries.filter(e => e.type === 'search');
  const errors = entries.filter(e => e.type === 'error');
  const totalResults = searches.reduce((sum, e) => sum + (e.result_count || 0), 0);

  console.log('📊 Collection Summary');
  console.log('=====================\n');
  console.log(`Total entries: ${entries.length}`);
  console.log(`Search queries: ${searches.length}`);
  console.log(`Errors: ${errors.length}`);
  console.log(`Total results: ${totalResults}`);
  console.log('');

  if (searches.length > 0) {
    console.log('📋 Recent Searches:');
    searches.slice(-5).forEach(entry => {
      console.log(`  • "${entry.query}" (${entry.result_count} results) - ${entry.timestamp}`);
    });
    console.log('');
  }

  if (errors.length > 0) {
    console.log('❌ Recent Errors:');
    errors.slice(-3).forEach(entry => {
      console.log(`  • "${entry.query}": ${entry.error}`);
    });
    console.log('');
  }
}

/**
 * Display filtered results
 */
function displayFiltered(entries, filter) {
  const filtered = entries.filter(entry => {
    if (filter.type && entry.type !== filter.type) return false;
    if (filter.query && entry.query && !entry.query.toLowerCase().includes(filter.query.toLowerCase())) return false;
    return true;
  });

  if (filtered.length === 0) {
    console.log('📭 No matching entries found.\n');
    return;
  }

  filtered.forEach(entry => {
    if (entry.type === 'search') {
      console.log(`🔎 "${entry.query}"`);
      console.log(`   Timestamp: ${entry.timestamp}`);
      console.log(`   Results: ${entry.result_count}`);
      console.log('');
      entry.results.forEach((result, idx) => {
        console.log(`   ${idx + 1}. ${result.title}`);
        console.log(`      ${result.url}`);
        if (result.snippet) {
          console.log(`      "${result.snippet.substring(0, 100)}..."`);
        }
        console.log('');
      });
      console.log('---\n');
    } else if (entry.type === 'error') {
      console.log(`❌ Error: "${entry.query}"`);
      console.log(`   ${entry.error}`);
      console.log(`   Timestamp: ${entry.timestamp}`);
      console.log('---\n');
    }
  });
}

/**
 * Display raw JSON
 */
function displayJson(entries) {
  console.log(JSON.stringify(entries, null, 2));
}

/**
 * Main function
 */
function main() {
  const args = process.argv.slice(2);

  // Parse arguments
  const filter = {};
  let showJson = false;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--query' && args[i + 1]) {
      filter.query = args[++i];
    } else if (arg === '--type' && args[i + 1]) {
      filter.type = args[++i];
    } else if (arg === '--json') {
      showJson = true;
    } else if (arg === '--help' || arg === '-h') {
      console.log('View Collected AI Prompts Data\n');
      console.log('Usage:');
      console.log('  node view-collected.js                    # Show summary');
      console.log('  node view-collected.js --query "tips"     # Filter by query');
      console.log('  node view-collected.js --type error       # Show errors only');
      console.log('  node view-collected.js --json             # Raw JSON output');
      console.log('  node view-collected.js --help             # Show this help');
      process.exit(0);
    }
  }

  const entries = readJsonl(OUTPUT_FILE);

  if (showJson) {
    displayJson(entries);
  } else if (Object.keys(filter).length > 0) {
    displayFiltered(entries, filter);
  } else {
    displaySummary(entries);
  }
}

if (require.main === module) {
  main();
}

module.exports = { readJsonl };
