from datetime import datetime
from typing import Optional

from app.database import get_connection
from app.domain.user import AuthorizedUserCreate


class UserRepository:
    def upsert_user(self, user: AuthorizedUserCreate) -> int:
        now = datetime.now().isoformat()
        email = user.teams_user_email.lower()

        with get_connection() as connection:
            existing = connection.execute(
                """
                SELECT id
                FROM authorized_users
                WHERE teams_user_email = ?
                """,
                (email,),
            ).fetchone()

            if existing:
                user_id = int(existing["id"])

                connection.execute(
                    """
                    UPDATE authorized_users
                    SET display_name = ?,
                        can_send_to_whatsapp = ?,
                        active = 1,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        user.display_name,
                        int(user.can_send_to_whatsapp),
                        now,
                        user_id,
                    ),
                )

                connection.commit()
                return user_id

            cursor = connection.execute(
                """
                INSERT INTO authorized_users (
                    teams_user_email,
                    display_name,
                    can_send_to_whatsapp,
                    active,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    email,
                    user.display_name,
                    int(user.can_send_to_whatsapp),
                    1,
                    now,
                    now,
                ),
            )

            connection.commit()
            return int(cursor.lastrowid)

    def get_active_user_by_email(self, teams_user_email: str) -> Optional[dict]:
        email = teams_user_email.lower()

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    teams_user_email,
                    display_name,
                    can_send_to_whatsapp,
                    active
                FROM authorized_users
                WHERE teams_user_email = ?
                  AND active = 1
                """,
                (email,),
            ).fetchone()

        if row is None:
            return None

        user = dict(row)
        user["can_send_to_whatsapp"] = bool(user["can_send_to_whatsapp"])
        user["active"] = bool(user["active"])

        return user

    def list_users(self) -> list[dict]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    teams_user_email,
                    display_name,
                    can_send_to_whatsapp,
                    active
                FROM authorized_users
                ORDER BY id DESC
                """
            ).fetchall()

        users = []

        for row in rows:
            user = dict(row)
            user["can_send_to_whatsapp"] = bool(user["can_send_to_whatsapp"])
            user["active"] = bool(user["active"])
            users.append(user)

        return users

    def deactivate_user(self, teams_user_email: str) -> bool:
        now = datetime.now().isoformat()
        email = teams_user_email.lower()

        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE authorized_users
                SET active = 0,
                    updated_at = ?
                WHERE teams_user_email = ?
                """,
                (
                    now,
                    email,
                ),
            )

            connection.commit()

        return cursor.rowcount > 0