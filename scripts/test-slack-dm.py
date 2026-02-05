#!/usr/bin/env python3
"""快速测试 Slack 私聊消息发送"""

import subprocess

# 你的 Slack 私聊 Channel ID（D 开头）
SLACK_CHANNEL_ID = "D0AB0J4QLAH"

def main():
    message = """🧪 Slack 私聊测试成功！

如果你看到这条消息，说明：
✅ Slack 私聊配置正确
✅ 用户 ID 正确
✅ 消息发送功能正常
✅ 不再需要群聊频道

从现在开始，所有通知都会发送到这个私聊！
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
        print("\n✅ 私聊测试成功！")
    else:
        print(f"\n❌ 测试失败，返回码: {result.returncode}")

if __name__ == "__main__":
    main()
