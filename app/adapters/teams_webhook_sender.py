import httpx

from app.config import settings
from app.domain.message import BridgeMessage


class TeamsWebhookSender:
    def __init__(self, default_webhook_url: str | None = None):
        self.default_webhook_url = default_webhook_url or settings.teams_webhook_url

    async def send_message(
        self,
        message: BridgeMessage,
        webhook_url: str | None = None,
    ) -> None:
        target_webhook_url = webhook_url or self.default_webhook_url

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
            response = await client.post(target_webhook_url, json=card_payload)
            response.raise_for_status()