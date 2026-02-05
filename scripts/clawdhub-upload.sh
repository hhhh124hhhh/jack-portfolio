#!/bin/bash
# ClawdHub Batch Upload - Correct Version with Current Directory

SKILLS_DIR="/root/clawd/dist/skills"
LOG_FILE="/root/clawd/logs/clawdhub-upload.log"
SUCCESS_COUNT=0
FAILED_COUNT=0
FAILED_LIST=()

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting batch upload..." | tee -a "$LOG_FILE"

# Check directory
if [ ! -d "$SKILLS_DIR" ]; then
    echo "ERROR: Skills directory does not exist: $SKILLS_DIR" | tee -a "$LOG_FILE"
    exit 1
fi

TOTAL=$(find "$SKILLS_DIR" -name "*.skill" -type f 2>/dev/null | wc -l)
echo "Found $TOTAL .skill files" | tee -a "$LOG_FILE"

# Process each skill
for skill_file in "$SKILLS_DIR"/*.skill; do
    if [ ! -f "$skill_file" ]; then
        continue
    fi
    
    skill_name=$(basename "$skill_file" .skill)
    temp_dir="/tmp/skill-upload-$$-$skill_name"
    
    echo "Processing: $skill_name" | tee -a "$LOG_FILE"
    
    mkdir -p "$temp_dir"
    cd "$temp_dir"
    
    # Unzip
    if ! unzip -q "$skill_file"; then
        echo "  ERROR: Unzip failed: $skill_file" | tee -a "$LOG_FILE"
        rm -rf "$temp_dir"
        continue
    fi
    
    # Find SKILL.md in subdirectory
    SKILL_MD=$(find . -name "SKILL.md" -type f 2>/dev/null | head -1)
    
    if [ ! -f "$SKILL_MD" ]; then
        echo "  ERROR: SKILL.md not found, skipping: $skill_name" | tee -a "$LOG_FILE"
        rm -rf "$temp_dir"
        cd - > /dev/null
        continue
    fi
    
    # Get directory containing SKILL.md
    SKILL_DIR=$(dirname "$SKILL_MD")
    
    # Get display name
    DISPLAY_NAME=$(grep "^# " "$SKILL_MD" 2>/dev/null | head -1 | cut -d '#' -f2 | xargs)
    if [ -z "$DISPLAY_NAME" ]; then
        DISPLAY_NAME="$skill_name"
    fi
    
    # Change to current directory (important!)
    cd "$SKILL_DIR"
    
    echo "  Publishing from: $(pwd)" | tee -a "$LOG_FILE"
    
    # Publish
    if clawdhub publish \
        --registry "https://www.clawhub.ai/api" \
        --slug "$skill_name" \
        --name "$DISPLAY_NAME" \
        --version "1.0.0" \
        --changelog "AI Prompts conversion - Image Generation/Video Generation/Coding related" \
        . 2>&1 | tee -a "$LOG_FILE"; then
        
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo "  SUCCESS: Published $skill_name" | tee -a "$LOG_FILE"
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
        FAILED_LIST+=("$skill_name")
        echo "  FAILED: $skill_name" | tee -a "$LOG_FILE"
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
echo "Success: $SUCCESS_COUNT" | tee -a "$LOG_FILE"
echo "Failed: $FAILED_COUNT" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

if [ $FAILED_COUNT -gt 0 ]; then
    echo "Failed Skills:" | tee -a "$LOG_FILE"
    for skill in "${FAILED_LIST[@]}"; do
        echo "  - $skill" | tee -a "$LOG_FILE"
    done
fi

# Notification
if [ $SUCCESS_COUNT -gt 0 ]; then
    MESSAGE="ClawdHub Batch Upload Complete!

Success: $SUCCESS_COUNT
Failed: $FAILED_COUNT

Result: $SUCCESS_COUNT Skills successfully published to ClawdHub!

View Skills: https://www.clawhub.ai/ search for your Skills"
    
    # Feishu
    clawdbot message send \
        --channel feishu \
        --target ou_3bc5290afc1a94f38e23dc17c35f26d6 \
        --message "$MESSAGE" >> "$LOG_FILE" 2>&1 || echo "Feishu notification failed"
    
    # Slack
    clawdbot message send \
        --channel slack \
        --target D0AB0J4QLAH \
        --message "$MESSAGE" >> "$LOG_FILE" 2>&1 || echo "Slack notification failed"
else
    echo "No Skills were successfully uploaded" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Upload Complete" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo ""
echo "Log: $LOG_FILE" | tee -a "$LOG_FILE"
