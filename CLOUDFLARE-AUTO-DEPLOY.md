# Cloudflare Pages 自动部署设置

## 🚀 GitHub Actions 自动部署已配置

### 已完成的配置

✅ 创建了 GitHub Actions 工作流：`.github/workflows/deploy-cloudflare.yml`
✅ 已推送到 GitHub 仓库

---

## 📋 需要配置 GitHub Secret

### 步骤 1: 访问 GitHub 仓库

**打开**：
```
https://github.com/hhhh124hhhh/hhhh124hhhh.github.io/settings/secrets/actions
```

---

### 步骤 2: 添加 Cloudflare API Token

1. **点击**: `New repository secret`
2. **Name**: `CLOUDFLARE_API_TOKEN`
3. **Value**: `Sd0vKvLKAVaKIScuBEEsPb1d3tAmL8aR-wh4M6sf`
4. **点击**: `Add secret`

---

### 步骤 3: 手动触发部署

**方式 A: 推送代码触发**

```bash
cd /tmp/hhhh124hhhh.github.io
git commit --allow-empty -m "触发 Cloudflare Pages 部署"
git push origin master
```

**方式 B: 在 GitHub 手动触发**

1. 访问：https://github.com/hhhh124hhhh/hhhh124hhhh.github.io/actions
2. 选择 workflow: `Deploy to Cloudflare Pages`
3. 点击: `Run workflow`

---

## ✅ 部署完成后

### 访问地址

**Cloudflare Pages**:
```
https://jack-portfolio.pages.dev
```

**GitHub Pages**（保留）:
```
https://hhhh124hhhh.github.io/
```

---

## 🔄 自动部署

以后每次推送代码到 `main` 分支时，会自动部署到：
- ✅ GitHub Pages
- ✅ Cloudflare Pages

---

## 📊 查看部署状态

**GitHub Actions**:
```
https://github.com/hhhh124hhhh/hhhh124hhhh.github.io/actions
```

**Cloudflare Pages**:
```
https://dash.cloudflare.com/
→ Workers & Pages
→ jack-portfolio
```

---

## 🎯 快速开始

1. 添加 Secret: `CLOUDFLARE_API_TOKEN` = `Sd0vKvLKAVaKIScuBEEsPb1d3tAmL8aR-wh4M6sf`
2. 访问: https://github.com/hhhh124hhhh/hhhh124hhhh.github.io/actions
3. 手动触发: `Deploy to Cloudflare Pages`
4. 等待 1-2 分钟
5. 访问: https://jack-portfolio.pages.dev

---

*Updated by Momo · 2026-02-03*
