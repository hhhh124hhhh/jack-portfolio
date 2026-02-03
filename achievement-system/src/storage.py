"""数据存储模块 - 负责加载和保存成就配置及用户进度"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# 获取数据目录路径
DATA_DIR = Path(__file__).parent.parent / "data"
ACHIEVEMENTS_FILE = DATA_DIR / "achievements.json"
PROGRESS_FILE = DATA_DIR / "progress.json"


def load_achievements() -> Dict[str, Any]:
    """加载成就配置文件"""
    if not ACHIEVEMENTS_FILE.exists():
        return {"achievements": []}

    try:
        with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"加载成就配置失败: {e}")
        return {"achievements": []}


def save_achievements(data: Dict[str, Any]) -> bool:
    """保存成就配置文件"""
    try:
        ACHIEVEMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ACHIEVEMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"保存成就配置失败: {e}")
        return False


def load_progress() -> Dict[str, Any]:
    """加载用户进度文件"""
    if not PROGRESS_FILE.exists():
        return {
            "user_id": "default",
            "unlocked_achievements": [],
            "progress": {},
            "statistics": {
                "total_points": 0,
                "total_unlocked": 0,
                "last_updated": None
            }
        }

    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"加载用户进度失败: {e}")
        return {
            "user_id": "default",
            "unlocked_achievements": [],
            "progress": {},
            "statistics": {
                "total_points": 0,
                "total_unlocked": 0,
                "last_updated": None
            }
        }


def save_progress(progress: Dict[str, Any]) -> bool:
    """保存用户进度文件"""
    try:
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"保存用户进度失败: {e}")
        return False


def get_achievement_by_id(achievement_id: str) -> Optional[Dict[str, Any]]:
    """根据 ID 获取成就信息"""
    data = load_achievements()
    for achievement in data.get("achievements", []):
        if achievement.get("id") == achievement_id:
            return achievement
    return None
