"""
CLI 命令处理系统

处理内置命令和参数解析，提供命令帮助和自动补全功能。
"""

import sys
import argparse
from typing import Dict, List, Callable, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

from .config import get_config
from .chat_manager import ChatManager


class CommandResult:
    """命令执行结果"""
    def __init__(self, success: bool, message: str = "", data: Any = None):
        self.success = success
        self.message = message
        self.data = data

    def __bool__(self):
        return self.success


class CLICommand:
    """CLI 命令基类"""
    def __init__(self, name: str, description: str, usage: str = "", examples: List[str] = None):
        self.name = name
        self.description = description
        self.usage = usage
        self.examples = examples or []
        self.aliases: List[str] = []

    def add_alias(self, alias: str):
        """添加别名"""
        self.aliases.append(alias)

    def execute(self, args: List[str], chat_manager: ChatManager) -> CommandResult:
        """执行命令（子类实现）"""
        raise NotImplementedError

    def get_help(self) -> str:
        """获取帮助信息"""
        help_text = f"**{self.name}** - {self.description}\n"
        if self.usage:
            help_text += f"用法: {self.usage}\n"
        if self.aliases:
            help_text += f"别名: {', '.join(self.aliases)}\n"
        if self.examples:
            help_text += "示例:\n"
            for example in self.examples:
                help_text += f"  {example}\n"
        return help_text


class HelpCommand(CLICommand):
    """帮助命令"""
    def __init__(self, command_registry):
        super().__init__(
            name="help",
            description="显示帮助信息",
            usage="/help [command_name]",
            examples=[
                "/help",
                "/help new",
                "/help history"
            ]
        )
        self.command_registry = command_registry

    def execute(self, args: List[str], chat_manager: ChatManager) -> CommandResult:
        if not args:
            # 显示所有命令列表
            return self._show_all_commands()
        else:
            # 显示特定命令的帮助
            command_name = args[0].lstrip('/')
            command = self.command_registry.get_command(command_name)
            if command:
                return CommandResult(True, command.get_help())
            else:
                return CommandResult(False, f"未知命令: {command_name}")

    def _show_all_commands(self) -> CommandResult:
        """显示所有命令"""
        console = Console()
        console.print("📚 可用命令列表:", style="bold blue")
        console.print("=" * 60, style="blue")

        table = Table()
        table.add_column("命令", style="cyan", width=15)
        table.add_column("描述", style="white", width=40)
        table.add_column("别名", style="green", width=15)

        commands = sorted(self.command_registry.commands.values(), key=lambda c: c.name)

        for command in commands:
            aliases = ", ".join(command.aliases) if command.aliases else "-"
            table.add_row(f"/{command.name}", command.description, aliases)

        console.print(table)
        console.print("\n💡 使用 '/help <command_name>' 查看具体命令的详细帮助")

        return CommandResult(True)


class NewCommand(CLICommand):
    """新建会话命令"""
    def __init__(self):
        super().__init__(
            name="new",
            description="创建新的聊天会话",
            usage="/new [session_name]",
            examples=[
                "/new",
                "/new 工作助手",
                "/new 学习笔记"
            ]
        )
        self.add_alias("create")

    def execute(self, args: List[str], chat_manager: ChatManager) -> CommandResult:
        session_name = " ".join(args) if args else None
        session = chat_manager.create_session(session_name)
        return CommandResult(True, f"已创建新会话: {session.name}")


class SwitchCommand(CLICommand):
    """切换会话命令"""
    def __init__(self):
        super().__init__(
            name="switch",
            description="切换到指定的聊天会话",
            usage="/switch <session_id|session_name>",
            examples=[
                "/switch 1",
                "/switch 工作助手"
            ]
        )
        self.add_alias("use")

    def execute(self, args: List[str], chat_manager: ChatManager) -> CommandResult:
        if not args:
            return CommandResult(False, "请指定会话ID或名称")

        target = args[0]

        # 尝试按ID查找
        for session_id, session in chat_manager.sessions.items():
            if session_id.startswith(target) or session.name == target:
                if chat_manager.switch_session(session_id):
                    return CommandResult(True, f"已切换到会话: {session.name}")
                else:
                    return CommandResult(False, "切换失败")

        return CommandResult(False, f"找不到会话: {target}")


class ListCommand(CLICommand):
    """列会话命令"""
    def __init__(self):
        super().__init__(
            name="list",
            description="列出所有聊天会话",
            usage="/list",
            examples=[
                "/list",
                "/sessions"
            ]
        )
        self.add_alias("sessions")

    def execute(self, args: List[str], chat_manager: ChatManager) -> CommandResult:
        chat_manager.display_sessions()
        return CommandResult(True)


class HistoryCommand(CLICommand):
    """历史命令"""
    def __init__(self):
        super().__init__(
            name="history",
            description="显示聊天历史记录",
            usage="/history [count]",
            examples=[
                "/history",
                "/history 10",
                "/history 50"
            ]
        )
        self.add_alias("hist")

    def execute(self, args: List[str], chat_manager: ChatManager) -> CommandResult:
        try:
            count = int(args[0]) if args else 20
            count = min(max(count, 1), 100)  # 限制在1-100之间
        except (ValueError, IndexError):
            count = 20

        chat_manager.display_session_history(count=count)
        return CommandResult(True)


class ClearCommand(CLICommand):
    """清空命令"""
    def __init__(self):
        super().__init__(
            name="clear",
            description="清空当前会话的消息历史",
            usage="/clear",
            examples=[
                "/clear",
                "/cls"
            ]
        )
        self.add_alias("cls")

    def execute(self, args: List[str], chat_manager: ChatManager) -> CommandResult:
        chat_manager.clear_current_session()
        return CommandResult(True, "已清空当前会话")


class DeleteCommand(CLICommand):
    """删除会话命令"""
    def __init__(self):
        super().__init__(
            name="delete",
            description="删除指定的聊天会话",
            usage="/delete <session_id|session_name>",
            examples=[
                "/delete 1",
                "/delete 旧的会话"
            ]
        )
        self.add_alias("rm")
        self.add_alias("del")

    def execute(self, args: List[str], chat_manager: ChatManager) -> CommandResult:
        if not args:
            return CommandResult(False, "请指定要删除的会话ID或名称")

        target = args[0]

        # 尝试按ID查找
        for session_id, session in chat_manager.sessions.items():
            if session_id.startswith(target) or session.name == target:
                if chat_manager.delete_session(session_id):
                    return CommandResult(True, f"已删除会话: {session.name}")
                else:
                    return CommandResult(False, "删除失败")

        return CommandResult(False, f"找不到会话: {target}")


class ExportCommand(CLICommand):
    """导出命令"""
    def __init__(self):
        super().__init__(
            name="export",
            description="导出当前会话到文件",
            usage="/export [file_path]",
            examples=[
                "/export",
                "/export chat_backup.json",
                "/export /path/to/export.json"
            ]
        )
        self.add_alias("save")

    def execute(self, args: List[str], chat_manager: ChatManager) -> CommandResult:
        try:
            file_path = args[0] if args else None
            export_path = chat_manager.export_session(file_path=file_path)
            return CommandResult(True, f"会话已导出到: {export_path}")
        except Exception as e:
            return CommandResult(False, f"导出失败: {str(e)}")


class ConfigCommand(CLICommand):
    """配置命令"""
    def __init__(self):
        super().__init__(
            name="config",
            description="查看或修改配置",
            usage="/config [key] [value]",
            examples=[
                "/config",
                "/config debug_mode",
                "/config debug_mode true",
                "/config max_steps 15"
            ]
        )
        self.add_alias("cfg")
        self.add_alias("settings")

    def execute(self, args: List[str], chat_manager: ChatManager) -> CommandResult:
        config = get_config()

        if not args:
            # 显示所有配置
            config.display()
            return CommandResult(True)

        if len(args) == 1:
            # 显示特定配置
            key = args[0]
            if hasattr(config, key):
                value = getattr(config, key)
                return CommandResult(True, f"{key}: {value}")
            else:
                return CommandResult(False, f"未知配置项: {key}")

        if len(args) >= 2:
            # 修改配置
            key = args[0]
            value = " ".join(args[1:])

            if not hasattr(config, key):
                return CommandResult(False, f"未知配置项: {key}")

            # 类型转换
            current_value = getattr(config, key)
            if isinstance(current_value, bool):
                if value.lower() in ('true', '1', 'yes', 'on'):
                    value = True
                elif value.lower() in ('false', '0', 'no', 'off'):
                    value = False
                else:
                    return CommandResult(False, f"布尔值必须是 true/false, yes/no, on/off, 1/0")
            elif isinstance(current_value, int):
                try:
                    value = int(value)
                except ValueError:
                    return CommandResult(False, f"整数值格式错误: {value}")
            elif isinstance(current_value, float):
                try:
                    value = float(value)
                except ValueError:
                    return CommandResult(False, f"数值格式错误: {value}")

            # 更新配置
            setattr(config, key, value)
            config.save_to_file()

            return CommandResult(True, f"配置已更新: {key} = {value}")

        return CommandResult(False, "参数错误")


class StatsCommand(CLICommand):
    """统计命令"""
    def __init__(self):
        super().__init__(
            name="stats",
            description="显示使用统计信息",
            usage="/stats",
            examples=[
                "/stats",
                "/statistics"
            ]
        )
        self.add_alias("statistics")
        self.add_alias("info")

    def execute(self, args: List[str], chat_manager: ChatManager) -> CommandResult:
        stats = chat_manager.get_statistics()
        config = get_config()

        console = Console()
        console.print("📊 使用统计信息:", style="bold blue")
        console.print("=" * 40, style="blue")
        console.print(f"总会话数: {stats['total_sessions']}")
        console.print(f"总消息数: {stats['total_messages']}")
        console.print(f"当前会话: {stats['current_session_name'] or 'None'}")
        console.print(f"当前消息数: {stats['current_session_messages']}")
        console.print(f"调试模式: {'开启' if config.debug_mode else '关闭'}")
        console.print(f"最大步数: {config.max_steps}")

        return CommandResult(True)


class QuitCommand(CLICommand):
    """退出命令"""
    def __init__(self):
        super().__init__(
            name="quit",
            description="退出程序",
            usage="/quit",
            examples=[
                "/quit",
                "/exit",
                "/q"
            ]
        )
        self.add_alias("exit")
        self.add_alias("q")

    def execute(self, args: List[str], chat_manager: ChatManager) -> CommandResult:
        console = Console()
        console.print("👋 再见!", style="bold green")
        sys.exit(0)


class CommandRegistry:
    """命令注册器"""
    def __init__(self):
        self.commands: Dict[str, CLICommand] = {}
        self._register_default_commands()

    def _register_default_commands(self):
        """注册默认命令"""
        default_commands = [
            HelpCommand(self),
            NewCommand(),
            SwitchCommand(),
            ListCommand(),
            HistoryCommand(),
            ClearCommand(),
            DeleteCommand(),
            ExportCommand(),
            ConfigCommand(),
            StatsCommand(),
            QuitCommand(),
        ]

        for command in default_commands:
            self.register_command(command)

    def register_command(self, command: CLICommand):
        """注册命令"""
        self.commands[command.name] = command

        # 注册别名
        for alias in command.aliases:
            self.commands[alias] = command

    def get_command(self, name: str) -> Optional[CLICommand]:
        """获取命令"""
        return self.commands.get(name)

    def is_command(self, text: str) -> bool:
        """检查是否为命令"""
        if not text.startswith('/'):
            return False

        parts = text[1:].split()
        command_name = parts[0] if parts else ""

        return command_name in self.commands

    def execute_command(self, text: str, chat_manager: ChatManager) -> CommandResult:
        """执行命令"""
        if not text.startswith('/'):
            return CommandResult(False, "不是有效的命令格式")

        parts = text[1:].split()
        command_name = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        command = self.get_command(command_name)
        if not command:
            return CommandResult(False, f"未知命令: {command_name}")

        try:
            return command.execute(args, chat_manager)
        except Exception as e:
            return CommandResult(False, f"命令执行失败: {str(e)}")

    def get_all_commands(self) -> List[CLICommand]:
        """获取所有命令"""
        # 去重（因为有别名）
        seen = set()
        unique_commands = []
        for command in self.commands.values():
            if command.name not in seen:
                seen.add(command.name)
                unique_commands.append(command)

        return sorted(unique_commands, key=lambda c: c.name)


if __name__ == "__main__":
    # 测试命令系统
    console = Console()
    console.print("🧪 测试命令系统", style="bold blue")

    # 创建命令注册器
    registry = CommandRegistry()
    chat_manager = ChatManager()

    # 测试帮助命令
    console.print("\n📚 测试帮助命令:")
    result = registry.execute_command("/help", chat_manager)
    console.print(f"结果: {result.success}")

    # 测试新建会话
    console.print("\n➕ 测试新建会话:")
    result = registry.execute_command("/new 测试会话", chat_manager)
    console.print(f"结果: {result.message}")

    # 测试配置命令
    console.print("\n⚙️ 测试配置命令:")
    result = registry.execute_command("/config", chat_manager)
    console.print(f"结果: {result.success}")

    console.print("\n✅ 命令系统测试完成", style="green")