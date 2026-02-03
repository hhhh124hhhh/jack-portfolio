"""成就系统统计模块 - 自动追踪工具使用、任务完成等数据"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# 统计数据目录
XDG_DATA_HOME = Path(os.environ.get('XDG_DATA_HOME', '~/.local/share')).expanduser()
STATS_DIR = XDG_DATA_HOME / "achievement-system"
STATS_FILE = STATS_DIR / "stats.json"


class AchievementStats:
    """成就统计数据追踪器"""

    def __init__(self):
        self.stats = self._load_stats()

    def _load_stats(self) -> Dict[str, Any]:
        """加载统计数据"""
        if not STATS_FILE.exists():
            return self._get_default_stats()

        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self._get_default_stats()

    def _get_default_stats(self) -> Dict[str, Any]:
        """获取默认统计数据"""
        return {
            "execution": {
                "total_tool_calls": 0,
                "total_api_calls": 0,
                "unique_tools_used": 0,
                "tools_used": set()
            },
            "intelligence": {
                "total_memories": 0,
                "total_searches": 0,
                "total_code_lines": 0,
                "total_bugs_fixed": 0
            },
            "collaboration": {
                "total_tasks_completed": 0,
                "continuous_work_hours": 0,
                "max_simultaneous_subagents": 0,
                "total_heartbeat_responses": 0
            },
            "project": {
                "projects_started": 0,
                "projects_deployed": 0,
                "total_git_commits": 0,
                "total_documents": 0
            },
            "history": {
                "first_task_completed": None,
                "last_updated": None
            }
        }

    def save(self) -> bool:
        """保存统计数据"""
        try:
            STATS_DIR.mkdir(parents=True, exist_ok=True)

            # 将 set 转换为 list 以便 JSON 序列化
            stats_to_save = self.stats.copy()
            stats_to_save["execution"]["tools_used"] = list(self.stats["execution"]["tools_used"])

            stats_to_save["history"]["last_updated"] = None

            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(stats_to_save, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"保存统计数据失败: {e}")
            return False

    # 执行类统计
    def increment_tool_calls(self, tool_name: str = None) -> None:
        """增加工具调用次数"""
        self.stats["execution"]["total_tool_calls"] += 1
        if tool_name and tool_name not in self.stats["execution"]["tools_used"]:
            self.stats["execution"]["tools_used"].add(tool_name)
            self.stats["execution"]["unique_tools_used"] = len(self.stats["execution"]["tools_used"])
        self.save()

    def increment_api_calls(self) -> None:
        """增加 API 调用次数"""
        self.stats["execution"]["total_api_calls"] += 1
        self.save()

    # 智力类统计
    def increment_memories(self) -> None:
        """增加记忆条数"""
        self.stats["intelligence"]["total_memories"] += 1
        self.save()

    def increment_searches(self) -> None:
        """增加搜索次数"""
        self.stats["intelligence"]["total_searches"] += 1
        self.save()

    def add_code_lines(self, lines: int) -> None:
        """增加代码行数"""
        self.stats["intelligence"]["total_code_lines"] += lines
        self.save()

    def increment_bugs_fixed(self) -> None:
        """增加修复的 bug 数量"""
        self.stats["intelligence"]["total_bugs_fixed"] += 1
        self.save()

    # 协作类统计
    def increment_tasks_completed(self) -> None:
        """增加完成任务数"""
        self.stats["collaboration"]["total_tasks_completed"] += 1
        if self.stats["history"]["first_task_completed"] is None:
            self.stats["history"]["first_task_completed"] = None
        self.save()

    def update_continuous_work_hours(self, hours: float) -> None:
        """更新连续工作小时数"""
        if hours > self.stats["collaboration"]["continuous_work_hours"]:
            self.stats["collaboration"]["continuous_work_hours"] = hours
        self.save()

    def update_simultaneous_subagents(self, count: int) -> None:
        """更新同时运行的子代理数"""
        if count > self.stats["collaboration"]["max_simultaneous_subagents"]:
            self.stats["collaboration"]["max_simultaneous_subagents"] = count
        self.save()

    def increment_heartbeat_responses(self) -> None:
        """增加心跳响应次数"""
        self.stats["collaboration"]["total_heartbeat_responses"] += 1
        self.save()

    # 项目类统计
    def increment_projects_started(self) -> None:
        """增加启动的项目数"""
        self.stats["project"]["projects_started"] += 1
        self.save()

    def increment_projects_deployed(self) -> None:
        """增加部署的项目数"""
        self.stats["project"]["projects_deployed"] += 1
        self.save()

    def increment_git_commits(self) -> None:
        """增加 Git 提交次数"""
        self.stats["project"]["total_git_commits"] += 1
        self.save()

    def increment_documents(self) -> None:
        """增加文档数量"""
        self.stats["project"]["total_documents"] += 1
        self.save()

    # 获取统计数据
    def get_stats(self) -> Dict[str, Any]:
        """获取所有统计数据"""
        stats_copy = self.stats.copy()
        stats_copy["execution"]["tools_used"] = list(self.stats["execution"]["tools_used"])
        return stats_copy

    def get_progress(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        """根据成就 ID 获取进度"""
        progress_map = {
            # 执行类
            "first_task": {"current": 1 if self.stats["collaboration"]["total_tasks_completed"] > 0 else 0, "target": 1},
            "hundred_calls": {"current": self.stats["execution"]["total_tool_calls"], "target": 100},
            "thousand_calls": {"current": self.stats["execution"]["total_api_calls"], "target": 1000},
            "multi_tool": {"current": self.stats["execution"]["unique_tools_used"], "target": 10},

            # 智力类
            "memory_master": {"current": self.stats["intelligence"]["total_memories"], "target": 500},
            "search_expert": {"current": self.stats["intelligence"]["total_searches"], "target": 100},
            "code_expert": {"current": self.stats["intelligence"]["total_code_lines"], "target": 5000},
            "debug_expert": {"current": self.stats["intelligence"]["total_bugs_fixed"], "target": 50},

            # 协作类
            "assistant_star": {"current": self.stats["collaboration"]["total_tasks_completed"], "target": 100},
            "efficiency_king": {"current": self.stats["collaboration"]["continuous_work_hours"], "target": 24},
            "multithread": {"current": self.stats["collaboration"]["max_simultaneous_subagents"], "target": 3},
            "punctual": {"current": self.stats["collaboration"]["total_heartbeat_responses"], "target": 100},

            # 项目类
            "project_starter": {"current": self.stats["project"]["projects_started"], "target": 1},
            "deploy_master": {"current": self.stats["project"]["projects_deployed"], "target": 3},
            "git_master": {"current": self.stats["project"]["total_git_commits"], "target": 100},
            "doc_expert": {"current": self.stats["project"]["total_documents"], "target": 50}
        }

        return progress_map.get(achievement_id)


# 全局统计实例
_stats_instance = None


def get_stats_instance() -> AchievementStats:
    """获取统计实例（单例）"""
    global _stats_instance
    if _stats_instance is None:
        _stats_instance = AchievementStats()
    return _stats_instance


# 便捷函数
def track_tool_call(tool_name: str = None) -> None:
    """追踪工具调用"""
    get_stats_instance().increment_tool_calls(tool_name)


def track_api_call() -> None:
    """追踪 API 调用"""
    get_stats_instance().increment_api_calls()


def track_memory() -> None:
    """追踪记忆记录"""
    get_stats_instance().increment_memories()


def track_search() -> None:
    """追踪搜索"""
    get_stats_instance().increment_searches()


def track_code_lines(lines: int) -> None:
    """追踪代码行数"""
    get_stats_instance().add_code_lines(lines)


def track_task_completed() -> None:
    """追踪任务完成"""
    get_stats_instance().increment_tasks_completed()


def track_heartbeat() -> None:
    """追踪心跳响应"""
    get_stats_instance().increment_heartbeat_responses()


def track_git_commit() -> None:
    """追踪 Git 提交"""
    get_stats_instance().increment_git_commits()


def track_document() -> None:
    """追踪文档编写"""
    get_stats_instance().increment_documents()


def track_project_deployed() -> None:
    """追踪项目部署"""
    get_stats_instance().increment_projects_deployed()
