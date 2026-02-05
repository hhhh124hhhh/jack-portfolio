#!/usr/bin/env python3
"""
收集谷歌生图模型和 Sora 2 的 Prompts
"""

import requests
import json
from datetime import datetime
import time

# 配置
SEARXNG_URL = "http://localhost:8080"
OUTPUT_DIR = "/root/clawd/data/prompts"
OUTPUT_FILE = f"{OUTPUT_DIR}/google-sora2-prompts.jsonl"

# 谷歌生图模型相关关键词
GOOGLE_IMAGE_QUERIES = [
    "google imagen 3 prompt",
    "google imagen prompt template",
    "google veo prompt",
    "google video generation prompt",
    "google imagen vs midjourney",
    "google ai image prompt",
    "谷歌生图提示词",
    "Google Imagen 提示词",
    "Veo 谷歌视频"
]

# Sora 2 相关关键词
SORA2_QUERIES = [
    "sora 2 prompt",
    "sora 2 prompt template",
    "openai sora 2 prompt",
    "sora 2 video prompt",
    "sora 2 text to video",
    "sora 2 vs runway",
    "sora 2 best prompts",
    "Sora 2 提示词"
    "OpenAI Sora 2 提示词"
]

def search_searxng(query, limit=30):
    """使用 SearXNG 搜索"""
    try:
        params = {
            'q': query,
            'engines': ['google', 'bing', 'duckduckgo'],
            'format': 'json',
            'categories': ['general', 'technology', 'science'],
            'limit': limit
        }
        response = requests.get(f"{SEARXNG_URL}/search", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])
    except Exception as e:
        print(f"  ⚠️  搜索失败: {e}")
        return []

def extract_prompt_from_content(content):
    """从内容中提取 Prompt"""
    if not content:
        return ""
    
    # 简单清理
    prompt = content.strip()
    
    # 限制长度
    if len(prompt) > 2000:
        prompt = prompt[:2000] + "..."
    
    return prompt

def categorize_prompt(content, query):
    """分类 Prompt 类型"""
    text = (content + " " + query).lower()
    
    # 谷歌生图相关
    google_keywords = ['imagen', 'veo', 'google image', '谷歌生图', 
                     'google video', 'Google Imagen', 'Google Veo']
    if any(kw in text for kw in google_keywords):
        return "谷歌生图"
    
    # Sora 2 相关
    sora_keywords = ['sora 2', 'openai sora', 'sora2', 'sora openai', 
                    'OpenAI Sora', 'Sora 2 提示词']
    if any(kw in text for kw in sora_keywords):
        return "Sora 2"
    
    # 视频生成相关
    video_keywords = ['video generation', 'text to video', 'ai video', 
                     'ai 做视频', '视频生成']
    if any(kw in text for kw in video_keywords):
        return "AI 视频"
    
    return "通用"

def calculate_quality_score(result):
    """计算质量分数（0-100）"""
    score = 0
    
    content = result.get('content', '')
    title = result.get('title', '')
    url = result.get('url', '')
    
    # 内容长度评分
    if len(content) > 100:
        score += 10
    if len(content) > 300:
        score += 10
    if len(content) > 500:
        score += 10
    
    # 标题质量
    if len(title) > 20:
        score += 10
    if len(title) > 50:
        score += 5
    
    # 是否包含 Prompt 相关关键词
    prompt_keywords = ['prompt', '提示词', 'template', '模板', 'instruction', '指令', 'example', '示例']
    text = title.lower() + ' ' + content.lower()
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
    print("🔍 收集谷歌生图模型和 Sora 2 的 Prompts")
    print("=" * 80)
    print()
    
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_results = []
    
    # 1. 搜索谷歌生图 Prompts
    print("[1/2] 搜索谷歌生图模型 Prompts...")
    for i, query in enumerate(GOOGLE_IMAGE_QUERIES):
        print(f"  [{i+1}/{len(GOOGLE_IMAGE_QUERIES)}] {query}...", end='', flush=True)
        
        results = search_searxng(query, limit=25)
        
        for result in results:
            result['prompt_type'] = "谷歌生图"
            result['query'] = query
            result['quality_score'] = calculate_quality_score(result)
            all_results.append(results)
        
        print(f" ✓ 找到 {len(results)} 个结果")
        
        # 添加延迟避免速率限制
        if i < len(GOOGLE_IMAGE_QUERIES) - 1:
            time.sleep(0.5)
    
    print(f"  ✓ 谷歌生图 Prompts: {len(all_results)} 条")
    print()
    
    # 2. 搜索 Sora 2 Prompts
    print("[2/2] 搜索 Sora 2 Prompts...")
    for i, query in enumerate(SORA2_QUERIES):
        print(f"  [{i+1}/{len(SORA2_QUERIES)}] {query}...", end='', flush=True)
        
        results = search_searxng(query, limit=25)
        
        for result in results:
            result['prompt_type'] = "Sora 2"
            result['query'] = query
            result['quality_score'] = calculate_quality_score(result)
            all_results.append(results)
        
        print(f" ✓ 找到 {len(results)} 个结果")
        
        # 添加延迟避免速率限制
        if i < len(SORA2_QUERIES) - 1:
            time.sleep(0.5)
    
    print(f"  ✓ Sora 2 Prompts: {len(all_results)} 条")
    print()
    
    # 3. 统计
    print("📊 统计信息")
    google_count = sum(1 for r in all_results if r.get('prompt_type') == '谷歌生图')
    sora2_count = sum(1 for r in all_results if r.get('prompt_type') == 'Sora 2')
    
    print(f"  谷歌生图 Prompts: {google_count} 条")
    print(f"  Sora 2 Prompts: {sora2_count} 条")
    print(f"  总计: {len(all_results)} 条")
    print()
    
    # 4. 高质量过滤
    high_quality = [r for r in all_results if r.get('quality_score', 0) >= 60]
    google_high = [r for r in high_quality if r.get('prompt_type') == '谷歌生图']
    sora2_high = [r for r in high_quality if r.get('prompt_type') == 'Sora 2']
    
    print(f"📊 高质量 Prompts (>=60 分):")
    print(f"  谷歌生图: {len(google_high)} 条")
    print(f"  Sora 2: {len(sora2_high)} 条")
    print(f"  总计: {len(high_quality)} 条")
    print()
    
    # 5. 保存数据
    print("💾 保存数据...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for result in high_quality:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    print(f"  ✓ 已保存: {OUTPUT_FILE}")
    print()
    
    # 6. 生成报告
    timestamp = datetime.now().strftime('%Y-%m-%d')
    report = {
        "timestamp": datetime.now().isoformat(),
        "search_queries": GOOGLE_IMAGE_QUERIES + SORA2_QUERIES,
        "total_results": len(all_results),
        "high_quality": len(high_quality),
        "by_type": {
            "谷歌生图": google_count,
            "Sora 2": sora2_count
        },
        "high_quality_by_type": {
            "谷歌生图": len(google_high),
            "Sora 2": len(sora2_high)
        },
        "output_file": OUTPUT_FILE
    }
    
    report_file = f"{OUTPUT_DIR}/google-sora2-collection-report-{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(report, indent=2, ensure_ascii=False))
    
    print(f"  ✓ 报告已生成: {report_file}")
    print()
    
    # 7. 显示 Top 20
    print("🏆 Top 20 高质量 Prompts")
    print("=" * 80)
    print()
    
    print(f"{'排名':<6} {'类型':<15} {'内容':<50} {'分数':<10}")
    print("-" * 80)
    
    # 按分数排序
    sorted_results = sorted(high_quality, key=lambda x: x.get('quality_score', 0), reverse=True)
    
    for i, result in enumerate(sorted_results[:20], 1):
        content = result.get('content', '')[:48]
        prompt_type = result.get('prompt_type', '')
        score = result.get('quality_score', 0)
        
        print(f"{i:<6} {prompt_type:<15} {content:<50} {score:<10}")
    
    print()
    print("=" * 80)
    print("✅ 收集完成！")
    print("=" * 80)
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
