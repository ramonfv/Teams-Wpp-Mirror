from datetime import datetime
from typing import Optional

from app.database import get_connection
from app.domain.mapping import ChannelMappingCreate


class MappingRepository:
    def upsert_mapping(self, mapping: ChannelMappingCreate) -> int:
        now = datetime.now().isoformat()

        with get_connection() as connection:
            existing = connection.execute(
                """
                SELECT id
                FROM channel_mappings
                WHERE whatsapp_group_id = ?
                """,
                (mapping.whatsapp_group_id,),
            ).fetchone()

            if existing:
                mapping_id = int(existing["id"])

                connection.execute(
                    """
                    UPDATE channel_mappings
                    SET whatsapp_group_name = ?,
                        teams_team_name = ?,
                        teams_channel_name = ?,
                        teams_webhook_url = ?,
                        active = 1,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        mapping.whatsapp_group_name,
                        mapping.teams_team_name,
                        mapping.teams_channel_name,
                        str(mapping.teams_webhook_url),
                        now,
                        mapping_id,
                    ),
                )
                connection.commit()
                return mapping_id

            cursor = connection.execute(
                """
                INSERT INTO channel_mappings (
                    whatsapp_group_id,
                    whatsapp_group_name,
                    teams_team_name,
                    teams_channel_name,
                    teams_webhook_url,
                    active,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mapping.whatsapp_group_id,
                    mapping.whatsapp_group_name,
                    mapping.teams_team_name,
                    mapping.teams_channel_name,
                    str(mapping.teams_webhook_url),
                    1,
                    now,
                    now,
                ),
            )

            connection.commit()
            return int(cursor.lastrowid)

    def get_active_mapping_by_whatsapp_group_id(
        self,
        whatsapp_group_id: str,
    ) -> Optional[dict]:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    whatsapp_group_id,
                    whatsapp_group_name,
                    teams_team_name,
                    teams_channel_name,
                    teams_webhook_url,
                    active
                FROM channel_mappings
                WHERE whatsapp_group_id = ?
                  AND active = 1
                """,
                (whatsapp_group_id,),
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def list_mappings(self) -> list[dict]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    whatsapp_group_id,
                    whatsapp_group_name,
                    teams_team_name,
                    teams_channel_name,
                    active
                FROM channel_mappings
                ORDER BY id DESC
                """
            ).fetchall()

        return [
            {
                **dict(row),
                "active": bool(row["active"]),
            }
            for row in rows
        ]

    def deactivate_mapping(self, whatsapp_group_id: str) -> bool:
        now = datetime.now().isoformat()

        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE channel_mappings
                SET active = 0,
                    updated_at = ?
                WHERE whatsapp_group_id = ?
                """,
                (
                    now,
                    whatsapp_group_id,
                ),
            )
            connection.commit()

        return cursor.rowcount > 0