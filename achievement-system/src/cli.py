"""命令行界面模块 - 提供用户友好的 CLI 交互"""

import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from achievements import AchievementManager
from progress import ProgressTracker
from storage import (
    load_achievements, save_achievements, save_progress,
    get_achievement_by_id
)

# 初始化 Rich Console（深色主题）
console = Console(theme=None)


@click.group()
@click.version_option(version="1.0.0", prog_name="ach")
def cli():
    """成就系统 - 个人成长追踪工具 🏆

    使用深色科技风格的命令行工具，帮助你追踪和成就目标！
    """
    pass


@cli.command()
def init():
    """初始化成就系统（创建默认数据）"""
    console.print("\n[bold cyan]🚀 正在初始化成就系统...[/bold cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("创建数据文件...", total=None)

        # 默认成就配置
        default_achievements = {
            "achievements": [
                {
                    "id": "hello_world",
                    "name": "Hello World",
                    "description": "第一次使用成就系统",
                    "icon": "🌟",
                    "points": 10,
                    "category": "system"
                },
                {
                    "id": "daily_login",
                    "name": "每日打卡",
                    "description": "连续 7 天登录",
                    "icon": "📅",
                    "points": 30,
                    "category": "habit",
                    "requirements": {"count": 7}
                },
                {
                    "id": "code_master",
                    "name": "代码大师",
                    "description": "累计 1000 行代码",
                    "icon": "💻",
                    "points": 50,
                    "category": "development",
                    "requirements": {"count": 1000}
                },
                {
                    "id": "first_commit",
                    "name": "首次提交",
                    "description": "完成第一次 Git 提交",
                    "icon": "🎯",
                    "points": 10,
                    "category": "git"
                },
                {
                    "id": "code_review",
                    "name": "代码审查",
                    "description": "完成 5 次代码审查",
                    "icon": "🔍",
                    "points": 20,
                    "category": "development",
                    "requirements": {"count": 5}
                }
            ]
        }

        # 保存成就配置
        save_achievements(default_achievements)

        # 重置用户进度
        default_progress = {
            "user_id": "default",
            "unlocked_achievements": [],
            "progress": {},
            "statistics": {
                "total_points": 0,
                "total_unlocked": 0,
                "last_updated": None
            }
        }
        save_progress(default_progress)

        progress.update(task, description="✅ 初始化完成！")

    console.print("\n[bold green]✨ 成就系统已成功初始化！[/bold green]\n")
    console.print("使用 [cyan]ach list[/cyan] 查看所有成就")
    console.print("使用 [cyan]ach status[/cyan] 查看当前进度\n")


@cli.command()
def list():
    """列出所有成就"""
    manager = AchievementManager()
    all_achievements = manager.get_all_achievements()
    unlocked_ids = set(manager.progress.get("unlocked_achievements", []))

    console.print("\n[bold cyan]📋 成就列表[/bold cyan]\n")

    # 按分类组织
    categories = {}
    for achievement in all_achievements:
        category = achievement.get("category", "default")
        if category not in categories:
            categories[category] = []
        categories[category].append(achievement)

    # 显示每个分类
    for category, achievements in categories.items():
        console.print(f"[bold yellow]📁 {category.upper()}[/bold yellow]")

        table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("图标", style="bold", width=4)
        table.add_column("名称", style="cyan", width=20)
        table.add_column("描述", style="white", width=30)
        table.add_column("积分", style="green", width=8)
        table.add_column("状态", width=10)

        for achievement in achievements:
            achievement_id = achievement.get("id")
            is_unlocked = achievement_id in unlocked_ids

            status = "[bold green]✓ 已解锁[/bold green]" if is_unlocked else "[dim]✗ 未解锁[/dim]"

            # 显示进度
            if not is_unlocked:
                progress = manager.get_progress_for_achievement(achievement_id)
                if progress:
                    status = f"[dim]{progress['current']}/{progress['target']}[/dim]"

            table.add_row(
                achievement.get("icon", "🏆"),
                achievement.get("name"),
                achievement.get("description"),
                f"[bold green]{achievement.get('points')}[/bold green]",
                status
            )

        console.print(table)
        console.print()

    console.print(f"[dim]总计: {len(all_achievements)} 个成就[/dim]\n")


@cli.command()
def status():
    """查看当前进度"""
    tracker = ProgressTracker()
    status_data = tracker.display_status()

    console.print("\n[bold cyan]📊 当前进度[/bold cyan]\n")

    # 分离已解锁和未解锁
    unlocked = [s for s in status_data if s["is_unlocked"]]
    locked = [s for s in status_data if not s["is_unlocked"]]

    # 已解锁
    if unlocked:
        console.print("[bold green]✅ 已解锁成就[/bold green]")
        for item in unlocked:
            console.print(f"  {item['icon']} [cyan]{item['name']}[/cyan] - [bold green]+{item['points']} 积分[/bold green]")
        console.print()

    # 进行中
    if locked:
        console.print("[bold yellow]⏳ 进行中[/bold yellow]")
        for item in locked:
            if "current" in item and "target" in item:
                bar = tracker.format_progress_bar(item["current"], item["target"])
                console.print(f"  {item['icon']} [cyan]{item['name']}[/cyan] - {item['current']}/{item['target']}")
                console.print(f"    [dim]{bar}[/dim]")
            else:
                console.print(f"  {item['icon']} [cyan]{item['name']}[/cyan] - [dim]0/1[/dim]")
        console.print()

    # 未开始
    not_started = [s for s in locked if "current" not in s]
    if not_started:
        console.print("[dim]🔘 未开始[/dim]")
        for item in not_started:
            console.print(f"  [dim]{item['icon']} {item['name']}[/dim]")
        console.print()


@cli.command()
def stats():
    """显示统计信息"""
    tracker = ProgressTracker()
    stats_data = tracker.display_statistics()

    console.print("\n[bold cyan]📈 统计信息[/bold cyan]\n")

    # 创建统计面板
    stats_text = Text()
    stats_text.append(f"总成就数: ", style="white")
    stats_text.append(f"{stats_data['total_achievements']}", style="cyan bold")
    stats_text.append("\n")

    stats_text.append(f"已解锁: ", style="white")
    stats_text.append(f"{stats_data['unlocked']}", style="green bold")
    stats_text.append("\n")

    stats_text.append(f"未解锁: ", style="white")
    stats_text.append(f"{stats_data['locked']}", style="yellow bold")
    stats_text.append("\n")

    stats_text.append(f"完成率: ", style="white")
    stats_text.append(f"{stats_data['completion_rate']:.1f}%", style="magenta bold")
    stats_text.append("\n")

    stats_text.append(f"总积分: ", style="white")
    stats_text.append(f"{stats_data['total_points']}", style="yellow bold")

    console.print(Panel(stats_text, title="[bold]📊 成就统计[/bold]", border_style="cyan"))
    console.print()


@cli.command()
@click.argument('achievement_id')
def unlock(achievement_id: str):
    """解锁成就"""
    manager = AchievementManager()

    console.print(f"\n[cyan]🔓 正在尝试解锁成就: {achievement_id}[/cyan]\n")

    achievement = get_achievement_by_id(achievement_id)
    if not achievement:
        console.print(f"[bold red]❌ 成就 '{achievement_id}' 不存在[/bold red]\n")
        return

    # 检查是否已解锁
    if achievement_id in manager.progress.get("unlocked_achievements", []):
        console.print(f"[dim]✓ 成就 '{achievement.get('name')}' 已经解锁[/dim]\n")
        return

    # 检查进度要求
    requirements = achievement.get("requirements", {})
    if requirements:
        progress = manager.get_progress_for_achievement(achievement_id)
        if not progress or progress["current"] < progress["target"]:
            console.print(f"[bold yellow]⚠️  进度不足，无法解锁[/bold yellow]")
            if progress:
                console.print(f"[dim]当前进度: {progress['current']}/{progress['target']}[/dim]\n")
            else:
                console.print(f"[dim]使用 'ach add {achievement_id} <数量>' 增加进度[/dim]\n")
            return

    # 解锁成就
    unlocked = manager.unlock_achievement(achievement_id)
    if unlocked:
        console.print(Panel(
            f"[bold green]🎉 恭喜！[/bold green]\n\n"
            f"[cyan]{unlocked.get('icon', '🏆')} {unlocked.get('name')}[/cyan]\n"
            f"[dim]{unlocked.get('description')}[/dim]\n\n"
            f"[bold green]+{unlocked.get('points', 0)} 积分[/bold green]",
            title="[bold]✨ 成就解锁！[/bold]",
            border_style="green"
        ))
    else:
        console.print("[bold red]❌ 解锁失败[/bold red]\n")

    console.print()


@cli.command()
@click.argument('achievement_id')
@click.argument('amount', type=int, default=1)
def add(achievement_id: str, amount: int):
    """添加成就进度"""
    manager = AchievementManager()

    console.print(f"\n[cyan]➕ 添加进度: {achievement_id} (+{amount})[/cyan]\n")

    achievement = get_achievement_by_id(achievement_id)
    if not achievement:
        console.print(f"[bold red]❌ 成就 '{achievement_id}' 不存在[/bold red]\n")
        return

    # 添加进度
    success, message, unlocked = manager.update_progress(achievement_id, amount)

    if success:
        console.print(f"[green]✓ {message}[/green]")

        # 如果解锁了成就，显示庆祝信息
        if unlocked:
            console.print(Panel(
                f"[bold yellow]🏆 {unlocked.get('icon')} {unlocked.get('name')}[/bold yellow]\n"
                f"[dim]{unlocked.get('description')}[/dim]\n"
                f"[bold green]+{unlocked.get('points', 0)} 积分[/bold green]",
                title="[bold]🎉 成就解锁！[/bold]",
                border_style="yellow"
            ))
    else:
        console.print(f"[yellow]⚠️  {message}[/yellow]")

    console.print()


if __name__ == "__main__":
    cli()
