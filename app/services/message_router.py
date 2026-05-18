from app.adapters.teams_webhook_sender import TeamsWebhookSender
from app.domain.message import BridgeMessage
from app.repositories.mapping_repository import MappingRepository
from app.repositories.message_repository import MessageRepository


class MessageRouter:
    def __init__(
        self,
        teams_sender: TeamsWebhookSender,
        message_repository: MessageRepository,
        mapping_repository: MappingRepository,
    ):
        self.teams_sender = teams_sender
        self.message_repository = message_repository
        self.mapping_repository = mapping_repository

    async def route_from_whatsapp_to_teams(self, message: BridgeMessage) -> int:
        message_id = self.message_repository.create_received_message(message)

        mapping = self.mapping_repository.get_active_mapping_by_whatsapp_group_id(
            whatsapp_group_id=message.source_group_id,
        )

        if mapping is None:
            error_message = (
                "Nenhum mapeamento ativo encontrado para o grupo "
                f"'{message.source_group_id}'."
            )

            self.message_repository.update_status(
                message_id=message_id,
                status="ERROR",
                error_message=error_message,
            )

            raise ValueError(error_message)

        try:
            await self.teams_sender.send_message(
                message=message,
                webhook_url=mapping["teams_webhook_url"],
            )
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