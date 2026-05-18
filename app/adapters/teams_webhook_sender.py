import httpx

from app.config import settings
from app.domain.message import BridgeMessage


class TeamsWebhookSender:
    def __init__(self, webhook_url: str | None = None):
        self.webhook_url = webhook_url or settings.teams_webhook_url

    async def send_message(self, message: BridgeMessage) -> None:
        text = (
            f"**{message.source_group_name}**\n\n"
            f"**{message.author_name}:** {message.body}"
        )

        payload = {
            "text": text,
            "group_name": message.source_group_name,
            "author_name": message.author_name,
            "body": message.body,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(self.webhook_url, json=payload)
            response.raise_for_status()