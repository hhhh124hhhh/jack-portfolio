#!/usr/bin/env python3
"""
AI Prompt Quality Evaluator
评估 AI 提示词的质量
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import requests
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/clawd/data/evaluator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PromptEvaluator:
    """提示词质量评估器"""

    def __init__(self, api_key: Optional[str] = None, provider: str = 'anthropic'):
        """
        初始化评估器

        Args:
            api_key: LLM API key
            provider: LLM 提供商 (anthropic, openai, etc.)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.provider = provider
        self.evaluation_dimensions = {
            'clarity': '清晰度 - 提示词是否明确、无歧义',
            'specificity': '具体性 - 是否提供具体参数和约束',
            'structured': '结构化 - 是否有清晰的格式和组织',
            'practical': '实用性 - 是否可以实际使用',
            'innovative': '创新性 - 是否有独特价值'
        }
        self.thresholds = {
            'excellent': 20,  # 优秀
            'good': 15,       # 良好
            'average': 10     # 一般
        }

    def evaluate_prompt(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        """
        评估单个提示词

        Args:
            prompt: 提示词内容
            context: 额外上下文信息

        Returns:
            评估结果字典
        """
        logger.info(f"开始评估提示词: {prompt[:50]}...")

        try:
            # 构建评估请求
            evaluation_result = self._call_llm_evaluation(prompt, context)

            # 计算总分和评级
            scores = evaluation_result.get('scores', {})
            total_score = sum(scores.values())
            rating = self._calculate_rating(total_score)

            result = {
                'prompt': prompt,
                'context': context,
                'scores': scores,
                'total_score': total_score,
                'rating': rating,
                'evaluation': evaluation_result.get('evaluation', ''),
                'suggestions': evaluation_result.get('suggestions', []),
                'evaluated_at': datetime.now().isoformat()
            }

            logger.info(f"评估完成 - 总分: {total_score}/25, 评级: {rating}")
            return result

        except Exception as e:
            logger.error(f"评估提示词时出错: {e}", exc_info=True)
            # 返回默认结果
            return {
                'prompt': prompt,
                'context': context,
                'scores': {dim: 1 for dim in self.evaluation_dimensions.keys()},
                'total_score': 5,
                'rating': 'poor',
                'evaluation': f'评估失败: {str(e)}',
                'suggestions': [],
                'evaluated_at': datetime.now().isoformat(),
                'error': str(e)
            }

    def _call_llm_evaluation(self, prompt: str, context: Optional[Dict]) -> Dict:
        """
        调用 LLM 进行评估

        Args:
            prompt: 提示词内容
            context: 上下文信息

        Returns:
            评估结果
        """
        # 构建评估提示
        evaluation_prompt = self._build_evaluation_prompt(prompt, context)

        # 根据提供商选择 API
        if self.provider == 'anthropic':
            return self._call_anthropic(evaluation_prompt)
        elif self.provider == 'openai':
            return self._call_openai(evaluation_prompt)
        else:
            raise ValueError(f"不支持的提供商: {self.provider}")

    def _build_evaluation_prompt(self, prompt: str, context: Optional[Dict]) -> str:
        """
        构建评估提示

        Args:
            prompt: 要评估的提示词
            context: 上下文信息

        Returns:
            评估提示字符串
        """
        context_info = ""
        if context:
            context_info = f"\n上下文信息:\n{json.dumps(context, ensure_ascii=False, indent=2)}\n"

        evaluation_template = f"""你是一个专业的 AI 提示词质量评估专家。请评估以下提示词的质量。

提示词内容:
```
{prompt}
```
{context_info}
请从以下 5 个维度进行评分（每个维度 1-5 分，5 分为最好）：

1. 清晰度 (Clarity) - 提示词是否明确、无歧义
2. 具体性 (Specificity) - 是否提供具体参数和约束
3. 结构化 (Structured) - 是否有清晰的格式和组织
4. 实用性 (Practical) - 是否可以实际使用
5. 创新性 (Innovative) - 是否有独特价值

请以 JSON 格式返回评估结果，格式如下：
{{
  "scores": {{
    "clarity": <1-5的整数>,
    "specificity": <1-5的整数>,
    "structured": <1-5的整数>,
    "practical": <1-5的整数>,
    "innovative": <1-5的整数>
  }},
  "evaluation": "<简要评估说明，50-100字>",
  "suggestions": [
    "<改进建议1>",
    "<改进建议2>",
    "<改进建议3>"
  ]
}}

请只返回 JSON，不要包含其他文字。"""

        return evaluation_template

    def _call_anthropic(self, prompt: str) -> Dict:
        """
        调用 Anthropic API

        Args:
            prompt: 评估提示

        Returns:
            评估结果
        """
        try:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self.api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            payload = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 2000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            # 提取响应内容
            content = data['content'][0]['text']

            # 解析 JSON
            result = json.loads(self._extract_json(content))
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Anthropic API 请求失败: {e}")
            raise
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"解析 Anthropic 响应失败: {e}")
            raise

    def _call_openai(self, prompt: str) -> Dict:
        """
        调用 OpenAI API

        Args:
            prompt: 评估提示

        Returns:
            评估结果
        """
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            # 提取响应内容
            content = data['choices'][0]['message']['content']

            # 解析 JSON
            result = json.loads(self._extract_json(content))
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API 请求失败: {e}")
            raise
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"解析 OpenAI 响应失败: {e}")
            raise

    def _extract_json(self, text: str) -> str:
        """
        从文本中提取 JSON

        Args:
            text: 包含 JSON 的文本

        Returns:
            JSON 字符串
        """
        # 尝试直接解析
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass

        # 尝试查找 JSON 代码块
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            if end != -1:
                return text[start:end].strip()
        elif '```' in text:
            start = text.find('```') + 3
            end = text.find('```', start)
            if end != -1:
                return text[start:end].strip()

        # 尝试查找 { } 包围的 JSON
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]

        return text

    def _calculate_rating(self, total_score: int) -> str:
        """
        计算评级

        Args:
            total_score: 总分

        Returns:
            评级字符串
        """
        if total_score >= self.thresholds['excellent']:
            return 'excellent'  # 优秀
        elif total_score >= self.thresholds['good']:
            return 'good'       # 良好
        elif total_score >= self.thresholds['average']:
            return 'average'    # 一般
        else:
            return 'poor'       # 较差

    def evaluate_batch(self, prompts: List[str], contexts: Optional[List[Dict]] = None) -> List[Dict]:
        """
        批量评估提示词

        Args:
            prompts: 提示词列表
            contexts: 上下文列表（可选）

        Returns:
            评估结果列表
        """
        results = []

        for i, prompt in enumerate(prompts):
            context = contexts[i] if contexts and i < len(contexts) else None

            try:
                result = self.evaluate_prompt(prompt, context)
                results.append(result)

                # 避免限流
                time.sleep(1)

            except Exception as e:
                logger.error(f"评估第 {i+1} 个提示词时出错: {e}")
                continue

        return results

    def generate_report(self, evaluations: List[Dict]) -> str:
        """
        生成 Markdown 评估报告

        Args:
            evaluations: 评估结果列表

        Returns:
            Markdown 报告字符串
        """
        lines = [
            "# AI 提示词质量评估报告",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**评估数量**: {len(evaluations)}",
            "",
            "---",
            ""
        ]

        # 统计信息
        rating_counts = {'excellent': 0, 'good': 0, 'average': 0, 'poor': 0}
        total_score = 0

        for eval_result in evaluations:
            rating = eval_result.get('rating', 'poor')
            rating_counts[rating] += 1
            total_score += eval_result.get('total_score', 0)

        avg_score = total_score / len(evaluations) if evaluations else 0

        lines.extend([
            "## 评分统计",
            "",
            f"- **优秀 (≥20分)**: {rating_counts['excellent']}",
            f"- **良好 (15-19分)**: {rating_counts['good']}",
            f"- **一般 (10-14分)**: {rating_counts['average']}",
            f"- **较差 (<10分)**: {rating_counts['poor']}",
            "",
            f"**平均分**: {avg_score:.1f}/25",
            "",
            "---",
            "",
            "## 详细评估结果",
            ""
        ])

        # 详细评估
        for i, eval_result in enumerate(evaluations, 1):
            prompt = eval_result.get('prompt', '')
            scores = eval_result.get('scores', {})
            total = eval_result.get('total_score', 0)
            rating = eval_result.get('rating', 'poor')
            evaluation = eval_result.get('evaluation', '')
            suggestions = eval_result.get('suggestions', [])

            rating_map = {
                'excellent': '🌟 优秀',
                'good': '👍 良好',
                'average': '😐 一般',
                'poor': '👎 较差'
            }

            lines.extend([
                f"### {i}. {prompt[:50]}...",
                "",
                f"**总分**: {total}/25 | **评级**: {rating_map.get(rating, rating)}",
                "",
                "**各项得分**:",
                f"- 清晰度: {scores.get('clarity', 0)}/5",
                f"- 具体性: {scores.get('specificity', 0)}/5",
                f"- 结构化: {scores.get('structured', 0)}/5",
                f"- 实用性: {scores.get('practical', 0)}/5",
                f"- 创新性: {scores.get('innovative', 0)}/5",
                "",
                f"**评估说明**: {evaluation}",
                ""
            ])

            if suggestions:
                lines.append("**改进建议**:")
                for suggestion in suggestions:
                    lines.append(f"- {suggestion}")
                lines.append("")

            lines.extend(["---", "", ""])

        # 推荐列表
        excellent_prompts = [e for e in evaluations if e.get('rating') == 'excellent']
        if excellent_prompts:
            lines.extend([
                "## 🌟 优秀提示词推荐",
                ""
            ])
            for i, eval_result in enumerate(excellent_prompts, 1):
                lines.append(f"{i}. {eval_result.get('prompt', '')}")
                lines.append(f"   - 总分: {eval_result.get('total_score', 0)}/25")
                lines.append("")
            lines.append("---")
            lines.append("")

        return '\n'.join(lines)

    def save_results(self, evaluations: List[Dict], json_path: str, markdown_path: str):
        """
        保存评估结果

        Args:
            evaluations: 评估结果列表
            json_path: JSON 输出路径
            markdown_path: Markdown 输出路径
        """
        try:
            # 保存 JSON
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(evaluations, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON 结果已保存到: {json_path}")

            # 保存 Markdown
            os.makedirs(os.path.dirname(markdown_path), exist_ok=True)
            report = self.generate_report(evaluations)
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Markdown 报告已保存到: {markdown_path}")

        except Exception as e:
            logger.error(f"保存结果失败: {e}", exc_info=True)
            raise


def main():
    """主函数 - 用于测试"""
    logger.info("=" * 60)
    logger.info("AI 提示词质量评估器")
    logger.info("=" * 60)

    # 测试提示词
    test_prompt = """你是一个专业的代码审查专家。请审查以下代码，重点关注：
1. 代码风格和格式
2. 潜在的 bug
3. 性能优化建议
4. 最佳实践遵循情况

请提供详细的反馈和改进建议。"""

    try:
        evaluator = PromptEvaluator()
        result = evaluator.evaluate_prompt(test_prompt)

        print("\n评估结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == '__main__':
    main()
