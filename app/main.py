from datetime import datetime

from fastapi import FastAPI, HTTPException

from app.adapters.teams_webhook_sender import TeamsWebhookSender
from app.adapters.whatsapp_mock_receiver import MockWhatsAppPayload
from app.domain.message import BridgeMessage, MessageSource, MessageType
from app.services.message_router import MessageRouter

app = FastAPI(title="Teams WhatsApp Mirror")

teams_sender = TeamsWebhookSender()
router = MessageRouter(teams_sender=teams_sender)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/mock/whatsapp/message")
async def receive_mock_whatsapp_message(payload: MockWhatsAppPayload):
    message = BridgeMessage(
        source=MessageSource.WHATSAPP,
        source_group_id=payload.group_id,
        source_group_name=payload.group_name,
        author_name=payload.author_name,
        body=payload.body,
        message_type=MessageType.TEXT,
        timestamp=payload.timestamp or datetime.now(),
    )

    try:
        await router.route_from_whatsapp_to_teams(message)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao enviar mensagem para o Teams: {exc}",
        ) from exc

    return {
        "status": "sent_to_teams",
        "message": message,
    }