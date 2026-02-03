"""进度追踪模块 - 负责显示和格式化进度信息"""

from typing import Dict, Any, List
from achievements import AchievementManager
from storage import load_progress


class ProgressTracker:
    """进度追踪器"""

    def __init__(self, manager: AchievementManager = None):
        self.manager = manager or AchievementManager()

    def display_status(self) -> List[Dict[str, Any]]:
        """
        显示当前进度状态

        Returns:
            包含成就进度信息的列表
        """
        all_achievements = self.manager.get_all_achievements()
        progress_data = load_progress()

        result = []
        for achievement in all_achievements:
            achievement_id = achievement.get("id")
            is_unlocked = achievement_id in progress_data.get("unlocked_achievements", [])

            info = {
                "id": achievement_id,
                "name": achievement.get("name"),
                "icon": achievement.get("icon"),
                "is_unlocked": is_unlocked,
                "points": achievement.get("points"),
                "category": achievement.get("category")
            }

            # 添加进度信息
            if not is_unlocked:
                progress = self.manager.get_progress_for_achievement(achievement_id)
                if progress:
                    info["current"] = progress["current"]
                    info["target"] = progress["target"]
                    info["percentage"] = (progress["current"] / progress["target"] * 100) if progress["target"] > 0 else 0

            result.append(info)

        return result

    def display_statistics(self) -> Dict[str, Any]:
        """
        显示统计信息

        Returns:
            统计数据字典
        """
        return self.manager.get_statistics()

    def format_progress_bar(self, current: int, total: int, width: int = 20) -> str:
        """
        格式化进度条

        Args:
            current: 当前进度
            total: 总进度
            width: 进度条宽度

        Returns:
            格式化的进度条字符串
        """
        if total == 0:
            return "█" * width

        filled = int((current / total) * width)
        empty = width - filled
        return "█" * filled + "░" * empty

    def get_achievements_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        按分类获取成就

        Args:
            category: 成就分类

        Returns:
            该分类下的成就列表
        """
        all_achievements = self.manager.get_all_achievements()
        return [a for a in all_achievements if a.get("category") == category]

    def get_categories(self) -> List[str]:
        """获取所有成就分类"""
        all_achievements = self.manager.get_all_achievements()
        categories = set(a.get("category", "default") for a in all_achievements)
        return sorted(list(categories))
