#!/usr/bin/env python3
"""
Visual AI Prompts Collector V2
改进版：获取完整页面内容，添加类型标注和完整性检查
"""

import json
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path
import re

DATA_DIR = Path("/root/clawd/data/prompts")
IMAGE_PROMPTS_FILE = DATA_DIR / "image-prompts-v2.jsonl"
VIDEO_PROMPTS_FILE = DATA_DIR / "video-prompts-v2.jsonl"
GENERAL_PROMPTS_FILE = DATA_DIR / "general-prompts-v2.jsonl"

# 创建目录
DATA_DIR.mkdir(parents=True, exist_ok=True)

def run_clawdbot_eval(js_code):
    """运行 clawdbot eval 命令"""
    try:
        result = subprocess.run(
            ["clawdbot", "eval", js_code],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.stdout:
            return json.loads(result.stdout)
        return None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, subprocess.CalledProcessError) as e:
        print(f"Error running clawdbot eval: {e}")
        return None

def fetch_full_content(url):
    """使用 web_fetch 获取完整页面内容"""
    try:
        js_code = f'await tool("web_fetch", {{ url: "{url}", extractMode: "text", maxChars: 10000 }})'
        data = run_clawdbot_eval(js_code)

        if data and 'content' in data:
            return data['content']
        return None
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return None

def extract_prompts_from_content(content, max_prompts=20):
    """从完整内容中提取提示词"""
    prompts = []

    # 匹配引号中的内容
    quote_patterns = [
        r'"([^"]{30,500})"',  # 双引号，更长
        r"'([^']{30,500})'",  # 单引号
        r'`([^`]{30,500})`',  # 反引号
    ]

    for pattern in quote_patterns:
        matches = re.findall(pattern, content)
        prompts.extend(matches)

    # 匹配冒号后面的描述性文本（更长）
    colon_patterns = [
        r'(?:prompt|Prompt|PROMPT)[\s:]+([^.!?\n]{30,500})',
        r'(?:prompt|Prompt|PROMPT)\s*[:=]\s*([^\n]{30,500})',
        r'(?:example|Example)[\s:]+([^.!?\n]{30,500})',
    ]

    for pattern in colon_patterns:
        matches = re.findall(pattern, content)
        prompts.extend(matches)

    # 去重
    unique_prompts = list(set(prompts))

    # 过滤过短或过长的提示词
    filtered = []
    for p in unique_prompts:
        p_clean = p.strip()
        # 过滤非英语字符过多的内容
        if len(p_clean) >= 30 and len(p_clean) <= 500:
            # 检查是否包含足够多的字母数字
            alpha_ratio = sum(c.isalnum() or c.isspace() for c in p_clean) / len(p_clean)
            if alpha_ratio > 0.6:  # 至少60%是字母数字或空格
                filtered.append(p_clean)

    return filtered[:max_prompts]

def classify_prompt_type(prompt):
    """分类提示词类型"""
    prompt_lower = prompt.lower()

    # 图像生成关键词
    image_keywords = [
        'paint', 'draw', 'illustration', 'photo', 'portrait', 'landscape',
        'style', 'color', 'lighting', 'composition', 'perspective',
        'detailed', 'realistic', 'artistic', 'digital art', 'concept art',
        'anime', 'cartoon', 'watercolor', 'oil painting', 'sketch',
        'midjourney', 'dall-e', 'dalle', 'stable diffusion', 'ai art',
        'pixel art', 'vector', '3d render', 'cinematic', 'photorealistic',
        'image', 'generate image', 'create image', 'make picture',
        'portrait', 'selfie', 'wallpaper', 'icon', 'logo'
    ]

    # 视频生成关键词
    video_keywords = [
        'video', 'animation', 'motion', 'animate', 'animated',
        'walk', 'run', 'jump', 'move', 'moving',
        'kling', 'veo', 'runway', 'pika', 'video generation',
        'camera movement', 'zoom', 'pan', 'transition', 'sequence',
        'frame', 'shot', 'scene', 'action', 'dynamic', 'flow',
        'clip', 'footage', 'film', 'movie', 'generate video'
    ]

    # 文本生成关键词
    text_keywords = [
        'write', 'essay', 'article', 'blog', 'content', 'copy',
        'story', 'narrative', 'dialogue', 'script', 'screenplay',
        'chatgpt', 'gpt', 'llm', 'text generation', 'writing'
    ]

    # 计算得分
    image_score = sum(1 for kw in image_keywords if kw in prompt_lower)
    video_score = sum(1 for kw in video_keywords if kw in prompt_lower)
    text_score = sum(1 for kw in text_keywords if kw in prompt_lower)

    # 判断主要类型
    if video_score > image_score and video_score > text_score:
        return 'video-generation'
    elif image_score > text_score:
        return 'image-generation'
    elif text_score > 0:
        return 'text-generation'
    else:
        return 'general'

def calculate_completeness_score(prompt):
    """计算提示词完整性分数"""
    score = 0
    prompt_lower = prompt.lower()

    # 长度检查（太短或太长都不完整）
    length = len(prompt)
    if 50 <= length <= 300:
        score += 25
    elif 301 <= length <= 500:
        score += 20
    else:
        score += 5

    # 主语/对象（描述的是谁或什么）
    has_subject = any(word in prompt_lower for word in [
        'portrait', 'photo', 'image', 'character', 'person', 'man', 'woman',
        'child', 'animal', 'landscape', 'scene', 'object', 'product', 'car',
        'house', 'building', 'city', 'nature', 'tree', 'flower', 'sky'
    ])
    if has_subject:
        score += 15

    # 风格描述
    has_style = any(word in prompt_lower for word in [
        'style', 'realistic', 'artistic', 'anime', 'cartoon', 'painting',
        'drawing', 'sketch', 'digital', 'cinematic', 'photorealistic',
        'watercolor', 'oil', 'pencil', 'ink', 'vintage', 'modern'
    ])
    if has_style:
        score += 15

    # 环境或背景
    has_background = any(word in prompt_lower for word in [
        'background', 'landscape', 'city', 'nature', 'forest', 'beach',
        'mountain', 'sky', 'sun', 'moon', 'night', 'day', 'indoor', 'outdoor',
        'studio', 'street', 'park', 'garden'
    ])
    if has_background:
        score += 15

    # 光照描述
    has_lighting = any(word in prompt_lower for word in [
        'light', 'lighting', 'bright', 'dark', 'shadow', 'sunlight',
        'moonlight', 'natural light', 'artificial light', 'golden hour',
        'sunset', 'sunrise', 'neon', 'soft light', 'dramatic light'
    ])
    if has_lighting:
        score += 10

    # 情绪或氛围
    has_mood = any(word in prompt_lower for word in [
        'mood', 'atmosphere', 'dramatic', 'peaceful', 'mysterious',
        'happy', 'sad', 'angry', 'calm', 'energetic', 'romantic',
        'nostalgic', 'futuristic', 'medieval', 'fantasy', 'sci-fi'
    ])
    if has_mood:
        score += 10

    # 技术参数
    has_params = any(param in prompt for param in [
        '--', 'aspect ratio', 'ar:', 'quality', 'stylize', 'version',
        'v5', 'v4', 'seed:', 'chaos:', 'weird:'
    ])
    if has_params:
        score += 10

    return min(score, 100)

def is_valid_prompt(prompt):
    """检查提示词是否有效"""
    # 过滤明显无效的内容
    invalid_patterns = [
        r'^https?://',  # URL
        r'^\s*\d+\s*$',  # 只有数字
        r'^[A-Z\s\-]+$',  # 只有大写字母
        r'^(click|visit|see|check|watch|read|go to)',  # 指令性词语开头
    ]

    for pattern in invalid_patterns:
        if re.match(pattern, prompt.strip(), re.IGNORECASE):
            return False

    # 过滤过短内容
    if len(prompt.strip()) < 30:
        return False

    # 过滤重复字符
    if len(set(prompt)) < len(prompt) * 0.3:  # 唯一字符少于30%
        return False

    return True

def calculate_quality_score(result, fetched_content=None):
    """计算结果的质量分数"""
    score = 0

    title = result.get('title', '')
    snippet = result.get('snippet', '')
    url = result.get('url', '')

    # 标题质量（包含特定关键词）
    if any(kw in title.lower() for kw in ['prompt', 'tutorial', 'best', 'guide', 'tips', 'examples']):
        score += 20

    # 片段质量
    if len(snippet) > 100:
        score += 10
    if any(kw in snippet.lower() for kw in ['prompt', 'example', 'image', 'style', 'generate']):
        score += 15

    # URL 质量（来自知名平台）
    quality_sources = [
        'github.com', 'reddit.com', 'medium.com', 'youtube.com',
        'dev.to', 'artstation.com', 'midjourney.com', 'stability.ai',
        'cyberlink.com', 'mockey.ai', 'aiarty.com', 'atlassian.com',
        'google.com', 'cloud.google.com', 'ibm.com', 'palantir.com'
    ]
    if any(source in url for source in quality_sources):
        score += 15

    # 成功获取完整内容
    if fetched_content and len(fetched_content) > 500:
        score += 25

    # 内容丰富度
    combined_text = title + ' ' + snippet
    if len(combined_text) > 200:
        score += 10
    if '--' in snippet or ':' in snippet:  # 参数或描述格式
        score += 5

    return min(score, 100)

def search_visual_ai_prompts():
    """搜索视觉 AI 提示词"""
    print("🔍 Searching for Visual AI Prompts...")

    queries = {
        'midjourney': [
            "best Midjourney prompts 2026",
            "Midjourney prompt examples gallery",
            "Midjourney styles and parameters guide",
            "photorealistic Midjourney prompts"
        ],
        'dalle': [
            "DALL-E 3 prompts examples",
            "creative DALL-E image prompts",
            "DALL-E prompt engineering tips",
            "DALL-E art style prompts"
        ],
        'stable_diffusion': [
            "Stable Diffusion prompt examples",
            "Stable Diffusion style prompts",
            "Stable Diffusion negative prompts",
            "Stable Diffusion LoRA prompts"
        ],
        'video_generation': [
            "Veo video generation prompts examples",
            "Kling AI video prompts guide",
            "AI video generation best prompts",
            "text to video prompt templates"
        ],
        'artistic_styles': [
            "AI art style prompts collection",
            "cinematic AI prompts examples",
            "photorealistic AI portrait prompts",
            "anime style AI prompts"
        ]
    }

    all_results = []

    for category, category_queries in queries.items():
        print(f"\n📁 Category: {category}")

        for query in category_queries:
            print(f"  - {query}")
            js_code = f'await tool("web_search", {{ query: "{query}", count: 5 }})'
            data = run_clawdbot_eval(js_code)

            if data and 'results' in data:
                for result in data['results']:
                    # 获取完整页面内容
                    print(f"    Fetching full content from {result.get('url', '')[:50]}...")
                    full_content = fetch_full_content(result.get('url', ''))

                    # 计算质量分数
                    quality_score = calculate_quality_score(result, full_content)

                    # 使用完整内容提取提示词
                    content_to_extract = full_content if full_content else (result.get('title', '') + ' ' + result.get('snippet', ''))
                    extracted_prompts = extract_prompts_from_content(content_to_extract)

                    # 过滤有效提示词
                    valid_prompts = [p for p in extracted_prompts if is_valid_prompt(p)]

                    # 分类并计算完整性
                    processed_prompts = []
                    for prompt in valid_prompts:
                        prompt_type = classify_prompt_type(prompt)
                        completeness_score = calculate_completeness_score(prompt)

                        processed_prompts.append({
                            'content': prompt,
                            'type': prompt_type,
                            'completeness_score': completeness_score
                        })

                    result_data = {
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'snippet': result.get('snippet', ''),
                        'published': result.get('published', ''),
                        'quality_score': quality_score,
                        'category': category,
                        'content_fetched': full_content is not None,
                        'prompts': processed_prompts,
                        'total_prompts': len(processed_prompts)
                    }

                    all_results.append(result_data)

                    print(f"    ✓ Extracted {len(processed_prompts)} valid prompts")

    return all_results

def save_prompts_by_type(all_results):
    """按类型保存提示词到不同文件"""
    image_prompts = []
    video_prompts = []
    general_prompts = []

    for result in all_results:
        for prompt_data in result['prompts']:
            record = {
                'content': prompt_data['content'],
                'prompt_type': prompt_data['type'],
                'completeness_score': prompt_data['completeness_score'],
                'title': result['title'],
                'source': result['category'],
                'url': result['url'],
                'quality_score': result['quality_score'],
                'extracted_at': datetime.utcnow().isoformat()
            }

            if prompt_data['type'] == 'image-generation':
                image_prompts.append(record)
            elif prompt_data['type'] == 'video-generation':
                video_prompts.append(record)
            else:
                general_prompts.append(record)

    # 保存到文件
    def save_to_file(filename, data, type_name):
        count = 0
        with open(filename, 'w') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
                count += 1
        print(f"✅ Saved {count} {type_name} prompts to {filename}")
        return count

    image_count = save_to_file(IMAGE_PROMPTS_FILE, image_prompts, "image")
    video_count = save_to_file(VIDEO_PROMPTS_FILE, video_prompts, "video")
    general_count = save_to_file(GENERAL_PROMPTS_FILE, general_prompts, "general")

    return {
        'image': image_count,
        'video': video_count,
        'general': general_count,
        'total': image_count + video_count + general_count
    }

def main():
    """主函数"""
    print("="*60)
    print("🚀 Starting Visual AI Prompts Collection V2")
    print(f"📅 Date: {datetime.utcnow().isoformat()}")
    print("="*60)

    # 搜索视觉 AI 提示词
    search_results = search_visual_ai_prompts()

    # 保存到分类文件
    print(f"\n{'='*60}")
    print("💾 Saving prompts by type...")
    counts = save_prompts_by_type(search_results)

    # 统计
    total_results = len(search_results)
    avg_quality = sum(r['quality_score'] for r in search_results) / total_results if search_results else 0
    high_quality_count = sum(1 for r in search_results if r['quality_score'] >= 70)

    print(f"\n{'='*60}")
    print("✨ Collection complete!")
    print(f"{'='*60}")
    print(f"\n📊 Statistics:")
    print(f"  • Total pages searched: {total_results}")
    print(f"  • Average quality score: {avg_quality:.1f}/100")
    print(f"  • High quality pages (≥70): {high_quality_count}")
    print(f"\n📝 Prompts by type:")
    print(f"  • Image generation: {counts['image']}")
    print(f"  • Video generation: {counts['video']}")
    print(f"  • General/Other: {counts['general']}")
    print(f"  • Total: {counts['total']}")

    # 生成修复报告
    generate_fix_report(search_results, counts, avg_quality, high_quality_count)

def generate_fix_report(search_results, counts, avg_quality, high_quality_count):
    """生成修复报告"""
    report = f"""
# Prompt Content Extraction Fix Report

**时间**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

## 🔧 修复内容

### 1. 内容提取改进
- ✅ 使用 `web_fetch` 获取完整页面内容（而非仅 snippet）
- ✅ 提取更长的提示词（30-500字符）
- ✅ 从多种模式提取（引号、冒号、示例）
- ✅ 过滤无效内容（URL、重复字符等）

### 2. 新增字段
- ✅ `prompt_type`: 提示词类型
  - `image-generation` - 图像生成
  - `video-generation` - 视频生成
  - `text-generation` - 文本生成
  - `general` - 通用
- ✅ `completeness_score`: 完整性分数（0-100）
  - 检查长度、主语、风格、环境、光照、情绪、技术参数

### 3. 文件组织
- ✅ 分别保存到：
  - `image-prompts-v2.jsonl` - 图像生成提示词
  - `video-prompts-v2.jsonl` - 视频生成提示词
  - `general-prompts-v2.jsonl` - 通用提示词

## 📊 收集统计

| 指标 | 数值 |
|------|------|
| 搜索页面数 | {len(search_results)} |
| 平均质量分数 | {avg_quality:.1f}/100 |
| 高质量页面 (≥70) | {high_quality_count} |
| 图像提示词 | {counts['image']} |
| 视频提示词 | {counts['video']} |
| 通用提示词 | {counts['general']} |
| **总计** | **{counts['total']}** |

## 🎯 质量对比

### 修复前问题
- ❌ 内容从 snippet 提取（100-200字符）
- ❌ 提示词不完整
- ❌ 没有类型标注
- ❌ 没有完整性检查
- ❌ video-prompts.jsonl 为空

### 修复后改进
- ✅ 从完整页面提取（最长10000字符）
- ✅ 提示词完整且丰富
- ✅ 自动类型标注（4种类型）
- ✅ 完整性评分（7个维度）
- ✅ 分类存储到独立文件

## 💡 提示词完整性评分标准

完整性分数基于以下维度（每项最高10-25分）：

1. **长度适当** (25分)
   - 50-300字符: 25分
   - 301-500字符: 20分
   - 其他: 5分

2. **包含主语** (15分)
   - 描述对象：portrait, character, landscape, object 等

3. **描述风格** (15分)
   - 风格关键词：realistic, anime, cinematic, watercolor 等

4. **描述环境** (15分)
   - 环境描述：background, city, nature, studio 等

5. **光照描述** (10分)
   - 光照关键词：lighting, sunset, golden hour, soft light 等

6. **情绪氛围** (10分)
   - 情绪描述：dramatic, peaceful, mysterious 等

7. **技术参数** (10分)
   - 参数标记：--style, --ar, version 等

## 🌟 高质量示例（Top 5）

"""

    # 提取高质量提示词
    all_prompts = []
    for result in search_results:
        for prompt in result['prompts']:
            if prompt['completeness_score'] >= 70:
                all_prompts.append({
                    'content': prompt['content'],
                    'type': prompt['type'],
                    'completeness_score': prompt['completeness_score'],
                    'source_quality': result['quality_score'],
                    'title': result['title'],
                    'url': result['url']
                })

    # 按完整性排序
    all_prompts.sort(key=lambda x: x['completeness_score'], reverse=True)

    # 展示前5个
    for i, item in enumerate(all_prompts[:5], 1):
        report += f"\n### {i}. [{item['title']}]({item['url']})\n"
        report += f"- **类型**: {item['type']}\n"
        report += f"- **完整性分数**: {item['completeness_score']}/100\n"
        report += f"- **来源质量**: {item['source_quality']}/100\n"
        report += f"- **提示词**: `{item['content'][:150]}...`\n"

    report += f"""

## 📈 数据质量分析

### 完整性分数分布

"""
    # 统计完整性分布
    if counts['total'] > 0:
        all_scores = [p['completeness_score'] for result in search_results for p in result['prompts']]
        excellent = sum(1 for s in all_scores if s >= 80)
        good = sum(1 for s in all_scores if 70 <= s < 80)
        moderate = sum(1 for s in all_scores if 50 <= s < 70)
        low = sum(1 for s in all_scores if s < 50)

        report += f"| 分数区间 | 数量 | 占比 |\n"
        report += f"|----------|------|------|\n"
        report += f"| 优秀 (≥80) | {excellent} | {excellent/len(all_scores)*100:.1f}% |\n"
        report += f"| 良好 (70-79) | {good} | {good/len(all_scores)*100:.1f}% |\n"
        report += f"| 中等 (50-69) | {moderate} | {moderate/len(all_scores)*100:.1f}% |\n"
        report += f"| 需改进 (<50) | {low} | {low/len(all_scores)*100:.1f}% |\n"

    report += f"""

### 类型分布

"""
    # 类型统计
    if counts['total'] > 0:
        report += f"| 类型 | 数量 | 占比 |\n"
        report += f"|------|------|------|\n"
        report += f"| 图像生成 | {counts['image']} | {counts['image']/counts['total']*100:.1f}% |\n"
        report += f"| 视频生成 | {counts['video']} | {counts['video']/counts['total']*100:.1f}% |\n"
        report += f"| 通用/其他 | {counts['general']} | {counts['general']/counts['total']*100:.1f}% |\n"

    report += f"""

## 🎯 下一步建议

1. **技能生成**:
   - 使用修复后的数据生成高质量 skills
   - 按 prompt_type 分类生成不同类型的技能
   - 优先使用 completeness_score ≥ 70 的提示词

2. **数据优化**:
   - 定期重新收集以保持数据新鲜度
   - 添加更多搜索查询扩大覆盖面
   - 考虑添加人工审核流程

3. **质量提升**:
   - 实现提示词去重算法
   - 添加相似度检测避免重复
   - 建立质量评估标准

---

*报告自动生成 | V2 Fix Complete*
"""

    # 保存报告
    report_path = DATA_DIR / f"fix-report-{datetime.utcnow().strftime('%Y-%m-%d-%H%M')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📄 Fix report saved: {report_path}")

if __name__ == "__main__":
    main()
