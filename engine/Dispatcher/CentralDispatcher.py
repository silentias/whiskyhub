import logging
from threading import RLock

from Core.Actions.BaseActions import BaseActions
from App.RunTime import RunTime
from Contracts.CommandRequest import CommandRequest
from Contracts.CommandResult import CommandResult
from Dispatcher.CommandCatalog import CommandCatalog
from Dispatcher.CommandDefinition import CommandDefinition
from Core.InnerActions.AssistantActions import AssistantActions

logger = logging.getLogger(__name__)


class CentralDispatcher:
    """Находит команду по slug и управляет сценарием её выполнения."""

    def __init__(
        self,
        base_actions: BaseActions,
        inner_actions: AssistantActions,
        runtime: RunTime,
        command_catalog: CommandCatalog,
    ):
        self._base_actions = base_actions
        self._inner_actions = inner_actions
        self._runtime = runtime
        self._command_catalog = command_catalog
        self._pending_request: CommandRequest | None = None
        self._dispatch_lock = RLock()
        self._action_groups = {
            "base_actions": base_actions,
            "inner_actions": inner_actions,
        }
        self._validate_action_methods()

    def dispatch(self, request: CommandRequest) -> CommandResult:
        with self._dispatch_lock:
            return self._dispatch(request)

    def list_commands(self) -> list[dict]:
        """Return a public, read-only representation of available commands."""
        return [
            {
                "id": definition.id,
                "slug": definition.slug,
                "voice_phrases": list(definition.voice_phrases),
                "voice_patterns": list(definition.voice_patterns),
                "requires_confirmation": definition.requires_confirmation,
            }
            for definition in self._command_catalog.commands
        ]

    def _dispatch(self, request: CommandRequest) -> CommandResult:
        logger.info("Получена команда: %s; source=%s", request.slug, request.source)

        if request.slug == "confirm_action":
            return self._confirm_pending(request)

        if request.slug == "cancel_action":
            return self._cancel_pending(request)

        if self._pending_request is not None:
            message = "Сначала подтвердите или отмените ожидающую команду"
            self._respond(request, message)
            return CommandResult(
                success=False,
                status="confirmation_required",
                message=message,
                keep_session_active=True,
            )

        definition = self._command_catalog.get_by_slug(request.slug)
        if definition is None:
            message = "Неизвестная команда"
            self._respond(request, message)
            return CommandResult(False, "unknown_command", message)

        if definition.requires_confirmation:
            self._pending_request = request
            self._runtime.pending_action = request.slug
            self._respond(request, definition.confirmation_message)
            logger.info("Ожидается подтверждение: %s", request.slug)
            return CommandResult(
                success=True,
                status="confirmation_required",
                message=definition.confirmation_message,
                keep_session_active=True,
            )

        return self._execute(request, definition)

    def _confirm_pending(self, confirmation: CommandRequest) -> CommandResult:
        pending_request = self._pending_request
        if pending_request is None:
            message = "Нет команды для подтверждения"
            self._respond(confirmation, message)
            return CommandResult(False, "nothing_to_confirm", message)

        definition = self._command_catalog.get_by_slug(pending_request.slug)
        self._clear_pending()
        if definition is None:
            message = "Ожидающая команда больше не существует"
            self._respond(confirmation, message)
            return CommandResult(False, "unknown_command", message)

        return self._execute(pending_request, definition)

    def _cancel_pending(self, cancellation: CommandRequest) -> CommandResult:
        if self._pending_request is None:
            message = "Нет команды для отмены"
            self._respond(cancellation, message)
            return CommandResult(False, "nothing_to_cancel", message)

        self._clear_pending()
        message = "Команда отменена"
        self._respond(cancellation, message)
        logger.info("Ожидающая команда отменена")
        return CommandResult(True, "cancelled", message)

    def _execute(
        self,
        request: CommandRequest,
        definition: CommandDefinition,
    ) -> CommandResult:
        try:
            handler = self._resolve_handler(definition)
            success = bool(handler(**request.arguments))
        except (TypeError, ValueError) as error:
            message = f"Некорректные аргументы команды: {error}"
            logger.warning("%s", message)
            self._respond(request, "Не удалось выполнить команду")
            return CommandResult(False, "invalid_arguments", message)
        except Exception as error:
            message = f"Ошибка выполнения команды: {error}"
            logger.exception("%s", message)
            self._respond(request, "Не удалось выполнить команду")
            return CommandResult(False, "execution_error", message)

        status = "completed" if success else "failed"
        logger.info("Результат команды %s: %s", request.slug, status)
        return CommandResult(success, status)

    def _respond(self, request: CommandRequest, message: str) -> None:
        if request.should_respond_with_voice:
            self._inner_actions.speak(message)

    def _clear_pending(self) -> None:
        self._pending_request = None
        self._runtime.pending_action = None

    def _resolve_handler(self, definition: CommandDefinition):
        if definition.action_group is None or definition.action_method is None:
            raise ValueError(f"Для команды {definition.slug} не указан Action")

        action_group = self._action_groups.get(definition.action_group)
        if action_group is None:
            raise ValueError(
                f"Неизвестная группа Actions: {definition.action_group}"
            )

        if definition.action_method.startswith("_"):
            raise ValueError("Нельзя вызывать приватные методы Actions")

        handler = getattr(action_group, definition.action_method, None)
        if not callable(handler):
            raise ValueError(
                f"Метод {definition.action_group}.{definition.action_method} не найден"
            )
        return handler

    def _validate_action_methods(self) -> None:
        control_slugs = {"confirm_action", "cancel_action"}
        for definition in self._command_catalog.commands:
            if definition.slug not in control_slugs:
                self._resolve_handler(definition)
