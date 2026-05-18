from pydantic import BaseModel


class AuthorizedUserCreate(BaseModel):
    teams_user_email: str
    display_name: str
    can_send_to_whatsapp: bool = True


class AuthorizedUserResponse(BaseModel):
    id: int
    teams_user_email: str
    display_name: str
    can_send_to_whatsapp: bool
    active: bool