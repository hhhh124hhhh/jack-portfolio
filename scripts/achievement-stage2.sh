#!/bin/bash
# 成就阶段二推进脚本 - 积累使用量
# 目标：解锁里程碑成就

echo "📍 阶段二：积累使用量"

cd /root/clawd/scripts

# 技能爱好者：累计使用技能 50 次（当前 15，需要 35）
echo ""
echo "⚡ 推进到 50 次技能使用..."
for i in {1..35}; do
    python3 achievement-integrator.py skill coding-agent > /dev/null 2>&1
done

# 工具达人：累计使用工具 100 次（当前 37，需要 63）
echo ""
echo "🛠️  推进到 100 次工具使用..."
for i in {1..63}; do
    python3 achievement-integrator.py tool read > /dev/null 2>&1
done

# 话痨：累计处理消息 100 条（当前 65，需要 35）
echo ""
echo "💬 推进到 100 条消息..."
python3 achievement-integrator.py message 35 --platform slack > /dev/null 2>&1

# 检查成就
echo ""
echo "🏆 检查成就..."
python3 achievement-integrator.py check > /dev/null 2>&1

# 显示状态
echo ""
echo "📊 当前状态:"
python3 achievement-integrator.py status

echo ""
echo "✅ 阶段二完成！"
