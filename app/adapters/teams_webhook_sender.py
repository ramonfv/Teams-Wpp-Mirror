import httpx

from app.config import settings
from app.domain.message import BridgeMessage


class TeamsWebhookSender:
    def __init__(self, webhook_url: str | None = None):
        self.webhook_url = webhook_url or settings.teams_webhook_url

    async def send_message(self, message: BridgeMessage) -> None:
        card_payload = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "Mensagem recebida do WhatsApp Bridge",
                    "weight": "Bolder",
                    "size": "Medium",
                    "wrap": True,
                },
                {
                    "type": "TextBlock",
                    "text": message.source_group_name,
                    "weight": "Bolder",
                    "wrap": True,
                },
                {
                    "type": "TextBlock",
                    "text": f"{message.author_name}: {message.body}",
                    "wrap": True,
                },
            ],
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(self.webhook_url, json=card_payload)
            response.raise_for_status()