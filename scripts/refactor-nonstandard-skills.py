#!/usr/bin/env python3
"""
Refactor skills with non-standard names by renaming and reinitializing.
"""

import os
import shutil
import subprocess
from pathlib import Path

# Mapping of old names to new standard names
SKILL_MAPPING = {
    "ai 编码-reddit-454d672a": "gaussian-process-mlp-hybrid",
    "ai 编码-reddit-96d5680b": "self-taught-ml-career-path",
    "ai 编码-unknown-165657c2": "langchain-chat-prompt-template",
    "sora 2-sora-2---未来科技展示-b95f8b89": "sora-2-futuristic-tech-showcase",
    "sora 2-sora-2---自然纪录片-ff4894c1": "sora-2-nature-documentary",
    "sora 2-sora-2---超级英雄电影-bcb42152": "sora-2-superhero-movie",
    "提示词工程-reddit-bee10779": "reddit-job-posting-templates",
    "谷歌生图-google-imagen-3---人像摄影-aa1d47e0": "google-imagen-3-portrait-photography",
    "谷歌生图-google-imagen-3---超写实风景-c1d838ac": "google-imagen-3-hyperrealistic-landscape",
    "谷歌生图-google-veo---动态城市夜景-162c3fd9": "google-veo-dynamic-city-nightview",
    "通用-reddit-e34899f0": "reddit-nlp-research-problems",
    "通用-reddit-e806778a": "akkadian-noun-analyzer",
}

BASE_DIR = Path("/root/clawd/generated-skills")
INIT_SKILL_SCRIPT = "/root/clawd/skills-bundle/anthropics/skill-creator/scripts/init_skill.py"


def backup_skill_md(skill_dir):
    """Backup SKILL.md content."""
    skill_md_path = skill_dir / "SKILL.md"
    if not skill_md_path.exists():
        return None

    with open(skill_md_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_frontmatter(content):
    """Extract YAML frontmatter from content."""
    if content.startswith("---"):
        end_idx = content.find("---", 3)
        if end_idx != -1:
            return content[3:end_idx].strip(), content[end_idx + 3:].strip()
    return None, content


def create_frontmatter(skill_name, description):
    """Create YAML frontmatter."""
    return f"""---
name: {skill_name}
description: {description}
---"""


def reinitialize_skill(skill_dir, skill_name, original_content, description=None):
    """Reinitialize skill using init_skill.py."""
    temp_backup = skill_dir.parent / f"{skill_name}.backup"

    # Move current directory to backup if exists
    if skill_dir.exists():
        shutil.move(str(skill_dir), str(temp_backup))

    try:
        # Run init_skill.py
        result = subprocess.run(
            [
                "python3",
                INIT_SKILL_SCRIPT,
                skill_name,
                "--path",
                str(skill_dir.parent)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"ERROR: init_skill.py failed for {skill_name}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            # Restore backup
            shutil.rmtree(str(skill_dir), ignore_errors=True)
            shutil.move(str(temp_backup), str(skill_dir))
            return False

        # Restore SKILL.md
        skill_md_path = skill_dir / "SKILL.md"

        # Check if original content has frontmatter
        frontmatter, body = extract_frontmatter(original_content)

        if frontmatter:
            # Keep original frontmatter
            with open(skill_md_path, "w", encoding="utf-8") as f:
                f.write(original_content)
        else:
            # Add frontmatter
            if description is None:
                description = "TODO: Add description"
            new_content = create_frontmatter(skill_name, description) + "\n\n" + body
            with open(skill_md_path, "w", encoding="utf-8") as f:
                f.write(new_content)

        print(f"✓ Successfully reinitialized {skill_name}")
        return True

    finally:
        # Clean up backup
        if temp_backup.exists():
            shutil.rmtree(str(temp_backup))


def main():
    print("=" * 60)
    print("REFACTORING NON-STANDARD SKILLS")
    print("=" * 60)
    print()

    processed = []
    failed = []

    for old_name, new_name in SKILL_MAPPING.items():
        print(f"\nProcessing: {old_name} → {new_name}")

        old_dir = BASE_DIR / old_name
        new_dir = BASE_DIR / new_name

        if not old_dir.exists():
            print(f"  ✗ Old directory not found, skipping")
            failed.append(old_name)
            continue

        # Backup SKILL.md
        original_content = backup_skill_md(old_dir)
        if original_content is None:
            print(f"  ✗ No SKILL.md found, skipping")
            failed.append(old_name)
            continue

        # Remove old directory
        shutil.rmtree(str(old_dir))

        # Create new skill directory with standard structure
        # Use a description based on the skill name
        description = f"Skill for {new_name.replace('-', ' ')}"

        if reinitialize_skill(new_dir, new_name, original_content, description):
            processed.append((old_name, new_name))
        else:
            failed.append(old_name)

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("-" * 60)
    print(f"Processed: {len(processed)}")
    for old_name, new_name in processed:
        print(f"  ✓ {old_name} → {new_name}")
    print(f"Failed: {len(failed)}")
    for name in failed:
        print(f"  ✗ {name}")

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
