#!/usr/bin/env python3
"""
安全通知包装器
在发送通知前检查深夜模式
"""

import sys
import subprocess
from night_mode_check import should_notify, get_current_time


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: safe-notify.py <command> [args...]")
        print("在执行命令前检查深夜模式，仅在允许通知时执行")
        return 1

    # 检查是否允许通知
    can_notify, reason, current_time = should_notify()

    if not can_notify:
        print(f"[{current_time}] {reason}")
        print("跳过通知任务")
        return 0  # 返回 0 表示成功跳过，不会触发错误

    # 执行命令
    command = sys.argv[1:]
    print(f"[{current_time}] 执行通知任务: {' '.join(command)}")

    try:
        result = subprocess.run(command, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        return e.returncode
    except Exception as e:
        print(f"执行出错: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
