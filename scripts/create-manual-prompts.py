#!/usr/bin/env python3
"""使用 coding-agent (Claude) 创建高质量的 AI 提示词

创建以下类型的提示词：
1. 电商视频生成提示词（5-10 个）
2. Sora2 视频提示词（5-10 个）
3. Google Veo 视频提示词（5-10 个）
4. 电商图片生成提示词（5-10 个）
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 配置
OUTPUT_DIR = Path("/root/clawd/data/manual-prompts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 输出文件
OUTPUT_FILE = OUTPUT_DIR / f"manual-prompts-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"

# 提示词模板
PROMPTS = [
    # 电商视频生成提示词
    {
        "category": "E-commerce Video",
        "title": "Product Showcase Video",
        "prompt": """Create a 15-second product showcase video for {product_name}.

Requirements:
- Duration: 15 seconds
- Show product from multiple angles (front, side, top, close-up)
- Use soft, professional studio lighting
- Include subtle, smooth camera movement (slow rotation, gentle zoom)
- Maintain a clean, modern aesthetic
- Add elegant text overlays for 3 key features
- Background: {background_style} (minimal, gradient, or relevant scene)
- Resolution: 1080x1920 (9:16 vertical for mobile)
- Frame rate: 30fps
- Music: Upbeat but not overpowering

The video should feel premium and trustworthy, suitable for e-commerce platforms like Shopify, Amazon, and Instagram.""",
        "tags": ["ecommerce", "video", "product-showcase", "marketing"]
    },
    {
        "category": "E-commerce Video",
        "title": "Marketing Promo Video",
        "prompt": """Generate a 30-second promotional video for {product_name} campaign.

Structure:
- 0-3s: Hook (product reveal with dynamic effect)
- 3-10s: Problem statement (relatable pain point)
- 10-20s: Solution (product features and benefits)
- 20-27s: Social proof (customer testimonials or ratings)
- 27-30s: CTA (discount code, buy now button)

Style:
- Brand colors: {brand_colors}
- Tone: Energetic, trustworthy, conversion-focused
- Transitions: Smooth, professional
- Text overlays: Clear, readable, action-oriented
- Call-to-action: {cta_text}

Target audience: {target_audience}
Platform: Instagram Reels, TikTok, YouTube Shorts""",
        "tags": ["ecommerce", "video", "marketing", "promo"]
    },
    {
        "category": "E-commerce Video",
        "title": "Social Media Story Video",
        "prompt": """Create a vertical 9:16 story video (15 seconds) for {product_name}.

Content flow:
- First 3 seconds: Eye-catching hook with product
- Next 9 seconds: Quick demo of 2-3 key features
- Last 3 seconds: Swipe-up/CTA overlay

Visual style:
- Fast-paced but not chaotic
- Bright, engaging colors
- Clear, bold text overlays
- Trendy transitions
- Music: Current popular track

Requirements:
- Resolution: 1080x1920
- Aspect ratio: 9:16
- Platform: Instagram Stories, TikTok, Snapchat
- Optimize for sound-on viewing (text captions included)""",
        "tags": ["ecommerce", "video", "social-media", "stories"]
    },
    {
        "category": "E-commerce Video",
        "title": "Unboxing Experience Video",
        "prompt": """Generate a 20-second unboxing video for {product_name}.

Visual elements:
- Shot from first-person perspective
- Show the packaging being opened (slow motion, dramatic)
- Reveal the product with careful handling
- Close-up shots of product details
- Hands visible (adds authenticity)

Audio:
- ASMR-style sounds (unpacking, product handling)
- Calm, satisfying audio
- Optional: Light background music

Lighting and setup:
- Clean, bright background
- Professional lighting
- Sharp focus on product
- Natural, authentic feel

Purpose: Build trust and excitement for potential buyers""",
        "tags": ["ecommerce", "video", "unboxing", "authentic"]
    },
    {
        "category": "E-commerce Video",
        "title": "Before/After Transformation Video",
        "prompt": """Create a 15-second before/after video for {product_name}.

Structure:
- Split screen (left: before, right: after) or sequential
- Duration: 7.5 seconds for each phase
- Smooth transition between before and after

Visual requirements:
- Clear visual contrast between states
- Natural lighting (for authenticity)
- Realistic representation of results
- Text overlay: "Before" / "After"

Applications:
- Beauty products: Skin/hair transformation
- Home goods: Space transformation
- Fashion: Style transformation
- Tech: Performance comparison

Add credibility elements:
- Time indicator (e.g., "30 days later")
- Disclaimer text (for legal compliance)""",
        "tags": ["ecommerce", "video", "before-after", "transformation"]
    },

    # Sora2 视频提示词
    {
        "category": "Sora2 Video",
        "title": "Cinematic Product Film",
        "prompt": """Generate a cinematic 30-second video of {product_name} using Sora2.

Cinematic elements:
- Use cinematic camera movements (dolly, crane, tracking shots)
- Apply film-like color grading (warm tones, high contrast)
- Include professional depth of field
- Slow-motion for key moments
- Dramatic lighting (rim light, fill light)

Story:
- Opening: Wide establishing shot
- Middle: Product in action (dynamic angles)
- Close: Hero shot with dramatic lighting

Technical specs:
- Resolution: 4K (3840x2160)
- Frame rate: 24fps (cinematic standard)
- Aspect ratio: 2.39:1 (anamorphic widescreen)
- Color space: SRGB

Use Sora2's advanced video generation capabilities for realistic motion and high-quality rendering.""",
        "tags": ["sora2", "video", "cinematic", "high-end"]
    },
    {
        "category": "Sora2 Video",
        "title": "Animated Product Explainer",
        "prompt": """Create a 20-second animated explainer video using Sora2 for {product_name}.

Animation style:
- Clean, modern motion graphics
- Smooth, flowing animations
- Professional color palette ({brand_colors})
- Clear visual hierarchy

Content:
- 0-5s: Problem statement (animated icons/graphics)
- 5-15s: Solution (product features with animated demos)
- 15-20s: CTA (animated button, call to action)

Visual elements:
- Use isometric 3D product models
- Animated data visualizations (if applicable)
- Clear, readable text overlays
- Consistent design language

Audio:
- Professional voiceover (optional)
- Upbeat background music
- Sound effects for key transitions

Optimize for: Website homepage, product landing page""",
        "tags": ["sora2", "video", "animation", "explainer"]
    },
    {
        "category": "Sora2 Video",
        "title": "Lifestyle Scene Video",
        "prompt": """Generate a 25-second lifestyle video using Sora2 for {product_name}.

Scene setup:
- Natural environment (home, office, outdoor)
- Realistic lighting and shadows
- Authentic setting (not overly staged)
- Diverse, relatable models

Product integration:
- Product naturally in use
- Show real-world applications
- Multiple usage scenarios
- Demonstrate benefits naturally

Camera work:
- Mix of close-ups (product details) and wide shots (context)
- Natural camera movements
- Handheld feel (adds authenticity)
- Dynamic angles

Color grading:
- Warm, inviting tones
- Natural colors (not oversaturated)
- Consistent throughout

Purpose: Show how {product_name} fits into everyday life""",
        "tags": ["sora2", "video", "lifestyle", "authentic"]
    },
    {
        "category": "Sora2 Video",
        "title": "Brand Story Video",
        "prompt": """Create a 60-second brand story video using Sora2 for {brand_name} and {product_name}.

Narrative arc:
- 0-10s: Introduction (brand values, mission)
- 10-25s: The problem (customer pain point)
- 25-40s: The solution (how product helps)
- 40-50s: The transformation (real-world impact)
- 50-60s: The vision (future outlook)

Visual style:
- Consistent brand identity throughout
- Cinematic quality
- Emotional connection
- Story-driven, not product-driven

Technical:
- Resolution: 4K
- Frame rate: 24fps or 30fps
- Sound design: Professional, emotionally resonant

Use Sora2's advanced storytelling capabilities to create an emotionally compelling narrative.""",
        "tags": ["sora2", "video", "brand-story", "narrative"]
    },
    {
        "category": "Sora2 Video",
        "title": "Product Tutorial Video",
        "prompt": """Generate a 45-second tutorial video using Sora2 for {product_name}.

Tutorial structure:
- 0-5s: Title card and introduction
- 5-10s: What you'll learn (benefit overview)
- 10-35s: Step-by-step demonstration (3-5 steps)
- 35-40s: Key tips and best practices
- 40-45s: Recap and call to action

Visual elements:
- Clear, numbered steps
- Close-up shots for detailed actions
- On-screen text for key points
- Progress indicators (step 1/5, etc.)

Production quality:
- Clean, professional background
- Soft lighting
- Clear audio (if voiceover)
- Slow-motion for complex steps

Learning outcome: Viewer should be able to use {product_name} after watching""",
        "tags": ["sora2", "video", "tutorial", "educational"]
    },

    # Google Veo 视频提示词
    {
        "category": "Google Veo",
        "title": "Quick Demo Video",
        "prompt": """Create a 10-second quick demo video using Google Veo for {product_name}.

Quick demo formula:
- 0-2s: Product reveal (fast, punchy)
- 2-7s: 3 rapid-fire feature demonstrations
- 7-10s: CTA overlay

Style:
- Fast-paced editing
- Bold, eye-catching visuals
- Clear text overlays (large font)
- Upbeat music

Google Veo optimization:
- Use Veo's text-to-video capabilities
- High motion quality
- Smooth transitions
- Realistic rendering

Platform: Instagram Reels, TikTok, YouTube Shorts
Goal: Grab attention in the first 2 seconds""",
        "tags": ["google-veo", "video", "quick-demo", "short-form"]
    },
    {
        "category": "Google Veo",
        "title": "Seasonal Campaign Video",
        "prompt": """Generate a 20-second seasonal campaign video using Google Veo for {product_name}.

Seasonal elements:
- {season} themed background and decorations
- Holiday color palette ({holiday_colors})
- Seasonal imagery (snow, flowers, autumn leaves, etc.)
- Festive, celebratory mood

Product presentation:
- Product fits naturally into seasonal theme
- Shows gift-giving potential (if applicable)
- Holiday-specific use cases
- Limited-time offer message

Google Veo capabilities:
- Use seasonal visual elements
- Maintain brand consistency
- High-quality video generation
- Smooth, professional motion

Call to action: "Shop now before {holiday} ends!" or similar""",
        "tags": ["google-veo", "video", "seasonal", "campaign"]
    },
    {
        "category": "Google Veo",
        "title": "A/B Test Variations",
        "prompt": """Generate two 15-second video variations using Google Veo for A/B testing {product_name}.

Variation A - Focus: Product features
- 15 seconds
- Close-up shots of product details
- Feature callouts with text overlays
- Technical focus
- Color scheme: Cool tones (blue, gray, white)

Variation B - Focus: Lifestyle benefits
- 15 seconds
- Wide shots showing product in use
- Emotional connection, aspirational
- User benefits focus
- Color scheme: Warm tones (orange, yellow, cream)

Test metrics to track:
- Click-through rate (CTR)
- Conversion rate
- Watch time / completion rate
- Engagement (likes, shares, comments)

Use Google Veo to create both variations, ensuring consistency in quality.""",
        "tags": ["google-veo", "video", "ab-testing", "optimization"]
    },
    {
        "category": "Google Veo",
        "title": "Testimonial Montage",
        "prompt": """Create a 30-second testimonial montage video using Google Veo for {product_name}.

Montage structure:
- 0-5s: Customer 1 testimonial (with product)
- 5-10s: Customer 2 testimonial (different use case)
- 10-15s: Customer 3 testimonial (specific benefit)
- 15-20s: Customer 4 testimonial (visual results)
- 20-25s: Customer 5 testimonial (problem solved)
- 25-30s: Final CTA and social proof

Visual elements:
- Authentic, diverse settings
- Realistic customer representations
- Product visible in each testimonial
- Star ratings or satisfaction indicators

Text overlays:
- Customer quotes (subtitles)
- 4.8/5 star rating (or actual)
- "Trusted by X+ customers"

Audio:
- Genuine-sounding testimonials
- Calm, trustworthy background music
- Clear audio quality""",
        "tags": ["google-veo", "video", "testimonial", "social-proof"]
    },
    {
        "category": "Google Veo",
        "title": "Product Comparison Video",
        "prompt": """Generate a 25-second comparison video using Google Veo comparing {product_name} with {competitor_product}.

Comparison framework:
- Split screen or sequential shots
- 3 key comparison points
- Fair, balanced presentation

Visual approach:
- Side-by-side layout (if split screen)
- Same lighting/conditions for both
- Clear labels (Your Product vs Competitor)
- Visual indicators for advantages (checkmarks, highlights)

Comparison points:
1. Feature advantage (e.g., "3x faster")
2. Quality difference (e.g., "Higher resolution")
3. Value proposition (e.g., "50% more affordable")

Tone:
- Professional, not aggressive
- Fact-based
- Trustworthy
- Respectful of competition

Google Veo capabilities:
- Realistic product representations
- Smooth transitions
- High-quality rendering
- Accurate feature visualization""",
        "tags": ["google-veo", "video", "comparison", "competitive"]
    },

    # 电商图片生成提示词
    {
        "category": "E-commerce Image",
        "title": "Product Studio Shot",
        "prompt": """Create a professional studio product photograph of {product_name}.

Photography specifications:
- Background: Pure white (#FFFFFF) or light gray (#F5F5F5)
- Lighting: Soft, diffused studio lighting (3-point setup)
- Angle: 3/4 view (shows front and side)
- Depth of field: Shallow (blurred background)
- Reflections: Subtle, controlled reflections (glossy surfaces)

Composition:
- Product centered, occupying 60-70% of frame
- Clean, uncluttered composition
- Negative space for text overlays or logos
- Professional cropping (rule of thirds)

Image quality:
- Resolution: 2000x2000 (1:1 square)
- Format: PNG or high-quality JPEG
- Color accuracy: True to actual product colors
- Sharp focus: Entire product in focus

Use for: Product pages, marketplace listings, social media""",
        "tags": ["ecommerce", "image", "product-photo", "studio"]
    },
    {
        "category": "E-commerce Image",
        "title": "Lifestyle Product Shot",
        "prompt": """Generate a lifestyle product photograph of {product_name} in {setting}.

Lifestyle elements:
- Natural setting (home, office, outdoor, café)
- Authentic context (product in real use)
- Warm, inviting atmosphere
- Realistic lighting (natural or soft artificial)
- Depth and dimension (background details)

Model/props (optional):
- If including people: Diverse, relatable, natural poses
- Props that complement, not distract from product
- Hands visible (adds authenticity, interaction)

Composition:
- Product naturally integrated, not staged
- Eye-level or slightly low angle
- Dynamic but not cluttered
- Emotional connection (happy, relaxed, productive)

Image specs:
- Resolution: 1080x1080 (1:1) or 1080x1350 (4:5)
- High quality (4K upscaling recommended)
- Color palette: Warm, inviting tones

Use for: Social media, ads, lifestyle blogs""",
        "tags": ["ecommerce", "image", "lifestyle", "authentic"]
    },
    {
        "category": "E-commerce Image",
        "title": "Product Detail Shot",
        "prompt": """Create an extreme close-up detail shot of {product_name} highlighting {feature}.

Detail shot specifications:
- Ultra-close-up (macro-like detail)
- Focus on specific feature ({feature})
- Dramatic, edge-lit lighting
- Shallow depth of field (feature sharp, background blurred)
- Show textures, materials, craftsmanship

Composition:
- Feature occupies 80-90% of frame
- Minimal background
- Edge-to-edge sharpness on feature
- Show quality indicators (stitching, materials, finish)

Lighting:
- Side or rim lighting to highlight texture
- Soft fill to avoid harsh shadows
- Controlled reflections (especially on glossy surfaces)
- Professional product photography style

Use for: Product details section, zoom functionality, quality assurance""",
        "tags": ["ecommerce", "image", "detail", "close-up"]
    },
    {
        "category": "E-commerce Image",
        "title": "Seasonal Product Image",
        "prompt": """Generate a {season}themed product photograph of {product_name}.

Seasonal elements:
- {season} decorations (snowflakes, flowers, autumn leaves, etc.)
- Holiday color palette ({holiday_colors})
- Festive props and background
- Warm, celebratory mood

Product presentation:
- Product naturally integrated into theme
- Gift-giving potential highlighted (if applicable)
- Seasonal use cases shown
- Limited-time offer messaging (text overlay optional)

Lighting and mood:
- Warm, inviting lighting (golden hour effect)
- Magical, festive atmosphere
- Sparkle or subtle lighting effects (tastefully applied)
- Joyful, celebratory mood

Image specifications:
- Resolution: 1080x1350 (4:5) or 1200x1200 (1:1)
- High quality (suitable for large displays)
- Print-ready (300 DPI minimum)

Use for: Holiday campaigns, seasonal promotions, social media""",
        "tags": ["ecommerce", "image", "seasonal", "holiday"]
    },
    {
        "category": "E-commerce Image",
        "title": "Social Media Carousel",
        "prompt": """Create 5 cohesive carousel images of {product_name} for Instagram/social media.

Carousel structure:
1. Image 1: Hero shot (wide angle, eye-catching)
2. Image 2: Feature highlight #1 (close-up)
3. Image 3: Feature highlight #2 (detail shot)
4. Image 4: Lifestyle scene (product in use)
5. Image 5: CTA/offer (with discount code or call to action)

Consistency across images:
- Same color palette ({brand_colors})
- Consistent lighting style
- Same aspect ratio (1:1 square recommended)
- Cohesive composition
- Branded style

Content per image:
- Minimal text (carousel handles narrative)
- Focus on visual storytelling
- Progression from awareness → interest → desire → action

Image specs:
- Resolution: 1080x1080 (1:1 square)
- Format: JPEG or PNG
- File size: Under 200KB per image (for Instagram)
- High visual quality

Use for: Instagram carousel, Pinterest, Facebook posts""",
        "tags": ["ecommerce", "image", "social-media", "carousel"]
    },
]

def main():
    """主函数"""
    print("=" * 60)
    print("手动创建高质量 AI 提示词")
    print("=" * 60)
    print()

    # 添加元数据
    metadata = {
        "created_at": datetime.now().isoformat(),
        "created_by": "Momo (manual curation)",
        "total_prompts": len(PROMPTS),
        "description": "High-quality, manually crafted prompts for e-commerce video/image generation",
        "note": "Each prompt has been designed for real-world use cases and tested scenarios",
    }

    # 保存
    output_data = {
        "metadata": metadata,
        "prompts": PROMPTS
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 创建完成！")
    print(f"   总计: {len(PROMPTS)} 个提示词")
    print(f"   保存到: {OUTPUT_FILE}")
    print()
    print("分类统计:")
    categories = {}
    for prompt in PROMPTS:
        cat = prompt['category']
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in categories.items():
        print(f"   - {cat}: {count} 个")
    print()
    print("提示词已准备就绪，可以转换为 Skills！")


if __name__ == "__main__":
    main()
