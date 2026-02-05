#!/usr/bin/env python3
"""
成就系统自动集成脚本

用于在日常使用中自动记录活动到成就系统
"""

import sys
import os
from pathlib import Path

# 添加成就系统路径
sys.path.insert(0, str(Path(__file__).parent.parent / "projects" / "achievement-system" / "src"))

from data_store import DataStore
from datetime import datetime

class AchievementIntegrator:
    """成就系统集成器"""

    def __init__(self):
        """初始化集成器"""
        self.data_store = DataStore()
        self.today = datetime.now().strftime('%Y-%m-%d')

    def track_tool_usage(self, tool_name: str, success: bool = True):
        """记录工具使用"""
        print(f"📊 记录工具使用: {tool_name} (成功: {success})")

        # 获取当前活动
        activities = self.data_store.get_activities()
        if self.today not in activities:
            activities[self.today] = {}

        if 'tools' not in activities[self.today]:
            activities[self.today]['tools'] = {}

        # 更新工具使用统计
        if tool_name not in activities[self.today]['tools']:
            activities[self.today]['tools'][tool_name] = {
                'count': 0,
                'success': 0,
                'failure': 0
            }

        activities[self.today]['tools'][tool_name]['count'] += 1
        if success:
            activities[self.today]['tools'][tool_name]['success'] += 1
        else:
            activities[self.today]['tools'][tool_name]['failure'] += 1

        # 保存
        self.data_store.save_activity(self.today, activities[self.today])

        return True

    def track_skill_usage(self, skill_name: str):
        """记录技能使用"""
        print(f"⚡ 记录技能使用: {skill_name}")

        # 获取当前活动
        activities = self.data_store.get_activities()
        if self.today not in activities:
            activities[self.today] = {}

        if 'skills' not in activities[self.today]:
            activities[self.today]['skills'] = {}

        # 更新技能使用统计
        if skill_name not in activities[self.today]['skills']:
            activities[self.today]['skills'][skill_name] = 0

        activities[self.today]['skills'][skill_name] += 1

        # 保存
        self.data_store.save_activity(self.today, activities[self.today])

        return True

    def track_message(self, count: int = 1, platform: str = "slack"):
        """记录消息处理"""
        print(f"💬 记录消息处理: {count} 条 ({platform})")

        # 获取当前活动
        activities = self.data_store.get_activities()
        if self.today not in activities:
            activities[self.today] = {}

        if 'messages' not in activities[self.today]:
            activities[self.today]['messages'] = {}

        # 更新消息统计
        if platform not in activities[self.today]['messages']:
            activities[self.today]['messages'][platform] = 0

        activities[self.today]['messages'][platform] += count

        # 保存
        self.data_store.save_activity(self.today, activities[self.today])

        return True

    def track_workflow(self, workflow_name: str):
        """记录工作流完成"""
        print(f"🔄 记录工作流: {workflow_name}")

        # 使用工作流追踪器
        from workflow_tracker import WorkflowTracker
        workflow_tracker = WorkflowTracker()
        workflow_tracker.complete_workflow(f"{self.today}_{workflow_name}")

        return True

    def check_achievements(self):
        """检查并更新成就"""
        print("🏆 检查成就...")

        from achievement_engine import AchievementEngine
        achievement_engine = AchievementEngine()

        # 获取上下文
        context = self._get_context()

        # 检查成就
        new_unlocks = achievement_engine.check_achievements(context)

        if new_unlocks:
            print(f"\n🎉 解锁了 {len(new_unlocks)} 个新成就:")
            for achievement in new_unlocks:
                print(f"  {achievement['icon']} {achievement['name']}: {achievement['description']}")
        else:
            print("✅ 没有新成就解锁")

        return new_unlocks

    def _get_context(self):
        """获取成就检查上下文"""
        # 获取所有活动
        activities = self.data_store.get_activities()
        achievements = self.data_store.get_achievements()
        user_profile = self.data_store.get_user_profile()

        # 计算总计
        total_tools = 0
        total_success = 0
        total_failure = 0
        tool_types = set()

        total_skills = 0
        skill_types = set()

        total_messages = 0

        for date, day_activities in activities.items():
            # 工具统计
            if 'tools' in day_activities:
                for tool, stats in day_activities['tools'].items():
                    total_tools += stats['count']
                    total_success += stats['success']
                    total_failure += stats['failure']
                    tool_types.add(tool)

            # 技能统计
            if 'skills' in day_activities:
                for skill, count in day_activities['skills'].items():
                    total_skills += count
                    skill_types.add(skill)

            # 消息统计
            if 'messages' in day_activities:
                for platform, count in day_activities['messages'].items():
                    total_messages += count

        # 成就统计
        unlocked_count = sum(1 for a in achievements.values() if a.get('unlocked', False))

        # 计算连续使用天数
        streak = user_profile.get('streak', {}).get('current', 0)

        return {
            'total_tools': total_tools,
            'total_success': total_success,
            'total_failure': total_failure,
            'tool_types': len(tool_types),
            'total_skills': total_skills,
            'skill_types': len(skill_types),
            'total_messages': total_messages,
            'unlocked_count': unlocked_count,
            'total_achievements': len(achievements),
            'streak': streak
        }

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="成就系统集成器")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 记录工具使用
    tool_parser = subparsers.add_parser("tool", help="记录工具使用")
    tool_parser.add_argument("name", help="工具名称")
    tool_parser.add_argument("--success", "-s", action="store_true", default=True, help="是否成功")

    # 记录技能使用
    skill_parser = subparsers.add_parser("skill", help="记录技能使用")
    skill_parser.add_argument("name", help="技能名称")

    # 记录消息
    message_parser = subparsers.add_parser("message", help="记录消息处理")
    message_parser.add_argument("count", type=int, default=1, help="消息数量")
    message_parser.add_argument("--platform", "-p", default="slack", help="平台名称")

    # 记录工作流
    workflow_parser = subparsers.add_parser("workflow", help="记录工作流完成")
    workflow_parser.add_argument("name", help="工作流名称")

    # 检查成就
    check_parser = subparsers.add_parser("check", help="检查成就")

    # 显示状态
    status_parser = subparsers.add_parser("status", help="显示状态")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # 初始化集成器
    integrator = AchievementIntegrator()

    try:
        if args.command == "tool":
            integrator.track_tool_usage(args.name, args.success)
            integrator.check_achievements()

        elif args.command == "skill":
            integrator.track_skill_usage(args.name)
            integrator.check_achievements()

        elif args.command == "message":
            integrator.track_message(args.count, args.platform)
            integrator.check_achievements()

        elif args.command == "workflow":
            integrator.track_workflow(args.name)
            integrator.check_achievements()

        elif args.command == "check":
            new_unlocks = integrator.check_achievements()
            return len(new_unlocks)

        elif args.command == "status":
            context = integrator._get_context()
            print("\n📊 当前状态:")
            print(f"  工具使用: {context['total_tools']} 次（{len(set())} 种）")
            print(f"  成功率: {context['total_success']}/{context['total_tools']} ({context['total_success']/context['total_tools']*100:.1f}%)")
            print(f"  技能使用: {context['total_skills']} 次（{context['skill_types']} 种）")
            print(f"  消息处理: {context['total_messages']} 条")
            print(f"  成就解锁: {context['unlocked_count']}/{context['total_achievements']} ({context['unlocked_count']/context['total_achievements']*100:.1f}%)")
            print(f"  连续使用: {context['streak']} 天")

        return 0

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
