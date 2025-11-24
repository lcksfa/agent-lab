理解 Agent 状态 (State) 与 Pydantic
目标：理解 LangGraph 或 PydanticAI 的核心——状态 (State)。Agent 本质上是一个状态机，它在“思考”、“执行工具”、“等待结果”之间流转。

任务：在 src/day2_framework/state.py 中定义 Agent 的状态。

AI 接口使用 deepseek ，请参考 day1 的AI 接入逻辑

AI 助攻提示：“为什么使用 Pydantic 来定义 State 比使用普通的 Python 字典更好？这对于构建复杂的 Agent 有什么帮助？”

调整节奏非常重要。**Day 2 是从“脚本”进化到“系统”的关键分水岭。**

在 Day 1，你学习了责任链（Chain），它是线性的（A -> B -> C）。
但在 Day 2，我们要打破线性，引入**状态（State）**和**循环（Loop）**，这是构建 Agent 的地基。

我们今天的目标不是直接去学 LangChain 或 LangGraph 的复杂 API，而是**用原生 Python 复现它们的核心原理**。

---

### 🎯 Day 2 核心概念：Chain vs. Graph

在开始写代码前，先建立两个心理模型：

1.  **Chain (链)**：像工厂流水线。
    *   输入 -> 步骤1 -> 步骤2 -> 输出。
    *   *缺点*：如果步骤1出错，或者需要重复步骤1，很难处理。
2.  **Graph (图/状态机)**：像玩大富翁（Monopoly）。
    *   有一个核心的**状态（State）**（比如你的棋子位置、手里的钱）。
    *   有不同的**节点（Node）**（比如“掷骰子”、“买地”、“坐牢”）。
    *   有**边（Edge/Router）**：根据当前状态决定下一步去哪（比如“钱不够”->“去银行”）。

**今天的任务**：在 `agent-lab` 中构建一个微型的“状态机”框架。

---

### 💻 实践环节：构建你的 State Machine

请在你的项目中操作 `src/day2_framework/` 目录。

#### 第一步：定义“状态” (The State)

Agent 运行过程中产生的所有数据（聊天记录、中间结果、错误信息）都需要存在一个地方，这就是 State。我们使用 `Pydantic` 来定义它，因为它能保证数据类型的安全。

新建/编辑 `src/day2_framework/state.py`：

```python
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# 1. 定义我们的“棋盘” (State)
class AgentState(BaseModel):
    # 对话历史
    messages: List[str] = Field(default_factory=list)
    # 当前任务是否完成
    is_finished: bool = False
    # 甚至可以存一些中间变量，比如“用户的情绪”
    user_mood: Literal["neutral", "happy", "angry"] = "neutral"
    # 最后的总结
    final_answer: Optional[str] = None

    def add_message(self, content: str):
        self.messages.append(content)
```

#### 第二步：定义“节点” (Nodes)

节点就是函数，但它们有一个特点：**输入是 State，输出也是 State**（或者对 State 进行修改）。

在同一个文件 `src/day2_framework/state.py` 中继续添加：

```python
import random

# 节点 1: 模拟“思考/规划”
def node_think(state: AgentState) -> AgentState:
    print("🧠 [Think Node] 正在分析用户需求...")
    # 模拟：这里本该调用 LLM，我们先用逻辑模拟
    last_msg = state.messages[-1]
    
    if "天气" in last_msg:
        state.add_message("System: 需要查询天气数据。")
    else:
        state.add_message("System: 这是一个普通聊天。")
    
    return state

# 节点 2: 模拟“执行/搜索”
def node_search(state: AgentState) -> AgentState:
    print("🔍 [Search Node] 正在检索数据...")
    state.add_message("Tool: 北京今日晴转多云，25度。")
    return state

# 节点 3: 模拟“生成回答”
def node_answer(state: AgentState) -> AgentState:
    print("📝 [Answer Node] 正在组织语言...")
    # 拿出最近的几条消息来生成回答
    context = "\n".join(state.messages)
    state.final_answer = f"基于上下文 '{context}'，我的回答是：天气不错。"
    state.is_finished = True
    return state
```

#### 第三步：定义“路由” (Router/Edge)

这是 Graph 和 Chain 最大的区别。我们需要一个逻辑来决定**下一步去哪**。

```python
# 路由逻辑：决定下一个节点是谁
def decide_next_step(state: AgentState) -> str:
    last_msg = state.messages[-1]
    
    if state.is_finished:
        return "end"
    
    # 如果系统决定需要查数据（基于 Think 节点的结果）
    if "需要查询" in last_msg:
        return "search"
    
    # 如果已经查到了数据（Tool 消息），或者不需要查数据
    if "Tool:" in last_msg or "普通聊天" in last_msg:
        return "answer"
    
    # 默认情况
    return "think"
```

#### 第四步：运行图 (The Graph Runner)

把所有东西串起来。

```python
def run_day2_demo():
    # 1. 初始化状态
    initial_state = AgentState()
    initial_state.add_message("User: 帮我查查北京的天气")
    
    print(f"🚀 开始状态: {initial_state}")
    
    # 2. 定义图的结构 (节点映射表)
    nodes = {
        "think": node_think,
        "search": node_search,
        "answer": node_answer
    }
    
    # 3. 开始循环 (这就是 Graph 的运行引擎)
    current_node_name = "think" # 入口节点
    
    while current_node_name != "end":
        print(f"\n--- 进入节点: {current_node_name} ---")
        
        # A. 获取当前节点的函数
        current_node_func = nodes[current_node_name]
        
        # B. 执行节点，更新状态
        initial_state = current_node_func(initial_state)
        
        # C. 路由：决定下一步去哪
        current_node_name = decide_next_step(initial_state)
        
        print(f"   -> 下一步去: {current_node_name}")
        print(f"   -> 当前消息数: {len(initial_state.messages)}")

    print(f"\n✅ 最终结果: {initial_state.final_answer}")

if __name__ == "__main__":
    run_day2_demo()
```

---

### 🧪 你的任务清单

1.  **代码实现**：将上述代码写入 `src/day2_framework/state.py`。
2.  **运行观察**：
    *   使用 `uv run src/day2_framework/state.py` 运行。
    *   观察控制台输出，看它是如何在 `think` -> `search` -> `answer` 之间跳转的。
3.  **修改实验**（关键步骤）：
    *   修改 `run_day2_demo` 中的初始输入为 `"User: 你好，讲个笑话"`。
    *   **预测**：代码会怎么跑？
    *   **验证**：路由逻辑应该会跳过 `search` 节点，直接从 `think` -> `answer`。
    *   如果实现了这一点，你就理解了 **条件边 (Conditional Edge)** 的概念。

### 💡 深度思考 (AI 助攻)

做完实验后，思考以下问题（这正是 LangGraph 解决的问题）：

1.  **状态持久化**：如果程序崩溃了，我怎么从“Search Node”断点续传？（答案：因为 State 是 Pydantic 对象，可以轻松序列化成 JSON 存数据库）。
2.  **循环限制**：如果 `decide_next_step` 逻辑写错了，导致 `think` -> `search` -> `think` -> `search` 死循环怎么办？（答案：通常需要加一个 `recursion_limit` 递归深度限制）。

完成 Day 2 后，你其实已经手写了一个微型的 LangGraph。Day 3 我们就要把这些模拟的 `print` 换成真正的 LLM 和 Tool 调用了！