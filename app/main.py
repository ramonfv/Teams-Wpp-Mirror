from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI, HTTPException

from app.adapters.teams_webhook_sender import TeamsWebhookSender
from app.adapters.whatsapp_mock_receiver import MockWhatsAppPayload
from app.database import initialize_database
from app.domain.mapping import ChannelMappingCreate
from app.domain.message import BridgeMessage, MessageSource, MessageType
from app.repositories.mapping_repository import MappingRepository
from app.repositories.message_repository import MessageRepository
from app.services.message_router import MessageRouter
from app.adapters.whatsapp_mock_sender import WhatsAppMockSender
from app.services.whatsapp_outbox_service import WhatsAppOutboxService
from app.adapters.teams_mock_receiver import MockTeamsPayload
from app.domain.user import AuthorizedUserCreate
from app.repositories.user_repository import UserRepository
from app.services.authorization_service import AuthorizationService


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

whatsapp_mock_sender = WhatsAppMockSender()

whatsapp_outbox_service = WhatsAppOutboxService(
    message_repository=message_repository,
    whatsapp_sender=whatsapp_mock_sender,
)

async def process_outbox_message_background(message_id: int) -> None:
    await whatsapp_outbox_service.process_message_by_id(message_id)

message_repository = MessageRepository()
mapping_repository = MappingRepository()
user_repository = UserRepository()

authorization_service = AuthorizationService(
    user_repository=user_repository,
)

teams_sender = TeamsWebhookSender()

router = MessageRouter(
    teams_sender=teams_sender,
    message_repository=message_repository,
    mapping_repository=mapping_repository,
    authorization_service=authorization_service,
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


@app.get("/mock/whatsapp/outbox")
async def list_whatsapp_outbox(limit: int = 10):
    return {
        "messages": message_repository.list_ready_to_send_to_whatsapp(
            limit=limit,
        )
    }


@app.post("/mock/whatsapp/outbox/process")
async def process_whatsapp_outbox(limit: int = 10):
    result = await whatsapp_outbox_service.process_pending_messages(
        limit=limit,
    )

    return {
        "status": "outbox_processed",
        **result,
    }

@app.post("/mock/teams/message")
async def receive_mock_teams_message(
    payload: MockTeamsPayload,
    background_tasks: BackgroundTasks,
    auto_process_outbox: bool = False,
):
    message = BridgeMessage(
        source=MessageSource.TEAMS,
        source_group_id=payload.target_whatsapp_group_id,
        source_group_name=payload.target_whatsapp_group_name,
        author_name=payload.teams_user_name,
        author_id=payload.teams_user_email.lower(),
        body=payload.body,
        message_type=MessageType.TEXT,
        timestamp=payload.timestamp or datetime.now(),
    )

    try:
        message_id = await router.route_from_teams_to_whatsapp_mock(
            message=message,
            teams_user_email=payload.teams_user_email,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao preparar mensagem para WhatsApp: {exc}",
        ) from exc

    return {
        "status": "ready_to_send_to_whatsapp",
        "message_id": message_id,
        "message": message,
    }


@app.post("/users/authorized")
async def create_or_update_authorized_user(user: AuthorizedUserCreate):
    user_id = user_repository.upsert_user(user)

    return {
        "status": "authorized_user_saved",
        "user_id": user_id,
        "teams_user_email": user.teams_user_email.lower(),
        "display_name": user.display_name,
        "can_send_to_whatsapp": user.can_send_to_whatsapp,
    }


@app.get("/users/authorized")
async def list_authorized_users():
    return {
        "users": user_repository.list_users()
    }


@app.delete("/users/authorized")
async def deactivate_authorized_user(teams_user_email: str):
    deactivated = user_repository.deactivate_user(
        teams_user_email=teams_user_email,
    )

    if not deactivated:
        raise HTTPException(
            status_code=404,
            detail="Usuário autorizado não encontrado.",
        )

    return {
        "status": "authorized_user_deactivated",
        "teams_user_email": teams_user_email.lower(),
    }


@app.post("/mock/teams/message")
async def receive_mock_teams_message(payload: MockTeamsPayload):
    message = BridgeMessage(
        source=MessageSource.TEAMS,
        source_group_id=payload.target_whatsapp_group_id,
        source_group_name=payload.target_whatsapp_group_name,
        author_name=payload.teams_user_name,
        author_id=payload.teams_user_email.lower(),
        body=payload.body,
        message_type=MessageType.TEXT,
        timestamp=payload.timestamp or datetime.now(),
    )

    try:
        message_id = await router.route_from_teams_to_whatsapp_mock(
            message=message,
            teams_user_email=payload.teams_user_email,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao preparar mensagem para WhatsApp: {exc}",
        ) from exc

    return {
        "status": "ready_to_send_to_whatsapp",
        "message_id": message_id,
        "message": message,
    }   


@app.post("/mock/whatsapp/outbox/process/{message_id}")
async def process_whatsapp_outbox_message(message_id: int):
    try:
        result = await whatsapp_outbox_service.process_message_by_id(
            message_id=message_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "status": "outbox_message_processed",
        "result": result,
    }