# AI Prompts Skills - Publishing Guide

## Summary
✅ **Fixed generation script** with proper YAML frontmatter
✅ **Generated 40 skills** from AI prompts
⏳ **Pending publication** - waiting for new ClawdHub token

## What Was Fixed
1. **YAML Frontmatter**: Now includes correct `name`, `description`, and `metadata` fields
2. **Description**: No longer truncated (now up to 500 characters)
3. **Skill Names**: Properly cleaned special characters for slugs

## Skills Generated
- **40 skills** from image generation prompts
- **Quality filtered** (score >= 60)
- **Packed as .skill files** in `/root/clawd/dist/skills/`

## Example Skill Structure
```yaml
---
name: 10-of-my-most-popular-text-to-image-series-prompts-78b0897e
description: generate a bunch of images, then you curate the results to handpick the best ones
metadata: {"clawdbot":{"type":"image generation","source":"image-generation","original_url":"https://www.whytryai.com/p/my-popular-text-to-image-series"}}
---
```

## Next Steps
Once you have a new ClawdHub token:
1. `clawdhub login --token <新token>`
2. `cd /root/clawd/scripts && bash clawdhub-upload-correct.sh`
3. All 40 skills will be published automatically

## Alternative: Manual Installation
If you want to install skills locally:
```bash
clawdhub install <skill-slug>
```

Or download .skill files from `/root/clawd/dist/skills/`

---

**Generated**: 2026-01-31 09:25 GMT+8
**Status**: Ready to publish (waiting for token)
