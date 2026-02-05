#!/bin/bash
# 成就阶段三推进脚本 - 建立连续使用习惯
# 目标：解锁连续使用成就

echo "📍 阶段三：建立连续使用习惯"

cd /root/clawd/projects/achievement-system

# 读取用户配置
python3 << 'EOF'
import json
from pathlib import Path
from datetime import datetime

data_dir = Path("/root/clawd/projects/data")
user_profile_file = data_dir / "user_profile.json"

# 创建用户配置（如果不存在）
if not user_profile_file.exists():
    profile = {
        "streak": {
            "current": 0,
            "longest": 0,
            "last_active_date": None
        }
    }
    with open(user_profile_file, 'w') as f:
        json.dump(profile, f, indent=2)
    print("✅ 创建用户配置文件")
else:
    print("✅ 用户配置文件已存在")

# 读取当前配置
with open(user_profile_file, 'r') as f:
    profile = json.load(f)

# 更新连续使用天数
today = datetime.now().strftime('%Y-%m-%d')
last_date = profile['streak']['last_active_date']

if last_date != today:
    # 今天是新的一天
    profile['streak']['current'] += 1
    profile['streak']['last_active_date'] = today

    # 更新最长连续天数
    if profile['streak']['current'] > profile['streak']['longest']:
        profile['streak']['longest'] = profile['streak']['current']

    # 保存
    with open(user_profile_file, 'w') as f:
        json.dump(profile, f, indent=2)

    print(f"📅 新的一天！连续使用: {profile['streak']['current']} 天")
else:
    print(f"📅 今天已经记录过了")
    print(f"📊 当前连续使用: {profile['streak']['current']} 天")

EOF

# 检查成就
echo ""
cd /root/clawd/scripts
echo "🏆 检查成就..."
python3 achievement-integrator.py check > /dev/null 2>&1

# 显示状态
echo ""
echo "📊 当前状态:"
python3 achievement-integrator.py status

echo ""
echo "✅ 阶段三完成！"
