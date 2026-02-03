# 主页观看人数统计设置指南

## 📊 方案选择

### Google Analytics (推荐）
**优势**:
- ✅ 完全免费
- ✅ 功能强大（访问量、用户行为、地理位置、设备等）
- ✅ 实时数据
- ✅ 无需额外服务器
- ✅ 集成简单

**适合**: 个人网站、博客、作品集

---

## 🚀 快速设置（5 分钟）

### 步骤 1: 创建 Google Analytics 账户

1. 访问：https://analytics.google.com/
2. 登录你的 Google 账户
3. 点击"开始设置"
4. 填写账户信息：
   - **账户名称**: jack-portfolio
   - **数据共享设置**: 保持默认
5. 点击"下一步"
6. 填写媒体资源信息：
   - **媒体资源名称**: jack-portfolio
   - **报告时区**: China Standard Time (GMT+08:00)
   - **货币**: 人民币 (CNY ¥)
7. 点击"下一步"
8. 填写关于商家信息（可选）：
   - **行业类别**: 科技 / 技术
   - **商家规模**: 小型（1-10 名员工）
   - **使用目的**: 产生潜在客户、提升在线销量
9. 点击"创建"并接受条款

### 步骤 2: 获取测量 ID

创建完成后，你会看到：
```
测量 ID: G-XXXXXXXXXX
```

**复制这个 ID**，格式为 `G-` 开头。

### 步骤 3: 添加追踪代码到页面

#### 方法 1: 逐个页面添加（推荐）

在每个 HTML 文件的 `<head>` 标签中添加以下代码（**替换 G-XXXXXXXXXX**）：

```html
<!-- Google Analytics (GA4) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**添加位置**：`<head>` 标签的第一行

#### 方法 2: 批量替换（快速）

```bash
# 复制 analytics-header.html 中的代码
cp analytics-header.html temp.txt

# 在每个 HTML 文件的 <head> 后面插入
for file in */index.html index.html; do
  # 替换 G-XXXXXXXXXX 为你的实际 ID
  sed -i 's|G-XXXXXXXXXX|G-你的实际ID|g' temp.txt

  # 在 <head> 后插入代码
  sed -i '/<head>/r temp.txt' "$file"
done

rm temp.txt
```

### 步骤 4: 部署并验证

```bash
# 提交并推送
git add .
git commit -m "添加 Google Analytics 追踪"
git push origin master

# 等待 GitHub Pages 部署（约 1-2 分钟）
```

### 步骤 5: 验证追踪

1. 访问你的主页：https://hhhh124hhhh.github.io/jack-portfolio/
2. 在浏览器中打开开发者工具（F12）
3. 进入 Console 标签
4. 输入：`gtag` 或 `dataLayer`
5. 如果没有报错，说明追踪代码已加载

---

## 📈 查看统计数据

### 实时数据（推荐开始时查看）

1. 访问：https://analytics.google.com/
2. 选择账户和媒体资源
3. 左侧菜单 → 报告 → 实时
4. 你会看到：
   - 当前在线用户数
   - 实时页面浏览量
   - 实时事件

### 常用报告

#### 1. 用户概览
- **路径**: 报告 → 生命周期 → 获取
- **数据**:
  - 用户数
  - 新用户
  - 会话数
  - 参与度

#### 2. 流量获取
- **路径**: 报告 → 生命周期 → 获取
- **数据**:
  - 流量来源（直接、搜索、社交媒体、引用）
  - 流量渠道
  - 带来的用户数

#### 3. 内容页面
- **路径**: 报告 → 参与 → 页面和屏幕
- **数据**:
  - 各页面浏览量
  - 平均参与时间
  - 跳出率

#### 4. 受众特征
- **路径**: 报告 → 用户 → 用户属性
- **数据**:
  - 地理位置
  - 设备类型
  - 浏览器
  - 操作系统

---

## 🔧 高级设置

### 自定义事件

你可以追踪特定事件，例如：

```html
<!-- 追踪"关于我"点击 -->
<a href="#about" onclick="gtag('event', 'about_click', {
  'page_title': '主页',
  'page_location': window.location.href
});">关于我</a>

<!-- 追踪项目链接点击 -->
<a href="https://github.com/..." onclick="gtag('event', 'project_link', {
  'project_name': '成就系统',
  'link_type': 'github'
});">项目</a>
```

### 排除内部流量

避免自己的访问影响统计数据：

1. 访问：https://analytics.google.com/
2. 左侧菜单 → 管理
3. 媒体资源 → 数据流 → 选择数据流
4. 点击"配置标记设置"
5. 启用"排除内部流量"
6. 选择"排除基于 IP 地址的流量"
7. 输入你的 IP 地址（或使用 VPN 固定 IP）

### 目标设置

设置转化目标，追踪特定行为：

1. 访问：https://analytics.google.com/
2. 左侧菜单 → 管理
3. 媒体资源 → 目标
4. 点击"新目标"
5. 设置目标类型：
   - 目的地：访问特定页面
   - 时长：停留超过 X 分钟
   - 每会话浏览页数：浏览超过 X 页
   - 事件：触发特定事件

---

## 📱 移动端查看

### Google Analytics App
- **iOS**: https://apps.apple.com/app/google-analytics/id9356266
- **Android**: https://play.google.com/store/apps/details?id=com.google.android.apps.analytics

### 功能
- 实时数据
- 用户概览
- 流量获取
- 内容报告

---

## 🎯 数据隐私

Google Analytics 默认匿名化 IP 地址，符合 GDPR 要求。

如果你想进一步提升隐私：

### 启用 IP 匿名化

```html
<script>
  gtag('config', 'G-XXXXXXXXXX', {
    'anonymize_ip': true,
    'cookie_flags': 'SameSite=None;Secure'
  });
</script>
```

---

## 📊 替代方案（如果不想用 Google Analytics）

### 1. Cloudflare Web Analytics
- **优势**: 完全免费、无 Cookie、隐私友好
- **设置**: 在 Cloudflare 添加网站即可
- **缺点**: 需要使用 Cloudflare

### 2. Plausible Analytics
- **优势**: 开源、隐私友好、简洁
- **缺点**: 自托管需要服务器，托管版本付费
- **价格**: $9/月起

### 3. Umami
- **优势**: 开源、自托管、隐私友好
- **缺点**: 需要自托管
- **价格**: 免费（自托管）

---

## ❓ 常见问题

### Q: 数据多久更新？
A: 实时数据是实时的，常规报告延迟 24-48 小时。

### Q: 如何删除我的历史数据？
A: Google Analytics 提供数据删除请求，但需要时间处理。

### Q: 可以追踪 GitHub Pages 吗？
A: 完全可以，这是最常见的使用场景。

### Q: 数据准确吗？
A: 非常准确，已被 Google 使用多年。

### Q: 会影响页面性能吗？
A: 影响极小，异步加载，不会阻塞页面渲染。

---

## 🚀 下一步

1. **设置 Google Analytics**（5 分钟）
2. **添加追踪代码到所有页面**
3. **验证追踪是否工作**
4. **查看实时数据**
5. **定期查看报告**（每周/每月）

---

*Created by Momo · 2026-02-03*
