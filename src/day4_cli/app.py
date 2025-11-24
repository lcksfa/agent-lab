"""
Personal Assistant CLI Application

Day 4-5: Final personal assistant with CLI interface using ReAct mode.
"""

import os
import sys
from typing import Optional
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from rich.console import Console
import typer

# 导入我们的模块
from src.day4_cli.config import get_config, CLIConfig
from src.day4_cli.chat_manager import ChatManager
from src.day4_cli.commands import CommandRegistry
from src.day4_cli.cli_interface import CLIInterface
from src.day3_core.react_agent import create_react_agent

console = Console()


class AssistantApp:
    """主应用程序类"""

    def __init__(self, config: Optional[CLIConfig] = None):
        self.config = config or get_config()
        self.console = Console()

        # 初始化核心组件
        self.chat_manager = ChatManager()
        self.command_registry = CommandRegistry()
        self.cli_interface = CLIInterface()

        # 创建 ReAct Agent
        self.react_agent = create_react_agent(
            agent_id=self.config.agent_id or "cli_assistant",
            debug_mode=self.config.debug_mode,
            ai_provider=self.config.ai_provider,
            max_steps=self.config.max_steps
        )

        # 设置输入回调
        self.cli_interface.set_input_callback(self._handle_user_message)

        console.print(f"🚀 {self.config.app_name} 已初始化", style="bold green")

    def _handle_user_message(self, user_input: str):
        """处理用户消息的回调函数"""
        try:
            # 显示加载状态
            with self.console.status("🤖 AI 正在思考...", spinner="dots"):
                # 使用 ReAct Agent 处理用户消息
                response = self.react_agent.process_query(user_input)

            # 显示助手回复
            metadata = self._get_response_metadata()
            self.cli_interface.display_assistant_message(response, metadata)

            # 保存助手回复到聊天历史
            self.chat_manager.add_assistant_message(response, metadata)

        except Exception as e:
            self.cli_interface.display_error("处理消息时发生错误", str(e))

            # 保存错误信息到聊天历史
            error_message = f"处理失败: {str(e)}"
            self.chat_manager.add_assistant_message(error_message)

    def _get_response_metadata(self) -> dict:
        """获取响应元数据"""
        try:
            # 从 ReAct Agent 获取状态信息
            agent_state = self.react_agent.get_agent_state()
            execution_summary = self.react_agent.get_execution_summary()

            metadata = {
                "agent_id": agent_state.agent_id,
                "status": agent_state.status.value if hasattr(agent_state.status, 'value') else str(agent_state.status),
                "total_thoughts": len(agent_state.thoughts),
                "total_tool_calls": len(agent_state.tool_calls),
                "execution_time": f"{agent_state.total_execution_time:.2f}s" if agent_state.total_execution_time else "0s"
            }

            # 添加执行摘要信息
            if execution_summary and "react_engine" in execution_summary:
                react_summary = execution_summary["react_engine"]
                metadata.update({
                    "total_steps": react_summary.get("total_steps", 0),
                    "is_complete": react_summary.get("is_complete", False)
                })

            return metadata

        except Exception:
            return {}

    def run_interactive_mode(self):
        """运行交互模式"""
        self.console.print("🎯 启动交互模式", style="bold blue")

        try:
            self.cli_interface.run_interactive_loop()
        except KeyboardInterrupt:
            self.console.print("\n👋 用户中断，正在退出...", style="yellow")
        except Exception as e:
            self.console.print(f"❌ 运行时错误: {e}", style="red")
        finally:
            self._cleanup()

    def run_batch_mode(self, input_file: str, output_file: Optional[str] = None):
        """运行批处理模式"""
        self.console.print("📁 启动批处理模式", style="bold blue")

        try:
            # 读取输入文件
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            if not lines:
                self.console.print("⚠️ 输入文件为空", style="yellow")
                return

            results = []

            # 处理每一行
            for i, line in enumerate(lines, 1):
                self.console.print(f"📝 处理第 {i} 行: {line}")

                try:
                    with self.console.status("🤖 处理中...", spinner="dots"):
                        response = self.react_agent.process_query(line)

                    results.append({
                        "input": line,
                        "output": response,
                        "success": True
                    })

                    self.console.print(f"✅ 完成: {response[:100]}...", style="green")

                except Exception as e:
                    results.append({
                        "input": line,
                        "output": f"错误: {str(e)}",
                        "success": False
                    })
                    self.console.print(f"❌ 失败: {str(e)}", style="red")

            # 保存结果
            if output_file:
                import json
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                self.console.print(f"💾 结果已保存到: {output_file}", style="green")

            # 显示统计
            total = len(results)
            success = sum(1 for r in results if r["success"])
            self.console.print(f"📊 处理完成: {total} 行，成功 {success} 行", style="blue")

        except Exception as e:
            self.console.print(f"❌ 批处理失败: {e}", style="red")

    def _cleanup(self):
        """清理资源"""
        try:
            # 保存配置
            self.config.save_to_file()

            # 保存聊天会话
            if self.chat_manager:
                # 聊天管理器会自动保存
                pass

            self.console.print("🧹 资源清理完成", style="green")

        except Exception as e:
            self.console.print(f"⚠️ 清理资源时出错: {e}", style="yellow")


# 创建 Typer 应用
app = typer.Typer(
    name="ai-assistant",
    help="🤖 基于 ReAct 模式的 AI 助手 CLI 应用",
    no_args_is_help=True
)


@app.command()
def run(
    debug: bool = typer.Option(False, "--debug", "-d", help="启用调试模式"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
    batch_file: Optional[str] = typer.Option(None, "--batch", "-b", help="批处理输入文件"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="批处理输出文件"),
):
    """运行 AI 助手应用"""

    try:
        # 加载配置
        if config_file:
            config = CLIConfig.load_from_file(config_file)
        else:
            config = get_config()

        # 应用命令行参数
        if debug:
            config.debug_mode = True

        # 创建应用实例
        assistant = AssistantApp(config)

        if batch_file:
            # 批处理模式
            assistant.run_batch_mode(batch_file, output_file)
        else:
            # 交互模式
            assistant.run_interactive_mode()

    except Exception as e:
        console.print(f"❌ 启动失败: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def config(
    key: Optional[str] = typer.Argument(None, help="配置项名称"),
    value: Optional[str] = typer.Argument(None, help="配置值"),
    show_all: bool = typer.Option(False, "--all", "-a", help="显示所有配置"),
):
    """配置管理"""

    try:
        cfg = get_config()

        if show_all:
            cfg.display()
            return

        if not key:
            # 显示常用配置
            console.print("📋 常用配置项:", style="bold blue")
            console.print(f"  debug_mode: {cfg.debug_mode}")
            console.print(f"  max_steps: {cfg.max_steps}")
            console.print(f"  show_thinking_process: {cfg.show_thinking_process}")
            console.print(f"  show_tool_calls: {cfg.show_tool_calls}")
            return

        if value is None:
            # 显示特定配置
            if hasattr(cfg, key):
                console.print(f"{key}: {getattr(cfg, key)}")
            else:
                console.print(f"❌ 未知配置项: {key}", style="red")
                raise typer.Exit(1)
        else:
            # 设置配置
            if hasattr(cfg, key):
                # 类型转换
                current_value = getattr(cfg, key)
                if isinstance(current_value, bool):
                    if value.lower() in ('true', '1', 'yes', 'on'):
                        value = True
                    elif value.lower() in ('false', '0', 'no', 'off'):
                        value = False
                    else:
                        console.print("❌ 布尔值必须是 true/false, yes/no, on/off, 1/0", style="red")
                        raise typer.Exit(1)
                elif isinstance(current_value, int):
                    try:
                        value = int(value)
                    except ValueError:
                        console.print("❌ 整数值格式错误", style="red")
                        raise typer.Exit(1)
                elif isinstance(current_value, float):
                    try:
                        value = float(value)
                    except ValueError:
                        console.print("❌ 数值格式错误", style="red")
                        raise typer.Exit(1)

                setattr(cfg, key, value)
                cfg.save_to_file()
                console.print(f"✅ 配置已更新: {key} = {value}", style="green")
            else:
                console.print(f"❌ 未知配置项: {key}", style="red")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"❌ 配置操作失败: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def version():
    """显示版本信息"""
    config = get_config()
    console.print(f"🤖 {config.app_name} v{config.version}", style="bold blue")


@app.command()
def demo():
    """运行演示模式"""
    console.print("🎬 演示模式", style="bold blue")
    console.print("=" * 50, style="blue")

    try:
        # 创建临时应用实例
        app = AssistantApp()

        # 演示对话
        demo_queries = [
            "你好，请介绍一下自己",
            "计算 123 * 456 等于多少？",
            "查询北京今天的天气",
            "现在几点了？"
        ]

        for i, query in enumerate(demo_queries, 1):
            console.print(f"\n📝 演示查询 {i}: {query}", style="bold yellow")
            console.print("-" * 40, style="yellow")

            # 显示用户消息
            app.cli_interface.display_user_message(query)

            # 处理查询
            with console.status("🤖 AI 正在思考...", spinner="dots"):
                response = app.react_agent.process_query(query)

            # 显示助手回复
            app.cli_interface.display_assistant_message(response)

            if i < len(demo_queries):
                console.print("\n按 Enter 继续...")
                input()

        console.print("\n🎉 演示完成！", style="bold green")

    except Exception as e:
        console.print(f"❌ 演示失败: {e}", style="red")


def main():
    """主入口函数"""
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        console.print("⚠️ 警告: 未设置 OPENAI_API_KEY 环境变量", style="yellow")
        console.print("请设置您的 OpenAI API Key:", style="yellow")
        console.print("export OPENAI_API_KEY=your_key_here", style="cyan")
        console.print()

    # 运行 Typer 应用
    app()


if __name__ == "__main__":
    main()