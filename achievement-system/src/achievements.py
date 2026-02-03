"""成就管理模块 - 负责成就解锁、条件检查和进度更新"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from storage import load_achievements, save_progress, load_progress, get_achievement_by_id


class AchievementManager:
    """成就管理器"""

    def __init__(self):
        self.achievements = load_achievements()
        self.progress = load_progress()

    def update_progress(self, achievement_id: str, amount: int = 1) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        更新成就进度

        Args:
            achievement_id: 成就 ID
            amount: 增加的进度数量

        Returns:
            (success, message, unlocked_achievement)
        """
        achievement = get_achievement_by_id(achievement_id)
        if not achievement:
            return False, f"成就 '{achievement_id}' 不存在", None

        # 如果已解锁，不再更新进度
        if achievement_id in self.progress.get("unlocked_achievements", []):
            return False, f"成就 '{achievement.get('name')}' 已解锁", None

        # 初始化进度
        if "progress" not in self.progress:
            self.progress["progress"] = {}

        if achievement_id not in self.progress["progress"]:
            # 从 requirements 中获取目标值
            requirements = achievement.get("requirements", {})
            target = requirements.get("count", 1) if requirements else 1
            self.progress["progress"][achievement_id] = {
                "current": 0,
                "target": target
            }

        # 更新进度
        current = self.progress["progress"][achievement_id]["current"]
        target = self.progress["progress"][achievement_id]["target"]
        new_current = min(current + amount, target)

        self.progress["progress"][achievement_id]["current"] = new_current

        # 检查是否达成目标
        if new_current >= target:
            unlocked = self.unlock_achievement(achievement_id)
            if unlocked:
                return True, f"🎉 恭喜！成就 '{achievement.get('name')}' 已解锁！", achievement
            return False, f"进度已更新：{new_current}/{target}，但解锁失败", None
        else:
            self._save_progress()
            return True, f"进度已更新：{new_current}/{target}", None

    def unlock_achievement(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        """
        解锁成就

        Args:
            achievement_id: 成就 ID

        Returns:
            解锁的成就信息，失败返回 None
        """
        achievement = get_achievement_by_id(achievement_id)
        if not achievement:
            return None

        # 检查是否已解锁
        if achievement_id in self.progress.get("unlocked_achievements", []):
            return None

        # 添加到已解锁列表
        if "unlocked_achievements" not in self.progress:
            self.progress["unlocked_achievements"] = []

        self.progress["unlocked_achievements"].append(achievement_id)

        # 更新统计数据
        points = achievement.get("points", 0)
        self.progress["statistics"]["total_points"] += points
        self.progress["statistics"]["total_unlocked"] = len(self.progress["unlocked_achievements"])
        self.progress["statistics"]["last_updated"] = datetime.now().isoformat() + "Z"

        self._save_progress()
        return achievement

    def check_achievement_conditions(self, achievement_id: str) -> bool:
        """
        检查成就是否满足解锁条件

        Args:
            achievement_id: 成就 ID

        Returns:
            是否满足条件
        """
        achievement = get_achievement_by_id(achievement_id)
        if not achievement:
            return False

        # 如果已解锁，返回 True
        if achievement_id in self.progress.get("unlocked_achievements", []):
            return True

        # 检查是否有进度要求
        requirements = achievement.get("requirements", {})
        if requirements:
            if "progress" in self.progress and achievement_id in self.progress["progress"]:
                current = self.progress["progress"][achievement_id]["current"]
                target = self.progress["progress"][achievement_id]["target"]
                return current >= target
            return False

        # 没有额外要求，可以直接解锁
        return True

    def get_all_achievements(self) -> List[Dict[str, Any]]:
        """获取所有成就列表"""
        return self.achievements.get("achievements", [])

    def get_unlocked_achievements(self) -> List[Dict[str, Any]]:
        """获取已解锁的成就列表"""
        unlocked_ids = self.progress.get("unlocked_achievements", [])
        all_achievements = self.get_all_achievements()
        return [a for a in all_achievements if a.get("id") in unlocked_ids]

    def get_locked_achievements(self) -> List[Dict[str, Any]]:
        """获取未解锁的成就列表"""
        unlocked_ids = set(self.progress.get("unlocked_achievements", []))
        all_achievements = self.get_all_achievements()
        return [a for a in all_achievements if a.get("id") not in unlocked_ids]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_achievements = len(self.get_all_achievements())
        unlocked = len(self.get_unlocked_achievements())
        locked = total_achievements - unlocked
        points = self.progress.get("statistics", {}).get("total_points", 0)

        return {
            "total_achievements": total_achievements,
            "unlocked": unlocked,
            "locked": locked,
            "completion_rate": (unlocked / total_achievements * 100) if total_achievements > 0 else 0,
            "total_points": points
        }

    def _save_progress(self) -> bool:
        """保存进度"""
        return save_progress(self.progress)

    def get_progress_for_achievement(self, achievement_id: str) -> Optional[Dict[str, int]]:
        """获取特定成就的进度"""
        if "progress" not in self.progress:
            return None
        return self.progress["progress"].get(achievement_id)
