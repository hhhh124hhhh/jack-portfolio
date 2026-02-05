#!/usr/bin/env python3
"""批量检查技能目录中的重复项"""

import os
import sys
import json
from pathlib import Path
from difflib import SequenceMatcher

def load_skill_metadata(skill_dir):
    """加载技能的元数据"""
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.exists(skill_md_path):
        return None

    metadata = {}
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 提取 name
        for line in content.split('\n'):
            if line.strip().startswith('name:'):
                metadata['name'] = line.split(':', 1)[1].strip()
            elif line.strip().startswith('description:'):
                metadata['description'] = line.split(':', 1)[1].strip()

    return metadata

def normalize_text(text):
    """标准化文本"""
    if not text:
        return ''
    return text.lower().strip()

def calculate_similarity(text1, text2):
    """计算文本相似度"""
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, normalize_text(text1), normalize_text(text2)).ratio()

def find_duplicates(skill_dir, name_threshold=0.85, desc_threshold=0.80):
    """查找重复技能"""
    skill_dirs = [d for d in Path(skill_dir).iterdir() if d.is_dir() and not d.name.endswith('.skill')]

    skills = []
    for skill_dir in skill_dirs:
        metadata = load_skill_metadata(skill_dir)
        if metadata:
            skills.append({
                'name': metadata.get('name', ''),
                'description': metadata.get('description', ''),
                'path': str(skill_dir),
                'dir_name': skill_dir.name
            })

    duplicates = {
        'name_duplicates': [],
        'description_duplicates': [],
        'potential_duplicates': []
    }

    # 检查名称重复
    for i, skill1 in enumerate(skills):
        for j, skill2 in enumerate(skills):
            if i >= j:
                continue

            # 完全匹配
            if skill1['name'] == skill2['name']:
                duplicates['name_duplicates'].append({
                    'skill1': skill1,
                    'skill2': skill2,
                    'type': 'exact'
                })
            # 模糊匹配
            elif skill1['name'] and skill2['name']:
                similarity = calculate_similarity(skill1['name'], skill2['name'])
                if similarity >= name_threshold:
                    duplicates['name_duplicates'].append({
                        'skill1': skill1,
                        'skill2': skill2,
                        'type': 'fuzzy',
                        'similarity': round(similarity * 100, 2)
                    })

            # 描述相似度
            if skill1['description'] and skill2['description']:
                desc_similarity = calculate_similarity(skill1['description'], skill2['description'])
                if desc_similarity >= desc_threshold:
                    duplicates['description_duplicates'].append({
                        'skill1': skill1,
                        'skill2': skill2,
                        'similarity': round(desc_similarity * 100, 2)
                    })

    return duplicates

def print_duplicates_report(duplicates):
    """打印重复报告"""
    print("=" * 70)
    print("重复技能检测报告")
    print("=" * 70)
    print()

    # 名称重复
    if duplicates['name_duplicates']:
        print(f"🔴 名称重复: {len(duplicates['name_duplicates'])} 对")
        print("-" * 70)
        for dup in duplicates['name_duplicates']:
            if dup['type'] == 'exact':
                print(f"\n⚠️  完全相同: {dup['skill1']['name']}")
                print(f"   技能1: {dup['skill1']['dir_name']}")
                print(f"   技能2: {dup['skill2']['dir_name']}")
            else:
                print(f"\n⚠️  相似名称 ({dup['similarity']}%):")
                print(f"   技能1: {dup['skill1']['name']} ({dup['skill1']['dir_name']})")
                print(f"   技能2: {dup['skill2']['name']} ({dup['skill2']['dir_name']})")
        print()

    # 描述重复
    if duplicates['description_duplicates']:
        print(f"🟡 描述相似: {len(duplicates['description_duplicates'])} 对")
        print("-" * 70)
        for dup in duplicates['description_duplicates']:
            print(f"\n⚠️  描述相似度 {dup['similarity']}%:")
            print(f"   技能1: {dup['skill1']['name']} ({dup['skill1']['dir_name']})")
            print(f"   技能2: {dup['skill2']['name']} ({dup['skill2']['dir_name']})")
        print()

    if not duplicates['name_duplicates'] and not duplicates['description_duplicates']:
        print("✅ 未发现重复技能！")
        print()

    print("=" * 70)

if __name__ == '__main__':
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '/root/clawd/dist/skills/'

    print(f"正在分析目录: {skill_dir}")
    print()

    duplicates = find_duplicates(skill_dir)
    print_duplicates_report(duplicates)

    # 保存报告
    report_path = '/root/clawd/memory/skill-duplicates-report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(duplicates, f, indent=2, ensure_ascii=False)

    print(f"\n详细报告已保存到: {report_path}")
