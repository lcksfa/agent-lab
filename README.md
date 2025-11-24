## 学习设计模式与 Agent 框架
*重点：让 AI 学会使用工具和规划。*

| 时间 | 任务详情 (Task) | 🤖 AI 助攻 (Prompt 示例) | 状态 |
| :--- | :--- | :--- | :--- |
| **Day 1 上午** | ✅ 学习"装饰模式，"“策略模式”和“责任链模式”在 AI 中的应用。| “举例说明如何在 AI 工作流中使用策略模式，装饰器模式，责任链模式处理长文档。” | ✅ 已完成 |
| **Day 1 下午** | **Agent 概念**：ReAct 模式（Reasoning + Acting），Tool Use 原理。 | “一步步推演 ReAct 模式下，AI 是如何决定调用搜索工具的。” | 🔄 待完成 |
| **Day 2 上午** | **LangChain/LangGraph 拆解**：不直接用库，先看源码或原理，理解 Chain 和 Graph 的区别。 | “LangGraph 的核心概念 State 和 Node 是什么意思？” | ⏳ 待完成 |
| **Day 2 下午** | **PydanticAI / 简单框架**：试用一个轻量级 Agent 框架，构建一个能查天气的 Agent。 | “使用 PydanticAI 写一个能调用天气 API 的 Agent 示例。” | ⏳ 待完成 |
| **Day 3 上午** | **手写简易 Agent**：不依赖框架，用原生 Python + DeepSeek 实现一个能调用计算器的 Agent。 | “帮我写一个 Python 函数，解析 LLM 返回的函数调用请求并执行它。” | ⏳ 待完成 |
| **Day 3 下午** | **多智能体 (Multi-Agent)**：理解路由（Router）和协作。设计一个"研究员+撰稿人"的工作流。 | “设计一个包含'搜索者'和'总结者'的双 Agent 系统架构图。” | ⏳ 待完成 |
| **Day 4-5 全天** | **实战项目 4：个人助理 Agent**。具备 2-3 个工具（查时间、简单计算、写文件），通过 CLI 交互。 | “帮我定义这三个工具的 JSON Schema，以便 LLM 理解。” | ⏳ 待完成 |

## 工程目录

```
agent-lab/
├── .env                # 存放 DEEPSEEK_API_KEY
├── pyproject.toml      # uv 管理的依赖文件
├── test_ai_api.py      # AI API 连接测试脚本
├── src/
│   ├── ai_service.py   # AI 服务统一接口（支持 DeepSeek）
│   ├── __init__.py
│   ├── main.py         # 程序入口
│   ├── day1_patterns/  # Day 1: 设计模式
│   │   ├── __init__.py
│   │   ├── chain.py    # 原始文件（保留）
│   │   ├── strategy.py # 策略模式实现
│   │   ├── decorator.py # 装饰器模式实现
│   │   ├── responsibility_chain.py # 责任链模式实现
│   │   └── demo.py     # 三种模式综合演示
│   ├── day2_framework/ # Day 2: 简单的 Agent 状态管理
│   │   ├── __init__.py
│   │   └── state.py
│   ├── day3_core/      # Day 3: 手写 ReAct 循环 & Tools
│   │   ├── __init__.py
│   │   ├── tools.py
│   │   └── engine.py
│   └── day4_cli/       # Day 4-5: 最终的个人助理
│       ├── __init__.py
│       └── app.py
├── task.md             # 任务清单
├── README.md           # 项目说明
└── CLAUDE.md           # Claude Code 指南
```

## Day 1: 设计模式实现 ✅

已完成三种设计模式的AI工作流实现：

### 📋 策略模式 (`strategy.py`)
- 不同文档类型的不同处理策略（法律、技术、学术）
- 智能分块和分析方法
- 可扩展的策略系统

### 🎭 装饰器模式 (`decorator.py`)
- 日志记录、缓存、性能监控
- AI增强功能（情感分析、关键词提取）
- 错误处理和重试机制

### 🔗 责任链模式 (`responsibility_chain.py`)
- 模块化的文档处理流水线
- 内容提取→情感分析→AI摘要→输出格式化
- 灵活的处理器组合

### 🎯 综合演示 (`demo.py`)
- 三种模式的完整使用示例
- 模式组合策略说明
- 实际应用场景展示

## AI API 配置

本项目使用 **DeepSeek API** 进行AI功能：

### 1. 配置 API Key
在 `.env` 文件中设置：
```bash
DEEPSEEK_API_KEY=你的DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 2. 测试 API 连接
```bash
python test_ai_api.py
```

### 3. 运行设计模式演示
```bash
# 运行策略模式演示
python src/day1_patterns/strategy.py

# 运行装饰器模式演示
python src/day1_patterns/decorator.py

# 运行责任链模式演示
python src/day1_patterns/responsibility_chain.py

# 运行综合演示（推荐）
python src/day1_patterns/demo.py

# 测试AI API连接
python test_ai_api.py
```

### 4. 环境准备
```bash
# 安装依赖
uv sync

# 运行主程序
python src/main.py
```
