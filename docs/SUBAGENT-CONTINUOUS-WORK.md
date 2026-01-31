# 让子代理持续工作的方案指南

## 📋 问题背景
子代理（sub-agent）默认是单次任务执行模式，任务完成后不会自动继续。需要手动机制来让它们持续工作。

---

## 🎯 三种推荐方案

### 方案 1：Cron Jobs（最推荐）

**优点**：
- 系统级调度，可靠性高
- 支持灵活的定时规则
- 不依赖主会话状态

**设置方法**：

```bash
# 每小时唤醒子代理
clawdbot cron add \
  --schedule "0 * * * *" \
  --text "继续执行下一个任务，从 memory 读取当前进度" \
  --target "agent:main:subagent:ee7e0c4e-365a-4e84-820f-888985600896"

# 每 30 分钟唤醒（更频繁）
clawdbot cron add \
  --schedule "*/30 * * * *" \
  --text "检查待办任务并继续执行" \
  --target "agent:main:subagent:ee7e0c4e-365a-4e84-820f-888985600896"
```

**查看所有 cron jobs**：
```bash
clawdbot cron list
```

**删除 cron job**：
```bash
clawdbot cron remove <jobId>
```

---

### 方案 2：Bash 后台脚本

**优点**：
- 实时控制（随时启动/停止）
- 可查看实时日志
- 适合开发和调试阶段

**使用方法**：

```bash
# 启动持续触发器（默认 60 秒间隔）
/root/clawd/scripts/subagent-looper.sh agent:main:subagent:ee7e0c4e-365a-4e84-820f-888985600896

# 自定义间隔（例如 30 秒）
/root/clawd/scripts/subagent-looper.sh agent:main:subagent:ee7e0c4e-365a-4e84-820f-888985600896 30
```

**在后台运行**：
```bash
nohup /root/clawd/scripts/subagent-looper.sh agent:main:subagent:ee7e0c4e-365a-4e84-820f-888985600896 > /tmp/subagent-looper.log 2>&1 &

# 查看日志
tail -f /tmp/subagent-looper.log
```

**停止运行**：
```bash
# 查找进程
ps aux | grep subagent-looper

# 杀死进程
kill <PID>
```

---

### 方案 3：主会话 Heartbeat

**优点**：
- 与其他周期性检查整合
- 统一管理所有后台任务
- 避免过多独立进程

**设置方法**：

在 `/root/clawd/HEARTBEAT.md` 添加：

```markdown
- 检查子代理 `skills-converter-project` 的最后更新时间
- 如果超过 2 小时未更新，发送续命指令：
  `clawdbot sessions send agent:main:subagent:ee7e0c4e-365a-4e84-820f-888985600896 "继续执行任务"`
- 每次检查时更新 `/root/clawd/memory/heartbeat-state.json` 记录检查时间
```

---

## 🔍 监控子代理状态

### 查看所有会话
```bash
clawdbot sessions list --limit 20
```

### 查看子代理历史
```bash
clawdbot sessions history agent:main:subagent:ee7e0c4e-365a-4e84-820f-888985600896 --limit 50
```

### 查看子代理会话状态
```bash
clawdbot sessions list --kinds other --messageLimit 5
```

---

## 🛠️ 子代理任务设计技巧

### 让子代理自我管理

在子代理的初始任务中包含循环逻辑：

```
## 工作流程
1. 读取 memory/2026-01-29.md 获取当前状态
2. 执行下一个待办任务
3. 更新 memory 文件记录进度
4. 休息 30 秒
5. 回到步骤 1

## 停止条件
- 收到"停止"指令
- 所有任务完成
- 遇到无法解决的问题
```

### 关键决策点才汇报

- 批量处理相似任务后统一汇报
- 遇到关键决策时才请求主会话指示
- 定期（如每完成一个大任务）发送总结报告

---

## 📊 推荐配置

### 阶段 1：开发调试
使用 **方案 2（Bash 脚本）**
- 快速迭代测试
- 可实时查看日志
- 随时调整参数

### 阶段 2：稳定运行
使用 **方案 1（Cron Jobs）**
- 系统级调度，更可靠
- 不依赖终端会话
- 适合长期运行

### 阶段 3：多任务协调
使用 **方案 3（Heartbeat）**
- 统一管理多个子代理
- 与其他周期性任务整合
- 灵活的条件触发逻辑

---

## 🚨 常见问题

### Q: 子代理没有响应怎么办？
A:
1. 检查会话状态：`clawdbot sessions list`
2. 查看子代理历史：`clawdbot sessions history <sessionKey>`
3. 重启子代理：`clawdbot sessions spawn <任务描述>`

### Q: 如何暂停子代理？
A:
- **临时暂停**：停止触发器（cron 或脚本）
- **完全停止**：发送"停止"指令到子代理

### Q: 如何查看子代理的实时输出？
A:
- 查看会话历史：`clawdbot sessions history <sessionKey> --limit 100`
- 子代理应该定期向 memory 文件写入进度

### Q: 多个子代理同时运行会冲突吗？
A:
- 不同 sessionKey 的子代理互相独立
- 共享 memory 文件时注意加锁或分区
- 使用不同的 memory 文件（如 `memory/subagent-xxx.md`）

---

## 📝 快速命令参考

```bash
# 查看所有会话
clawdbot sessions list

# 启动子代理持续工作（Bash 脚本）
/root/clawd/scripts/subagent-looper.sh agent:main:subagent:ee7e0c4e-365a-4e84-820f-888985600896

# 设置定时唤醒（Cron）
clawdbot cron add --schedule "*/30 * * * *" --text "继续执行任务" --target "agent:main:subagent:ee7e0c4e-365a-4e84-820f-888985600896"

# 查看所有 cron jobs
clawdbot cron list

# 发送消息到子代理
clawdbot sessions send agent:main:subagent:ee7e0c4e-365a-4e84-820f-888985600896 "你的指令"

# 查看子代理历史
clawdbot sessions history agent:main:subagent:ee7e0c4e-365a-4e84-820f-888985600896
```

---

**最后更新**: 2026-01-29
**适用版本**: Clawdbot (latest)
