import platform
from datetime import datetime

from Core.Actions.LinuxActions import LinuxActions
from Core.Actions.MacActions import MacActions
from Core.Actions.WindowsActions import WindowsActions


class BaseActions:
    """Единый интерфейс для действий на разных операционных системах."""

    def __init__(self, speech=None):
        system_name = platform.system()
        actions_by_system = {
            "Windows": ("windows", WindowsActions),
            "Linux": ("linux", LinuxActions),
            "Darwin": ("mac", MacActions),
        }

        if system_name not in actions_by_system:
            raise OSError(f"Неподдерживаемая операционная система: {system_name}")

        self.os_type, actions_class = actions_by_system[system_name]
        self._platform_actions = actions_class()
        self._speech = speech
        print(f"[ACTION] Определена операционная система: {self.os_type}")

    def _speak(self, text: str) -> bool:
        if self._speech is None:
            return False

        try:
            self._speech.speak(text)
            return True
        except Exception as error:
            print(f"[TTS] Не удалось озвучить сообщение: {error}")
            return False

    def _execute(self, action, success_message: str, error_message: str) -> bool:
        try:
            result = action()
            if result is False:
                self._speak(error_message)
                return False

            self._speak(success_message)
            return True
        except (FileNotFoundError, OSError) as error:
            print(f"[ACTION] {error_message}: {error}")
            self._speak(error_message)
            return False

    def openBrowser(self, url="https://www.google.com") -> bool:
        return self._execute(
            lambda: self._platform_actions.openBrowser(url),
            "Открыла браузер",
            "Не удалось открыть браузер",
        )

    def openCalculator(self) -> bool:
        return self._execute(
            self._platform_actions.openCalculator,
            "Открыла калькулятор",
            "Не удалось открыть калькулятор. Возможно, он не установлен",
        )

    def openNotepad(self) -> bool:
        return self._execute(
            self._platform_actions.openNotepad,
            "Открыла блокнот",
            "Не удалось открыть блокнот. Возможно, он не установлен",
        )

    def openFileManager(self) -> bool:
        return self._execute(
            self._platform_actions.openFileManager,
            "Открыла проводник",
            "Не удалось открыть проводник",
        )

    def openTerminal(self) -> bool:
        return self._execute(
            self._platform_actions.openTerminal,
            "Открыла терминал",
            "Не удалось открыть терминал. Возможно, он не установлен",
        )

    def openCalendar(self) -> bool:
        return self._execute(
            self._platform_actions.openCalendar,
            "Открыла календарь",
            "Не удалось открыть календарь. Возможно, он не установлен",
        )

    def openTaskManager(self) -> bool:
        return self._execute(
            self._platform_actions.openTaskManager,
            "Открыла диспетчер задач",
            "Не удалось открыть диспетчер задач",
        )

    def openSettings(self) -> bool:
        return self._execute(
            self._platform_actions.openSettings,
            "Открыла настройки",
            "Не удалось открыть настройки",
        )

    def emptyTrash(self) -> bool:
        result = self._platform_actions.emptyTrash()

        if result:
            self._speak("Корзина очищена")
        else:
            self._speak("Не удалось очистить корзину")

        return result

    def shutdownComputer(self) -> bool:
        self._speak("Выключаю компьютер")
        result = self._platform_actions.shutdownComputer()

        if not result:
            self._speak("Не удалось выключить компьютер")

        return result

    def restartComputer(self) -> bool:
        self._speak("Перезагружаю компьютер")
        result = self._platform_actions.restartComputer()

        if not result:
            self._speak("Не удалось перезагрузить компьютер")

        return result

    def getCurrentDateTime(self):
        now = datetime.now()
        weekdays = (
            "понедельник",
            "вторник",
            "среда",
            "четверг",
            "пятница",
            "суббота",
            "воскресенье",
        )

        return (
            f"Сейчас {now:%H:%M}. "
            f"Сегодня {now:%d.%m.%Y}, {weekdays[now.weekday()]}"
        )

    def sayCurrentDateTime(self) -> bool:
        date_time_text = self.getCurrentDateTime()
        self._speak(date_time_text)
        return True

    def openApplication(self, app_name: str) -> bool:
        return self._execute(
            lambda: self._platform_actions.openApplication(app_name),
            f"Открыла приложение {app_name}",
            f"Не удалось открыть приложение {app_name}",
        )
