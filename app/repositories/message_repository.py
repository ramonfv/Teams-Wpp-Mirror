from datetime import datetime
from typing import Optional

from app.database import get_connection
from app.domain.message import BridgeMessage


class MessageRepository:
    def create_received_message(
        self,
        message: BridgeMessage,
        direction: str = "WHATSAPP_TO_TEAMS",
    ) -> int:
        now = datetime.now().isoformat()

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO bridge_messages (
                    source,
                    source_group_id,
                    source_group_name,
                    author_name,
                    author_id,
                    body,
                    message_type,
                    direction,
                    status,
                    external_message_id,
                    error_message,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message.source.value,
                    message.source_group_id,
                    message.source_group_name,
                    message.author_name,
                    message.author_id,
                    message.body,
                    message.message_type.value,
                    direction,
                    "RECEIVED",
                    message.external_message_id,
                    None,
                    now,
                    now,
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def update_status(
        self,
        message_id: int,
        status: str,
        error_message: Optional[str] = None,
        external_message_id: Optional[str] = None,
    ) -> None:
        now = datetime.now().isoformat()

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE bridge_messages
                SET status = ?,
                    error_message = ?,
                    external_message_id = COALESCE(?, external_message_id),
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    status,
                    error_message,
                    external_message_id,
                    now,
                    message_id,
                ),
            )
            connection.commit()

    def register_delivery_attempt(self, message_id: int) -> None:
        now = datetime.now().isoformat()

        with get_connection() as connection:
            connection.execute(
                """
                UPDATE bridge_messages
                SET delivery_attempts = delivery_attempts + 1,
                    last_attempt_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    now,
                    now,
                    message_id,
                ),
            )
            connection.commit()

    def list_recent_messages(self, limit: int = 20) -> list[dict]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    source,
                    source_group_id,
                    source_group_name,
                    author_name,
                    author_id,
                    body,
                    direction,
                    status,
                    external_message_id,
                    error_message,
                    delivery_attempts,
                    last_attempt_at,
                    created_at,
                    updated_at
                FROM bridge_messages
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def list_ready_to_send_to_whatsapp(self, limit: int = 10) -> list[dict]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    source,
                    source_group_id,
                    source_group_name,
                    author_name,
                    author_id,
                    body,
                    message_type,
                    direction,
                    status,
                    delivery_attempts,
                    created_at,
                    updated_at
                FROM bridge_messages
                WHERE direction = 'TEAMS_TO_WHATSAPP'
                  AND status = 'READY_TO_SEND_TO_WHATSAPP'
                ORDER BY id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def get_message_by_id(self, message_id: int) -> dict | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    source,
                    source_group_id,
                    source_group_name,
                    author_name,
                    author_id,
                    body,
                    message_type,
                    direction,
                    status,
                    external_message_id,
                    error_message,
                    delivery_attempts,
                    last_attempt_at,
                    created_at,
                    updated_at
                FROM bridge_messages
                WHERE id = ?
                """,
                (message_id,),
            ).fetchone()

        if row is None:
            return None

        return dict(row)