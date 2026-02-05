#!/bin/bash
# Simple ClawdHub Batch Upload

SKILLS_DIR="/root/clawd/dist/skills"
LOG_FILE="/root/clawd/logs/clawdhub-simple-upload.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting batch upload..." | tee -a "$LOG_FILE"

# Check directory
if [ ! -d "$SKILLS_DIR" ]; then
    echo "ERROR: Skills directory not found: $SKILLS_DIR" | tee -a "$LOG_FILE"
    exit 1
fi

# Count files
TOTAL=$(find "$SKILLS_DIR" -name "*.skill" -type f 2>/dev/null | wc -l)
echo "Found $TOTAL .skill files" | tee -a "$LOG_FILE"

# Process each skill
SUCCESS=0
FAILED=0
FAILED_LIST=()

for skill_file in "$SKILLS_DIR"/*.skill; do
    if [ ! -f "$skill_file" ]; then
        continue
    fi
    
    skill_name=$(basename "$skill_file" .skill)
    temp_dir="/tmp/skill-$$-$skill_name"
    
    echo "Processing: $skill_name" | tee -a "$LOG_FILE"
    
    mkdir -p "$temp_dir"
    cd "$temp_dir"
    
    if unzip -q "$skill_file" 2>/dev/null; then
        echo "  Unzipped" | tee -a "$LOG_FILE"
    else
        echo "  ERROR: Unzip failed" | tee -a "$LOG_FILE"
        FAILED=$((FAILED + 1))
        FAILED_LIST+=("$skill_name")
        rm -rf "$temp_dir"
        continue
    fi
    
    # Find SKILL.md
    SKILL_MD=$(find . -name "SKILL.md" -type f 2>/dev/null | head -1)
    
    if [ -z "$SKILL_MD" ]; then
        echo "  ERROR: SKILL.md not found" | tee -a "$LOG_FILE"
        FAILED=$((FAILED + 1))
        FAILED_LIST+=("$skill_name")
        cd - > /dev/null
        rm -rf "$temp_dir"
        continue
    fi
    
    # Get display name
    DISPLAY_NAME=$(grep "^# " "$SKILL_MD" 2>/dev/null | head -1 | cut -d '#' -f2 | xargs)
    if [ -z "$DISPLAY_NAME" ]; then
        DISPLAY_NAME="$skill_name"
    fi
    
    # Upload
    echo "  Uploading..." | tee -a "$LOG_FILE"
    
    cd "$(dirname "$SKILL_MD")"
    
    if clawdhub publish \
        --registry "https://www.clawhub.ai/api" \
        --slug "$skill_name" \
        --name "$DISPLAY_NAME" \
        --version "1.0.0" \
        --changelog "AI Prompts - Image Generation/Video Generation/Coding" 2>&1 | tee -a "$LOG_FILE"; then
        
        SUCCESS=$((SUCCESS + 1))
        echo "  SUCCESS: Published" | tee -a "$LOG_FILE"
    else
        FAILED=$((FAILED + 1))
        FAILED_LIST+=("$skill_name")
        echo "  ERROR: Publish failed" | tee -a "$LOG_FILE"
    fi
    
    cd - > /dev/null
    rm -rf "$temp_dir"
    
    # Add delay
    sleep 1
done

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Upload Statistics" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Success: $SUCCESS" | tee -a "$LOG_FILE"
echo "Failed: $FAILED" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Notification
if [ $SUCCESS -gt 0 ]; then
    MESSAGE="ClawdHub Upload Complete!

Success: $SUCCESS
Failed: $FAILED

Skills have been published to ClawdHub: https://www.clawhub.ai/"
    
    clawdbot message send \
        --channel feishu \
        --target ou_3bc5290afc1a94f38e23dc17c35f26d6 \
        --message "$MESSAGE" 2>&1 || true
    
    clawdbot message send \
        --channel slack \
        --target D0AB0J4QLAH \
        --message "$MESSAGE" 2>&1 || true
fi

echo "Complete!" | tee -a "$LOG_FILE"
echo "Log: $LOG_FILE" | tee -a "$LOG_FILE"
