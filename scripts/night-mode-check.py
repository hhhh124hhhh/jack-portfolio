#!/usr/bin/env python3
"""
深夜模式检查脚本
判断当前时间是否在允许通知的时段内（07:00-23:00）
"""

import sys
import json
import os
from datetime import datetime, timezone, timedelta

# 配置
NIGHT_START = 23  # 晚 23:00 开始深夜模式
NIGHT_END = 7     # 早上 07:00 结束深夜模式
TIMEZONE_OFFSET = 8  # Asia/Shanghai (UTC+8)
STATE_FILE = "/root/clawd/memory/night-mode-state.json"


def get_current_time():
    """获取当前时间（Asia/Shanghai 时区）"""
    utc_now = datetime.now(timezone.utc)
    shanghai_tz = timezone(timedelta(hours=TIMEZONE_OFFSET))
    return utc_now.astimezone(shanghai_tz)


def is_night_mode():
    """判断当前是否在深夜模式"""
    now = get_current_time()
    hour = now.hour
    return hour >= NIGHT_START or hour < NIGHT_END


def should_notify(allow_urgent=False):
    """
    判断当前时间是否可以发送通知

    Args:
        allow_urgent: 是否允许紧急通知（即使深夜模式也允许）

    Returns:
        (can_notify: bool, reason: str, current_time: str)
    """
    now = get_current_time()
    is_night = is_night_mode()

    if not is_night:
        return True, "白天时段，允许通知", now.strftime("%Y-%m-%d %H:%M:%S")
    elif allow_urgent:
        return True, "深夜模式，但允许紧急通知", now.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return False, f"深夜模式（{NIGHT_END}:00-{NIGHT_START}:00），暂不通知", now.strftime("%Y-%m-%d %H:%M:%S")


def save_state(can_notify, reason):
    """保存当前状态"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

    state = {
        "checked_at": get_current_time().isoformat(),
        "can_notify": can_notify,
        "reason": reason,
        "night_mode_start": NIGHT_START,
        "night_mode_end": NIGHT_END,
        "timezone": f"UTC+{TIMEZONE_OFFSET}"
    }

    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def load_state():
    """加载状态"""
    if not os.path.exists(STATE_FILE):
        return None

    with open(STATE_FILE, 'r') as f:
        return json.load(f)


def main():
    if len(sys.argv) < 2:
        # 默认检查
        can_notify, reason, current_time = should_notify()
        save_state(can_notify, reason)
        print(f"[{current_time}] {reason}")
        return 0 if can_notify else 1

    command = sys.argv[1].lower()

    if command == "check":
        # 检查是否可以通知
        allow_urgent = "--urgent" in sys.argv or "-u" in sys.argv
        can_notify, reason, current_time = should_notify(allow_urgent)
        save_state(can_notify, reason)
        print(f"[{current_time}] {reason}")
        return 0 if can_notify else 1

    elif command == "status":
        # 显示详细状态
        now = get_current_time()
        is_night = is_night_mode()
        state = load_state()

        print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"时区: UTC+{TIMEZONE_OFFSET}")
        print(f"深夜模式: {'开启' if is_night else '关闭'}")
        print(f"安静时段: {NIGHT_END}:00 - {NIGHT_START}:00")
        print(f"允许通知: {'是' if not is_night else '否'}")

        if state:
            print(f"\n上次检查: {state.get('checked_at', 'N/A')}")
            print(f"上次结果: {state.get('reason', 'N/A')}")

        return 0

    elif command == "wait":
        # 等待到允许通知的时间
        now = get_current_time()
        is_night = is_night_mode()

        if not is_night:
            print("当前已是白天时段，无需等待")
            return 0

        # 计算到早上 7:00 还有多少秒
        tomorrow = now.replace(hour=NIGHT_END, minute=0, second=0, microsecond=0)
        if tomorrow <= now:
            tomorrow += timedelta(days=1)

        wait_seconds = (tomorrow - now).total_seconds()
        wait_minutes = int(wait_seconds / 60)

        print(f"当前为深夜模式，需等待 {wait_minutes} 分钟到 {tomorrow.strftime('%Y-%m-%d %H:%M')}")
        return 2

    else:
        print(f"Usage: {sys.argv[0]} [check|status|wait] [--urgent]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
