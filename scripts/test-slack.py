#!/usr/bin/env python3
"""快速测试 Slack 消息发送"""

import subprocess

SLACK_CHANNEL_ID = "C0ABSK92X4G"

def main():
    message = """🧪 Slack 消息测试成功！

如果你看到这条消息，说明：
✅ Clawdbot Slack 配置正确
✅ 频道 ID 正确
✅ 消息发送功能正常

下一步：运行完整的收集脚本
`python3 /root/clawd/scripts/collect-and-slack.py`
"""

    result = subprocess.run(
        [
            "clawdbot", "message", "send",
            "--channel", "slack",
            "--target", SLACK_CHANNEL_ID,
            "--message", message
        ],
        capture_output=True,
        text=True,
        timeout=30
    )

    print(result.stdout)
    if result.stderr:
        print("Error:", result.stderr)

    if result.returncode == 0:
        print("\n✅ 测试成功！")
    else:
        print(f"\n❌ 测试失败，返回码: {result.returncode}")

if __name__ == "__main__":
    main()
