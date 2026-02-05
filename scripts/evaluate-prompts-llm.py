#!/usr/bin/env python3
"""
基于 LLM 的提示词质量评分系统

功能特性：
- 使用 Claude API 进行语义评估
- 评估提示词质量、实用性、完整性、创新性
- 输出 0-100 分和详细评估理由
- 批量处理已有数据
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging
import time

try:
    import yaml
except ImportError:
    print("⚠️  请安装 PyYAML: pip install pyyaml")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("⚠️  请安装 requests: pip install requests")
    sys.exit(1)

# 日志配置
def setup_logging(log_dir: str = "/root/clawd/logs") -> logging.Logger:
    """设置日志记录"""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "evaluate-prompts-llm.log")

    logger = logging.getLogger("evaluate_prompts_llm")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logging()


class Config:
    """配置管理"""

    def __init__(self, config_path: str = "/root/clawd/config/prompts-config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
            return self._default_config()

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'llm_evaluation': {
                'api_endpoint': 'https://api.anthropic.com/v1/messages',
                'api_key_env': 'ANTHROPIC_API_KEY',
                'model': 'claude-3-5-sonnet-20241022',
                'dimensions': {
                    'quality': {'weight': 0.35, 'description': '提示词的质量和清晰度'},
                    'usefulness': {'weight': 0.30, 'description': '提示词的实用性'},
                    'completeness': {'weight': 0.20, 'description': '提示词的完整性'},
                    'innovation': {'weight': 0.15, 'description': '提示词的创新性'}
                },
                'thresholds': {
                    'excellent': 85,
                    'good': 70,
                    'average': 50
                },
                'batch_size': 10,
                'max_retries': 3,
                'retry_delay_seconds': 2
            },
            'output': {
                'data_dir': '/root/clawd/data/prompts',
                'reports_dir': '/root/clawd/reports'
            }
        }

    @property
    def anthropic_api_key(self) -> Optional[str]:
        """获取 Anthropic API Key"""
        key = os.getenv(self.config['llm_evaluation']['api_key_env'])
        if not key:
            logger.error(f"环境变量 {self.config['llm_evaluation']['api_key_env']} 未设置")
        return key

    @property
    def api_endpoint(self) -> str:
        return self.config['llm_evaluation']['api_endpoint']

    @property
    def model(self) -> str:
        return self.config['llm_evaluation']['model']

    @property
    def dimensions(self) -> Dict:
        return self.config['llm_evaluation']['dimensions']

    @property
    def thresholds(self) -> Dict:
        return self.config['llm_evaluation']['thresholds']

    @property
    def batch_size(self) -> int:
        return self.config['llm_evaluation']['batch_size']

    @property
    def max_retries(self) -> int:
        return self.config['llm_evaluation']['max_retries']

    @property
    def retry_delay(self) -> int:
        return self.config['llm_evaluation']['retry_delay_seconds']

    @property
    def input_dir(self) -> str:
        return self.config['output']['data_dir']

    @property
    def reports_dir(self) -> str:
        return self.config['output']['reports_dir']


class LLMEvaluator:
    """LLM 评估器"""

    def __init__(self, config: Config):
        self.config = config

    def evaluate_prompt(self, prompt_text: str) -> Dict:
        """评估单个提示词"""
        evaluation_prompt = self._build_evaluation_prompt(prompt_text)

        for attempt in range(self.config.max_retries):
            try:
                response = self._call_claude_api(evaluation_prompt)
                result = self._parse_response(response, prompt_text)
                return result

            except Exception as e:
                logger.warning(f"评估失败 (尝试 {attempt + 1}/{self.config.max_retries}): {e}")

                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    logger.error(f"评估失败，已达到最大重试次数")
                    return self._fallback_evaluation(prompt_text)

    def _build_evaluation_prompt(self, prompt_text: str) -> str:
        """构建评估提示词"""
        dimensions_desc = "\n".join([
            f"- {name}: {info['description']} (权重 {info['weight']})"
            for name, info in self.config.dimensions.items()
        ])

        return f"""你是一个专业的提示词评估专家。请对以下提示词进行质量评估。

提示词:
```
{prompt_text}
```

评估维度:
{dimensions_desc}

请提供以下格式的 JSON 输出（不要包含任何其他文本）:
{{
  "dimensions": {{
    "quality": <0-100 分>,
    "usefulness": <0-100 分>,
    "completeness": <0-100 分>,
    "innovation": <0-100 分>
  }},
  "overall_score": <0-100 加权总分>,
  "reasoning": "<详细评估理由>",
  "strengths": ["<优点1>", "<优点2>"],
  "weaknesses": ["<不足1>", "<不足2>"],
  "suggestions": ["<改进建议1>", "<改进建议2>"]
}}

评估标准:
- 质量 (Quality): 提示词是否清晰、具体、无歧义
- 实用性 (Usefulness): 提示词是否具有实际应用价值
- 完整性 (Completeness): 提示词是否包含必要的信息和上下文
- 创新性 (Innovation): 提示词是否有独特的创意或角度

请只输出 JSON，不要包含任何解释或格式化文本。"""

    def _call_claude_api(self, prompt: str) -> str:
        """调用 Claude API"""
        headers = {
            "x-api-key": self.config.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        body = {
            "model": self.config.model,
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = requests.post(
            self.config.api_endpoint,
            headers=headers,
            json=body,
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        return data['content'][0]['text']

    def _parse_response(self, response: str, prompt_text: str) -> Dict:
        """解析 API 响应"""
        try:
            # 提取 JSON
            json_match = response.strip()
            if json_match.startswith('```json'):
                json_match = json_match[7:-3].strip()
            elif json_match.startswith('```'):
                json_match = json_match[3:-3].strip()

            result = json.loads(json_match)

            # 计算加权总分
            dimensions = result.get('dimensions', {})
            overall = sum(
                dimensions.get(dim, 0) * weight
                for dim, weight in [
                    (name, info['weight'])
                    for name, info in self.config.dimensions.items()
                ]
            )

            result['overall_score'] = round(overall, 2)
            result['prompt'] = prompt_text
            result['evaluated_at'] = datetime.now().isoformat()
            result['model'] = self.config.model

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            logger.debug(f"响应内容: {response}")
            return self._fallback_evaluation(prompt_text)
        except Exception as e:
            logger.error(f"响应解析失败: {e}")
            return self._fallback_evaluation(prompt_text)

    def _fallback_evaluation(self, prompt_text: str) -> Dict:
        """降级评估（当 API 失败时）"""
        # 基于规则的基础评分
        score = 50

        # 长度评分
        if 50 <= len(prompt_text) <= 500:
            score += 10

        # 包含特定关键词加分
        keywords = ['please', 'you', 'act as', 'role', 'task']
        if any(kw in prompt_text.lower() for kw in keywords):
            score += 10

        # 结构化加分
        if '\n' in prompt_text or ':' in prompt_text:
            score += 5

        score = min(100, max(0, score))

        return {
            'prompt': prompt_text,
            'dimensions': {
                'quality': score,
                'usefulness': score,
                'completeness': score,
                'innovation': 50
            },
            'overall_score': score,
            'reasoning': 'API 失败，使用规则降级评估',
            'strengths': ['N/A'],
            'weaknesses': ['API 评估失败'],
            'suggestions': ['请稍后重试'],
            'evaluated_at': datetime.now().isoformat(),
            'model': 'fallback'
        }


class BatchEvaluator:
    """批量评估器"""

    def __init__(self, config: Config):
        self.config = config
        self.evaluator = LLMEvaluator(config)

    def load_prompts(self, filepath: str) -> List[Dict]:
        """加载提示词数据"""
        prompts = []

        if not os.path.exists(filepath):
            logger.warning(f"文件不存在: {filepath}")
            return prompts

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        prompts.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        logger.info(f"加载 {len(prompts)} 条提示词")
        return prompts

    def evaluate_batch(self, prompts: List[Dict]) -> List[Dict]:
        """批量评估"""
        evaluated = []
        total = len(prompts)

        for i, prompt_data in enumerate(prompts, 1):
            prompt_text = prompt_data.get('prompt', '')

            logger.info(f"[{i}/{total}] 评估提示词: {prompt_text[:50]}...")

            evaluation = self.evaluator.evaluate_prompt(prompt_text)

            # 合并原始数据和评估结果
            merged = {**prompt_data, **evaluation}
            evaluated.append(merged)

            # 批次间隔，避免 API 限流
            if i % self.config.batch_size == 0:
                logger.info(f"已处理 {i} 条，暂停 2 秒...")
                time.sleep(2)

        return evaluated

    def evaluate_file(
        self,
        input_file: str,
        output_file: Optional[str] = None
    ) -> Dict:
        """评估整个文件"""
        logger.info(f"开始评估文件: {input_file}")

        prompts = self.load_prompts(input_file)

        if not prompts:
            logger.warning("没有可评估的提示词")
            return {}

        evaluated = self.evaluate_batch(prompts)

        # 确定输出文件路径
        if not output_file:
            base_name = os.path.basename(input_file)
            name, ext = os.path.splitext(base_name)
            output_file = os.path.join(
                self.config.reports_dir,
                f"{name}-evaluated{ext}"
            )

        # 保存结果
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            for item in evaluated:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

        logger.info(f"保存评估结果: {output_file}")

        # 生成统计报告
        stats = self._generate_stats(evaluated)

        report_file = output_file.replace('.jsonl', '-report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        logger.info(f"保存统计报告: {report_file}")

        return stats

    def _generate_stats(self, evaluated: List[Dict]) -> Dict:
        """生成统计信息"""
        scores = [item.get('overall_score', 0) for item in evaluated]

        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_evaluated": len(evaluated),
            "score_statistics": {
                "min": min(scores),
                "max": max(scores),
                "average": sum(scores) / len(scores) if scores else 0,
                "median": sorted(scores)[len(scores) // 2] if scores else 0
            },
            "quality_distribution": {
                "excellent": sum(1 for s in scores if s >= self.config.thresholds['excellent']),
                "good": sum(1 for s in scores if self.config.thresholds['good'] <= s < self.config.thresholds['excellent']),
                "average": sum(1 for s in scores if self.config.thresholds['average'] <= s < self.config.thresholds['good']),
                "poor": sum(1 for s in scores if s < self.config.thresholds['average'])
            },
            "thresholds": self.config.thresholds
        }

        return stats


def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("🤖 开始基于 LLM 的提示词质量评估")
    logger.info("=" * 80)

    # 加载配置
    config = Config()

    # 检查 API Key
    if not config.anthropic_api_key:
        logger.error("❌ ANTHROPIC_API_KEY 环境变量未设置")
        logger.info("提示: export ANTHROPIC_API_KEY='your-key-here'")
        return

    # 获取输入文件
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # 默认文件
        input_file = os.path.join(config.input_dir, "extracted-prompts.jsonl")

    if not os.path.exists(input_file):
        logger.error(f"输入文件不存在: {input_file}")
        logger.info("用法: python3 evaluate-prompts-llm.py <input-file> [output-file]")
        return

    # 获取输出文件
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # 执行评估
    batch_evaluator = BatchEvaluator(config)
    stats = batch_evaluator.evaluate_file(input_file, output_file)

    # 打印结果
    logger.info("=" * 80)
    logger.info("✅ 评估完成！")
    logger.info("=" * 80)
    logger.info(f"📊 评估统计:")
    logger.info(f"  总数: {stats['total_evaluated']}")
    logger.info(f"  平均分: {stats['score_statistics']['average']:.2f}")
    logger.info(f"  最高分: {stats['score_statistics']['max']}")
    logger.info(f"  最低分: {stats['score_statistics']['min']}")
    logger.info(f"📈 质量分布:")
    logger.info(f"  优秀 (≥{config.thresholds['excellent']}): {stats['quality_distribution']['excellent']}")
    logger.info(f"  良好 (≥{config.thresholds['good']}): {stats['quality_distribution']['good']}")
    logger.info(f"  一般 (≥{config.thresholds['average']}): {stats['quality_distribution']['average']}")
    logger.info(f"  较差 (<{config.thresholds['average']}): {stats['quality_distribution']['poor']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⏸️  用户中断")
    except Exception as e:
        logger.error(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
