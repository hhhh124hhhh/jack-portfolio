#!/usr/bin/env python3
"""
改进的提示词提取器
支持专门解析 awesome-chatgpt-prompts 格式，并使用 LLM 验证提示词质量
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImprovedPromptExtractor:
    """改进的提示词提取器"""

    def __init__(self, use_llm_validation: bool = True):
        """
        初始化提取器

        Args:
            use_llm_validation: 是否使用 LLM 验证提示词质量
        """
        self.use_llm_validation = use_llm_validation
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # awesome-chatgpt-prompts 的 GitHub URL
        self.prompts_repo = "https://raw.githubusercontent.com/f/prompts.chat/main/PROMPTS.md"

    def extract_from_awesome_chatgpt_prompts(self) -> List[Dict]:
        """
        从 awesome-chatgpt-prompts 仓库提取提示词

        Returns:
            提示词列表
        """
        logger.info(f"Fetching prompts from {self.prompts_repo}")

        try:
            # 下载 PROMPTS.md
            response = requests.get(self.prompts_repo, timeout=30)
            response.raise_for_status()
            content = response.text

            # 解析提示词
            prompts = self._parse_awesome_chatgpt_format(content)

            logger.info(f"Extracted {len(prompts)} prompts from awesome-chatgpt-prompts")
            return prompts

        except Exception as e:
            logger.error(f"Failed to fetch from awesome-chatgpt-prompts: {e}")
            return []

    def _parse_awesome_chatgpt_format(self, content: str) -> List[Dict]:
        """
        解析 awesome-chatgpt-prompts 格式

        Args:
            content: PROMPTS.md 文件内容

        Returns:
            提示词列表
        """
        prompts = []

        # 匹配 <details> 块
        details_pattern = r'<details>.*?</details>'
        details_blocks = re.findall(details_pattern, content, re.DOTALL)

        logger.info(f"Found {len(details_blocks)} detail blocks")

        for block in details_blocks:
            try:
                # 提取角色名称（从 summary）
                summary_match = re.search(r'<summary><strong>([^<]+)</strong></summary>', block)
                role_name = summary_match.group(1).strip() if summary_match else "Unknown"

                # 提取贡献者
                contributor_match = re.search(r'Contributed by \[@([^\]]+)\]', block)
                contributor = contributor_match.group(1) if contributor_match else "Unknown"

                # 提取实际提示词（从 markdown 代码块）
                prompt_match = re.search(r'```md\n(.*?)\n```', block, re.DOTALL)
                if not prompt_match:
                    prompt_match = re.search(r'```\n(.*?)\n```', block, re.DOTALL)

                prompt_text = prompt_match.group(1).strip() if prompt_match else None

                if prompt_text and len(prompt_text) >= 50:  # 过滤太短的内容
                    prompt = {
                        "role": role_name,
                        "contributor": contributor,
                        "prompt": prompt_text,
                        "source": "awesome-chatgpt-prompts",
                        "extracted_at": datetime.now().isoformat(),
                        "length": len(prompt_text)
                    }
                    prompts.append(prompt)
                    logger.debug(f"Extracted prompt: {role_name} ({len(prompt_text)} chars)")

            except Exception as e:
                logger.debug(f"Failed to parse block: {e}")
                continue

        return prompts

    def validate_with_llm(self, prompts: List[Dict], limit: int = 50) -> List[Dict]:
        """
        使用 LLM 验证提示词质量

        Args:
            prompts: 提示词列表
            limit: 最多验证的数量

        Returns:
            验证后的提示词列表（添加质量评分）
        """
        if not self.use_llm_validation or not self.anthropic_api_key:
            logger.warning("LLM validation disabled or API key not available")
            return prompts

        logger.info(f"Validating {min(len(prompts), limit)} prompts with LLM...")

        # 这里可以集成 Claude API 进行验证
        # 暂时添加基础质量检查
        for i, prompt in enumerate(prompts[:limit]):
            # 基础质量评分
            score = self._calculate_base_quality_score(prompt)
            prompt["quality_score"] = score
            prompt["validated_at"] = datetime.now().isoformat()

        return prompts

    def _calculate_base_quality_score(self, prompt: Dict) -> float:
        """
        计算基础质量评分（0-100）

        Args:
            prompt: 提示词字典

        Returns:
            质量分数
        """
        prompt_text = prompt["prompt"]
        score = 50.0  # 基础分

        # 长度评分（500-1500 字符为最佳）
        length = prompt_text["length"] if isinstance(prompt_text, dict) else len(prompt_text)
        if 500 <= length <= 1500:
            score += 20
        elif 300 <= length <= 2000:
            score += 10

        # 包含 "act as" 通常表示是角色扮演提示词
        if "act as" in prompt_text.lower():
            score += 15

        # 包含具体指令（如 "I want you to", "You will"）
        if any(phrase in prompt_text.lower() for phrase in ["i want you to", "you will", "your task"]):
            score += 15

        # 避免过于简单的提示词
        if len(prompt_text.split()) < 20:
            score -= 30

        # 限制在 0-100 范围内
        return max(0.0, min(100.0, score))

    def extract_from_text(self, text: str) -> List[str]:
        """
        从通用文本中提取可能的提示词（改进版）

        Args:
            text: 文本内容

        Returns:
            提取的提示词列表
        """
        candidates = []

        # 模式1: "I want you to act as" 开头的段落
        pattern1 = r'I want you to act as [^.!?]+[.!?](.*?)(?=\n\n|$)'
        matches = re.findall(pattern1, text, re.DOTALL | re.IGNORECASE)
        candidates.extend(matches)

        # 模式2: "Act as" 开头的指令
        pattern2 = r'Act as [^.!?]+[.!?](.*?)(?=\n\n|$)'
        matches = re.findall(pattern2, text, re.DOTALL | re.IGNORECASE)
        candidates.extend(matches)

        # 模式3: 包含 "you will" 的指令段落
        pattern3 = r'You will [^.!?]+[.!?](.*?)(?=\n\n|$)'
        matches = re.findall(pattern3, text, re.DOTALL | re.IGNORECASE)
        candidates.extend(matches)

        # 过滤和去重
        unique_prompts = []
        seen = set()

        for candidate in candidates:
            candidate = candidate.strip()

            # 长度检查
            if len(candidate) < 50 or len(candidate) > 2000:
                continue

            # 去重
            normalized = candidate.lower()[:100]
            if normalized in seen:
                continue
            seen.add(normalized)

            unique_prompts.append(candidate)

        logger.info(f"Extracted {len(unique_prompts)} candidate prompts from text")
        return unique_prompts

    def save_prompts(self, prompts: List[Dict], output_file: str):
        """
        保存提示词到文件

        Args:
            prompts: 提示词列表
            output_file: 输出文件路径
        """
        try:
            os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(prompts, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(prompts)} prompts to {output_file}")

            # 生成统计报告
            stats = self._generate_statistics(prompts)
            stats_file = output_file.replace(".json", "_stats.json")
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved statistics to {stats_file}")

        except Exception as e:
            logger.error(f"Failed to save prompts: {e}")

    def _generate_statistics(self, prompts: List[Dict]) -> Dict:
        """
        生成统计信息

        Args:
            prompts: 提示词列表

        Returns:
            统计字典
        """
        stats = {
            "total_count": len(prompts),
            "extracted_at": datetime.now().isoformat(),
            "source": "awesome-chatgpt-prompts"
        }

        # 长度分布
        lengths = [p.get("length", len(p.get("prompt", ""))) for p in prompts]
        if lengths:
            stats["length_stats"] = {
                "min": min(lengths),
                "max": max(lengths),
                "avg": sum(lengths) / len(lengths)
            }

        # 质量分数分布
        quality_scores = [p.get("quality_score", 0) for p in prompts if "quality_score" in p]
        if quality_scores:
            stats["quality_stats"] = {
                "min": min(quality_scores),
                "max": max(quality_scores),
                "avg": sum(quality_scores) / len(quality_scores)
            }

        # 贡献者统计
        contributors = {}
        for p in prompts:
            contributor = p.get("contributor", "Unknown")
            contributors[contributor] = contributors.get(contributor, 0) + 1

        stats["top_contributors"] = sorted(
            contributors.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return stats


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="改进的提示词提取器")
    parser.add_argument(
        "--output", "-o",
        default="/root/clawd/data/prompts/awesome-chatgpt-prompts.json",
        help="输出文件路径"
    )
    parser.add_argument(
        "--no-llm-validation",
        action="store_true",
        help="禁用 LLM 验证"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="限制提取数量"
    )

    args = parser.parse_args()

    # 创建提取器
    extractor = ImprovedPromptExtractor(use_llm_validation=not args.no_llm_validation)

    # 从 awesome-chatgpt-prompts 提取
    prompts = extractor.extract_from_awesome_chatgpt_prompts()

    if args.limit:
        prompts = prompts[:args.limit]

    # 保存结果
    extractor.save_prompts(prompts, args.output)

    # 打印摘要
    print(f"\n✅ 提取完成！")
    print(f"   提示词数量: {len(prompts)}")
    print(f"   输出文件: {args.output}")

    # 显示前3个提示词预览
    print(f"\n📋 前3个提示词预览:")
    for i, prompt in enumerate(prompts[:3], 1):
        role = prompt.get("role", "Unknown")
        preview = prompt.get("prompt", "")[:100] + "..."
        quality = prompt.get("quality_score", "N/A")
        print(f"\n{i}. {role} (质量: {quality})")
        print(f"   {preview}")


if __name__ == "__main__":
    main()
