#!/bin/bash

# AI Prompts Collector - Quick Start Script
#
# This script checks for BRAVE_API_KEY and runs the collector if configured.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔍 AI Prompts Collector"
echo "========================"
echo ""

# Check for API key
if [ -z "$BRAVE_API_KEY" ]; then
    echo "❌ Error: BRAVE_API_KEY is not set"
    echo ""
    echo "To set up:"
    echo "  1. Get a free API key from https://brave.com/search/api/"
    echo "  2. Run: export BRAVE_API_KEY=your_api_key_here"
    echo "  3. Or add to ~/.bashrc: echo 'export BRAVE_API_KEY=your_api_key_here' >> ~/.bashrc"
    echo ""
    exit 1
fi

echo "✓ API key configured"
echo ""

# Run the collector
node collect-prompts.js

echo ""
echo "💡 Tip: Add to crontab to run automatically:"
echo "   crontab -e"
echo "   # Add: 0 9 * * * $SCRIPT_DIR/run-collect-prompts.sh >> $SCRIPT_DIR/collect-prompts.log 2>&1"
