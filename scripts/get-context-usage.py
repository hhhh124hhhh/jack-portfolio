#!/usr/bin/env python3
"""
获取当前上下文使用率
作者：Momo
创建日期：2026-02-05

返回：当前上下文使用百分比（整数）
"""

import subprocess
import json
import re

def get_context_usage():
    """
    获取上下文使用率
    通过解析 session_status 输出
    """
    try:
        # 运行 session_status 命令
        result = subprocess.run(
            ['clawdbot', 'status'],
            capture_output=True,
            text=True,
            timeout=10
        )

        # 解析输出，查找上下文使用率
        # 格式类似：Context: 73k/205k (36%)
        match = re.search(r'Context:\s+\d+k/\d+k\s+\((\d+)%\)', result.stdout)

        if match:
            usage = int(match.group(1))
            return usage
        else:
            # 如果找不到，返回 0
            return 0

    except Exception as e:
        # 如果出错，返回 0
        return 0

if __name__ == '__main__':
    usage = get_context_usage()
    print(usage)
