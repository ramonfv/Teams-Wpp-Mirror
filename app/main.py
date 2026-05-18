from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException

from app.adapters.teams_webhook_sender import TeamsWebhookSender
from app.adapters.whatsapp_mock_receiver import MockWhatsAppPayload
from app.database import initialize_database
from app.domain.mapping import ChannelMappingCreate
from app.domain.message import BridgeMessage, MessageSource, MessageType
from app.repositories.mapping_repository import MappingRepository
from app.repositories.message_repository import MessageRepository
from app.services.message_router import MessageRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Teams WhatsApp Mirror",
    lifespan=lifespan,
)

message_repository = MessageRepository()
mapping_repository = MappingRepository()
teams_sender = TeamsWebhookSender()

router = MessageRouter(
    teams_sender=teams_sender,
    message_repository=message_repository,
    mapping_repository=mapping_repository,
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/messages/recent")
async def list_recent_messages(limit: int = 20):
    return {
        "messages": message_repository.list_recent_messages(limit=limit)
    }


@app.post("/mappings/whatsapp-to-teams")
async def create_or_update_mapping(mapping: ChannelMappingCreate):
    mapping_id = mapping_repository.upsert_mapping(mapping)

    return {
        "status": "mapping_saved",
        "mapping_id": mapping_id,
        "whatsapp_group_id": mapping.whatsapp_group_id,
        "whatsapp_group_name": mapping.whatsapp_group_name,
        "teams_team_name": mapping.teams_team_name,
        "teams_channel_name": mapping.teams_channel_name,
    }


@app.get("/mappings/whatsapp-to-teams")
async def list_mappings():
    return {
        "mappings": mapping_repository.list_mappings()
    }


@app.delete("/mappings/whatsapp-to-teams/{whatsapp_group_id}")
async def deactivate_mapping(whatsapp_group_id: str):
    deactivated = mapping_repository.deactivate_mapping(
        whatsapp_group_id=whatsapp_group_id,
    )

    if not deactivated:
        raise HTTPException(
            status_code=404,
            detail="Mapeamento não encontrado.",
        )

    return {
        "status": "mapping_deactivated",
        "whatsapp_group_id": whatsapp_group_id,
    }


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
        message_id = await router.route_from_whatsapp_to_teams(message)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao rotear mensagem para o Teams: {exc}",
        ) from exc

    return {
        "status": "sent_to_teams",
        "message_id": message_id,
        "message": message,
    }