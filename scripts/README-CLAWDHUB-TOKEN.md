# ClawdHub Token 管理脚本

## 脚本列表

### 1. `check-clawdhub-token.sh` - 交互式检测脚本
检测 ClawdHub Token 是否有效，提供更新指南。

**使用方法：**
```bash
bash /root/clawd/scripts/check-clawdhub-token.sh
```

**功能：**
- ✓ 检测当前 token 是否有效
- ✓ 显示 token 状态
- ✓ 提供更新指南
- ✓ 可选择更新 TOOLS.md 记录
- ✓ 可交互式输入新 token

---

### 2. `check-clawdhub-token-auto.sh` - 自动检测脚本
非交互式检测，适合用于 cron 或自动化任务。

**使用方法：**
```bash
bash /root/clawd/scripts/check-clawdhub-token-auto.sh
```

**功能：**
- ✓ 自动检测 token 有效性
- ✓ 记录到日志文件
- ✓ 非交互式（适合自动化）
- ✓ 返回状态码（0=有效，1=无效）

**日志文件：**
- 检测日志：`/root/clawd/memory/clawdhub-token-check.log`
- 告警日志：`/root/clawd/memory/clawdhub-token-alerts.txt`

**示例：在 cron 中使用**
```bash
# 每小时检查一次 token 状态
0 * * * * bash /root/clawd/scripts/check-clawdhub-token-auto.sh
```

---

### 3. `update-clawdhub-token.sh` - 更新脚本
快速更新 ClawdHub Token。

**使用方法：**
```bash
bash /root/clawd/scripts/update-clawdhub-token.sh
```

**功能：**
- ✓ 交互式输入新 token
- ✓ 自动更新配置文件 `~/.config/clawdhub/config.json`
- ✓ 自动更新 TOOLS.md 记录
- ✓ 自动验证新 token
- ✓ 备份旧配置

**更新后的文件：**
- `~/.config/clawdhub/config.json`
- `/root/clawd/TOOLS.md`

---

## 如何获取新 Token？

1. 访问 https://clawdhub.com
2. 登录你的账户
3. 进入设置/个人资料页面
4. 复制新的 API Token
5. 运行更新脚本

---

## 常见问题

### Q: `clawdhub whoami` 返回 Unauthorized 怎么办？
A: 这是正常的，在服务器环境下 `whoami` 命令可能不支持。使用 `clawdhub search` 或 `clawdhub list` 测试 token 是否有效。

### Q: Token 多久会过期？
A: 具体时间取决于 ClawdHub 的策略。建议定期检查（例如每周一次）。

### Q: 如何自动检测 token 过期？
A: 将自动检测脚本添加到 cron：
```bash
crontab -e
# 添加以下行
0 */6 * * * bash /root/clawd/scripts/check-clawdhub-token-auto.sh || bash /root/clawd/scripts/send-alert.sh "ClawdHub Token 无效"
```

---

## 日志文件位置

- 检测日志：`/root/clawd/memory/clawdhub-token-check.log`
- 更新日志：`/root/clawd/memory/clawdhub-token-update.log`
- 告警日志：`/root/clawd/memory/clawdhub-token-alerts.txt`
