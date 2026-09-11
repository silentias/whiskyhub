import webbrowser
import logging
import ctypes
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class WindowsActions:
    @staticmethod
    def _start_process(command) -> bool:
        try:
            subprocess.Popen(command)
            return True
        except OSError as error:
            logger.exception("Не удалось запустить %s: %s", command[0], error)
            return False

    def openBrowser(self, url="https://www.google.com") -> bool:
        try:
            return bool(webbrowser.open(url))
        except webbrowser.Error as error:
            logger.exception("Не удалось открыть браузер: %s", error)
            return False

    def openCalculator(self) -> bool:
        return self._start_process(["calc.exe"])

    def openNotepad(self) -> bool:
        return self._start_process(["notepad.exe"])

    def openFileManager(self) -> bool:
        return self._start_process(["explorer.exe", str(Path.home())])

    def openTerminal(self) -> bool:
        terminal_names = ("wt.exe", "powershell.exe", "cmd.exe")

        for terminal_name in terminal_names:
            terminal_path = shutil.which(terminal_name)
            if terminal_path:
                return self._start_process([terminal_path])

        logger.warning("В системе не найден терминал")
        return False

    def openCalendar(self) -> bool:
        try:
            os.startfile("outlookcal:")
            return True
        except OSError as error:
            logger.warning("Системный календарь недоступен: %s", error)
            return self.openBrowser("https://calendar.google.com")

    def openTaskManager(self) -> bool:
        return self._start_process(["taskmgr.exe"])

    def openSettings(self) -> bool:
        try:
            os.startfile("ms-settings:")
            return True
        except OSError as error:
            logger.exception("Не удалось открыть настройки: %s", error)
            return False

    def emptyTrash(self) -> bool:
        no_confirmation = 0x00000001
        no_progress = 0x00000002
        no_sound = 0x00000004

        try:
            result = ctypes.windll.shell32.SHEmptyRecycleBinW(
                None,
                None,
                no_confirmation | no_progress | no_sound,
            )
            return result == 0
        except OSError as error:
            logger.exception("Не удалось очистить корзину: %s", error)
            return False

    def shutdownComputer(self) -> bool:
        shutdown_path = shutil.which("shutdown.exe")
        if not shutdown_path:
            logger.warning("Системная команда выключения не найдена")
            return False

        return self._start_process([shutdown_path, "/s", "/t", "5"])

    def restartComputer(self) -> bool:
        shutdown_path = shutil.which("shutdown.exe")
        if not shutdown_path:
            logger.warning("Системная команда перезагрузки не найдена")
            return False

        return self._start_process([shutdown_path, "/r", "/t", "5"])

    def lockComputer(self) -> bool:
        try:
            return bool(ctypes.windll.user32.LockWorkStation())
        except Exception as error:
            logger.exception("Не удалось заблокировать компьютер: %s", error)
            return False

    def takeScreenshot(self) -> bool:
        try:
            from PIL import ImageGrab

            screenshots_directory = Path.home() / "Pictures" / "WhiskyHub"
            screenshots_directory.mkdir(parents=True, exist_ok=True)
            filename = datetime.now().strftime("screenshot_%Y-%m-%d_%H-%M-%S.png")
            ImageGrab.grab(all_screens=True).save(screenshots_directory / filename)
            logger.info("Скриншот сохранён: %s", screenshots_directory / filename)
            return True
        except Exception as error:
            logger.exception("Не удалось сделать скриншот: %s", error)
            return False

    @staticmethod
    def _get_endpoint_volume():
        from pycaw.pycaw import AudioUtilities

        return AudioUtilities.GetSpeakers().EndpointVolume

    def setVolume(self, level: int | str) -> bool:
        try:
            normalized_level = int(level)
            if not 0 <= normalized_level <= 100:
                logger.warning("Громкость должна быть от 0 до 100")
                return False

            self._get_endpoint_volume().SetMasterVolumeLevelScalar(
                normalized_level / 100,
                None,
            )
            return True
        except Exception as error:
            logger.exception("Не удалось установить громкость: %s", error)
            return False

    def muteSound(self) -> bool:
        return self._set_mute(True)

    def unmuteSound(self) -> bool:
        return self._set_mute(False)

    def _set_mute(self, muted: bool) -> bool:
        try:
            self._get_endpoint_volume().SetMute(int(muted), None)
            return True
        except Exception as error:
            logger.exception("Не удалось изменить состояние звука: %s", error)
            return False

    def increaseVolume(self) -> bool:
        return self._change_volume(10)

    def decreaseVolume(self) -> bool:
        return self._change_volume(-10)

    def _change_volume(self, delta: int) -> bool:
        try:
            endpoint = self._get_endpoint_volume()
            current_level = endpoint.GetMasterVolumeLevelScalar() * 100
            new_level = max(0, min(100, round(current_level + delta)))
            endpoint.SetMasterVolumeLevelScalar(new_level / 100, None)
            return True
        except Exception as error:
            logger.exception("Не удалось изменить громкость: %s", error)
            return False

    def openApplication(self, app_name: str) -> bool:
        app_path = shutil.which(app_name)
        if not app_path:
            logger.warning("Приложение не найдено: %s", app_name)
            return False

        return self._start_process([app_path])
