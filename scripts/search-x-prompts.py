#!/usr/bin/env python3
"""
从 X (Twitter) 搜索 AI 提示词（优化版）

功能特性：
- 标签过滤（#AIPrompts, #promptengineering 等）
- 账号白名单功能
- 缓存机制减少 API 调用
- 优化的搜索查询格式
"""

import json
import os
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging
import pickle

try:
    import yaml
except ImportError:
    print("⚠️  请安装 PyYAML: pip install pyyaml")
    exit(1)

try:
    import requests
except ImportError:
    print("⚠️  请安装 requests: pip install requests")
    exit(1)

# 日志配置
def setup_logging(log_dir: str = "/root/clawd/logs") -> logging.Logger:
    """设置日志记录"""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "search-x-prompts.log")

    logger = logging.getLogger("search_x_prompts")
    logger.setLevel(logging.INFO)

    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 格式化器
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
            'twitter': {
                'api_endpoint': 'https://api.twitterapi.io/v2/tweets/search/recent',
                'api_key_env': 'TWITTER_API_KEY',
                'search_queries': [
                    "AI prompts (#AIPrompts OR #promptengineering) -is:retweet lang:en",
                    "ChatGPT prompts (#ChatGPT OR #GPT4) -is:retweet lang:en"
                ],
                'hashtag_filters': ['#AIPrompts', '#promptengineering', '#ChatGPT'],
                'account_whitelist': ['openai', 'AnthropicAI'],
                'cache': {
                    'enabled': True,
                    'cache_dir': '/root/clawd/cache/twitter',
                    'cache_ttl_hours': 24
                },
                'max_results_per_query': 100,
                'max_total_results': 500
            },
            'output': {
                'data_dir': '/root/clawd/data/prompts',
                'format': 'jsonl'
            }
        }

    @property
    def twitter_api_key(self) -> Optional[str]:
        """获取 Twitter API Key"""
        key = os.getenv(self.config['twitter']['api_key_env'])
        if not key:
            logger.error(f"环境变量 {self.config['twitter']['api_key_env']} 未设置")
        return key

    @property
    def twitter_endpoint(self) -> str:
        return self.config['twitter']['api_endpoint']

    @property
    def search_queries(self) -> List[str]:
        return self.config['twitter'].get('search_queries', [])

    @property
    def hashtag_filters(self) -> List[str]:
        return self.config['twitter'].get('hashtag_filters', [])

    @property
    def account_whitelist(self) -> List[str]:
        return self.config['twitter'].get('account_whitelist', [])

    @property
    def cache_enabled(self) -> bool:
        return self.config['twitter']['cache'].get('enabled', True)

    @property
    def cache_dir(self) -> str:
        return self.config['twitter']['cache']['cache_dir']

    @property
    def cache_ttl_hours(self) -> int:
        return self.config['twitter']['cache']['cache_ttl_hours']

    @property
    def max_results_per_query(self) -> int:
        return self.config['twitter']['max_results_per_query']

    @property
    def max_total_results(self) -> int:
        return self.config['twitter']['max_total_results']

    @property
    def output_dir(self) -> str:
        return self.config['output']['data_dir']


class CacheManager:
    """缓存管理器"""

    def __init__(self, cache_dir: str, ttl_hours: int):
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, query: str) -> str:
        """生成缓存键"""
        return hashlib.md5(query.encode()).hexdigest()

    def _get_cache_path(self, query: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{self._get_cache_key(query)}.pkl"

    def get(self, query: str) -> Optional[Dict]:
        """从缓存获取数据"""
        cache_path = self._get_cache_path(query)

        if not cache_path.exists():
            return None

        # 检查缓存是否过期
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        if cache_age > timedelta(hours=self.ttl_hours):
            logger.info(f"缓存过期: {query}")
            cache_path.unlink()
            return None

        try:
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            logger.info(f"从缓存加载: {query} ({len(cached_data.get('data', []))} 条)")
            return cached_data
        except Exception as e:
            logger.error(f"读取缓存失败: {e}")
            return None

    def set(self, query: str, data: Dict):
        """写入缓存"""
        cache_path = self._get_cache_path(query)

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"写入缓存: {query} ({len(data.get('data', []))} 条)")
        except Exception as e:
            logger.error(f"写入缓存失败: {e}")


class TwitterSearcher:
    """Twitter 搜索器"""

    def __init__(self, config: Config):
        self.config = config
        self.cache = CacheManager(config.cache_dir, config.cache_ttl_hours) if config.cache_enabled else None

    def search(self, query: str) -> List[Dict]:
        """搜索 Twitter"""
        # 检查缓存
        if self.cache:
            cached = self.cache.get(query)
            if cached:
                return cached.get('data', [])

        headers = {
            "X-API-Key": self.config.twitter_api_key,
            "Accept": "application/json"
        }

        params = {
            "query": query,
            "max_results": self.config.max_results_per_query,
            "tweet.fields": "created_at,author_id,public_metrics,entities"
        }

        try:
            response = requests.get(
                self.config.twitter_endpoint,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            tweets = data.get("data", [])

            # 过滤推文
            filtered_tweets = self._filter_tweets(tweets, query)

            # 写入缓存
            if self.cache:
                self.cache.set(query, {
                    'data': filtered_tweets,
                    'timestamp': datetime.now().isoformat()
                })

            logger.info(f"搜索 '{query}': 找到 {len(filtered_tweets)} 条推文")
            return filtered_tweets

        except Exception as e:
            logger.error(f"搜索失败 '{query}': {e}")
            return []

    def _filter_tweets(self, tweets: List[Dict], query: str) -> List[Dict]:
        """过滤推文：标签过滤 + 账号白名单"""
        filtered = []

        hashtag_filters = self.config.hashtag_filters
        account_whitelist = [acc.lower() for acc in self.config.account_whitelist]

        for tweet in tweets:
            author_id = tweet.get('author_id', '')
            entities = tweet.get('entities', {})
            hashtags = [tag.get('tag', '').lower() for tag in entities.get('hashtags', [])]

            # 检查标签过滤
            has_target_hashtag = any(
                tag.lower() in [ht.lower() for ht in hashtag_filters]
                for tag in hashtags
            )

            # 检查账号白名单
            in_whitelist = any(acc in str(author_id).lower() for acc in account_whitelist)

            # 如果有标签或在白名单中，则保留
            if has_target_hashtag or in_whitelist:
                tweet_data = {
                    "tweet_id": tweet.get("id"),
                    "text": tweet.get("text", ""),
                    "author_id": author_id,
                    "created_at": tweet.get("created_at"),
                    "public_metrics": tweet.get("public_metrics", {}),
                    "hashtags": hashtags,
                    "source": "X",
                    "search_query": query,
                    "scraped_at": datetime.now().isoformat(),
                    "matched_hashtag": has_target_hashtag,
                    "in_whitelist": in_whitelist
                }
                filtered.append(tweet_data)

        return filtered


class PromptExtractor:
    """提示词提取器"""

    def extract_from_tweets(self, tweets: List[Dict]) -> List[Dict]:
        """从推文中提取提示词"""
        prompts = []

        for tweet in tweets:
            text = tweet.get("text", "")
            extracted = self._extract_prompts(text)

            for prompt in extracted:
                if len(prompt.strip()) > 20:
                    prompts.append({
                        "prompt": prompt.strip(),
                        "source": "X",
                        "source_tweet_id": tweet.get("tweet_id"),
                        "author_id": tweet.get("author_id"),
                        "search_query": tweet.get("search_query"),
                        "hashtags": tweet.get("hashtags", []),
                        "extracted_at": datetime.now().isoformat(),
                        "quality_score": 50  # 默认分数，待 LLM 评估
                    })

        logger.info(f"从 {len(tweets)} 条推文中提取 {len(prompts)} 个提示词")
        return prompts

    def _extract_prompts(self, text: str) -> List[str]:
        """从文本中提取提示词"""
        prompts = []

        # 代码块
        code_blocks = re.findall(r'```([\s\S]*?)```', text)
        prompts.extend(code_blocks)

        # 引号
        quotes = re.findall(r'"([^"]{20,})"', text)
        prompts.extend(quotes)

        # Prompt: 标记
        specific = re.findall(r'(?:Prompt|prompt)[:：]\s*([^\n]{20,})', text)
        prompts.extend(specific)

        return list(set(prompts))  # 去重


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
    logger.info("🔍 开始搜索 X (Twitter) 获取 AI 提示词（优化版）")
    logger.info("=" * 80)

    # 加载配置
    config = Config()

    # 检查 API Key
    if not config.twitter_api_key:
        logger.error("❌ TWITTER_API_KEY 环境变量未设置")
        return

    # 创建输出目录
    output_dir = config.output_dir
    os.makedirs(output_dir, exist_ok=True)

    # 搜索器
    searcher = TwitterSearcher(config)

    # 执行搜索
    all_tweets = []
    total_searched = 0

    logger.info(f"搜索查询数: {len(config.search_queries)}")

    for i, query in enumerate(config.search_queries, 1):
        logger.info(f"[{i}/{len(config.search_queries)}] 搜索: {query}")

        tweets = searcher.search(query)

        if tweets:
            all_tweets.extend(tweets)
            total_searched += len(tweets)

        # 限制总数
        if len(all_tweets) >= config.max_total_results:
            logger.info(f"达到最大结果数限制: {config.max_total_results}")
            all_tweets = all_tweets[:config.max_total_results]
            break

    # 保存推文
    tweets_file = os.path.join(output_dir, "x-search-results.jsonl")
    save_jsonl(all_tweets, tweets_file)

    # 提取提示词
    extractor = PromptExtractor()
    prompts = extractor.extract_from_tweets(all_tweets)

    prompts_file = os.path.join(output_dir, "extracted-prompts.jsonl")
    save_jsonl(prompts, prompts_file)

    # 生成报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "searched_queries": config.search_queries,
        "hashtag_filters": config.hashtag_filters,
        "account_whitelist": config.account_whitelist,
        "total_tweets_found": len(all_tweets),
        "total_prompts_extracted": len(prompts),
        "cache_enabled": config.cache_enabled,
        "output_files": {
            "tweets": tweets_file,
            "prompts": prompts_file
        }
    }

    report_file = os.path.join(output_dir, f"x-search-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info("=" * 80)
    logger.info("✅ 搜索完成！")
    logger.info("=" * 80)
    logger.info(f"📊 统计:")
    logger.info(f"  搜索查询: {len(config.search_queries)} 个")
    logger.info(f"  找到推文: {len(all_tweets)} 条")
    logger.info(f"  提取提示词: {len(prompts)} 个")
    logger.info(f"📁 输出文件:")
    logger.info(f"  推文: {tweets_file}")
    logger.info(f"  提示词: {prompts_file}")
    logger.info(f"  报告: {report_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⏸️  用户中断")
    except Exception as e:
        logger.error(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
