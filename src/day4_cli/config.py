"""
CLI 应用配置管理

提供应用程序的配置管理功能，包括默认配置、环境变量处理、配置文件管理等。
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from rich.console import Console

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

console = Console()


class CLIConfig(BaseModel):
    """CLI 应用配置"""

    # 基础配置
    app_name: str = "AI Assistant CLI"
    version: str = "1.0.0"
    debug_mode: bool = False

    # ReAct Agent 配置
    agent_id: Optional[str] = None
    max_steps: int = 10
    ai_provider: str = "deepseek"

    # 聊天配置
    max_history_length: int = 100
    auto_save_history: bool = True
    history_file: str = "chat_history.json"

    # 界面配置
    show_thinking_process: bool = True
    show_tool_calls: bool = True
    show_execution_trace: bool = False
    colored_output: bool = True

    # 文件路径配置
    config_dir: str = "~/.ai_assistant"
    sessions_dir: str = "sessions"
    logs_dir: str = "logs"

    # 性能配置
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

    def __init__(self, **data):
        super().__init__(**data)
        # 确保目录存在
        self._ensure_directories()

    def _ensure_directories(self):
        """确保配置目录存在"""
        # 展开用户目录
        config_dir = Path(self.config_dir).expanduser()

        # 创建必要的目录
        directories = [
            config_dir,
            config_dir / self.sessions_dir,
            config_dir / self.logs_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def config_dir_path(self) -> Path:
        """配置目录路径"""
        return Path(self.config_dir).expanduser()

    @property
    def sessions_dir_path(self) -> Path:
        """会话目录路径"""
        return self.config_dir_path / self.sessions_dir

    @property
    def logs_dir_path(self) -> Path:
        """日志目录路径"""
        return self.config_dir_path / self.logs_dir

    @property
    def history_file_path(self) -> Path:
        """历史文件路径"""
        return self.config_dir_path / self.history_file

    @property
    def config_file_path(self) -> Path:
        """配置文件路径"""
        return self.config_dir_path / "config.yaml"

    def save_to_file(self, file_path: Optional[str] = None):
        """保存配置到文件"""
        if file_path is None:
            file_path = self.config_file_path

        config_data = self.model_dump(exclude_none=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)

            console.print(f"✅ 配置已保存到: {file_path}", style="green")

        except Exception as e:
            console.print(f"❌ 保存配置失败: {e}", style="red")
            raise

    @classmethod
    def load_from_file(cls, file_path: Optional[str] = None) -> "CLIConfig":
        """从文件加载配置"""
        if file_path is None:
            config = cls()
            file_path = config.config_file_path

        if not Path(file_path).exists():
            console.print(f"📝 配置文件不存在，使用默认配置: {file_path}", style="yellow")
            return cls()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            if config_data:
                config = cls(**config_data)
                console.print(f"✅ 配置已加载: {file_path}", style="green")
                return config
            else:
                return cls()

        except Exception as e:
            console.print(f"❌ 加载配置失败: {e}，使用默认配置", style="red")
            return cls()

    @classmethod
    def load_from_env(cls) -> "CLIConfig":
        """从环境变量加载配置"""
        env_config = {}

        # 环境变量映射
        env_mapping = {
            'AI_ASSISTANT_DEBUG': 'debug_mode',
            'AI_ASSISTANT_AGENT_ID': 'agent_id',
            'AI_ASSISTANT_MAX_STEPS': 'max_steps',
            'AI_ASSISTANT_AI_PROVIDER': 'ai_provider',
            'AI_ASSISTANT_MAX_HISTORY': 'max_history_length',
            'AI_ASSISTANT_AUTO_SAVE': 'auto_save_history',
            'AI_ASSISTANT_SHOW_THINKING': 'show_thinking_process',
            'AI_ASSISTANT_SHOW_TOOLS': 'show_tool_calls',
            'AI_ASSISTANT_SHOW_TRACE': 'show_execution_trace',
            'AI_ASSISTANT_CONFIG_DIR': 'config_dir',
        }

        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # 类型转换
                if config_key in ['debug_mode', 'auto_save_history', 'show_thinking_process',
                                'show_tool_calls', 'show_execution_trace']:
                    env_config[config_key] = value.lower() in ('true', '1', 'yes', 'on')
                elif config_key in ['max_steps', 'max_history_length', 'request_timeout',
                                 'max_retries']:
                    env_config[config_key] = int(value)
                elif config_key == 'retry_delay':
                    env_config[config_key] = float(value)
                else:
                    env_config[config_key] = value

        if env_config:
            console.print("✅ 从环境变量加载配置", style="green")

        return cls(**env_config)

    def update(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                console.print(f"⚠️ 未知配置项: {key}", style="yellow")

    def get_dict(self) -> Dict[str, Any]:
        """获取配置字典"""
        return self.model_dump(exclude_none=True)

    def display(self):
        """显示当前配置"""
        console.print("📋 当前配置:", style="bold blue")
        console.print("=" * 50, style="blue")

        config_dict = self.get_dict()

        for key, value in config_dict.items():
            if isinstance(value, bool):
                status = "✅" if value else "❌"
                console.print(f"  {key}: {status}")
            else:
                console.print(f"  {key}: {value}")


# 全局配置实例
_config: Optional[CLIConfig] = None


def get_config() -> CLIConfig:
    """获取全局配置实例"""
    global _config
    if _config is None:
        # 加载顺序：环境变量 -> 配置文件 -> 默认配置
        _config = CLIConfig.load_from_env()
        if not any(os.getenv(key) for key in ['AI_ASSISTANT_DEBUG', 'AI_ASSISTANT_AGENT_ID']):
            # 如果没有环境变量，尝试加载配置文件
            file_config = CLIConfig.load_from_file()
            if file_config.get_dict():
                _config = file_config
    return _config


def set_config(config: CLIConfig):
    """设置全局配置实例"""
    global _config
    _config = config


if __name__ == "__main__":
    # 测试配置管理
    console.print("🧪 测试配置管理", style="bold blue")

    # 创建配置
    config = CLIConfig(debug_mode=True, max_steps=5)
    config.display()

    # 保存配置
    config.save_to_file()

    # 加载配置
    loaded_config = CLIConfig.load_from_file()
    console.print("\n📖 加载的配置:")
    loaded_config.display()

    # 从环境变量加载
    os.environ['AI_ASSISTANT_DEBUG'] = 'true'
    os.environ['AI_ASSISTANT_MAX_STEPS'] = '8'
    env_config = CLIConfig.load_from_env()
    console.print("\n🌍 环境变量配置:")
    env_config.display()