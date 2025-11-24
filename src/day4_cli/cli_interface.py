"""
CLI 界面核心模块

提供美观的命令行界面，处理用户输入和输出格式化。
"""

import sys
import readline
import threading
import time
from typing import Optional, Callable, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.align import Align
from rich.columns import Columns
from rich.status import Status

from .config import get_config
from .commands import CommandRegistry
from .chat_manager import ChatManager


class CLIInterface:
    """CLI 界面类"""

    def __init__(self):
        self.config = get_config()
        self.console = Console()
        self.command_registry = CommandRegistry()
        self.chat_manager = ChatManager()
        self.is_running = False
        self.input_callback: Optional[Callable[[str], None]] = None

        # 设置 readline 补全
        self._setup_readline()

    def _setup_readline(self):
        """设置 readline 自动补全"""
        try:
            # 获取所有命令名用于补全
            commands = [f"/{cmd.name}" for cmd in self.command_registry.get_all_commands()]
            commands.extend([f"/{alias}" for cmd in self.command_registry.get_all_commands() for alias in cmd.aliases])

            def completer(text, state):
                options = [cmd for cmd in commands if cmd.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            readline.set_completer(completer)
            readline.parse_and_bind("tab: complete")
            readline.set_completer_delims(' \t\n')
        except Exception:
            # 如果 readline 设置失败，忽略错误
            pass

    def display_welcome(self):
        """显示欢迎信息"""
        config = self.config
        welcome_text = f"""
🤖 欢迎使用 {config.app_name} v{config.version}

基于 ReAct 模式的智能助手 CLI 应用
💬 输入消息开始对话，或输入 /help 查看帮助
⚡ 支持命令补全 (Tab 键)
🎯 当前模式: {'调试' if config.debug_mode else '普通'}
        """

        panel = Panel(
            Align.center(welcome_text.strip()),
            title="🚀 AI Assistant CLI",
            border_style="blue",
            padding=(1, 2)
        )

        self.console.print(panel)
        self.console.print()

    def display_prompt(self) -> str:
        """显示提示符并获取用户输入"""
        session = self.chat_manager.get_current_session()
        session_name = session.name if session else "新会话"

        if self.config.colored_output:
            prompt = f"[bold green]👤 用户[/bold green] [dim]({session_name})[/dim]> "
        else:
            prompt = f"👤 用户 ({session_name})> "

        try:
            user_input = self.console.input(prompt).strip()
            return user_input
        except (KeyboardInterrupt, EOFError):
            return "/quit"

    def display_user_message(self, content: str):
        """显示用户消息"""
        session = self.chat_manager.get_current_session()
        session_name = session.name if session else "新会话"

        if self.config.colored_output:
            # 创建用户消息面板
            user_panel = Panel(
                content,
                title=f"👤 用户 ({session_name})",
                border_style="green",
                padding=(0, 1)
            )
            self.console.print(user_panel)
        else:
            self.console.print(f"👤 用户: {content}")

    def display_assistant_message(self, content: str, metadata: Optional[dict] = None):
        """显示助手消息"""
        if self.config.colored_output:
            # 创建助手消息面板
            assistant_panel = Panel(
                content,
                title="🤖 AI 助手",
                border_style="cyan",
                padding=(0, 1)
            )
            self.console.print(assistant_panel)
        else:
            self.console.print(f"🤖 AI 助手: {content}")

        # 显示元数据（如果有）
        if metadata and self.config.show_tool_calls:
            self._display_metadata(metadata)

    def _display_metadata(self, metadata: dict):
        """显示消息元数据"""
        if not metadata:
            return

        metadata_table = Table(title="📊 执行信息", show_header=False, box=None)
        metadata_table.add_column("项目", style="blue")
        metadata_table.add_column("值", style="white")

        for key, value in metadata.items():
            metadata_table.add_row(str(key), str(value))

        self.console.print(metadata_table)
        self.console.print()

    def display_thinking(self, text: str):
        """显示思考过程"""
        if self.config.show_thinking_process:
            if self.config.colored_output:
                thinking_panel = Panel(
                    text,
                    title="🧠 思考过程",
                    border_style="yellow",
                    padding=(0, 1)
                )
                self.console.print(thinking_panel)
            else:
                self.console.print(f"🧠 思考: {text}")

    def display_tool_call(self, tool_name: str, parameters: dict, result: Any):
        """显示工具调用"""
        if not self.config.show_tool_calls:
            return

        if self.config.colored_output:
            # 工具调用信息
            tool_info = f"🔧 工具: {tool_name}\n📥 参数: {parameters}\n📤 结果: {result}"
            tool_panel = Panel(
                tool_info,
                title=f"🛠️ 工具执行",
                border_style="magenta",
                padding=(0, 1)
            )
            self.console.print(tool_panel)
        else:
            self.console.print(f"🔧 调用工具 {tool_name}: {parameters} -> {result}")

    def display_error(self, error: str, details: Optional[str] = None):
        """显示错误信息"""
        if self.config.colored_output:
            error_content = error
            if details:
                error_content += f"\n\n详细信息: {details}"

            error_panel = Panel(
                error_content,
                title="❌ 错误",
                border_style="red",
                padding=(0, 1)
            )
            self.console.print(error_panel)
        else:
            self.console.print(f"❌ 错误: {error}")
            if details:
                self.console.print(f"   详情: {details}")

    def display_success(self, message: str):
        """显示成功信息"""
        if self.config.colored_output:
            success_panel = Panel(
                message,
                title="✅ 成功",
                border_style="green",
                padding=(0, 1)
            )
            self.console.print(success_panel)
        else:
            self.console.print(f"✅ {message}")

    def display_status(self, message: str, spinner: str = "dots"):
        """显示状态信息（带动画）"""
        status = Status(message, spinner=spinner, console=self.console)
        return status

    def display_loading_indicator(self, message: str = "AI 正在思考..."):
        """显示加载指示器"""
        with self.console.status(message, spinner="dots") as status:
            # 这个方法会在上下文管理器中显示加载状态
            yield status

    def display_execution_trace(self, trace_data: dict):
        """显示执行轨迹"""
        if not self.config.show_execution_trace or not trace_data:
            return

        trace_panel = Panel(
            str(trace_data),
            title="🔍 执行轨迹",
            border_style="blue",
            padding=(0, 1)
        )
        self.console.print(trace_panel)

    def display_session_info(self):
        """显示当前会话信息"""
        session = self.chat_manager.get_current_session()
        if not session:
            self.console.print("📝 当前无会话", style="yellow")
            return

        stats = self.chat_manager.get_statistics()

        info_table = Table(title="📋 会话信息", show_header=False)
        info_table.add_column("项目", style="blue")
        info_table.add_column("值", style="white")

        info_table.add_row("会话名称", session.name)
        info_table.add_row("消息数量", str(len(session.messages)))
        info_table.add_row("创建时间", session.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        info_table.add_row("最后更新", session.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
        info_table.add_row("总会话数", str(stats["total_sessions"]))
        info_table.add_row("总消息数", str(stats["total_messages"]))

        self.console.print(info_table)

    def clear_screen(self):
        """清屏"""
        self.console.clear()

    def print_separator(self, char: str = "=", style: str = "blue"):
        """打印分隔线"""
        self.console.print(char * 60, style=style)

    def set_input_callback(self, callback: Callable[[str], None]):
        """设置输入回调函数"""
        self.input_callback = callback

    def handle_input(self, user_input: str):
        """处理用户输入"""
        # 保存用户消息到聊天历史
        if user_input.startswith('/'):
            # 处理命令
            result = self.command_registry.execute_command(user_input, self.chat_manager)
            if not result.success:
                self.display_error(result.message)
            elif result.message:
                self.display_success(result.message)
        else:
            # 普通聊天消息
            self.chat_manager.add_user_message(user_input)

            # 调用输入回调（如果设置）
            if self.input_callback:
                self.input_callback(user_input)

    def run_interactive_loop(self):
        """运行交互式循环"""
        self.is_running = True
        self.display_welcome()

        try:
            while self.is_running:
                try:
                    # 获取用户输入
                    user_input = self.display_prompt()

                    if not user_input:
                        continue

                    # 处理输入
                    self.handle_input(user_input)

                except KeyboardInterrupt:
                    # 处理 Ctrl+C
                    self.console.print("\n👋 再见!", style="bold green")
                    break
                except EOFError:
                    # 处理 Ctrl+D
                    self.console.print("\n👋 再见!", style="bold green")
                    break
                except Exception as e:
                    self.display_error("处理输入时发生错误", str(e))

        finally:
            self.is_running = False

    def stop(self):
        """停止交互循环"""
        self.is_running = False


class FormattedOutput:
    """格式化输出工具类"""

    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化时间长度"""
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds // 60)
            remaining = seconds % 60
            return f"{minutes}m {remaining:.0f}s"

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    @staticmethod
    def format_number(number: int) -> str:
        """格式化数字（添加千位分隔符）"""
        return f"{number:,}"

    @staticmethod
    def create_progress_bar(current: int, total: int, width: int = 20) -> str:
        """创建进度条"""
        filled = int(width * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (width - filled)
        percentage = (current / total * 100) if total > 0 else 0
        return f"[{bar}] {percentage:.1f}%"


if __name__ == "__main__":
    # 测试 CLI 界面
    console = Console()
    console.print("🧪 测试 CLI 界面", style="bold blue")

    # 创建 CLI 界面
    cli = CLIInterface()

    # 测试各种显示方法
    console.print("\n📝 测试用户消息显示:")
    cli.display_user_message("你好，我想了解一下 ReAct Agent")

    console.print("\n🤖 测试助手消息显示:")
    cli.display_assistant_message("ReAct Agent 是一个结合推理和行动的智能代理系统...")

    console.print("\n🧠 测试思考过程显示:")
    cli.display_thinking("用户询问了 ReAct Agent，我需要详细解释这个概念")

    console.print("\n🔧 测试工具调用显示:")
    cli.display_tool_call("calculator", {"expression": "123 + 456"}, 579)

    console.print("\n❌ 测试错误显示:")
    cli.display_error("API 调用失败", "网络连接超时")

    console.print("\n✅ 测试成功显示:")
    cli.display_success("配置已保存")

    console.print("\n📋 测试会话信息显示:")
    cli.display_session_info()

    console.print("\n🎯 CLI 界面测试完成!", style="bold green")