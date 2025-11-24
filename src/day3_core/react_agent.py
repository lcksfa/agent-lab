"""
ReAct Agent - 完整的 ReAct 智能代理

集成 Day2 状态管理系统的 ReAct Agent，提供完整的 Agent 能力。
"""

import os
import sys
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.day2_framework.state import Agent
from .engine import ReActEngine, create_react_engine
from rich.console import Console


class ReActAgent:
    """
    集成 ReAct 引擎的完整 Agent

    结合了：
    - Day2 的状态管理系统（观察和调试）
    - Day3 的 ReAct 引擎（思考和行动）
    """

    def __init__(self, agent_id: str = None, debug_mode: bool = True, ai_provider: str = "deepseek", max_steps: int = 10):
        # 创建基础 Agent（Day2）
        self.agent = Agent(agent_id=agent_id, debug_mode=debug_mode, ai_provider=ai_provider)

        # 创建 ReAct 引擎（Day3）
        self.react_engine = create_react_engine(
            agent_id=agent_id,
            ai_provider=ai_provider,
            max_steps=max_steps
        )

        # 集成状态管理
        self.react_engine.set_state_manager(self.agent.state)

        self.console = Console()

        self.console.print("🤖 ReAct Agent 已初始化", style="bold green")
        self.console.print(f"🆔 Agent ID: {self.agent.state.agent_id}")
        self.console.print(f"🛠️ 可用工具数: {len(self.react_engine.available_tools)}")
        self.console.print(f"🎯 最大步数: {max_steps}")

    def process_query(self, user_query: str) -> str:
        """
        处理用户查询的主要接口

        Args:
            user_query (str): 用户查询

        Returns:
            str: 最终答案
        """
        self.console.print(f"\n🚀 ReAct Agent 处理查询", style="bold blue")
        self.console.print(f"📝 用户问题: {user_query}")
        self.console.print("=" * 80, style="blue")

        try:
            # 使用 ReAct 引擎处理查询
            result = self.react_engine.process(user_query)

            # 显示执行轨迹
            self.react_engine.display_execution_trace()

            # 显示状态摘要
            self.console.print(f"\n📊 状态摘要:")
            self.agent.debugger.display_state_summary(self.agent.state)

            return result

        except Exception as e:
            error_msg = f"查询处理失败: {str(e)}"
            self.console.print(f"❌ {error_msg}", style="red")
            return f"抱歉，处理您的查询时遇到了问题: {error_msg}"

    def get_agent_state(self):
        """获取 Agent 状态"""
        return self.agent.state

    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        react_summary = self.react_engine.get_execution_summary()
        state_summary = self.agent.state.get_state_summary()

        return {
            "react_engine": react_summary,
            "agent_state": state_summary
        }

    def display_full_debug_info(self):
        """显示完整调试信息"""
        self.console.print("\n🔍 完整调试信息", style="bold blue")
        self.console.print("=" * 80, style="blue")

        # Agent 状态信息
        self.agent.debugger.display_full_debug_info(self.agent.state)

        # ReAct 执行轨迹
        self.react_engine.display_execution_trace()

    def reset(self):
        """重置 Agent 状态"""
        self.agent.reset_state()
        self.react_engine.current_step = 0
        self.react_engine.steps = []
        self.react_engine.is_complete = False
        self.react_engine.final_answer = None

        self.console.print("🔄 Agent 已重置", style="green")

    def save_state(self, filepath: str):
        """保存 Agent 状态到文件"""
        self.agent.save_state(filepath)

        # 同时保存 ReAct 执行轨迹
        import json
        react_filepath = filepath.replace('.json', '_react.json')
        with open(react_filepath, 'w', encoding='utf-8') as f:
            json.dump(self.react_engine.get_execution_summary(), f, ensure_ascii=False, indent=2)

        self.console.print(f"💾 状态已保存到: {filepath}")
        self.console.print(f"💾 ReAct 轨迹已保存到: {react_filepath}")

    def get_available_tools(self) -> list:
        """获取可用工具列表"""
        return self.react_engine.available_tools

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具信息"""
        return self.react_engine.tool_executor.get_tool_schema(tool_name)


def create_react_agent(agent_id: str = None, debug_mode: bool = True, ai_provider: str = "deepseek", max_steps: int = 10) -> ReActAgent:
    """创建 ReAct Agent 实例"""
    return ReActAgent(
        agent_id=agent_id,
        debug_mode=debug_mode,
        ai_provider=ai_provider,
        max_steps=max_steps
    )


if __name__ == "__main__":
    # 测试 ReAct Agent
    console = Console()

    console.print("🧪 测试 ReAct Agent", style="bold blue")
    console.print("=" * 60, style="blue")

    # 创建 Agent
    agent = create_react_agent("test_react_agent", debug_mode=True, max_steps=5)

    # 测试查询
    test_queries = [
        "计算 123 * 456 等于多少？",
        "查询北京今天的天气情况",
        "现在几点了？"
    ]

    for i, query in enumerate(test_queries, 1):
        console.print(f"\n🔍 测试查询 {i}: {query}", style="bold yellow")
        console.print("-" * 50, style="yellow")

        result = agent.process_query(query)
        console.print(f"✅ 最终答案: {result}", style="bold green")

        if i < len(test_queries):
            input("\n按 Enter 继续下一个测试...")

    # 显示完整摘要
    console.print("\n📊 执行摘要:", style="bold blue")
    summary = agent.get_execution_summary()
    console.print(f"总步骤数: {summary['react_engine']['total_steps']}")
    console.print(f"是否完成: {summary['react_engine']['is_complete']}")

    console.print("\n✅ ReAct Agent 测试完成", style="bold green")