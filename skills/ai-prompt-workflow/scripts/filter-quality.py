#!/usr/bin/env python3
"""
质量筛选层主脚本
作者：Momo (Clawdbot Team)
创建日期：2026-02-05

功能：
1. 实现 4 种筛选规则（阈值、去重、合规性、完整性）
2. 实现人工审核机制（Slack 通知）
3. 生成筛选报告
"""

import json
import hashlib
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any, Tuple, Set
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
    SCORED_DIR = DATA_DIR / "scored"
    FILTERED_DIR = DATA_DIR / "filtered"
    NEEDS_REVIEW_DIR = DATA_DIR / "needs_review"
    
    # 配置文件路径
    CONFIG_FILE = project_root / "config/quality-filter.yaml"
    
    # 日志文件
    LOG_DIR = project_root / "logs"
    LOG_FILE = LOG_DIR / "filter-quality.log"
    
    @classmethod
    def ensure_dirs(cls):
        """确保所有目录存在"""
        cls.FILTERED_DIR.mkdir(parents=True, exist_ok=True)
        cls.NEEDS_REVIEW_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

# ==================== 日志 ====================

def setup_logging() -> logging.Logger:
    """设置日志"""
    Config.ensure_dirs()
    
    logger = logging.getLogger("filter-quality")
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

# ==================== 筛选规则 ====================

def filter_by_threshold(items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """阈值筛选"""
    logger.info("Running threshold filter...")
    
    filtered_items = []
    low_quality_count = 0
    
    for item in items:
        total_score = item.get("total_score", 0)
        threshold = item.get("threshold", 70)
        quality_level = item.get("quality_level", "low")
        
        # 只保留 high 和 medium 质量
        if quality_level in ["high", "medium"]:
            filtered_items.append(item)
        else:
            low_quality_count += 1
            item_id = item.get('id', item.get('url', 'unknown'))
            logger.debug(f"Threshold filter: {item_id} (score={total_score}, level={quality_level})")
    
    logger.info(f"Threshold filter: {len(filtered_items)} passed, {low_quality_count} filtered out")
    
    stats = {
        "total_items": len(items),
        "passed_items": len(filtered_items),
        "filtered_out": low_quality_count,
        "filter_rate": f"{low_quality_count / len(items) * 100:.1f}%" if len(items) > 0 else "N/A"
    }
    
    return filtered_items, stats


def deduplicate_by_content(items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """内容去重（MD5）"""
    logger.info("Running content deduplication...")
    
    seen_md5 = set()
    unique_items = []
    duplicates = 0
    
    for item in items:
        content = item.get("content", "")
        md5_hash = hashlib.md5(content.encode()).hexdigest()
        
        if md5_hash not in seen_md5:
            seen_md5.add(md5_hash)
            unique_items.append(item)
        else:
            duplicates += 1
            logger.debug(f"MD5 duplicate found: {item['id']}")
    
    logger.info(f"Content deduplication: {len(unique_items)} unique, {duplicates} duplicates removed")
    
    stats = {
        "total_items": len(items),
        "unique_items": len(unique_items),
        "duplicates": duplicates,
        "dedup_rate": f"{duplicates / len(items) * 100:.1f}%"
    }
    
    return unique_items, stats


def filter_by_compliance(items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """合规性筛选（NSFW, 政治敏感）"""
    logger.info("Running compliance filter...")
    
    nsfw_keywords = ["nsfw", "adult", "porn", "sex", "xxx"]
    political_keywords = ["政治", "government", "politics", "war", "terrorism"]
    
    compliant_items = []
    non_compliant_items = []
    non_compliant_count = 0
    
    for item in items:
        content = item.get("content", "").lower()
        title = item.get("title", "").lower()
        text = f"{content} {title}"
        
        # 检查 NSFW
        is_nsfw = any(keyword in text for keyword in nsfw_keywords)
        
        # 检查政治敏感
        is_political = any(keyword in text for keyword in political_keywords)
        
        if is_nsfw or is_political:
            # 标记为不合规
            item["compliance_status"] = "non_compliant"
            item["compliance_reason"] = "NSFW" if is_nsfw else "political_sensitive"
            non_compliant_items.append(item)
            non_compliant_count += 1
            logger.debug(f"Compliance filter: {item['id']} ({item['compliance_reason']})")
        else:
            # 标记为合规
            item["compliance_status"] = "compliant"
            item["compliance_reason"] = "passed"
            compliant_items.append(item)
    
    logger.info(f"Compliance filter: {len(compliant_items)} compliant, {non_compliant_count} non_compliant")
    
    stats = {
        "total_items": len(items),
        "compliant_items": len(compliant_items),
        "non_compliant_items": non_compliant_count,
        "compliance_rate": f"{len(compliant_items) / len(items) * 100:.1f}%"
    }
    
    return compliant_items, non_compliant_items, stats


def filter_by_completeness(items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """完整性筛选"""
    logger.info("Running completeness filter...")
    
    complete_items = []
    incomplete_items = []
    incomplete_count = 0
    
    for item in items:
        content = item.get("content", "")
        title = item.get("title", "")
        
        # 必需字段检查
        has_content = len(content.strip()) > 10
        has_title = len(title.strip()) > 0
        has_type = item.get("type") is not None
        
        # 内容类型特定检查
        content_type = item.get("type", "Guide")
        type_specific_checks = True
        
        if content_type == "Prompt":
            # Prompt 需要明确的任务指令
            type_specific_checks = any(keyword in content.lower() for keyword in ["请", "生成", "创建"])
        elif content_type == "Workflow":
            # Workflow 需要步骤
            type_specific_checks = "步骤" in content.lower() or "step" in content.lower()
        elif content_type == "Guide":
            # Guide 需要结构
            type_specific_checks = "##" in content or "###" in content
        
        if has_content and has_title and has_type and type_specific_checks:
            item["completeness_status"] = "complete"
            complete_items.append(item)
        else:
            # 标记为不完整
            missing_fields = []
            if not has_content:
                missing_fields.append("content")
            if not has_title:
                missing_fields.append("title")
            if not has_type:
                missing_fields.append("type")
            if not type_specific_checks:
                missing_fields.append(f"{content_type}_specific_structure")
            
            item["completeness_status"] = "incomplete"
            item["completeness_reason"] = f"Missing: {', '.join(missing_fields)}"
            incomplete_items.append(item)
            incomplete_count += 1
            logger.debug(f"Completeness filter: {item['id']} ({item['completeness_reason']})")
    
    logger.info(f"Completeness filter: {len(complete_items)} complete, {incomplete_count} incomplete")
    
    stats = {
        "total_items": len(items),
        "complete_items": len(complete_items),
        "incomplete_items": incomplete_count,
        "completeness_rate": f"{len(complete_items) / len(items) * 100:.1f}%"
    }
    
    return complete_items, incomplete_items, stats


# ==================== 人工审核机制 ====================

def identify_needs_review(items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """识别需要人工审核的内容"""
    logger.info("Identifying items needing review...")
    
    needs_review = []
    auto_approve = []
    
    for item in items:
        # 规则 1：低置信度分类
        if item.get("validated_confidence", 1.0) < 0.7:
            item["review_reason"] = "low_classification_confidence"
            needs_review.append(item)
            continue
        
        # 规则 2：中等质量
        if item.get("quality_level") == "medium":
            item["review_reason"] = "medium_quality"
            needs_review.append(item)
            continue
        
        # 规则 3：长度异常
        content_length = len(item.get("content", ""))
        if content_length > 2000 or content_length < 50:
            item["review_reason"] = "unusual_length"
            needs_review.append(item)
            continue
        
        # 规则 4：缺少关键字段
        if item.get("completeness_status") == "incomplete":
            item["review_reason"] = "incomplete_fields"
            needs_review.append(item)
            continue
        
        # 自动批准
        auto_approve.append(item)
    
    logger.info(f"Review identification: {len(needs_review)} need review, {len(auto_approve)} auto approved")
    
    return needs_review, auto_approve


def send_to_slack_for_review(items: List[Dict[str, Any]]) -> int:
    """发送到 Slack 人工审核"""
    logger.info(f"Sending {len(items)} items to Slack for review...")
    
    # 模拟 Slack 通知
    # 实际实现中应该调用 Slack API
    
    for item in items[:5]:  # 只发送前 5 个用于演示
        item_id = item.get('id', item.get('url', 'unknown'))
        logger.info(f"Review item: {item_id} - {item['review_reason']}")
    
    logger.info(f"Sent {min(5, len(items))} items to Slack for review (demo)")
    
    return len(items)


# ==================== 数据存储 ====================

def save_filtered(items: List[Dict[str, Any]], filepath: Path) -> int:
    """保存筛选结果到 JSONL 文件"""
    logger.info(f"Saving {len(items)} filtered items to {filepath}...")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(items)} filtered items to {filepath}")
        return len(items)
        
    except Exception as e:
        logger.error(f"Failed to save to {filepath}: {e}")
        return 0


# ==================== 主流程 ====================

def main():
    """主流程"""
    logger.info("Starting quality filtering...")
    
    # 1. 读取评分的数据
    jsonl_files = list(Config.SCORED_DIR.glob("*.jsonl"))
    
    if not jsonl_files:
        logger.warning("No scored data found")
        return {}
    
    # 读取最新的文件
    latest_file = max(jsonl_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Reading from {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        items = [json.loads(line) for line in f]
    
    logger.info(f"Loaded {len(items)} items")
    
    # 2. 应用筛选规则
    all_items = items
    
    # 规则 1：阈值筛选
    threshold_passed, threshold_stats = filter_by_threshold(all_items)
    all_items = threshold_passed
    
    # 规则 2：去重
    deduplicated, dedup_stats = deduplicate_by_content(all_items)
    all_items = deduplicated
    
    # 规则 3：合规性筛选
    compliant, non_compliant, compliance_stats = filter_by_compliance(all_items)
    all_items = compliant
    
    # 规则 4：完整性筛选
    complete, incomplete, completeness_stats = filter_by_completeness(all_items)
    all_items = complete
    
    # 3. 识别需要人工审核的内容
    needs_review, auto_approved = identify_needs_review(all_items)
    
    # 发送到 Slack
    review_count = send_to_slack_for_review(needs_review)
    
    # 4. 保存结果
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = Config.FILTERED_DIR / f"filtered-{timestamp}.jsonl"
    saved_count = save_filtered(auto_approved, output_file)
    
    # 保存需要审核的内容
    needs_review_file = Config.NEEDS_REVIEW_DIR / f"needs-review-{timestamp}.jsonl"
    save_filtered(needs_review, needs_review_file)
    
    # 5. 生成报告
    report = {
        "timestamp": timestamp,
        "total_items": len(items),
        "output_file": str(output_file),
        "saved_count": saved_count,
        "threshold_filter": threshold_stats,
        "deduplication": dedup_stats,
        "compliance_filter": compliance_stats,
        "completeness_filter": completeness_stats,
        "review_identification": {
            "needs_review_count": len(needs_review),
            "auto_approved_count": len(auto_approved),
            "sent_to_slack": review_count,
            "needs_review_file": str(needs_review_file)
        }
    }
    
    logger.info(f"Filtering completed: {saved_count} items saved to {output_file}")
    
    # 保存报告
    report_file = Config.FILTERED_DIR / f"report-{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Report saved to {report_file}")
    
    return report


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    main()
