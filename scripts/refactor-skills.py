#!/usr/bin/env python3
"""
Refactor skills to use skill-creator standard structure.
This script will:
1. Backup SKILL.md content
2. Reinitialize skill structure using init_skill.py
3. Restore SKILL.md content
4. Ensure YAML frontmatter is correct
"""

import os
import shutil
import subprocess
import re
import sys
from pathlib import Path

# Skills to process (directory names)
SKILLS_TO_PROCESS = [
    "ai-genie-3-game-prompts",  # Already has structure, skip
    "merc-income-guide",
    "ai-from-trueslazac",
    "ai-portrait-generator",
    "prompt-from-lexx-aura",
]

# Skills with non-standard names (need manual attention)
NON_STANDARD_SKILLS = [
    "ai 编码-reddit-454d672a",
    "ai 编码-reddit-96d5680b",
    "ai 编码-unknown-165657c2",
    "sora 2-sora-2---未来科技展示-b95f8b89",
    "sora 2-sora-2---自然纪录片-ff4894c1",
    "sora 2-sora-2---超级英雄电影-bcb42152",
    "提示词工程-reddit-bee10779",
    "谷歌生图-google-imagen-3---人像摄影-aa1d47e0",
    "谷歌生图-google-imagen-3---超写实风景-c1d838ac",
    "谷歌生图-google-veo---动态城市夜景-162c3fd9",
    "通用-reddit-e34899f0",
    "通用-reddit-e806778a",
]

BASE_DIR = Path("/root/clawd/generated-skills")
INIT_SKILL_SCRIPT = "/root/clawd/skills-bundle/anthropics/skill-creator/scripts/init_skill.py"
PACKAGE_SKILL_SCRIPT = "/root/clawd/skills-bundle/anthropics/skill-creator/scripts/package_skill.py"


def has_standard_structure(skill_dir):
    """Check if skill already has standard structure."""
    required_dirs = ["scripts", "references", "assets"]
    return all((skill_dir / d).exists() for d in required_dirs)


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


def reinitialize_skill(skill_dir, skill_name, original_content):
    """Reinitialize skill using init_skill.py."""
    # Remove existing directory contents (except we're about to recreate)
    temp_backup = skill_dir.parent / f"{skill_name}.backup"

    # Move current directory to backup
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
            new_content = create_frontmatter(skill_name, "TODO: Add description") + "\n\n" + body
            with open(skill_md_path, "w", encoding="utf-8") as f:
                f.write(new_content)

        print(f"✓ Successfully reinitialized {skill_name}")
        return True

    finally:
        # Clean up backup
        if temp_backup.exists():
            shutil.rmtree(str(temp_backup))


def package_skill(skill_dir, skill_name):
    """Package skill using package_skill.py."""
    result = subprocess.run(
        [
            "python3",
            PACKAGE_SKILL_SCRIPT,
            "--path",
            str(skill_dir)
        ],
        capture_output=True,
        text=True,
        cwd=str(skill_dir.parent)
    )

    if result.returncode != 0:
        print(f"WARNING: package_skill.py failed for {skill_name}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False

    print(f"✓ Successfully packaged {skill_name}")
    return True


def main():
    print("=" * 60)
    print("SKILL REFACTORING SCRIPT")
    print("=" * 60)
    print()

    # Process standard skills
    print("STANDARD SKILLS:")
    print("-" * 60)
    processed = []
    skipped = []

    for skill_name in SKILLS_TO_PROCESS:
        skill_dir = BASE_DIR / skill_name

        print(f"\nProcessing: {skill_name}")

        if not skill_dir.exists():
            print(f"  ✗ Directory not found, skipping")
            skipped.append(skill_name)
            continue

        # Check if already has standard structure
        if has_standard_structure(skill_dir):
            print(f"  ⊙ Already has standard structure, skipping")
            skipped.append(skill_name)
            continue

        # Backup SKILL.md
        original_content = backup_skill_md(skill_dir)
        if original_content is None:
            print(f"  ✗ No SKILL.md found, skipping")
            skipped.append(skill_name)
            continue

        # Reinitialize
        if reinitialize_skill(skill_dir, skill_name, original_content):
            processed.append(skill_name)

    print("\n" + "=" * 60)
    print("NON-STANDARD SKILLS (require manual attention):")
    print("-" * 60)
    for skill_name in NON_STANDARD_SKILLS:
        print(f"  - {skill_name}")

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("-" * 60)
    print(f"Processed: {len(processed)}")
    for s in processed:
        print(f"  ✓ {s}")
    print(f"Skipped: {len(skipped)}")
    for s in skipped:
        print(f"  ⊙ {s}")
    print(f"Non-standard: {len(NON_STANDARD_SKILLS)}")

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
