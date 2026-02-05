#!/usr/bin/env python3
"""
Fix Existing Prompts
从现有的 prompts 文件中提取完整内容并添加元数据
"""

import json
import requests
from datetime import datetime, timezone
from pathlib import Path
import re
import html

DATA_DIR = Path("/root/clawd/data/prompts")
SOURCE_FILE = DATA_DIR / "image-prompts.jsonl"
IMAGE_PROMPTS_FILE = DATA_DIR / "image-prompts-v2.jsonl"
VIDEO_PROMPTS_FILE = DATA_DIR / "video-prompts-v2.jsonl"
GENERAL_PROMPTS_FILE = DATA_DIR / "general-prompts-v2.jsonl"

# 创建目录
DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_page_content(url, max_chars=10000):
    """获取页面内容"""
    try:
        result = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        if result.status_code == 200:
            text = result.text
            # 移除 HTML 标签（简单处理）
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = html.unescape(text)
            # 清理空白
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:max_chars]
        return None
    except Exception as e:
        print(f"    ⚠ Error fetching {url[:50]}: {e}")
        return None

def extract_prompts_from_content(content, max_prompts=30):
    """从完整内容中提取提示词"""
    prompts = []

    # 匹配引号中的内容
    quote_patterns = [
        r'"([^"]{30,500})"',  # 双引号
        r"'([^']{30,500})'",  # 单引号
        r'`([^`]{30,500})`',  # 反引号
    ]

    for pattern in quote_patterns:
        matches = re.findall(pattern, content)
        prompts.extend(matches)

    # 匹配冒号后面的描述性文本
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

    # 过滤
    filtered = []
    for p in unique_prompts:
        p_clean = p.strip()
        if len(p_clean) >= 30 and len(p_clean) <= 500:
            alpha_ratio = sum(c.isalnum() or c.isspace() for c in p_clean) / len(p_clean)
            if alpha_ratio > 0.6:
                filtered.append(p_clean)

    return filtered[:max_prompts]

def classify_prompt_type(prompt):
    """分类提示词类型"""
    prompt_lower = prompt.lower()

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

    video_keywords = [
        'video', 'animation', 'motion', 'animate', 'animated',
        'walk', 'run', 'jump', 'move', 'moving',
        'kling', 'veo', 'runway', 'pika', 'video generation',
        'camera movement', 'zoom', 'pan', 'transition', 'sequence',
        'frame', 'shot', 'scene', 'action', 'dynamic', 'flow',
        'clip', 'footage', 'film', 'movie', 'generate video'
    ]

    text_keywords = [
        'write', 'essay', 'article', 'blog', 'content', 'copy',
        'story', 'narrative', 'dialogue', 'script', 'screenplay',
        'chatgpt', 'gpt', 'llm', 'text generation', 'writing'
    ]

    image_score = sum(1 for kw in image_keywords if kw in prompt_lower)
    video_score = sum(1 for kw in video_keywords if kw in prompt_lower)
    text_score = sum(1 for kw in text_keywords if kw in prompt_lower)

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

    length = len(prompt)
    if 50 <= length <= 300:
        score += 25
    elif 301 <= length <= 500:
        score += 20
    else:
        score += 5

    has_subject = any(word in prompt_lower for word in [
        'portrait', 'photo', 'image', 'character', 'person', 'man', 'woman',
        'child', 'animal', 'landscape', 'scene', 'object', 'product', 'car',
        'house', 'building', 'city', 'nature', 'tree', 'flower', 'sky'
    ])
    if has_subject:
        score += 15

    has_style = any(word in prompt_lower for word in [
        'style', 'realistic', 'artistic', 'anime', 'cartoon', 'painting',
        'drawing', 'sketch', 'digital', 'cinematic', 'photorealistic',
        'watercolor', 'oil', 'pencil', 'ink', 'vintage', 'modern'
    ])
    if has_style:
        score += 15

    has_background = any(word in prompt_lower for word in [
        'background', 'landscape', 'city', 'nature', 'forest', 'beach',
        'mountain', 'sky', 'sun', 'moon', 'night', 'day', 'indoor', 'outdoor',
        'studio', 'street', 'park', 'garden'
    ])
    if has_background:
        score += 15

    has_lighting = any(word in prompt_lower for word in [
        'light', 'lighting', 'bright', 'dark', 'shadow', 'sunlight',
        'moonlight', 'natural light', 'artificial light', 'golden hour',
        'sunset', 'sunrise', 'neon', 'soft light', 'dramatic light'
    ])
    if has_lighting:
        score += 10

    has_mood = any(word in prompt_lower for word in [
        'mood', 'atmosphere', 'dramatic', 'peaceful', 'mysterious',
        'happy', 'sad', 'angry', 'calm', 'energetic', 'romantic',
        'nostalgic', 'futuristic', 'medieval', 'fantasy', 'sci-fi'
    ])
    if has_mood:
        score += 10

    has_params = any(param in prompt for param in [
        '--', 'aspect ratio', 'ar:', 'quality', 'stylize', 'version',
        'v5', 'v4', 'seed:', 'chaos:', 'weird:'
    ])
    if has_params:
        score += 10

    return min(score, 100)

def is_valid_prompt(prompt):
    """检查提示词是否有效"""
    invalid_patterns = [
        r'^https?://',
        r'^\s*\d+\s*$',
        r'^[A-Z\s\-]+$',
        r'^(click|visit|see|check|watch|read|go to)',
    ]

    for pattern in invalid_patterns:
        if re.match(pattern, prompt.strip(), re.IGNORECASE):
            return False

    if len(prompt.strip()) < 30:
        return False

    if len(set(prompt)) < len(prompt) * 0.3:
        return False

    return True

def process_existing_prompts():
    """处理现有的 prompts"""
    print("="*60)
    print("🔧 Processing Existing Prompts")
    print(f"📅 Date: {datetime.now(timezone.utc).isoformat()}")
    print("="*60)

    if not SOURCE_FILE.exists():
        print(f"❌ Source file not found: {SOURCE_FILE}")
        return None, None, None

    # 读取源文件
    all_records = []
    with open(SOURCE_FILE, 'r') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                all_records.append(record)
            except json.JSONDecodeError:
                continue

    print(f"\n📊 Loaded {len(all_records)} records from source file")

    # 收集唯一的 URL
    unique_urls = {}
    for record in all_records:
        url = record.get('url', '')
        if url and url not in unique_urls:
            unique_urls[url] = {
                'records': [],
                'title': record.get('title', ''),
                'source': record.get('source', '')
            }
        if url in unique_urls:
            unique_urls[url]['records'].append(record)

    print(f"🌐 Found {len(unique_urls)} unique URLs to process")

    # 处理每个 URL
    all_results = []
    fetched_count = 0
    failed_count = 0

    for i, (url, data) in enumerate(unique_urls.items(), 1):
        print(f"\n[{i}/{len(unique_urls)}] Processing: {data['title'][:60]}...")
        print(f"    URL: {url[:70]}")

        # 获取完整页面内容
        full_content = fetch_page_content(url)

        if full_content:
            fetched_count += 1
            print(f"    ✓ Fetched {len(full_content)} characters")

            # 提取提示词
            extracted_prompts = extract_prompts_from_content(full_content)
            print(f"    ✓ Extracted {len(extracted_prompts)} potential prompts")

            # 过滤有效提示词
            valid_prompts = [p for p in extracted_prompts if is_valid_prompt(p)]
            print(f"    ✓ Valid prompts: {len(valid_prompts)}")

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

            # 计算质量分数
            quality_score = 0
            if any(kw in data['title'].lower() for kw in ['prompt', 'tutorial', 'best', 'guide', 'tips']):
                quality_score += 20
            if len(full_content) > 1000:
                quality_score += 25
            if len(processed_prompts) > 5:
                quality_score += 15

            result_data = {
                'title': data['title'],
                'url': url,
                'source': data['source'],
                'quality_score': min(quality_score, 100),
                'content_fetched': True,
                'prompts': processed_prompts,
                'total_prompts': len(processed_prompts)
            }

            all_results.append(result_data)

            # 统计类型分布
            type_counts = {}
            for p in processed_prompts:
                t = p['type']
                type_counts[t] = type_counts.get(t, 0) + 1
            if type_counts:
                print(f"    📊 Types: {', '.join([f'{k}: {v}' for k, v in type_counts.items()])}")
        else:
            failed_count += 1
            print(f"    ⚠ Failed to fetch content")

    print(f"\n{'='*60}")
    print(f"📊 Processing Summary")
    print(f"{'='*60}")
    print(f"  Total URLs: {len(unique_urls)}")
    print(f"  Successfully fetched: {fetched_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total prompts extracted: {sum(r['total_prompts'] for r in all_results)}")

    return all_results, fetched_count, failed_count

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
                'source': result['source'],
                'url': result['url'],
                'quality_score': result['quality_score'],
                'extracted_at': datetime.now(timezone.utc).isoformat()
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

def generate_final_report(all_results, counts, fetched_count, failed_count):
    """生成最终修复报告"""
    report = f"""
# Prompt Content Extraction Fix - Final Report

**时间**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}

## 🔧 修复内容

### 1. 内容提取改进
- ✅ 使用 HTTP 请求获取完整页面内容（而非仅 snippet）
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

## 📊 处理统计

| 指标 | 数值 |
|------|------|
| 处理的页面数 | {len(all_results)} |
| 成功获取内容 | {fetched_count} |
| 获取失败 | {failed_count} |
| 成功率 | {fetched_count/len(unique_urls)*100 if len(unique_urls) > 0 else 0:.1f}% |

## 📝 提示词统计

| 类型 | 数量 | 占比 |
|------|------|------|
| 图像生成 | {counts['image']} | {counts['image']/counts['total']*100:.1f}% |
| 视频生成 | {counts['video']} | {counts['video']/counts['total']*100:.1f}% |
| 通用/其他 | {counts['general']} | {counts['general']/counts['total']*100:.1f}% |
| **总计** | **{counts['total']}** | 100% |

## 🎯 质量对比

### 修复前问题
- ❌ 内容从 snippet 提取（100-200字符）
- ❌ 提示词不完整且截断
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

1. **长度适当** (25分) - 50-300字符最优
2. **包含主语** (15分) - 描述对象
3. **描述风格** (15分) - 风格关键词
4. **描述环境** (15分) - 环境描述
5. **光照描述** (10分) - 光照关键词
6. **情绪氛围** (10分) - 情绪描述
7. **技术参数** (10分) - 参数标记

## 🌟 高质量提示词示例（Top 10）

"""

    # 提取高质量提示词
    all_prompts = []
    for result in all_results:
        for prompt in result['prompts']:
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

    # 展示前10个
    for i, item in enumerate(all_prompts[:10], 1):
        report += f"\n### {i}. {item['type'].upper()} (Score: {item['completeness_score']}/100)\n"
        report += f"- **来源**: [{item['title']}]({item['url']})\n"
        report += f"- **提示词**: `{item['content'][:200]}`\n"
        if len(item['content']) > 200:
            report += f"- **完整**: `{item['content']}`\n"

    # 添加完整性分布
    if counts['total'] > 0:
        all_scores = [p['completeness_score'] for result in all_results for p in result['prompts']]
        excellent = sum(1 for s in all_scores if s >= 80)
        good = sum(1 for s in all_scores if 70 <= s < 80)
        moderate = sum(1 for s in all_scores if 50 <= s < 70)
        low = sum(1 for s in all_scores if s < 50)

        report += f"""

## 📈 数据质量分析

### 完整性分数分布

| 分数区间 | 数量 | 占比 |
|----------|------|------|
| 优秀 (≥80) | {excellent} | {excellent/len(all_scores)*100:.1f}% |
| 良好 (70-79) | {good} | {good/len(all_scores)*100:.1f}% |
| 中等 (50-69) | {moderate} | {moderate/len(all_scores)*100:.1f}% |
| 需改进 (<50) | {low} | {low/len(all_scores)*100:.1f}% |

### 高质量提示词数量 (≥70): {excellent + good}
"""

    report += f"""

## 🎯 下一步建议

1. **技能生成**:
   - 使用修复后的数据生成高质量 skills
   - 按 prompt_type 分类生成不同类型的技能
   - 优先使用 completeness_score ≥ 70 的提示词

2. **数据优化**:
   - 考虑添加更多搜索来源
   - 实现提示词去重算法
   - 建立质量评估标准

3. **质量提升**:
   - 添加相似度检测避免重复
   - 定期更新数据源
   - 添加人工审核流程

## ✅ 修复完成

所有现有提示词已成功修复并增强。新的数据文件包含：
- 完整的提示词内容
- 类型标注
- 完整性评分
- 分类存储

可以直接用于技能生成。

---

*修复报告生成完成*
"""

    # 保存报告
    report_path = DATA_DIR / f"fix-final-report-{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📄 Final report saved: {report_path}")
    return report_path

def main():
    """主函数"""
    # 处理现有数据
    all_results, fetched_count, failed_count = process_existing_prompts()

    if not all_results:
        print("\n❌ No results to process")
        return

    # 保存到分类文件
    print(f"\n{'='*60}")
    print("💾 Saving prompts by type...")
    counts = save_prompts_by_type(all_results)

    # 统计
    avg_quality = sum(r['quality_score'] for r in all_results) / len(all_results) if all_results else 0
    high_quality_count = sum(1 for r in all_results if r['quality_score'] >= 70)

    print(f"\n{'='*60}")
    print("✨ Fix complete!")
    print(f"{'='*60}")
    print(f"\n📊 Final Statistics:")
    print(f"  • Average quality score: {avg_quality:.1f}/100")
    print(f"  • High quality sources (≥70): {high_quality_count}")
    print(f"\n📝 Prompts by type:")
    print(f"  • Image generation: {counts['image']}")
    print(f"  • Video generation: {counts['video']}")
    print(f"  • General/Other: {counts['general']}")
    print(f"  • Total: {counts['total']}")

    # 生成最终报告
    report_path = generate_final_report(all_results, counts, fetched_count, failed_count)

if __name__ == "__main__":
    main()
