from app.adapters.teams_webhook_sender import TeamsWebhookSender
from app.domain.message import BridgeMessage
from app.repositories.message_repository import MessageRepository


class MessageRouter:
    def __init__(
        self,
        teams_sender: TeamsWebhookSender,
        message_repository: MessageRepository,
    ):
        self.teams_sender = teams_sender
        self.message_repository = message_repository

    async def route_from_whatsapp_to_teams(self, message: BridgeMessage) -> int:
        message_id = self.message_repository.create_received_message(message)

        try:
            await self.teams_sender.send_message(message)
        except Exception as exc:
            self.message_repository.update_status(
                message_id=message_id,
                status="ERROR",
                error_message=str(exc),
            )
            raise

        self.message_repository.update_status(
            message_id=message_id,
            status="SENT_TO_TEAMS",
        )

        return message_id