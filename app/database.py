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
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()