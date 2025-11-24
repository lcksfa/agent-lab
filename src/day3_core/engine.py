"""
ReAct Engine - Agent 的"大脑"

实现 ReAct (Reasoning + Acting) 核心循环逻辑。
这是最关键的部分 - Agent 的心脏。

ReAct 循环步骤：
1. **Thought (思考)**：分析当前情况，决定下一步行动
2. **Action (行动)**：生成工具调用指令
3. **Observation (观察)**：执行工具，获得结果
4. **Answer (回答)**：基于观察结果生成最终回复

本质上就是：LLM 输出文本 → Python 解析文本 → Python 执行函数 → 把结果拼回 Prompt → 再发给 LLM
"""

import json
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# 导入工具和状态管理
from .tools import ToolExecutor, get_tools_description, ToolResult
try:
    from ..day2_framework.state import Agent, AgentState, MessageRole
    from ..ai_service import get_ai_service
except ImportError:
    # 如果导入失败，创建占位符
    def get_ai_service(provider="deepseek"):
        class MockAIService:
            def chat_completion(self, messages, **kwargs):
                return {
                    "success": True,
                    "content": "模拟AI回复：这是一个ReAct思考过程的结果。",
                    "usage": {"total_tokens": 150}
                }
        return MockAIService()

console = Console()


@dataclass
class ReActStep:
    """ReAct 步骤记录"""
    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    tool_result: Optional[ToolResult] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "step_number": self.step_number,
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
            "tool_result": self.tool_result.to_dict() if self.tool_result else None,
            "timestamp": self.timestamp
        }


class ReActEngine:
    """ReAct 引擎 - Agent 的核心大脑"""

    def __init__(self, agent_id: str = None, ai_provider: str = "deepseek", max_steps: int = 10):
        # 初始化组件
        self.agent_id = agent_id or f"react_agent_{int(time.time())}"
        self.ai_service = get_ai_service(ai_provider)
        self.tool_executor = ToolExecutor()
        self.max_steps = max_steps

        # 状态管理
        self.state = None  # 将在集成 day2 时设置

        # ReAct 循环状态
        self.current_step = 0
        self.steps: List[ReActStep] = []
        self.is_complete = False
        self.final_answer = None

        # 可用工具
        self.available_tools = self.tool_executor.get_available_tools()

        # 构建系统提示词
        self.system_prompt = self._build_system_prompt()

        console.print(f"🤖 ReAct 引擎已初始化", style="green")
        console.print(f"Agent ID: {self.agent_id}")
        console.print(f"可用工具数: {len(self.available_tools)}")

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        tools_desc = get_tools_description()

        prompt = f"""你是一个具有推理和行动能力的 AI 助手。请使用 ReAct (Reasoning + Acting) 方法来回答用户的问题。

## 可用工具：
{tools_desc}

## ReAct 工作流程：
1. **Thought (思考)**：分析当前情况，确定需要什么信息或采取什么行动
2. **Action (行动)**：选择并调用合适的工具
3. **Observation (观察)**：分析工具返回的结果
4. **循环**：重复直到能够给出最终答案
5. **Final Answer (最终答案)**：基于所有观察结果给出完整回答

## 回答格式要求：
每个步骤必须严格按照以下格式：

**Thought**: [你的思考过程]
**Action**: [工具名称]
**Action Input**: {{参数1: "值1", 参数2: "值2"}}
**Observation**: [工具执行结果]

当你认为可以回答用户问题时，使用：
**Final Answer**: [最终答案]

## 重要提醒：
- 每个 "Thought" 后面必须跟着 "Action" 或 "Final Answer"
- "Action Input" 必须是有效的 JSON 格式
- 工具名称必须完全匹配可用工具列表
- 仔细观察工具结果，用于指导下一步思考
- 当有足够信息时，给出 "Final Answer"

现在请开始回答用户的问题。"""

        return prompt

    def _parse_response(self, response: str) -> Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]], bool]:
        """
        解析 LLM 响应，提取 Thought, Action, Action Input

        Returns:
            Tuple[thought, action, action_input, is_final_answer]
        """
        try:
            # 查找 Thought
            thought_match = re.search(r'\*\*Thought\*\*:\s*(.+?)(?=\*\*(?:Action|Final Answer)\*\*)', response, re.DOTALL)
            thought = thought_match.group(1).strip() if thought_match else None

            # 查找 Final Answer
            final_answer_match = re.search(r'\*\*Final Answer\*\*:\s*(.+)', response, re.DOTALL)
            if final_answer_match:
                return thought, None, None, True

            # 查找 Action
            action_match = re.search(r'\*\*Action\*\*:\s*(.+?)(?=\*\*Action Input\*\*)', response, re.DOTALL)
            action = action_match.group(1).strip() if action_match else None

            # 查找 Action Input
            action_input_match = re.search(r'\*\*Action Input\*\*:\s*(.+)', response, re.DOTALL)
            action_input = None
            if action_input_match:
                try:
                    action_input = json.loads(action_input_match.group(1).strip())
                except json.JSONDecodeError:
                    # 尝试修复常见的 JSON 格式问题
                    json_str = action_input_match.group(1).strip()
                    # 替换单引号为双引号
                    json_str = json_str.replace("'", '"')
                    try:
                        action_input = json.loads(json_str)
                    except:
                        action_input = {"raw_input": json_str}

            return thought, action, action_input, False

        except Exception as e:
            console.print(f"❌ 解析响应时出错: {str(e)}", style="red")
            return None, None, None, False

    def _build_context_prompt(self, user_query: str) -> str:
        """构建包含历史步骤的上下文提示词"""
        context_parts = [f"用户问题: {user_query}"]

        if self.steps:
            context_parts.append("\n之前的对话步骤:")
            for step in self.steps:
                step_text = f"步骤 {step.step_number}:\n"
                step_text += f"Thought: {step.thought}\n"

                if step.action:
                    step_text += f"Action: {step.action}\n"
                    step_text += f"Action Input: {json.dumps(step.action_input, ensure_ascii=False)}\n"

                if step.observation:
                    step_text += f"Observation: {step.observation}\n"

                context_parts.append(step_text)

        return "\n".join(context_parts)

    def _execute_tool_action(self, action: str, action_input: Dict[str, Any]) -> ToolResult:
        """执行工具动作"""
        if action not in self.available_tools:
            return ToolResult(False, error=f"工具 '{action}' 不存在。可用工具: {', '.join(self.available_tools)}")

        try:
            console.print(f"🔧 执行工具: {action}", style="blue")
            console.print(f"📥 参数: {action_input}", style="dim")

            # 记录工具调用（如果状态管理可用）
            if self.state:
                from ..day2_framework.state import ToolType
                self.state.add_tool_call(
                    ToolType.CUSTOM,  # 使用自定义类型
                    action,
                    action_input
                )
                self.state.current_tool_call.start_execution()

            # 执行工具
            result = self.tool_executor.execute(action, action_input)

            # 完成工具调用记录
            if self.state and self.state.current_tool_call:
                self.state.current_tool_call.finish_execution(
                    result=result.to_dict() if result.success else None,
                    error=result.error if not result.success else None
                )

            console.print(f"📤 结果: {result.success}", style="green" if result.success else "red")
            if not result.success and result.error:
                console.print(f"❌ 错误: {result.error}", style="red")

            return result

        except Exception as e:
            error_msg = f"工具执行异常: {str(e)}"
            console.print(f"❌ {error_msg}", style="red")
            return ToolResult(False, error=error_msg)

    def _format_observation(self, result: ToolResult) -> str:
        """格式化工具执行结果为观察文本"""
        if not result.success:
            return f"工具执行失败: {result.error}"

        if isinstance(result.data, dict):
            # 格式化字典数据
            formatted_data = []
            for key, value in result.data.items():
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False, indent=2)
                formatted_data.append(f"{key}: {value}")
            return "工具执行成功:\n" + "\n".join(formatted_data)
        else:
            return f"工具执行成功: {result.data}"

    def process(self, user_query: str) -> str:
        """
        处理用户查询的主要 ReAct 循环

        Args:
            user_query (str): 用户查询

        Returns:
            str: 最终答案
        """
        console.print(f"\n🚀 开始 ReAct 处理: {user_query}", style="bold blue")
        console.print("=" * 80, style="blue")

        # 重置状态
        self.current_step = 0
        self.steps = []
        self.is_complete = False
        self.final_answer = None

        # 记录开始（如果状态管理可用）
        if self.state:
            self.state.start_task("ReAct处理", total_steps=0)
            self.state.add_message(MessageRole.USER, user_query)

        try:
            while not self.is_complete and self.current_step < self.max_steps:
                self.current_step += 1

                console.print(f"\n📍 步骤 {self.current_step}", style="bold yellow")
                console.print("-" * 60, style="yellow")

                # 构建当前步骤的提示词
                context_prompt = self._build_context_prompt(user_query)
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": context_prompt}
                ]

                # 记录思考状态
                if self.state:
                    self.state.update_status(getattr(self.state.status.__class__, 'THINKING', 'thinking'))
                    self.state.next_step(f"ReAct步骤{self.current_step} - 思考")

                # 调用 LLM
                console.print("🧠 正在思考...", style="blue")
                llm_response = self.ai_service.chat_completion(messages, temperature=0.1, max_tokens=1000)

                if not llm_response.get("success"):
                    error_msg = f"LLM 调用失败: {llm_response.get('error')}"
                    console.print(f"❌ {error_msg}", style="red")
                    return f"抱歉，处理过程中遇到了问题: {error_msg}"

                response_content = llm_response["content"]
                console.print(f"💭 LLM 回复:\n{response_content}", style="dim")

                # 解析响应
                thought, action, action_input, is_final_answer = self._parse_response(response_content)

                # 创建步骤记录
                step = ReActStep(
                    step_number=self.current_step,
                    thought=thought or "无明确思考过程"
                )

                if is_final_answer:
                    # 处理最终答案
                    self.final_answer = thought or response_content
                    self.is_complete = True
                    step.observation = self.final_answer

                    console.print(f"✅ 最终答案: {self.final_answer}", style="bold green")

                    # 记录完成状态
                    if self.state:
                        self.state.add_message(MessageRole.ASSISTANT, self.final_answer)
                        self.state.complete_task(success=True)

                elif action and action_input:
                    # 执行工具动作
                    step.action = action
                    step.action_input = action_input

                    # 记录行动状态
                    if self.state:
                        from ..day2_framework.state import AgentStatus
                        self.state.update_status(AgentStatus.TOOL_EXECUTION)

                    # 执行工具
                    tool_result = self._execute_tool_action(action, action_input)
                    step.tool_result = tool_result
                    step.observation = self._format_observation(tool_result)

                    console.print(f"👀 观察结果: {step.observation[:200]}...", style="cyan")

                    # 记录观察状态
                    if self.state:
                        self.state.update_status(AgentStatus.PROCESSING_RESULT)
                        self.state.add_thought(f"观察工具结果: {step.observation[:100]}...")

                else:
                    # 解析失败，尝试继续
                    console.print("⚠️ 无法解析 LLM 响应，尝试继续...", style="yellow")
                    step.observation = "响应解析失败，请重新思考"

                self.steps.append(step)

            if not self.is_complete:
                # 达到最大步数限制
                console.print(f"⚠️ 达到最大步数限制 ({self.max_steps} 步)", style="yellow")
                return f"抱歉，无法在 {self.max_steps} 步内完成您的请求。当前进展：\n" + \
                       "\n".join([f"步骤{i}: {step.thought}" for i, step in enumerate(self.steps, 1)])

            return self.final_answer

        except Exception as e:
            error_msg = f"ReAct 处理过程中发生错误: {str(e)}"
            console.print(f"❌ {error_msg}", style="red")

            if self.state:
                self.state.complete_task(success=False)
                self.state.add_message(MessageRole.ASSISTANT, f"处理失败: {error_msg}")

            return f"抱歉，处理您的请求时遇到了问题: {error_msg}"

    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        return {
            "agent_id": self.agent_id,
            "total_steps": len(self.steps),
            "is_complete": self.is_complete,
            "final_answer": self.final_answer,
            "steps": [step.to_dict() for step in self.steps],
            "available_tools": self.available_tools
        }

    def display_execution_trace(self):
        """显示执行轨迹"""
        if not self.steps:
            console.print("📝 暂无执行记录", style="dim")
            return

        console.print("\n🔍 ReAct 执行轨迹", style="bold blue")
        console.print("=" * 80, style="blue")

        table = Table(show_header=True)
        table.add_column("步骤", style="cyan", width=8)
        table.add_column("思考", style="white", width=30)
        table.add_column("行动", style="green", width=15)
        table.add_column("结果", style="yellow", width=25)

        for step in self.steps:
            # 截断长文本
            thought = step.thought[:100] + "..." if len(step.thought) > 100 else step.thought
            action = step.action or "N/A"
            observation = step.observation[:100] + "..." if step.observation and len(step.observation) > 100 else (step.observation or "N/A")

            table.add_row(
                str(step.step_number),
                thought,
                action,
                observation
            )

        console.print(table)

        if self.final_answer:
            console.print(f"\n✅ 最终答案: {self.final_answer}", style="bold green")

    def set_state_manager(self, state: AgentState):
        """设置状态管理器（集成 day2）"""
        self.state = state
        console.print("🔗 已集成 Day2 状态管理系统", style="green")


def create_react_engine(agent_id: str = None, ai_provider: str = "deepseek", max_steps: int = 10) -> ReActEngine:
    """创建 ReAct 引擎实例"""
    return ReActEngine(agent_id=agent_id, ai_provider=ai_provider, max_steps=max_steps)


if __name__ == "__main__":
    # 简单测试
    console.print("🧪 测试 ReAct Engine", style="bold blue")

    engine = create_react_engine("test_engine")

    # 测试查询
    test_queries = [
        "计算 123 + 456 等于多少？",
        "北京现在的天气怎么样？"
    ]

    for query in test_queries:
        console.print(f"\n🔍 测试查询: {query}", style="yellow")
        result = engine.process(query)
        console.print(f"📝 结果: {result}")
        engine.display_execution_trace()
        console.print("\n" + "="*80)

    console.print("✅ ReAct Engine 测试完成")