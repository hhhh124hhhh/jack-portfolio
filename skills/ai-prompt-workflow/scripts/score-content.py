#!/usr/bin/env python3
"""
分类评分层主脚本
作者：Momo (Clawdbot Team)
创建日期：2026-02-05

功能：
1. 实现 4 种内容类型的差异化评分
2. 实现多维度评分（实用性、清晰度、独特性等）
3. 实现评分阈值设计
4. 生成评分报告
"""

import json
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any, Tuple
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
    SCORED_DIR = DATA_DIR / "scored"
    
    # 配置文件路径
    CONFIG_FILE = project_root / "config/scoring-standards.yaml"
    
    # 日志文件
    LOG_DIR = project_root / "logs"
    LOG_FILE = LOG_DIR / "score-content.log"
    
    @classmethod
    def ensure_dirs(cls):
        """确保所有目录存在"""
        cls.SCORED_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

# ==================== 日志 ====================

def setup_logging() -> logging.Logger:
    """设置日志"""
    Config.ensure_dirs()
    
    logger = logging.getLogger("score-content")
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

# ==================== 评分函数 ====================

def score_prompt(content: str, features: Dict[str, Any]) -> Dict[str, Any]:
    """Prompt 类型评分"""
    
    scores = {}
    
    # 1. 实用性 (50%): 0-50 分
    practicality = 0
    
    # 有明确的任务指令
    if any(keyword in content.lower() for keyword in ["请", "生成", "创建", "写"]):
        practicality += 15
    
    # 有明确的输出要求
    if any(keyword in content.lower() for keyword in ["输出", "结果", "格式"]):
        practicality += 10
    
    # 有具体的应用场景
    if any(keyword in content.lower() for keyword in ["场景", "例子", "案例"]):
        practicality += 10
    
    # 长度适中（50-500 字符）
    content_length = len(content)
    if 50 <= content_length <= 500:
        practicality += 10
    elif content_length > 500:
        practicality += 5
    
    # 有角色设定
    if "你是一个" in content.lower():
        practicality += 5
    
    scores["实用性"] = min(50, practicality)
    
    # 2. 清晰度 (30%): 0-30 分
    clarity = 0
    
    # 结构清晰
    if features.get("has_bullets", False):
        clarity += 10
    
    if features.get("has_numbers", False):
        clarity += 5
    
    # 逻辑连贯
    if "然后" in content.lower() or "接下来" in content.lower():
        clarity += 5
    
    # 明确的步骤
    if "第一步" in content.lower() or "1." in content:
        clarity += 5
    
    # 无歧义
    content_lower = content.lower()
    ambiguity_keywords = ["可能", "也许", "大概", "或者"]
    if not any(k in content_lower for k in ambiguity_keywords):
        clarity += 5
    
    scores["清晰度"] = min(30, clarity)
    
    # 3. 独特性 (20%): 0-20 分
    uniqueness = 0
    
    # 有独特的角度或方法
    if any(keyword in content.lower() for keyword in ["独特", "创新", "新颖", "原创"]):
        uniqueness += 10
    
    # 不是常见的通用模板
    if not any(keyword in content.lower() for keyword in ["简单", "基础", "基本"]):
        uniqueness += 5
    
    # 有具体的领域应用
    domain_keywords = ["编程", "写作", "设计", "商业", "营销", "教育"]
    if any(k in content.lower() for k in domain_keywords):
        uniqueness += 5
    
    scores["独特性"] = min(20, uniqueness)
    
    return scores


def score_workflow(content: str, features: Dict[str, Any]) -> Dict[str, Any]:
    """Workflow 类型评分"""
    
    scores = {}
    
    # 1. 完整性 (30%): 0-30 分
    completeness = 0
    
    # 有明确的步骤
    if re.search(r'(第一步|step 1|1\.)', content, re.IGNORECASE):
        completeness += 10
    
    # 有多个步骤
    step_count = len(re.findall(r'(第二步|step 2|2\.)', content, re.IGNORECASE))
    if step_count >= 2:
        completeness += 10
    elif step_count >= 1:
        completeness += 5
    
    # 有明确的开始和结束
    if "开始" in content.lower() and "结束" in content.lower():
        completeness += 5
    
    # 有预期的结果说明
    if "结果" in content.lower() or "输出" in content.lower():
        completeness += 5
    
    scores["完整性"] = min(30, completeness)
    
    # 2. 可扩展性 (20%): 0-20 分
    extensibility = 0
    
    # 可以添加更多步骤
    if "可以" in content.lower() or "可选" in content.lower():
        extensibility += 10
    
    # 有参数化设计
    if "参数" in content.lower() or "配置" in content.lower():
        extensibility += 5
    
    # 有自定义选项
    if "自定义" in content.lower() or "修改" in content.lower():
        extensibility += 5
    
    scores["可扩展性"] = min(20, extensibility)
    
    # 3. 实用性 (30%): 0-30 分
    practicality = 0
    
    # 有实际应用场景
    if any(keyword in content.lower() for keyword in ["场景", "用途", "应用"]):
        practicality += 10
    
    # 有工具或资源说明
    if any(keyword in content.lower() for keyword in ["工具", "资源", "库"]):
        practicality += 10
    
    # 有常见问题的解决方案
    if any(keyword in content.lower() for keyword in ["问题", "错误", "bug"]):
        practicality += 5
    
    # 有注意事项
    if any(keyword in content.lower() for keyword in ["注意", "提醒", "警告"]):
        practicality += 5
    
    scores["实用性"] = min(30, practicality)
    
    # 4. 可复用性 (20%): 0-20 分
    reusability = 0
    
    # 有通用性
    if "通用" in content.lower() or "广泛" in content.lower():
        reusability += 10
    
    # 有模板化设计
    if "模板" in content.lower():
        reusability += 5
    
    # 有独立模块
    if "模块" in content.lower() or "组件" in content.lower():
        reusability += 5
    
    scores["可复用性"] = min(20, reusability)
    
    return scores


def score_industry(content: str, features: Dict[str, Any]) -> Dict[str, Any]:
    """Industry Knowledge 类型评分"""
    
    scores = {}
    
    # 1. 专业深度 (40%): 0-40 分
    depth = 0
    
    # 有专业知识
    if any(keyword in content.lower() for keyword in ["经验", "实践", "专业"]):
        depth += 15
    
    # 有具体数据或案例
    if any(keyword in content.lower() for keyword in ["数据", "案例", "统计"]):
        depth += 10
    
    # 有技术细节
    if features.get("has_code", False):
        depth += 10
    
    # 有深入分析
    if any(keyword in content.lower() for keyword in ["分析", "研究", "探索"]):
        depth += 5
    
    scores["专业深度"] = min(40, depth)
    
    # 2. 实用性 (40%): 0-40 分
    practicality = 0
    
    # 有最佳实践
    if "最佳实践" in content.lower():
        practicality += 15
    
    # 有优化建议
    if any(keyword in content.lower() for keyword in ["优化", "改进", "提升"]):
        practicality += 10
    
    # 有具体操作步骤
    if "步骤" in content.lower() or "方法" in content.lower():
        practicality += 10
    
    # 有效果验证
    if any(keyword in content.lower() for keyword in ["验证", "测试", "检查"]):
        practicality += 5
    
    scores["实用性"] = min(40, practicality)
    
    # 3. 系统性 (20%): 0-20 分
    systematic = 0
    
    # 有系统性框架
    if any(keyword in content.lower() for keyword in ["框架", "体系", "模型"]):
        systematic += 10
    
    # 有层次结构
    if features.get("has_bullets", False) and features.get("has_numbers", False):
        systematic += 5
    
    # 有总结和展望
    if "总结" in content.lower() or "展望" in content.lower():
        systematic += 5
    
    scores["系统性"] = min(20, systematic)
    
    return scores


def score_guide(content: str, features: Dict[str, Any]) -> Dict[str, Any]:
    """Guide 类型评分"""
    
    scores = {}
    
    # 1. 指导性 (40%): 0-40 分
    directiveness = 0
    
    # 有明确的指导
    if any(keyword in content.lower() for keyword in ["指南", "教程", "指导"]):
        directiveness += 15
    
    # 有步骤说明
    if "步骤" in content.lower() or "方法" in content.lower():
        directiveness += 10
    
    # 有示例
    if any(keyword in content.lower() for keyword in ["示例", "例子", "例"]):
        directiveness += 10
    
    # 有常见问题解答
    if any(keyword in content.lower() for keyword in ["问题", "faq", "常见问题"]):
        directiveness += 5
    
    scores["指导性"] = min(40, directiveness)
    
    # 2. 结构性 (30%): 0-30 分
    structure = 0
    
    # 有清晰的章节结构
    if features.get("has_bullets", False):
        structure += 10
    
    if features.get("has_numbers", False):
        structure += 10
    
    # 有标题或小标题
    if any(keyword in content.lower() for keyword in ["第一章", "##", "###"]):
        structure += 10
    
    scores["结构性"] = min(30, structure)
    
    # 3. 实用性 (30%): 0-30 分
    practicality = 0
    
    # 有实际应用
    if any(keyword in content.lower() for keyword in ["应用", "场景", "用途"]):
        practicality += 10
    
    # 有工具或资源推荐
    if any(keyword in content.lower() for keyword in ["工具", "资源", "推荐"]):
        practicality += 10
    
    # 有注意事项
    if any(keyword in content.lower() for keyword in ["注意", "提醒", "警告"]):
        practicality += 5
    
    # 有后续学习建议
    if any(keyword in content.lower() for keyword in ["学习", "进阶", "深入"]):
        practicality += 5
    
    scores["实用性"] = min(30, practicality)
    
    return scores


# ==================== 主评分函数 ====================

def score_content(item: Dict[str, Any]) -> Dict[str, Any]:
    """根据内容类型进行差异化评分"""
    
    content = item.get("content", "")
    content_type = item.get("type", "Guide")
    features = item.get("features", {})
    
    # 根据类型选择评分函数
    if content_type == "Prompt":
        scores = score_prompt(content, features)
        threshold = 70
    elif content_type == "Workflow":
        scores = score_workflow(content, features)
        threshold = 65
    elif content_type == "Industry Knowledge":
        scores = score_industry(content, features)
        threshold = 70
    elif content_type == "Guide":
        scores = score_guide(content, features)
        threshold = 75
    else:
        # 默认使用 Guide 评分
        scores = score_guide(content, features)
        threshold = 75
    
    # 计算总分
    total_score = sum(scores.values())
    
    # 确定质量等级
    if total_score >= threshold:
        quality_level = "high"
    elif total_score >= threshold - 20:
        quality_level = "medium"
    else:
        quality_level = "low"
    
    # 生成评分理由
    top_scores = sorted(scores.items(), key=lambda x: -x[1])[:2]
    reason = f"优势：{top_scores[0][0]}({top_scores[0][1]}), {top_scores[1][0]}({top_scores[1][1]})"
    
    return {
        "scores": scores,
        "total_score": total_score,
        "threshold": threshold,
        "quality_level": quality_level,
        "scoring_reason": reason,
        "scored_at": datetime.now().isoformat()
    }


# ==================== 数据存储 ====================

def save_scored(items: List[Dict[str, Any]], filepath: Path) -> int:
    """保存评分结果到 JSONL 文件"""
    logger.info(f"Saving {len(items)} scored items to {filepath}...")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(items)} scored items to {filepath}")
        return len(items)
        
    except Exception as e:
        logger.error(f"Failed to save to {filepath}: {e}")
        return 0


# ==================== 主流程 ====================

def main():
    """主流程"""
    logger.info("Starting content scoring...")
    
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
    
    # 2. 评分所有内容
    scored_items = []
    
    for item in items:
        # 评分
        scoring_result = score_content(item)
        
        # 更新 item
        scored_item = {
            **item,
            **scoring_result
        }
        
        scored_items.append(scored_item)
    
    # 3. 保存结果
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = Config.SCORED_DIR / f"scored-{timestamp}.jsonl"
    saved_count = save_scored(scored_items, output_file)
    
    # 4. 生成报告
    report = {
        "timestamp": timestamp,
        "total_items": len(items),
        "scored_count": len(scored_items),
        "output_file": str(output_file),
        "saved_count": saved_count,
        "quality_distribution": {
            "high": sum(1 for i in scored_items if i["quality_level"] == "high"),
            "medium": sum(1 for i in scored_items if i["quality_level"] == "medium"),
            "low": sum(1 for i in scored_items if i["quality_level"] == "low")
        },
        "type_distribution": {
            "Prompt": sum(1 for i in scored_items if i["type"] == "Prompt"),
            "Workflow": sum(1 for i in scored_items if i["type"] == "Workflow"),
            "Industry Knowledge": sum(1 for i in scored_items if i["type"] == "Industry Knowledge"),
            "Guide": sum(1 for i in scored_items if i["type"] == "Guide")
        },
        "average_score": sum(i["total_score"] for i in scored_items) / len(scored_items) if scored_items else 0
    }
    
    logger.info(f"Scoring completed: {saved_count} items saved to {output_file}")
    
    # 保存报告
    report_file = Config.SCORED_DIR / f"report-{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Report saved to {report_file}")
    
    return report


if __name__ == "__main__":
    import re
    main()
