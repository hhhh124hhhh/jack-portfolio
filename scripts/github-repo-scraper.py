#!/usr/bin/env python3
"""
GitHub Repository Scraper for AI Prompts
抓取 GitHub 上关于 AI prompts 的仓库
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/clawd/data/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class GitHubRepoScraper:
    """GitHub 仓库抓取器"""

    def __init__(self, token: Optional[str] = None):
        """
        初始化抓取器

        Args:
            token: GitHub API token (从环境变量 GITHUB_TOKEN 读取)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.headers = {}
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
        self.headers['Accept'] = 'application/vnd.github.v3+json'

    def search_repos(
        self,
        keywords: List[str],
        min_stars: int = 100,
        days_active: int = 180,
        max_results: int = 100
    ) -> List[Dict]:
        """
        搜索符合条件的仓库

        Args:
            keywords: 搜索关键词列表
            min_stars: 最少 star 数
            days_active: 最近活跃天数
            max_results: 最大结果数

        Returns:
            仓库列表
        """
        all_repos = []
        cutoff_date = (datetime.now() - timedelta(days=days_active)).strftime('%Y-%m-%d')

        for keyword in keywords:
            logger.info(f"搜索关键词: {keyword}")
            query = f"{keyword} stars:>={min_stars} pushed:>={cutoff_date}"

            page = 1
            while len(all_repos) < max_results:
                try:
                    url = f"{self.base_url}/search/repositories"
                    params = {
                        'q': query,
                        'sort': 'stars',
                        'order': 'desc',
                        'per_page': 100,
                        'page': page
                    }

                    response = requests.get(url, headers=self.headers, params=params)
                    response.raise_for_status()
                    data = response.json()

                    if not data.get('items'):
                        break

                    repos = data['items']
                    logger.info(f"找到 {len(repos)} 个仓库 (页面 {page})")

                    # 过滤和存储仓库
                    for repo in repos:
                        if len(all_repos) >= max_results:
                            break

                        repo_info = self._process_repo(repo)
                        if repo_info:
                            all_repos.append(repo_info)
                            logger.debug(f"添加仓库: {repo_info['repo_name']}")

                    # 检查是否还有更多页面
                    if len(repos) < 100:
                        break

                    page += 1
                    time.sleep(1)  # 避免 API 限流

                except requests.exceptions.RequestException as e:
                    logger.error(f"请求失败: {e}")
                    break
                except Exception as e:
                    logger.error(f"处理数据时出错: {e}")
                    break

        # 去重
        seen = set()
        unique_repos = []
        for repo in all_repos:
            repo_id = repo['repo_name']
            if repo_id not in seen:
                seen.add(repo_id)
                unique_repos.append(repo)

        logger.info(f"共找到 {len(unique_repos)} 个唯一仓库")
        return unique_repos

    def _process_repo(self, repo: Dict) -> Optional[Dict]:
        """
        处理单个仓库信息

        Args:
            repo: 原始仓库数据

        Returns:
            处理后的仓库信息
        """
        try:
            # 检查仓库是否有 README 或 prompt 相关文件
            if not self._has_prompt_files(repo):
                logger.debug(f"跳过 {repo['full_name']}: 无 prompt 相关文件")
                return None

            return {
                'repo_name': repo['full_name'],
                'description': repo.get('description', ''),
                'stars': repo['stargazers_count'],
                'updated_at': repo['updated_at'],
                'url': repo['html_url'],
                'topics': repo.get('topics', []),
                'language': repo.get('language', ''),
                'forks': repo['forks_count']
            }
        except Exception as e:
            logger.error(f"处理仓库 {repo.get('full_name', 'unknown')} 时出错: {e}")
            return None

    def _has_prompt_files(self, repo: Dict) -> bool:
        """
        检查仓库是否包含 prompt 相关文件

        Args:
            repo: 仓库数据

        Returns:
            是否包含 prompt 相关文件
        """
        try:
            # 优先检查 README
            if repo.get('has_pages', False) or repo.get('description', '').lower():
                # 简单检查：如果描述或主题包含 prompt 关键词
                desc_lower = repo.get('description', '').lower()
                topics = repo.get('topics', [])

                prompt_keywords = ['prompt', 'ai', 'chatgpt', 'gpt', 'llm', 'instruction']
                keyword_in_desc = any(kw in desc_lower for kw in prompt_keywords)
                keyword_in_topics = any(kw in topic.lower() for topic in topics for kw in prompt_keywords)

                if keyword_in_desc or keyword_in_topics:
                    return True

            # 尝试获取仓库内容（需要 API 调用，可能会限流）
            try:
                url = f"{self.base_url}/repos/{repo['full_name']}/contents/"
                response = requests.get(url, headers=self.headers, timeout=5)
                if response.status_code == 200:
                    files = response.json()
                    prompt_files = [f['name'].lower() for f in files if isinstance(f, dict)]
                    return any('prompt' in f or 'readme' in f for f in prompt_files)
            except Exception:
                pass

            return False

        except Exception as e:
            logger.debug(f"检查仓库文件时出错: {e}")
            return False

    def save_to_json(self, repos: List[Dict], filepath: str):
        """
        保存仓库数据到 JSON 文件

        Args:
            repos: 仓库列表
            filepath: 输出文件路径
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(repos, f, ensure_ascii=False, indent=2)

            logger.info(f"成功保存 {len(repos)} 个仓库到 {filepath}")

        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            raise


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始抓取 GitHub AI Prompts 仓库")
    logger.info("=" * 60)

    try:
        # 创建抓取器
        scraper = GitHubRepoScraper()

        # 搜索关键词
        keywords = [
            'ai-prompts',
            'prompt-engineering',
            'chatgpt-prompts',
            'gpt-prompts',
            'llm-prompts',
            'prompt-template'
        ]

        # 搜索仓库
        repos = scraper.search_repos(
            keywords=keywords,
            min_stars=100,
            days_active=180,
            max_results=100
        )

        # 保存结果
        output_file = '/root/clawd/data/github-repos.json'
        scraper.save_to_json(repos, output_file)

        logger.info("=" * 60)
        logger.info(f"抓取完成！共获取 {len(repos)} 个仓库")
        logger.info(f"结果已保存到: {output_file}")
        logger.info("=" * 60)

        # 打印统计信息
        if repos:
            total_stars = sum(repo['stars'] for repo in repos)
            avg_stars = total_stars / len(repos)
            logger.info(f"总 Stars: {total_stars:,}, 平均 Stars: {avg_stars:.1f}")

    except Exception as e:
        logger.error(f"主程序出错: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
