## TODO
- [x] 按照下面的工程目录生成项目
- [x] 完成day1 的代码开发和知识梳理
- [x] 完成day2 的代码开发和知识梳理
- [x] 完成day3 的代码开发和知识梳理
- [ ] 完成day4 的最终的对话项目

## 工程目录

agent-lab/
├── .env                # 存放 OPENAI_API_KEY
├── pyproject.toml      # uv 管理的依赖文件
├── src/
│   ├── __init__.py
│   ├── main.py         # 程序入口
│   ├── day1_patterns/  # Day 1: 设计模式
│   │   ├── __init__.py
│   │   └── chain.py
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
└── README.md

