---
name: wechat-cover-generator
description: "Generate optimized WeChat official account cover prompts for AI image generators (Midjourney, Stable Diffusion, DALL-E). Use when users need: (1) Create WeChat cover images with proper dimensions (900×383px, 2.35:1 aspect ratio), (2) Generate prompts for specific industries/verticals, (3) Extract and analyze high-quality prompts from X (Twitter), (4) Evaluate prompt quality and commercial value. Supports 50+ industry templates, automated prompt generation, quality scoring, and periodic X scanning for new prompt patterns."
---

# WeChat Cover Generator

## Overview

This skill generates professional WeChat official account cover prompts optimized for AI image generators. It includes a curated template library of 50+ industry verticals, an automated quality scoring system, and continuous learning from X (Twitter) to capture trending prompt patterns.

All generated prompts include:
- WeChat-specific dimensions (900×383px, 2.35:1 aspect ratio)
- Text placeholder areas for headlines
- WeChat ecosystem-appropriate aesthetic styles
- Industry-specific visual language and color schemes

## Core Capabilities

### 1. Generate WeChat Cover Prompts

**Workflow:**
1. Collect user input: topic/title, industry/vertical, brand preferences
2. Select appropriate template from [PROMPT_TEMPLATES.md](references/PROMPT_TEMPLATES.md)
3. Customize prompt with user-specific details
4. Output ready-to-use prompt for Midjourney/Stable Diffusion

**User triggers:**
- "Generate a WeChat cover for [topic]"
- "Create a cover prompt for [industry]"
- "I need a cover for my article about [subject]"
- "Make a WeChat-style cover for [company/product]"

**Example output:**
```
A professional magazine cover for a business WeChat official account, minimalist design, 
featuring abstract geometric shapes in blue and gold gradients, modern typography with 
headline space, clean layout, 900x383 aspect ratio, 4K quality, professional lighting --ar 2.35:1
```

### 2. Industry-Specific Templates

Access the curated prompt library in [PROMPT_TEMPLATES.md](references/PROMPT_TEMPLATES.md) for pre-built templates across:

- **Business & Finance**: Fintech, corporate, investment, blockchain
- **Technology**: AI, SaaS, hardware, software development
- **Lifestyle**: Food, travel, fashion, wellness
- **Education**: E-learning, courses, tutorials, certifications
- **Healthcare**: Medical devices, wellness, pharmaceuticals
- **Media & Entertainment**: Gaming, streaming, music, video
- **Professional Services**: Legal, consulting, HR, marketing
- **E-commerce**: Retail, marketplace, luxury, consumer goods

**Usage:**
Read the appropriate industry section from PROMPT_TEMPLATES.md when generating prompts for that vertical.

### 3. Quality Scoring System

Use [SCORING_CRITERIA.md](references/SCORING_CRITERIA.md) to evaluate prompt quality:

**Scoring dimensions:**
- **Technical Quality** (0-10): Aspect ratio, resolution, technical parameters
- **Commercial Value** (0-10): Brand alignment, visual hierarchy, professionalism
- **WeChat Compatibility** (0-10): Dimension accuracy, text space, ecosystem fit
- **Uniqueness** (0-10): Originality, creativity, differentiation

**Usage:**
1. Run `scripts/score_prompt.py` to automatically score prompts
2. Or manually evaluate using criteria from SCORING_CRITERIA.md
3. Average scores across dimensions for overall quality (0-10)

### 4. X (Twitter) Prompt Mining

Automated scanning and extraction of high-quality AI prompts from X:

**Automation:**
- `scripts/scan_twitter_prompts.py` - Scans X for AI image generation prompts
- Scheduled via cron every 6 hours (see `scripts/setup_twitter_scan.sh`)

**Manual extraction:**
Use [TWITTER_EXTRACTION_GUIDE.md](references/TWITTER_EXTRACTION_GUIDE.md) for:
- Search strategies on X
- Quality filtering criteria
- Pattern recognition techniques
- Integrating found prompts into template library

**Cron job setup:**
```bash
bash /root/clawd/skills/wechat-cover-generator/scripts/setup_twitter_scan.sh
```

This installs a cron job running every 6 hours at `0 */6 * * *` to scan X and update the prompt library.

### 5. Prompt Optimization

Enhance existing prompts using [OPTIMIZATION_GUIDE.md](references/OPTIMIZATION_GUIDE.md):

**Optimization techniques:**
- Add WeChat-specific dimensions and aspect ratios
- Improve text space allocation
- Refine color schemes for WeChat audience
- Enhance visual hierarchy
- Add quality boosters (lighting, resolution, render quality)

**Usage:**
Read OPTIMIZATION_GUIDE.md when users want to improve existing prompts.

## Quick Start Examples

### Example 1: Generate Business Cover
**User request:** "Create a WeChat cover for a fintech article about blockchain"

**Response:**
1. Read Business & Finance templates from PROMPT_TEMPLATES.md
2. Customize with fintech/blockchain keywords
3. Output:
```
Modern fintech cover for WeChat official account, blockchain network visualization 
with interconnected nodes and digital chains, deep blue and emerald gradients, 
sleek minimalist design, clean headline space, professional corporate aesthetic, 
4K render, high contrast, 900x383 aspect ratio --ar 2.35:1 --v 6.0
```

### Example 2: Score a Prompt
**User request:** "Evaluate this prompt quality"

**Response:**
1. Run `scripts/score_prompt.py <prompt>`
2. Output scores for each dimension with explanations
3. Provide improvement suggestions if score < 7.0

### Example 3: Extract from X
**User request:** "Find good cover prompts on Twitter"

**Response:**
1. Read TWITTER_EXTRACTION_GUIDE.md
2. Use search strategies to find relevant tweets
3. Apply quality filters
4. Extract top prompts and convert to WeChat format
5. Add to PROMPT_TEMPLATES.md if high quality

## Scripts

### `scripts/score_prompt.py`
Automatically score prompts based on [SCORING_CRITERIA.md](references/SCORING_CRITERIA.md).

**Usage:**
```bash
python3 /root/clawd/skills/wechat-cover-generator/scripts/score_prompt.py "<prompt>"
```

**Output:**
- Technical Quality: X/10
- Commercial Value: X/10
- WeChat Compatibility: X/10
- Uniqueness: X/10
- Overall: X/10

### `scripts/scan_twitter_prompts.py`
Scan X for AI image generation prompts and extract high-quality examples.

**Usage:**
```bash
python3 /root/clawd/skills/wechat-cover-generator/scripts/scan_twitter_prompts.py
```

**Output:**
- Saves extracted prompts to `scripts/extracted_prompts.json`
- Logs scan results with timestamps
- Filters by quality criteria (likes, retweets, prompt structure)

### `scripts/setup_twitter_scan.sh`
Set up automated cron job for periodic X scanning.

**Usage:**
```bash
bash /root/clawd/skills/wechat-cover-generator/scripts/setup_twitter_scan.sh
```

**Schedule:** Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)

## Reference Materials

### [PROMPT_TEMPLATES.md](references/PROMPT_TEMPLATES.md)
Curated library of 50+ industry-specific WeChat cover prompt templates.

**Structure:**
- Industry categories
- Template prompts
- Visual style guidelines
- Color palette recommendations
- Text placement notes

**When to read:**
- Before generating any WeChat cover prompt
- When exploring new industry verticals
- For inspiration on prompt structure

### [SCORING_CRITERIA.md](references/SCORING_CRITERIA.md)
Detailed evaluation criteria for prompt quality assessment.

**Structure:**
- Scoring methodology
- Dimension-specific rubrics
- Example prompts with scores
- Quality benchmarks

**When to read:**
- Before scoring prompts
- When setting quality thresholds
- For understanding what makes high-quality prompts

### [TWITTER_EXTRACTION_GUIDE.md](references/TWITTER_EXTRACTION_GUIDE.md)
Guide for mining X (Twitter) for high-quality AI prompts.

**Structure:**
- Search strategies and keywords
- Quality indicators (likes, retweets, replies)
- Prompt pattern recognition
- Conversion to WeChat format
- Integration workflow

**When to read:**
- Before manual X scanning
- When setting up automated scanning
- For understanding quality filters

### [OPTIMIZATION_GUIDE.md](references/OPTIMIZATION_GUIDE.md)
Techniques for improving existing prompts for WeChat compatibility.

**Structure:**
- WeChat-specific optimizations
- Dimension and aspect ratio adjustments
- Text space enhancement
- Color scheme refinement
- Technical parameter tuning

**When to read:**
- When users want to improve existing prompts
- When optimizing extracted X prompts
- For troubleshooting prompt issues

## Commercial Value Assessment

When generating or evaluating prompts, consider commercial value factors:

1. **Market Demand**: How many content creators need this style?
2. **Uniqueness**: Is this differentiated from generic prompts?
3. **Ease of Use**: Can non-designers generate quality results?
4. **Scalability**: Can this template apply to multiple topics?
5. **Brand Alignment**: Does it fit professional standards?

High-commercial-value prompts should score ≥ 8.0 in the Commercial Value dimension.

## Troubleshooting

**Problem:** Prompt doesn't generate good images
- **Solution:** Check if aspect ratio is included (`--ar 2.35:1`)
- **Solution:** Verify resolution specifications (4K, 8K)
- **Solution:** Ensure text space is explicitly mentioned

**Problem:** Text overlay is hard to add
- **Solution:** Add specific text placeholder instructions ("clean headline space on left")
- **Solution:** Include contrast enhancement keywords ("high contrast", "clean background")

**Problem:** Style doesn't match WeChat aesthetic
- **Solution:** Review PROMPT_TEMPLATES.md for industry-specific style guides
- **Solution:** Add WeChat ecosystem keywords ("WeChat official account style", "Chinese social media aesthetic")

## Continuous Learning

The skill evolves through:
1. **Automated X scanning**: Every 6 hours via cron job
2. **User feedback**: Track which templates get most use
3. **Quality monitoring**: Monitor scores and adjust templates
4. **Market trends**: Update with new industry verticals as needed

Update PROMPT_TEMPLATES.md regularly with new patterns discovered from X scanning.
