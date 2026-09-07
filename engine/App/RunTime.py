from threading import Event

from config import Config


class RunTime:
    """Единое хранилище изменяемого состояния приложения."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.state_program = "running"
            cls._instance.state_voice = "awaiting_input"
            cls._instance.microphone_enabled = Event()
            cls._instance.microphone_enabled.set()
            cls._instance.is_database_created = False
            cls._instance.assistant_name = Config.DEFAULT_ASSISTANT_NAME
            cls._instance.pending_action = None

        return cls._instance
