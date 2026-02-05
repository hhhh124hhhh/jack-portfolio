# Stage 2 问题分析与解决方案

## 🚨 问题诊断

### 问题 1: 质量阈值过高

**现状**：
- 质量阈值：70（只转换 ≥70 的提示词）
- 收集结果：362 个提示词
- 达到阈值：0 个（0%）
- 已转换：0 个

**质量分布**：
- 高质量 (≥70)：0 (0%)
- 中等 (50-69)：11 (3%)
- 低质量 (<50)：351 (96%)
- 平均质量分数：29.5/100

**根本原因**：
- SearXNG 搜索到的提示词质量普遍较低
- 评估标准（Claude API）可能过于严格
- 或数据源不适合高质量提示词

---

## ✅ 解决方案

### 方案 1：降低质量阈值（推荐）

```bash
# 修改脚本中的 QUALITY_THRESHOLD
QUALITY_THRESHOLD="${QUALITY_THRESHOLD:-50}"  # 从 70 降到 50
```

**预期效果**：
- 中等质量提示词：11 个
- 转换概率：11/362 (3%)
- 发布概率：低（可能 1-2 个）

---

### 方案 2：改为使用其他高质量数据源

**推荐数据源**：
1. **GitHub**：搜索 "awesome prompts", "prompt engineering"
2. **HuggingFace**：搜索 "high quality prompts"
3. **ChatGPT Prompts**：优质提示词库

**查询示例**：
```bash
# 搜索高质量提示词
bash /root/clawd/scripts/integrated-prompt-workflow.sh \
  --query "best ChatGPT prompts" \
  --limit 100 \
  --quality-threshold 60
```

---

### 方案 3：提高数据源质量（SearXNG 配置优化）

**问题**：当前 SearXNG 配置可能返回低质量结果

**优化方案**：
```yaml
# SearXNG 配置调整
engines:
  - google: 3
  - bing: 2
  - duckduckgo: 2

# 搜索时间
time_range: 1m  # 最近 1 个月
language: en       # 限制为英语（可能质量更高）

# 过滤器
filters:
  - exclude_sites:
    - spam-sites.com
    - low-quality-content.com
```

---

### 方案 4：人工干预和手动转换

如果自动化无法产生高质量结果：

```bash
# 1. 手动查找优质提示词
# 从 ChatGPT Prompts, Reddit r/ChatGPT 等

# 2. 手动创建 SKILL.md
cd /root/clawd/skills/prompt-to-skill-converter
python3 main.py create --prompt "Your prompt here"

# 3. 打包和发布
python3 /root/clawd/skills/skill-creator/scripts/package_skill.py your-skill
clawdhub publish your-skill.skill --registry https://www.clawhub.ai/api
```

---

### 方案 5：调整评估标准（降低门槛）

**当前评估**：Claude API 4 个维度（创新性、实用性、清晰度、可复用性），满分 40

**调整方案**：
```python
# 降低总分要求
current_threshold = 30  # 75% of 40
adjusted_threshold = 20  # 50% of 40

# 或调整评分权重
weights = {
    "creativity": 0.2,    # 降低创新性权重
    "practicality": 0.4,  # 提高实用性权重
    "clarity": 0.25,       # 提高清晰度权重
    "reusability": 0.15   # 降低可复用性权重
}
```

---

## 🚀 立即行动

### 选项 1：降低阈值到 50

```bash
# 编辑脚本
vim /root/clawd/scripts/integrated-prompt-workflow.sh

# 修改第 25 行
QUALITY_THRESHOLD="${QUALITY_THRESHOLD:-50}"  # 改为 50

# 保存后手动执行一次
bash /root/clawd/scripts/integrated-prompt-workflow.sh
```

### 选项 2：使用更好的数据源

```bash
# 修改 config.yaml 只使用 GitHub
# 禁用 Reddit, Hacker News 等低质量源

vim /root/clawd/skills/x-prompt-hunter/config.yaml

# 只保留 github.enabled: true
```

### 选项 3：检查 prompt-to-skill-converter

```bash
# 检查转换器是否正常工作
cd /root/clawd/skills/prompt-to-skill-converter
python3 main.py help

# 检查依赖
pip install -r requirements.txt
```

---

## 📊 推荐配置

### 保守方案（阈值 60）
```bash
QUALITY_THRESHOLD="${QUALITY_THRESHOLD:-60}"
```

**预期**：
- 转换数量：5-10 个
- 质量：中等到高
- 风险：可能发布一些中等质量的内容

### 激进方案（阈值 40）
```bash
QUALITY_THRESHOLD="${QUALITY_THRESHOLD:-40}"
```

**预期**：
- 转换数量：30-50 个
- 质量：包含低质量
- 风险：可能降低市场声誉

---

## 🎯 最佳实践

### 1. 分阶段执行

```bash
# 第一阶段：低阈值测试（40）
bash /root/clawd/scripts/integrated-prompt-workflow.sh \
  --quality-threshold 40

# 第二阶段：审查结果
# 查看发布的 Skills
ls -la /root/clawd/skills/

# 第三阶段：调整阈值（根据反馈）
bash /root/clawd/scripts/integrated-prompt-workflow.sh \
  --quality-threshold 50
```

### 2. 人工审查机制

在发布前增加人工审查：
```bash
# 生成 SKILL.md 后暂不发布
python3 /root/clawd/skills/prompt-to-skill-converter/main.py \
  convert --input /root/clawd/data/prompts-enhanced-latest.jsonl \
  --output /root/clawd/skills/temp \
  --dry-run  # 不发布

# 手动审查
ls /root/clawd/skills/temp/

# 确认后再发布
python3 /root/clawd/skills/prompt-to-skill-converter/main.py \
  publish --dir /root/clawd/skills/temp
```

### 3. 持续优化

```bash
# 监控已发布 Skills 的用户反馈
# 根据反馈调整评估标准和阈值
```

---

## 💡 总结

| 方案 | 难度 | 效果 | 推荐度 |
|------|------|------|--------|
| 降低阈值到 50 | 低 | 中等 | ⭐⭐⭐ |
| 使用更好数据源 | 中 | 高 | ⭐⭐⭐⭐⭐ |
| 调整评估标准 | 高 | 高 | ⭐⭐⭐ |
| 人工干预 | 中 | 高 | ⭐⭐⭐⭐ |
| 降低阈值到 40 | 低 | 很高 | ⭐ |

**推荐**：先使用方案 1（降低阈值到 50），然后考虑方案 2（使用更好的数据源）。
