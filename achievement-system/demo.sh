#!/bin/bash
# Achievement System Demo Script

echo "==================================="
echo "   成就系统 CLI 工具演示"
echo "==================================="
echo ""

echo "1. 初始化系统"
echo "---"
./ach init
echo ""

echo "2. 查看所有成就"
echo "---"
./ach list
echo ""

echo "3. 查看当前进度"
echo "---"
./ach status
echo ""

echo "4. 查看统计信息"
echo "---"
./ach stats
echo ""

echo "5. 解锁 Hello World 成就"
echo "---"
./ach add hello_world 1
echo ""

echo "6. 解锁首次提交成就"
echo "---"
./ach add first_commit 1
echo ""

echo "7. 再次查看进度"
echo "---"
./ach status
echo ""

echo "8. 再次查看统计信息"
echo "---"
./ach stats
echo ""

echo "9. 查看成就列表（显示已解锁状态）"
echo "---"
./ach list
echo ""

echo "==================================="
echo "   演示完成！"
echo "==================================="
