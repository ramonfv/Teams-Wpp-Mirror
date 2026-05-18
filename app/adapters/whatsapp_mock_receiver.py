from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MockWhatsAppPayload(BaseModel):
    group_id: str
    group_name: str
    author_name: str
    body: str
    timestamp: Optional[datetime] = None