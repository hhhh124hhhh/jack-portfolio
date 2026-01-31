# 🚀 Smart Skill Publisher - 使用指南

## 功能特点

1. **自动质量检测**：使用 Claude Coding Agent 检测技能质量
2. **结构化审查**：检查 SKILL.md、代码质量、最佳实践、发布就绪性
3. **智能决策**：根据审查结果自动批准或拒绝发布
4. **自动化发布**：检测通过后自动上传到 ClawdHub

## 安装依赖

```bash
# 安装 ClawdHub CLI
npm install -g clawdhub

# 安装 Claude Code（推荐）
npm install -g @anthropic-ai/claude-code

# 或安装 Codex CLI（备选）
# 详见文档

# 登录 ClawdHub
clawdhub login
```

## 基本用法

### 1. 手动模式（默认）

```bash
/root/clawd/bin/smart-publish-v2.sh ./my-skill --slug my-skill --name "My Skill" --version 1.0.0
```

流程：
- ✅ 运行质量检测
- 👀 显示审查结果
- ✋ 询问是否发布
- 📤 确认后发布到 ClawdHub

### 2. 自动模式（--auto）

```bash
/root/clawd/bin/smart-publish-v2.sh ./my-skill --slug my-skill --name "My Skill" --version 1.0.0 --auto
```

流程：
- ✅ 运行质量检测
- ✅ 检测通过直接发布（无需确认）
- 📤 自动上传到 ClawdHub

**适合：** CI/CD 流程、批量发布

### 3. 强制模式（--force）

```bash
/root/clawd/bin/smart-publish-v2.sh ./my-skill --slug my-skill --name "My Skill" --version 1.0.0 --force
```

流程：
- ⏭️ 跳过质量检测
- ✋ 询问是否发布
- 📤 确认后发布到 ClawdHub

**适合：** 你确定技能质量、快速发布

## 参数说明

| 参数 | 必需 | 说明 | 示例 |
|------|------|------|------|
| `<skill-path>` | ✅ | 技能目录路径 | `./my-skill` |
| `--slug` | ✅ | 技能唯一标识 | `my-awesome-skill` |
| `--name` | ❌ | 技能显示名称 | `"My Awesome Skill"` |
| `--version` | ❌ | 版本号 | `1.0.0` |
| `--changelog` | ❌ | 更新日志 | `"Fixed bug #123"` |
| `--auto` | ❌ | 自动发布模式 | - |
| `--force` | ❌ | 强制跳过检测 | - |

## 质量检测标准

Claude 会检测以下方面：

### 1. SKILL.md 质量
- ✅ 清晰的名称和描述
- ✅ 完整的使用说明
- ✅ 可运行的示例
- ✅ 记录依赖项
- ✅ 有效的 metadata 部分

### 2. 代码质量（如果有）
- ✅ 遵循 Clawdbot 惯例
- ✅ 无硬编码密钥
- ✅ 适当的错误处理
- ✅ 代码清晰易读

### 3. 最佳实践
- ✅ 正确的工具调用模式
- ✅ 无安全问题
- ✅ 完整的文档
- ✅ 无已弃用的 API

### 4. 发布就绪性
- ✅ 所有必需文件存在
- ✅ 可无错误安装
- ✅ 按文档说明工作

## 审查输出示例

```
───────────────────────────────────────
  📊 Review Results
───────────────────────────────────────

Score: 9/10
Recommendation: APPROVE

Critical Issues: None
Summary: Well-documented skill with clear instructions. Ready for publish.

Full Review:
# Skill Quality Review

## Overall Score: 9/10

## Critical Issues (must fix before publish)
- None

## Warnings (should fix)
- Consider adding error handling examples

## Suggestions (nice to have)
- Add more edge case examples

## Recommendation
- ✅ APPROVE for publish

## Summary
Well-documented skill with clear instructions. Ready for publish.
```

## CI/CD 集成示例

### GitHub Actions

```yaml
name: Publish Skill

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install ClawdHub CLI
        run: npm install -g clawdhub

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Login to ClawdHub
        run: clawdhub login
        env:
          CLAWDHUB_TOKEN: ${{ secrets.CLAWDHUB_TOKEN }}

      - name: Publish Skill
        run: |
          /root/clawd/bin/smart-publish-v2.sh \
            ./my-skill \
            --slug my-skill \
            --name "My Skill" \
            --version ${GITHUB_REF#refs/tags/v} \
            --auto
```

### Cron 任务（自动发布）

```bash
# 每天凌晨 2 点检查并发布准备好的技能
0 2 * * * /root/clawd/bin/smart-publish-v2.sh ./skills/pending/my-skill --slug my-skill --auto >> /var/log/publish.log 2>&1
```

## 工作流程建议

### 新技能发布流程

```bash
# 1. 创建技能
mkdir -p ./my-skill
cd my-skill

# 2. 编写 SKILL.md
cat > SKILL.md << 'EOF'
---
name: my-skill
description: My awesome skill
metadata: {}
---

# My Skill

## Usage
...
EOF

# 3. 添加代码和文档
# ... write your code ...

# 4. 测试技能
# ... test locally ...

# 5. 使用智能发布工具
cd ..
/root/clawd/bin/smart-publish-v2.sh \
  ./my-skill \
  --slug my-skill \
  --name "My Skill" \
  --version 1.0.0

# 6. 如果检测通过，确认发布
# 7. 技能成功发布到 ClawdHub！
```

### 批量发布多个技能

```bash
#!/bin/bash
# batch-publish.sh

SKILLS=(
  "skill1:skill-1:Skill 1:1.0.0"
  "skill2:skill-2:Skill 2:1.0.0"
  "skill3:skill-3:Skill 3:1.0.0"
)

for skill_info in "${SKILLS[@]}"; do
  IFS=':' read -r path slug name version <<< "$skill_info"

  echo "Publishing: $name"
  /root/clawd/bin/smart-publish-v2.sh \
    "./skills/$path" \
    --slug "$slug" \
    --name "$name" \
    --version "$version" \
    --auto

  if [[ $? -eq 0 ]]; then
    echo "✅ $name published successfully"
  else
    echo "❌ $name failed to publish"
  fi
  echo ""
done
```

## 故障排查

### 问题：Claude Code 未找到

```bash
npm install -g @anthropic-ai/claude-code
```

### 问题：无法登录 ClawdHub

```bash
# 检查 token 是否正确
clawdhub whoami

# 重新登录
clawdhub login
```

### 问题：审查超时

```bash
# 增加超时时间
export REVIEW_TIMEOUT=600
/root/clawd/bin/smart-publish-v2.sh ...
```

### 问题：JSON 解析失败

安装 `jq` 工具：

```bash
# Ubuntu/Debian
apt-get install jq

# macOS
brew install jq

# 或使用脚本内置的备用解析（无需 jq）
```

## 高级用法

### 自定义审查提示

编辑 `smart-publish-v2.sh` 中的 `review_prompt.md` 部分，添加自定义检查项。

### 集成到项目根目录的 Makefile

```makefile
.PHONY: publish
publish:
	/root/clawd/bin/smart-publish-v2.sh ./my-skill --slug my-skill --name "My Skill" --version $(VERSION)

publish-auto:
	/root/clawd/bin/smart-publish-v2.sh ./my-skill --slug my-skill --name "My Skill" --version $(VERSION) --auto
```

使用：

```bash
make publish VERSION=1.2.3
make publish-auto VERSION=1.2.3
```

## 最佳实践

1. **始终使用检测**：除非非常确定，否则不要使用 `--force`
2. **版本号遵循语义化**：`MAJOR.MINOR.PATCH`
3. **更新日志要清晰**：描述变更内容，方便用户了解
4. **先在本地测试**：确保技能在实际环境中工作正常
5. **响应审查建议**：Claude 的建议通常有价值

## 相关链接

- [ClawdHub 文档](https://docs.clawd.bot)
- [Clawdbot Skills](https://clawdhub.com)
- [Claude Code 文档](https://github.com/anthropics/claude-code)

---

**提示**：第一次使用时建议用手动模式，熟悉流程后再使用 `--auto` 自动化。
