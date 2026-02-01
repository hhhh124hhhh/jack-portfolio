# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### Search Preferences
- **🚨 MANDATORY: ONLY use searXNG** for all web searches
- **FORBIDDEN:** Never use Brave Search API
- **Reason:** User explicitly requires searXNG exclusively
- **Usage:** Always use searXNG skill for any web search needs
- **Exception:** Only use other search methods if explicitly requested by user

### API Keys
- **Twitter/X API Key**: 已配置 (从 ~/.bashrc 加载)
  - 配置位置：`~/.bashrc`
  - 环境变量名：`TWITTER_API_KEY`
  - 服务提供商：twitterapi.io
  - 注意：此 key 已配置，脚本会自动加载

- **ClawdHub Token**: `clh_Ki_M1Xiws5Qzi83gqdZhYG3jXSuZOnEfQOxhaRsjHcw`
  - 用途：ClawdHub CLI 认证 (用于发布和搜索技能)
  - 配置位置：`~/.config/clawdhub/config.json`
  - Registry: `https://www.clawhub.ai/api` ⚠️ 必须使用此 URL
  - 更新时间：2026-02-01
  - 状态：✅ 已配置并验证 (可以发布、搜索和安装技能)
  - 旧 token (已废弃): `clh_6aVBxdBkWmSOoZN9tUDX1nABYZFMqO_ARPUbHbkboj4`
  - 更旧 token (已废弃): `clh_3y5KFMb3ulzh_wxIyRqm05YvfVgHbkGHvVxF80FQzbQ`

  **重要提示**：
  - ⚠️ Registry URL 必须是 `https://www.clawhub.ai/api`，不是 `clawdhub.com` 或 `clawhub.ai`
  - 服务器环境不支持浏览器认证，必须直接编辑配置文件
  - `clawdhub whoami` 命令可能返回 Unauthorized，但不影响其他功能
  - 使用 `clawdhub list` 和 `clawdhub search` 验证 token 是否有效
  - 发布技能时必须明确指定 `--registry https://www.clawhub.ai/api`

### Coding Agent
- **认知**: 使用 coding-agent 就是使用 Claude
- **用途**: 编程任务、代码编写、调试
- **调用方式**: 使用 `coding-agent` skill
- **原理**: 实际上调用的是 Claude 的编程能力
- **⚠️ 重要规则**: 所有文件操作和编程任务必须使用 coding-agent，不要自己直接执行文件！
  - 用户明确要求："你执行还是用 coding-agent 把，我发现你本身执行文件都能力很弱"
  - coding-agent 使用的是 Claude，能力强于我自己直接操作
  - 记录时间：2026-01-31

### NL to Exec Tool (自然语言命令解释器)
- **路径**: `/root/clawd/scripts/nl-to-exec.sh`
- **用途**: 将自然语言请求转换为可执行命令并执行
- **特点**:
  - 维护上下文记忆（用户偏好、任务历史、学习模式）
  - 使用子代理处理复杂请求
  - 内置常见任务模式匹配
  - 任务历史记录（JSON 格式）
- **使用方式**:
  - 交互模式: `bash /root/clawd/scripts/nl-to-exec.sh`
  - 单次执行: `bash /root/clawd/scripts/nl-to-exec.sh execute "你的需求"`
  - 查看上下文: `bash /root/clawd/scripts/nl-to-exec.sh context`
  - 查看历史: `bash /root/clawd/scripts/nl-to-exec.sh history`
- **内置模式**:
  - "批量处理skill" → 执行 batch-process-all-skills.sh
  - "上传skill" → 执行 batch-upload-skills-v3.sh
  - "转换prompt" → 执行 convert-prompts-to-skills.py
  - "搜索 X AI提示词" → 执行 search-x-prompts.py
  - "评估提示词" → 执行 evaluate-prompts.py
- **记忆位置**: `/root/clawd/memory/nl-exec/`
  - `context.json` - 上下文信息
  - `tasks/` - 任务历史（JSON 文件）
  - `sessions/` - 子代理会话记录
- **使用频率**: 高（经常使用）
