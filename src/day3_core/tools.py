"""
ReAct Tools - Agent 的"手"

定义所有 AI 可以调用的工具函数，使用策略模式实现。

这本质上就是一个 Dict[str, Callable]，关键在于 TOOLS_SCHEMA 变量，
这是给 LLM 看的"说明书"。如果说明书写得不好（description 不清楚），
LLM 就不知道什么时候用这个策略。
"""

import json
import time
import math
import re
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime
from rich.console import Console

# 注释掉 requests，因为在这个演示中没有实际使用
# import requests

console = Console()


# 基础工具类型定义
class ToolResult:
    """工具执行结果"""
    def __init__(self, success: bool, data: Any = None, error: str = None, metadata: Dict[str, Any] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


# 工具函数定义
def calculator(expression: str) -> ToolResult:
    """
    数学计算工具

    Args:
        expression (str): 数学表达式，如 "123 + 456" 或 "sin(0.5)"

    Returns:
        ToolResult: 计算结果或错误信息
    """
    try:
        # 安全的数学表达式评估
        # 只允许数字、基本运算符和数学函数
        allowed_chars = set('0123456789+-*/.()[]{}sincostanlogsqrtexpabs')
        if not all(c in allowed_chars or c.isspace() for c in expression):
            return ToolResult(False, error="表达式包含不允许的字符")

        # 使用 eval 进行计算（注意：生产环境中应该用更安全的方式）
        # 创建安全的命名空间
        safe_dict = {
            '__builtins__': {},
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'sqrt': math.sqrt,
            'exp': math.exp,
            'abs': abs,
            'pi': math.pi,
            'e': math.e
        }

        result = eval(expression, safe_dict, {})

        return ToolResult(True, data={
            "expression": expression,
            "result": result,
            "type": type(result).__name__
        })

    except Exception as e:
        return ToolResult(False, error=f"计算错误: {str(e)}")


def web_search(query: str, num_results: int = 5) -> ToolResult:
    """
    网络搜索工具（模拟实现）

    Args:
        query (str): 搜索查询
        num_results (int): 返回结果数量，默认5个

    Returns:
        ToolResult: 搜索结果
    """
    try:
        # 这里模拟网络搜索
        # 在实际应用中，应该调用真实的搜索 API，如 Google Search API, Bing Search API 等

        # 模拟搜索延迟
        time.sleep(0.5)

        # 模拟搜索结果
        mock_results = [
            {
                "title": f"关于'{query}'的搜索结果 {i+1}",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"这是关于{query}的第{i+1}个搜索结果摘要...",
                "relevance": 0.9 - i * 0.1
            }
            for i in range(min(num_results, 5))
        ]

        return ToolResult(True, data={
            "query": query,
            "results": mock_results,
            "total_results": len(mock_results),
            "search_time": 0.5
        })

    except Exception as e:
        return ToolResult(False, error=f"搜索失败: {str(e)}")


def get_weather(city: str) -> ToolResult:
    """
    天气查询工具（模拟实现）

    Args:
        city (str): 城市名称

    Returns:
        ToolResult: 天气信息
    """
    try:
        # 模拟天气数据
        weather_data = {
            "北京": {"temp": 25, "weather": "晴天", "humidity": 45, "wind": "北风3级"},
            "上海": {"temp": 28, "weather": "多云", "humidity": 65, "wind": "东南风2级"},
            "广州": {"temp": 32, "weather": "阵雨", "humidity": 78, "wind": "南风2级"},
            "深圳": {"temp": 30, "weather": "晴天", "humidity": 70, "wind": "东风3级"},
            "成都": {"temp": 22, "weather": "阴天", "humidity": 80, "wind": "无风"},
        }

        if city not in weather_data:
            # 返回默认天气数据
            weather_data[city] = {
                "temp": 20,
                "weather": "未知",
                "humidity": 50,
                "wind": "未知"
            }

        city_weather = weather_data[city]

        return ToolResult(True, data={
            "city": city,
            "temperature": city_weather["temp"],
            "weather": city_weather["weather"],
            "humidity": city_weather["humidity"],
            "wind": city_weather["wind"],
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        return ToolResult(False, error=f"天气查询失败: {str(e)}")


def text_analyzer(text: str, analysis_type: str = "sentiment") -> ToolResult:
    """
    文本分析工具

    Args:
        text (str): 要分析的文本
        analysis_type (str): 分析类型，支持 "sentiment", "keywords", "length"

    Returns:
        ToolResult: 分析结果
    """
    try:
        if analysis_type == "sentiment":
            # 简单的情感分析（基于关键词）
            positive_words = ["好", "棒", "优秀", "喜欢", "开心", "满意", "完美", "amazing", "good", "great"]
            negative_words = ["差", "糟糕", "失败", "讨厌", "失望", "问题", "错误", "bad", "terrible", "awful"]

            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if positive_count > negative_count:
                sentiment = "positive"
                score = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
            elif negative_count > positive_count:
                sentiment = "negative"
                score = max(0.1, 0.5 - (negative_count - positive_count) * 0.1)
            else:
                sentiment = "neutral"
                score = 0.5

            return ToolResult(True, data={
                "text": text,
                "sentiment": sentiment,
                "confidence": score,
                "positive_words": positive_count,
                "negative_words": negative_count
            })

        elif analysis_type == "keywords":
            # 简单的关键词提取
            # 移除标点符号并分割单词
            words = re.findall(r'\b\w+\b', text.lower())
            # 过滤停用词（简单实现）
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "的", "了", "在", "是", "我", "有", "和"}
            filtered_words = [word for word in words if word not in stop_words and len(word) > 2]

            # 统计词频
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1

            # 取前10个高频词
            keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

            return ToolResult(True, data={
                "text": text,
                "keywords": [{"word": word, "frequency": freq} for word, freq in keywords],
                "total_words": len(words)
            })

        elif analysis_type == "length":
            # 文本长度分析
            return ToolResult(True, data={
                "text": text,
                "character_count": len(text),
                "word_count": len(text.split()),
                "line_count": len(text.split('\n')),
                "sentence_count": len(re.split(r'[.!?]+', text))
            })

        else:
            return ToolResult(False, error=f"不支持的分析类型: {analysis_type}")

    except Exception as e:
        return ToolResult(False, error=f"文本分析失败: {str(e)}")


def current_time(timezone: str = "local") -> ToolResult:
    """
    时间查询工具

    Args:
        timezone (str): 时区，支持 "local", "utc", "beijing", "new_york"

    Returns:
        ToolResult: 当前时间信息
    """
    try:
        now = datetime.now()

        # 简单的时区处理（实际应用中应该使用 pytz 或类似的库）
        timezones = {
            "local": now,
            "utc": datetime.utcnow(),
            "beijing": now,  # 简化处理
            "new_york": now  # 简化处理
        }

        tz_time = timezones.get(timezone, now)

        return ToolResult(True, data={
            "timezone": timezone,
            "current_time": tz_time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": tz_time.timestamp(),
            "weekday": tz_time.strftime("%A"),
            "date": tz_time.strftime("%Y-%m-%d"),
            "time": tz_time.strftime("%H:%M:%S")
        })

    except Exception as e:
        return ToolResult(False, error=f"时间查询失败: {str(e)}")


def memory_store(key: str, value: str = "", operation: str = "set") -> ToolResult:
    """
    内存存储工具（简单实现，在会话期间有效）

    Args:
        key (str): 存储键
        value (str): 存储值（get 操作时可为空）
        operation (str): 操作类型，支持 "set", "get", "delete"

    Returns:
        ToolResult: 操作结果
    """
    try:
        # 这里使用一个全局字典来存储数据
        # 在实际应用中，应该使用数据库或文件系统
        global _memory_store

        if '_memory_store' not in globals():
            _memory_store = {}

        if operation == "set":
            _memory_store[key] = value
            return ToolResult(True, data={
                "operation": "set",
                "key": key,
                "value": value,
                "message": f"已存储: {key} = {value}"
            })
        elif operation == "get":
            if key in _memory_store:
                return ToolResult(True, data={
                    "operation": "get",
                    "key": key,
                    "value": _memory_store[key],
                    "found": True
                })
            else:
                return ToolResult(True, data={
                    "operation": "get",
                    "key": key,
                    "found": False,
                    "message": f"键 '{key}' 不存在"
                })
        elif operation == "delete":
            if key in _memory_store:
                del _memory_store[key]
                return ToolResult(True, data={
                    "operation": "delete",
                    "key": key,
                    "message": f"已删除键: {key}"
                })
            else:
                return ToolResult(False, error=f"键 '{key}' 不存在")
        else:
            return ToolResult(False, error=f"不支持的操作类型: {operation}")

    except Exception as e:
        return ToolResult(False, error=f"内存操作失败: {str(e)}")


# 工具注册表
TOOLS: Dict[str, Callable] = {
    "calculator": calculator,
    "web_search": web_search,
    "get_weather": get_weather,
    "text_analyzer": text_analyzer,
    "current_time": current_time,
    "memory_store": memory_store,
}


# 工具 Schema - 这是给 LLM 看的"说明书"
TOOLS_SCHEMA = [
    {
        "name": "calculator",
        "description": "数学计算工具，可以执行各种数学运算，包括加减乘除、三角函数、对数、指数等。适用于需要精确计算的场景。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，例如：'123 + 456', 'sin(0.5)', 'sqrt(16)', 'log(10)'"
                }
            },
            "required": ["expression"]
        },
        "examples": [
            {"expression": "123 + 456"},
            {"expression": "sin(3.14159 / 2)"},
            {"expression": "sqrt(144)"},
            {"expression": "log(100)"}
        ]
    },
    {
        "name": "web_search",
        "description": "网络搜索工具，用于搜索互联网上的信息。当你需要查找最新信息、背景知识或具体数据时使用此工具。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询词，要简洁明确，例如：'Python编程教程', '最新AI发展', '北京天气'"
                },
                "num_results": {
                    "type": "integer",
                    "description": "返回搜索结果的数量，默认为5个，范围1-10",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        },
        "examples": [
            {"query": "Python异步编程最佳实践", "num_results": 3},
            {"query": "2024年AI发展趋势", "num_results": 5}
        ]
    },
    {
        "name": "get_weather",
        "description": "天气查询工具，用于查询指定城市的天气信息，包括温度、天气状况、湿度和风力等信息。",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如：'北京', '上海', '广州', '深圳', '成都'"
                }
            },
            "required": ["city"]
        },
        "examples": [
            {"city": "北京"},
            {"city": "上海"}
        ]
    },
    {
        "name": "text_analyzer",
        "description": "文本分析工具，可以对文本进行情感分析、关键词提取、长度统计等。适用于需要理解文本内容和特征的场景。",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要分析的文本内容"
                },
                "analysis_type": {
                    "type": "string",
                    "description": "分析类型：'sentiment'(情感分析), 'keywords'(关键词提取), 'length'(长度统计)",
                    "enum": ["sentiment", "keywords", "length"],
                    "default": "sentiment"
                }
            },
            "required": ["text"]
        },
        "examples": [
            {"text": "这个产品真的很棒，我非常喜欢！", "analysis_type": "sentiment"},
            {"text": "Python是一种流行的编程语言", "analysis_type": "keywords"}
        ]
    },
    {
        "name": "current_time",
        "description": "时间查询工具，用于获取当前时间信息。支持不同时区的时间查询。",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "时区：'local'(本地时间), 'utc'(UTC时间), 'beijing'(北京时间), 'new_york'(纽约时间)",
                    "enum": ["local", "utc", "beijing", "new_york"],
                    "default": "local"
                }
            },
            "required": []
        },
        "examples": [
            {"timezone": "local"},
            {"timezone": "utc"},
            {"timezone": "beijing"}
        ]
    },
    {
        "name": "memory_store",
        "description": "内存存储工具，用于在会话期间临时存储和检索信息。可以记住用户之前提供的信息或中间计算结果。",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "存储键，用于标识存储的内容"
                },
                "value": {
                    "type": "string",
                    "description": "存储的值，仅在set操作时需要"
                },
                "operation": {
                    "type": "string",
                    "description": "操作类型：'set'(存储), 'get'(获取), 'delete'(删除)",
                    "enum": ["set", "get", "delete"],
                    "default": "set"
                }
            },
            "required": ["key"]
        },
        "examples": [
            {"key": "user_name", "value": "张三", "operation": "set"},
            {"key": "user_name", "operation": "get"}
        ]
    }
]


# 工具执行器
class ToolExecutor:
    """工具执行器"""

    @staticmethod
    def execute(tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """
        执行指定工具

        Args:
            tool_name (str): 工具名称
            parameters (Dict[str, Any]): 工具参数

        Returns:
            ToolResult: 执行结果
        """
        if tool_name not in TOOLS:
            return ToolResult(False, error=f"未知工具: {tool_name}")

        try:
            tool_func = TOOLS[tool_name]
            result = tool_func(**parameters)
            return result
        except TypeError as e:
            return ToolResult(False, error=f"参数错误: {str(e)}")
        except Exception as e:
            return ToolResult(False, error=f"工具执行失败: {str(e)}")

    @staticmethod
    def get_available_tools() -> List[str]:
        """获取可用工具列表"""
        return list(TOOLS.keys())

    @staticmethod
    def get_tool_schema(tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具的 schema 信息"""
        for tool in TOOLS_SCHEMA:
            if tool["name"] == tool_name:
                return tool
        return None


# 便捷函数
def get_tools_description() -> str:
    """获取所有工具的描述信息，用于 prompt"""
    descriptions = []
    for tool in TOOLS_SCHEMA:
        desc = f"- **{tool['name']}**: {tool['description']}"
        if 'examples' in tool:
            examples_text = ", ".join([f"{ex}" for ex in tool['examples'][:2]])
            desc += f"\n  示例: {examples_text}"
        descriptions.append(desc)

    return "\n\n".join(descriptions)


if __name__ == "__main__":
    # 测试工具
    console.print("🧪 测试 ReAct Tools", style="bold blue")

    # 测试计算器
    console.print("\n📊 测试计算器:")
    result = calculator("123 + 456")
    console.print(f"结果: {result.to_dict()}")

    # 测试天气查询
    console.print("\n🌤️ 测试天气查询:")
    result = get_weather("北京")
    console.print(f"结果: {result.to_dict()}")

    # 测试文本分析
    console.print("\n📝 测试文本分析:")
    result = text_analyzer("这个产品真的很棒，我非常喜欢！", "sentiment")
    console.print(f"结果: {result.to_dict()}")

    console.print("\n✅ Tools 测试完成")