from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MockTeamsPayload(BaseModel):
    target_whatsapp_group_id: str
    target_whatsapp_group_name: str
    teams_user_email: str
    teams_user_name: str
    body: str
    timestamp: Optional[datetime] = None