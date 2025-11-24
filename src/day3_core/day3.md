### 1. 理论核心：什么是 ReAct？

ReAct 是 **Re**asoning（推理） + **Act**ing（行动）的缩写。

在 ReAct 出现之前，LLM 只是一个“说话者”。ReAct 把它变成了一个“行动者”。它的核心是一个**循环（Loop）**，步骤如下：

1.  **Thought (思考)**：模型分析用户问题。“用户问天气，我应该查天气 API。”
2.  **Action (行动)**：模型生成一个特定的指令（Function Call）。`get_weather(city="Beijing")`
3.  **Observation (观察)**：代码执行这个指令，获得结果。“北京今天是晴天，25 度。”
4.  **Answer (回答)**：模型根据观察结果，生成最终回复给用户。

> **你的任务**：不要把这看作魔法。这本质上就是：**LLM 输出文本 -> Python 解析文本 -> Python 执行函数 -> 把结果拼回 Prompt -> 再发给 LLM**。

---

### 2. 实践指引：手写 ReAct 引擎

现在，我们要去实现 `src/day3_core/engine.py`。不要复制粘贴完事，请按照以下步骤，边写边理解：

#### 第一步：定义“手”（Tools）—— 策略模式的应用
在 `src/day3_core/tools.py` 中。这里你定义了所有 AI 可以调用的函数。

*   **思考**：这其实就是一个 `Dict[str, Callable]`。
*   **代码重点**：`TOOLS_SCHEMA` 变量。这是给 LLM 看的“说明书”。如果说明书写得不好（description 不清楚），LLM 就不知道什么时候用这个策略。

#### 第二步：构建“大脑”（The Loop）—— 动态路由
在 `src/day3_core/engine.py` 中。这是最关键的部分。

请重点关注那个 `while True` 循环。这就是 Agent 的心脏。