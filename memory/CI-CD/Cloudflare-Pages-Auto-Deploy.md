# Cloudflare Pages 自动部署经验总结

## 📋 概述

本文档记录了配置 Cloudflare Pages 自动部署的完整经验、问题和解决方案。

---

## 🎯 项目信息

**项目名称**: jack-portfolio  
**Cloudflare Pages URL**: https://jack-portfolio-5un.pages.dev/  
**GitHub 仓库**: https://github.com/hhhh124hhhh/jack-portfolio  
**GitHub Actions**: 自动部署已配置 ✅

---

## 🔧 配置历程

### 第一次尝试 (失败)

**配置**:
- 项目名称: `jack-portfolio`
- Action: `cloudflare/wrangler-action@v3`
- 结果: ❌ 失败

**错误信息**:
```
Error: The process '/usr/local/bin/npx' failed with exit code 1
```

**原因**: Wrangler Action 版本兼容性问题

---

### 第二次尝试 (失败)

**配置**:
- 项目名称: `jack-portfolio-5un`（错误：用了自定义域名）
- Action: `cloudflare/wrangler-action@v3`
- 结果: ❌ 失败

**错误**: 同第一次尝试

**原因**:
1. 项目名称错误（用了自定义域名）
2. Wrangler Action 问题未解决

---

### 第三次尝试 (失败)

**配置**:
- 项目名称: `jack-portfolio-5un`（还是错误）
- Action: `cloudflare/pages-action@v1`（改为官方 Action）
- 结果: ❌ 部署成功，但页面未更新

**原因**: 项目名称仍然是自定义域名，部署到了错误的项目

---

### 第四次尝试 (成功)

**配置**:
- 项目名称: `jack-portfolio`（正确的项目名称）
- Action: `cloudflare/pages-action@v1`（官方 Action）
- 结果: ✅ 成功

**成功原因**:
1. 使用了正确的项目名称
2. 使用了官方 Cloudflare Pages Action

---

## 🔍 关键发现

### 项目名称 vs 自定义域名

**项目名称**:
- Cloudflare 内部标识
- 用于 API 调用
- 配置文件中使用
- 示例: `jack-portfolio`

**自定义域名**:
- 访问 URL
- 对外展示
- 不用于配置
- 示例: `jack-portfolio-5un.pages.dev`

**重要**: 配置文件中使用的是 **项目名称**，不是自定义域名！

### 如何找到正确的项目名称

**方法 1: 查看 Dashboard URL**
1. 访问 Cloudflare Dashboard
2. 进入 Pages 项目
3. **查看 URL 路径**: `/pages/view/<项目名称>/...`
4. 提取 `<项目名称>`

**示例**:
- Dashboard URL: `dash.cloudflare.com/.../pages/view/jack-portfolio/...`
- 项目名称: `jack-portfolio`

### Action 选择

**推荐**: `cloudflare/pages-action@v1`
- Cloudflare 官方维护
- 专为 Cloudflare Pages 设计
- 更稳定可靠
- 更简单的配置

**不推荐**: `cloudflare/wrangler-action@v3`
- 通用 Wrangler 工具
- 兼容性问题较多
- 复杂的配置

---

## 📝 配置模板

### GitHub Actions Workflow

**文件**: `.github/workflows/deploy-cloudflare.yml`

**内容**:
```yaml
name: Deploy to Cloudflare Pages

on:
  # 自动部署：当推送到 main 分支时
  push:
    branches:
      - main
  # 手动触发
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    name: Deploy to Cloudflare Pages
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: <项目名称>
          directory: .
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

**注意**: 将 `<项目名称>` 替换为实际的 Cloudflare Pages 项目名称。

### GitHub Secrets

**需要的 Secrets**:

1. **CLOUDFLARE_API_TOKEN**
   - 获取方式: https://dash.cloudflare.com/profile/api-tokens
   - 权限: Cloudflare Pages → Edit
   - 只显示一次，请妥善保存

2. **CLOUDFLARE_ACCOUNT_ID**
   - 获取方式: Cloudflare Dashboard URL 或 Profile 页面
   - 格式: 32 个字符的十六进制字符串

---

## 🔍 常见问题

### 问题 1: Wrangler Action 失败

**错误信息**:
```
Error: The process '/usr/local/bin/npx' failed with exit code 1
```

**原因**: Wrangler Action 版本兼容性问题

**解决方案**:
1. 切换到官方 Pages Action: `cloudflare/pages-action@v1`
2. 重新配置 workflow

---

### 问题 2: 项目名称错误

**症状**: 部署成功，但页面未更新

**原因**: 使用了自定义域名作为项目名称

**解决方案**:
1. 查看 Cloudflare Dashboard URL 路径
2. 提取正确的项目名称
3. 更新 workflow 配置

---

### 问题 3: 部署成功但页面未更新

**原因**: Cloudflare CDN 缓存

**解决方案**:
1. 强制刷新浏览器（Ctrl+Shift+R）
2. 等待 5-10 分钟让 CDN 缓存更新
3. 访问预览 URL（最新部署的 URL）

---

### 问题 4: GitHub Secrets 配置错误

**症状**: GitHub Actions 失败，提示 Token 或 Account ID 错误

**原因**: Secrets 名称或值不正确

**解决方案**:
1. 确认 Secrets 名称完全匹配：
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
2. 确认 Secrets 值正确
3. 重新配置 Secrets

---

## 📊 最佳实践

### 1. 使用官方 Action

**推荐**: `cloudflare/pages-action@v1`  
**原因**: 官方维护，更稳定

### 2. 正确的项目命名

**项目名称**: Cloudflare 内部标识  
**自定义域名**: 访问 URL  
**配置文件**: 使用项目名称

### 3. 自动触发配置

**推荐配置**:
```yaml
on:
  push:
    branches:
      - main
  workflow_dispatch:
```

**说明**:
- 自动触发: 推送到 `main` 分支时
- 手动触发: 在 GitHub Actions 页面手动触发

### 4. 部署验证

**验证清单**:
- [ ] GitHub Actions 状态是 "Success"
- [ ] Cloudflare Pages 部署记录显示最新内容
- [ ] Cloudflare Pages URL 显示最新内容
- [ ] 所有功能正常

---

## 🚀 未来工作流程

### 正常开发流程

```bash
# 1. 修改代码
vim index.html

# 2. 提交更改
git add .
git commit -m "feat: 新功能或优化"

# 3. 推送到 GitHub
git push origin main

# 4. GitHub Actions 自动部署（无需手动操作）
# 等待 1-3 分钟

# 5. 查看结果
# https://jack-portfolio-5un.pages.dev/
```

---

## 📚 相关文档

### 项目文档
- Cloudflare Pages 自动部署指南: `CLOUDFLARE-AUTO-DEPLOY.md`
- Cloudflare Pages 修复指南: `CLOUDFLARE-PAGES-FIX.md`
- Cloudflare Pages 教程: `CLOUDFLARE-PAGES-TUTORIAL.md`
- 部署选项说明: `DEPLOYMENT-OPTIONS.md`

### 官方文档
- [Cloudflare Pages 文档](https://developers.cloudflare.com/pages/)
- [Cloudflare Pages Action](https://github.com/cloudflare/pages-action)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

---

## 🎯 总结

### 配置要点
1. 获取 Cloudflare 凭证（API Token、Account ID、项目名称）
2. 配置 GitHub Secrets
3. 创建 GitHub Actions workflow
4. 验证部署

### 关键要点
1. 使用官方 Action: `cloudflare/pages-action@v1`
2. 项目名称是 Cloudflare 内部标识，不是自定义域名
3. 从 Dashboard URL 路径找到正确的项目名称
4. 推送到 `main` 分支时自动触发部署

### 常见错误
1. 使用自定义域名作为项目名称 ❌
2. 使用非官方 Action ❌
3. 项目名称配置错误 ❌
4. Secrets 配置错误 ❌

---

## 🆘 经验教训

### 项目名称混淆
- **错误**: 使用自定义域名作为项目名称
- **正确**: 使用 Dashboard URL 路径中的项目名称
- **教训**: 项目名称和自定义域名是两个不同的概念

### Action 选择
- **错误**: 使用 `cloudflare/wrangler-action@v3`
- **正确**: 使用 `cloudflare/pages-action@v1`
- **教训**: 使用官方 Action 更稳定可靠

### 调试方法
- **错误**: 盲目尝试不同配置
- **正确**: 查看详细错误日志，分析 Dashboard URL
- **教训**: 理解问题本质，系统化调试

---

## 📅 时间记录

**配置开始**: 2026-02-07 20:35  
**配置成功**: 2026-02-07 21:53  
**总耗时**: 约 1 小时 18 分钟  
**尝试次数**: 4 次  
**最终状态**: ✅ 成功

---

**文档创建时间**: 2026-02-07 22:35  
**最后更新**: 2026-02-07 22:35
