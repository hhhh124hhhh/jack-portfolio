#!/usr/bin/env python3
"""
从 GitHub 和 Reddit 收集谷歌生图和 Sora 2 的 Prompts
"""

import json
import os
from datetime import datetime

# 数据源
DATA_SOURCES = [
    "/root/clawd/data/prompts/reddit-prompts.jsonl",
    "/root/clawd/data/prompts/hacker-news-ai.jsonl",
    "/root/clawd/data/prompts/collected.jsonl"
]

# 输出目录
OUTPUT_DIR = "/root/clawd/data/prompts"
OUTPUT_FILE = f"{OUTPUT_DIR}/google-sora2-prompts-manual.jsonl"

# 谷歌生图相关关键词
GOOGLE_IMAGE_KEYWORDS = [
    "google imagen 3",
    "google imagen prompt",
    "google image generation",
    "veo prompt",
    "google ai image",
    "imagen 3",
    "google veo"
    "google image model"
    "谷歌生图",
    "Google Imagen",
    "Google Veo"
]

# Sora 2 相关关键词
SORA2_KEYWORDS = [
    "sora 2",
    "sora2",
    "openai sora 2",
    "sora 2 prompt",
    "sora 2 video",
    "sora 2 text to video",
    "sora 2 vs",
    "openai sora2",
    "Sora 2",
    "Sora 2 提示词",
    "OpenAI Sora 2"
]

def search_in_content(content, keywords):
    """在内容中搜索关键词"""
    if not content:
        return []
    
    text = content.lower()
    found_keywords = []
    
    for keyword in keywords:
        if keyword.lower() in text:
            found_keywords.append(keyword)
    
    return found_keywords

def categorize_prompt(content):
    """分类 prompt 类型"""
    if not content:
        return "通用"
    
    text = content.lower()
    
    # 检查谷歌生图相关
    google_keywords = ['imagen', 'veo', 'google image', '谷歌生图', 
                     'Google Imagen', 'Google Veo', 'image generation']
    if any(kw in text for kw in google_keywords):
        return "谷歌生图"
    
    # 检查 Sora 2 相关
    sora_keywords = ['sora 2', 'sora2', 'openai sora 2', 'sora 2 video',
                    'Sora 2', 'OpenAI Sora 2']
    if any(kw in text for kw in sora_keywords):
        return "Sora 2"
    
    return "通用"

def extract_prompt_from_text(text):
    """从文本中提取 prompt"""
    if not text:
        return ""
    
    prompt = text.strip()
    
    # 限制长度
    if len(prompt) > 2000:
        prompt = prompt[:2000] + "..."
    
    return prompt

def calculate_quality_score(data):
    """计算质量分数（0-100）"""
    score = 0
    
    content = extract_prompt_from_text(data.get('content', data.get('text', '')))
    title = data.get('title', '')
    likes = data.get('likes', 0) or data.get('points', 0) or data.get('score', 0)
    
    # 内容长度评分
    if len(content) > 100:
        score += 10
    if len(content) > 300:
        score += 10
    if len(content) > 500:
        score += 10
    
    # 提到关键词的评分
    text = content.lower() + ' ' + title.lower()
    
    google_keywords = ['imagen', 'veo', 'google image', '谷歌生图', 'Google Imagen']
    sora_keywords = ['sora 2', 'sora2', 'openai sora 2']
    video_keywords = ['video', 'video generation', 'text to video', '生视频']
    
    for keyword in google_keywords + sora_keywords + video_keywords:
        if keyword in text:
            score += 20
            break
    
    # 互动评分
    if likes > 0:
        import math
        score += min(30, math.log2(likes + 1) * 3)
    
    return min(100, score)

def main():
    print("=" * 80)
    print("🔍 从已收集的数据中提取谷歌生图和 Sora 2 Prompts")
    print("=" * 80)
    print()
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 读取所有数据
    all_data = []
    for source_file in DATA_SOURCES:
        if os.path.exists(source_file):
            print(f"📖 读取: {source_file}")
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            all_data.append(data)
                        except:
                            continue
                print(f"  ✓ 读取了 {len(all_data)} 条数据")
            except Exception as e:
                print(f"  ⚠️  读取失败: {e}")
    
    print()
    print(f"📊 总共读取 {len(all_data)} 条数据")
    print()
    
    # 搜索谷歌生图 Prompts
    print("[1/2] 搜索谷歌生图 Prompts...")
    google_prompts = []
    
    for data in all_data:
        content = data.get('content', data.get('text', ''))
        title = data.get('title', '')
        
        found_keywords = search_in_content(content + ' ' + title, GOOGLE_IMAGE_KEYWORDS)
        
        if found_keywords:
            prompt_type = "谷歌生图"
            quality_score = calculate_quality_score(data)
            
            google_prompts.append({
                "content": content,
                "title": title,
                "prompt_type": prompt_type,
                "quality_score": quality_score,
                "found_keywords": found_keywords,
                "source": data.get('source', 'unknown'),
                "url": data.get('url', ''),
                "likes": data.get('likes', 0) or data.get('points', 0) or data.get('score', 0)
            })
    
    print(f"  ✓ 找到 {len(google_prompts)} 个谷歌生图 Prompts")
    print()
    
    # 搜索 Sora 2 Prompts
    print("[2/2] 搜索 Sora 2 Prompts...")
    sora2_prompts = []
    
    for data in all_data:
        content = data.get('content', data.get('text', ''))
        title = data.get('title', '')
        
        found_keywords = search_in_content(content + ' ' + title, SORA2_KEYWORDS)
        
        if found_keywords:
            prompt_type = "Sora 2"
            quality_score = calculate_quality_score(data)
            
            sora2_prompts.append({
                "content": content,
                "title": title,
                "prompt_type": prompt_type,
                "quality_score": quality_score,
                "found_keywords": found_keywords,
                "source": data.get('source', 'unknown'),
                "url": data.get('url', ''),
                "likes": data.get('likes', 0) or data.get('points', 0) or data.get('score', 0)
            })
    
    print(f"  ✓ 找到 {len(sora2_prompts)} 个 Sora 2 Prompts")
    print()
    
    # 去重
    seen = set()
    unique_prompts = []
    
    for prompt in google_prompts + sora2_prompts:
        content_hash = hash(prompt.get('content', ''))
        if content_hash not in seen:
            seen.add(content_hash)
            unique_prompts.append(prompt)
    
    print(f"📊 去重后: {len(unique_prompts)} 个 Prompts")
    print()
    
    # 高质量过滤
    high_quality = [p for p in unique_prompts if p.get('quality_score', 0) >= 50]
    
    print(f"📊 高质量 Prompts (>=50 分): {len(high_quality)} 个")
    print()
    
    # 分类统计
    google_count = sum(1 for p in high_quality if p.get('prompt_type') == '谷歌生图')
    sora2_count = sum(1 for p in high_quality if p.get('prompt_type') == 'Sora 2')
    
    print(f"📂 谷歌生图 Prompts: {google_count} 个")
    print(f"📂 Sora 2 Prompts: {sora2_count} 个")
    print()
    
    # 保存数据
    print("💾 保存数据...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for prompt in high_quality:
            f.write(json.dumps(prompt, ensure_ascii=False) + '\n')
    
    print(f"  ✓ 已保存: {OUTPUT_FILE}")
    print()
    
    # 显示 Top 20
    print("🏆 Top 20 谷歌生图和 Sora 2 Prompts")
    print("=" * 80)
    print()
    
    print(f"{'排名':<6} {'类型':<15} {'分数':<10} {'关键词'}")
    print("-" * 80)
    
    sorted_prompts = sorted(high_quality, key=lambda x: x.get('quality_score', 0), reverse=True)
    
    for i, prompt in enumerate(sorted_prompts[:20], 1):
        prompt_type = prompt.get('prompt_type', '')
        score = prompt.get('quality_score', 0)
        keywords = ', '.join(prompt.get('found_keywords', [])[:2])
        
        print(f"{i:<6} {prompt_type:<15} {score:<10} {keywords}")
    
    print()
    print("=" * 80)
    print("✅ 收集完成！")
    print("=" * 80)
    print()
    
    # 生成报告
    timestamp = datetime.now().strftime('%Y-%m-%d')
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_data": len(all_data),
        "unique_prompts": len(unique_prompts),
        "high_quality": len(high_quality),
        "google_prompts": google_count,
        "sora2_prompts": sora2_count,
        "google_search_keywords": GOOGLE_IMAGE_KEYWORDS,
        "sora2_search_keywords": SORA2_KEYWORDS,
        "output_file": OUTPUT_FILE
    }
    
    report_file = f"{OUTPUT_DIR}/google-sora2-manual-collection-report-{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(report, indent=2, ensure_ascii=False))
    
    print(f"📄 报告已生成: {report_file}")
    print()
    print(f"📁 数据文件: {OUTPUT_FILE}")
    print(f"📄 报告文件: {report_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
