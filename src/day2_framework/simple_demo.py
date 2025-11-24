#!/usr/bin/env python3
"""
Day 2 Agent 状态管理系统简单演示

无需交互输入，展示 Agent 状态管理系统的核心功能
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.day2_framework.state import Agent
from rich.console import Console


def main():
    """主演示函数"""
    console = Console()

    console.print("🎯 Day 2 Agent 状态管理系统演示", style="bold blue", justify="center")
    console.print("=" * 70, style="blue")
    console.print("展示基于 Pydantic 的 Agent 状态管理，便于调试和观察", style="italic")
    console.print()

    # 创建 Agent
    agent = Agent("demo_agent_simple", debug_mode=True)
    console.print("✅ Agent 创建成功", style="green")
    console.print(f"Agent ID: {agent.state.agent_id}")
    console.print(f"初始状态: {agent.state.status.value}")
    console.print(f"调试模式: {agent.state.debug_mode}")
    console.print()

    # 演示消息处理
    demo_messages = [
        "你好，请介绍一下你的功能",
        "帮我计算 100 + 200 等于多少？",
        "分析一下Python编程语言的特点"
    ]

    for i, message in enumerate(demo_messages, 1):
        console.print(f"📝 处理消息 {i}: {message}", style="cyan")
        console.print("-" * 50)

        # 处理消息
        response = agent.process_user_message(message)
        console.print(f"🤖 Agent 回复: {response}", style="green")

        # 显示状态摘要
        console.print("\n📊 状态摘要:")
        summary = agent.state.get_state_summary()
        console.print(f"  • 状态: {summary['status']}")
        console.print(f"  • 任务: {summary['current_task']}")
        console.print(f"  • 进度: {summary['progress']}")
        console.print(f"  • 消息数: {summary['messages_count']}")
        console.print(f"  • 工具调用数: {summary['tool_calls_count']}")
        console.print(f"  • 思考过程数: {summary['thoughts_count']}")

        if i < len(demo_messages):
            console.print("\n" + " " * 30 + "继续下一条消息...\n")

    # 显示完整状态信息
    console.print("\n🔍 完整状态详情", style="bold yellow", justify="center")
    console.print("=" * 70, style="yellow")

    agent.debugger.display_full_debug_info(agent.state)

    # 演示状态保存
    console.print("\n💾 状态保存演示", style="bold blue")
    state_file = "demo_agent_state.json"
    agent.save_state(state_file)
    console.print(f"✅ 状态已保存到: {state_file}")

    if os.path.exists(state_file):
        file_size = os.path.getsize(state_file)
        console.print(f"📁 文件大小: {file_size} 字节")

    # 清理文件
    if os.path.exists(state_file):
        os.remove(state_file)
        console.print(f"🗑️ 已清理临时文件")

    console.print("\n🎉 演示完成！", style="bold blue", justify="center")
    console.print("Agent 状态管理系统展现了强大的调试和观察能力", style="italic")


if __name__ == "__main__":
    main()