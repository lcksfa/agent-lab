#!/usr/bin/env python3
"""
Day 2 Agent 状态管理交互式演示

一个简单易用的交互式演示，展示 Agent 状态管理系统的核心功能
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.day2_framework.state import Agent


def main():
    """交互式演示主函数"""
    print("🎯 Day 2 Agent 状态管理系统 - 交互式演示")
    print("=" * 60)
    print("这是一个基于 Pydantic 的 Agent 状态管理系统演示")
    print("Agent 本质上是一个状态机，在思考、执行工具、等待结果之间流转")
    print()

    # 创建 Agent
    agent = Agent("interactive_demo_agent", debug_mode=True)

    print("✅ Agent 已创建")
    print(f"Agent ID: {agent.state.agent_id}")
    print(f"调试模式: {agent.state.debug_mode}")
    print()

    # 演示菜单
    demo_messages = [
        "你好，请介绍一下你的功能",
        "帮我计算 25 + 37",
        "分析一下机器学习的发展趋势",
        "搜索 Python 的最佳编程实践",
        "展示一个简单的状态管理示例"
    ]

    print("📝 可用的测试消息:")
    for i, msg in enumerate(demo_messages, 1):
        print(f"  {i}. {msg}")
    print("  6. 自定义输入")
    print("  0. 退出")

    while True:
        print("\n" + "-" * 50)
        try:
            choice = input("请选择 (0-6): ").strip()

            if choice == "0":
                print("👋 再见！")
                break

            if choice in ["1", "2", "3", "4", "5"]:
                message = demo_messages[int(choice) - 1]
            elif choice == "6":
                message = input("请输入您的消息: ").strip()
                if not message:
                    continue
            else:
                print("❌ 无效选择，请重试")
                continue

            print(f"\n👤 用户: {message}")

            # 处理消息
            print("🤖 Agent: ", end="")
            response = agent.process_user_message(message)
            print(response)

            # 显示状态摘要
            print(f"\n📊 当前状态:")
            summary = agent.state.get_state_summary()
            print(f"  状态: {summary['status']}")
            print(f"  任务: {summary['current_task']}")
            print(f"  进度: {summary['progress']}")
            print(f"  消息数: {summary['messages_count']}")
            print(f"  工具调用数: {summary['tool_calls_count']}")

        except KeyboardInterrupt:
            print("\n\n👋 程序被中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    main()