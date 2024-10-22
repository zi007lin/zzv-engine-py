# zeta-zen-vm/zzv/models/message_types.py

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

class MessageType(Enum):
    SERVER_TIME = "server_time"
    SNAPSHOTS = "snapshots"  
    ALERTS = "alerts"
    CHATS = "chats"
    UNKNOWN = "unknown"

    def to_json(self):
        return self.value

    @classmethod
    def from_json(cls, value: str) -> "MessageType":
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN

class Message:
    def __init__(
        self,
        type: MessageType,
        payload: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        self.type = type
        self.payload = payload
        self.timestamp = timestamp or datetime.now()

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            type=MessageType.from_json(data.get("type", "")),
            payload=data.get("payload", {}),
            timestamp=datetime.fromisoformat(data.get("timestamp")) if data.get("timestamp") else None
        )