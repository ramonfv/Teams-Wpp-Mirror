from app.adapters.teams_webhook_sender import TeamsWebhookSender
from app.domain.message import BridgeMessage


class MessageRouter:
    def __init__(self, teams_sender: TeamsWebhookSender):
        self.teams_sender = teams_sender

    async def route_from_whatsapp_to_teams(self, message: BridgeMessage) -> None:
        await self.teams_sender.send_message(message)