#!/usr/bin/env python3
"""使用 Firecrawl API 收集 AI 提示词数据
解决 403 错误和反爬虫保护
"""

import json
import os
import time
import requests
from datetime import datetime
from typing import List, Dict, Any

try:
    from firecrawl import Firecrawl
except ImportError:
    print("❌ firecrawl-py 未安装，请运行: pip install firecrawl-py")
    exit(1)

OUTPUT_FILE = "/root/clawd/data/prompts/firecrawl-prompts.jsonl"

# 配置
API_KEY = os.environ.get("FIRECRAWL_API_KEY")
if not API_KEY:
    print("❌ FIRECRAWL_API_KEY 环境变量未设置")
    exit(1)

# 要抓取的电商视频和图片生成相关网站列表
URLS_TO_SCRAPE = [
    # 电商视频生成教程
    "https://www.adobe.com/express/feature/video/create/ecommerce-video",
    "https://www.canva.com/templates/s/ecommerce-product-videos/",
    "https://www.wondershare.com/ecommerce-video-maker.html",

    # Sora 和 OpenAI 视频生成
    "https://openai.com/sora",
    "https://platform.openai.com/docs/guides/sora",
    "https://github.com/openai/sora",

    # Google Veo 和视频生成
    "https://deepmind.google/technologies/veo/",
    "https://cloud.google.com/vertex-ai/generative-ai/docs/video/veo",

    # 电商图片生成
    "https://www.midjourney.com/docs/quick-start",
    "https://platform.openai.com/docs/guides/dall-e-3",
    "https://stability.ai/blog/stable-diffusion-3-release",

    # 产品摄影 AI
    "https://www.peppertype.ai/ai-product-photography",
    "https://www.flair.ai/",
    "https://www.pebblely.com/",

    # 电商 AI 工具
    "https://www.claid.ai/",
    "https://www.photoroom.com/",
    "https://www.remove.bg/",

    # GitHub 电商/视频/图片生成资源
    "https://github.com/topics/ecommerce-ai",
    "https://github.com/topics/video-generation-ai",
    "https://github.com/topics/image-generation-ai",
]

# 搜索查询
SEARCH_QUERIES = [
    "e-commerce video generation AI prompts",
    "product video AI prompts 2026",
    "Sora 2 video prompts for marketing",
    "Google Veo video generation prompts",
    "e-commerce image generation prompts",
    "product photo AI prompts Midjourney",
    "DALL-E 3 e-commerce prompts",
    "Stable Diffusion product photography",
    "AI video editing prompts for e-commerce",
    "text to video prompts workflow",
]

def scrape_with_jina_ai(url: str) -> Dict[str, Any]:
    """使用 Jina AI Reader 作为备用方案"""
    try:
        print(f"  🌐 尝试 Jina AI Reader: {url}")

        # Jina AI Reader API
        jina_url = f"https://r.jina.ai/http://{url.replace('https://', '').replace('http://', '')}"
        
        response = requests.get(jina_url, timeout=30)
        response.raise_for_status()
        
        content = response.text
        
        if not content or len(content.strip()) < 50:
            return {
                "url": url,
                "title": "",
                "content": "",
                "word_count": 0,
                "success": False,
                "error": "Jina AI content too short",
                "method": "jina-ai"
            }
        
        # 尝试提取标题
        title = ""
        lines = content.split('\n')
        if lines:
            # 第一行通常是标题
            title = lines[0].strip('#').strip()
        
        return {
            "url": url,
            "title": title,
            "content": content[:15000],  # 限制字符数
            "word_count": len(content.split()),
            "success": True,
            "method": "jina-ai"
        }
        
    except Exception as e:
        print(f"  ❌ Jina AI Reader 失败: {e}")
        return {"url": url, "success": False, "error": f"Jina AI: {str(e)}"}

def scrape_url(url: str, app: Firecrawl) -> Dict[str, Any]:
    """抓取单个 URL"""
    try:
        print(f"  🔍 抓取: {url}")

        result = app.scrape(
            url,
            formats=["markdown"],  # 优化：只提取 markdown，更快
            only_main_content=True,
            wait_for=5000,  # 增加到 5 秒，让 JS 完全渲染
            timeout=60000,  # 增加到 60 秒超时
            max_age=86400,  # 1 天缓存
        )

        if result and hasattr(result, 'markdown'):
            # metadata 是对象，不是字典
            title = ""
            if hasattr(result, 'metadata') and result.metadata:
                if hasattr(result.metadata, 'title'):
                    title = result.metadata.title
                elif hasattr(result.metadata, 'get'):
                    title = result.metadata.get("title", "")
                else:
                    title = str(result.metadata)[:100]

            markdown_content = result.markdown
            
            # 如果内容为空或太短，标记为失败
            if not markdown_content or len(markdown_content.strip()) < 50:
                print(f"  ⚠️  内容过短或为空: {len(markdown_content)} 字符")
                return {
                    "url": url, 
                    "title": title,
                    "content": "",
                    "word_count": 0,
                    "success": False, 
                    "error": "Content too short or empty"
                }
            
            return {
                "url": url,
                "title": title,
                "content": markdown_content,
                "word_count": len(markdown_content.split()),
                "success": True
            }
        else:
            print(f"  ❌ 抓取失败: 无内容返回")
            return {"url": url, "success": False, "error": "No content returned"}

    except Exception as e:
        print(f"  ❌ 抓取失败: {e}")
        # 如果遇到 403 或反爬虫错误，尝试使用 stealth 模式
        if "403" in str(e) or "401" in str(e) or "bot" in str(e).lower():
            print(f"  🔄 尝试使用 stealth 模式...")
            try:
                result = app.scrape(
                    url,
                    formats=["markdown"],
                    only_main_content=True,
                    proxy="stealth",  # 使用 stealth 模式
                    timeout=30000,
                )

                if result and hasattr(result, 'markdown'):
                    # metadata 是对象，不是字典
                    title = ""
                    if hasattr(result, 'metadata') and result.metadata:
                        if hasattr(result.metadata, 'title'):
                            title = result.metadata.title
                        elif hasattr(result.metadata, 'get'):
                            title = result.metadata.get("title", "")
                        else:
                            title = str(result.metadata)[:100]

                    return {
                        "url": url,
                        "title": title,
                        "content": result.markdown,
                        "word_count": len(result.markdown.split()),
                        "success": True,
                        "stealth_used": True,
                        "method": "firecrawl-stealth"
                    }
            except Exception as e2:
                print(f"  ❌ Stealth 模式也失败: {e2}")
        
        # 最后的回退：Jina AI Reader
        print(f"  🔄 尝试 Jina AI Reader 作为最后回退...")
        jina_result = scrape_with_jina_ai(url)
        if jina_result.get("success"):
            return jina_result
        
        return {"url": url, "success": False, "error": str(e)}

def search_firecrawl(query: str, app: Firecrawl, limit: int = 5) -> List[Dict[str, Any]]:
    """使用 Firecrawl 搜索"""
    try:
        print(f"\n🔎 搜索: {query}")

        results = app.search(
            query,
            limit=limit,
            scrape_options={
                "formats": ["markdown"],
                "only_main_content": True
            }
        )

        formatted_results = []
        for result in results:
            formatted_results.append({
                "url": result.url if hasattr(result, 'url') else "",
                "title": result.title if hasattr(result, 'title') else "",
                "content": result.markdown if hasattr(result, 'markdown') else "",
                "word_count": len(result.markdown.split()) if hasattr(result, 'markdown') else 0,
                "success": True,
                "source": "search"
            })
            print(f"  ✅ {result.title if hasattr(result, 'title') else 'N/A'}")

        return formatted_results

    except Exception as e:
        print(f"  ❌ 搜索失败: {e}")
        return []

def extract_prompts_from_content(content: str, title: str, url: str) -> List[str]:
    """从内容中提取提示词（简单版本）"""
    prompts = []

    # 查找代码块中的提示词
    import re
    code_blocks = re.findall(r'```(?:python|javascript|json|text|bash)?\n(.*?)```', content, re.DOTALL)
    for block in code_blocks:
        block = block.strip()
        if len(block) > 50 and ('prompt' in block.lower() or '指令' in block):
            prompts.append(block)

    # 查找引用的提示词
    quoted = re.findall(r'"([^"]{30,200})"', content)
    for quote in quoted:
        if any(word in quote.lower() for word in ['act as', 'you are', 'please', '帮我', '扮演']):
            prompts.append(quote)

    # 去重
    prompts = list(set(prompts))

    return prompts[:5]  # 最多返回 5 个

def calculate_quality_score(content: str) -> int:
    """计算内容质量分数 (0-100)"""
    score = 0
    
    # 长度评分
    length = len(content)
    if 100 <= length <= 500:
        score += 20
    elif 501 <= length <= 1000:
        score += 30
    elif 1001 <= length <= 2000:
        score += 25
    elif 2001 <= length <= 5000:
        score += 15
    elif length > 5000:
        score += 10
    
    # 关键词评分
    quality_keywords = [
        'prompt', 'generate', 'create', 'write', 'design',
        'best', 'effective', 'professional', 'guide', 'tutorial'
    ]
    content_lower = content.lower()
    score += min(30, sum(3 for kw in quality_keywords if kw in content_lower))
    
    # 结构评分
    if '\n\n' in content:
        score += 10  # 有段落分隔
    if any(marker in content for marker in ['##', '###', '**', '1.', '2.']):
        score += 15  # 有标题或列表
    
    return min(100, score)

def main():
    timestamp = datetime.now().isoformat()
    all_entries = []

    # 初始化 Firecrawl
    print("\n🔥 初始化 Firecrawl...")
    app = Firecrawl(api_key=API_KEY)

    # 阶段 1: 抓取预定义的 URL
    print("\n" + "="*60)
    print("[1/2] 抓取预定义网站")
    print("="*60)

    scraped_count = 0
    failed_count = 0

    for idx, url in enumerate(URLS_TO_SCRAPE, 1):
        print(f"\n[{idx}/{len(URLS_TO_SCRAPE)}]")

        result = scrape_url(url, app)

        if result.get("success"):
            scraped_count += 1
            
            # 获取完整内容
            full_content = result.get("content", "")
            title = result.get("title", "")
            
            # 保存页面内容本身作为提示词
            # 如果内容太长则截取
            content_to_save = full_content[:15000] if len(full_content) > 15000 else full_content
            
            if content_to_save:
                # 计算质量分数
                quality_score = calculate_quality_score(content_to_save)
                
                entry = {
                    "timestamp": timestamp,
                    "source": "firecrawl",
                    "method": "scrape",
                    "url": url,
                    "title": title,
                    "content": content_to_save,
                    "word_count": len(content_to_save.split()),
                    "quality_score": quality_score,
                    "success": True,
                    "stealth_used": result.get("stealth_used", False)
                }
                all_entries.append(entry)
                print(f"  ✅ 保存页面内容 ({len(content_to_save)} 字符, 质量分数: {quality_score})")
            
            # 额外提取提示词（作为补充）
            prompts = extract_prompts_from_content(full_content, title, url)
            
            if prompts:
                print(f"  💡 额外提取 {len(prompts)} 个提示词")
                
                # 只保存前 3 个额外提示词
                for i, prompt in enumerate(prompts[:3], 1):
                    # 避免与主内容重复（简单检查）
                    if len(prompt) < len(full_content) * 0.5:  # 提示词比正文短很多
                        quality_score = calculate_quality_score(prompt)
                        
                        entry = {
                            "timestamp": timestamp,
                            "source": "firecrawl",
                            "method": "scrape",
                            "url": url,
                            "title": f"{title} (extracted-{i})",
                            "content": prompt,
                            "quality_score": quality_score,
                            "success": True,
                            "stealth_used": result.get("stealth_used", False)
                        }
                        all_entries.append(entry)
        else:
            failed_count += 1
            entry = {
                "timestamp": timestamp,
                "source": "firecrawl",
                "method": "scrape",
                "url": url,
                "success": False,
                "error": result.get("error", "Unknown error")
            }
            all_entries.append(entry)

        # 避免请求过快
        time.sleep(1)

    # 阶段 2: 搜索查询
    print("\n" + "="*60)
    print("[2/2] 搜索 AI 提示词")
    print("="*60)

    search_count = 0
    for idx, query in enumerate(SEARCH_QUERIES, 1):
        print(f"\n[{idx}/{len(SEARCH_QUERIES)}]")

        results = search_firecrawl(query, app, limit=3)

        search_count += len(results)

        for result in results:
            # 获取完整内容
            full_content = result.get("content", "")
            title = result.get("title", "")
            url = result.get("url", "")
            
            # 保存页面内容本身作为提示词
            # 如果内容太长则截取
            content_to_save = full_content[:15000] if len(full_content) > 15000 else full_content
            
            if content_to_save:
                # 计算质量分数
                quality_score = calculate_quality_score(content_to_save)
                
                entry = {
                    "timestamp": timestamp,
                    "source": "firecrawl",
                    "method": "search",
                    "search_query": query,
                    "url": url,
                    "title": title,
                    "content": content_to_save,
                    "word_count": len(content_to_save.split()),
                    "quality_score": quality_score,
                    "success": True
                }
                all_entries.append(entry)
                print(f"  ✅ 保存页面内容 ({len(content_to_save)} 字符, 质量分数: {quality_score})")
            
            # 额外提取提示词（作为补充）
            prompts = extract_prompts_from_content(full_content, title, url)
            
            if prompts:
                print(f"  💡 额外提取 {len(prompts)} 个提示词")
                
                # 只保存前 3 个额外提示词
                for i, prompt in enumerate(prompts[:3], 1):
                    # 避免与主内容重复
                    if len(prompt) < len(full_content) * 0.5:  # 提示词比正文短很多
                        quality_score = calculate_quality_score(prompt)
                        
                        entry = {
                            "timestamp": timestamp,
                            "source": "firecrawl",
                            "method": "search",
                            "search_query": query,
                            "url": url,
                            "title": f"{title} (extracted-{i})",
                            "content": prompt,
                            "quality_score": quality_score,
                            "success": True
                        }
                        all_entries.append(entry)

        time.sleep(2)

    # 保存到 JSONL
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # 读取现有数据
    existing_entries = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    existing_entries.append(json.loads(line))

    # 合并数据
    all_data = existing_entries + all_entries

    # 写回文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for entry in all_data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    # 统计
    total_prompts = sum(e.get("prompts_found", 0) for e in all_entries if e.get("success"))
    stealth_used_count = sum(1 for e in all_entries if e.get("stealth_used"))

    print("\n" + "="*60)
    print("✅ 收集完成！")
    print("="*60)
    print(f"\n📊 统计:")
    print(f"  • 抓取成功: {scraped_count}/{len(URLS_TO_SCRAPE)}")
    print(f"  • 搜索结果: {search_count} 条")
    print(f"  • 失败: {failed_count}")
    print(f"  • 提取的提示词: {total_prompts} 个")
    print(f"  • 使用 stealth 模式: {stealth_used_count} 次")
    print(f"\n📁 文件: {OUTPUT_FILE}")
    print(f"📊 总数据量: {len(all_data)} 条")

    return {
        "scraped": scraped_count,
        "searched": search_count,
        "failed": failed_count,
        "prompts": total_prompts,
        "stealth": stealth_used_count
    }

if __name__ == "__main__":
    main()
