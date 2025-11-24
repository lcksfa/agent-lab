# Day 4 CLI 聊天应用

基于 ReAct 模式的智能助手 CLI 应用，提供完整的聊天体验和强大的任务处理能力。

## 🎯 功能特性

### 核心功能
- ✅ **交互式聊天界面** - 美观的 CLI 输出格式，用户友好的提示符和界面
- ✅ **ReAct 模式集成** - 完整集成 Day 3 的 ReAct 引擎，支持所有工具
- ✅ **聊天历史管理** - 会话历史保存、查看和搜索，支持导出
- ✅ **配置管理** - 个性化设置，API 配置，调试模式开关

### 高级功能
- ✅ **多会话支持** - 会话切换和管理
- ✅ **状态监控** - 实时显示 Agent 状态和性能统计
- ✅ **命令系统** - 内置命令帮助，快捷操作支持
- ✅ **批处理模式** - 处理命令文件，批量执行任务

## 🚀 快速开始

### 环境要求
- Python 3.12+
- OpenAI API Key

### 安装依赖
```bash
# 使用 uv 安装依赖
uv sync
```

### 设置环境变量
```bash
# 设置 OpenAI API Key
export OPENAI_API_KEY=your_key_here
```

### 运行应用

#### 1. 交互模式（推荐）
```bash
# 启动交互式聊天
python src/day4_cli/app.py run

# 或使用 uv
uv run python src/day4_cli/app.py run
```

#### 2. 调试模式
```bash
# 启用调试模式
python src/day4_cli/app.py run --debug
```

#### 3. 批处理模式
```bash
# 批处理文件中的查询
python src/day4_cli/app.py run --batch queries.txt --output results.json
```

#### 4. 配置管理
```bash
# 查看所有配置
python src/day4_cli/app.py config --all

# 查看特定配置
python src/day4_cli/app.py config debug_mode

# 修改配置
python src/day4_cli/app.py config debug_mode true
python src/day4_cli/app.py config max_steps 15
```

#### 5. 演示模式
```bash
# 运行功能演示
python src/day4_cli/app.py demo
```

## 💬 基本使用

### 交互式聊天
```bash
🤖 Assistant> 你好，我想了解今天的天气情况

# AI 会使用 ReAct 模式处理您的请求：
# 1. 思考：用户询问天气，需要使用天气查询工具
# 2. 行动：调用 get_weather 工具
# 3. 观察：分析天气查询结果
# 4. 回答：提供天气信息和建议
```

### 命令系统
应用支持丰富的内置命令：

```bash
# 帮助命令
/help                    # 显示所有可用命令
/help <command>         # 查看特定命令帮助

# 会话管理
/new [会话名]           # 创建新会话
/list                   # 列出所有会话
/switch <会话ID或名称>  # 切换会话
/delete <会话ID或名称>  # 删除会话

# 历史记录
/history [数量]         # 显示聊天历史
/clear                  # 清空当前会话
/export [文件路径]      # 导出会话到文件

# 配置管理
/config                # 显示常用配置
/config <项>           # 查看特定配置
/config <项> <值>      # 修改配置

# 信息查询
/stats                  # 显示使用统计
/version               # 显示版本信息

# 程序控制
/quit                   # 退出程序
```

## ⚙️ 配置选项

### 主要配置项
- `debug_mode`: 调试模式开关 (默认: false)
- `max_steps`: ReAct 最大执行步数 (默认: 10)
- `show_thinking_process`: 显示思考过程 (默认: true)
- `show_tool_calls`: 显示工具调用 (默认: true)
- `show_execution_trace`: 显示执行轨迹 (默认: false)
- `colored_output`: 彩色输出 (默认: true)
- `max_history_length`: 最大历史记录长度 (默认: 100)
- `auto_save_history`: 自动保存历史记录 (默认: true)

### 配置文件
配置文件位置：`~/.ai_assistant/config.yaml`

```yaml
app_name: "AI Assistant CLI"
version: "1.0.0"
debug_mode: false
max_steps: 10
show_thinking_process: true
show_tool_calls: true
colored_output: true
max_history_length: 100
auto_save_history: true
```

## 🔧 ReAct 工具集成

应用集成了 Day 3 的所有 6 个工具：

1. **计算器** (`calculator`)
   - 数学运算、三角函数、对数等
   - 示例：`计算 123 * 456`

2. **天气查询** (`get_weather`)
   - 查询城市天气信息
   - 示例：`查询北京今天的天气`

3. **网络搜索** (`web_search`)
   - 搜索互联网信息
   - 示例：`搜索 Python 最新特性`

4. **文本分析** (`text_analyzer`)
   - 情感分析、关键词提取、长度统计
   - 示例：`分析这段文字的情感`

5. **时间查询** (`current_time`)
   - 查询当前时间，支持不同时区
   - 示例：`现在几点了？`

6. **内存存储** (`memory_store`)
   - 会话期间的数据存储和检索
   - 示例：`记住我的名字是张三`

## 📁 项目结构

```
src/day4_cli/
├── README.md           # 本文件 - 项目说明
├── day4.md            # 开发需求和说明
├── app.py             # 主应用程序入口
├── cli_interface.py   # CLI 界面核心逻辑
├── chat_manager.py    # 聊天会话管理
├── config.py          # 配置管理
├── commands.py        # CLI 命令处理
├── demo.py            # 功能演示程序
├── test_cli.py        # 测试套件
└── __init__.py        # 模块初始化
```

## 🧪 测试

### 运行演示程序
```bash
# 运行完整功能演示
uv run python src/day4_cli/demo.py

# 运行应用内置演示
uv run python src/day4_cli/app.py demo
```

### 运行测试套件
```bash
# 运行所有测试
uv run python src/day4_cli/test_cli.py

# 测试覆盖
# - 配置管理测试 (4个)
# - 聊天管理测试 (10个)
# - 命令系统测试 (6个)
# - CLI 界面测试 (4个)
# 总计：26个测试用例，100% 通过率
```

## 🎨 界面特色

### 美观的输出格式
- 🎨 **彩色输出** - 用户消息、AI回复、工具调用等使用不同颜色
- 📱 **面板显示** - 重要信息使用 Rich 面板展示
- 📊 **表格格式** - 会话列表、统计信息等使用表格展示
- ⏳ **加载动画** - 处理请求时显示美观的加载动画

### 智能交互体验
- 🔧 **命令补全** - 支持 Tab 键命令自动补全
- 💬 **会话切换** - 无缝切换不同聊天会话
- 📝 **历史管理** - 智能保存和恢复聊天历史
- ⚙️ **实时配置** - 运行时修改配置立即生效

## 🔍 调试和监控

### 调试模式
```bash
# 启动调试模式
python src/day4_cli/app.py run --debug

# 或在运行时启用
/config debug_mode true
```

调试模式会显示：
- 🧠 Agent 思考过程
- 🔧 工具调用详情
- 📊 执行轨迹信息
- ⏱️ 性能统计数据

### 统计信息
```bash
# 查看使用统计
/stats
```

显示信息包括：
- 总会话数和总消息数
- 当前会话详细信息
- 执行时间和成功率
- Agent 状态和配置

## 🚀 使用场景

### 1. 个人助手
```bash
# 日常对话和任务处理
🤖 Assistant> 帮我制定今天的工作计划
🤖 Assistant> 提醒我下午3点开会
🤖 Assistant> 查询明天去上海的天气预报
```

### 2. 学习辅导
```bash
# 学习辅助和知识查询
🤖 Assistant> 解释一下什么是 ReAct 模式
🤖 Assistant> 计算 sin(π/2) 的值
🤖 Assistant> 搜索最新的 AI 发展趋势
```

### 3. 批量任务
```bash
# 创建批处理文件 queries.txt
计算圆周率后100位
分析《三体》的主题思想
查询股票代码AAPL的最新价格

# 批量执行
python src/day4_cli/app.py run --batch queries.txt --output results.json
```

## 💡 最佳实践

### 1. 会话组织
- 为不同主题创建独立会话
- 使用描述性的会话名称
- 定期清理不需要的会话

### 2. 配置优化
- 根据需要调整显示选项
- 合理设置历史记录长度
- 在调试时启用详细日志

### 3. 工具使用
- 明确指定工具调用需求
- 提供充分的上下文信息
- 合理使用内存存储功能

## 🔮 扩展方向

1. **插件系统** - 支持自定义工具扩展
2. **语音交互** - 集成语音识别和合成
3. **多语言支持** - 国际化和本地化
4. **云端同步** - 跨设备会话同步
5. **团队协作** - 多用户会话共享

## 📞 技术支持

如果您在使用过程中遇到问题：

1. 查看内置帮助：`/help`
2. 检查配置：`/config --all`
3. 启用调试：`/config debug_mode true`
4. 运行演示：`python src/day4_cli/app.py demo`

---

**Day 4 CLI 聊天应用** - 展示了如何将 ReAct Agent 集成到生产级 CLI 应用中，提供优秀的用户体验和强大的功能。