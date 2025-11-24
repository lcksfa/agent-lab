#!/usr/bin/env python3
"""
Day 4 CLI 聊天应用测试套件

全面测试 CLI 应用的各个组件和功能。
"""

import os
import sys
import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent.parent))

# 导入测试目标
from src.day4_cli.config import CLIConfig, get_config
from src.day4_cli.chat_manager import ChatManager, ChatSession, ChatMessage
from src.day4_cli.commands import CommandRegistry, HelpCommand, NewCommand, CLICommand, CommandResult
from src.day4_cli.cli_interface import CLIInterface


class TestCLIConfig(unittest.TestCase):
    """测试配置管理"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")

    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_creation(self):
        """测试配置创建"""
        config = CLIConfig(debug_mode=True, max_steps=5)

        self.assertEqual(config.app_name, "AI Assistant CLI")
        self.assertTrue(config.debug_mode)
        self.assertEqual(config.max_steps, 5)

    def test_config_save_and_load(self):
        """测试配置保存和加载"""
        # 创建配置
        original_config = CLIConfig(
            debug_mode=True,
            max_steps=8,
            show_thinking_process=False
        )

        # 保存配置
        original_config.save_to_file(self.config_file)
        self.assertTrue(os.path.exists(self.config_file))

        # 加载配置
        loaded_config = CLIConfig.load_from_file(self.config_file)

        self.assertEqual(loaded_config.debug_mode, True)
        self.assertEqual(loaded_config.max_steps, 8)
        self.assertEqual(loaded_config.show_thinking_process, False)

    def test_config_update(self):
        """测试配置更新"""
        config = CLIConfig()

        config.update(debug_mode=True, max_steps=15)
        self.assertTrue(config.debug_mode)
        self.assertEqual(config.max_steps, 15)

        # 测试无效配置项
        config.update(invalid_key="value")  # 应该不会抛出错误

    def test_config_dict_conversion(self):
        """测试配置字典转换"""
        config = CLIConfig(debug_mode=True, max_steps=10)
        config_dict = config.get_dict()

        self.assertIn("debug_mode", config_dict)
        self.assertIn("max_steps", config_dict)
        self.assertTrue(config_dict["debug_mode"])
        self.assertEqual(config_dict["max_steps"], 10)


class TestChatMessage(unittest.TestCase):
    """测试聊天消息"""

    def test_message_creation(self):
        """测试消息创建"""
        message = ChatMessage(role="user", content="Hello")

        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello")
        self.assertIsNotNone(message.id)
        self.assertIsNotNone(message.timestamp)

    def test_message_serialization(self):
        """测试消息序列化"""
        message = ChatMessage(role="assistant", content="Hi there!")
        message_dict = message.to_dict()

        self.assertEqual(message_dict["role"], "assistant")
        self.assertEqual(message_dict["content"], "Hi there!")
        self.assertIn("id", message_dict)
        self.assertIn("timestamp", message_dict)

        # 测试反序列化
        restored_message = ChatMessage.from_dict(message_dict)
        self.assertEqual(restored_message.role, message.role)
        self.assertEqual(restored_message.content, message.content)
        self.assertEqual(restored_message.id, message.id)


class TestChatSession(unittest.TestCase):
    """测试聊天会话"""

    def setUp(self):
        """测试前准备"""
        self.session = ChatSession(name="Test Session")

    def test_session_creation(self):
        """测试会话创建"""
        self.assertEqual(self.session.name, "Test Session")
        self.assertEqual(len(self.session.messages), 0)
        self.assertIsNotNone(self.session.id)
        self.assertIsNotNone(self.session.created_at)

    def test_add_message(self):
        """测试添加消息"""
        user_message = self.session.add_message("user", "Hello")
        assistant_message = self.session.add_message("assistant", "Hi there!")

        self.assertEqual(len(self.session.messages), 2)
        self.assertEqual(self.session.messages[0].role, "user")
        self.assertEqual(self.session.messages[1].role, "assistant")

    def test_get_last_messages(self):
        """测试获取最后消息"""
        for i in range(5):
            self.session.add_message("user", f"Message {i}")

        last_messages = self.session.get_last_messages(3)
        self.assertEqual(len(last_messages), 3)
        self.assertEqual(last_messages[0].content, "Message 2")
        self.assertEqual(last_messages[2].content, "Message 4")

    def test_clear_messages(self):
        """测试清空消息"""
        self.session.add_message("user", "Hello")
        self.session.add_message("assistant", "Hi")
        self.assertEqual(len(self.session.messages), 2)

        self.session.clear_messages()
        self.assertEqual(len(self.session.messages), 0)


class TestChatManager(unittest.TestCase):
    """测试聊天管理器"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()

        # 模拟配置
        with patch('src.day4_cli.chat_manager.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.sessions_dir_path = Path(self.temp_dir)
            mock_get_config.return_value = mock_config

            self.chat_manager = ChatManager()

    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_session(self):
        """测试创建会话"""
        session = self.chat_manager.create_session("Test Session")

        self.assertIsNotNone(session)
        self.assertEqual(session.name, "Test Session")
        self.assertIn(session.id, self.chat_manager.sessions)

    def test_add_user_message(self):
        """测试添加用户消息"""
        self.chat_manager.create_session("Test")
        message = self.chat_manager.add_user_message("Hello")

        self.assertIsNotNone(message)
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello")

    def test_add_assistant_message(self):
        """测试添加助手消息"""
        self.chat_manager.create_session("Test")
        message = self.chat_manager.add_assistant_message("Hi there!")

        self.assertIsNotNone(message)
        self.assertEqual(message.role, "assistant")
        self.assertEqual(message.content, "Hi there!")

    def test_switch_session(self):
        """测试切换会话"""
        session1 = self.chat_manager.create_session("Session 1")
        session2 = self.chat_manager.create_session("Session 2")

        # 切换到第一个会话
        result = self.chat_manager.switch_session(session1.id)
        self.assertTrue(result)
        self.assertEqual(self.chat_manager.current_session_id, session1.id)

        # 切换到第二个会话
        result = self.chat_manager.switch_session(session2.id)
        self.assertTrue(result)
        self.assertEqual(self.chat_manager.current_session_id, session2.id)

    def test_delete_session(self):
        """测试删除会话"""
        session = self.chat_manager.create_session("To Delete")
        session_id = session.id

        result = self.chat_manager.delete_session(session_id)
        self.assertTrue(result)
        self.assertNotIn(session_id, self.chat_manager.sessions)

    def test_get_statistics(self):
        """测试获取统计信息"""
        self.chat_manager.create_session("Session 1")
        self.chat_manager.add_user_message("Hello")
        self.chat_manager.add_assistant_message("Hi")

        stats = self.chat_manager.get_statistics()

        self.assertEqual(stats["total_sessions"], 1)
        self.assertEqual(stats["total_messages"], 2)
        self.assertEqual(stats["current_session_messages"], 2)


class TestCommandSystem(unittest.TestCase):
    """测试命令系统"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()

        # 模拟聊天管理器
        with patch('src.day4_cli.chat_manager.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.sessions_dir_path = Path(self.temp_dir)
            mock_get_config.return_value = mock_config

            self.chat_manager = ChatManager()
            self.registry = CommandRegistry()

    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_command_registration(self):
        """测试命令注册"""
        # 检查默认命令是否已注册
        help_command = self.registry.get_command("help")
        self.assertIsNotNone(help_command)
        self.assertEqual(help_command.name, "help")

    def test_is_command(self):
        """测试命令识别"""
        self.assertTrue(self.registry.is_command("/help"))
        self.assertTrue(self.registry.is_command("/new"))
        self.assertFalse(self.registry.is_command("Hello world"))
        self.assertFalse(self.registry.is_command(""))

    def test_help_command(self):
        """测试帮助命令"""
        result = self.registry.execute_command("/help", self.chat_manager)
        self.assertTrue(result.success)

    def test_new_command(self):
        """测试新建会话命令"""
        result = self.registry.execute_command("/new Test Session", self.chat_manager)
        self.assertTrue(result.success)
        self.assertIn("Test Session", result.message)

    def test_list_command(self):
        """测试列会话命令"""
        result = self.registry.execute_command("/list", self.chat_manager)
        self.assertTrue(result.success)

    def test_unknown_command(self):
        """测试未知命令"""
        result = self.registry.execute_command("/unknown", self.chat_manager)
        self.assertFalse(result.success)
        self.assertIn("未知命令", result.message)


class TestCLIInterface(unittest.TestCase):
    """测试 CLI 界面"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()

        # 模拟配置
        with patch('src.day4_cli.cli_interface.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.colored_output = True
            mock_config.show_thinking_process = True
            mock_config.show_tool_calls = True
            mock_get_config.return_value = mock_config

            self.cli = CLIInterface()

    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_display_user_message(self):
        """测试显示用户消息"""
        # 这个测试主要确保方法不会抛出异常
        try:
            self.cli.display_user_message("Hello, world!")
        except Exception as e:
            self.fail(f"display_user_message 抛出异常: {e}")

    def test_display_assistant_message(self):
        """测试显示助手消息"""
        try:
            self.cli.display_assistant_message("Hi there!")
            self.cli.display_assistant_message("Response", {"test": "metadata"})
        except Exception as e:
            self.fail(f"display_assistant_message 抛出异常: {e}")

    def test_display_error(self):
        """测试显示错误"""
        try:
            self.cli.display_error("Test error", "Error details")
        except Exception as e:
            self.fail(f"display_error 抛出异常: {e}")

    def test_display_success(self):
        """测试显示成功消息"""
        try:
            self.cli.display_success("Operation completed")
        except Exception as e:
            self.fail(f"display_success 抛出异常: {e}")


def run_comprehensive_test():
    """运行综合测试"""
    from rich.console import Console

    console = Console()
    console.print("🧪 开始 CLI 应用综合测试", style="bold blue")
    console.print("=" * 60, style="blue")

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    test_classes = [
        TestCLIConfig,
        TestChatMessage,
        TestChatSession,
        TestChatManager,
        TestCommandSystem,
        TestCLIInterface,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出结果摘要
    console.print(f"\n📊 测试结果摘要:")
    console.print(f"总测试数: {result.testsRun}")
    console.print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    console.print(f"失败: {len(result.failures)}")
    console.print(f"错误: {len(result.errors)}")
    console.print(f"跳过: {len(result.skipped)}")

    if result.wasSuccessful():
        console.print("\n✅ 所有测试通过！CLI 应用工作正常。", style="bold green")
        return True
    else:
        console.print("\n❌ 部分测试失败，请检查问题。", style="bold red")

        # 显示失败详情
        if result.failures:
            console.print("\n失败的测试:")
            for test, traceback in result.failures:
                console.print(f"• {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'Unknown error'}")

        if result.errors:
            console.print("\n错误的测试:")
            for test, traceback in result.errors:
                console.print(f"• {test}: {traceback.split('Exception:')[-1].strip() if 'Exception:' in traceback else 'Unknown error'}")

        return False


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)