from contextlib import closing

from config import Config
from Core.Storage.ConnectionManager import ConnectionManager


class CreateManager:
    """Создаёт таблицы и начальные данные приложения."""

    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager

    def create(self) -> None:
        with closing(self.connection_manager.get_connection()) as connection, connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS assistant_names (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    active INTEGER NOT NULL DEFAULT 0
                        CHECK (active IN (0, 1))
                )
                """
            )
            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS one_active_assistant_name
                ON assistant_names(active)
                WHERE active = 1
                """
            )

            names_count = connection.execute(
                "SELECT COUNT(*) FROM assistant_names"
            ).fetchone()[0]

            if names_count == 0:
                connection.execute(
                    "INSERT INTO assistant_names(name, active) VALUES (?, 1)",
                    (Config.DEFAULT_ASSISTANT_NAME,),
                )
