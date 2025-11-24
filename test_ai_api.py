#!/usr/bin/env python3
"""
AI API 连接测试脚本

测试 DeepSeek API 是否正常工作
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ai_service import get_ai_service


def test_ai_service():
    """测试 AI 服务"""
    print("🧪 测试 AI API 连接")
    print("=" * 50)

    try:
        # 获取 AI 服务
        ai_service = get_ai_service("deepseek")

        # 显示配置信息
        info = ai_service.get_provider_info()
        print(f"📡 AI 提供商: {info['provider']}")
        print(f"🤖 模型: {info['model']}")
        print(f"🔗 API 地址: {info['base_url']}")
        print(f"🔑 API Key 配置: {'✅ 已设置' if info['has_api_key'] else '❌ 未设置'}")

        if not info['has_api_key']:
            print("\n❌ 错误: 请在 .env 文件中设置 DEEPSEEK_API_KEY")
            return False

        # 测试简单的对话
        print("\n📝 测试基础对话...")
        messages = [
            {"role": "user", "content": "请用一句话介绍 DeepSeek"}
        ]

        result = ai_service.chat_completion(messages, max_tokens=100)

        if result["success"]:
            print(f"✅ 对话成功!")
            print(f"📄 回复: {result['content'][:200]}...")
            if result["usage"]:
                print(f"📊 Token 使用: {result['usage']['total_tokens']} (输入: {result['usage']['prompt_tokens']}, 输出: {result['usage']['completion_tokens']})")
        else:
            print(f"❌ 对话失败: {result['error']}")
            return False

        # 测试文档分析
        print("\n📋 测试文档分析...")
        test_doc = """
        # 项目总结

        本项目取得了非常成功的结果。
        团队表现出色，完成了所有预定目标。
        主要成就包括：
        1. 性能提升50%
        2. 成本降低30%
        3. 用户满意度达到95%
        """

        analysis_result = ai_service.analyze_document(test_doc, "general")

        if analysis_result["success"]:
            print(f"✅ 文档分析成功!")
            print(f"📄 分析结果预览: {analysis_result['content'][:200]}...")
            if analysis_result["usage"]:
                print(f"📊 Token 使用: {analysis_result['usage']['total_tokens']}")
        else:
            print(f"❌ 文档分析失败: {analysis_result['error']}")
            return False

        # 测试情感分析
        print("\n😊 测试情感分析...")
        sentiment_result = ai_service.sentiment_analysis("这个产品真的很棒，我非常喜欢！")

        if sentiment_result["success"]:
            print(f"✅ 情感分析成功!")
            print(f"📄 情感结果: {sentiment_result['content'][:200]}...")
        else:
            print(f"❌ 情感分析失败: {sentiment_result['error']}")

        print("\n🎉 所有测试完成! DeepSeek API 工作正常。")
        return True

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        print("\n🔧 请检查以下配置:")
        print("1. .env 文件是否存在")
        print("2. DEEPSEEK_API_KEY 是否正确设置")
        print("3. 网络连接是否正常")
        return False


def test_env_setup():
    """检查环境配置"""
    print("🔍 检查环境配置")
    print("=" * 30)

    # 检查 .env 文件
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ {env_file} 文件存在")

        # 检查关键环境变量
        load_dotenv()
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            if deepseek_key == "your_deepseek_api_key_here":
                print("⚠️  DEEPSEEK_API_KEY 需要设置真实的 API Key")
                return False
            elif len(deepseek_key) > 10:
                print(f"✅ DEEPSEEK_API_KEY 已设置 (长度: {len(deepseek_key)})")
                return True
            else:
                print("❌ DEEPSEEK_API_KEY 长度不正确")
                return False
        else:
            print("❌ DEEPSEEK_API_KEY 未设置")
            return False
    else:
        print(f"❌ {env_file} 文件不存在")
        return False


if __name__ == "__main__":
    # 导入 load_dotenv
    from dotenv import load_dotenv

    print("🚀 AI API 连接测试")
    print("=" * 60)

    # 检查环境配置
    env_ok = test_env_setup()

    if env_ok:
        print()
        # 测试 AI 服务
        api_ok = test_ai_service()

        if api_ok:
            print("\n✅ 所有测试通过! 您可以开始使用 AI 功能了。")
        else:
            print("\n❌ API 测试失败，请检查配置。")
    else:
        print("\n❌ 环境配置有问题，请先修复配置。")
        print("\n💡 解决方案:")
        print("1. 确保在 .env 文件中设置了正确的 DEEPSEEK_API_KEY")
        print("2. API Key 格式应为 'sk-xxxxx'")
        print("3. 确保网络连接正常")