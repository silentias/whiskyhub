import re
from pathlib import Path

import yaml

from Dispatcher.CommandDefinition import CommandDefinition


DEFAULT_COMMANDS_PATH = Path(__file__).parent / "Data" / "commands.yaml"


class CommandCatalog:
    """Загружает и проверяет определения команд из YAML."""

    def __init__(self, path: Path = DEFAULT_COMMANDS_PATH):
        self.path = Path(path)
        self._commands = self._load()
        self._by_slug = {command.slug: command for command in self._commands}
        self._by_phrase = {
            phrase: command
            for command in self._commands
            for phrase in command.voice_phrases
        }
        self._patterns = [
            (re.compile(pattern), command)
            for command in self._commands
            for pattern in command.voice_patterns
        ]

    def get_by_slug(self, slug: str) -> CommandDefinition | None:
        return self._by_slug.get(slug)

    @property
    def commands(self) -> tuple[CommandDefinition, ...]:
        return self._commands

    def match_voice_text(
        self,
        text: str,
    ) -> tuple[CommandDefinition, dict[str, str]] | None:
        command = self._by_phrase.get(text)
        if command is not None:
            return command, {}

        for pattern, pattern_command in self._patterns:
            match = pattern.fullmatch(text)
            if match is not None:
                return pattern_command, match.groupdict()

        return None

    def _load(self) -> tuple[CommandDefinition, ...]:
        if not self.path.is_file():
            raise FileNotFoundError(f"Файл команд не найден: {self.path}")

        try:
            document = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            raise ValueError(f"Некорректный YAML в {self.path}: {error}") from error

        rows = document.get("commands") if isinstance(document, dict) else None
        if not isinstance(rows, list) or not rows:
            raise ValueError("В YAML должен быть непустой список commands")

        commands = tuple(self._parse_command(row) for row in rows)
        self._validate_unique(commands)
        return commands

    @staticmethod
    def _parse_command(row: object) -> CommandDefinition:
        if not isinstance(row, dict):
            raise ValueError("Каждая команда в YAML должна быть объектом")

        command_id = row.get("id")
        slug = row.get("slug")
        if not isinstance(command_id, int) or command_id <= 0:
            raise ValueError("id команды должен быть положительным целым числом")
        if not isinstance(slug, str) or not slug.strip():
            raise ValueError(f"У команды id={command_id} отсутствует slug")

        phrases = CommandCatalog._string_list(row, "voice_phrases")
        patterns = CommandCatalog._string_list(row, "voice_patterns")
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as error:
                raise ValueError(f"Ошибка regex команды {slug}: {error}") from error

        action_group = row.get("action_group")
        action_method = row.get("action_method")
        if (action_group is None) != (action_method is None):
            raise ValueError(
                f"У команды {slug} action_group и action_method задаются вместе"
            )
        if action_group is not None and not isinstance(action_group, str):
            raise ValueError(f"Некорректный action_group команды {slug}")
        if action_method is not None and not isinstance(action_method, str):
            raise ValueError(f"Некорректный action_method команды {slug}")

        requires_confirmation = row.get("requires_confirmation", False)
        if not isinstance(requires_confirmation, bool):
            raise ValueError(f"requires_confirmation команды {slug} должен быть bool")

        confirmation_message = row.get("confirmation_message", "")
        if not isinstance(confirmation_message, str):
            raise ValueError(f"Некорректный confirmation_message команды {slug}")
        if requires_confirmation and not confirmation_message.strip():
            raise ValueError(f"Для команды {slug} нужен confirmation_message")

        return CommandDefinition(
            id=command_id,
            slug=slug.strip(),
            voice_phrases=tuple(CommandCatalog._normalize(x) for x in phrases),
            voice_patterns=tuple(patterns),
            action_group=action_group,
            action_method=action_method,
            requires_confirmation=requires_confirmation,
            confirmation_message=confirmation_message.strip(),
        )

    @staticmethod
    def _string_list(row: dict, field_name: str) -> list[str]:
        value = row.get(field_name, [])
        if not isinstance(value, list) or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            raise ValueError(f"Поле {field_name} должно быть списком непустых строк")
        return value

    @staticmethod
    def _validate_unique(commands: tuple[CommandDefinition, ...]) -> None:
        ids = [command.id for command in commands]
        slugs = [command.slug for command in commands]
        phrases = [phrase for command in commands for phrase in command.voice_phrases]
        if len(ids) != len(set(ids)):
            raise ValueError("В YAML найдены повторяющиеся id команд")
        if len(slugs) != len(set(slugs)):
            raise ValueError("В YAML найдены повторяющиеся slug команд")
        if len(phrases) != len(set(phrases)):
            raise ValueError("В YAML найдены повторяющиеся голосовые фразы")

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.lower().strip().split())
