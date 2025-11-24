# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个用于构建 AI 智能体系统的 Python 学习项目，集成了 OpenAI API。项目遵循 5 天的课程结构：

- **Day 1**: 设计模式（责任链模式实现）
- **Day 2**: 智能体状态管理框架
- **Day 3**: ReAct 循环和工具实现
- **Day 4-5**: 个人助手 CLI 应用程序

## 开发命令

### 环境设置
```bash
# 使用 uv 安装依赖
uv sync

# 创建包含 OPENAI_API_KEY 的 .env 文件
echo "OPENAI_API_KEY=your_key_here" > .env
```

### 运行应用程序
```bash
# 运行主入口点
python main.py

# 使用 uv 运行
uv run main.py
```

### 运行演示和测试
```bash
# Day 2 状态管理演示
python src/day2_framework/demo.py

# Day 2 交互式演示
python src/day2_framework/interactive_demo.py

# Day 3 ReAct 演示
python src/day3_core/demo.py

# Day 3 测试套件
python src/day3_core/test_react.py
```

## 架构

### 项目结构
```
src/
├── day1_patterns/     # 责任链设计模式实现
├── day2_framework/    # 智能体状态管理系统
├── day3_core/         # ReAct 引擎和工具系统
└── day4_cli/         # 最终 CLI 助手应用
```

### 依赖包
- **openai**: OpenAI API 客户端，用于 LLM 交互
- **pydantic**: 数据验证和配置管理
- **python-dotenv**: 环境变量管理（.env 文件）
- **rich**: 丰富的文本和 CLI 输出格式化
- **typer**: 构建命令行界面的 CLI 框架

## 核心概念

本项目专注于教授基础 AI 智能体模式：

1. **责任链模式**: 智能体操作的顺序处理
2. **状态管理**: 维护对话和任务状态，使用 Pydantic 进行类型安全
3. **ReAct 循环**: 推理和行动的问题解决模式
   - Thought（思考）：分析问题，决定下一步行动
   - Action（行动）：选择并调用合适的工具
   - Observation（观察）：分析工具返回的结果
   - Final Answer（最终答案）：基于所有观察结果给出完整回答
4. **工具集成**: 通过外部工具扩展智能体能力

## 项目特色功能

### Day 2 状态管理系统
- 基于 Pydantic 的类型安全状态模型
- 完整的智能体状态机（8 种状态：idle, thinking, tool_selection 等）
- 强大的调试和观察系统
- 状态持久化和恢复功能
- 详细的执行追踪和性能监控

### Day 3 ReAct 引擎
- 完整的 Thought→Action→Observation→Final Answer 循环
- 6 个内置工具：计算器、天气查询、网络搜索、文本分析、时间查询、内存存储
- 智能 LLM 响应解析和 JSON 处理
- 工具执行结果格式化
- 执行轨迹追踪和调试
- 错误处理和优雅降级

### 集成测试覆盖
- **Day 2**: 20 个测试用例，覆盖状态管理、智能体集成、复杂场景
- **Day 3**: 30 个测试用例，覆盖工具系统、ReAct 引擎、智能体集成
- 总体测试通过率：100%

## 环境配置

项目需要在项目根目录创建 `.env` 文件：
```
OPENAI_API_KEY=your_openai_api_key_here
```

项目配置为支持 Python 3.12+ 并使用 `uv` 进行依赖管理。

## 技术亮点

### ReAct 核心理念
将 LLM 从"说话者"转变为"行动者"：
- LLM 输出文本 → Python 解析 → 执行函数 → 结果回传 → 发送给 LLM

### 状态管理优势
相比传统 LLM 的 token-based 方式：
- **结构化数据**: 使用 Pydantic 模型确保类型安全
- **完整追踪**: 详细记录每个状态变化和工具调用
- **调试友好**: 可视化状态转换和执行轨迹
- **持久化**: 支持状态保存和恢复

### 工具系统设计
- **标准化接口**: 所有工具返回统一的 ToolResult 格式
- **策略模式**: 易于扩展新工具
- **详细说明**: TOOLS_SCHEMA 为 LLM 提供清晰的使用指导
- **错误处理**: 完善的异常处理和降级机制