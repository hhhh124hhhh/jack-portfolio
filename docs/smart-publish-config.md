# 🔧 Smart Publisher 配置指南

## 快速设置

### 1. 获取 ClawdHub Token

访问 [ClawdHub](https://clawdhub.com) 获取你的 API token。

### 2. 设置环境变量

**临时设置（当前会话）：**
```bash
export CLAWDHUB_TOKEN="your_token_here"
```

**永久设置（推荐）：**
```bash
# 添加到 ~/.bashrc
echo 'export CLAWDHUB_TOKEN="your_token_here"' >> ~/.bashrc

# 重新加载配置
source ~/.bashrc
```

### 3. 验证配置

```bash
# 检查 token 是否设置
echo $CLAWDHUB_TOKEN

# 测试登录
clawdhub whoami
```

## 手动登录（备选方案）

如果 token 方法不工作，可以手动登录：

```bash
clawdhub login
# 按照提示输入 token
```

## 配置文件模板

创建 `~/.clawdhub/config.json`:

```json
{
  "token": "your_token_here",
  "registry": "https://clawdhub.com",
  "defaultWorkdir": "./skills"
}
```

## 检查清单

使用前确认以下事项：

- [ ] ClawdHub CLI 已安装：`which clawdhub`
- [ ] Claude Code 已安装：`which claude`
- [ ] jq 工具已安装：`which jq`
- [ ] CLAWDHUB_TOKEN 已设置：`echo $CLAWDHUB_TOKEN`
- [ ] 已登录成功：`clawdhub whoami`

## 故障排查

### 问题：Unauthorized

**解决方案：**
1. 检查 token 是否正确
2. 重新登录：`clawdhub login`
3. 检查 token 是否过期

### 问题：Command not found

**解决方案：**
```bash
# 安装 ClawdHub CLI
npm install -g clawdhub

# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 安装 jq
apt-get install jq  # Ubuntu/Debian
# brew install jq   # macOS
```

### 问题：Permission denied

**解决方案：**
```bash
# 确保脚本有执行权限
chmod +x /root/clawd/bin/smart-publish-v2.sh
```

## 测试配置

使用测试技能验证配置：

```bash
cd /root/clawd

# 运行测试发布（手动模式）
./bin/smart-publish-v2.sh \
  ./test-skill \
  --slug test-skill \
  --name "Test Skill" \
  --version 0.0.1

# 或自动模式（检测通过后直接发布）
./bin/smart-publish-v2.sh \
  ./test-skill \
  --slug test-skill \
  --name "Test Skill" \
  --version 0.0.1 \
  --auto
```

## 环境变量参考

| 变量 | 说明 | 示例 |
|------|------|------|
| `CLAWDHUB_TOKEN` | ClawdHub API token | `clh_xxxxxxxx` |
| `CLAUDE_MODEL` | Claude 模型（可选） | `claude-3.5-sonnet` |
| `REVIEW_TIMEOUT` | 审查超时时间（秒） | `300` |

## 相关文件

- 智能发布工具：`/root/clawd/bin/smart-publish-v2.sh`
- 快速参考：`/root/clawd/bin/PUBLISH_QUICKREF.md`
- 完整文档：`/root/clawd/docs/smart-publish-guide.md`
- 测试技能：`/root/clawd/test-skill`

---

**下一步：** 配置完成后，查看 `PUBLISH_QUICKREF.md` 开始使用！
