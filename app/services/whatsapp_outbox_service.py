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

                processed.append(
                    {
                        "message_id": message_id,
                        "external_message_id": external_message_id,
                        "status": "SENT_TO_WHATSAPP_MOCK",
                    }
                )

            except Exception as exc:
                self.message_repository.update_status(
                    message_id=message_id,
                    status="ERROR",
                    error_message=str(exc),
                )

                failed.append(
                    {
                        "message_id": message_id,
                        "status": "ERROR",
                        "error": str(exc),
                    }
                )

        return {
            "total_pending": len(pending_messages),
            "processed": processed,
            "failed": failed,
        }