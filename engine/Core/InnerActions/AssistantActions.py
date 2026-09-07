import sqlite3

from App.RunTime import RunTime
from Core.Storage.DB import DB


class AssistantActions:
    """Действия, которые изменяют состояние самого ассистента."""

    def __init__(self, database: DB, runtime: RunTime, speech=None):
        self.database = database
        self.runtime = runtime
        self._speech = speech

    def speak(self, text: str) -> None:
        if self._speech is None:
            return

        try:
            self._speech.speak(text)
        except Exception as error:
            print(f"[TTS] Не удалось озвучить сообщение: {error}")

    def changeAssistantName(self, name: str) -> bool:
        normalized_name = " ".join(name.split()).capitalize()

        if not normalized_name:
            self.speak("Имя не может быть пустым")
            return False

        if len(normalized_name) > 50:
            self.speak("Это имя слишком длинное")
            return False

        try:
            name_added = self.database.add_assistant_name(
                normalized_name,
                active=True,
            )

            if not name_added:
                name_activated = self.database.set_active_assistant_name(
                    normalized_name
                )
                if not name_activated:
                    self.speak("Не удалось изменить имя")
                    return False

            active_name = self.database.get_active_assistant_name()
            if active_name is None:
                self.speak("Не удалось получить новое имя")
                return False

            self.runtime.assistant_name = active_name
            print(f"[INNER ACTION] Новое имя ассистента: {active_name}")
            self.speak(f"Теперь меня зовут {active_name}")
            return True

        except (sqlite3.Error, ValueError) as error:
            print(f"[INNER ACTION] Не удалось изменить имя: {error}")
            self.speak("Не удалось изменить имя")
            return False
