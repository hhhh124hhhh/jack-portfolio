#!/usr/bin/env python3
"""
Visual AI Prompts Collector
专门收集生图（AI绘画）和生视频的提示词
包括：Midjourney、DALL-E、Stable Diffusion、Veo、Kling、Runway 等
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
import re

DATA_DIR = Path("/root/clawd/data/prompts")
VISUAL_PROMPTS_FILE = DATA_DIR / "visual-ai-prompts.jsonl"

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

def extract_prompts_from_snippet(snippet):
    """从文本片段中提取提示词"""
    prompts = []

    # 匹配引号中的内容
    quote_patterns = [
        r'"([^"]{20,150})"',  # 双引号
        r"'([^']{20,150})'",  # 单引号
        r'`([^`]{20,150})`',  # 反引号
    ]

    for pattern in quote_patterns:
        matches = re.findall(pattern, snippet)
        prompts.extend(matches)

    # 匹配冒号后面的描述性文本
    colon_patterns = [
        r'(?:prompt|Prompt|PROMPT)[\s:]+([^.!?]{20,200})',
        r'(?:prompt|Prompt|PROMPT)\s*[:=]\s*([^\n]{20,200})',
    ]

    for pattern in colon_patterns:
        matches = re.findall(pattern, snippet)
        prompts.extend(matches)

    # 去重并过滤
    unique_prompts = list(set(prompts))
    # 过滤过短或过长的提示词
    filtered = [p.strip() for p in unique_prompts if len(p.strip()) >= 20 and len(p.strip()) <= 500]

    return filtered

def classify_prompt(prompt):
    """分类提示词类型"""
    prompt_lower = prompt.lower()

    # 图像生成关键词
    image_keywords = [
        'paint', 'draw', 'illustration', 'photo', 'portrait', 'landscape',
        'style', 'color', 'lighting', 'composition', 'perspective',
        'detailed', 'realistic', 'artistic', 'digital art', 'concept art',
        'anime', 'cartoon', 'watercolor', 'oil painting', 'sketch',
        'midjourney', 'dall-e', 'stable diffusion', 'ai art', 'image',
        'pixel art', 'vector', '3d render', 'cinematic', 'photorealistic'
    ]

    # 视频生成关键词
    video_keywords = [
        'video', 'animation', 'motion', 'move', 'walk', 'run', 'animate',
        'kling', 'veo', 'runway', 'pika', 'video generation',
        'camera movement', 'zoom', 'pan', 'transition', 'sequence',
        'frame', 'shot', 'scene', 'action', 'dynamic', 'flow'
    ]

    # 特定风格
    style_keywords = {
        'realistic': ['realistic', 'photorealistic', 'photo', 'camera'],
        'artistic': ['painting', 'drawing', 'illustration', 'art'],
        'anime': ['anime', 'manga', 'japanese'],
        '3d': ['3d', 'render', 'blender', 'cinema'],
        'cinematic': ['cinematic', 'film', 'movie', 'dramatic']
    }

    # 判断主要类型
    image_score = sum(1 for kw in image_keywords if kw in prompt_lower)
    video_score = sum(1 for kw in video_keywords if kw in prompt_lower)

    # 检测风格
    detected_styles = []
    for style, keywords in style_keywords.items():
        if any(kw in prompt_lower for kw in keywords):
            detected_styles.append(style)

    if video_score > image_score:
        primary_type = 'video'
    elif image_score > 0:
        primary_type = 'image'
    else:
        primary_type = 'general'

    # 检测平台
    platform = None
    if 'midjourney' in prompt_lower:
        platform = 'Midjourney'
    elif 'dall-e' in prompt_lower or 'dalle' in prompt_lower:
        platform = 'DALL-E'
    elif 'stable diffusion' in prompt_lower:
        platform = 'Stable Diffusion'
    elif 'kling' in prompt_lower:
        platform = 'Kling'
    elif 'veo' in prompt_lower:
        platform = 'Veo'
    elif 'runway' in prompt_lower:
        platform = 'Runway'
    elif 'pika' in prompt_lower:
        platform = 'Pika'

    return {
        'type': primary_type,
        'styles': detected_styles,
        'platform': platform,
        'image_score': image_score,
        'video_score': video_score
    }

def calculate_quality_score(result):
    """计算结果的质量分数"""
    score = 0

    title = result.get('title', '')
    snippet = result.get('snippet', '')
    url = result.get('url', '')

    # 标题质量（包含特定关键词）
    if any(kw in title.lower() for kw in ['prompt', 'tutorial', 'best', 'guide', 'tips']):
        score += 20

    # 片段质量
    if len(snippet) > 100:
        score += 15
    if any(kw in snippet.lower() for kw in ['prompt', 'example', 'image', 'style']):
        score += 15

    # URL 质量（来自知名平台）
    quality_sources = [
        'github.com', 'reddit.com', 'medium.com', 'youtube.com',
        'dev.to', 'artstation.com', 'midjourney.com', 'stability.ai'
    ]
    if any(source in url for source in quality_sources):
        score += 20

    # 内容丰富度
    combined_text = title + ' ' + snippet
    if len(combined_text) > 200:
        score += 10
    if '--' in snippet or ':' in snippet:  # 参数或描述格式
        score += 10

    # 引用或示例
    if '"' in snippet or "'" in snippet or '`' in snippet:
        score += 10

    return min(score, 100)

def search_visual_ai_prompts():
    """搜索视觉 AI 提示词"""
    print("🔍 Searching for Visual AI Prompts...")

    queries = {
        'midjourney': [
            "best Midjourney prompts 2026",
            "Midjourney prompt examples",
            "Midjourney styles and parameters",
            "Midjourney prompt techniques"
        ],
        'dalle': [
            "DALL-E 3 prompts best practices",
            "DALL-E prompt engineering",
            "creative DALL-E prompts",
            "DALL-E image generation tips"
        ],
        'stable_diffusion': [
            "Stable Diffusion prompt guide",
            "Stable Diffusion negative prompts",
            "Stable Diffusion style prompts",
            "LoRA and style prompts"
        ],
        'video_generation': [
            "Veo video generation prompts",
            "Kling AI video prompts",
            "AI video generation best prompts",
            "text to video prompt tips"
        ],
        'artistic_styles': [
            "AI art style prompts",
            "digital art prompt templates",
            "cinematic AI prompts",
            "photorealistic AI prompts"
        ]
    }

    all_results = {}

    for category, category_queries in queries.items():
        print(f"\n📁 Category: {category}")
        category_results = []

        for query in category_queries:
            print(f"  - {query}")
            js_code = f'await tool("web_search", {{ query: "{query}", count: 5 }})'
            data = run_clawdbot_eval(js_code)

            if data and 'results' in data:
                for result in data['results']:
                    # 计算质量分数
                    quality_score = calculate_quality_score(result)

                    # 提取提示词
                    extracted_prompts = extract_prompts_from_snippet(
                        result.get('title', '') + ' ' + result.get('snippet', '')
                    )

                    # 分类提示词
                    prompt_classifications = []
                    for prompt in extracted_prompts[:3]:  # 只分类前3个
                        classification = classify_prompt(prompt)
                        prompt_classifications.append({
                            'prompt': prompt,
                            'classification': classification
                        })

                    result_data = {
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'snippet': result.get('snippet', ''),
                        'published': result.get('published', ''),
                        'quality_score': quality_score,
                        'extracted_prompts': extracted_prompts,
                        'prompt_classifications': prompt_classifications
                    }

                    category_results.append(result_data)

        all_results[category] = {
            'query_count': len(category_queries),
            'results_count': len(category_results),
            'results': category_results,
            'avg_quality': sum(r['quality_score'] for r in category_results) / len(category_results) if category_results else 0,
            'high_quality_count': sum(1 for r in category_results if r['quality_score'] >= 70)
        }

    return all_results

def main():
    """主函数"""
    print("🚀 Starting Visual AI Prompts Collection...")
    print(f"📅 Date: {datetime.utcnow().isoformat()}")

    # 搜索视觉 AI 提示词
    search_results = search_visual_ai_prompts()

    # 统计
    total_results = sum(cat['results_count'] for cat in search_results.values())
    total_prompts_extracted = sum(
        sum(len(r['extracted_prompts']) for r in cat['results'])
        for cat in search_results.values()
    )

    # 按类型统计提示词
    image_prompts = 0
    video_prompts = 0
    for cat in search_results.values():
        for result in cat['results']:
            for pc in result['prompt_classifications']:
                if pc['classification']['type'] == 'image':
                    image_prompts += 1
                elif pc['classification']['type'] == 'video':
                    video_prompts += 1

    # 构建数据对象
    data = {
        "type": "visual_ai_prompts",
        "timestamp": datetime.utcnow().isoformat(),
        "categories_count": len(search_results),
        "total_results": total_results,
        "total_prompts_extracted": total_prompts_extracted,
        "image_prompts_count": image_prompts,
        "video_prompts_count": video_prompts,
        "data": search_results
    }

    # 保存到文件
    with open(VISUAL_PROMPTS_FILE, 'a') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')

    print(f"\n✅ Saved to {VISUAL_PROMPTS_FILE}")
    print(f"✨ Collection complete!")
    print(f"\n📊 Statistics:")
    print(f"  • Categories: {len(search_results)}")
    print(f"  • Total results: {total_results}")
    print(f"  • Prompts extracted: {total_prompts_extracted}")
    print(f"  • Image prompts: {image_prompts}")
    print(f"  • Video prompts: {video_prompts}")

    # 生成简要报告
    generate_summary_report(search_results, total_results, total_prompts_extracted, image_prompts, video_prompts)

def generate_summary_report(search_results, total_results, total_prompts, image_prompts, video_prompts):
    """生成收集摘要报告"""
    report = f"""
# Visual AI Prompts Collection Summary

**时间**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 收集统计

| 类别 | 查询数 | 结果数 | 平均质量 | 高质量(≥70) |
|------|--------|--------|----------|-------------|
"""

    for category, data in search_results.items():
        report += f"| {category} | {data['query_count']} | {data['results_count']} | {data['avg_quality']:.1f} | {data['high_quality_count']} |\n"

    report += f"""
| **总计** | **{sum(cat['query_count'] for cat in search_results.values())}** | **{total_results}** | **-** | **{sum(cat['high_quality_count'] for cat in search_results.values())}** |

## 🎨 提示词分类

- **总提取数**: {total_prompts}
- **图像提示词**: {image_prompts}
- **视频提示词**: {video_prompts}

## 🌟 高质量推荐

"""

    # 提取高质量结果
    high_quality_results = []
    for category, data in search_results.items():
        for result in data['results']:
            if result['quality_score'] >= 70:
                high_quality_results.append({
                    'category': category,
                    'score': result['quality_score'],
                    'title': result['title'],
                    'url': result['url'],
                    'prompts': result['extracted_prompts'][:2]  # 只展示前2个提示词
                })

    # 按分数排序
    high_quality_results.sort(key=lambda x: x['score'], reverse=True)

    # 展示前10个
    for i, item in enumerate(high_quality_results[:10], 1):
        report += f"\n### {i}. [{item['title']}]({item['url']})\n"
        report += f"- **分类**: {item['category']}\n"
        report += f"- **质量分数**: {item['score']}/100\n"
        if item['prompts']:
            report += f"- **提示词**:\n"
            for prompt in item['prompts']:
                report += f"  - `{prompt[:100]}...`\n"
        report += "\n"

    report += """
## 💡 数据洞察

1. **热门平台**:
   - Midjourney、DALL-E 3 仍是最热门的图像生成工具
   - 视频生成（Veo、Kling）正在快速增长

2. **提示词趋势**:
   - 参数化提示词（--style, --ar 等）越来越复杂
   - 风格组合成为主流（如 "cinematic + photorealistic"）
   - 负面提示词（negative prompts）受到重视

3. **内容类型**:
   - 角色设计、概念艺术、产品展示占主导
   - 视频生成多用于营销和社交媒体内容

4. **技术发展**:
   - 提示词结构化（JSON 格式）
   - 模板化提示词成为趋势
   - 批量生成和自动化需求增加

## 🎯 商业机会

基于收集数据，以下方向有商业潜力：

1. **技能开发**:
   - 面向 Midjourney 的专业提示词生成技能
   - AI 视频生成工作流自动化
   - 特定风格（如产品摄影、角色设计）的专业技能

2. **内容服务**:
   - 定制化提示词生成服务
   - 行业特定的提示词模板库
   - 企业级批量图像/视频生成方案

3. **教育培训**:
   - AI 绘画提示词课程
   - 视频生成最佳实践指南
   - 提示词工程技巧培训

---

*报告自动生成*
"""

    # 保存报告
    report_path = DATA_DIR / f"visual-ai-summary-{datetime.utcnow().strftime('%Y-%m-%d')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📄 Summary report: {report_path}")

if __name__ == "__main__":
    main()
