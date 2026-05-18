import sqlite3
from pathlib import Path

from app.config import settings


def get_database_path() -> Path:
    database_path = Path(settings.database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    return database_path


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(get_database_path())
    connection.row_factory = sqlite3.Row
    return connection


def _ensure_column(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str,
) -> None:
    columns = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_column_names = {column["name"] for column in columns}

    if column_name not in existing_column_names:
        connection.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS bridge_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_group_id TEXT NOT NULL,
                source_group_name TEXT NOT NULL,
                author_name TEXT NOT NULL,
                body TEXT NOT NULL,
                message_type TEXT NOT NULL,
                direction TEXT NOT NULL,
                status TEXT NOT NULL,
                external_message_id TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teams_user_email TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                can_send_to_whatsapp INTEGER NOT NULL DEFAULT 1,
                active INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        _ensure_column(
            connection=connection,
            table_name="bridge_messages",
            column_name="author_id",
            column_definition="TEXT",
        )

        _ensure_column(
            connection=connection,
            table_name="bridge_messages",
            column_name="delivery_attempts",
            column_definition="INTEGER NOT NULL DEFAULT 0",
        )

        _ensure_column(
            connection=connection,
            table_name="bridge_messages",
            column_name="last_attempt_at",
            column_definition="TEXT",
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS channel_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                whatsapp_group_id TEXT NOT NULL UNIQUE,
                whatsapp_group_name TEXT NOT NULL,
                teams_team_name TEXT NOT NULL,
                teams_channel_name TEXT NOT NULL,
                teams_webhook_url TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS authorized_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teams_user_email TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                can_send_to_whatsapp INTEGER NOT NULL DEFAULT 1,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.commit()