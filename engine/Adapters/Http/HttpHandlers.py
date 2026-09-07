from dataclasses import asdict
from typing import Any

from flask import jsonify

from App.RunTime import RunTime
from Contracts.CommandRequest import CommandRequest
from Dispatcher.CentralDispatcher import CentralDispatcher


class HttpHandlers:
    """Validates HTTP input and forwards commands to CentralDispatcher."""

    def __init__(self, dispatcher: CentralDispatcher, runtime: RunTime):
        self._dispatcher = dispatcher
        self._runtime = runtime

    def health(self):
        return jsonify(status="ok"), 200

    def microphone_state(self):
        return jsonify(enabled=self._runtime.microphone_enabled.is_set()), 200

    def toggle_microphone(self, payload: Any):
        if not isinstance(payload, dict) or not isinstance(payload.get("enabled"), bool):
            return jsonify(error="Поле enabled обязательно и должно иметь тип bool"), 400

        return self._dispatch({
            "slug": "toggle_microphone",
            "arguments": {"value": payload["enabled"]},
            "should_respond_with_voice": False,
        })

    def command(self, payload: Any):
        if not isinstance(payload, dict):
            return jsonify(error="Тело запроса должно быть JSON-объектом"), 400

        slug = payload.get("slug")
        arguments = payload.get("arguments", {})
        should_respond = payload.get("should_respond_with_voice", False)
        if not isinstance(slug, str) or not slug.strip():
            return jsonify(error="Поле slug обязательно"), 400
        if not isinstance(arguments, dict):
            return jsonify(error="Поле arguments должно быть JSON-объектом"), 400
        if not isinstance(should_respond, bool):
            return jsonify(error="Поле should_respond_with_voice должно быть bool"), 400

        return self._dispatch({
            "slug": slug.strip(),
            "arguments": arguments,
            "should_respond_with_voice": should_respond,
        })

    def _dispatch(self, payload: dict[str, Any]):
        command_request = CommandRequest(
            slug=payload["slug"],
            arguments=payload["arguments"],
            should_respond_with_voice=payload["should_respond_with_voice"],
            source="http",
        )
        result = self._dispatcher.dispatch(command_request)
        status_code = 200
        if result.status == "confirmation_required":
            status_code = 202
        elif not result.success:
            status_code = 404 if result.status == "unknown_command" else 422

        response = asdict(result)
        response["request_id"] = command_request.request_id
        return jsonify(response), status_code
