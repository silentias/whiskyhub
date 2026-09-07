import sqlite3
from pathlib import Path

from config import Config


class ConnectionManager:
    """Создаёт настроенные подключения к локальной SQLite базе."""

    def __init__(self, database_path: str | Path = Config.DATABASE_PATH):
        self.database_path = Path(database_path)

    def get_connection(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
