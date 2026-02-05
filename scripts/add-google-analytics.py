#!/usr/bin/env python3
"""
批量添加 Google Analytics 追踪代码
"""

import os
import re
from pathlib import Path

# 配置
MEASUREMENT_ID = "G-E25S3PK9M6"  # jack 的 Google Analytics 测量 ID
GA_SCRIPT = f'''<!-- Google Analytics (GA4) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', '{MEASUREMENT_ID}');
</script>
'''

PORTFOLIO_DIR = Path("/root/clawd/jack-portfolio")


def add_analytics_to_file(file_path):
    """添加 Google Analytics 到 HTML 文件"""

    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已有 GA 代码
    if 'gtag(' in content or 'googletagmanager' in content:
        print(f"  ⏭️  跳过（已有 GA 代码）")
        return False

    # 在 <head> 后插入 GA 代码
    if '<head>' in content:
        content = content.replace('<head>', f'<head>\n{GA_SCRIPT}')

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✅ 已添加 GA 代码")
        return True
    else:
        print(f"  ❌ 没有找到 <head> 标签")
        return False


def main():
    """主函数"""
    print("📊 批量添加 Google Analytics 追踪代码")
    print(f"测量 ID: {MEASUREMENT_ID}")
    print(f"目录: {PORTFOLIO_DIR}")
    print()

    # 查找所有 HTML 文件
    html_files = list(PORTFOLIO_DIR.glob("index.html")) + \
                list(PORTFOLIO_DIR.glob("*/index.html"))

    if not html_files:
        print("❌ 没有找到 HTML 文件")
        return

    print(f"找到 {len(html_files)} 个 HTML 文件")
    print()

    # 处理每个文件
    success_count = 0
    for html_file in html_files:
        print(f"处理: {html_file.relative_to(PORTFOLIO_DIR)}")
        if add_analytics_to_file(html_file):
            success_count += 1
        print()

    print(f"✅ 完成！已添加 GA 代码到 {success_count}/{len(html_files)} 个文件")
    print()
    print("📝 下一步：")
    print("1. 修改脚本中的 MEASUREMENT_ID 为你的实际 ID")
    print("2. 重新运行脚本：python3 /root/clawd/scripts/add-google-analytics.py")
    print("3. 提交并推送：git add . && git commit && git push")


if __name__ == "__main__":
    main()
