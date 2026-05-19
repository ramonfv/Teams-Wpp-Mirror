from app.adapters.whatsapp_mock_sender import WhatsAppMockSender
from app.repositories.message_repository import MessageRepository


class WhatsAppOutboxService:
    def __init__(
        self,
        message_repository: MessageRepository,
        whatsapp_sender: WhatsAppMockSender,
    ):
        self.message_repository = message_repository
        self.whatsapp_sender = whatsapp_sender

    async def process_pending_messages(self, limit: int = 10) -> dict:
        pending_messages = self.message_repository.list_ready_to_send_to_whatsapp(
            limit=limit,
        )

        processed = []
        failed = []

        for message in pending_messages:
            result = await self._process_single_message(message)

            if result["status"] == "SENT_TO_WHATSAPP_MOCK":
                processed.append(result)
            else:
                failed.append(result)

        return {
            "total_pending": len(pending_messages),
            "processed": processed,
            "failed": failed,
        }

    async def process_message_by_id(self, message_id: int) -> dict:
        message = self.message_repository.get_message_by_id(message_id)

        if message is None:
            raise ValueError(f"Mensagem '{message_id}' não encontrada.")

        if message["direction"] != "TEAMS_TO_WHATSAPP":
            return {
                "message_id": message_id,
                "status": "SKIPPED",
                "reason": "Mensagem não pertence ao fluxo TEAMS_TO_WHATSAPP.",
            }

        if message["status"] != "READY_TO_SEND_TO_WHATSAPP":
            return {
                "message_id": message_id,
                "status": "SKIPPED",
                "reason": (
                    "Mensagem não está com status READY_TO_SEND_TO_WHATSAPP. "
                    f"Status atual: {message['status']}."
                ),
            }

        return await self._process_single_message(message)

    async def _process_single_message(self, message: dict) -> dict:
        message_id = int(message["id"])

        self.message_repository.register_delivery_attempt(
            message_id=message_id,
        )

        try:
            external_message_id = await self.whatsapp_sender.send_text_message(
                whatsapp_group_id=message["source_group_id"],
                author_name=message["author_name"],
                body=message["body"],
            )

            self.message_repository.update_status(
                message_id=message_id,
                status="SENT_TO_WHATSAPP_MOCK",
                error_message=None,
                external_message_id=external_message_id,
            )

            return {
                "message_id": message_id,
                "external_message_id": external_message_id,
                "status": "SENT_TO_WHATSAPP_MOCK",
            }

        except Exception as exc:
            self.message_repository.update_status(
                message_id=message_id,
                status="ERROR",
                error_message=str(exc),
            )

            return {
                "message_id": message_id,
                "status": "ERROR",
                "error": str(exc),
            }