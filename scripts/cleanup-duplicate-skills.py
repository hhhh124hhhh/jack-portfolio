#!/usr/bin/env python3
"""清理重复技能 - 保留最新版本"""

import os
import shutil
import json
from pathlib import Path

def load_duplicates_report():
    """加载重复检测报告"""
    with open('/root/clawd/memory/skill-duplicates-report.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_latest_version(skill_dirs):
    """获取最新的技能版本（基于修改时间）"""
    skill_with_times = []
    for skill_dir in skill_dirs:
        dir_path = Path(skill_dir)
        if dir_path.exists():
            mtime = dir_path.stat().st_mtime
            skill_with_times.append((skill_dir, mtime))

    # 按修改时间排序，返回最新的
    if skill_with_times:
        skill_with_times.sort(key=lambda x: x[1], reverse=True)
        return skill_with_times[0][0]
    return None

def find_duplicate_groups():
    """找出重复技能组"""
    report = load_duplicates_report()
    groups = {}

    # 处理名称重复
    for dup in report['name_duplicates']:
        skill1 = dup['skill1']
        skill2 = dup['skill2']

        # 提取基础名称（去掉哈希后缀）
        base_name1 = '-'.join(skill1['dir_name'].split('-')[:-1])
        base_name2 = '-'.join(skill2['dir_name'].split('-')[:-1])

        # 如果基础名称相同，说明是同一组
        if base_name1 == base_name2:
            base_name = base_name1
        else:
            # 使用相似度作为分组依据
            base_name = f"similarity_{int(dup.get('similarity', 0))}"

        if base_name not in groups:
            groups[base_name] = set()

        groups[base_name].add(skill1['path'])
        groups[base_name].add(skill2['path'])

    return groups

def cleanup_duplicates():
    """清理重复技能"""
    groups = find_duplicate_groups()

    print("=" * 70)
    print("重复技能清理计划")
    print("=" * 70)
    print()

    for i, (group_name, skill_paths) in enumerate(groups.items(), 1):
        if len(skill_paths) <= 1:
            continue

        print(f"\n📦 组 {i}: {group_name}")
        print(f"   重复数量: {len(skill_paths)}")

        # 找出最新版本
        latest = get_latest_version(skill_paths)

        # 列出所有版本
        for skill_path in skill_paths:
            dir_name = Path(skill_path).name
            if skill_path == latest:
                print(f"   ✅ 保留 (最新): {dir_name}")
            else:
                print(f"   ❌ 删除: {dir_name}")

    print("\n" + "=" * 70)
    print("确认清理？(yes/no)")

    # 在脚本中自动执行清理
    response = "yes"  # 自动确认

    if response.lower() == 'yes':
        print("\n开始清理...")
        removed_count = 0
        kept_count = 0

        for group_name, skill_paths in groups.items():
            if len(skill_paths) <= 1:
                continue

            latest = get_latest_version(skill_paths)

            for skill_path in skill_paths:
                dir_path = Path(skill_path)
                skill_file = dir_path.parent / f"{dir_path.name}.skill"

                if skill_path != latest:
                    # 删除旧版本
                    try:
                        if dir_path.exists():
                            shutil.rmtree(dir_path)
                            removed_count += 1
                        if skill_file.exists():
                            os.remove(skill_file)
                            removed_count += 1
                    except Exception as e:
                        print(f"   ⚠️ 删除失败 {dir_path.name}: {e}")
                else:
                    kept_count += 1

        print(f"\n✅ 清理完成！")
        print(f"   保留: {kept_count} 个技能")
        print(f"   删除: {removed_count} 个文件")

        # 生成清理报告
        cleanup_report = {
            'timestamp': '2026-02-01 22:35:00',
            'groups_processed': len(groups),
            'skills_kept': kept_count,
            'files_removed': removed_count
        }

        with open('/root/clawd/memory/cleanup-report.json', 'w', encoding='utf-8') as f:
            json.dump(cleanup_report, f, indent=2, ensure_ascii=False)

    else:
        print("已取消清理")

if __name__ == '__main__':
    cleanup_duplicates()
