#!/usr/bin/env python3
"""
收集 AI 生图和生视频 Prompts
"""

import requests
import json
from datetime import datetime

# 配置
SEARXNG_URL = "http://localhost:8080"
OUTPUT_DIR = "/root/clawd/data/prompts"
IMAGE_OUTPUT = f"{OUTPUT_DIR}/image-prompts.jsonl"
VIDEO_OUTPUT = f"{OUTPUT_DIR}/video-prompts.jsonl"

# 搜索查询
IMAGE_QUERIES = [
    "midjourney prompt template",
    "dalle prompt generator",
    "stable diffusion prompt",
    "leonardo ai prompt",
    "firefly ai prompt",
    "starryai prompt",
    "playgroundai prompt",
    "AI 绘图提示词大全",
    "AI 绘图指令"
]

VIDEO_QUERIES = [
    "kling ai prompt",
    "runway video prompt",
    "pika labs prompt",
    "sora prompt",
    "AI 视频生成",
    "AI 做视频指令"
]

def search_searxng(query, limit=30):
    """使用 SearXNG 搜索"""
    try:
        params = {
            'q': query,
            'engines': ['google', 'bing', 'duckduckgo', 'github'],
            'format': 'json',
            'categories': ['general', 'science', 'technology'],
            'limit': limit
        }
        response = requests.get(f"{SEARXNG_URL}/search", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])
    except Exception as e:
        print(f"  ⚠️  搜索 '{query}' 失败: {e}")
        return []

def extract_prompt_from_content(content):
    """从内容中提取 prompt"""
    if not content:
        return ""
    
    # 简单清理
    prompt = content.strip()
    
    # 限制长度
    if len(prompt) > 2000:
        prompt = prompt[:2000] + "..."
    
    return prompt

def categorize_prompt(content, query):
    """分类 prompt 类型"""
    text = (content + " " + query).lower()
    
    # 生图相关
    image_keywords = ['image', 'midjourney', 'dalle', 'stable diffusion', 
                    'leonardo', 'firefly', 'starryai', '绘图', '画图', '图片']
    if any(kw in text for kw in image_keywords):
        return "image"
    
    # 生视频相关
    video_keywords = ['video', 'kling', 'runway', 'pika', 'sora', 
                    '视频', '做视频', '生成视频', 'runwayml']
    if any(kw in text for kw in video_keywords):
        return "video"
    
    # 默认为 general
    return "general"

def calculate_quality_score(result):
    """计算质量分数（0-100）"""
    score = 0
    
    content = result.get('content', '')
    title = result.get('title', '')
    url = result.get('url', '')
    
    # 内容长度评分
    if len(content) > 500:
        score += 20
    elif len(content) > 200:
        score += 10
    
    # 标题质量
    if len(title) > 20:
        score += 10
    elif len(title) > 10:
        score += 5
    
    # 是否包含 prompt 相关关键词
    prompt_keywords = ['prompt', '提示词', 'template', '模板', 'instruction', '指令']
    text = title.lower() + " " + content.lower()
    for keyword in prompt_keywords:
        if keyword in text:
            score += 15
            break
    
    # 来源评分
    source = result.get('source', '').lower()
    if 'github' in source or 'reddit' in source:
        score += 10
    elif 'medium' in source or 'dev.to' in source:
        score += 5
    
    return min(100, score)

def main():
    print("=" * 80)
    print("🔍 收集 AI 生图和生视频 Prompts")
    print("=" * 80)
    print()
    
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_results = []
    
    # 1. 搜索生图 Prompts
    print("[1/2] 搜索生图 Prompts...")
    for i, query in enumerate(IMAGE_QUERIES):
        print(f"  [{i+1}/{len(IMAGE_QUERIES)}] {query}...", end='', flush=True)
        
        results = search_searxng(query, limit=20)
        
        print(f" 找到 {len(results)} 个结果")
        
        for result in results:
            result['prompt_type'] = categorize_prompt(result.get('content', ''), query)
            result['quality_score'] = calculate_quality_score(result)
            all_results.append(result)
    
    print(f"  ✓ 生图 Prompts: {sum(1 for r in all_results if r.get('prompt_type') == 'image')} 条")
    print()
    
    # 2. 搜索生视频 Prompts
    print("[2/2] 搜索生视频 Prompts...")
    for i, query in enumerate(VIDEO_QUERIES):
        print(f"  [{i+1}/{len(VIDEO_QUERIES)}] {query}...", end='', flush=True)
        
        results = search_searxng(query, limit=20)
        
        print(f" 找到 {len(results)} 个结果")
        
        for result in results:
            result['prompt_type'] = categorize_prompt(result.get('content', ''), query)
            result['quality_score'] = calculate_quality_score(result)
            all_results.append(result)
    
    print(f"  ✓ 生视频 Prompts: {sum(1 for r in all_results if r.get('prompt_type') == 'video')} 条")
    print()
    
    # 3. 保存数据
    print("💾 保存数据...")
    
    image_prompts = [r for r in all_results if r.get('prompt_type') == 'image']
    video_prompts = [r for r in all_results if r.get('prompt_type') == 'video']
    
    with open(IMAGE_OUTPUT, 'w', encoding='utf-8') as f:
        for prompt in image_prompts:
            f.write(json.dumps(prompt, ensure_ascii=False) + '\n')
    
    with open(VIDEO_OUTPUT, 'w', encoding='utf-8') as f:
        for prompt in video_prompts:
            f.write(json.dumps(prompt, ensure_ascii=False) + '\n')
    
    print(f"  ✓ 生图 Prompts: {IMAGE_OUTPUT}")
    print(f"  ✓ 生视频 Prompts: {VIDEO_OUTPUT}")
    print()
    
    # 4. 统计
    print("📊 统计信息")
    print(f"  生图 Prompts: {len(image_prompts)} 条")
    print(f"  生视频 Prompts: {len(video_prompts)} 条")
    print(f"  总 Prompts: {len(all_results)} 条")
    print()
    
    # 5. 质量评估
    high_quality_image = sum(1 for r in image_prompts if r.get('quality_score', 0) >= 60)
    high_quality_video = sum(1 for r in video_prompts if r.get('quality_score', 0) >= 60)
    
    print(f"  高质量生图 Prompts (>=60): {high_quality_image} 条")
    print(f"  高质量生视频 Prompts (>=60): {high_quality_video} 条")
    print()
    
    # 6. 生成报告
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report = {
        "timestamp": timestamp,
        "total_prompts": len(all_results),
        "image_prompts": len(image_prompts),
        "video_prompts": len(video_prompts),
        "high_quality_image": high_quality_image,
        "high_quality_video": high_quality_video,
        "files": {
            "image_prompts": IMAGE_OUTPUT,
            "video_prompts": VIDEO_OUTPUT
        }
    }
    
    report_file = f"{OUTPUT_DIR}/prompt-collection-report-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(report, indent=2, ensure_ascii=False))
    
    print(f"✅ 报告已生成: {report_file}")
    print()
    
    print("=" * 80)
    print("✅ Prompt 收集完成！")
    print("=" * 80)
    print()
    print(f"📁 数据文件:")
    print(f"  - {IMAGE_OUTPUT}")
    print(f"  - {VIDEO_OUTPUT}")
    print(f"  - {report_file}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
