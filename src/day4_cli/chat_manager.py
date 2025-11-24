"""
聊天会话管理器

管理聊天会话、历史记录和消息存储。
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from pydantic import BaseModel, Field
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .config import get_config


class ChatMessage(BaseModel):
    """聊天消息"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    role: str  # "user" or "assistant"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """从字典创建消息"""
        # 解析时间戳
        if isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class ChatSession(BaseModel):
    """聊天会话"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: List[ChatMessage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """添加消息"""
        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message

    def get_last_messages(self, count: int = 10) -> List[ChatMessage]:
        """获取最后几条消息"""
        return self.messages[-count:] if self.messages else []

    def clear_messages(self):
        """清空消息"""
        self.messages = []
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [msg.to_dict() for msg in self.messages],
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSession":
        """从字典创建会话"""
        # 解析时间戳
        if isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        # 解析消息
        messages = [ChatMessage.from_dict(msg) for msg in data.get("messages", [])]
        data["messages"] = messages

        return cls(**data)


class ChatManager:
    """聊天管理器"""

    def __init__(self):
        self.config = get_config()
        self.console = Console()
        self.sessions: Dict[str, ChatSession] = {}
        self.current_session_id: Optional[str] = None

        # 确保会话目录存在
        self.sessions_dir = self.config.sessions_dir_path
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # 加载现有会话
        self._load_sessions()

    def _load_sessions(self):
        """加载现有会话"""
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                session = ChatSession.from_dict(session_data)
                self.sessions[session.id] = session
            except Exception as e:
                self.console.print(f"⚠️ 加载会话失败 {session_file}: {e}", style="yellow")

        if self.sessions:
            self.console.print(f"📚 已加载 {len(self.sessions)} 个历史会话", style="green")

    def create_session(self, name: Optional[str] = None) -> ChatSession:
        """创建新会话"""
        if name is None:
            # 生成默认名称
            session_count = len(self.sessions) + 1
            name = f"会话 {session_count}"

        session = ChatSession(name=name)
        self.sessions[session.id] = session
        self.current_session_id = session.id

        # 保存会话
        self._save_session(session)

        self.console.print(f"✅ 创建新会话: {name}", style="green")
        return session

    def get_current_session(self) -> Optional[ChatSession]:
        """获取当前会话"""
        if self.current_session_id is None:
            # 如果没有当前会话，创建一个
            self.create_session()
        return self.sessions.get(self.current_session_id)

    def switch_session(self, session_id: str) -> bool:
        """切换会话"""
        if session_id in self.sessions:
            self.current_session_id = session_id
            session = self.sessions[session_id]
            self.console.print(f"🔄 切换到会话: {session.name}", style="blue")
            return True
        else:
            self.console.print(f"❌ 会话不存在: {session_id}", style="red")
            return False

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id not in self.sessions:
            self.console.print(f"❌ 会话不存在: {session_id}", style="red")
            return False

        session = self.sessions[session_id]

        # 删除文件
        session_file = self.sessions_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()

        # 从内存中删除
        del self.sessions[session_id]

        # 如果删除的是当前会话，切换到其他会话
        if self.current_session_id == session_id:
            self.current_session_id = None
            if self.sessions:
                # 切换到第一个会话
                first_session_id = next(iter(self.sessions))
                self.current_session_id = first_session_id

        self.console.print(f"🗑️ 删除会话: {session.name}", style="yellow")
        return True

    def add_user_message(self, content: str) -> Optional[ChatMessage]:
        """添加用户消息"""
        session = self.get_current_session()
        if session:
            message = session.add_message("user", content)
            self._save_session(session)
            return message
        return None

    def add_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[ChatMessage]:
        """添加助手消息"""
        session = self.get_current_session()
        if session:
            message = session.add_message("assistant", content, metadata)
            self._save_session(session)
            return message
        return None

    def get_session_history(self, session_id: Optional[str] = None, count: int = 10) -> List[ChatMessage]:
        """获取会话历史"""
        if session_id is None:
            session = self.get_current_session()
        else:
            session = self.sessions.get(session_id)

        if session:
            return session.get_last_messages(count)
        return []

    def list_sessions(self) -> List[ChatSession]:
        """列出所有会话"""
        return sorted(self.sessions.values(), key=lambda s: s.updated_at, reverse=True)

    def display_sessions(self):
        """显示所有会话"""
        sessions = self.list_sessions()

        if not sessions:
            self.console.print("📝 暂无会话", style="yellow")
            return

        table = Table(title="聊天会话列表")
        table.add_column("ID", style="cyan", width=8)
        table.add_column("名称", style="white")
        table.add_column("消息数", style="green", justify="right")
        table.add_column("创建时间", style="blue")
        table.add_column("当前", style="yellow", justify="center")

        for session in sessions:
            is_current = "✅" if session.id == self.current_session_id else "❌"
            table.add_row(
                session.id[:8],
                session.name,
                str(len(session.messages)),
                session.created_at.strftime("%Y-%m-%d %H:%M"),
                is_current
            )

        self.console.print(table)

    def display_session_history(self, session_id: Optional[str] = None, count: int = 20):
        """显示会话历史"""
        messages = self.get_session_history(session_id, count)

        if not messages:
            self.console.print("📝 暂无消息历史", style="yellow")
            return

        session = self.get_current_session()
        if session:
            self.console.print(f"💬 会话: {session.name}", style="bold blue")
            self.console.print("=" * 60, style="blue")

        for message in messages:
            timestamp = message.timestamp.strftime("%H:%M:%S")
            if message.role == "user":
                self.console.print(f"[{timestamp}] 👤 用户: {message.content}", style="green")
            else:
                self.console.print(f"[{timestamp}] 🤖 助手: {message.content}", style="cyan")

    def export_session(self, session_id: Optional[str] = None, file_path: Optional[str] = None) -> str:
        """导出会话"""
        if session_id is None:
            session = self.get_current_session()
        else:
            session = self.sessions.get(session_id)

        if not session:
            raise ValueError("会话不存在")

        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"chat_export_{timestamp}.json"

        export_data = {
            "session": session.to_dict(),
            "exported_at": datetime.now().isoformat(),
            "app_version": "1.0.0"
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        self.console.print(f"📤 会话已导出到: {file_path}", style="green")
        return file_path

    def _save_session(self, session: ChatSession):
        """保存会话到文件"""
        session_file = self.sessions_dir / f"{session.id}.json"

        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)

    def clear_current_session(self):
        """清空当前会话"""
        session = self.get_current_session()
        if session:
            session.clear_messages()
            self._save_session(session)
            self.console.print(f"🗑️ 已清空会话: {session.name}", style="yellow")

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_sessions = len(self.sessions)
        total_messages = sum(len(session.messages) for session in self.sessions.values())

        current_session = self.get_current_session()
        current_messages = len(current_session.messages) if current_session else 0

        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "current_session_messages": current_messages,
            "current_session_name": current_session.name if current_session else None
        }


if __name__ == "__main__":
    # 测试聊天管理器
    console = Console()
    console.print("🧪 测试聊天管理器", style="bold blue")

    # 创建聊天管理器
    chat_manager = ChatManager()

    # 创建测试会话
    session1 = chat_manager.create_session("测试会话1")
    chat_manager.add_user_message("你好，我想了解 ReAct Agent")
    chat_manager.add_assistant_message("ReAct Agent 是一个结合推理和行动的智能代理系统...")

    session2 = chat_manager.create_session("测试会话2")
    chat_manager.add_user_message("今天的天气怎么样？")
    chat_manager.add_assistant_message("我需要查询天气信息来回答您的问题...")

    # 显示会话列表
    chat_manager.display_sessions()

    # 显示统计信息
    stats = chat_manager.get_statistics()
    console.print(f"\n📊 统计信息: {stats}", style="blue")

    # 导出会话
    try:
        export_path = chat_manager.export_session()
        console.print(f"✅ 导出成功: {export_path}", style="green")
    except Exception as e:
        console.print(f"❌ 导出失败: {e}", style="red")