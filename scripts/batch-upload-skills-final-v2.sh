#!/bin/bash
# Batch upload all Skills to ClawdHub (Final Version)

set -e

SKILLS_DIR="/root/clawd/dist/skills"
REGISTRY_URL="https://www.clawhub.ai/api"
LOG_FILE="/root/clawd/logs/clawdhub-upload.log"
SUCCESS_COUNT=0
FAILED_COUNT=0
FAILED_SKILLS=()

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

find_skill_md() {
    local dir="$1"
    local skill_md=""
    
    if [ -f "$dir/SKILL.md" ]; then
        skill_md="$dir/SKILL.md"
    else
        for subdir in "$dir"/*/; do
            if [ -d "$subdir" ] && [ -f "$subdir/SKILL.md" ]; then
                skill_md="$subdir/SKILL.md"
                break
            fi
        done
    fi
    
    echo "$skill_md"
}

main() {
    log "=========================================="
    log "Batch upload all Skills to ClawdHub"
    log "=========================================="
    log ""
    
    log_info "Configuration:"
    log "  Skills Directory: $SKILLS_DIR"
    log "  Registry: $REGISTRY_URL"
    log ""
    
    if [ ! -d "$SKILLS_DIR" ]; then
        log_error "Skills directory does not exist: $SKILLS_DIR"
        exit 1
    fi
    
    TOTAL_SKILLS=$(find "$SKILLS_DIR" -name "*.skill" -type f 2>/dev/null | wc -l)
    
    if [ $TOTAL_SKILLS -eq 0 ]; then
        log_warn "No .skill files found to upload"
        exit 0
    fi
    
    log_info "Found $TOTAL_SKILLS .skill files"
    log ""
    
    for skill_file in "$SKILLS_DIR"/*.skill; do
        if [ ! -f "$skill_file" ]; then
            continue
        fi
        
        skill_name=$(basename "$skill_file" .skill)
        temp_dir="/tmp/skill-upload-$$-$skill_name"
        
        log_info "Processing: $skill_name"
        
        mkdir -p "$temp_dir"
        
        cd "$temp_dir"
        if ! unzip -q "$skill_file"; then
            log_error "Unzip failed: $skill_file"
            cd - > /dev/null
            rm -rf "$temp_dir"
            continue
        fi
        
        skill_md_path=$(find_skill_md ".")
        
        if [ ! -f "$skill_md_path" ]; then
            log_warn "SKILL.md not found, skipping: $skill_name"
            cd - > /dev/null
            rm -rf "$temp_dir"
            continue
        fi
        
        display_name=$(grep "^# " "$skill_md_path" 2>/dev/null | head -1 | cut -d '#' -f2 | xargs)
        if [ -z "$display_name" ]; then
            display_name="$skill_name"
        fi
        
        skill_subdir=$(dirname "$skill_md_path")
        cd "$skill_subdir"
        
        if clawdhub publish "$skill_subdir" \
            --registry "$REGISTRY_URL" \
            --slug "$skill_name" \
            --name "$display_name" \
            --version "1.0.0" \
            --changelog "AI Prompts conversion - Image Generation/Video Generation/Coding related" 2>&1 | tee -a "$LOG_FILE"; then
            
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            log_info "Success: $skill_name"
        else
            FAILED_COUNT=$((FAILED_COUNT + 1))
            FAILED_SKILLS+=("$skill_name")
            log_error "Failed: $skill_name"
        fi
        
        cd - > /dev/null
        rm -rf "$temp_dir"
        
        sleep 1
    done
    
    log ""
    log "=========================================="
    log "Upload Statistics"
    log "=========================================="
    log_info "Success: $SUCCESS_COUNT"
    log_error "Failed: $FAILED_COUNT"
    log ""
    
    if [ $FAILED_COUNT -gt 0 ]; then
        log_error "Failed Skills:"
        for skill in "${FAILED_SKILLS[@]}"; do
            log "  - $skill"
        done
        log ""
    fi
    
    # Send notification
    if [ $SUCCESS_COUNT -gt 0 ]; then
        SUCCESS_MESSAGE="✅ **ClawdHub Batch Upload Complete!**

📊 **Statistics**:
• Success: $SUCCESS_COUNT
• Failed: $FAILED_COUNT

**Result**: $SUCCESS_COUNT Skills successfully published to ClawdHub!

🔗 **View Skills**: https://www.clawhub.ai/ search for your Skills"
"
        
        # Send to Feishu
        clawdbot message send --channel feishu --target ou_3bc5290afc1a94f38e23dc17c35f26d6 --message "$SUCCESS_MESSAGE" >> "$LOG_FILE" 2>&1 || log_error "Feishu notification failed"
        
        # Send to Slack
        clawdbot message send --channel slack --target D0AB0J4QLAH --message "$SUCCESS_MESSAGE" >> "$LOG_FILE" 2>&1 || log_error "Slack notification failed"
    else
        log_info "No Skills were successfully uploaded"
    fi
    
    log ""
    log "=========================================="
    log "✅ Upload Complete"
    log "=========================================="
    log ""
    log "Log file: $LOG_FILE"
    log ""
}

main "$@"
