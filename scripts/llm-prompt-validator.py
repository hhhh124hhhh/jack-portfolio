#!/usr/bin/env python3
"""
LLM 辅助的提示词质量验证器
使用 Claude API 对提取的提示词进行专业评估
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List
from anthropic import Anthropic

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LLMPromptValidator:
    """使用 LLM 验证提示词质量"""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """
        初始化验证器

        Args:
            model: 使用的 Claude 模型
        """
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=self.api_key)
        logger.info(f"Initialized LLM validator with model: {model}")

    def validate_prompt(self, prompt: str, role: str = "") -> Dict:
        """
        验证单个提示词

        Args:
            prompt: 提示词文本
            role: 角色名称（如果有）

        Returns:
            验证结果字典
        """
        evaluation_prompt = self._build_evaluation_prompt(prompt, role)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": evaluation_prompt
                    }
                ]
            )

            response_text = message.content[0].text
            return self._parse_evaluation_response(response_text, prompt, role)

        except Exception as e:
            logger.error(f"Failed to validate prompt: {e}")
            return {
                "prompt": prompt[:200],
                "role": role,
                "is_valid": False,
                "quality_score": 0,
                "error": str(e)
            }

    def _build_evaluation_prompt(self, prompt: str, role: str = "") -> str:
        """
        构建评估提示词

        Args:
            prompt: 待评估的提示词
            role: 角色名称

        Returns:
            评估提示词
        """
        return f"""你是一个专业的提示词质量评估专家。请评估以下提示词的质量。

**角色名称**: {role if role else "未指定"}

**提示词内容**:
```
{prompt[:2000]}  # 限制长度避免超时
```

请从以下维度评估这个提示词（每个维度 0-10 分）：

1. **清晰度** (0-10): 提示词是否清晰、无歧义？
2. **完整性** (0-10): 是否包含了完整的指令和要求？
3. **实用性** (0-10): 实际应用中的价值和可用性
4. **创新性** (0-10): 是否有独特的创意或方法？
5. **可复用性** (0-10): 能否在不同场景中重复使用？

**评估要求**:
- 只返回 JSON 格式的结果
- 不要包含任何解释或额外文字
- JSON 格式必须严格遵循以下结构

返回格式（只返回 JSON）:
```json
{{
  "clarity": <0-10>,
  "completeness": <0-10>,
  "practicality": <0-10>,
  "innovation": <0-10>,
  "reusability": <0-10>,
  "is_valid_prompt": true/false,
  "total_score": <总分, 0-50>,
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["缺点1", "缺点2"],
  "improvement_suggestions": ["改进建议1", "改进建议2"]
}}
```

如果这个不是真正的提示词（比如文档标题、导航栏文字、页面内容等），请设置 is_valid_prompt 为 false。
"""

    def _parse_evaluation_response(self, response: str, prompt: str, role: str) -> Dict:
        """
        解析评估响应

        Args:
            response: LLM 返回的响应
            prompt: 原始提示词
            role: 角色名称

        Returns:
            解析后的评估结果
        """
        try:
            # 尝试提取 JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                evaluation = json.loads(json_str)

                # 添加元数据
                evaluation["prompt"] = prompt[:500]  # 截断避免过大
                evaluation["role"] = role
                evaluation["evaluated_at"] = datetime.now().isoformat()
                evaluation["quality_percentage"] = (evaluation.get("total_score", 0) / 50) * 100

                return evaluation
            else:
                raise ValueError("No JSON found in response")

        except Exception as e:
            logger.warning(f"Failed to parse evaluation response: {e}")
            logger.debug(f"Response: {response[:500]}")

            # 返回默认值
            return {
                "prompt": prompt[:200],
                "role": role,
                "clarity": 0,
                "completeness": 0,
                "practicality": 0,
                "innovation": 0,
                "reusability": 0,
                "is_valid_prompt": False,
                "total_score": 0,
                "quality_percentage": 0,
                "evaluated_at": datetime.now().isoformat(),
                "error": f"Parse error: {e}"
            }

    def validate_batch(self, prompts: List[Dict], batch_size: int = 10, limit: int = None) -> List[Dict]:
        """
        批量验证提示词

        Args:
            prompts: 提示词列表（每个元素应包含 'prompt' 和可选的 'role'）
            batch_size: 每批处理的数量
            limit: 最多验证的数量

        Returns:
            验证后的提示词列表
        """
        if limit:
            prompts = prompts[:limit]

        results = []
        total = len(prompts)

        logger.info(f"Starting batch validation of {total} prompts...")

        for i, prompt_data in enumerate(prompts, 1):
            try:
                logger.info(f"Validating {i}/{total}: {prompt_data.get('role', 'Unknown')}")

                prompt_text = prompt_data.get("prompt", "")
                role_name = prompt_data.get("role", "")

                # 验证
                validation_result = self.validate_prompt(prompt_text, role_name)

                # 合并原始数据
                validation_result.update(prompt_data)
                results.append(validation_result)

                # API 速率限制
                if i % batch_size == 0:
                    logger.info(f"Completed {i}/{total}, waiting 2 seconds...")
                    time.sleep(2)

            except Exception as e:
                logger.error(f"Failed to validate prompt {i}: {e}")
                continue

        logger.info(f"Batch validation completed: {len(results)} validated")
        return results

    def filter_high_quality(self, validated_prompts: List[Dict], min_score: float = 35) -> List[Dict]:
        """
        过滤高质量提示词

        Args:
            validated_prompts: 已验证的提示词列表
            min_score: 最低总分要求（满分 50）

        Returns:
            高质量提示词列表
        """
        high_quality = [
            p for p in validated_prompts
            if p.get("is_valid_prompt", False) and p.get("total_score", 0) >= min_score
        ]

        logger.info(f"Filtered {len(high_quality)} high-quality prompts (score >= {min_score})")
        return high_quality

    def save_results(self, validated_prompts: List[Dict], output_file: str):
        """
        保存验证结果

        Args:
            validated_prompts: 验证后的提示词列表
            output_file: 输出文件路径
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(validated_prompts, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(validated_prompts)} validated prompts to {output_file}")

            # 生成统计报告
            self._generate_report(validated_prompts, output_file.replace(".json", "_report.txt"))

        except Exception as e:
            logger.error(f"Failed to save results: {e}")

    def _generate_report(self, validated_prompts: List[Dict], report_file: str):
        """
        生成统计报告

        Args:
            validated_prompts: 验证后的提示词列表
            report_file: 报告文件路径
        """
        try:
            total = len(validated_prompts)
            valid_count = sum(1 for p in validated_prompts if p.get("is_valid_prompt", False))
            avg_score = sum(p.get("total_score", 0) for p in validated_prompts) / total if total > 0 else 0

            # 分数分布
            score_ranges = {
                "45-50": 0,
                "40-44": 0,
                "35-39": 0,
                "30-34": 0,
                "0-29": 0
            }

            for p in validated_prompts:
                score = p.get("total_score", 0)
                if score >= 45:
                    score_ranges["45-50"] += 1
                elif score >= 40:
                    score_ranges["40-44"] += 1
                elif score >= 35:
                    score_ranges["35-39"] += 1
                elif score >= 30:
                    score_ranges["30-34"] += 1
                else:
                    score_ranges["0-29"] += 1

            # 维度平均分
            dimension_avgs = {}
            for dim in ["clarity", "completeness", "practicality", "innovation", "reusability"]:
                avg = sum(p.get(dim, 0) for p in validated_prompts) / total if total > 0 else 0
                dimension_avgs[dim] = round(avg, 2)

            # 写入报告
            with open(report_file, "w", encoding="utf-8") as f:
                f.write("提示词质量评估报告\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"生成时间: {datetime.now().isoformat()}\n")
                f.write(f"总数量: {total}\n")
                f.write(f"有效提示词: {valid_count} ({valid_count/total*100:.1f}%)\n")
                f.write(f"平均总分: {avg_score:.1f}/50 ({avg_score/50*100:.1f}%)\n\n")

                f.write("分数分布:\n")
                for range_name, count in score_ranges.items():
                    f.write(f"  {range_name}: {count} ({count/total*100:.1f}%)\n")
                f.write("\n")

                f.write("各维度平均分:\n")
                for dim, avg in dimension_avgs.items():
                    f.write(f"  {dim}: {avg}/10\n")
                f.write("\n")

                # Top 10 提示词
                f.write("Top 10 高质量提示词:\n")
                f.write("-" * 50 + "\n")
                top_prompts = sorted(
                    validated_prompts,
                    key=lambda x: x.get("total_score", 0),
                    reverse=True
                )[:10]

                for i, p in enumerate(top_prompts, 1):
                    role = p.get("role", "Unknown")
                    score = p.get("total_score", 0)
                    prompt = p.get("prompt", "")[:100] + "..."
                    f.write(f"{i}. {role} (总分: {score})\n")
                    f.write(f"   {prompt}\n\n")

            logger.info(f"Generated report: {report_file}")

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="LLM 辅助的提示词质量验证器")
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入 JSON 文件路径"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="输出 JSON 文件路径"
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=35,
        help="最低总分要求（满分 50）"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="最多验证的数量"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="每批处理的数量"
    )

    args = parser.parse_args()

    # 加载输入文件
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            prompts = json.load(f)

        logger.info(f"Loaded {len(prompts)} prompts from {args.input}")

    except Exception as e:
        logger.error(f"Failed to load input file: {e}")
        return

    # 创建验证器
    validator = LLMPromptValidator()

    # 批量验证
    validated = validator.validate_batch(
        prompts,
        batch_size=args.batch_size,
        limit=args.limit
    )

    # 保存结果
    validator.save_results(validated, args.output)

    # 过滤高质量提示词
    high_quality = validator.filter_high_quality(validated, min_score=args.min_score)

    # 保存高质量提示词
    high_quality_file = args.output.replace(".json", "_high_quality.json")
    with open(high_quality_file, "w", encoding="utf-8") as f:
        json.dump(high_quality, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(high_quality)} high-quality prompts to {high_quality_file}")

    # 打印摘要
    print(f"\n✅ 验证完成！")
    print(f"   总数量: {len(validated)}")
    print(f"   高质量提示词 (score >= {args.min_score}): {len(high_quality)}")
    print(f"   输出文件: {args.output}")
    print(f"   高质量提示词文件: {high_quality_file}")


if __name__ == "__main__":
    main()
