from app.adapters.teams_webhook_sender import TeamsWebhookSender
from app.domain.message import BridgeMessage
from app.repositories.mapping_repository import MappingRepository
from app.repositories.message_repository import MessageRepository
from app.services.authorization_service import AuthorizationService


class MessageRouter:
    def __init__(
        self,
        teams_sender: TeamsWebhookSender,
        message_repository: MessageRepository,
        mapping_repository: MappingRepository,
        authorization_service: AuthorizationService,
    ):
        self.teams_sender = teams_sender
        self.message_repository = message_repository
        self.mapping_repository = mapping_repository
        self.authorization_service = authorization_service

    async def route_from_whatsapp_to_teams(self, message: BridgeMessage) -> int:
        message_id = self.message_repository.create_received_message(
            message=message,
            direction="WHATSAPP_TO_TEAMS",
        )

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

    async def route_from_teams_to_whatsapp_mock(
        self,
        message: BridgeMessage,
        teams_user_email: str,
    ) -> int:
        message_id = self.message_repository.create_received_message(
            message=message,
            direction="TEAMS_TO_WHATSAPP",
        )

        try:
            self.authorization_service.assert_can_send_to_whatsapp(
                teams_user_email=teams_user_email,
            )

            mapping = self.mapping_repository.get_active_mapping_by_whatsapp_group_id(
                whatsapp_group_id=message.source_group_id,
            )

            if mapping is None:
                raise ValueError(
                    "Nenhum mapeamento ativo encontrado para o grupo "
                    f"'{message.source_group_id}'."
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
            status="READY_TO_SEND_TO_WHATSAPP",
        )

        return message_id