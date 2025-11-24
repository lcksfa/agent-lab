"""
Chain Pattern Implementation

Day 1: Design patterns for AI agents

注意：这是原来的 chain.py 文件，现在保留作为参考。
实际的演示代码已经分离到独立的文件中：
- strategy.py: 策略模式实现
- decorator.py: 装饰器模式实现
- responsibility_chain.py: 责任链模式实现
- demo.py: 三种模式的综合演示
"""

# 这个文件可以继续使用或者被其他模块替换

# src/day1_patterns/chain.py
from abc import ABC, abstractmethod
from typing import Optional

# 定义处理器的抽象基类
class Handler(ABC):
    def __init__(self, next_handler: Optional['Handler'] = None):
        self.next_handler = next_handler

    @abstractmethod
    def handle(self, request: str) -> str:
        if self.next_handler:
            return self.next_handler.handle(request)
        return request

# 1. 安全过滤器 (例如：防止 Prompt 注入)
class SafetyFilter(Handler):
    def handle(self, request: str) -> str:
        if "IGNORE ALL INSTRUCTIONS" in request:
            return "Error: Unsafe input detected."
        print(f"[Safety] Input '{request}' is safe.")
        return super().handle(request)

# 2. 提示词增强器 (给用户的输入加点料)
class PromptEnhancer(Handler):
    def handle(self, request: str) -> str:
        enhanced_request = f"{request}\n(Please answer concisely)"
        print(f"[Enhancer] Modified prompt: {enhanced_request}")
        return super().handle(enhanced_request)

# 3. 模拟 AI 调用 (这里先不真调 API，模拟一下)
class MockAIModel(Handler):
    def handle(self, request: str) -> str:
        print("[AI] Generating response...")
        return f"AI Response to: {request}"

# 运行示例
def run_chain_demo():
    # 构建链条: 安全检查 -> 提示词增强 -> AI 生成
    chain = SafetyFilter(PromptEnhancer(MockAIModel()))
    
    user_input = "Hello, world!"
    result = chain.handle(user_input)
    print(f"\nFinal Result: {result}")

if __name__ == "__main__":
    run_chain_demo()
