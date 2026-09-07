import webbrowser
import shutil
import subprocess
from pathlib import Path


class LinuxActions:
    @staticmethod
    def _start_process(command) -> bool:
        try:
            subprocess.Popen(command)
            return True
        except OSError as error:
            print(f"[LINUX] Не удалось запустить {command[0]}: {error}")
            return False

    def openBrowser(self, url="https://www.google.com") -> bool:
        try:
            return bool(webbrowser.open(url))
        except webbrowser.Error as error:
            print(f"[LINUX] Не удалось открыть браузер: {error}")
            return False

    def openCalculator(self) -> bool:
        calculator_names = (
            "gnome-calculator",
            "kcalc",
            "galculator",
            "mate-calc",
            "xcalc",
        )

        for calculator_name in calculator_names:
            calculator_path = shutil.which(calculator_name)
            if calculator_path:
                return self._start_process([calculator_path])

        print("[LINUX] В системе не найден калькулятор")
        return False

    def openNotepad(self) -> bool:
        editor_names = (
            "gedit",
            "kate",
            "xed",
            "mousepad",
            "leafpad",
        )

        for editor_name in editor_names:
            editor_path = shutil.which(editor_name)
            if editor_path:
                return self._start_process([editor_path])

        print("[LINUX] В системе не найден текстовый редактор")
        return False

    def openFileManager(self) -> bool:
        file_manager_path = shutil.which("xdg-open")
        if not file_manager_path:
            print("[LINUX] В системе не найден файловый менеджер")
            return False

        return self._start_process([file_manager_path, str(Path.home())])

    def openTerminal(self) -> bool:
        terminal_names = (
            "x-terminal-emulator",
            "gnome-terminal",
            "konsole",
            "xfce4-terminal",
            "xterm",
        )

        for terminal_name in terminal_names:
            terminal_path = shutil.which(terminal_name)
            if terminal_path:
                return self._start_process([terminal_path])

        print("[LINUX] В системе не найден терминал")
        return False

    def openCalendar(self) -> bool:
        calendar_names = ("gnome-calendar", "korganizer", "orage")

        for calendar_name in calendar_names:
            calendar_path = shutil.which(calendar_name)
            if calendar_path:
                return self._start_process([calendar_path])

        return self.openBrowser("https://calendar.google.com")

    def openTaskManager(self) -> bool:
        task_manager_names = (
            "gnome-system-monitor",
            "plasma-systemmonitor",
            "ksysguard",
            "xfce4-taskmanager",
        )

        for task_manager_name in task_manager_names:
            task_manager_path = shutil.which(task_manager_name)
            if task_manager_path:
                return self._start_process([task_manager_path])

        print("[LINUX] В системе не найден диспетчер задач")
        return False

    def openSettings(self) -> bool:
        settings_names = (
            "gnome-control-center",
            "systemsettings",
            "xfce4-settings-manager",
            "mate-control-center",
        )

        for settings_name in settings_names:
            settings_path = shutil.which(settings_name)
            if settings_path:
                return self._start_process([settings_path])

        print("[LINUX] В системе не найдены системные настройки")
        return False

    def emptyTrash(self) -> bool:
        gio_path = shutil.which("gio")
        if gio_path:
            return self._start_process([gio_path, "trash", "--empty"])

        trash_empty_path = shutil.which("trash-empty")
        if trash_empty_path:
            return self._start_process([trash_empty_path])

        print("[LINUX] Не найдена команда для очистки корзины")
        return False

    def shutdownComputer(self) -> bool:
        systemctl_path = shutil.which("systemctl")
        if not systemctl_path:
            print("[LINUX] Системная команда выключения не найдена")
            return False

        return self._start_process([systemctl_path, "poweroff"])

    def restartComputer(self) -> bool:
        systemctl_path = shutil.which("systemctl")
        if not systemctl_path:
            print("[LINUX] Системная команда перезагрузки не найдена")
            return False

        return self._start_process([systemctl_path, "reboot"])

    def openApplication(self, app_name: str) -> bool:
        app_path = shutil.which(app_name)
        if not app_path:
            print(f"[LINUX] Приложение не найдено: {app_name}")
            return False

        return self._start_process([app_path])
