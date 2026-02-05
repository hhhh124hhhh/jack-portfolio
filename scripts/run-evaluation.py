#!/usr/bin/env python3
"""
Run Complete Evaluation Pipeline
完整的评估流程：抓取仓库 -> 提取提示词 -> 质量评估 -> 生成报告
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, '/root/clawd/scripts')

from github_repo_scraper import GitHubRepoScraper
from prompt_evaluator import PromptEvaluator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/clawd/data/pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EvaluationPipeline:
    """评估流程管理器"""

    def __init__(self):
        """初始化流程"""
        self.scraper = GitHubRepoScraper()
        self.evaluator = PromptEvaluator()
        self.data_dir = '/root/clawd/data'

    def run_full_pipeline(self):
        """运行完整的评估流程"""
        logger.info("=" * 70)
        logger.info("开始运行完整的评估流程")
        logger.info("=" * 70)

        try:
            # 步骤 1: 抓取 GitHub 仓库
            repos = self.scrape_github_repos()

            if not repos:
                logger.warning("未找到任何仓库，终止流程")
                return

            # 步骤 2: 从仓库中提取提示词
            prompts_data = self.extract_prompts_from_repos(repos)

            if not prompts_data:
                logger.warning("未提取到任何提示词，终止流程")
                return

            # 步骤 3: 评估提示词质量
            evaluations = self.evaluate_prompts(prompts_data)

            # 步骤 4: 生成报告
            self.generate_reports(evaluations)

            logger.info("=" * 70)
            logger.info("评估流程完成！")
            logger.info("=" * 70)

        except Exception as e:
            logger.error(f"流程执行失败: {e}", exc_info=True)
            raise

    def scrape_github_repos(self) -> List[Dict]:
        """
        抓取 GitHub 仓库

        Returns:
            仓库列表
        """
        logger.info("\n" + "=" * 70)
        logger.info("步骤 1: 抓取 GitHub 仓库")
        logger.info("=" * 70 + "\n")

        repos_file = os.path.join(self.data_dir, 'github-repos.json')

        # 检查是否已有缓存数据
        if os.path.exists(repos_file):
            logger.info(f"发现已存在的仓库数据: {repos_file}")
            logger.info("跳过抓取步骤，使用缓存数据")

            try:
                with open(repos_file, 'r', encoding='utf-8') as f:
                    repos = json.load(f)
                logger.info(f"加载了 {len(repos)} 个仓库")
                return repos
            except Exception as e:
                logger.error(f"加载缓存数据失败: {e}")
                logger.info("将重新抓取数据")

        # 抓取新数据
        keywords = [
            'ai-prompts',
            'prompt-engineering',
            'chatgpt-prompts',
            'gpt-prompts',
            'llm-prompts'
        ]

        repos = self.scraper.search_repos(
            keywords=keywords,
            min_stars=100,
            days_active=180,
            max_results=50  # 降低数量以加快处理速度
        )

        # 保存结果
        self.scraper.save_to_json(repos, repos_file)

        return repos

    def extract_prompts_from_repos(self, repos: List[Dict]) -> List[Dict]:
        """
        从仓库中提取提示词

        Args:
            repos: 仓库列表

        Returns:
            提示词数据列表
        """
        logger.info("\n" + "=" * 70)
        logger.info("步骤 2: 从仓库中提取提示词")
        logger.info("=" * 70 + "\n")

        prompts_data = []
        skipped = 0

        for i, repo in enumerate(repos, 1):
            logger.info(f"[{i}/{len(repos)}] 处理仓库: {repo['repo_name']}")

            try:
                prompts = self._extract_prompts_from_repo(repo)

                if prompts:
                    for prompt in prompts:
                        prompts_data.append({
                            'prompt': prompt,
                            'source': {
                                'repo': repo['repo_name'],
                                'url': repo['url'],
                                'stars': repo['stars']
                            }
                        })
                    logger.info(f"  ✓ 提取到 {len(prompts)} 个提示词")
                else:
                    skipped += 1
                    logger.info(f"  ✗ 未找到提示词")

            except Exception as e:
                logger.error(f"  ✗ 处理仓库时出错: {e}")
                skipped += 1
                continue

        logger.info(f"\n提取完成: {len(prompts_data)} 个提示词，跳过 {skipped} 个仓库")

        # 保存提取的提示词
        prompts_file = os.path.join(self.data_dir, 'extracted-prompts.json')
        with open(prompts_file, 'w', encoding='utf-8') as f:
            json.dump(prompts_data, f, ensure_ascii=False, indent=2)
        logger.info(f"提示词已保存到: {prompts_file}")

        return prompts_data

    def _extract_prompts_from_repo(self, repo: Dict) -> List[str]:
        """
        从单个仓库提取提示词

        Args:
            repo: 仓库信息

        Returns:
            提示词列表
        """
        prompts = []

        try:
            # 尝试获取 README
            readme = self._fetch_readme(repo['repo_name'])

            if readme:
                # 从 README 中提取提示词
                extracted = self._parse_prompts_from_text(readme)
                prompts.extend(extracted)

            # 限制每个仓库最多提取 5 个提示词
            if len(prompts) > 5:
                prompts = prompts[:5]

            return prompts

        except Exception as e:
            logger.debug(f"提取提示词失败: {e}")
            return []

    def _fetch_readme(self, repo_name: str) -> Optional[str]:
        """
        获取仓库的 README 内容

        Args:
            repo_name: 仓库名称 (owner/repo)

        Returns:
            README 内容
        """
        try:
            url = f"https://api.github.com/repos/{repo_name}/readme"
            headers = {}
            token = os.getenv('GITHUB_TOKEN')
            if token:
                headers['Authorization'] = f'token {token}'

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # GitHub API 返回 base64 编码的内容
                import base64
                content = base64.b64decode(data['content']).decode('utf-8')
                return content

            return None

        except Exception as e:
            logger.debug(f"获取 README 失败: {e}")
            return None

    def _parse_prompts_from_text(self, text: str) -> List[str]:
        """
        从文本中解析提示词

        Args:
            text: 文本内容

        Returns:
            提示词列表
        """
        prompts = []

        # 常见的提示词标记模式
        patterns = [
            # Markdown 代码块
            '```',
            # 提示词分隔符
            '---',
            '***',
            # 常见的关键词
            'Prompt:',
            '提示词:',
            '提示:',
        ]

        lines = text.split('\n')
        in_code_block = False
        in_prompt_section = False
        current_prompt = []

        for line in lines:
            stripped = line.strip()

            # 检测代码块开始
            if stripped.startswith('```'):
                if in_code_block:
                    # 代码块结束
                    if current_prompt:
                        prompt_text = '\n'.join(current_prompt).strip()
                        if self._is_valid_prompt(prompt_text):
                            prompts.append(prompt_text)
                    current_prompt = []
                    in_code_block = False
                else:
                    in_code_block = True
                continue

            # 在代码块内，收集内容
            if in_code_block:
                current_prompt.append(line)
                continue

            # 检测提示词关键词
            for pattern in patterns:
                if pattern in line.lower():
                    in_prompt_section = True
                    break

            if in_prompt_section:
                if stripped:
                    current_prompt.append(line)

                # 如果行太短，可能是一个新的章节
                if len(stripped) < 10 and current_prompt:
                    in_prompt_section = False
                    prompt_text = '\n'.join(current_prompt).strip()
                    if self._is_valid_prompt(prompt_text):
                        prompts.append(prompt_text)
                    current_prompt = []

        # 处理最后一个提示词
        if current_prompt:
            prompt_text = '\n'.join(current_prompt).strip()
            if self._is_valid_prompt(prompt_text):
                prompts.append(prompt_text)

        return prompts

    def _is_valid_prompt(self, text: str) -> bool:
        """
        检查是否是有效的提示词

        Args:
            text: 文本

        Returns:
            是否有效
        """
        if not text:
            return False

        # 长度检查：提示词应该在 20-2000 字符之间
        if len(text) < 20 or len(text) > 2000:
            return False

        # 内容检查：应该包含一些常见的提示词特征
        prompt_keywords = [
            'you are', 'you will', 'please', 'task', 'goal', 'objective',
            '你是', '请', '任务', '目标'
        ]

        lower_text = text.lower()
        has_keywords = any(kw in lower_text for kw in prompt_keywords)

        return has_keywords

    def evaluate_prompts(self, prompts_data: List[Dict]) -> List[Dict]:
        """
        评估提示词质量

        Args:
            prompts_data: 提示词数据列表

        Returns:
            评估结果列表
        """
        logger.info("\n" + "=" * 70)
        logger.info("步骤 3: 评估提示词质量")
        logger.info("=" * 70 + "\n")

        # 提取提示词和上下文
        prompts = [item['prompt'] for item in prompts_data]
        contexts = [item.get('source') for item in prompts_data]

        logger.info(f"准备评估 {len(prompts)} 个提示词")

        # 批量评估（限制数量以避免 API 超限）
        max_evaluations = 20  # 限制最多评估 20 个
        if len(prompts) > max_evaluations:
            logger.info(f"提示词数量过多，只评估前 {max_evaluations} 个")
            prompts = prompts[:max_evaluations]
            contexts = contexts[:max_evaluations]

        evaluations = self.evaluator.evaluate_batch(prompts, contexts)

        logger.info(f"完成 {len(evaluations)} 个提示词的评估")

        return evaluations

    def generate_reports(self, evaluations: List[Dict]):
        """
        生成报告

        Args:
            evaluations: 评估结果列表
        """
        logger.info("\n" + "=" * 70)
        logger.info("步骤 4: 生成报告")
        logger.info("=" * 70 + "\n")

        json_path = os.path.join(self.data_dir, 'evaluation-results.json')
        markdown_path = os.path.join(self.data_dir, 'evaluation-report.md')

        self.evaluator.save_results(evaluations, json_path, markdown_path)

        logger.info(f"\n报告生成完成:")
        logger.info(f"  - JSON: {json_path}")
        logger.info(f"  - Markdown: {markdown_path}")


def main():
    """主函数"""
    try:
        pipeline = EvaluationPipeline()
        pipeline.run_full_pipeline()

    except KeyboardInterrupt:
        logger.info("\n用户中断执行")
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
