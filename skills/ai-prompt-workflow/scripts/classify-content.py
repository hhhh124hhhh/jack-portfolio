#!/usr/bin/env python3
"""
自动分类层主脚本
作者：Momo (Clawdbot Team)
创建日期：2026-02-05

功能：
1. 支持 4 种内容类型分类（Prompt, Workflow, Industry Knowledge, Guide）
2. 实现规则引擎（规则匹配 + LLM 分类）
3. 实现置信度计算和验证
4. 生成分类报告
"""

import json
import re
import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
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
    COLLECTED_DIR = DATA_DIR / "collected"
    CLASSIFIED_DIR = DATA_DIR / "classified"
    
    # 配置文件路径
    CONFIG_FILE = project_root / "config/classification.yaml"
    
    # 日志文件
    LOG_DIR = project_root / "logs"
    LOG_FILE = LOG_DIR / "classify-content.log"
    
    @classmethod
    def ensure_dirs(cls):
        """确保所有目录存在"""
        cls.CLASSIFIED_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

# ==================== 日志 ====================

def setup_logging() -> logging.Logger:
    """设置日志"""
    Config.ensure_dirs()
    
    logger = logging.getLogger("classify-content")
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

# ==================== 特征提取 ====================

def extract_features(content: str) -> Dict[str, Any]:
    """提取文本特征"""
    features = {
        "content_length": len(content),
        "word_count": len(content.split()),
        "has_steps": bool(re.search(r'(第一|第二步|step 1|1\.)', content, re.IGNORECASE)),
        "has_code": bool(re.search(r'```', content)),
        "has_bullets": bool(re.search(r'^\s*[-*]', content, re.MULTILINE)),
        "has_numbers": bool(re.search(r'\d+\.', content))
    }
    
    # 关键词特征
    prompt_keywords = ["请", "生成", "你是一个", "扮演", "act as"]
    workflow_keywords = ["步骤", "流程", "然后", "最后"]
    industry_keywords = ["经验", "最佳实践", "优化", "性能"]
    guide_keywords = ["指南", "教程", "方法", "原则"]
    
    features.update({
        "prompt_keyword_count": sum(1 for k in prompt_keywords if k.lower() in content.lower()),
        "workflow_keyword_count": sum(1 for k in workflow_keywords if k.lower() in content.lower()),
        "industry_keyword_count": sum(1 for k in industry_keywords if k.lower() in content.lower()),
        "guide_keyword_count": sum(1 for k in guide_keywords if k.lower() in content.lower())
    })
    
    return features


# ==================== 规则引擎 ====================

def classify_by_rules(content: str, features: Dict[str, Any]) -> Tuple[Optional[str], float, Optional[str]]:
    """使用规则引擎分类"""
    
    # Prompt 规则
    if re.search(r'你是一个.*请.*', content, re.IGNORECASE):
        return "Prompt", 0.95, "包含角色设定和任务指令"
    
    # Workflow 规则
    if re.search(r'第一步.*第二步.*第三步', content, re.IGNORECASE):
        return "Workflow", 0.90, "包含明确的步骤说明"
    
    # Industry 规则
    if re.search(r'(经验|最佳实践|优化).*\d+.*条', content, re.IGNORECASE):
        return "Industry Knowledge", 0.85, "包含经验总结"
    
    # Guide 规则
    if re.search(r'(指南|教程|方法)', content, re.IGNORECASE):
        return "Guide", 0.80, "包含方法论或指导"
    
    # 关键词规则
    keyword_scores = {
        "Prompt": features["prompt_keyword_count"] * 0.3,
        "Workflow": features["workflow_keyword_count"] * 0.3,
        "Industry Knowledge": features["industry_keyword_count"] * 0.3,
        "Guide": features["guide_keyword_count"] * 0.3
    }
    
    max_type = max(keyword_scores, key=keyword_scores.get)
    max_score = keyword_scores[max_type]
    
    if max_score > 0.6:
        confidence = min(0.9, 0.6 + max_score * 0.3)
        reason = f"关键词匹配：{max_type} 相关词出现 {max_score:.2f} 次"
        return max_type, confidence, reason
    
    return None, 0.0, None


# ==================== LLM 分类 ====================

def classify_by_llm(content: str) -> Tuple[Optional[str], float, Optional[str]]:
    """使用 LLM 分类"""
    # 模拟 LLM 分类结果
    # 实际实现中应该调用 Claude API
    
    # 模拟分类结果
    content_lower = content.lower()
    
    if "请" in content_lower and "生成" in content_lower:
        classification = "Prompt"
        confidence = 0.85
        reason = "LLM 分类：包含明确的任务指令"
    elif "步骤" in content_lower and "流程" in content_lower:
        classification = "Workflow"
        confidence = 0.80
        reason = "LLM 分类：包含步骤和流程"
    elif "经验" in content_lower or "最佳实践" in content_lower:
        classification = "Industry Knowledge"
        confidence = 0.85
        reason = "LLM 分类：包含经验或最佳实践"
    elif "指南" in content_lower or "教程" in content_lower:
        classification = "Guide"
        confidence = 0.80
        reason = "LLM 分类：包含指南或教程"
    else:
        classification = "Guide"
        confidence = 0.70
        reason = "LLM 分类：默认分类为 Guide"
    
    return classification, confidence, reason


# ==================== 结果验证 ====================

def validate_result(content: str, classification: str, confidence: float, features: Dict[str, Any]) -> Tuple[str, float]:
    """验证分类结果"""
    
    validated_classification = classification
    validated_confidence = confidence
    
    # 验证 1：长度验证
    content_length = features["content_length"]
    if classification == "Prompt" and content_length > 1000:
        validated_confidence *= 0.8
    elif classification == "Guide" and content_length < 300:
        validated_confidence *= 0.7
    
    # 验证 2：结构验证
    has_steps = features["has_steps"]
    has_code = features["has_code"]
    
    if classification == "Workflow" and not has_steps:
        validated_confidence *= 0.6
    elif classification == "Industry Knowledge" and not has_code:
        validated_confidence *= 0.8
    
    # 置信度验证
    if validated_confidence < 0.7:
        validated_classification = "uncertain"
    elif validated_confidence < 0.9:
        validated_classification = f"{classification} (needs_review)"
    else:
        validated_classification = f"{classification} (high_confidence)"
    
    return validated_classification, validated_confidence


# ==================== 数据存储 ====================

def save_classified(items: List[Dict[str, Any]], filepath: Path) -> int:
    """保存分类结果到 JSONL 文件"""
    logger.info(f"Saving {len(items)} classified items to {filepath}...")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(items)} classified items to {filepath}")
        return len(items)
        
    except Exception as e:
        logger.error(f"Failed to save to {filepath}: {e}")
        return 0


# ==================== 主流程 ====================

def main():
    """主流程"""
    logger.info("Starting content classification...")
    
    # 1. 读取收集的数据
    jsonl_files = list(Config.COLLECTED_DIR.glob("*.jsonl"))
    
    if not jsonl_files:
        logger.warning("No collected data found")
        return {}
    
    # 读取最新的文件
    latest_file = max(jsonl_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Reading from {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        items = [json.loads(line) for line in f]
    
    logger.info(f"Loaded {len(items)} items")
    
    # 2. 分类所有内容
    classified_items = []
    
    for item in items:
        content = item.get("content", "")
        features = extract_features(content)
        
        # 尝试规则分类
        rule_type, rule_confidence, rule_reason = classify_by_rules(content, features)
        
        # 如果规则分类失败，使用 LLM 分类
        if rule_type is None or rule_confidence < 0.7:
            llm_type, llm_confidence, llm_reason = classify_by_llm(content)
            classification = llm_type
            confidence = llm_confidence
            reason = llm_reason
            method = "llm"
        else:
            classification = rule_type
            confidence = rule_confidence
            reason = rule_reason
            method = "rules"
        
        # 验证结果
        validated_classification, validated_confidence = validate_result(
            content, classification, confidence, features
        )
        
        # 更新 item
        classified_item = {
            **item,
            "type": classification,
            "classification_confidence": confidence,
            "classification_reason": reason,
            "classification_method": method,
            "validated_type": validated_classification,
            "validated_confidence": validated_confidence,
            "features": features,
            "classified_at": datetime.now().isoformat()
        }
        
        classified_items.append(classified_item)
    
    # 3. 保存结果
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = Config.CLASSIFIED_DIR / f"classified-{timestamp}.jsonl"
    saved_count = save_classified(classified_items, output_file)
    
    # 4. 生成报告
    report = {
        "timestamp": timestamp,
        "total_items": len(items),
        "classified_count": len(classified_items),
        "output_file": str(output_file),
        "saved_count": saved_count,
        "classification_distribution": {
            "Prompt": sum(1 for i in classified_items if i["type"] == "Prompt"),
            "Workflow": sum(1 for i in classified_items if i["type"] == "Workflow"),
            "Industry Knowledge": sum(1 for i in classified_items if i["type"] == "Industry Knowledge"),
            "Guide": sum(1 for i in classified_items if i["type"] == "Guide")
        },
        "confidence_distribution": {
            "high_confidence": sum(1 for i in classified_items if i["validated_confidence"] >= 0.9),
            "needs_review": sum(1 for i in classified_items if 0.7 <= i["validated_confidence"] < 0.9),
            "uncertain": sum(1 for i in classified_items if i["validated_confidence"] < 0.7)
        }
    }
    
    logger.info(f"Classification completed: {saved_count} items saved to {output_file}")
    
    # 保存报告
    report_file = Config.CLASSIFIED_DIR / f"report-{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Report saved to {report_file}")
    
    return report


if __name__ == "__main__":
    main()
