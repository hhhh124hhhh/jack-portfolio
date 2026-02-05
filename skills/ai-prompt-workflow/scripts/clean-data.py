#!/usr/bin/env python3
"""
数据清洗层
作者：Momo (Clawdbot Team)
创建日期：2026-02-05

功能：
1. 去除空内容
2. 去除太短内容
3. 去除重复内容（基于内容 hash）
4. 去除导航和页脚
5. 去除特殊格式内容
"""

import json
import logging
import hashlib
import re
import sys
from datetime import datetime
from typing import List, Dict, Any, Set
from pathlib import Path

# 添加项目路径
# 修正路径计算：脚本在 /root/clawd/skills/ai-prompt-workflow/scripts/
# 需要 4 个 .parent 才能到达 /root/clawd
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# ==================== 配置 ====================

class Config:
    """配置管理"""
    
    # 数据目录
    DATA_DIR = project_root / "data/prompts"
    CLASSIFIED_DIR = DATA_DIR / "classified"
    CLEANED_DIR = DATA_DIR / "cleaned"
    
    # 日志文件
    LOG_DIR = project_root / "logs"
    LOG_FILE = LOG_DIR / "clean-data.log"
    
    # 清洗规则
    MIN_CONTENT_LENGTH = 50  # 最小内容长度
    MAX_CONTENT_LENGTH = 50000  # 最大内容长度
    
    @classmethod
    def ensure_dirs(cls):
        """确保所有目录存在"""
        cls.CLEANED_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

# ==================== 日志 ====================

def setup_logging() -> logging.Logger:
    """设置日志"""
    Config.ensure_dirs()
    
    logger = logging.getLogger("clean-data")
    logger.setLevel(logging.DEBUG)
    
    # 文件 handler
    file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# ==================== 清洗函数 ====================

def clean_empty_content(items: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
    """去除空内容"""
    cleaned = []
    removed_count = 0
    
    for item in items:
        content = item.get("content", "") or item.get("prompt", "")
        
        if content and len(content.strip()) > 0:
            cleaned.append(item)
        else:
            removed_count += 1
            logger.debug(f"Removed empty content: {item.get('title', 'N/A')[:50]}")
    
    stats = {
        "total": len(items),
        "removed": removed_count,
        "kept": len(cleaned),
        "removal_rate": f"{removed_count / len(items) * 100:.1f}%" if len(items) > 0 else "0%"
    }
    
    logger.info(f"Empty content removed: {removed_count}/{len(items)} ({stats['removal_rate']})")
    
    return cleaned, stats

def clean_too_short(items: List[Dict[str, Any]], min_length: int) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
    """去除太短的内容"""
    cleaned = []
    removed_count = 0
    
    for item in items:
        content = item.get("content", "") or item.get("prompt", "")
        
        if len(content) >= min_length:
            cleaned.append(item)
        else:
            removed_count += 1
            logger.debug(f"Removed too short content ({len(content)} chars): {item.get('title', 'N/A')[:50]}")
    
    stats = {
        "total": len(items),
        "removed": removed_count,
        "kept": len(cleaned),
        "removal_rate": f"{removed_count / len(items) * 100:.1f}%" if len(items) > 0 else "0%"
    }
    
    logger.info(f"Too short content removed: {removed_count}/{len(items)} ({stats['removal_rate']})")
    
    return cleaned, stats

def clean_duplicates(items: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
    """去除重复内容（基于内容 hash）"""
    content_hashes: Set[str] = set()
    cleaned = []
    removed_count = 0
    
    for item in items:
        content = item.get("content", "") or item.get("prompt", "")
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        if content_hash not in content_hashes:
            content_hashes.add(content_hash)
            cleaned.append(item)
        else:
            removed_count += 1
            logger.debug(f"Removed duplicate: {item.get('title', 'N/A')[:50]}")
    
    stats = {
        "total": len(items),
        "removed": removed_count,
        "kept": len(cleaned),
        "unique": len(content_hashes),
        "removal_rate": f"{removed_count / len(items) * 100:.1f}%" if len(items) > 0 else "0%"
    }
    
    logger.info(f"Duplicates removed: {removed_count}/{len(items)} ({stats['removal_rate']})")
    
    return cleaned, stats

def clean_navigation_footer(items: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
    """去除导航和页脚"""
    cleaned = []
    removed_count = 0
    
    # 导航和页脚的典型模式
    navigation_patterns = [
        r'\[Skip to content\]',
        r'Sign in.*Sign out',
        r'Profile.*Notification',
        r'Creator Center',
        r'Footer|Copyright',
        r'Privacy Policy|Terms of Service',
        r'Language.*Change',
        r'Navigation.*Menu',
        r'Home.*About.*Contact',
        r'^\s*#+\s*$',
        r'^\s*[-*_]{3,}\s*$',
    ]
    
    for item in items:
        content = item.get("content", "") or item.get("prompt", "")
        
        # 检查是否匹配导航/页脚模式
        is_navigation = False
        for pattern in navigation_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                is_navigation = True
                break
        
        # 额外检查：如果内容大部分是链接或短行，可能是导航
        lines = content.split('\n')
        short_lines = sum(1 for line in lines if len(line.strip()) < 50)
        if short_lines / len(lines) > 0.7 and len(lines) > 5:
            is_navigation = True
        
        if is_navigation:
            removed_count += 1
            logger.debug(f"Removed navigation/footer: {item.get('title', 'N/A')[:50]}")
        else:
            cleaned.append(item)
    
    stats = {
        "total": len(items),
        "removed": removed_count,
        "kept": len(cleaned),
        "removal_rate": f"{removed_count / len(items) * 100:.1f}%" if len(items) > 0 else "0%"
    }
    
    logger.info(f"Navigation/footer removed: {removed_count}/{len(items)} ({stats['removal_rate']})")
    
    return cleaned, stats

def clean_special_format(items: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
    """去除特殊格式内容"""
    cleaned = []
    removed_count = 0
    
    for item in items:
        content = item.get("content", "") or item.get("prompt", "")
        title = item.get("title", "")
        
        # 特殊格式模式
        special_formats = [
            r'^\s*Loading\s*\.\.\.×\s*Sorry\s+to\s+interrupt',  # Loading 提示
            r'^\s*\[Subscribe\].*Atom\s+feed',  # RSS 订阅链接
            r'^\s*\[Random\]',  # 随机链接
            r'^\s*<!DOCTYPE',  # HTML 文档开头
            r'^\s*<html',  # HTML 标签
        ]
        
        is_special = False
        for pattern in special_formats:
            if re.match(pattern, content, re.IGNORECASE):
                is_special = True
                break
        
        # 额外检查：如果是 URL 列表，去除
        if not is_special and content.strip().startswith(('http://', 'https://')):
            # 检查是否主要是 URL
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            url_lines = sum(1 for line in lines if line.startswith(('http://', 'https://')))
            if url_lines / len(lines) > 0.5:
                is_special = True
        
        if is_special:
            removed_count += 1
            logger.debug(f"Removed special format: {title[:50]}")
        else:
            cleaned.append(item)
    
    stats = {
        "total": len(items),
        "removed": removed_count,
        "kept": len(cleaned),
        "removal_rate": f"{removed_count / len(items) * 100:.1f}%" if len(items) > 0 else "0%"
    }
    
    logger.info(f"Special format removed: {removed_count}/{len(items)} ({stats['removal_rate']})")
    
    return cleaned, stats

def clean_low_quality_content(items: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    过滤低质量内容
    
    只保留：
    - 教程、指南、提示词等实质性内容
    - 有结构的文章
    - 提供示例或代码的内容
    
    过滤掉：
    - 短讨论、评论
    - 网站导航、页脚
    - 文章列表
    - 无结构的短文本
    """
    cleaned = []
    removed_count = 0
    
    for item in items:
        content = item.get("content", "") or item.get("prompt", "")
        title = item.get("title", "")
        
        # 1. 检查内容长度（至少 200 字符）
        if len(content) < 200:
            removed_count += 1
            logger.debug(f"Removed (too short): {title[:50]} - {len(content)} chars")
            continue
        
        # 2. 检查是否有结构性内容
        has_structure = False
        
        # 有代码块
        if re.search(r'```[\s\S]*?```', content):
            has_structure = True
        # 有编号列表
        elif re.search(r'\d+\.\s+[A-Z]', content):
            has_structure = True
        # 有 Markdown 标题
        elif re.search(r'^#+\s+[A-Z]', content, re.MULTILINE):
            has_structure = True
        # 有引用
        elif re.search(r'>\s+[A-Z]', content):
            has_structure = True
        # 有明显的段落结构（多个段落）
        elif len([p for p in content.split('\n\n') if len(p.strip()) > 50]) >= 2:
            has_structure = True
        
        # 3. 检查是否包含提示词相关内容
        is_prompt_related = False
        prompt_keywords = [
            'prompt', '提示词', '提示语',
            'example', '示例',
            'template', '模板',
            'pattern', '模式',
            'guide', '指南', '教程',
            'tutorial', 'how to',
            'step', '步骤',
            'instruction', '指令',
            'best practice', '最佳实践',
            'technique', '技巧',
        ]
        content_lower = content.lower()
        for keyword in prompt_keywords:
            if keyword in content_lower or keyword.lower() in content_lower:
                is_prompt_related = True
                break
        
        # 4. 检查是否主要是导航或列表
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if len(lines) > 0:
            # 如果大部分是短行（<50 字符），可能是导航
            short_lines = sum(1 for line in lines if len(line) < 50)
            if short_lines / len(lines) > 0.8:
                removed_count += 1
                logger.debug(f"Removed (navigation-like): {title[:50]}")
                continue
            
            # 如果大部分是链接列表
            link_lines = sum(1 for line in lines if line.startswith(('http', 'https', 'www.')))
            if link_lines / len(lines) > 0.5:
                removed_count += 1
                logger.debug(f"Removed (link list): {title[:50]}")
                continue
        
        # 5. 综合判断
        if has_structure and is_prompt_related:
            # 保留有结构且相关的
            cleaned.append(item)
        elif has_structure and len(content) > 500:
            # 有结构但可能不相关，但内容较长，保留
            cleaned.append(item)
        elif not has_structure:
            # 无结构，过滤
            removed_count += 1
            logger.debug(f"Removed (no structure): {title[:50]}")
        else:
            # 其他情况，过滤
            removed_count += 1
            logger.debug(f"Removed (other): {title[:50]}")
    
    stats = {
        "total": len(items),
        "removed": removed_count,
        "kept": len(cleaned),
        "removal_rate": f"{removed_count / len(items) * 100:.1f}%" if len(items) > 0 else "0%"
    }
    
    logger.info(f"Low-quality content removed: {removed_count}/{len(items)} ({stats['removal_rate']})")
    
    return cleaned, stats

# ==================== 数据存储 ====================

def save_cleaned(items: List[Dict[str, Any]], filepath: Path) -> int:
    """保存清洗后的数据到 JSONL 文件"""
    saved_count = 0
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
                saved_count += 1
        
        logger.debug(f"Saved {saved_count} cleaned items to {filepath}")
        return saved_count
    except Exception as e:
        logger.error(f"Failed to save to {filepath}: {e}")
        return 0

# ==================== 主流程 ====================

def main():
    """主流程"""
    logger.info("Starting data cleaning...")
    
    # 1. 读取分类的数据
    jsonl_files = list(Config.CLASSIFIED_DIR.glob("*.jsonl"))
    
    if not jsonl_files:
        logger.warning("No classified data found")
        return {}
    
    # 读取最新的文件
    latest_file = max(jsonl_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Reading from {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        items = [json.loads(line) for line in f]
    
    logger.info(f"Loaded {len(items)} items")
    
    # 2. 执行清洗流程
    all_stats = {}
    cleaned_items = items
    
    # 2.1 去除空内容
    cleaned_items, stats = clean_empty_content(cleaned_items)
    all_stats["empty_content"] = stats
    
    # 2.2 去除太短的内容
    cleaned_items, stats = clean_too_short(cleaned_items, Config.MIN_CONTENT_LENGTH)
    all_stats["too_short"] = stats
    
    # 2.3 去除重复内容
    cleaned_items, stats = clean_duplicates(cleaned_items)
    all_stats["duplicates"] = stats
    
    # 2.4 去除导航和页脚
    cleaned_items, stats = clean_navigation_footer(cleaned_items)
    all_stats["navigation_footer"] = stats
    
    # 2.5 去除特殊格式
    cleaned_items, stats = clean_special_format(cleaned_items)
    all_stats["special_format"] = stats
    
    # 2.6 过滤低质量内容（新增）
    cleaned_items, stats = clean_low_quality_content(cleaned_items)
    all_stats["low_quality"] = stats
    
    # 3. 保存结果
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = Config.CLEANED_DIR / f"cleaned-{timestamp}.jsonl"
    saved_count = save_cleaned(cleaned_items, output_file)
    
    # 4. 生成报告
    report = {
        "timestamp": timestamp,
        "input_file": str(latest_file),
        "input_count": len(items),
        "output_file": str(output_file),
        "output_count": len(cleaned_items),
        "saved_count": saved_count,
        "total_removed": len(items) - len(cleaned_items),
        "removal_rate": f"{(len(items) - len(cleaned_items)) / len(items) * 100:.1f}%" if len(items) > 0 else "0%",
        "cleaning_steps": all_stats
    }
    
    logger.info(f"Cleaning completed: {len(cleaned_items)} items saved to {output_file}")
    logger.info(f"Total removed: {len(items) - len(cleaned_items)} ({report['removal_rate']})")
    
    # 保存报告
    report_file = Config.CLEANED_DIR / f"report-{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Report saved to {report_file}")
    
    return report


if __name__ == "__main__":
    main()
