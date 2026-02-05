#!/usr/bin/env python3
"""
Reinitialize a single skill with standard structure.
"""

import shutil
import subprocess
from pathlib import Path

SKILL_NAME = "gemini-nano-banana-pro-portraits"
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


def reinitialize_skill(skill_dir, skill_name, original_content):
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
            description = "Skill for gemini nano banana pro portraits"
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
    print(f"REINITIALIZING SKILL: {SKILL_NAME}")
    print("=" * 60)
    print()

    skill_dir = BASE_DIR / SKILL_NAME

    if not skill_dir.exists():
        print(f"✗ Directory not found: {skill_dir}")
        return

    # Backup SKILL.md
    original_content = backup_skill_md(skill_dir)
    if original_content is None:
        print(f"✗ No SKILL.md found")
        return

    # Reinitialize
    if reinitialize_skill(skill_dir, SKILL_NAME, original_content):
        print("\n" + "=" * 60)
        print("Done!")
    else:
        print("\n" + "=" * 60)
        print("Failed!")


if __name__ == "__main__":
    main()
