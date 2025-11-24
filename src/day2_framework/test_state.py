#!/usr/bin/env python3
"""
Agent 状态管理系统测试脚本

非交互式测试，验证所有核心功能
"""

import os
import sys
import json
import tempfile
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.day2_framework.state import (
    Agent, AgentState, StateDebugger, MessageRole, LogLevel,
    ToolType, AgentStatus
)


def test_agent_creation():
    """测试 Agent 创建"""
    print("🧪 测试 Agent 创建...")

    agent = Agent(agent_id="test_agent", debug_mode=True)

    assert agent.state.agent_id == "test_agent"
    assert agent.state.status == AgentStatus.IDLE
    assert agent.state.debug_mode == True
    assert len(agent.state.messages) == 0
    assert len(agent.state.tool_calls) == 0
    assert len(agent.state.thoughts) == 0

    print("✅ Agent 创建测试通过")
    return agent


def test_message_processing(agent):
    """测试消息处理"""
    print("\n🧪 测试消息处理...")

    test_messages = [
        "你好，请介绍一下自己",
        "帮我计算 10 + 20",
        "分析一下Python编程的特点"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"  处理消息 {i}: {message[:20]}...")
        response = agent.process_user_message(message)

        assert response is not None
        assert len(response) > 0
        assert len(agent.state.messages) >= i * 2  # 每条消息产生用户和助手两条记录
        assert len(agent.state.tool_calls) >= i

    print(f"✅ 消息处理测试通过，共处理 {len(test_messages)} 条消息")
    print(f"  - 总消息数: {len(agent.state.messages)}")
    print(f"  - 工具调用数: {len(agent.state.tool_calls)}")
    print(f"  - 思考过程数: {len(agent.state.thoughts)}")


def test_state_management(agent):
    """测试状态管理"""
    print("\n🧪 测试状态管理...")

    # 测试上下文管理
    agent.state.set_context("test_key", "test_value")
    assert agent.state.get_context("test_key") == "test_value"

    # 测试工作记忆
    agent.state.set_working_memory("memory_key", "memory_value")
    assert agent.state.get_working_memory("memory_key") == "memory_value"

    # 测试思考过程
    agent.state.add_thought("这是一个测试思考")
    assert len(agent.state.thoughts) > 0

    # 测试日志
    agent.state.log(LogLevel.INFO, "测试日志消息")
    assert len(agent.state.logs) > 0

    print("✅ 状态管理测试通过")


def test_state_serialization(agent):
    """测试状态序列化"""
    print("\n🧪 测试状态序列化...")

    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name

    try:
        # 保存状态
        agent.save_state(temp_file)
        assert os.path.exists(temp_file)

        # 读取保存的文件
        with open(temp_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        assert saved_data['agent_id'] == agent.state.agent_id
        assert saved_data['debug_mode'] == agent.state.debug_mode
        assert len(saved_data['messages']) == len(agent.state.messages)

        # 创建新 Agent 并加载状态
        new_agent = Agent("new_agent", debug_mode=True)
        original_id = new_agent.state.agent_id
        original_message_count = len(new_agent.state.messages)

        new_agent.load_state(temp_file)

        # 验证状态已恢复
        assert new_agent.state.agent_id == agent.state.agent_id
        assert new_agent.state.agent_id != original_id  # 应该被覆盖
        assert len(new_agent.state.messages) == len(agent.state.messages)
        assert len(new_agent.state.messages) != original_message_count

        print("✅ 状态序列化测试通过")

    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_error_handling(agent):
    """测试错误处理"""
    print("\n🧪 测试错误处理...")

    initial_error_count = len(agent.state.errors)

    # 添加错误日志
    agent.state.log(LogLevel.ERROR, "测试错误消息", {"code": "TEST_ERROR"})
    assert len(agent.state.errors) == initial_error_count + 1

    # 添加警告日志（不应该增加错误计数）
    agent.state.log(LogLevel.WARNING, "测试警告消息")
    assert len(agent.state.errors) == initial_error_count + 1

    print("✅ 错误处理测试通过")


def test_debugger(agent):
    """测试调试器"""
    print("\n🧪 测试调试器...")

    debugger = StateDebugger()

    # 创建临时 console 来捕获输出
    from rich.console import Console
    from io import StringIO

    string_io = StringIO()
    test_console = Console(file=string_io)
    test_debugger = StateDebugger(test_console)

    # 测试各种显示方法
    test_debugger.display_state_summary(agent.state)
    test_debugger.display_messages(agent.state, limit=2)
    test_debugger.display_thoughts(agent.state, limit=2)
    test_debugger.display_logs(agent.state, limit=2)

    # 检查是否有输出
    output = string_io.getvalue()
    assert len(output) > 0

    print("✅ 调试器测试通过")


def test_agent_reset():
    """测试 Agent 重置"""
    print("\n🧪 测试 Agent 重置...")

    # 创建有状态的 Agent
    agent = Agent("reset_test_agent")
    agent.process_user_message("测试消息")

    original_message_count = len(agent.state.messages)
    original_thought_count = len(agent.state.thoughts)
    original_log_count = len(agent.state.logs)

    # 重置状态
    agent.reset_state()

    # 验证状态已重置
    assert len(agent.state.messages) == 0
    assert len(agent.state.thoughts) == 0
    assert len(agent.state.logs) == 1  # 只有重置日志

    # Agent ID 应该保持不变
    assert agent.state.agent_id == "reset_test_agent"

    print("✅ Agent 重置测试通过")


def test_performance_metrics():
    """测试性能指标"""
    print("\n🧪 测试性能指标...")

    agent = Agent("performance_test")

    # 处理一些消息
    start_time = datetime.now()
    agent.process_user_message("性能测试消息1")
    agent.process_user_message("性能测试消息2")
    end_time = datetime.now()

    # 检查执行时间
    if agent.state.total_execution_time:
        execution_time = agent.state.total_execution_time
        assert execution_time >= 0
        print(f"  - 总执行时间: {execution_time:.3f}秒")

    # 检查工具调用时间
    if agent.state.tool_calls:
        for tool_call in agent.state.tool_calls:
            if tool_call.execution_time:
                assert tool_call.execution_time >= 0
                print(f"  - 工具 {tool_call.tool_name} 执行时间: {tool_call.execution_time:.3f}秒")

    print("✅ 性能指标测试通过")


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始 Agent 状态管理系统测试")
    print("=" * 60)

    try:
        # 1. 测试 Agent 创建
        agent = test_agent_creation()

        # 2. 测试消息处理
        test_message_processing(agent)

        # 3. 测试状态管理
        test_state_management(agent)

        # 4. 测试状态序列化
        test_state_serialization(agent)

        # 5. 测试错误处理
        test_error_handling(agent)

        # 6. 测试调试器
        test_debugger(agent)

        # 7. 测试 Agent 重置
        test_agent_reset()

        # 8. 测试性能指标
        test_performance_metrics()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("✅ Agent 状态管理系统工作正常")

        # 显示最终状态摘要
        print("\n📊 最终状态摘要:")
        debugger = StateDebugger()
        debugger.display_state_summary(agent.state)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)