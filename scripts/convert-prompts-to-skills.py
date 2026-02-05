#!/usr/bin/env python3
"""
将 Prompts 转换成 Skills (增强版)
修复内容：
1. 内容提取验证
2. 类型推断（而非硬编码）
3. 去重机制
4. 质量增强验证
5. 详细日志记录
"""

import json
import os
import re
from datetime import datetime
import hashlib

# 配置
PROMPTS_DIR = "/root/clawd/data/prompts"
SKILLS_DIR = "/root/clawd/generated-skills"
SKILLS_OUTPUT_DIR = "/root/clawd/dist/skills"
LOGS_DIR = "/root/clawd/data/conversion-logs"

# 高质量阈值
MIN_QUALITY_SCORE = 60

# 质量验证规则
MIN_CONTENT_LENGTH = 20
MAX_CONTENT_LENGTH = 2000
TRUNCATION_MARKERS = ['...', '# 1', '# 2', 'Read more', 'continue reading', 'click to continue']
ACTION_VERBS = ['generate', 'write', 'create', 'design', 'build', 'make', 'produce', 'develop', 'craft', 'render', 'draw', 'paint', 'compose']

# 类型推断关键词
TYPE_KEYWORDS = {
    "Image Generation": ['image', 'photo', 'picture', 'render image', 'generate image', 'portrait', 'landscape', 'scene', 'visual', 'illustration'],
    "Video Generation": ['video', 'animation', 'motion', 'render video', 'generate video', 'clip', 'sequence', 'animate', 'movement'],
}

def validate_content(content):
    """
    验证内容质量
    返回 (is_valid, reason)
    """
    # 检查长度
    if not content or len(content) < MIN_CONTENT_LENGTH:
        return False, f"内容过短: {len(content) if content else 0} < {MIN_CONTENT_LENGTH}"
    
    if len(content) > MAX_CONTENT_LENGTH:
        return False, f"内容过长: {len(content)} > {MAX_CONTENT_LENGTH}"
    
    # 检查截断标记
    for marker in TRUNCATION_MARKERS:
        if marker.lower() in content.lower():
            return False, f"包含截断标记: '{marker}'"
    
    # 检查是否包含动作动词
    content_lower = content.lower()
    has_action_verb = any(verb in content_lower for verb in ACTION_VERBS)
    
    if not has_action_verb:
        return False, "缺少动作动词（需要 generate, write, create 等）"
    
    return True, "通过"

def infer_type(content):
    """
    根据内容推断类型
    返回 inferred_type
    """
    content_lower = content.lower()
    
    # 检查每个类型的关键词
    for prompt_type, keywords in TYPE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in content_lower:
                return prompt_type
    
    # 默认为文本 prompt
    return "Text Prompt"

def create_skill_from_prompt(prompt_data, inferred_type, processed_hashes, processed_skill_names, log_file):
    """从 prompt 创建 skill（增强版）"""
    content = prompt_data.get('content', '').strip()
    title = prompt_data.get('title', 'AI Skill')
    source = prompt_data.get('source', '')
    url = prompt_data.get('url', '')
    quality_score = prompt_data.get('quality_score', 0)
    
    # 1. 内容验证
    is_valid, validation_reason = validate_content(content)
    
    if not is_valid:
        # 记录跳过原因
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "title": title[:100],
            "status": "skipped",
            "reason": validation_reason,
            "content_length": len(content) if content else 0,
            "quality_score": quality_score
        }
        log_file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        log_file.flush()  # 立即 flush，确保数据写入
        return None
    
    # 2. 生成 skill name（先用于去重检查）
    skill_name_clean = title.lower()
    skill_name_clean = re.sub(r'[^a-z0-9\s-]', '-', skill_name_clean)
    skill_name_clean = re.sub(r'\s+', '-', skill_name_clean)
    skill_name_clean = re.sub(r'-+', '-', skill_name_clean)
    skill_name_clean = skill_name_clean.strip('-')
    skill_name_clean = skill_name_clean[:50]
    
    # 3. 基于 skill name 去重（更稳健）
    if skill_name_clean in processed_skill_names:
        # 记录重复
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "title": title[:100],
            "status": "duplicate",
            "skill_name": skill_name_clean,
            "content_length": len(content)
        }
        log_file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        log_file.flush()  # 立即 flush，确保数据写入
        return None
    
    processed_skill_names.add(skill_name_clean)
    
    # 4. 计算 content hash（保留用于日志）
    content_hash = hashlib.md5(content.encode()).hexdigest()
    
    if content_hash in processed_hashes:
        # 记录重复
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "title": title[:100],
            "status": "duplicate",
            "content_hash": content_hash,
            "content_length": len(content)
        }
        log_file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        return None
    
    processed_hashes.add(content_hash)
    
    # 5. 类型推断（已经在上层完成，但这里用于记录）
    actual_type = inferred_type
    
    # 生成 description（不被截断）
    description = content[:500] + "..." if len(content) > 500 else content
    
    # 6. 生成 skill
    # 生成唯一的 skill name（清理特殊字符）
    skill_name_final = f"{skill_name_clean}-{content_hash[:8]}"
    
    # 生成 SKILL.md with proper YAML frontmatter
    # 先构建 metadata JSON 对象
    metadata_obj = {
        "clawdbot": {
            "type": actual_type.lower(),
            "inferred_type": actual_type,
            "source": source,
            "original_url": url,
            "quality_score": quality_score
        }
    }
    import json as json_lib
    metadata_json = json_lib.dumps(metadata_obj, ensure_ascii=False)

    skill_md = f"""---
name: {skill_name_final}
description: {description}
metadata: {metadata_json}
---

# {title}

## 描述
{description}

## 来源
- 平台: {source}
- 原始链接: {url}
- 类型: {actual_type}
- 质量分数: {quality_score}

## Prompt
```
{prompt_display}
```

---

## 标签
- AI
- {actual_type}
- prompt
- 生成
- clawdbot

---

*Skill generated by Clawdbot*
"""

    # 创建 skill 目录
    skill_dir = os.path.join(SKILLS_OUTPUT_DIR, skill_name_final)
    os.makedirs(skill_dir, exist_ok=True)
    
    # 保存 SKILL.md
    with open(os.path.join(skill_dir, "SKILL.md"), 'w', encoding='utf-8') as f:
        f.write(skill_md)
    
    # 创建 metadata.json
    metadata = {
        "name": title,
        "version": "1.0.0",
        "description": description,
        "author": "Clawdbot",
        "type": actual_type,
        "source": source,
        "url": url,
        "quality_score": quality_score,
        "content_hash": content_hash,
        "created_at": datetime.now().isoformat()
    }
    
    with open(os.path.join(skill_dir, "metadata.json"), 'w', encoding='utf-8') as f:
        f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
    
    # 记录成功
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "title": title[:100],
        "status": "success",
        "skill_name": skill_name_final,
        "inferred_type": actual_type,
        "content_length": len(content),
        "content_hash": content_hash,
        "quality_score": quality_score
    }
    log_file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    return {
        "name": skill_name_final,
        "path": skill_dir,
        "md_file": os.path.join(skill_dir, "SKILL.md"),
        "metadata": metadata
    }

def main():
    print("=" * 80)
    print("🔄 转换 Prompts 为 Skills (增强版)")
    print("=" * 80)
    print()
    
    # 创建日志目录
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(SKILLS_OUTPUT_DIR, exist_ok=True)
    
    # 创建日志文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file_path = os.path.join(LOGS_DIR, f"conversion-{timestamp}.jsonl")
    
    print(f"📝 日志文件: {log_file_path}")
    print()
    
    # 检查输入文件 - 扩展支持所有数据源
    input_file_configs = [
        ("reddit", "reddit-prompts.jsonl"),
        ("github", "github-prompts.jsonl"),
        ("github-awesome", "github-awesome-prompts.jsonl"),
        ("hackernews", "hacker-news-ai.jsonl"),
        ("collected", "collected.jsonl"),
        ("firecrawl", "firecrawl-prompts.jsonl"),
        ("image", "image-prompts.jsonl"),
        ("general", "general-prompts-v2.jsonl"),
        ("image-v2", "image-prompts-v2.jsonl"),
        ("video-v2", "video-prompts-v2.jsonl")
    ]
    
    all_skills = []
    processed_hashes = set()
    processed_skill_names = set()  # 新增：基于 skill name 的去重
    
    # 用于统计
    stats = {
        "total_processed": 0,
        "converted": 0,
        "skipped_invalid": 0,
        "skipped_duplicate": 0,
        "skipped_low_quality": 0,
        "type_text": 0,
        "type_image": 0,
        "type_video": 0
    }
    
    # 打开日志文件
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        # 处理所有输入文件 - 扩展支持所有数据源
        input_files = []
        for file_type, filename in input_file_configs:
            file_path = os.path.join(PROMPTS_DIR, filename)
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                input_files.append((file_type, file_path))
                print(f"[✓ 已加载] {file_type}: {filename} ({os.path.getsize(file_path)} bytes)")
            else:
                print(f"[✗ 跳过] {file_type}: {filename} (不存在或为空)")
        
        print()
        print(f"总共加载 {len(input_files)} 个数据源")
        print()
        
        # 遍历所有加载的数据源
        for file_type, file_path in input_files:
            print(f"[处理中] {file_type} prompts: {os.path.basename(file_path)}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    
                    try:
                        prompt_data = json.loads(line)
                        stats["total_processed"] += 1
                        
                        # 检查质量分数 - 支持多种分数字段和范围
                        quality_score = prompt_data.get('quality_score', 0)
                        
                        # 如果是 collected.jsonl (SearXNG 数据)，使用 score 字段并映射到 0-100
                        if file_type == "collected":
                            raw_score = prompt_data.get('score', 0)
                            # SearXNG 的 score 范围是 0-5，需要映射到 0-100
                            quality_score = raw_score * 20
                        
                        # 如果是 firecrawl 数据，计算质量分数
                        elif file_type == "firecrawl":
                            content = prompt_data.get('content', '')
                            word_count = len(content.split())
                            # 根据内容长度和提示词数量计算分数
                            prompts_found = prompt_data.get('prompts_found', 0)
                            quality_score = min(90, word_count / 10 + prompts_found * 10)
                        
                        # GitHub awesome prompts 的分数范围较小，给予额外加分
                        elif file_type == "github-awesome" and quality_score > 0:
                            quality_score = min(90, quality_score * 4)
                        
                        if quality_score < MIN_QUALITY_SCORE:
                            # 记录低质量跳过
                            log_entry = {
                                "timestamp": datetime.now().isoformat(),
                                "title": prompt_data.get('title', 'Unknown')[:100],
                                "status": "skipped_low_quality",
                                "quality_score": quality_score,
                                "min_required": MIN_QUALITY_SCORE
                            }
                            log_file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                            stats["skipped_low_quality"] += 1
                            continue
                        
                        # 推断类型
                        content = prompt_data.get('content', '')
                        inferred_type = infer_type(content)
                        
                        # 更新类型统计
                        if inferred_type == "Text Prompt":
                            stats["type_text"] += 1
                        elif inferred_type == "Image Generation":
                            stats["type_image"] += 1
                        elif inferred_type == "Video Generation":
                            stats["type_video"] += 1
                        
                        # 创建 skill
                        skill = create_skill_from_prompt(prompt_data, inferred_type, processed_hashes, processed_skill_names, log_file)
                        
                        if skill:
                            all_skills.append(skill)
                            stats["converted"] += 1
                            if line_num % 10 == 0:
                                print(f"  已处理 {line_num} 条，成功转换 {stats['converted']} 个")
                        else:
                            # 读取最后一条日志来判断是无效还是重复
                            try:
                                with open(log_file_path, 'r', encoding='utf-8') as log_f:
                                    lines = log_f.readlines()
                                    if lines:
                                        last_log = json.loads(lines[-1].strip())
                                        if last_log.get('status') == 'duplicate':
                                            stats["skipped_duplicate"] += 1
                                        else:
                                            stats["skipped_invalid"] += 1
                            except:
                                stats["skipped_invalid"] += 1
                            
                    except Exception as e:
                        # 记录错误
                        log_entry = {
                            "timestamp": datetime.now().isoformat(),
                            "line_number": line_num,
                            "error": str(e),
                            "status": "error"
                        }
                        log_file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                        print(f"  ⚠️  跳过第 {line_num} 行: {e}")
            
            print(f"  ✓ 完成")
            print()
    
    # 打包成 .skill 文件
    print("[打包] 生成 .skill 文件...")
    
    packaged_count = 0
    for skill in all_skills:
        skill_name = skill["name"]
        skill_path = skill["path"]
        
        # 打包成 zip
        import zipfile
        skill_file = os.path.join(SKILLS_OUTPUT_DIR, f"{skill_name}.skill")
        
        try:
            with zipfile.ZipFile(skill_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(skill_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, skill_path)
                        zipf.write(file_path, arcname)
            
            packaged_count += 1
        except Exception as e:
            print(f"  ⚠️  打包失败 {skill_name}: {e}")
    
    print(f"  ✓ 打包完成: {packaged_count} 个 .skill 文件")
    print()
    
    # 生成统计报告
    print("生成统计报告...")
    
    report_file = os.path.join(LOGS_DIR, f"conversion-report-{timestamp}.json")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "total_processed": stats['total_processed'],
        "total_converted": stats['converted'],
        "total_skipped": stats['skipped_invalid'] + stats['skipped_duplicate'] + stats['skipped_low_quality'],
        "total_packaged": packaged_count,
        "type_distribution": {
            "text_prompt": stats['type_text'],
            "image_generation": stats['type_image'],
            "video_generation": stats['type_video']
        },
        "output_dir": SKILLS_OUTPUT_DIR,
        "log_file": log_file_path
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(report, indent=2, ensure_ascii=False))
    
    print(f"✅ 报告已保存: {report_file}")
    print()
    print("=" * 80)
    print("✅ 转换完成！")
    print("=" * 80)
    print()
    print(f"📊 统计信息:")
    print(f"  总计处理: {stats['total_processed']} 条")
    print(f"  成功转换: {stats['converted']} 个")
    print(f"  跳过 (内容无效): {stats['skipped_invalid']} 条")
    print(f"  跳过 (重复): {stats['skipped_duplicate']} 条")
    print(f"  跳过 (低质量): {stats['skipped_low_quality']} 条")
    print()
    print(f"  类型分布:")
    print(f"    Text Prompt: {stats['type_text']}")
    print(f"    Image Generation: {stats['type_image']}")
    print(f"    Video Generation: {stats['type_video']}")
    print()
    print(f"  打包: {packaged_count} 个 .skill 文件")
    print()
    print(f"📁 输出文件:")
    print(f"  Skills: {SKILLS_OUTPUT_DIR}")
    print(f"  日志: {log_file_path}")
    print(f"  报告: {report_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
