#!/usr/bin/env python3
"""
Day 4 CLI 聊天应用演示程序

展示完整的 CLI 聊天应用功能，包括 ReAct 模式集成、命令系统、配置管理等。
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout

# 导入我们的模块
try:
    from src.day4_cli.config import CLIConfig, get_config
    from src.day4_cli.chat_manager import ChatManager, ChatSession, ChatMessage
    from src.day4_cli.commands import CommandRegistry, HelpCommand, NewCommand
    from src.day4_cli.cli_interface import CLIInterface
    from src.day4_cli.app import AssistantApp
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有依赖包，并且项目结构正确")
    IMPORTS_AVAILABLE = False


def demo_config():
    """演示配置管理"""
    console = Console()

    if not IMPORTS_AVAILABLE:
        console.print("❌ 无法运行配置演示，请检查依赖安装", style="bold red")
        return

    console.print("🔧 配置管理演示", style="bold blue", justify="center")
    console.print("=" * 60, style="blue")

    # 创建自定义配置
    config = CLIConfig(
        debug_mode=True,
        max_steps=5,
        show_thinking_process=True,
        show_tool_calls=True,
        colored_output=True
    )

    console.print("✅ 创建自定义配置")
    config.display()

    # 保存配置
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config_file = f.name

    try:
        config.save_to_file(config_file)
        console.print(f"✅ 配置已保存到临时文件")

        # 加载配置
        loaded_config = CLIConfig.load_from_file(config_file)
        console.print("✅ 从文件加载配置成功")
        console.print(f"📋 调试模式: {loaded_config.debug_mode}")
        console.print(f"📋 最大步数: {loaded_config.max_steps}")

    finally:
        # 清理临时文件
        Path(config_file).unlink(missing_ok=True)


def demo_chat_manager():
    """演示聊天管理"""
    console = Console()

    if not IMPORTS_AVAILABLE:
        console.print("❌ 无法运行聊天管理演示，请检查依赖安装", style="bold red")
        return

    console.print("💬 聊天管理演示", style="bold blue", justify="center")
    console.print("=" * 60, style="blue")

    # 创建临时聊天管理器
    chat_manager = ChatManager()

    # 创建几个测试会话
    console.print("\n📝 创建测试会话:")
    session1 = chat_manager.create_session("工作助手")
    chat_manager.add_user_message("你好，我想了解项目进展")
    chat_manager.add_assistant_message("项目进展良好，主要功能已经完成")

    session2 = chat_manager.create_session("学习笔记")
    chat_manager.add_user_message("什么是 ReAct 模式？")
    chat_manager.add_assistant_message("ReAct 是推理和行动的结合模式...")

    # 显示会话列表
    console.print("\n📋 会话列表:")
    chat_manager.display_sessions()

    # 显示会话历史
    console.print("\n📚 显示当前会话历史:")
    chat_manager.display_session_history(count=5)

    # 显示统计信息
    stats = chat_manager.get_statistics()
    console.print(f"\n📊 聊天统计: {stats}")


def demo_command_system():
    """演示命令系统"""
    console = Console()

    if not IMPORTS_AVAILABLE:
        console.print("❌ 无法运行命令系统演示，请检查依赖安装", style="bold red")
        return

    console.print("⚡ 命令系统演示", style="bold blue", justify="center")
    console.print("=" * 60, style="blue")

    # 创建命令注册器和聊天管理器
    registry = CommandRegistry()
    chat_manager = ChatManager()

    # 测试帮助命令
    console.print("\n📚 测试帮助命令:")
    result = registry.execute_command("/help", chat_manager)
    console.print(f"结果: {'成功' if result.success else '失败'}")

    # 测试新建会话命令
    console.print("\n➕ 测试新建会话命令:")
    result = registry.execute_command("/new 演示会话", chat_manager)
    console.print(f"结果: {result.message}")

    # 测试配置命令
    console.print("\n⚙️ 测试配置命令:")
    result = registry.execute_command("/config debug_mode", chat_manager)
    console.print(f"结果: {result.message}")

    # 测试统计命令
    console.print("\n📊 测试统计命令:")
    result = registry.execute_command("/stats", chat_manager)
    console.print(f"结果: {'成功' if result.success else '失败'}")

    # 显示所有可用命令
    console.print("\n🔧 所有可用命令:")
    commands = registry.get_all_commands()
    command_table = Table()
    command_table.add_column("命令", style="cyan")
    command_table.add_column("描述", style="white")

    for cmd in commands:
        command_table.add_row(f"/{cmd.name}", cmd.description)

    console.print(command_table)


def demo_cli_interface():
    """演示 CLI 界面"""
    console = Console()

    if not IMPORTS_AVAILABLE:
        console.print("❌ 无法运行 CLI 界面演示，请检查依赖安装", style="bold red")
        return

    console.print("🎨 CLI 界面演示", style="bold blue", justify="center")
    console.print("=" * 60, style="blue")

    # 创建 CLI 界面
    cli = CLIInterface()

    # 演示各种显示方法
    console.print("\n📝 用户消息显示:")
    cli.display_user_message("你好，我想了解一下 ReAct Agent")

    console.print("\n🤖 助手消息显示:")
    cli.display_assistant_message(
        "ReAct Agent 是一个结合推理和行动的智能代理系统，"
        "通过思考-行动-观察的循环来解决问题。"
    )

    console.print("\n🧠 思考过程显示:")
    cli.display_thinking(
        "用户询问了 ReAct Agent，我需要详细解释这个概念，"
        "包括它的核心思想和应用场景。"
    )

    console.print("\n🔧 工具调用显示:")
    cli.display_tool_call(
        "calculator",
        {"expression": "123 * 456"},
        {"result": 56088, "type": "integer"}
    )

    console.print("\n✅ 成功消息显示:")
    cli.display_success("配置已保存成功")

    console.print("\n❌ 错误消息显示:")
    cli.display_error("API 调用失败", "网络连接超时，请检查网络设置")

    console.print("\n📋 会话信息显示:")
    cli.display_session_info()


def demo_integration():
    """演示完整集成"""
    console = Console()

    if not IMPORTS_AVAILABLE:
        console.print("❌ 无法运行集成演示，请检查依赖安装", style="bold red")
        return

    console.print("🔗 完整集成演示", style="bold blue", justify="center")
    console.print("=" * 60, style="blue")

    try:
        # 创建应用实例
        console.print("🚀 创建 AssistantApp 实例...")
        app = AssistantApp()

        console.print("✅ 应用创建成功！")

        # 演示批处理模式
        console.print("\n📁 演示批处理模式...")

        # 创建临时输入文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("你好\n")
            f.write("2 + 2 等于多少？\n")
            f.write("现在几点了？\n")
            input_file = f.name

        try:
            # 创建临时输出文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                output_file = f.name

            console.print(f"📄 输入文件: {input_file}")
            console.print(f"📄 输出文件: {output_file}")

            # 运行批处理（这里只演示设置，不实际调用 API）
            console.print("⚡ 批处理设置完成")
            console.print("💡 实际运行会处理输入文件中的每一行")

        finally:
            # 清理临时文件
            Path(input_file).unlink(missing_ok=True)
            Path(output_file).unlink(missing_ok=True)

    except Exception as e:
        console.print(f"⚠️ 集成演示部分功能受限: {e}", style="yellow")


def main():
    """主演示函数"""
    console = Console()

    console.print("🎯 Day 4 CLI 聊天应用完整演示", style="bold blue", justify="center")
    console.print("=" * 80, style="blue")
    console.print("展示基于 ReAct 模式的 AI 助手 CLI 应用的完整功能", style="italic")
    console.print()

    # 检查环境
    if not IMPORTS_AVAILABLE:
        console.print("❌ 依赖不完整，部分演示无法运行", style="bold red")
        console.print("请确保已安装所有必要的依赖包", style="italic")
        console.print()

    # 运行各个演示
    demo_config()
    console.print()

    demo_chat_manager()
    console.print()

    demo_command_system()
    console.print()

    demo_cli_interface()
    console.print()

    demo_integration()

    console.print("\n🎉 演示完成！", style="bold green", justify="center")
    console.print("您已经了解了 CLI 聊天应用的所有核心功能", style="italic")

    console.print("\n📚 使用方法:")
    console.print("• 交互模式: python src/day4_cli/app.py run")
    console.print("• 批处理模式: python src/day4_cli/app.py run --batch input.txt")
    console.print("• 配置管理: python src/day4_cli/app.py config --all")
    console.print("• 演示模式: python src/day4_cli/app.py demo")

    console.print("\n🔧 命令行选项:")
    console.print("• --debug: 启用调试模式")
    console.print("• --config FILE: 指定配置文件")
    console.print("• --batch FILE: 批处理模式")
    console.print("• --output FILE: 批处理输出文件")

    console.print("\n💡 核心特性:")
    console.print("1. 完整的 ReAct 模式集成")
    console.print("2. 美观的 CLI 界面和用户体验")
    console.print("3. 强大的聊天历史管理")
    console.print("4. 灵活的配置系统")
    console.print("5. 丰富的命令支持")
    console.print("6. 批处理模式支持")


if __name__ == "__main__":
    main()