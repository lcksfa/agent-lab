#!/usr/bin/env python3
"""
ReAct Agent 测试套件

全面测试 ReAct 引擎和工具系统的功能
"""

import os
import sys
import json
import tempfile
import unittest
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.day3_core.tools import (
    ToolResult, calculator, web_search, get_weather,
    text_analyzer, current_time, memory_store, ToolExecutor
)
from src.day3_core.engine import ReActEngine, ReActStep, create_react_engine
from src.day3_core.react_agent import create_react_agent
from src.day2_framework.state import AgentState, AgentStatus, MessageRole


class TestTools(unittest.TestCase):
    """测试工具系统"""

    def setUp(self):
        """测试前准备"""
        self.tool_executor = ToolExecutor()

    def test_calculator_success(self):
        """测试计算器成功情况"""
        result = calculator("123 + 456")

        self.assertTrue(result.success)
        self.assertEqual(result.data["result"], 579)
        self.assertIsNone(result.error)

    def test_calculator_invalid_expression(self):
        """测试计算器无效表达式"""
        result = calculator("invalid expression")

        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)

    def test_get_weather_known_city(self):
        """测试天气查询已知城市"""
        result = get_weather("北京")

        self.assertTrue(result.success)
        self.assertIn("temperature", result.data)
        self.assertIn("weather", result.data)

    def test_get_weather_unknown_city(self):
        """测试天气查询未知城市"""
        result = get_weather("未知城市")

        self.assertTrue(result.success)
        self.assertEqual(result.data["city"], "未知城市")

    def test_text_analyzer_sentiment(self):
        """测试文本分析情感分析"""
        result = text_analyzer("这个产品真的很棒！", "sentiment")

        self.assertTrue(result.success)
        self.assertIn("sentiment", result.data)
        self.assertIn("confidence", result.data)

    def test_text_analyzer_keywords(self):
        """测试文本分析关键词提取"""
        result = text_analyzer("Python编程语言很强大", "keywords")

        self.assertTrue(result.success)
        self.assertIn("keywords", result.data)

    def test_current_time(self):
        """测试时间查询"""
        result = current_time()

        self.assertTrue(result.success)
        self.assertIn("current_time", result.data)

    def test_memory_store_set_get(self):
        """测试内存存储设置和获取"""
        # 设置值
        set_result = memory_store("test_key", "test_value", "set")
        self.assertTrue(set_result.success)

        # 获取值
        get_result = memory_store("test_key", "", "get")
        self.assertTrue(get_result.success)
        self.assertTrue(get_result.data["found"])
        self.assertEqual(get_result.data["value"], "test_value")

    def test_memory_store_delete(self):
        """测试内存存储删除"""
        # 先设置值
        memory_store("test_key_delete", "test_value", "set")

        # 删除值
        delete_result = memory_store("test_key_delete", "", "delete")
        self.assertTrue(delete_result.success)

        # 验证删除
        get_result = memory_store("test_key_delete", "", "get")
        self.assertTrue(get_result.success)
        self.assertFalse(get_result.data["found"])

    def test_tool_executor_execute_success(self):
        """测试工具执行器成功执行"""
        result = self.tool_executor.execute("calculator", {"expression": "10 * 5"})

        self.assertTrue(result.success)
        self.assertEqual(result.data["result"], 50)

    def test_tool_executor_execute_unknown_tool(self):
        """测试工具执行器未知工具"""
        result = self.tool_executor.execute("unknown_tool", {})

        self.assertFalse(result.success)
        self.assertIn("未知工具", result.error)

    def test_tool_executor_execute_invalid_params(self):
        """测试工具执行器无效参数"""
        result = self.tool_executor.execute("calculator", {})

        self.assertFalse(result.success)
        self.assertIn("参数错误", result.error)


class TestReActEngine(unittest.TestCase):
    """测试 ReAct 引擎"""

    def setUp(self):
        """测试前准备"""
        self.engine = create_react_engine("test_engine", max_steps=3)

    def test_engine_initialization(self):
        """测试引擎初始化"""
        self.assertIsNotNone(self.engine.agent_id)
        self.assertEqual(self.engine.max_steps, 3)
        self.assertGreater(len(self.engine.available_tools), 0)
        self.assertIsNotNone(self.engine.system_prompt)

    def test_parse_response_with_final_answer(self):
        """测试解析包含最终答案的响应"""
        response = """**Thought**: 我已经计算完成

**Final Answer**: 最终答案: 42"""

        thought, action, action_input, is_final = self.engine._parse_response(response)

        self.assertIsNotNone(thought)
        self.assertIsNone(action)
        self.assertIsNone(action_input)
        self.assertTrue(is_final)

    def test_parse_response_with_action(self):
        """测试解析包含动作的响应"""
        response = """**Thought**: 需要计算

**Action**: calculator

**Action Input**: {"expression": "10 + 20"}"""

        thought, action, action_input, is_final = self.engine._parse_response(response)

        self.assertIsNotNone(thought)
        self.assertEqual(action, "calculator")
        self.assertIsNotNone(action_input)
        self.assertFalse(is_final)

    def test_parse_response_invalid_json(self):
        """测试解析包含无效 JSON 的响应"""
        response = """**Thought**: 需要计算

**Action**: calculator

**Action Input**: {'expression': '10 + 20'}"""  # 单引号 JSON

        thought, action, action_input, is_final = self.engine._parse_response(response)

        self.assertIsNotNone(thought)
        self.assertEqual(action, "calculator")
        self.assertIsNotNone(action_input)
        self.assertFalse(is_final)

    def test_build_context_prompt_empty_history(self):
        """测试构建空历史记录的上下文提示"""
        user_query = "测试查询"
        context = self.engine._build_context_prompt(user_query)

        self.assertIn(user_query, context)
        self.assertNotIn("之前的对话步骤", context)

    def test_build_context_prompt_with_history(self):
        """测试构建包含历史记录的上下文提示"""
        # 添加一个步骤到历史
        step = ReActStep(1, "测试思考", "calculator", {"expression": "1+1"}, "结果: 2")
        self.engine.steps.append(step)

        user_query = "测试查询"
        context = self.engine._build_context_prompt(user_query)

        self.assertIn(user_query, context)
        self.assertIn("之前的对话步骤", context)
        self.assertIn("测试思考", context)

    def test_format_observation_success(self):
        """测试格式化成功观察结果"""
        tool_result = ToolResult(True, {"result": 42, "unit": "items"})
        observation = self.engine._format_observation(tool_result)

        self.assertIn("工具执行成功", observation)
        self.assertIn("result: 42", observation)

    def test_format_observation_failure(self):
        """测试格式化失败观察结果"""
        tool_result = ToolResult(False, error="计算错误")
        observation = self.engine._format_observation(tool_result)

        self.assertIn("工具执行失败", observation)
        self.assertIn("计算错误", observation)

    def test_get_execution_summary(self):
        """测试获取执行摘要"""
        # 添加一个步骤
        step = ReActStep(1, "测试思考", "calculator", {"expression": "1+1"}, "结果: 2")
        self.engine.steps.append(step)
        self.engine.final_answer = "最终答案"

        summary = self.engine.get_execution_summary()

        self.assertEqual(summary["agent_id"], self.engine.agent_id)
        self.assertEqual(summary["total_steps"], 1)
        self.assertFalse(summary["is_complete"])  # 手动设置，引擎可能不认为完成
        self.assertEqual(summary["final_answer"], "最终答案")


class TestReActAgent(unittest.TestCase):
    """测试 ReAct Agent"""

    def setUp(self):
        """测试前准备"""
        self.agent = create_react_agent("test_agent", debug_mode=True, max_steps=2)

    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        self.assertIsNotNone(self.agent.agent)
        self.assertIsNotNone(self.agent.react_engine)
        self.assertTrue(self.agent.agent.state.debug_mode)
        self.assertEqual(self.agent.react_engine.max_steps, 2)

    def test_get_available_tools(self):
        """测试获取可用工具"""
        tools = self.agent.get_available_tools()

        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        self.assertIn("calculator", tools)

    def test_get_tool_info(self):
        """测试获取工具信息"""
        info = self.agent.get_tool_info("calculator")

        self.assertIsNotNone(info)
        self.assertIn("name", info)
        self.assertIn("description", info)
        self.assertIn("parameters", info)

    def test_get_tool_info_unknown(self):
        """测试获取未知工具信息"""
        info = self.agent.get_tool_info("unknown_tool")

        self.assertIsNone(info)

    def test_get_agent_state(self):
        """测试获取 Agent 状态"""
        state = self.agent.get_agent_state()

        self.assertIsNotNone(state)
        self.assertEqual(state.agent_id, "test_agent")
        self.assertTrue(state.debug_mode)

    def test_reset(self):
        """测试重置 Agent"""
        # 添加一些状态
        initial_thoughts = len(self.agent.agent.state.thoughts)
        self.agent.agent.state.add_thought("测试思考")
        self.agent.react_engine.current_step = 1
        self.agent.react_engine.steps.append(ReActStep(1, "测试"))

        # 重置
        self.agent.reset()

        # 验证重置结果
        # 重置后 thoughts 会清空（重置日志不计入 thoughts）
        self.assertEqual(len(self.agent.agent.state.thoughts), 0)
        self.assertEqual(self.agent.react_engine.current_step, 0)
        self.assertEqual(len(self.agent.react_engine.steps), 0)
        self.assertFalse(self.agent.react_engine.is_complete)

    def test_save_state(self):
        """测试保存状态"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            # 添加一些状态
            self.agent.agent.state.add_thought("测试思考")

            # 保存状态
            self.agent.save_state(temp_file)

            # 验证文件存在
            self.assertTrue(os.path.exists(temp_file))

            # 验证 ReAct 状态文件
            react_file = temp_file.replace('.json', '_react.json')
            self.assertTrue(os.path.exists(react_file))

        finally:
            # 清理文件
            for file_path in [temp_file, temp_file.replace('.json', '_react.json')]:
                if os.path.exists(file_path):
                    os.remove(file_path)


class TestReActIntegration(unittest.TestCase):
    """ReAct 集成测试"""

    def test_manual_react_process(self):
        """测试手动 ReAct 过程"""
        engine = create_react_engine("integration_test", max_steps=5)

        # 模拟手动 ReAct 过程
        user_query = "计算圆的面积，半径为3"

        # 步骤 1: 思考并执行
        step1 = ReActStep(
            step_number=1,
            thought="需要计算圆的面积，公式是 π × r²，半径是3",
            action="calculator",
            action_input={"expression": "3.14159 * 3 * 3"},
        )

        # 执行工具
        tool_result = engine.tool_executor.execute(step1.action, step1.action_input)
        step1.tool_result = tool_result
        step1.observation = engine._format_observation(tool_result)

        engine.steps.append(step1)

        # 步骤 2: 最终答案
        if tool_result.success and tool_result.data.get("result"):
            area = tool_result.data["result"]
            final_answer = f"半径为3的圆的面积约为 {area:.2f}"

            step2 = ReActStep(
                step_number=2,
                thought=f"计算完成，圆的面积是 {area}",
                observation=final_answer
            )
            engine.steps.append(step2)
            engine.final_answer = final_answer
            engine.is_complete = True

        # 验证结果
        self.assertTrue(engine.is_complete)
        self.assertEqual(len(engine.steps), 2)
        self.assertIsNotNone(engine.final_answer)
        self.assertIn("面积", engine.final_answer)

    def test_complex_multi_step_react(self):
        """测试复杂多步骤 ReAct 过程"""
        engine = create_react_engine("complex_test", max_steps=5)

        # 模拟复杂任务：计算并存储结果，然后再次查询
        steps = [
            {
                "thought": "用户要计算100*200并存储结果",
                "action": "calculator",
                "input": {"expression": "100 * 200"},
                "memory_key": "calculation_result"
            },
            {
                "thought": "已经计算并存储了结果",
                "action": "memory_store",
                "input": {"key": "calculation_result", "value": "20000", "operation": "set"},
                "final_answer": "计算完成：100 × 200 = 20000，结果已存储到内存中"
            }
        ]

        # 执行步骤
        for i, step_data in enumerate(steps, 1):
            if step_data.get("final_answer"):
                # 最终答案步骤
                step = ReActStep(
                    step_number=i,
                    thought=step_data["thought"],
                    observation=step_data["final_answer"]
                )
                engine.final_answer = step_data["final_answer"]
                engine.is_complete = True
            else:
                # 工具执行步骤
                step = ReActStep(
                    step_number=i,
                    thought=step_data["thought"],
                    action=step_data["action"],
                    action_input=step_data["input"]
                )

                tool_result = engine.tool_executor.execute(step.action, step.action_input)
                step.tool_result = tool_result
                step.observation = engine._format_observation(tool_result)

            engine.steps.append(step)

        # 验证结果
        self.assertTrue(engine.is_complete)
        self.assertEqual(len(engine.steps), 2)
        self.assertIn("20000", engine.final_answer)


def run_comprehensive_test():
    """运行综合测试"""
    from rich.console import Console
    console = Console()

    console.print("🧪 开始 ReAct Agent 综合测试", style="bold blue")
    console.print("=" * 60, style="blue")

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    test_classes = [
        TestTools,
        TestReActEngine,
        TestReActAgent,
        TestReActIntegration
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出结果摘要
    console.print(f"\n📊 测试结果摘要:")
    console.print(f"总测试数: {result.testsRun}")
    console.print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    console.print(f"失败: {len(result.failures)}")
    console.print(f"错误: {len(result.errors)}")
    console.print(f"跳过: {len(result.skipped)}")

    if result.wasSuccessful():
        console.print("\n✅ 所有测试通过！ReAct Agent 工作正常。", style="bold green")
        return True
    else:
        console.print("\n❌ 部分测试失败，请检查问题。", style="bold red")
        return False


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)