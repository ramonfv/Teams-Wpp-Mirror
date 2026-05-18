from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class MessageSource(str, Enum):
    WHATSAPP = "whatsapp"
    TEAMS = "teams"


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    FILE = "file"


class BridgeMessage(BaseModel):
    source: MessageSource
    source_group_id: str
    source_group_name: str
    author_name: str
    body: str
    timestamp: datetime
    message_type: MessageType = MessageType.TEXT
    author_id: Optional[str] = None
    external_message_id: Optional[str] = None