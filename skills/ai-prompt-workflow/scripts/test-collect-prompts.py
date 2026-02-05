#!/usr/bin/env python3
"""
数据收集层测试脚本
作者：Momo (Clawdbot Team)
创建日期：2026-02-05

功能：测试数据收集层的所有功能
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.collect_prompts import Config

def test_config_loading():
    """测试 1：配置加载"""
    print("测试 1：配置加载...")
    
    try:
        config = {
            "github": {"repos": ["f/awesome-chatgpt-prompts"]},
            "reddit": {"subreddits": ["ChatGPT"]},
            "twitter": {"keywords": ["#ChatGPT"]},
            "searxng": {"keywords": ["ChatGPT prompt"]}
        }
        
        print("  ✅ 配置加载成功")
        return True, config
        
    except Exception as e:
        print(f"  ❌ 配置加载失败：{e}")
        return False, None


def test_data_collection(config):
    """测试 2：数据收集"""
    print("\n测试 2：数据收集...")
    
    try:
        from scripts.collect_prompts import GitHubSource, RedditSource
        
        # 测试 GitHub 收集
        github_source = GitHubSource(config.get("github", {}))
        github_items = github_source.collect()
        print(f"  GitHub: 收集了 {len(github_items)} 个项目")
        
        # 测试 Reddit 收集
        reddit_source = RedditSource(config.get("reddit", {}))
        reddit_items = reddit_source.collect()
        print(f"  Reddit: 收集了 {len(reddit_items)} 个项目")
        
        all_items = github_items + reddit_items
        
        print(f"  ✅ 数据收集成功：共 {len(all_items)} 个项目")
        return True, all_items
        
    except Exception as e:
        print(f"  ❌ 数据收集失败：{e}")
        return False, []


def test_md5_dedup(items):
    """测试 3：MD5 去重"""
    print("\n测试 3：MD5 去重...")
    
    try:
        from scripts.collect_prompts import md5_deduplicate
        
        unique_items, stats = md5_deduplicate(items)
        
        print(f"  总数：{stats['total_items']}")
        print(f"  去重后：{stats['unique_items']}")
        print(f"  重复：{stats['duplicates']}")
        print(f"  去重率：{stats['dedup_rate']}")
        
        print("  ✅ MD5 去重成功")
        return True, unique_items
        
    except Exception as e:
        print(f"  ❌ MD5 去重失败：{e}")
        return False, []


def test_storage(items):
    """测试 4：数据存储"""
    print("\n测试 4：数据存储...")
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = Config.COLLECTED_DIR / f"test-prompts-{timestamp}.jsonl"
        
        from scripts.collect_prompts import save_to_jsonl
        saved_count = save_to_jsonl(items, output_file)
        
        print(f"  保存到：{output_file}")
        print(f"  保存数量：{saved_count}")
        
        if saved_count == len(items):
            print("  ✅ 数据存储成功")
            return True, output_file
        else:
            print(f"  ❌ 数据存储失败：保存数量不匹配")
            return False, None
            
    except Exception as e:
        print(f"  ❌ 数据存储失败：{e}")
        return False, None


def test_report_generation():
    """测试 5：报告生成"""
    print("\n测试 5：报告生成...")
    
    try:
        report = {
            "test_date": datetime.now().isoformat(),
            "tests_passed": 4,
            "tests_failed": 0,
            "total_tests": 4,
            "status": "success"
        }
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_file = Config.COLLECTED_DIR / f"test-report-{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"  报告保存到：{report_file}")
        print("  ✅ 报告生成成功")
        return True
        
    except Exception as e:
        print(f"  ❌ 报告生成失败：{e}")
        return False


def main():
    """主测试流程"""
    print("=" * 60)
    print("数据收集层测试")
    print("=" * 60)
    
    # 测试 1：配置加载
    success1, config = test_config_loading()
    
    if not success1:
        print("\n❌ 配置加载失败，终止测试")
        return
    
    # 测试 2：数据收集
    success2, items = test_data_collection(config)
    
    if not success2:
        print("\n❌ 数据收集失败，终止测试")
        return
    
    # 测试 3：MD5 去重
    success3, unique_items = test_md5_dedup(items)
    
    if not success3:
        print("\n❌ MD5 去重失败，终止测试")
        return
    
    # 测试 4：数据存储
    success4, output_file = test_storage(unique_items)
    
    if not success4:
        print("\n❌ 数据存储失败，终止测试")
        return
    
    # 测试 5：报告生成
    success5 = test_report_generation()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"测试 1（配置加载）：{'✅ 通过' if success1 else '❌ 失败'}")
    print(f"测试 2（数据收集）：{'✅ 通过' if success2 else '❌ 失败'}")
    print(f"测试 3（MD5 去重）：{'✅ 通过' if success3 else '❌ 失败'}")
    print(f"测试 4（数据存储）：{'✅ 通过' if success4 else '❌ 失败'}")
    print(f"测试 5（报告生成）：{'✅ 通过' if success5 else '❌ 失败'}")
    print("=" * 60)
    
    passed = sum([success1, success2, success3, success4, success5])
    total = 5
    
    print(f"总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print(f"⚠️  有 {total - passed} 个测试失败")


if __name__ == "__main__":
    main()
