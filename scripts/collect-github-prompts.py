#!/usr/bin/env python3
"""
从 GitHub 仓库收集提示词

支持仓库:
- f/awesome-chatgpt-prompts
- dair-ai/Prompt-Engineering-Guide
- microsoft/prompt-engine
- anthropics/prompt-engineering-interactive-tutorial
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging
import hashlib

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
    log_file = os.path.join(log_dir, "collect-github-prompts.log")

    logger = logging.getLogger("collect_github_prompts")
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
            'github': {
                'api_endpoint': 'https://api.github.com',
                'cache_dir': '/root/clawd/cache/github',
                'cache_ttl_hours': 72,
                'repositories': [
                    {
                        'owner': 'f',
                        'repo': 'awesome-chatgpt-prompts',
                        'branch': 'main',
                        'files': ['README.md']
                    }
                ]
            },
            'output': {
                'data_dir': '/root/clawd/data/prompts',
                'format': 'jsonl'
            }
        }

    @property
    def github_api_endpoint(self) -> str:
        return self.config['github']['api_endpoint']

    @property
    def repositories(self) -> List[Dict]:
        return self.config['github'].get('repositories', [])

    @property
    def cache_dir(self) -> str:
        return self.config['github']['cache_dir']

    @property
    def cache_ttl_hours(self) -> int:
        return self.config['github']['cache_ttl_hours']

    @property
    def output_dir(self) -> str:
        return self.config['output']['data_dir']


class CacheManager:
    """GitHub 内容缓存管理器"""

    def __init__(self, cache_dir: str, ttl_hours: int):
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, url: str) -> str:
        """生成缓存键"""
        return hashlib.md5(url.encode()).hexdigest()

    def _get_cache_path(self, url: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{self._get_cache_key(url)}.json"

    def get(self, url: str) -> Optional[Dict]:
        """从缓存获取数据"""
        cache_path = self._get_cache_path(url)

        if not cache_path.exists():
            return None

        # 检查缓存是否过期
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        if cache_age > timedelta(hours=self.ttl_hours):
            logger.info(f"缓存过期: {url}")
            cache_path.unlink()
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取缓存失败: {e}")
            return None

    def set(self, url: str, data: Dict):
        """写入缓存"""
        cache_path = self._get_cache_path(url)

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            logger.info(f"写入缓存: {url}")
        except Exception as e:
            logger.error(f"写入缓存失败: {e}")


from datetime import timedelta


class GitHubClient:
    """GitHub API 客户端"""

    def __init__(self, config: Config):
        self.config = config
        self.cache = CacheManager(config.cache_dir, config.cache_ttl_hours)
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'clawd-prompt-collector'
        })

        # 添加 GitHub Token（如果有）
        token = os.getenv('GITHUB_TOKEN')
        if token:
            self.session.headers.update({
                'Authorization': f'token {token}'
            })

    def get_file_content(self, owner: str, repo: str, path: str, ref: str = 'main') -> Optional[str]:
        """获取文件内容"""
        url = f"{self.config.github_api_endpoint}/repos/{owner}/{repo}/contents/{path}"

        params = {'ref': ref} if ref else {}

        # 检查缓存
        cached = self.cache.get(url)
        if cached:
            content = cached.get('content')
            if content:
                import base64
                return base64.b64decode(content).decode('utf-8')

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('type') != 'file':
                logger.warning(f"不是文件: {path}")
                return None

            # 写入缓存
            self.cache.set(url, data)

            # 解码内容
            import base64
            content = base64.b64decode(data['content']).decode('utf-8')

            return content

        except Exception as e:
            logger.error(f"获取文件失败 {owner}/{repo}/{path}: {e}")
            return None

    def get_directory_contents(self, owner: str, repo: str, path: str, ref: str = 'main') -> List[Dict]:
        """获取目录内容"""
        url = f"{self.config.github_api_endpoint}/repos/{owner}/{repo}/contents/{path}"

        params = {'ref': ref} if ref else {}

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict) and data.get('type') == 'file':
                return [data]

            if isinstance(data, list):
                return data

            return []

        except Exception as e:
            logger.error(f"获取目录失败 {owner}/{repo}/{path}: {e}")
            return []


class PromptExtractor:
    """提示词提取器"""

    def extract_from_readme(self, content: str, repo_info: Dict) -> List[Dict]:
        """从 README.md 中提取提示词"""
        prompts = []

        # 尝试不同的提取模式

        # 1. 代码块中的提示词
        code_blocks = re.findall(r'```(?:markdown|text)?\n(.*?)```', content, re.DOTALL)
        for block in code_blocks:
            if self._is_valid_prompt(block):
                prompts.append(self._create_prompt_data(block, repo_info, 'code_block'))

        # 2. Markdown 表格中的提示词（常见于 awesome-chatgpt-prompts）
        table_rows = re.findall(r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', content)
        for role, prompt_text in table_rows:
            role = role.strip()
            prompt_text = prompt_text.strip()

            if self._is_valid_prompt(prompt_text):
                # 合并角色和提示词
                full_prompt = f"Act as {role}.\n\n{prompt_text}"
                prompts.append(self._create_prompt_data(full_prompt, repo_info, 'table', extra={'role': role}))

        # 3. 列表项中的提示词
        list_items = re.findall(r'^[-*]\s+(.+)$', content, re.MULTILINE)
        for item in list_items:
            if self._is_valid_prompt(item):
                prompts.append(self._create_prompt_data(item, repo_info, 'list'))

        # 4. 引号中的内容
        quotes = re.findall(r'"([^"]{50,})"', content)
        for quote in quotes:
            if self._is_valid_prompt(quote):
                prompts.append(self._create_prompt_data(quote, repo_info, 'quote'))

        # 去重
        unique_prompts = []
        seen = set()

        for prompt in prompts:
            key = prompt['prompt'][:100]  # 使用前100字符作为键
            if key not in seen:
                seen.add(key)
                unique_prompts.append(prompt)

        logger.info(f"从 README.md 提取 {len(unique_prompts)} 个提示词")
        return unique_prompts

    def extract_from_docs(self, content: str, repo_info: Dict, file_path: str) -> List[Dict]:
        """从文档文件中提取提示词"""
        prompts = []

        # 查找示例提示词部分
        example_patterns = [
            r'(?:Example|示例)[:：]\s*\n(.*?)(?:\n\n|$)',
            r'(?:Prompt|提示词)[:：]\s*\n(.*?)(?:\n\n|$)',
            r'```(?:markdown)?\n(.*?)```'
        ]

        for pattern in example_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                if self._is_valid_prompt(match):
                    prompts.append(self._create_prompt_data(match, repo_info, 'doc_example', extra={'source_file': file_path}))

        return prompts

    def _is_valid_prompt(self, text: str) -> bool:
        """判断是否是有效的提示词"""
        text = text.strip()

        # 长度检查
        if len(text) < 30 or len(text) > 2000:
            return False

        # 排除常见的非提示词内容
        exclude_patterns = [
            r'^[A-Z\s]+$',  # 全大写标题
            r'^\d+\.\s*$',  # 纯数字
            r'^[_\-\*]+$',  # 纯符号
            r'^https?://',  # URL
            r'^\[.*\]$',  # Markdown 链接
        ]

        for pattern in exclude_patterns:
            if re.match(pattern, text):
                return False

        # 包含提示词特征
        prompt_indicators = [
            r'\b(please|you|act|as|role|task|create|write|generate)\b',
            r':',  # 冒号
            r'\?',  # 问号
        ]

        score = sum(1 for pattern in prompt_indicators if re.search(pattern, text, re.IGNORECASE))
        return score >= 1

    def _create_prompt_data(self, prompt_text: str, repo_info: Dict, source_type: str, extra: Optional[Dict] = None) -> Dict:
        """创建提示词数据结构"""
        data = {
            "prompt": prompt_text.strip(),
            "source": "GitHub",
            "repository": f"{repo_info['owner']}/{repo_info['repo']}",
            "source_type": source_type,
            "source_file": repo_info.get('file', 'README.md'),
            "branch": repo_info.get('branch', 'main'),
            "collected_at": datetime.now().isoformat(),
            "quality_score": 60  # 默认分数，待 LLM 评估
        }

        if extra:
            data.update(extra)

        return data


class GitHubPromptCollector:
    """GitHub 提示词收集器"""

    def __init__(self, config: Config):
        self.config = config
        self.client = GitHubClient(config)
        self.extractor = PromptExtractor()

    def collect_from_repository(self, repo_config: Dict) -> List[Dict]:
        """从单个仓库收集提示词"""
        owner = repo_config['owner']
        repo = repo_config['repo']
        branch = repo_config.get('branch', 'main')
        files = repo_config.get('files', ['README.md'])

        logger.info(f"收集仓库: {owner}/{repo} (branch: {branch})")

        repo_info = {
            'owner': owner,
            'repo': repo,
            'branch': branch
        }

        all_prompts = []

        for file_path in files:
            logger.info(f"  处理文件: {file_path}")

            repo_info['file'] = file_path

            # 检查是否是目录
            if file_path.endswith('/'):
                # 获取目录内容
                contents = self.client.get_directory_contents(owner, repo, file_path.rstrip('/'), branch)

                for item in contents:
                    if item.get('type') == 'file' and item.get('name', '').endswith('.md'):
                        content = self.client.get_file_content(
                            owner, repo,
                            f"{file_path.rstrip('/')}/{item['name']}",
                            branch
                        )

                        if content:
                            prompts = self.extractor.extract_from_docs(content, repo_info, item['name'])
                            all_prompts.extend(prompts)
            else:
                # 获取单个文件
                content = self.client.get_file_content(owner, repo, file_path, branch)

                if content:
                    if file_path.lower() == 'readme.md':
                        prompts = self.extractor.extract_from_readme(content, repo_info)
                    else:
                        prompts = self.extractor.extract_from_docs(content, repo_info, file_path)

                    all_prompts.extend(prompts)

        logger.info(f"  从 {owner}/{repo} 收集到 {len(all_prompts)} 个提示词")

        return all_prompts

    def collect_all(self) -> List[Dict]:
        """从所有配置的仓库收集"""
        all_prompts = []

        for i, repo_config in enumerate(self.config.repositories, 1):
            logger.info(f"[{i}/{len(self.config.repositories)}] 开始收集仓库")

            try:
                prompts = self.collect_from_repository(repo_config)
                all_prompts.extend(prompts)
            except Exception as e:
                logger.error(f"收集仓库失败: {e}")

            # 避免触发 GitHub API 限流
            if i < len(self.config.repositories):
                logger.info("等待 2 秒后继续...")
                import time
                time.sleep(2)

        return all_prompts


def save_jsonl(data: List[Dict], filepath: str):
    """保存 JSONL 格式数据"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    logger.info(f"保存 {len(data)} 条数据到: {filepath}")


def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("📦 开始从 GitHub 收集提示词")
    logger.info("=" * 80)

    # 加载配置
    config = Config()

    # 创建输出目录
    output_dir = config.output_dir
    os.makedirs(output_dir, exist_ok=True)

    # 收集器
    collector = GitHubPromptCollector(config)

    # 收集所有仓库
    logger.info(f"配置的仓库数量: {len(config.repositories)}")

    all_prompts = collector.collect_all()

    # 保存结果
    output_file = os.path.join(output_dir, "github-prompts.jsonl")
    save_jsonl(all_prompts, output_file)

    # 生成报告
    repo_counts = {}
    for prompt in all_prompts:
        repo = prompt.get('repository', 'unknown')
        repo_counts[repo] = repo_counts.get(repo, 0) + 1

    report = {
        "timestamp": datetime.now().isoformat(),
        "repositories_processed": len(config.repositories),
        "total_prompts_collected": len(all_prompts),
        "prompts_by_repository": repo_counts,
        "output_file": output_file
    }

    report_file = os.path.join(
        config.output_dir,
        f"github-collection-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    )

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info("=" * 80)
    logger.info("✅ 收集完成！")
    logger.info("=" * 80)
    logger.info(f"📊 统计:")
    logger.info(f"  处理仓库: {report['repositories_processed']} 个")
    logger.info(f"  收集提示词: {report['total_prompts_collected']} 个")
    logger.info(f"📁 输出文件:")
    logger.info(f"  提示词: {output_file}")
    logger.info(f"  报告: {report_file}")
    logger.info(f"📦 各仓库贡献:")
    for repo, count in repo_counts.items():
        logger.info(f"  {repo}: {count} 个")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⏸️  用户中断")
    except Exception as e:
        logger.error(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
