"""
AI Service - 统一的AI接口服务

支持 DeepSeek 和 OpenAI API，提供统一的调用接口
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()


@dataclass
class AIConfig:
    """AI配置类"""
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30


class AIService:
    """AI服务类 - 统一的AI接口"""

    def __init__(self, provider: str = "deepseek"):
        self.provider = provider
        self.config = self._load_config(provider)
        self.client = self._create_client()

    def _load_config(self, provider: str) -> AIConfig:
        """加载AI配置"""
        if provider == "deepseek":
            return AIConfig(
                api_key=os.getenv("DEEPSEEK_API_KEY", ""),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                model="deepseek-chat"
            )
        elif provider == "openai":
            return AIConfig(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                base_url="https://api.openai.com/v1",
                model="gpt-3.5-turbo"
            )
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")

    def _create_client(self) -> OpenAI:
        """创建OpenAI客户端"""
        if not self.config.api_key:
            raise ValueError(f"未设置 {self.provider.upper()}_API_KEY 环境变量")

        return OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )

    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """聊天完成接口"""
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.config.model),
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                **{k: v for k, v in kwargs.items()
                   if k not in ["model", "max_tokens", "temperature"]}
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None,
                "model": response.model,
                "provider": self.provider
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": self.provider
            }

    def analyze_document(self, content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """文档分析接口"""
        prompts = {
            "legal": """
            请分析以下法律文档，提取关键信息：

            文档内容：
            {content}

            请以JSON格式返回：
            {{
                "key_clauses": ["关键条款1", "关键条款2"],
                "legal_concepts": ["法律概念1", "法律概念2"],
                "parties": ["当事人1", "当事人2"],
                "important_dates": ["日期1", "日期2"],
                "obligations": ["义务1", "义务2"],
                "risk_level": "high/medium/low"
            }}
            """,

            "technical": """
            请分析以下技术文档：

            文档内容：
            {content}

            请以Markdown格式返回：
            ## 技术概念
            - 概念1：说明
            - 概念2：说明

            ## 代码示例
            ```code
            重要的代码片段
            ```

            ## 关键要点
            - 要点1
            - 要点2
            """,

            "academic": """
            请分析以下学术文档：

            文档内容：
            {content}

            请以结构化格式返回：
            ### 研究问题
            主要研究问题...

            ### 研究方法
            使用的方法...

            ### 主要发现
            发现1，发现2...

            ### 研究贡献
            贡献1，贡献2...
            """,

            "general": """
            请分析以下文档，提取关键信息：

            文档内容：
            {content}

            请返回：
            - 主要观点
            - 关键信息
            - 内容摘要
            - 重要数据
            """
        }

        prompt = prompts.get(analysis_type, prompts["general"])
        messages = [
            {"role": "user", "content": prompt.format(content=content)}
        ]

        return self.chat_completion(messages, temperature=0.3)

    def extract_summary(self, content: str, max_length: int = 200) -> Dict[str, Any]:
        """生成文档摘要"""
        prompt = f"""
        请为以下文档生成简洁的摘要（不超过{max_length}字）：

        文档内容：
        {content}

        摘要：
        """

        messages = [
            {"role": "user", "content": prompt}
        ]

        return self.chat_completion(messages, temperature=0.5, max_tokens=max_length)

    def sentiment_analysis(self, content: str) -> Dict[str, Any]:
        """情感分析"""
        prompt = """
        请分析以下文本的情感倾向：

        文本内容：
        {content}

        请以JSON格式返回：
        {{
            "sentiment": "positive/negative/neutral",
            "confidence": 0.95,
            "key_emotions": ["情感1", "情感2"],
            "explanation": "分析说明"
        }}
        """.format(content=content)

        messages = [
            {"role": "user", "content": prompt}
        ]

        return self.chat_completion(messages, temperature=0.1)

    def extract_keywords(self, content: str, max_keywords: int = 10) -> Dict[str, Any]:
        """关键词提取"""
        prompt = f"""
        请从以下文本中提取{max_keywords}个最重要的关键词：

        文本内容：
        {content}

        请以JSON格式返回：
        {{
            "keywords": ["关键词1", "关键词2", ...],
            "categories": ["类别1", "类别2"]
        }}
        """

        messages = [
            {"role": "user", "content": prompt}
        ]

        return self.chat_completion(messages, temperature=0.2)

    def translate_text(self, text: str, target_language: str = "English") -> Dict[str, Any]:
        """文本翻译"""
        prompt = f"""
        请将以下文本翻译成{target_language}：

        原文：
        {text}

        翻译：
        """

        messages = [
            {"role": "user", "content": prompt}
        ]

        return self.chat_completion(messages, temperature=0.3)

    def get_provider_info(self) -> Dict[str, Any]:
        """获取提供商信息"""
        return {
            "provider": self.provider,
            "model": self.config.model,
            "base_url": self.config.base_url,
            "has_api_key": bool(self.config.api_key)
        }


# 全局AI服务实例
_ai_service = None

def get_ai_service(provider: str = "deepseek") -> AIService:
    """获取AI服务实例（单例模式）"""
    global _ai_service
    if _ai_service is None or _ai_service.provider != provider:
        _ai_service = AIService(provider)
    return _ai_service


# 便捷函数
def analyze_document(content: str, analysis_type: str = "general") -> Dict[str, Any]:
    """便捷的文档分析函数"""
    return get_ai_service().analyze_document(content, analysis_type)

def extract_summary(content: str, max_length: int = 200) -> Dict[str, Any]:
    """便捷的摘要生成函数"""
    return get_ai_service().extract_summary(content, max_length)

def sentiment_analysis(content: str) -> Dict[str, Any]:
    """便捷的情感分析函数"""
    return get_ai_service().sentiment_analysis(content)


# 示例使用
if __name__ == "__main__":
    # 创建AI服务
    ai_service = get_ai_service("deepseek")

    # 显示提供商信息
    info = ai_service.get_provider_info()
    print(f"AI提供商: {info['provider']}")
    print(f"模型: {info['model']}")
    print(f"API Key已设置: {info['has_api_key']}")

    # 测试文档
    test_content = """
    这是一份关于人工智能发展的报告。
    报告指出，近年来AI技术在各个领域都取得了显著进展。
    特别是在自然语言处理和计算机视觉方面，突破性成果不断涌现。
    """

    print("\n📝 测试文档分析:")
    result = ai_service.analyze_document(test_content, "general")
    if result["success"]:
        print(result["content"])
    else:
        print(f"分析失败: {result['error']}")