import shutil
from pathlib import Path

from config import Config, USER_DATA_ROOT


class UserDataManager:
    """Creates editable application data in the user's Documents directory."""

    def __init__(self, data_root: str | Path = USER_DATA_ROOT):
        self.data_root = Path(data_root)

    def initialize(self) -> None:
        self.data_root.mkdir(parents=True, exist_ok=True)
        self._copy_if_missing(
            Config.SETTINGS_TEMPLATE_PATH,
            self.data_root / "config.json",
        )
        self._copy_if_missing(
            Config.COMMANDS_TEMPLATE_PATH,
            self.data_root / "commands.yaml",
        )

    @staticmethod
    def _copy_if_missing(source: Path, destination: Path) -> None:
        if destination.exists():
            return
        if not source.is_file():
            raise FileNotFoundError(f"Template file not found: {source}")

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
