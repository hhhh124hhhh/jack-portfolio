# Skill 管理系统 - 架构设计文档

## 1. 项目概述

### 1.1 背景
- 现有的 Prompts workflow 可以将 AI 提示词转换成 Skills
- 最近成功转换了 23 个 Skills
- 问题：转换的 Skills 可能与原有 Skills 重复，需要版本管理
- 目标：建立一个完整的 Skill 管理系统

### 1.2 核心目标
1. **去重检测** - 避免创建重复的 Skills
2. **版本管理** - 跟踪 Skills 的版本历史
3. **变更跟踪** - 记录新建、更新的 Skills
4. **状态标记** - 管理不同状态（新建、更新、重复、冲突）
5. **依赖关系** - 记录 Skills 之间的依赖
6. **质量评分** - 评估 Skills 的质量
7. **发布管理** - 与 ClawdHub 集成

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      Skill Management System                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   CLI Tool   │    │  Core Engine │    │  Storage     │      │
│  │  (skill-man) │───▶│  (Python)    │◀──▶│  (JSON)      │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                                      │
│         │                   ▼                                      │
│         │         ┌─────────────────┐                            │
│         │         │  Core Modules   │                            │
│         │         └─────────────────┘                            │
│         │                   │                                      │
│         │         ┌─────────┴──────────┐                          │
│         │         │  ┌─────────────┐  │                          │
│         │         │  │ Deduplicator│  │                          │
│         │         │  └─────────────┘  │                          │
│         │         │  ┌─────────────┐  │                          │
│         │         │  │  Versioning │  │                          │
│         │         │  └─────────────┘  │                          │
│         │         │  ┌─────────────┐  │                          │
│         │         │  │ ChangeTrack │  │                          │
│         │         │  └─────────────┘  │                          │
│         │         │  ┌─────────────┐  │                          │
│         │         │  │ Dependency  │  │                          │
│         │         │  └─────────────┘  │                          │
│         │         │  ┌─────────────┐  │                          │
│         │         │  │ QualityEval │  │                          │
│         │         │  └─────────────┘  │                          │
│         │         │  ┌─────────────┐  │                          │
│         │         │  │   Publisher │  │                          │
│         │         │  └─────────────┘  │                          │
│         │         └───────────────────┘                          │
│         │                                                      │
│         ▼                                                      │
│  ┌──────────────┐                                              │
│  │  Integration │                                              │
│  └──────────────┘                                              │
│         │                                                      │
│    ┌────┴────┐                                                 │
│    ▼         ▼                                                 │
│ ┌──────┐  ┌──────┐                                             │
│ │Prompts│  │Clawd │                                             │
│ │Workflow│  │Hub   │                                             │
│ └──────┘  └──────┘                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

#### 2.2.1 CLI Tool (`skill-man`)
命令行接口，提供用户友好的交互方式。

**主要命令：**
```bash
skill-man init                    # 初始化管理系统
skill-man status                  # 查看系统状态
skill-man scan [path]             # 扫描技能目录
skill-man check                   # 检查重复和冲突
skill-man diff [skill1] [skill2] # 比较两个技能
skill-man merge [source] [target] # 合并技能
skill-man publish [skill]        # 发布到 ClawdHub
skill-man list [--status]         # 列出技能
skill-man history [skill]         # 查看技能历史
skill-man rollback [skill] [ver]  # 回滚版本
skill-man clean                   # 清理无效技能
```

#### 2.2.2 Core Engine
核心引擎，负责所有业务逻辑处理。

**主要模块：**
- `Deduplicator` - 去重检测
- `VersionManager` - 版本管理
- `ChangeTracker` - 变更跟踪
- `DependencyManager` - 依赖管理
- `QualityEvaluator` - 质量评估
- `Publisher` - 发布管理

#### 2.2.3 Storage
存储层，基于 JSON 文件。

**目录结构：**
```
/root/clawd/skill-management/
├── config.json                 # 系统配置
├── skills/                     # 技能注册表
│   └── registry.json          # 所有技能的索引
├── versions/                   # 版本历史
│   └── [skill-name]/
│       ├── v1.0.0.json
│       ├── v1.1.0.json
│       └── ...
├── changes/                    # 变更记录
│   └── [YYYY-MM-DD].jsonl     # 按日期记录
├── dependencies/                # 依赖关系
│   └── graph.json              # 依赖图
├── quality/                    # 质量评估
│   └── scores.json             # 质量分数
└── logs/                       # 系统日志
    └── [YYYY-MM-DD].log
```

---

## 3. 数据模型

### 3.1 技能注册表 (`skills/registry.json`)

```json
{
  "skills": {
    "ai-genie-3-game-prompts": {
      "name": "ai-genie-3-game-prompts",
      "current_version": "1.0.0",
      "status": "active",
      "created_at": "2026-02-01T09:17:00Z",
      "updated_at": "2026-02-01T09:17:00Z",
      "content_hash": "a1102733eefa789996d165f6aa1b9718",
      "path": "/root/clawd/generated-skills/ai-genie-3-game-prompts",
      "quality_score": 85,
      "published": false,
      "clawdhub_id": null,
      "clawdhub_version": null,
      "tags": ["ai", "video", "game"],
      "dependencies": [],
      "metadata": {
        "source": "prompts-workflow",
        "original_title": "AI Genie 3 Game Prompts",
        "type": "Text Prompt"
      }
    }
  },
  "statistics": {
    "total_skills": 23,
    "active_skills": 23,
    "archived_skills": 0,
    "published_skills": 5
  }
}
```

### 3.2 版本记录 (`versions/[skill-name]/vX.X.X.json`)

```json
{
  "version": "1.0.0",
  "skill_name": "ai-genie-3-game-prompts",
  "created_at": "2026-02-01T09:17:00Z",
  "author": "system",
  "change_type": "initial",
  "change_description": "Initial version from prompts workflow",
  "content_hash": "a1102733eefa789996d165f6aa1b9718",
  "previous_version": null,
  "files": {
    "SKILL.md": {
      "size": 4841,
      "hash": "md5:abc123..."
    }
  },
  "quality_score": 85,
  "metadata": {
    "source": "prompts-workflow",
    "conversion_id": "conv-20260201-091700"
  }
}
```

### 3.3 变更记录 (`changes/YYYY-MM-DD.jsonl`)

每行一个 JSON 记录：

```json
{"timestamp": "2026-02-01T09:17:00Z", "action": "create", "skill_name": "ai-genie-3-game-prompts", "version": "1.0.0", "source": "prompts-workflow", "author": "system", "change_description": "Initial version from prompts workflow"}
{"timestamp": "2026-02-01T10:30:00Z", "action": "update", "skill_name": "ai-genie-3-game-prompts", "version": "1.1.0", "previous_version": "1.0.0", "author": "user", "change_description": "Added new prompt patterns"}
{"timestamp": "2026-02-01T11:00:00Z", "action": "duplicate_detected", "skill_name": "ai-genie-3-game-prompts", "existing_skill": "ai-game-prompts", "similarity": 0.95, "content_hash": "a1102733eefa789996d165f6aa1b9718"}
```

### 3.4 依赖关系 (`dependencies/graph.json`)

```json
{
  "nodes": [
    {
      "id": "ai-genie-3-game-prompts",
      "type": "skill",
      "version": "1.0.0"
    },
    {
      "id": "google-imagen-3-portraits",
      "type": "skill",
      "version": "1.0.0"
    }
  ],
  "edges": [
    {
      "from": "ai-genie-3-game-prompts",
      "to": "google-imagen-3-portraits",
      "type": "uses",
      "strength": 0.8
    }
  ]
}
```

### 3.5 质量评估 (`quality/scores.json`)

```json
{
  "scores": {
    "ai-genie-3-game-prompts": {
      "overall": 85,
      "completeness": 90,
      "documentation": 80,
      "examples": 85,
      "clarity": 85,
      "reusability": 85,
      "evaluated_at": "2026-02-01T09:17:00Z",
      "evaluator": "system"
    }
  },
  "criteria": {
    "completeness": {
      "weight": 0.25,
      "description": "Has all required sections and metadata"
    },
    "documentation": {
      "weight": 0.20,
      "description": "Clear and comprehensive documentation"
    },
    "examples": {
      "weight": 0.20,
      "description": "Includes practical examples"
    },
    "clarity": {
      "weight": 0.15,
      "description": "Clear and easy to understand"
    },
    "reusability": {
      "weight": 0.20,
      "description": "Can be reused in different contexts"
    }
  }
}
```

### 3.6 系统配置 (`config.json`)

```json
{
  "version": "1.0.0",
  "skills_registry": "/root/clawd/skill-management/skills/registry.json",
  "versions_dir": "/root/clawd/skill-management/versions",
  "changes_dir": "/root/clawd/skill-management/changes",
  "dependencies_file": "/root/clawd/skill-management/dependencies/graph.json",
  "quality_file": "/root/clawd/skill-management/quality/scores.json",
  "logs_dir": "/root/clawd/skill-management/logs",
  "clawdhub_config": {
    "registry_url": "https://www.clawhub.ai/api",
    "config_path": "/root/clawd/.config/clawdhub/config.json"
  },
  "deduplication": {
    "content_similarity_threshold": 0.85,
    "name_similarity_threshold": 0.7,
    "description_similarity_threshold": 0.8
  },
  "quality": {
    "minimum_score": 60,
    "auto_evaluate": true
  },
  "versioning": {
    "auto_increment": true,
    "keep_history": true,
    "max_versions": 10
  }
}
```

---

## 4. 核心模块设计

### 4.1 Deduplicator (去重检测模块)

**职责：**
- 检测重复的 Skills
- 基于多种相似度算法
- 生成去重建议

**相似度检测方法：**
1. **内容哈希** - MD5/SHA256 精确匹配
2. **文本相似度** - 使用 difflib 或 TF-IDF + 余弦相似度
3. **名称相似度** - Levenshtein 距离
4. **描述相似度** - TF-IDF + 余弦相似度

**接口设计：**
```python
class Deduplicator:
    def __init__(self, config):
        self.thresholds = config['deduplication']
    
    def check_duplicate(self, skill_data, registry):
        """检查技能是否重复"""
        pass
    
    def find_similar(self, skill_name, registry, limit=5):
        """查找相似的技能"""
        pass
    
    def generate_report(self, duplicates):
        """生成去重报告"""
        pass
```

**输出格式：**
```json
{
  "duplicates": [
    {
      "skill": "new-skill",
      "duplicates_with": [
        {
          "existing_skill": "existing-skill",
          "similarity": 0.95,
          "similarity_type": "content",
          "content_hash": "abc123..."
        }
      ],
      "suggestion": "merge"  // "keep", "merge", "replace"
    }
  ]
}
```

### 4.2 VersionManager (版本管理模块)

**职责：**
- 管理技能版本历史
- 自动或手动版本号递增
- 版本回滚

**版本号规则：** 语义化版本 (Semantic Versioning)
- MAJOR.MINOR.PATCH
- MAJOR: 不兼容的 API 变更
- MINOR: 向下兼容的功能新增
- PATCH: 向下兼容的问题修正

**接口设计：**
```python
class VersionManager:
    def __init__(self, config):
        self.versions_dir = config['versions_dir']
        self.max_versions = config['versioning']['max_versions']
    
    def create_version(self, skill_name, skill_data, change_type, change_description):
        """创建新版本"""
        pass
    
    def get_version(self, skill_name, version):
        """获取指定版本"""
        pass
    
    def get_latest_version(self, skill_name):
        """获取最新版本"""
        pass
    
    def list_versions(self, skill_name):
        """列出所有版本"""
        pass
    
    def rollback(self, skill_name, target_version):
        """回滚到指定版本"""
        pass
    
    def increment_version(self, current_version, change_type):
        """递增版本号"""
        pass
```

### 4.3 ChangeTracker (变更跟踪模块)

**职责：**
- 记录所有变更操作
- 支持变更历史查询
- 生成变更报告

**变更类型：**
- `create` - 创建新技能
- `update` - 更新技能
- `delete` - 删除技能
- `archive` - 归档技能
- `restore` - 恢复技能
- `merge` - 合并技能
- `split` - 拆分技能
- `duplicate_detected` - 检测到重复
- `conflict_resolved` - 解决冲突

**接口设计：**
```python
class ChangeTracker:
    def __init__(self, config):
        self.changes_dir = config['changes_dir']
    
    def record(self, action, skill_data, extra_data=None):
        """记录变更"""
        pass
    
    def get_history(self, skill_name, start_date=None, end_date=None):
        """获取技能的变更历史"""
        pass
    
    def get_recent_changes(self, limit=10):
        """获取最近的变更"""
        pass
    
    def generate_report(self, date_range=None):
        """生成变更报告"""
        pass
```

### 4.4 DependencyManager (依赖管理模块)

**职责：**
- 分析技能之间的依赖关系
- 构建依赖图
- 检测循环依赖
- 生成依赖报告

**依赖类型：**
- `uses` - 使用
- `extends` - 扩展
- `implements` - 实现
- `requires` - 需要

**接口设计：**
```python
class DependencyManager:
    def __init__(self, config):
        self.dependencies_file = config['dependencies_file']
    
    def analyze_dependencies(self, skill_data):
        """分析技能的依赖"""
        pass
    
    def add_dependency(self, from_skill, to_skill, dep_type, strength=1.0):
        """添加依赖关系"""
        pass
    
    def remove_dependency(self, from_skill, to_skill):
        """移除依赖关系"""
        pass
    
    def get_dependencies(self, skill_name):
        """获取技能的依赖"""
        pass
    
    def get_dependents(self, skill_name):
        """获取依赖此技能的其他技能"""
        pass
    
    def detect_cycles(self):
        """检测循环依赖"""
        pass
    
    def visualize(self, output_format="dot"):
        """生成依赖图可视化"""
        pass
```

### 4.5 QualityEvaluator (质量评估模块)

**职责：**
- 评估技能质量
- 基于多个维度打分
- 生成质量报告
- 提供改进建议

**评估维度：**
1. **完整性 (Completeness)** - 是否包含所有必需的部分
2. **文档质量 (Documentation)** - 文档是否清晰完整
3. **示例质量 (Examples)** - 是否有实用的示例
4. **清晰度 (Clarity)** - 表达是否清晰易懂
5. **可重用性 (Reusability)** - 是否可以在不同场景下使用

**接口设计：**
```python
class QualityEvaluator:
    def __init__(self, config):
        self.criteria = config['quality']
    
    def evaluate(self, skill_data):
        """评估技能质量"""
        pass
    
    def evaluate_batch(self, skills_data):
        """批量评估技能"""
        pass
    
    def get_score(self, skill_name):
        """获取技能的质量分数"""
        pass
    
    def generate_report(self, skill_name=None):
        """生成质量报告"""
        pass
    
    def suggest_improvements(self, skill_name):
        """生成改进建议"""
        pass
```

### 4.6 Publisher (发布管理模块)

**职责：**
- 与 ClawdHub 集成
- 管理发布流程
- 跟踪发布状态

**发布状态：**
- `draft` - 草稿
- `pending` - 待审核
- `published` - 已发布
- `rejected` - 已拒绝
- `archived` - 已归档

**接口设计：**
```python
class Publisher:
    def __init__(self, config):
        self.clawdhub_config = config['clawdhub_config']
    
    def publish(self, skill_name, version=None):
        """发布技能到 ClawdHub"""
        pass
    
    def unpublish(self, skill_name):
        """撤销发布"""
        pass
    
    def get_status(self, skill_name):
        """获取发布状态"""
        pass
    
    def sync_from_hub(self, skill_name=None):
        """从 ClawdHub 同步"""
        pass
```

---

## 5. CLI 接口设计

### 5.1 命令结构

```bash
skill-man <command> [options] [arguments]
```

### 5.2 主要命令

#### 5.2.1 `skill-man init`
初始化技能管理系统。

```bash
skill-man init [--config-dir PATH]
```

**功能：**
- 创建必要的目录结构
- 生成默认配置文件
- 初始化空的注册表

#### 5.2.2 `skill-man status`
查看系统状态。

```bash
skill-man status [--verbose]
```

**输出：**
```
Skill Management System v1.0.0

Registry: /root/clawd/skill-management/skills/registry.json
Total Skills: 23
  - Active: 23
  - Archived: 0
  - Published: 5

Recent Changes:
  2026-02-01 11:00 - Update: ai-genie-3-game-prompts v1.1.0
  2026-02-01 10:30 - Create: google-imagen-3-portraits v1.0.0

Quality Summary:
  - Average Score: 82.5
  - Above Threshold (60): 23/23
  - Need Improvement: 0
```

#### 5.2.3 `skill-man scan`
扫描技能目录。

```bash
skill-man scan [path] [--recursive] [--auto-register]
```

**功能：**
- 扫描指定目录下的技能
- 识别新技能
- 更新现有技能

#### 5.2.4 `skill-man check`
检查重复和冲突。

```bash
skill-man check [--fix] [--report FILE]
```

**功能：**
- 检测重复技能
- 检测版本冲突
- 生成去重报告
- 可选自动修复

#### 5.2.5 `skill-man diff`
比较两个技能。

```bash
skill-man diff <skill1> <skill2> [--format json|text]
```

**输出：**
```
Comparing: ai-genie-3-game-prompts vs ai-game-prompts

Similarity: 0.95 (High)

Differences:
  - Description: 80% similar
  - Content: 95% similar
  - Examples: Different

Recommendation: Merge or mark as duplicate
```

#### 5.2.6 `skill-man merge`
合并技能。

```bash
skill-man merge <source> <target> [--strategy auto|manual|keep-both]
```

**合并策略：**
- `auto` - 自动合并（简单合并）
- `manual` - 手动合并（需要用户确认）
- `keep-both` - 保留两个技能，标记为相关

#### 5.2.7 `skill-man publish`
发布技能。

```bash
skill-man publish <skill> [--version VERSION] [--dry-run]
```

**功能：**
- 发布到 ClawdHub
- 更新发布状态
- 跟踪发布结果

#### 5.2.8 `skill-man list`
列出技能。

```bash
skill-man list [--status all|active|archived|published] [--sort name|date|quality] [--filter TAG]
```

**输出：**
```
Skills (23 total)

NAME                          VERSION   STATUS      QUALITY   UPDATED
ai-genie-3-game-prompts       1.1.0     active      85        2026-02-01
google-imagen-3-portraits     1.0.0     published   90        2026-02-01
ai-portrait-generator         1.0.0     active      80        2026-01-31
...
```

#### 5.2.9 `skill-man history`
查看技能历史。

```bash
skill-man history <skill> [--limit N]
```

**输出：**
```
History: ai-genie-3-game-prompts

v1.1.0 - 2026-02-01 10:30
  Author: user
  Change: Added new prompt patterns
  
v1.0.0 - 2026-02-01 09:17
  Author: system
  Change: Initial version from prompts workflow
```

#### 5.2.10 `skill-man rollback`
回滚版本。

```bash
skill-man rollback <skill> <version> [--confirm]
```

**功能：**
- 回滚到指定版本
- 保留回滚前的版本
- 记录回滚操作

#### 5.2.11 `skill-man clean`
清理无效技能。

```bash
skill-man clean [--dry-run] [--remove-orphaned]
```

**功能：**
- 清理重复技能
- 清理无效文件
- 清理孤立版本

---

## 6. 与现有系统集成

### 6.1 与 Prompts Workflow 集成

**集成方案 1：后处理集成**

在 `convert-prompts-to-skills.py` 转换完成后，自动调用 Skill Management System：

```python
# 在 convert-prompts-to-skills.py 的 main() 函数末尾添加
def main():
    # ... 现有转换逻辑 ...
    
    # 集成 Skill Management System
    from skill_manager import SkillManager
    
    print("\n[集成] 调用 Skill Management System...")
    manager = SkillManager(config_path="/root/clawd/skill-management/config.json")
    
    # 扫描新生成的技能
    scan_result = manager.scan(SKILLS_OUTPUT_DIR)
    
    # 检查重复
    duplicates = manager.check_duplicates()
    
    if duplicates['duplicates']:
        print(f"\n⚠️  检测到 {len(duplicates['duplicates'])} 个重复技能")
        manager.generate_duplicate_report(duplicates)
    else:
        print("\n✅ 未检测到重复技能")
    
    # 评估质量
    quality_report = manager.evaluate_quality()
    print(f"\n📊 质量评估完成: 平均分 {quality_report['average_score']}")
```

**集成方案 2：中间件集成**

创建一个中间件脚本 `convert-with-management.py`：

```python
#!/usr/bin/env python3
"""
集成 Prompts Workflow 和 Skill Management System 的中间件
"""

from convert_prompts_to_skills import main as convert_main
from skill_manager import SkillManager

def main():
    # 1. 执行转换
    convert_main()
    
    # 2. 执行管理
    manager = SkillManager()
    manager.scan()
    manager.check_duplicates()
    manager.evaluate_quality()
    
    # 3. 生成报告
    manager.generate_integrated_report()

if __name__ == "__main__":
    main()
```

### 6.2 与 ClawdHub 集成

**集成方案：**

```python
class ClawdHubPublisher:
    def __init__(self, config):
        self.config = config['clawdhub_config']
        self.registry_url = self.config['registry_url']
        self.config_path = self.config['config_path']
    
    def publish(self, skill_name, version=None):
        """发布技能到 ClawdHub"""
        # 1. 读取技能数据
        skill_data = self._load_skill_data(skill_name)
        
        # 2. 构建发布包
        package = self._build_package(skill_data, version)
        
        # 3. 调用 ClawdHub CLI
        import subprocess
        cmd = [
            'clawdhub', 'publish',
            '--registry', self.registry_url,
            package['path']
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 4. 更新发布状态
            self._update_publish_status(skill_name, version, 'published')
            return True
        else:
            self._update_publish_status(skill_name, version, 'failed')
            return False
    
    def sync_from_hub(self, skill_name=None):
        """从 ClawdHub 同步"""
        import subprocess
        cmd = ['clawdhub', 'list', '--registry', self.registry_url]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 解析并更新本地注册表
        # ...
```

---

## 7. 实施计划

### 7.1 阶段一：核心功能 (Phase 1: Core)

**目标：** 实现基础的去重和版本管理功能

**任务：**
1. ✅ 设计数据模型
2. ✅ 实现存储层（JSON）
3. 🔲 实现 Deduplicator 模块
4. 🔲 实现 VersionManager 模块
5. 🔲 实现 ChangeTracker 模块
6. 🔲 实现基础 CLI 命令（init, status, scan, check）

**预期时间：** 3-5 天

### 7.2 阶段二：高级功能 (Phase 2: Advanced)

**目标：** 实现依赖管理和质量评估

**任务：**
1. 🔲 实现 DependencyManager 模块
2. 🔲 实现 QualityEvaluator 模块
3. 🔲 实现高级 CLI 命令（diff, merge, history, rollback）
4. 🔲 实现依赖图可视化
5. 🔲 实现质量报告生成

**预期时间：** 3-5 天

### 7.3 阶段三：集成与发布 (Phase 3: Integration)

**目标：** 与现有系统集成并支持发布

**任务：**
1. 🔲 实现 Publisher 模块
2. 🔲 与 Prompts Workflow 集成
3. 🔲 与 ClawdHub 集成
4. 🔲 实现完整的 CLI 命令（publish, list, clean）
5. 🔲 编写文档和测试

**预期时间：** 3-5 天

### 7.4 阶段四：优化与测试 (Phase 4: Optimization)

**目标：** 性能优化和完善测试

**任务：**
1. 🔲 性能优化（缓存、索引）
2. 🔲 完善单元测试
3. 🔲 集成测试
4. 🔲 文档完善
5. 🔲 用户指南

**预期时间：** 2-3 天

**总预期时间：** 11-18 天

---

## 8. 技术细节

### 8.1 相似度计算

**内容相似度：**

```python
from difflib import SequenceMatcher

def content_similarity(text1, text2):
    """使用 difflib 计算文本相似度"""
    return SequenceMatcher(None, text1, text2).ratio()

# 或使用 TF-IDF + 余弦相似度
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def tfidf_similarity(text1, text2):
    """使用 TF-IDF 计算相似度"""
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return similarity
```

**名称相似度：**

```python
from Levenshtein import distance as levenshtein_distance

def name_similarity(name1, name2):
    """使用 Levenshtein 距离计算名称相似度"""
    max_len = max(len(name1), len(name2))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(name1.lower(), name2.lower())
    return 1.0 - (dist / max_len)
```

### 8.2 版本号递增

```python
from packaging import version

def increment_version(current_version, change_type):
    """递增版本号"""
    v = version.parse(current_version)
    major, minor, patch = v.major, v.minor, v.micro
    
    if change_type == "major":
        return f"{major + 1}.0.0"
    elif change_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif change_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        return current_version
```

### 8.3 质量评分算法

```python
def calculate_quality_score(skill_data, criteria):
    """计算质量分数"""
    scores = {}
    
    # 完整性
    scores['completeness'] = check_completeness(skill_data) * criteria['completeness']['weight']
    
    # 文档质量
    scores['documentation'] = check_documentation(skill_data) * criteria['documentation']['weight']
    
    # 示例质量
    scores['examples'] = check_examples(skill_data) * criteria['examples']['weight']
    
    # 清晰度
    scores['clarity'] = check_clarity(skill_data) * criteria['clarity']['weight']
    
    # 可重用性
    scores['reusability'] = check_reusability(skill_data) * criteria['reusability']['weight']
    
    # 总分
    overall = sum(scores.values())
    
    return {
        'overall': overall,
        'scores': scores
    }
```

---

## 9. 文件结构

```
/root/clawd/
├── scripts/
│   ├── skill-management/
│   │   ├── __init__.py
│   │   ├── skill_man.py           # CLI 主入口
│   │   ├── skill_manager.py       # 核心管理器
│   │   ├── deduplicator.py        # 去重模块
│   │   ├── version_manager.py    # 版本管理
│   │   ├── change_tracker.py     # 变更跟踪
│   │   ├── dependency_manager.py  # 依赖管理
│   │   ├── quality_evaluator.py   # 质量评估
│   │   └── publisher.py           # 发布管理
│   └── convert-with-management.py # 集成中间件
│
├── skill-management/              # 数据存储
│   ├── config.json
│   ├── skills/
│   │   └── registry.json
│   ├── versions/
│   ├── changes/
│   ├── dependencies/
│   │   └── graph.json
│   ├── quality/
│   │   └── scores.json
│   └── logs/
│
└── docs/
    └── skill-management-system-architecture.md  # 本文档
```

---

## 10. 配置示例

### 10.1 初始化配置

```bash
# 初始化系统
skill-man init

# 或指定配置目录
skill-man init --config-dir /root/clawd/skill-management
```

### 10.2 日常使用

```bash
# 扫描新技能
skill-man scan /root/clawd/generated-skills --auto-register

# 检查重复
skill-man check --report /root/clawd/duplicate-report.json

# 查看状态
skill-man status

# 列出所有技能
skill-man list --sort quality

# 查看特定技能历史
skill-man history ai-genie-3-game-prompts

# 发布技能
skill-man publish ai-genie-3-game-prompts --version 1.0.0

# 生成集成报告（与 prompts workflow）
skill-man generate-integrated-report
```

---

## 11. 后续扩展

### 11.1 Web UI
在终端工具完善后，可以开发 Web UI 以提供更好的用户体验：
- 技能浏览和搜索
- 可视化依赖图
- 质量仪表板
- 发布管理界面

### 11.2 数据库支持
当数据量增大时，可以迁移到数据库：
- SQLite（本地）
- PostgreSQL（远程）
- MongoDB（文档存储）

### 11.3 分布式支持
支持多机协作：
- 分布式版本控制
- 共享注册表
- 冲突解决机制

---

## 12. 总结

本架构设计文档提供了一个完整的 Skill 管理系统方案，包括：

1. **核心功能**：去重检测、版本管理、变更跟踪、依赖管理、质量评估、发布管理
2. **数据模型**：基于 JSON 的简单存储方案，易于迁移
3. **CLI 接口**：友好的命令行工具，支持常用操作
4. **集成方案**：与现有 Prompts Workflow 和 ClawdHub 无缝集成
5. **实施计划**：分四个阶段逐步实施，预计 11-18 天完成

**关键优势：**
- ✅ 与现有代码风格一致（Python）
- ✅ 存储简单（JSON），易于迁移
- ✅ 模块化设计，易于扩展
- ✅ 完整的 CLI 工具，易于使用
- ✅ 与现有系统无缝集成

**下一步行动：**
1. 开始实施阶段一（核心功能）
2. 实现基础模块（Deduplicator, VersionManager, ChangeTracker）
3. 实现基础 CLI 命令
4. 进行测试和迭代

---

**文档版本：** 1.0.0
**创建日期：** 2026-02-01
**作者：** Subagent for Skill Management System Design
**状态：** Draft - Ready for Implementation
