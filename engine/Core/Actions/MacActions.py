import webbrowser
import logging
import shutil
import subprocess

logger = logging.getLogger(__name__)
from pathlib import Path


class MacActions:
    @staticmethod
    def _start_process(command) -> bool:
        try:
            subprocess.Popen(command)
            return True
        except OSError as error:
            logger.exception("Не удалось выполнить команду: %s", error)
            return False

    def openBrowser(self, url="https://www.google.com") -> bool:
        try:
            return bool(webbrowser.open(url))
        except webbrowser.Error as error:
            logger.exception("Не удалось открыть браузер: %s", error)
            return False

    def openCalculator(self) -> bool:
        return self._open_system_app("Calculator")

    def openNotepad(self) -> bool:
        return self._open_system_app("TextEdit")

    def openFileManager(self) -> bool:
        open_path = shutil.which("open")
        if not open_path:
            logger.warning("Системная команда open не найдена")
            return False

        return self._start_process([open_path, str(Path.home())])

    def openTerminal(self) -> bool:
        return self._open_system_app("Terminal")

    def openCalendar(self) -> bool:
        return self._open_system_app("Calendar")

    def openTaskManager(self) -> bool:
        return self._open_system_app("Activity Monitor")

    def openSettings(self) -> bool:
        return self._open_system_app("System Settings")

    def emptyTrash(self) -> bool:
        osascript_path = shutil.which("osascript")
        if not osascript_path:
            logger.warning("Не найдена команда очистки корзины")
            return False

        return self._start_process(
            [
                osascript_path,
                "-e",
                'tell application "Finder" to empty trash',
            ]
        )

    def shutdownComputer(self) -> bool:
        osascript_path = shutil.which("osascript")
        if not osascript_path:
            logger.warning("Системная команда выключения не найдена")
            return False

        return self._start_process(
            [
                osascript_path,
                "-e",
                'tell application "System Events" to shut down',
            ]
        )

    def restartComputer(self) -> bool:
        osascript_path = shutil.which("osascript")
        if not osascript_path:
            logger.warning("Системная команда перезагрузки не найдена")
            return False

        return self._start_process(
            [
                osascript_path,
                "-e",
                'tell application "System Events" to restart',
            ]
        )

    def openApplication(self, app_name: str) -> bool:
        return self._open_system_app(app_name)

    def _open_system_app(self, app_name: str) -> bool:
        open_path = shutil.which("open")
        if not open_path:
            logger.warning("Системная команда open не найдена")
            return False

        return self._start_process([open_path, "-a", app_name])
