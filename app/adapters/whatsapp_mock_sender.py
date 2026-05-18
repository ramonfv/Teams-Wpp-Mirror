from uuid import uuid4


class WhatsAppMockSender:
    async def send_text_message(
        self,
        whatsapp_group_id: str,
        author_name: str,
        body: str,
    ) -> str:
        if "__fail__" in body.lower():
            raise RuntimeError("Falha simulada no envio mock para WhatsApp.")

        mock_message_id = f"mock-wpp-{uuid4()}"

        print(
            "[WHATSAPP MOCK SEND]",
            {
                "mock_message_id": mock_message_id,
                "whatsapp_group_id": whatsapp_group_id,
                "author_name": author_name,
                "body": body,
            },
        )

        return mock_message_id