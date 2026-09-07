from App.RunTime import RunTime
from Core.Storage.ConfigManager import ConfigManager
from Core.Storage.DB import DB


class App:
    """Главный объект приложения и его постоянных настроек."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.config_manager = ConfigManager()
        voice_enabled = self.config_manager.get_setting(
            "voice_enabled",
            True,
        )
        if not isinstance(voice_enabled, bool):
            raise ValueError("Настройка voice_enabled должна иметь тип bool")

        self.voice_enabled = voice_enabled
        self.database = DB()

        RunTime().is_database_created = True
        self._initialized = True

    def set_voice_enabled(self, enabled: bool) -> None:
        if not isinstance(enabled, bool):
            raise TypeError("Параметр enabled должен иметь тип bool")

        self.voice_enabled = enabled
        self.config_manager.set_setting("voice_enabled", enabled)
