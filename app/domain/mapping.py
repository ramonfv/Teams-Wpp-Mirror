from pydantic import BaseModel, HttpUrl


class ChannelMappingCreate(BaseModel):
    whatsapp_group_id: str
    whatsapp_group_name: str
    teams_team_name: str
    teams_channel_name: str
    teams_webhook_url: HttpUrl


class ChannelMappingResponse(BaseModel):
    id: int
    whatsapp_group_id: str
    whatsapp_group_name: str
    teams_team_name: str
    teams_channel_name: str
    active: bool