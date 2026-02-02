---
name: skill-manager
description: Comprehensive skill management system for Clawdbot Skills. Provides duplication detection (name/description/content similarity), version management with change tracking, dependency relationship management, quality scoring system, and ClawdHub publishing integration. Use when managing multiple skills, preparing skills for distribution, ensuring skill quality, detecting duplicates before publishing, or maintaining skill dependencies and versions.
---

# Skill Manager

## Overview

Skill Manager is a comprehensive system for managing Clawdbot Skills throughout their lifecycle. It enables skill authors to maintain quality, avoid duplication, track versions, manage dependencies, and publish to ClawdHub with confidence.

## Core Capabilities

### 1. Duplication Detection

Detect potential duplicate skills before publishing by comparing:
- **Name similarity**: Exact matches and fuzzy name matching
- **Description similarity**: Semantic similarity between skill descriptions
- **Content similarity**: Compare SKILL.md and bundled resources

**When to use:**
- Before publishing a new skill
- When reviewing existing skill portfolio
- During skill updates to ensure no conflicts

**Command:**
```bash
python3 /root/clawd/skills/skill-manager/scripts/check_duplicates.py /path/to/skill
```

### 2. Version Management

Track skill versions and changes:
- **Version tracking**: Maintain version history per skill
- **Change logs**: Record what changed between versions
- **Migration paths**: Document breaking changes

**When to use:**
- Releasing a new version of a skill
- Reviewing version history
- Planning breaking changes

**Commands:**
```bash
# Initialize version tracking
python3 /root/clawd/skills/skill-manager/scripts/init_version.py /path/to/skill

# Bump version
python3 /root/clawd/skills/skill-manager/scripts/bump_version.py /path/to/skill --type major|minor|patch

# View version history
python3 /root/clawd/skills/skill-manager/scripts/version_history.py /path/to/skill
```

### 3. Dependency Management

Manage skill dependencies:
- **Dependency declaration**: Specify required skills or tools
- **Dependency validation**: Check if dependencies are met
- **Dependency resolution**: Identify conflicts and missing deps

**When to use:**
- Adding a skill that depends on other skills
- Validating skill installation
- Troubleshooting dependency issues

**Commands:**
```bash
# Add dependency
python3 /root/clawd/skills/skill-manager/scripts/add_dependency.py /path/to/skill --dependency skill-name --version ">=1.0.0"

# Validate dependencies
python3 /root/clawd/skills/skill-manager/scripts/validate_dependencies.py /path/to/skill

# Check conflicts
python3 /root/clawd/skills/skill-manager/scripts/check_conflicts.py /path/to/skill
```

### 4. Quality Scoring

Evaluate skill quality with a scoring system:
- **Documentation quality**: SKILL.md completeness, clarity
- **Code quality**: Script organization, error handling
- **Testing coverage**: Evidence of testing
- **Best practices**: Follows skill guidelines

**When to use:**
- Pre-publishing quality check
- Skill portfolio review
- Identifying improvement areas

**Command:**
```bash
python3 /root/clawd/skills/skill-manager/scripts/score_quality.py /path/to/skill
```

### 5. ClawdHub Publishing

Streamline publishing to ClawdHub:
- **Pre-flight checks**: Run all validations before publishing
- **Automatic packaging**: Bundle skill into .skill file
- **Publish to ClawdHub**: Upload and register skill
- **Version management**: Sync with ClawdHub versions

**When to use:**
- Publishing a new skill or update
- Re-publishing after changes
- Managing published skill versions

**Commands:**
```bash
# Pre-flight check (includes dup check, quality score, validation)
python3 /root/clawd/skills/skill-manager/scripts/preflight.py /path/to/skill

# Publish to ClawdHub
python3 /root/clawd/skills/skill-manager/scripts/publish.py /path/to/skill

# Full workflow (preflight + package + publish)
python3 /root/clawd/skills/skill-manager/scripts/release.py /path/to/skill
```

## Workflow

### Publishing a New Skill

1. **Run duplication check**
   ```bash
   python3 /root/clawd/skills/skill-manager/scripts/check_duplicates.py /path/to/skill
   ```

2. **Initialize version tracking**
   ```bash
   python3 /root/clawd/skills/skill-manager/scripts/init_version.py /path/to/skill
   ```

3. **Add dependencies (if any)**
   ```bash
   python3 /root/clawd/skills/skill-manager/scripts/add_dependency.py /path/to/skill --dependency skill-name
   ```

4. **Run quality check**
   ```bash
   python3 /root/clawd/skills/skill-manager/scripts/score_quality.py /path/to/skill
   ```

5. **Publish to ClawdHub**
   ```bash
   python3 /root/clawd/skills/skill-manager/scripts/release.py /path/to/skill
   ```

### Updating an Existing Skill

1. **Make changes to the skill**

2. **Bump version**
   ```bash
   python3 /root/clawd/skills/skill-manager/scripts/bump_version.py /path/to/skill --type patch|minor|major
   ```

3. **Run pre-flight check**
   ```bash
   python3 /root/clawd/skills/skill-manager/scripts/preflight.py /path/to/skill
   ```

4. **Publish update**
   ```bash
   python3 /root/clawd/skills/skill-manager/scripts/publish.py /path/to/skill
   ```

## Resources

### scripts/
Executable scripts for skill management operations:

- `check_duplicates.py` - Detect duplicate skills
- `init_version.py` - Initialize version tracking
- `bump_version.py` - Bump skill version
- `version_history.py` - View version history
- `add_dependency.py` - Add skill dependency
- `validate_dependencies.py` - Validate dependencies are met
- `check_conflicts.py` - Check dependency conflicts
- `score_quality.py` - Score skill quality
- `preflight.py` - Run all pre-publishing checks
- `publish.py` - Publish to ClawdHub
- `release.py` - Complete release workflow
- `analyze_portfolio.py` - Analyze entire skill portfolio

### references/
- `scoring_criteria.md` - Quality scoring criteria and thresholds
- `clawdhub_api.md` - ClawdHub API reference
- `versioning_guide.md` - Semantic versioning best practices

### assets/
- `version_template.json` - Version tracking template
- `quality_report_template.md` - Quality score report template
