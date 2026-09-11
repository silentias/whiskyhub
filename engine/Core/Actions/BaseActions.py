import platform
import logging
from datetime import datetime
from urllib.parse import quote_plus

from App.RunTime import RunTime
from Core.Actions.LinuxActions import LinuxActions
from Core.Actions.MacActions import MacActions
from Core.Actions.WindowsActions import WindowsActions

logger = logging.getLogger(__name__)


class BaseActions:
    """Единый интерфейс для действий на разных операционных системах."""

    def __init__(self, speech=None, runtime: RunTime | None = None):
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
        self._runtime = runtime or RunTime()
        logger.info("Определена операционная система: %s", self.os_type)

    def toggleMicrophone(self, value: str | bool) -> bool:
        """Enable or disable microphone capture for the voice adapter."""
        if isinstance(value, bool):
            enabled = value
        elif isinstance(value, str):
            normalized = value.strip().casefold()
            enabled_values = {"вкл", "включить", "включен", "включён", "on", "true", "1"}
            disabled_values = {"выкл", "выключить", "выключен", "off", "false", "0"}

            if normalized in enabled_values:
                enabled = True
            elif normalized in disabled_values:
                enabled = False
            else:
                logger.warning("Неизвестное состояние микрофона: %s", value)
                return False
        else:
            logger.warning("Состояние микрофона должно быть строкой или bool")
            return False

        if enabled:
            self._runtime.microphone_enabled.set()
            logger.info("Микрофон включён")
        else:
            self._runtime.microphone_enabled.clear()
            logger.info("Микрофон выключен")

        return True

    def _speak(self, text: str) -> bool:
        if self._speech is None:
            return False

        try:
            self._speech.speak(text)
            return True
        except Exception as error:
            logger.exception("Не удалось озвучить сообщение: %s", error)
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
            logger.exception("%s: %s", error_message, error)
            self._speak(error_message)
            return False

    def openBrowser(self, url="https://www.google.com") -> bool:
        return self._execute(
            lambda: self._platform_actions.openBrowser(url),
            "Открыла браузер",
            "Не удалось открыть браузер",
        )

    def searchInternet(self, query: str) -> bool:
        if not isinstance(query, str) or not query.strip():
            self._speak("Не удалось определить поисковый запрос")
            return False

        normalized_query = query.strip()
        search_url = f"https://www.google.com/search?q={quote_plus(normalized_query)}"
        return self._execute(
            lambda: self._platform_actions.openBrowser(search_url),
            f"Ищу в интернете {normalized_query}",
            "Не удалось открыть поисковик",
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

    def lockComputer(self) -> bool:
        return self._execute(
            self._platform_actions.lockComputer,
            "Заблокировала компьютер",
            "Не удалось заблокировать компьютер",
        )

    def takeScreenshot(self) -> bool:
        return self._execute(
            self._platform_actions.takeScreenshot,
            "Сделала скриншот",
            "Не удалось сделать скриншот",
        )

    def setVolume(self, level: int | str) -> bool:
        try:
            normalized_level = int(level)
        except (TypeError, ValueError):
            self._speak("Укажите громкость числом от нуля до ста")
            return False

        if not 0 <= normalized_level <= 100:
            self._speak("Громкость должна быть от нуля до ста")
            return False

        return self._execute(
            lambda: self._platform_actions.setVolume(normalized_level),
            f"Установила громкость на {normalized_level} процентов",
            "Не удалось установить громкость",
        )

    def muteSound(self) -> bool:
        return self._execute(
            self._platform_actions.muteSound,
            "Выключила звук",
            "Не удалось выключить звук",
        )

    def unmuteSound(self) -> bool:
        return self._execute(
            self._platform_actions.unmuteSound,
            "Включила звук",
            "Не удалось включить звук",
        )

    def increaseVolume(self) -> bool:
        return self._execute(
            self._platform_actions.increaseVolume,
            "Сделала громче",
            "Не удалось увеличить громкость",
        )

    def decreaseVolume(self) -> bool:
        return self._execute(
            self._platform_actions.decreaseVolume,
            "Сделала тише",
            "Не удалось уменьшить громкость",
        )

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
