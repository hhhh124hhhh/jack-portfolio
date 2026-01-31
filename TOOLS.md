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
- **Preferred:** searXNG (local instance)
- **Avoid:** Brave Search API (configuration issues)
- **Reason:** User unable to configure Brave search properly
- **Usage:** Always use searXNG for web searches unless explicitly asked otherwise

### API Keys
- **Twitter/X API Key**: 已配置 (从 ~/.bashrc 加载)
  - 配置位置：`~/.bashrc`
  - 环境变量名：`TWITTER_API_KEY`
  - 服务提供商：twitterapi.io
  - 注意：此 key 已配置，脚本会自动加载

- **ClawdHub Token**: `clh_6aVBxdBkWmSOoZN9tUDX1nABYZFMqO_ARPUbHbkboj4`
  - 用途：ClawdHub CLI 认证 (用于发布和搜索技能)
  - 使用命令：`clawdhub login` (会提示输入 token)
  - 更新时间：2026-01-30
