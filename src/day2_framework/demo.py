#!/usr/bin/env python3
"""
Agent 状态管理演示脚本

演示如何使用状态管理系统，包括：
1. Agent 创建和初始化
2. 状态变化观察
3. 调试信息展示
4. 状态保存和恢复
"""

import os
import sys
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.day2_framework.state import Agent, AgentState, StateDebugger, MessageRole, LogLevel


def demo_basic_functionality():
    """演示基本功能"""
    console = Console()

    console.print("🎯 Day 2 Agent 状态管理演示", style="bold blue", justify="center")
    console.print("=" * 80, style="blue")
    console.print()

    # 创建 Agent
    console.print("📝 1. 创建 Agent", style="bold green")
    agent = Agent(agent_id="demo_agent_001", debug_mode=True)

    # 显示初始状态
    console.print("\n📊 初始状态:")
    agent.debugger.display_state_summary(agent.state)

    input("\n按 Enter 继续...")

    return agent


def demo_message_processing(agent: Agent):
    """演示消息处理流程"""
    console = Console()

    console.print("\n💬 2. 消息处理流程演示", style="bold green")

    # 测试消息列表
    test_messages = [
        "你好，请分析一下当前AI技术的发展状况",
        "帮我计算 15 + 27 等于多少？",
        "搜索 Python 异步编程的最佳实践",
        "展示一段 Python 代码示例"
    ]

    for i, message in enumerate(test_messages, 1):
        console.print(f"\n👤 用户消息 {i}: {message}", style="cyan")

        # 处理消息
        response = agent.process_user_message(message)

        console.print(f"🤖 Agent 回复: {response}", style="green")

        # 显示状态摘要
        console.print("\n📊 处理后的状态摘要:")
        agent.debugger.display_state_summary(agent.state)

        if i < len(test_messages):
            input("\n按 Enter 继续下一条消息...")


def demo_debug_features(agent: Agent):
    """演示调试功能"""
    console = Console()

    console.print("\n🔍 3. 调试功能演示", style="bold green")

    # 显示消息历史
    console.print("\n💬 消息历史:")
    agent.debugger.display_messages(agent.state, limit=10)

    # 显示思考过程
    console.print("\n🧠 思考过程:")
    agent.debugger.display_thoughts(agent.state, limit=15)

    # 显示工具调用
    console.print("\n🔧 工具调用历史:")
    agent.debugger.display_tool_calls(agent.state)

    # 显示日志
    console.print("\n📝 最近的日志记录:")
    agent.debugger.display_logs(agent.state, limit=15)

    input("\n按 Enter 继续...")


def demo_state_management(agent: Agent):
    """演示状态管理功能"""
    console = Console()

    console.print("\n💾 4. 状态管理功能演示", style="bold green")

    # 保存状态
    state_file = "agent_state_demo.json"
    console.print(f"\n💾 保存状态到文件: {state_file}")
    agent.save_state(state_file)

    # 显示文件信息
    if os.path.exists(state_file):
        file_size = os.path.getsize(state_file)
        console.print(f"✅ 状态已保存，文件大小: {file_size} 字节")

        # 读取并显示状态文件的部分内容
        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)

        console.print("\n📋 状态文件内容预览:")
        preview_data = {
            "agent_id": state_data.get("agent_id"),
            "status": state_data.get("status"),
            "messages_count": len(state_data.get("messages", [])),
            "tool_calls_count": len(state_data.get("tool_calls", [])),
            "thoughts_count": len(state_data.get("thoughts", [])),
            "logs_count": len(state_data.get("logs", []))
        }

        table = Table(show_header=True)
        table.add_column("属性", style="cyan")
        table.add_column("值", style="green")

        for key, value in preview_data.items():
            table.add_row(key, str(value))

        console.print(table)

    input("\n按 Enter 继续...")

    # 重置状态
    console.print("\n🔄 重置 Agent 状态")
    old_id = agent.state.agent_id
    agent.reset_state()

    console.print("✅ 状态已重置")
    console.print(f"Agent ID: {agent.state.agent_id}")
    console.print(f"消息数量: {len(agent.state.messages)}")
    console.print(f"状态: {agent.state.status.value}")

    input("\n按 Enter 继续恢复状态...")

    # 恢复状态
    if os.path.exists(state_file):
        console.print(f"\n📥 从文件恢复状态: {state_file}")
        try:
            agent.load_state(state_file)
            console.print("✅ 状态已恢复")

            # 显示恢复后的状态摘要
            console.print("\n📊 恢复后的状态摘要:")
            agent.debugger.display_state_summary(agent.state)

        except Exception as e:
            console.print(f"❌ 恢复状态失败: {str(e)}")

    # 清理文件
    if os.path.exists(state_file):
        os.remove(state_file)
        console.print(f"\n🗑️  已清理临时文件: {state_file}")


def demo_advanced_features(agent: Agent):
    """演示高级功能"""
    console = Console()

    console.print("\n🚀 5. 高级功能演示", style="bold green")

    # 演示上下文管理
    console.print("\n📋 上下文管理:")
    agent.state.set_context("user_preference", "技术文档")
    agent.state.set_context("session_theme", "AI开发")
    agent.state.set_working_memory("last_calculation", 42)
    agent.state.set_working_memory("analysis_result", {"accuracy": 0.95, "confidence": "high"})

    agent.debugger.display_context(agent.state)

    # 演示推理步骤
    console.print("\n🧩 推理步骤记录:")
    agent.state.add_reasoning_step(
        "问题分析",
        "用户询问技术问题，需要提供准确的答案",
        {"complexity": "medium", "domain": "technology"}
    )
    agent.state.add_reasoning_step(
        "信息检索",
        "从知识库中搜索相关信息",
        {"sources": 3, "relevance_score": 0.89}
    )
    agent.state.add_reasoning_step(
        "答案生成",
        "基于检索到的信息生成结构化回答",
        {"format": "markdown", "length": "medium"}
    )

    # 显示最新的推理步骤
    if agent.state.reasoning_steps:
        console.print("\n📝 最新的推理步骤:")
        for step in agent.state.reasoning_steps[-3:]:
            console.print(f"• {step['step_type']}: {step['content']}")

    input("\n按 Enter 继续...")

    # 演示错误处理
    console.print("\n❌ 错误处理演示:")
    agent.state.log(LogLevel.WARNING, "这是一个警告消息", {"code": "WARN_001"})
    agent.state.log(LogLevel.ERROR, "这是一个错误消息", {"code": "ERR_001", "recoverable": True})

    console.print("\n📝 错误和警告日志:")
    agent.debugger.display_logs(agent.state, level=LogLevel.WARNING, limit=10)


def demo_performance_monitoring(agent: Agent):
    """演示性能监控"""
    console = Console()

    console.print("\n📊 6. 性能监控演示", style="bold green")

    # 显示性能统计
    console.print("\n⏱️ 性能统计:")

    total_tool_calls = len(agent.state.tool_calls)
    successful_calls = sum(1 for tc in agent.state.tool_calls if tc.result is not None)
    failed_calls = sum(1 for tc in agent.state.tool_calls if tc.error is not None)

    if total_tool_calls > 0:
        avg_time = sum(tc.execution_time or 0 for tc in agent.state.tool_calls) / total_tool_calls

        table = Table(show_header=True)
        table.add_column("指标", style="cyan")
        table.add_column("值", style="green")

        table.add_row("总工具调用次数", str(total_tool_calls))
        table.add_row("成功调用次数", str(successful_calls))
        table.add_row("失败调用次数", str(failed_calls))
        table.add_row("成功率", f"{(successful_calls/total_tool_calls)*100:.1f}%")
        table.add_row("平均执行时间", f"{avg_time:.3f}s")

        if agent.state.total_execution_time:
            table.add_row("总执行时间", f"{agent.state.total_execution_time:.3f}s")

        console.print(table)
    else:
        console.print("暂无工具调用记录")

    input("\n按 Enter 继续完整调试信息展示...")


def demo_full_debug_info(agent: Agent):
    """展示完整调试信息"""
    console = Console()

    console.print("\n🔍 7. 完整调试信息展示", style="bold green")
    agent.debugger.display_full_debug_info(agent.state)


def interactive_mode():
    """交互模式"""
    console = Console()

    console.print("\n🎮 8. 交互模式", style="bold green")
    console.print("现在您可以与 Agent 进行实时对话，输入 'quit' 退出交互模式。")

    agent = Agent(agent_id="interactive_agent", debug_mode=True)

    while True:
        try:
            console.print("\n" + "-"*50)
            user_input = input("👤 您: ")

            if user_input.lower() in ['quit', 'exit', '退出']:
                console.print("👋 再见！")
                break

            if not user_input.strip():
                continue

            # 处理用户输入
            console.print("🤖 Agent: ", end="")
            response = agent.process_user_message(user_input)
            console.print(response)

            # 询问是否查看调试信息
            debug_choice = input("\n🔍 查看调试信息? (y/n): ").lower().strip()
            if debug_choice in ['y', 'yes', '是']:
                console.print("\n📊 状态摘要:")
                agent.debugger.display_state_summary(agent.state)

        except KeyboardInterrupt:
            console.print("\n\n👋 程序被中断，再见！")
            break
        except Exception as e:
            console.print(f"\n❌ 发生错误: {str(e)}")


def main():
    """主函数"""
    console = Console()

    try:
        # 基本功能演示
        agent = demo_basic_functionality()

        # 消息处理演示
        demo_message_processing(agent)

        # 调试功能演示
        demo_debug_features(agent)

        # 状态管理演示
        demo_state_management(agent)

        # 高级功能演示
        demo_advanced_features(agent)

        # 性能监控演示
        demo_performance_monitoring(agent)

        # 完整调试信息展示
        demo_full_debug_info(agent)

        # 交互模式
        interactive_choice = input("\n🎮 是否进入交互模式? (y/n): ").lower().strip()
        if interactive_choice in ['y', 'yes', '是']:
            interactive_mode()

        console.print("\n🎉 演示完成！", style="bold blue", justify="center")
        console.print("您已经了解了 Agent 状态管理系统的所有主要功能。", style="blue")

    except KeyboardInterrupt:
        console.print("\n\n👋 演示被中断，感谢观看！")
    except Exception as e:
        console.print(f"\n❌ 演示过程中发生错误: {str(e)}")


if __name__ == "__main__":
    main()