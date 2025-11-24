#!/usr/bin/env python3
"""
ReAct Agent 演示程序

展示 ReAct (Reasoning + Acting) 的工作原理，包括：
1. 工具系统演示
2. ReAct 循环演示
3. 状态管理集成
4. 调试和观察功能
"""

import os
import sys
import json
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# 尝试导入，如果失败则显示错误
try:
    from src.day3_core.tools import ToolExecutor, calculator, get_weather, web_search, text_analyzer
    from src.day3_core.react_agent import create_react_agent
    from src.day2_framework.state import AgentState, MessageRole
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有依赖包，并且项目结构正确")
    IMPORTS_AVAILABLE = False


def demo_tools():
    """演示工具系统"""
    console = Console()

    if not IMPORTS_AVAILABLE:
        console.print("❌ 无法运行工具演示，请检查依赖安装", style="bold red")
        return

    console.print("🔧 工具系统演示", style="bold blue", justify="center")
    console.print("=" * 60, style="blue")

    tool_executor = ToolExecutor()

    # 显示可用工具
    available_tools = tool_executor.get_available_tools()
    console.print(f"🛠️ 可用工具: {', '.join(available_tools)}")

    # 演示计算器
    console.print("\n📊 计算器演示:")
    result = calculator("123 + 456")
    console.print(f"✅ 123 + 456 = {result.data['result']}")

    # 演示天气查询
    console.print("\n🌤️ 天气查询演示:")
    result = get_weather("北京")
    console.print(f"📍 北京天气: {result.data['temperature']}°C, {result.data['weather']}")

    # 演示文本分析
    console.print("\n📝 文本分析演示:")
    result = text_analyzer("这个产品真的很棒，我非常喜欢！", "sentiment")
    console.print(f"😊 情感分析: {result.data['sentiment']} (置信度: {result.data['confidence']:.2f})")

    console.print("\n✅ 工具系统演示完成")


def demo_react_concept():
    """演示 ReAct 概念"""
    console = Console()

    console.print("\n🧠 ReAct 概念演示", style="bold blue", justify="center")
    console.print("=" * 60, style="blue")

    console.print("ReAct = Reasoning + Acting")
    console.print("Agent 通过思考-行动-观察的循环来解决问题")

    # 创建模拟的 ReAct 过程
    example_query = "计算圆的面积，半径为 5"

    console.print(f"\n📝 示例问题: {example_query}")
    console.print("\n🔄 ReAct 循环过程:")

    steps = [
        {
            "step": 1,
            "thought": "用户要求计算圆的面积，公式是 π × r²。半径是5，需要计算 π × 5²。",
            "action": "calculator",
            "input": {"expression": "3.14159 * 5 * 5"},
            "observation": "计算结果: 78.53975"
        },
        {
            "step": 2,
            "thought": "已经得到了圆的面积计算结果，可以给用户最终答案。",
            "final_answer": "半径为5的圆的面积是 78.54（保留两位小数）。"
        }
    ]

    table = Table(show_header=True)
    table.add_column("步骤", style="cyan", width=6)
    table.add_column("思考", style="white", width=40)
    table.add_column("行动", style="green", width=12)
    table.add_column("结果", style="yellow", width=25)

    for step_data in steps:
        if "final_answer" in step_data:
            table.add_row(
                str(step_data["step"]),
                step_data["thought"],
                "Final Answer",
                step_data["final_answer"]
            )
        else:
            table.add_row(
                str(step_data["step"]),
                step_data["thought"],
                step_data["action"],
                step_data["observation"]
            )

    console.print(table)

    console.print("\n💡 关键概念:")
    console.print("• Thought: 分析问题，决定下一步")
    console.print("• Action: 选择并执行工具")
    console.print("• Observation: 分析工具结果")
    console.print("• Final Answer: 给出最终答案")


def demo_state_management():
    """演示状态管理集成"""
    console = Console()

    console.print("\n📊 状态管理集成演示", style="bold blue", justify="center")
    console.print("=" * 60, style="blue")

    # 创建 Agent 状态
    state = AgentState(
        agent_id="demo_react_state",
        debug_mode=True
    )

    console.print("✅ 已创建 Agent 状态")

    # 模拟 ReAct 过程中的状态变化
    console.print("\n🔄 模拟 ReAct 过程:")

    # 开始任务
    state.start_task("计算圆面积", total_steps=2)
    console.print(f"📋 任务开始: {state.current_task}")

    # 步骤 1: 思考
    state.next_step("分析问题")
    state.add_thought("需要使用计算器计算 π × 5²")
    from src.day2_framework.state import AgentStatus
    state.update_status(AgentStatus.THINKING)
    console.print(f"🧠 思考: {state.thoughts[-1]}")

    # 步骤 2: 执行工具
    state.next_step("执行计算")
    from src.day2_framework.state import ToolType
    state.add_tool_call(ToolType.CALCULATOR, "calculator", {"expression": "3.14159 * 5 * 5"})
    if state.current_tool_call:
        state.current_tool_call.start_execution()
        state.current_tool_call.finish_execution(result="78.53975")
    console.print(f"🔧 执行工具: {state.current_tool_call.tool_name}")

    # 完成
    state.complete_task(success=True)
    console.print(f"✅ 任务完成，执行时间: {state.total_execution_time:.3f}秒")

    # 显示状态摘要
    console.print("\n📊 状态摘要:")
    summary = state.get_state_summary()
    console.print(f"• 状态: {summary['status']}")
    console.print(f"• 消息数: {summary['messages_count']}")
    console.print(f"• 工具调用数: {summary['tool_calls_count']}")
    console.print(f"• 思考过程数: {summary['thoughts_count']}")


def demo_manual_react():
    """手动演示 ReAct 过程（不依赖 LLM）"""
    console = Console()

    console.print("\n🎯 手动 ReAct 演示", style="bold blue", justify="center")
    console.print("=" * 60, style="blue")

    # 创建工具执行器
    tool_executor = ToolExecutor()

    # 示例问题
    query = "北京现在天气怎么样？如果下雨，我需要带伞吗？"

    console.print(f"📝 用户问题: {query}")

    # 手动 ReAct 过程
    console.print("\n🔄 手动 ReAct 执行:")

    # Step 1: Thought
    thought1 = "用户询问北京天气，并根据天气情况决定是否需要带伞。我需要先查询北京当前的天气状况。"
    console.print(f"\n步骤 1 - 💭 Thought: {thought1}")

    # Step 1: Action
    action1 = "get_weather"
    action_input1 = {"city": "北京"}
    console.print(f"步骤 1 - 🔧 Action: {action1}")
    console.print(f"步骤 1 - 📥 Action Input: {action_input1}")

    # Step 1: Observation
    result1 = tool_executor.execute(action1, action_input1)
    observation1 = f"北京当前天气：{result1.data['temperature']}°C，{result1.data['weather']}"
    console.print(f"步骤 1 - 👀 Observation: {observation1}")

    # Step 2: Thought
    if "雨" in result1.data['weather']:
        thought2 = "北京正在下雨，用户确实需要带伞。"
        final_answer = "北京现在正在下雨，温度25°C，建议您带伞出门。"
    else:
        thought2 = "北京没有下雨，用户不需要带伞。"
        final_answer = f"北京现在是{result1.data['weather']}，温度{result1.data['temperature']}°C，不需要带伞。"

    console.print(f"\n步骤 2 - 💭 Thought: {thought2}")
    console.print(f"步骤 2 - ✅ Final Answer: {final_answer}")

    console.print(f"\n🎉 ReAct 过程完成！")
    console.print(f"最终答案: {final_answer}")


def demo_debug_features():
    """演示调试功能"""
    console = Console()

    console.print("\n🔍 调试功能演示", style="bold blue", justify="center")
    console.print("=" * 60, style="blue")

    # 创建 ReAct Agent
    agent = create_react_agent("debug_demo", debug_mode=True, max_steps=1)

    console.print("✅ 创建了调试模式的 ReAct Agent")

    # 显示可用工具信息
    console.print(f"\n🛠️ 可用工具:")
    for tool_name in agent.get_available_tools():
        tool_info = agent.get_tool_info(tool_name)
        if tool_info:
            console.print(f"• {tool_name}: {tool_info['description']}")

    # 显示初始状态
    console.print(f"\n📊 初始状态:")
    state = agent.get_agent_state()
    console.print(f"• Agent ID: {state.agent_id}")
    console.print(f"• 状态: {state.status.value}")
    console.print(f"• 调试模式: {state.debug_mode}")

    console.print("\n💡 调试功能包括:")
    console.print("• 完整的执行轨迹追踪")
    console.print("• 详细的状态变化日志")
    console.print("• 工具调用时间统计")
    console.print("• 思考过程记录")
    console.print("• 状态持久化和恢复")


def main():
    """主演示函数"""
    console = Console()

    console.print("🎯 Day 3 ReAct Agent 完整演示", style="bold blue", justify="center")
    console.print("=" * 80, style="blue")
    console.print("展示 ReAct (Reasoning + Acting) 智能代理的完整功能", style="italic")
    console.print()

    # 演示各个组件
    demo_tools()
    demo_react_concept()
    demo_state_management()
    demo_manual_react()
    demo_debug_features()

    console.print("\n🎉 演示完成！", style="bold green", justify="center")
    console.print("您已经了解了 ReAct Agent 的所有核心功能", style="italic")

    console.print("\n📚 学习要点:")
    console.print("1. ReAct 将 LLM 从'说话者'变成了'行动者'")
    console.print("2. Thought → Action → Observation → Final Answer 的循环")
    console.print("3. 工具系统提供了强大的执行能力")
    console.print("4. 状态管理提供了完整的调试和观察能力")
    console.print("5. 本质上是：LLM输出文本 → Python解析 → 执行函数 → 结果回传")


if __name__ == "__main__":
    main()