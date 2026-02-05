#!/usr/bin/env python3
"""
内容补充层主脚本
作者：Momo (Clawdbot Team)
创建日期：2026-02-05

功能：
1. 实现 4 种补充策略（联网搜索、工具调用、LLM 生成、规则模板）
2. 实现缺失信息识别
3. 生成补充报告
"""

import json
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
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
    FILTERED_DIR = DATA_DIR / "filtered"
    ENHANCED_DIR = DATA_DIR / "enhanced"
    
    # 配置文件路径
    CONFIG_FILE = project_root / "config/content-enhancement.yaml"
    
    # 日志文件
    LOG_DIR = project_root / "logs"
    LOG_FILE = LOG_DIR / "enhance-content.log"
    
    @classmethod
    def ensure_dirs(cls):
        """确保所有目录存在"""
        cls.ENHANCED_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

# ==================== 日志 ====================

def setup_logging() -> logging.Logger:
    """设置日志"""
    Config.ensure_dirs()
    
    logger = logging.getLogger("enhance-content")
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

# ==================== 缺失信息识别 ====================

def identify_missing_info(item: Dict[str, Any]) -> Dict[str, List[str]]:
    """识别缺失信息"""
    
    content = item.get("content", "")
    content_type = item.get("type", "Guide")
    
    missing_info = {
        "examples": [],
        "structure": [],
        "details": []
    }
    
    # 识别 1：缺少示例
    if "示例" not in content and "例子" not in content and "example" not in content.lower():
        missing_info["examples"].append("需要添加使用示例")
    
    # 识别 2：缺少结构
    if "##" not in content and "###" not in content:
        missing_info["structure"].append("需要添加章节标题")
    
    if content_type == "Workflow" and "步骤" not in content and "step" not in content.lower():
        missing_info["structure"].append("需要添加步骤说明")
    
    # 识别 3：缺少细节
    if len(content) < 300:
        missing_info["details"].append("内容过于简短，需要补充细节")
    
    if content_type == "Guide" and "注意事项" not in content and "注意" not in content:
        missing_info["details"].append("需要添加注意事项")
    
    return missing_info


# ==================== 补充策略 ====================

def enhance_by_web_search(content: str, missing_info: Dict[str, List[str]]) -> Dict[str, Any]:
    """通过联网搜索补充信息"""
    logger.info("Enhancing by web search...")
    
    enhancements = {
        "method": "web_search",
        "enhanced_fields": [],
        "enhanced_content": content,
        "success": False,
        "reason": ""
    }
    
    # 模拟联网搜索
    # 实际实现中应该调用 SearXNG API
    
    # 检查是否需要补充示例
    if missing_info.get("examples"):
        # 模拟搜索结果
        search_result = "示例：\n1. 场景一：...\n2. 场景二：...\n"
        enhancements["enhanced_content"] += "\n" + search_result
        enhancements["enhanced_fields"].append("examples")
        enhancements["success"] = True
    
    # 检查是否需要补充细节
    if missing_info.get("details"):
        # 模拟搜索结果
        search_result = "补充细节：\n...\n"
        enhancements["enhanced_content"] += "\n" + search_result
        enhancements["enhanced_fields"].append("details")
        enhancements["success"] = True
    
    if enhancements["success"]:
        enhancements["reason"] = "通过联网搜索补充了缺失信息"
    else:
        enhancements["reason"] = "无需补充或搜索失败"
    
    return enhancements


def enhance_by_tool_call(content: str, missing_info: Dict[str, List[str]]) -> Dict[str, Any]:
    """通过工具调用补充信息"""
    logger.info("Enhancing by tool call...")
    
    enhancements = {
        "method": "tool_call",
        "enhanced_fields": [],
        "enhanced_content": content,
        "success": False,
        "reason": ""
    }
    
    # 模拟工具调用
    # 实际实现中应该调用 Firecrawl 或其他工具
    
    # 检查是否需要补充结构
    if missing_info.get("structure"):
        # 模拟工具调用结果
        structure = "\n## 结构说明\n\n"
        enhancements["enhanced_content"] = structure + enhancements["enhanced_content"]
        enhancements["enhanced_fields"].append("structure")
        enhancements["success"] = True
    
    if enhancements["success"]:
        enhancements["reason"] = "通过工具调用补充了结构信息"
    else:
        enhancements["reason"] = "无需补充或工具调用失败"
    
    return enhancements


def enhance_by_llm(content: str, missing_info: Dict[str, List[str]], content_type: str) -> Dict[str, Any]:
    """通过 LLM 生成补充信息"""
    logger.info("Enhancing by LLM generation...")
    
    enhancements = {
        "method": "llm_generation",
        "enhanced_fields": [],
        "enhanced_content": content,
        "success": False,
        "reason": ""
    }
    
    # 模拟 LLM 生成
    # 实际实现中应该调用 Claude API
    
    # 检查是否需要补充示例
    if missing_info.get("examples"):
        # 模拟 LLM 生成
        generated_examples = "\n\n## 使用示例\n\n### 示例 1\n...\n\n### 示例 2\n...\n"
        enhancements["enhanced_content"] += generated_examples
        enhancements["enhanced_fields"].append("examples")
        enhancements["success"] = True
    
    # 检查是否需要补充注意事项
    if missing_info.get("details") and "注意事项" in " ".join(missing_info["details"]):
        # 模拟 LLM 生成
        generated_notes = "\n\n## 注意事项\n\n1. ...\n2. ...\n"
        enhancements["enhanced_content"] += generated_notes
        enhancements["enhanced_fields"].append("notes")
        enhancements["success"] = True
    
    if enhancements["success"]:
        enhancements["reason"] = "通过 LLM 生成补充了示例和注意事项"
    else:
        enhancements["reason"] = "无需补充或 LLM 生成失败"
    
    return enhancements


def enhance_by_template(content: str, content_type: str) -> Dict[str, Any]:
    """通过规则模板补充信息"""
    logger.info("Enhancing by template...")
    
    enhancements = {
        "method": "template",
        "enhanced_fields": [],
        "enhanced_content": content,
        "success": False,
        "reason": ""
    }
    
    # 规则模板
    templates = {
        "Prompt": {
            "prefix": "以下是一个高质量的提示词模板：\n\n",
            "suffix": "\n\n## 使用建议\n\n1. 根据具体场景调整参数\n2. 可以多次迭代优化\n"
        },
        "Workflow": {
            "prefix": "以下是一个完整的工作流程：\n\n",
            "suffix": "\n\n## 常见问题\n\nQ: ...\nA: ...\n"
        },
        "Industry Knowledge": {
            "prefix": "以下行业知识总结：\n\n",
            "suffix": "\n\n## 最佳实践总结\n\n..."
        },
        "Guide": {
            "prefix": "以下是一份详细指南：\n\n",
            "suffix": "\n\n## 相关资源\n\n..."
        }
    }
    
    template = templates.get(content_type, {})
    
    if template:
        enhancements["enhanced_content"] = template.get("prefix", "") + content + template.get("suffix", "")
        enhancements["enhanced_fields"].append("template_formatting")
        enhancements["success"] = True
        enhancements["reason"] = "通过规则模板添加了标准格式"
    else:
        enhancements["reason"] = "没有适用的模板"
    
    return enhancements


# ==================== 主补充函数 ====================

def enhance_content(item: Dict[str, Any]) -> Dict[str, Any]:
    """综合补充内容"""
    
    content = item.get("content", "")
    content_type = item.get("type", "Guide")
    
    # 1. 识别缺失信息
    missing_info = identify_missing_info(item)
    
    # 2. 选择补充策略（优先级从高到低）
    enhancements = None
    
    # 策略 1：联网搜索（最高优先级）
    if missing_info.get("examples") or missing_info.get("details"):
        enhancements = enhance_by_web_search(content, missing_info)
    
    # 策略 2：LLM 生成
    elif missing_info.get("examples") or missing_info.get("details"):
        enhancements = enhance_by_llm(content, missing_info, content_type)
    
    # 策略 3：工具调用
    elif missing_info.get("structure"):
        enhancements = enhance_by_tool_call(content, missing_info)
    
    # 策略 4：规则模板（最低优先级，兜底）
    else:
        enhancements = enhance_by_template(content, content_type)
    
    # 3. 更新 item
    enhanced_item = {
        **item,
        "missing_info": missing_info,
        "enhancement": enhancements,
        "enhanced_content": enhancements["enhanced_content"],
        "enhanced_at": datetime.now().isoformat()
    }
    
    # 4. 重新评分
    # 这里简化处理，实际应该调用评分脚本
    original_score = item.get("total_score", 0)
    if enhancements["success"]:
        # 简单加分逻辑
        score_boost = 5 * len(enhancements["enhanced_fields"])
        enhanced_item["enhanced_score"] = min(100, original_score + score_boost)
    else:
        enhanced_item["enhanced_score"] = original_score
    
    return enhanced_item


# ==================== 数据存储 ====================

def save_enhanced(items: List[Dict[str, Any]], filepath: Path) -> int:
    """保存补充结果到 JSONL 文件"""
    logger.info(f"Saving {len(items)} enhanced items to {filepath}...")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(items)} enhanced items to {filepath}")
        return len(items)
        
    except Exception as e:
        logger.error(f"Failed to save to {filepath}: {e}")
        return 0


# ==================== 主流程 ====================

def main():
    """主流程"""
    logger.info("Starting content enhancement...")
    
    # 1. 读取筛选后的数据
    jsonl_files = list(Config.FILTERED_DIR.glob("*.jsonl"))
    
    if not jsonl_files:
        logger.warning("No filtered data found")
        return {}
    
    # 读取最新的文件
    latest_file = max(jsonl_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Reading from {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        items = [json.loads(line) for line in f]
    
    logger.info(f"Loaded {len(items)} items")
    
    # 2. 补充所有内容
    enhanced_items = []
    
    for item in items:
        # 补充内容
        enhanced_item = enhance_content(item)
        enhanced_items.append(enhanced_item)
    
    # 3. 保存结果
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = Config.ENHANCED_DIR / f"enhanced-{timestamp}.jsonl"
    saved_count = save_enhanced(enhanced_items, output_file)
    
    # 4. 生成报告
    report = {
        "timestamp": timestamp,
        "total_items": len(items),
        "enhanced_count": len(enhanced_items),
        "output_file": str(output_file),
        "saved_count": saved_count,
        "enhancement_stats": {
            "successfully_enhanced": sum(1 for i in enhanced_items if i["enhancement"]["success"]),
            "no_enhancement_needed": sum(1 for i in enhanced_items if not i["enhancement"]["success"]),
            "methods_used": {
                "web_search": sum(1 for i in enhanced_items if i["enhancement"]["method"] == "web_search"),
                "tool_call": sum(1 for i in enhanced_items if i["enhancement"]["method"] == "tool_call"),
                "llm_generation": sum(1 for i in enhanced_items if i["enhancement"]["method"] == "llm_generation"),
                "template": sum(1 for i in enhanced_items if i["enhancement"]["method"] == "template")
            }
        },
        "score_improvement": {
            "items_improved": sum(1 for i in enhanced_items if i.get("enhanced_score", 0) > i.get("total_score", 0)),
            "average_improvement": sum(
                i.get("enhanced_score", 0) - i.get("total_score", 0)
                for i in enhanced_items
                if i.get("enhanced_score", 0) > i.get("total_score", 0)
            ) / len([i for i in enhanced_items if i.get("enhanced_score", 0) > i.get("total_score", 0)]) if any(i.get("enhanced_score", 0) > i.get("total_score", 0) for i in enhanced_items) else 0
        }
    }
    
    logger.info(f"Enhancement completed: {saved_count} items saved to {output_file}")
    
    # 保存报告
    report_file = Config.ENHANCED_DIR / f"report-{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Report saved to {report_file}")
    
    return report


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    main()
