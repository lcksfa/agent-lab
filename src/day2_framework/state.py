"""
Agent 状态管理系统 - Day 2 Framework

基于 Pydantic 的 Agent 状态管理，便于调试和观察。
Agent 本质上是一个状态机，在"思考"、"执行工具"、"等待结果"之间流转。

使用 Pydantic 比普通 Python 字典更好的原因：
1. 类型安全：编译时和运行时类型检查
2. 自动验证：数据完整性保证
3. IDE 支持：自动补全和类型提示
4. 序列化：自动 JSON 序列化/反序列化
5. 文档生成：自动生成 schema 文档
6. 默认值和字段验证逻辑
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# 导入 AI 服务
try:
    from ..ai_service import get_ai_service
except ImportError:
    # 如果导入失败，创建一个占位符
    def get_ai_service(provider="deepseek"):
        class MockAIService:
            def chat_completion(self, messages, **kwargs):
                return {
                    "success": True,
                    "content": f"模拟AI回复: {messages[-1]['content'][:50]}...",
                    "usage": {"total_tokens": 100}
                }
            def analyze_document(self, content, analysis_type="general"):
                return {
                    "success": True,
                    "content": f"模拟文档分析: {content[:30]}..."
                }
        return MockAIService()


class AgentStatus(str, Enum):
    """Agent 状态枚举"""
    IDLE = "idle"                      # 空闲状态
    THINKING = "thinking"              # 思考中
    TOOL_SELECTION = "tool_selection"  # 工具选择
    TOOL_EXECUTION = "tool_execution"  # 工具执行
    WAITING_RESULT = "waiting_result"  # 等待结果
    PROCESSING_RESULT = "processing_result"  # 处理结果
    RESPONDING = "responding"          # 生成回复
    ERROR = "error"                    # 错误状态
    COMPLETED = "completed"            # 任务完成


class ToolType(str, Enum):
    """工具类型枚举"""
    AI_CHAT = "ai_chat"                # AI 对话
    DOCUMENT_ANALYZE = "document_analyze"  # 文档分析
    WEB_SEARCH = "web_search"          # 网络搜索
    CALCULATOR = "calculator"          # 计算器
    CODE_EXECUTOR = "code_executor"    # 代码执行
    DATABASE_QUERY = "database_query"  # 数据库查询
    CUSTOM = "custom"                  # 自定义工具


class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"                      # 用户
    ASSISTANT = "assistant"            # 助手
    SYSTEM = "system"                  # 系统
    TOOL = "tool"                      # 工具


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "debug"                    # 调试信息
    INFO = "info"                      # 一般信息
    WARNING = "warning"                # 警告
    ERROR = "error"                    # 错误
    CRITICAL = "critical"              # 严重错误


class Message(BaseModel):
    """消息模型"""
    id: str = Field(default_factory=lambda: f"msg_{int(time.time()*1000)}")
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def __str__(self):
        return f"[{self.role.value}] {self.content}"


class ToolCall(BaseModel):
    """工具调用模型"""
    id: str = Field(default_factory=lambda: f"tool_{int(time.time()*1000)}")
    tool_type: ToolType
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: Optional[float] = None

    def start_execution(self):
        """开始执行工具"""
        self.start_time = datetime.now()

    def finish_execution(self, result: Any = None, error: str = None):
        """完成工具执行"""
        self.end_time = datetime.now()
        if self.start_time:
            self.execution_time = (self.end_time - self.start_time).total_seconds()
        self.result = result
        self.error = error


class LogEntry(BaseModel):
    """日志条目模型"""
    id: str = Field(default_factory=lambda: f"log_{int(time.time()*1000)}")
    timestamp: datetime = Field(default_factory=datetime.now)
    level: LogLevel
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)

    def __str__(self):
        return f"[{self.level.value.upper()}] {self.timestamp.strftime('%H:%M:%S')} {self.message}"


class AgentState(BaseModel):
    """Agent 状态模型 - 核心状态管理"""

    # 基本信息
    agent_id: str = Field(default_factory=lambda: f"agent_{int(time.time())}")
    session_id: Optional[str] = None
    user_id: Optional[str] = None

    # 状态信息
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    current_step: int = 0
    total_steps: int = 0

    # 对话历史
    messages: List[Message] = Field(default_factory=list)
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)

    # 工具调用
    tool_calls: List[ToolCall] = Field(default_factory=list)
    current_tool_call: Optional[ToolCall] = None

    # 思考过程
    thoughts: List[str] = Field(default_factory=list)
    reasoning_steps: List[Dict[str, Any]] = Field(default_factory=list)

    # 上下文和记忆
    context: Dict[str, Any] = Field(default_factory=dict)
    working_memory: Dict[str, Any] = Field(default_factory=dict)
    long_term_memory: Dict[str, Any] = Field(default_factory=dict)

    # 配置
    config: Dict[str, Any] = Field(default_factory=dict)

    # 日志和调试
    logs: List[LogEntry] = Field(default_factory=list)
    debug_mode: bool = True

    # 性能指标
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_execution_time: Optional[float] = None

    # 错误处理
    errors: List[str] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3

    class Config:
        """Pydantic 配置"""
        use_enum_values = True
        validate_assignment = True
        extra = "allow"  # 允许额外字段

    def add_message(self, role: MessageRole, content: str, metadata: Dict[str, Any] = None) -> Message:
        """添加消息"""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)

        # 同时维护简化的对话历史
        self.conversation_history.append({
            "role": role.value,
            "content": content
        })

        self.log(LogLevel.INFO, f"添加{role.value}消息", {"message_length": len(content)})
        return message

    def add_tool_call(self, tool_type: ToolType, tool_name: str, parameters: Dict[str, Any]) -> ToolCall:
        """添加工具调用"""
        tool_call = ToolCall(
            tool_type=tool_type,
            tool_name=tool_name,
            parameters=parameters
        )
        self.tool_calls.append(tool_call)
        self.current_tool_call = tool_call

        self.log(LogLevel.INFO, f"开始执行工具: {tool_name}", {
            "tool_type": tool_type.value,
            "parameters": parameters
        })
        return tool_call

    def add_thought(self, thought: str):
        """添加思考过程"""
        self.thoughts.append(thought)
        self.log(LogLevel.DEBUG, f"思考: {thought}")

    def add_reasoning_step(self, step_type: str, content: str, data: Dict[str, Any] = None):
        """添加推理步骤"""
        step = {
            "step_type": step_type,
            "content": content,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }
        self.reasoning_steps.append(step)
        self.log(LogLevel.DEBUG, f"推理步骤: {step_type} - {content}")

    def update_status(self, new_status: AgentStatus, task: str = None):
        """更新状态"""
        old_status = self.status
        self.status = new_status

        if task:
            self.current_task = task

        # 处理状态可能已经是字符串的情况
        old_status_value = old_status.value if hasattr(old_status, 'value') else str(old_status)
        new_status_value = new_status.value if hasattr(new_status, 'value') else str(new_status)

        self.log(LogLevel.INFO, f"状态变化: {old_status_value} -> {new_status_value}", {
            "task": task,
            "old_status": old_status_value,
            "new_status": new_status_value
        })

    def log(self, level: LogLevel, message: str, details: Dict[str, Any] = None):
        """添加日志"""
        log_entry = LogEntry(
            level=level,
            message=message,
            details=details or {}
        )
        self.logs.append(log_entry)

        # 如果是错误级别，同时添加到错误列表
        if level == LogLevel.ERROR:
            self.errors.append(message)

    def start_task(self, task: str, total_steps: int = 0):
        """开始任务"""
        self.current_task = task
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = datetime.now()
        self.update_status(AgentStatus.THINKING, task)

        self.log(LogLevel.INFO, f"开始任务: {task}", {"total_steps": total_steps})

    def next_step(self, step_description: str = None):
        """进入下一步"""
        if self.total_steps > 0:
            self.current_step = min(self.current_step + 1, self.total_steps)

        if step_description:
            self.log(LogLevel.INFO, f"步骤 {self.current_step}/{self.total_steps}: {step_description}")

    def complete_task(self, success: bool = True):
        """完成任务"""
        self.end_time = datetime.now()
        if self.start_time:
            self.total_execution_time = (self.end_time - self.start_time).total_seconds()

        self.update_status(AgentStatus.COMPLETED if success else AgentStatus.ERROR)

        self.log(LogLevel.INFO, f"任务完成", {
            "success": success,
            "total_time": self.total_execution_time,
            "total_steps": self.current_step
        })

    def set_context(self, key: str, value: Any):
        """设置上下文"""
        self.context[key] = value
        self.log(LogLevel.DEBUG, f"设置上下文: {key}")

    def get_context(self, key: str, default: Any = None) -> Any:
        """获取上下文"""
        return self.context.get(key, default)

    def set_working_memory(self, key: str, value: Any):
        """设置工作记忆"""
        self.working_memory[key] = value
        self.log(LogLevel.DEBUG, f"设置工作记忆: {key}")

    def get_working_memory(self, key: str, default: Any = None) -> Any:
        """获取工作记忆"""
        return self.working_memory.get(key, default)

    def get_state_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        # 处理状态可能已经是字符串的情况
        status_value = self.status.value if hasattr(self.status, 'value') else str(self.status)

        return {
            "agent_id": self.agent_id,
            "status": status_value,
            "current_task": self.current_task,
            "progress": f"{self.current_step}/{self.total_steps}" if self.total_steps > 0 else "N/A",
            "messages_count": len(self.messages),
            "tool_calls_count": len(self.tool_calls),
            "thoughts_count": len(self.thoughts),
            "errors_count": len(self.errors),
            "execution_time": self.total_execution_time,
            "debug_mode": self.debug_mode
        }

    def export_state(self) -> Dict[str, Any]:
        """导出完整状态（用于序列化）"""
        return self.model_dump()

    def import_state(self, state_data: Dict[str, Any]):
        """导入状态（用于反序列化）"""
        # 这里可以实现状态的恢复逻辑
        for key, value in state_data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class StateDebugger:
    """状态调试器 - 提供状态观察和调试功能"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def display_state_summary(self, state: AgentState):
        """显示状态摘要"""
        summary = state.get_state_summary()

        table = Table(title="🤖 Agent 状态摘要", show_header=True, header_style="bold magenta")
        table.add_column("属性", style="cyan", width=20)
        table.add_column("值", style="green")

        for key, value in summary.items():
            table.add_row(key, str(value) if value is not None else "N/A")

        self.console.print(table)

    def display_messages(self, state: AgentState, limit: int = 5):
        """显示消息历史"""
        messages = state.messages[-limit:] if limit > 0 else state.messages

        table = Table(title=f"💬 消息历史 (最近 {len(messages)} 条)", show_header=True)
        table.add_column("时间", style="cyan", width=12)
        table.add_column("角色", style="magenta", width=10)
        table.add_column("内容", style="white")

        for msg in messages:
            timestamp = msg.timestamp.strftime("%H:%M:%S")
            content = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
            table.add_row(timestamp, msg.role.value, content)

        self.console.print(table)

    def display_tool_calls(self, state: AgentState):
        """显示工具调用历史"""
        if not state.tool_calls:
            self.console.print("📦 暂无工具调用记录", style="dim")
            return

        table = Table(title="🔧 工具调用历史", show_header=True)
        table.add_column("工具", style="cyan", width=15)
        table.add_column("类型", style="magenta", width=12)
        table.add_column("状态", style="green", width=8)
        table.add_column("执行时间", style="yellow", width=10)
        table.add_column("结果/错误", style="white")

        for tool_call in state.tool_calls:
            status = "✅ 成功" if tool_call.result is not None else "❌ 失败" if tool_call.error else "⏳ 进行中"
            exec_time = f"{tool_call.execution_time:.2f}s" if tool_call.execution_time else "N/A"

            result_info = ""
            if tool_call.result:
                result_info = str(tool_call.result)[:50] + "..." if len(str(tool_call.result)) > 50 else str(tool_call.result)
            elif tool_call.error:
                result_info = f"错误: {tool_call.error}"

            table.add_row(
                tool_call.tool_name,
                tool_call.tool_type.value,
                status,
                exec_time,
                result_info
            )

        self.console.print(table)

    def display_thoughts(self, state: AgentState, limit: int = 10):
        """显示思考过程"""
        thoughts = state.thoughts[-limit:] if limit > 0 else state.thoughts

        if not thoughts:
            self.console.print("🧠 暂无思考记录", style="dim")
            return

        panel_content = ""
        for i, thought in enumerate(thoughts, 1):
            panel_content += f"{i}. {thought}\n"

        panel = Panel(
            panel_content.strip(),
            title=f"🧠 思考过程 (最近 {len(thoughts)} 条)",
            border_style="blue"
        )
        self.console.print(panel)

    def display_logs(self, state: AgentState, level: Optional[LogLevel] = None, limit: int = 20):
        """显示日志"""
        logs = state.logs

        # 过滤日志级别
        if level:
            logs = [log for log in logs if log.level == level]

        # 限制数量
        logs = logs[-limit:] if limit > 0 else logs

        if not logs:
            self.console.print("📝 暂无日志记录", style="dim")
            return

        table = Table(title=f"📝 日志记录 (最近 {len(logs)} 条)", show_header=True)
        table.add_column("时间", style="cyan", width=12)
        table.add_column("级别", style="magenta", width=8)
        table.add_column("消息", style="white")

        for log in logs:
            timestamp = log.timestamp.strftime("%H:%M:%S")

            table.add_row(
                timestamp,
                log.level.value,
                log.message[:80] + "..." if len(log.message) > 80 else log.message
            )

        self.console.print(table)

    def display_full_debug_info(self, state: AgentState):
        """显示完整调试信息"""
        self.console.print("\n" + "="*80, style="bold white")
        self.console.print("🔍 AGENT 完整调试信息", style="bold white", justify="center")
        self.console.print("="*80, style="bold white")

        # 状态摘要
        self.display_state_summary(state)
        self.console.print()

        # 消息历史
        self.display_messages(state)
        self.console.print()

        # 思考过程
        self.display_thoughts(state)
        self.console.print()

        # 工具调用
        self.display_tool_calls(state)
        self.console.print()

        # 日志
        self.display_logs(state)
        self.console.print()

        # 上下文信息
        self.display_context(state)

    def display_context(self, state: AgentState):
        """显示上下文信息"""
        if not state.context and not state.working_memory:
            self.console.print("📋 暂无上下文信息", style="dim")
            return

        # 上下文
        if state.context:
            context_table = Table(title="📋 上下文信息", show_header=True)
            context_table.add_column("键", style="cyan", width=20)
            context_table.add_column("值", style="white")

            for key, value in state.context.items():
                value_str = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
                context_table.add_row(key, value_str)

            self.console.print(context_table)

        # 工作记忆
        if state.working_memory:
            memory_table = Table(title="🧠 工作记忆", show_header=True)
            memory_table.add_column("键", style="cyan", width=20)
            memory_table.add_column("值", style="white")

            for key, value in state.working_memory.items():
                value_str = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
                memory_table.add_row(key, value_str)

            self.console.print(memory_table)


class Agent:
    """Agent 类 - 集成状态管理的智能代理"""

    def __init__(self, agent_id: str = None, debug_mode: bool = True, ai_provider: str = "deepseek"):
        self.state = AgentState(
            agent_id=agent_id or f"agent_{int(time.time())}",
            debug_mode=debug_mode
        )
        self.debugger = StateDebugger()
        self.ai_service = get_ai_service(ai_provider)

        self.state.log(LogLevel.INFO, f"Agent 初始化完成", {
            "agent_id": self.state.agent_id,
            "ai_provider": ai_provider,
            "debug_mode": debug_mode
        })

    def process_user_message(self, message: str) -> str:
        """处理用户消息的主要流程"""
        # 开始任务
        self.state.start_task("处理用户消息", total_steps=5)

        try:
            # 步骤1: 添加用户消息
            self.state.next_step("记录用户消息")
            self.state.add_message(MessageRole.USER, message)

            # 步骤2: 分析用户意图
            self.state.next_step("分析用户意图")
            intent = self._analyze_intent(message)
            self.state.add_thought(f"用户意图分析: {intent}")

            # 步骤3: 决定行动策略
            self.state.next_step("决定行动策略")
            strategy = self._decide_strategy(intent, message)
            self.state.add_thought(f"选择策略: {strategy}")

            # 步骤4: 执行策略
            self.state.next_step("执行策略")
            result = self._execute_strategy(strategy, message)

            # 步骤5: 生成回复
            self.state.next_step("生成回复")
            response = self._generate_response(result, message)

            # 添加助手回复
            self.state.add_message(MessageRole.ASSISTANT, response)

            # 完成任务
            self.state.complete_task(success=True)

            return response

        except Exception as e:
            error_msg = f"处理用户消息时发生错误: {str(e)}"
            self.state.log(LogLevel.ERROR, error_msg)
            self.state.complete_task(success=False)

            # 添加错误回复
            error_response = "抱歉，处理您的消息时遇到了问题，请稍后再试。"
            self.state.add_message(MessageRole.ASSISTANT, error_response)

            return error_response

    def _analyze_intent(self, message: str) -> str:
        """分析用户意图"""
        self.state.update_status(AgentStatus.THINKING)

        # 简单的意图识别逻辑
        message_lower = message.lower()

        if any(word in message_lower for word in ['分析', 'analyze', '总结', 'summary']):
            return 'document_analysis'
        elif any(word in message_lower for word in ['计算', 'calculator', '算', '计算']):
            return 'calculation'
        elif any(word in message_lower for word in ['搜索', 'search', '查找', 'find']):
            return 'web_search'
        elif any(word in message_lower for word in ['代码', 'code', '编程', 'program']):
            return 'code_related'
        else:
            return 'general_chat'

    def _decide_strategy(self, intent: str, _message: str) -> str:
        """决定行动策略"""
        self.state.update_status(AgentStatus.TOOL_SELECTION)

        strategies = {
            'document_analysis': 'use_ai_analysis',
            'calculation': 'use_calculator',
            'web_search': 'use_web_search',
            'code_related': 'use_code_assistant',
            'general_chat': 'use_ai_chat'
        }

        strategy = strategies.get(intent, 'use_ai_chat')
        self.state.add_reasoning_step(
            "策略选择",
            f"根据意图 '{intent}' 选择策略 '{strategy}'",
            {"intent": intent, "strategy": strategy}
        )

        return strategy

    def _execute_strategy(self, strategy: str, message: str) -> Dict[str, Any]:
        """执行策略"""
        self.state.update_status(AgentStatus.TOOL_EXECUTION)

        if strategy == 'use_ai_analysis':
            return self._execute_document_analysis(message)
        elif strategy == 'use_calculator':
            return self._execute_calculator(message)
        elif strategy == 'use_web_search':
            return self._execute_web_search(message)
        elif strategy == 'use_code_assistant':
            return self._execute_code_assistant(message)
        else:  # use_ai_chat
            return self._execute_ai_chat(message)

    def _execute_ai_chat(self, message: str) -> Dict[str, Any]:
        """执行 AI 聊天"""
        tool_call = self.state.add_tool_call(
            ToolType.AI_CHAT,
            "chat_completion",
            {"message": message}
        )

        tool_call.start_execution()

        try:
            messages = [
                {"role": "system", "content": "你是一个有用的 AI 助手，请简洁、准确地回答用户的问题。"},
                {"role": "user", "content": message}
            ]

            result = self.ai_service.chat_completion(messages, temperature=0.7, max_tokens=500)

            if result["success"]:
                tool_call.finish_execution(result=result)
                return {"success": True, "response": result["content"], "usage": result.get("usage")}
            else:
                tool_call.finish_execution(error=result.get("error", "Unknown error"))
                return {"success": False, "error": result.get("error")}

        except Exception as e:
            tool_call.finish_execution(error=str(e))
            raise

    def _execute_document_analysis(self, message: str) -> Dict[str, Any]:
        """执行文档分析"""
        tool_call = self.state.add_tool_call(
            ToolType.DOCUMENT_ANALYZE,
            "analyze_document",
            {"content": message}
        )

        tool_call.start_execution()

        try:
            result = self.ai_service.analyze_document(message, "general")

            if result["success"]:
                tool_call.finish_execution(result=result["content"])
                return {"success": True, "analysis": result["content"]}
            else:
                tool_call.finish_execution(error=result.get("error", "Unknown error"))
                return {"success": False, "error": result.get("error")}

        except Exception as e:
            tool_call.finish_execution(error=str(e))
            raise

    def _execute_calculator(self, message: str) -> Dict[str, Any]:
        """执行计算器（模拟）"""
        tool_call = self.state.add_tool_call(
            ToolType.CALCULATOR,
            "simple_calculator",
            {"expression": message}
        )

        tool_call.start_execution()

        # 简单的计算模拟
        try:
            # 这里应该有更复杂的表达式解析逻辑
            # 为了演示，我们只做简单的模拟
            import re

            # 提取数字和运算符
            numbers = re.findall(r'\d+\.?\d*', message)
            if len(numbers) >= 2:
                result = float(numbers[0]) + float(numbers[1])  # 简单加法
                result_text = f"计算结果: {numbers[0]} + {numbers[1]} = {result}"
            else:
                result_text = f"找到数字: {numbers}，但无法确定运算方式"
                result = None

            tool_call.finish_execution(result=result_text)
            return {"success": True, "calculation": result_text, "result": result}

        except Exception as e:
            error_msg = f"计算错误: {str(e)}"
            tool_call.finish_execution(error=error_msg)
            return {"success": False, "error": error_msg}

    def _execute_web_search(self, message: str) -> Dict[str, Any]:
        """执行网络搜索（模拟）"""
        tool_call = self.state.add_tool_call(
            ToolType.WEB_SEARCH,
            "web_search",
            {"query": message}
        )

        tool_call.start_execution()

        # 模拟网络搜索
        import time
        time.sleep(0.5)  # 模拟搜索延迟

        mock_result = f"关于 '{message}' 的搜索结果：\n1. 这是一个模拟的搜索结果\n2. 实际应用中会调用真实的搜索 API"

        tool_call.finish_execution(result=mock_result)
        return {"success": True, "search_results": mock_result}

    def _execute_code_assistant(self, message: str) -> Dict[str, Any]:
        """执行代码助手（模拟）"""
        tool_call = self.state.add_tool_call(
            ToolType.CODE_EXECUTOR,
            "code_assistant",
            {"request": message}
        )

        tool_call.start_execution()

        # 模拟代码分析
        mock_code_help = f"代码分析结果：\n- 您询问的是关于: {message}\n- 建议检查代码语法和逻辑结构\n- 可以提供具体的代码片段以便更好地帮助您"

        tool_call.finish_execution(result=mock_code_help)
        return {"success": True, "code_help": mock_code_help}

    def _generate_response(self, result: Dict[str, Any], _original_message: str) -> str:
        """生成最终回复"""
        self.state.update_status(AgentStatus.RESPONDING)

        if result.get("success"):
            if "response" in result:
                return result["response"]
            elif "analysis" in result:
                return f"📋 文档分析结果：\n{result['analysis']}"
            elif "calculation" in result:
                return f"🧮 计算结果：\n{result['calculation']}"
            elif "search_results" in result:
                return f"🔍 搜索结果：\n{result['search_results']}"
            elif "code_help" in result:
                return f"💻 代码助手：\n{result['code_help']}"
            else:
                return "处理完成，但没有生成具体结果。"
        else:
            error_msg = result.get("error", "未知错误")
            return f"❌ 处理失败：{error_msg}"

    def get_debug_info(self) -> str:
        """获取调试信息的字符串表示"""
        if self.state.debug_mode:
            # 使用 rich console 的 capture 来获取字符串
            from io import StringIO
            console_str = Console(file=StringIO())
            debugger = StateDebugger(console_str)
            debugger.display_full_debug_info(self.state)
            return console_str.file.getvalue()
        else:
            return "调试模式未启用"

    def save_state(self, filepath: str):
        """保存状态到文件"""
        try:
            state_data = self.state.export_state()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2, default=str)

            self.state.log(LogLevel.INFO, f"状态已保存到: {filepath}")

        except Exception as e:
            self.state.log(LogLevel.ERROR, f"保存状态失败: {str(e)}")
            raise

    def load_state(self, filepath: str):
        """从文件加载状态"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state_data = json.load(f)

            self.state.import_state(state_data)
            self.state.log(LogLevel.INFO, f"状态已从文件加载: {filepath}")

        except Exception as e:
            self.state.log(LogLevel.ERROR, f"加载状态失败: {str(e)}")
            raise

    def reset_state(self):
        """重置状态"""
        old_agent_id = self.state.agent_id
        self.state = AgentState(
            agent_id=old_agent_id,
            debug_mode=self.state.debug_mode
        )
        self.state.log(LogLevel.INFO, "Agent 状态已重置")


# 便捷函数
def create_agent(agent_id: str = None, debug_mode: bool = True) -> Agent:
    """创建 Agent 实例"""
    return Agent(agent_id=agent_id, debug_mode=debug_mode)


def demo_state_management():
    """演示状态管理功能"""
    console = Console()

    console.print("🎯 Agent 状态管理演示", style="bold blue", justify="center")
    console.print("=" * 60, style="blue")

    # 创建 Agent
    agent = create_agent("demo_agent", debug_mode=True)

    # 演示对话
    demo_messages = [
        "请分析一下人工智能的发展趋势",
        "帮我计算 123 + 456",
        "搜索 Python 编程的最佳实践",
        "你好，介绍一下你的功能"
    ]

    for i, message in enumerate(demo_messages, 1):
        console.print(f"\n👤 用户 {i}: {message}", style="green")

        # 处理消息
        response = agent.process_user_message(message)
        console.print(f"🤖 Agent: {response}", style="blue")

        # 显示状态摘要
        console.print("\n" + "-"*40)
        agent.debugger.display_state_summary(agent.state)

        if i < len(demo_messages):
            input("\n按 Enter 继续...")

    # 显示完整调试信息
    console.print("\n\n🔍 完整调试信息", style="bold red", justify="center")
    console.print("=" * 60, style="red")
    agent.debugger.display_full_debug_info(agent.state)

    return agent


if __name__ == "__main__":
    # 运行演示
    demo_state_management()