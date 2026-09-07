from contextlib import closing

from Core.Storage.ConnectionManager import ConnectionManager
from Core.Storage.CreateManager import CreateManager


class DB:
    """Предоставляет операции чтения и изменения локальных данных."""

    _instance = None

    def __new__(cls, connection_manager: ConnectionManager | None = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self, connection_manager: ConnectionManager | None = None):
        if self._initialized:
            return

        self.connection_manager = connection_manager or ConnectionManager()
        self.create_manager = CreateManager(self.connection_manager)
        self.create_manager.create()
        self._initialized = True

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Имя ассистента не может быть пустым")
        return normalized_name

    def add_assistant_name(self, name: str, active: bool = False) -> bool:
        name = self._normalize_name(name)

        with closing(self.connection_manager.get_connection()) as connection, connection:
            existing_name = connection.execute(
                "SELECT id FROM assistant_names WHERE name = ?",
                (name,),
            ).fetchone()
            if existing_name is not None:
                return False

            if active:
                connection.execute(
                    "UPDATE assistant_names SET active = 0 WHERE active = 1"
                )

            connection.execute(
                "INSERT INTO assistant_names(name, active) VALUES (?, ?)",
                (name, int(active)),
            )
            return True

    def get_assistant_names(self) -> list[dict]:
        with closing(self.connection_manager.get_connection()) as connection, connection:
            rows = connection.execute(
                "SELECT id, name, active FROM assistant_names ORDER BY id"
            ).fetchall()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "active": bool(row["active"]),
            }
            for row in rows
        ]

    def get_active_assistant_name(self) -> str | None:
        with closing(self.connection_manager.get_connection()) as connection, connection:
            row = connection.execute(
                "SELECT name FROM assistant_names WHERE active = 1 LIMIT 1"
            ).fetchone()

        return row["name"] if row is not None else None

    def set_active_assistant_name(self, name: str) -> bool:
        name = self._normalize_name(name)

        with closing(self.connection_manager.get_connection()) as connection, connection:
            existing_name = connection.execute(
                "SELECT id FROM assistant_names WHERE name = ?",
                (name,),
            ).fetchone()
            if existing_name is None:
                return False

            connection.execute(
                "UPDATE assistant_names SET active = 0 WHERE active = 1"
            )
            connection.execute(
                "UPDATE assistant_names SET active = 1 WHERE id = ?",
                (existing_name["id"],),
            )
            return True

    def update_assistant_name(self, old_name: str, new_name: str) -> bool:
        old_name = self._normalize_name(old_name)
        new_name = self._normalize_name(new_name)

        with closing(self.connection_manager.get_connection()) as connection, connection:
            cursor = connection.execute(
                "UPDATE assistant_names SET name = ? WHERE name = ?",
                (new_name, old_name),
            )
            return cursor.rowcount > 0

    def delete_assistant_name(self, name: str) -> bool:
        name = self._normalize_name(name)

        with closing(self.connection_manager.get_connection()) as connection, connection:
            cursor = connection.execute(
                "DELETE FROM assistant_names WHERE name = ?",
                (name,),
            )
            return cursor.rowcount > 0
