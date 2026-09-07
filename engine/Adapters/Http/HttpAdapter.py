from threading import Thread

from flask import Flask, request
from werkzeug.serving import BaseWSGIServer, make_server

from Adapters.Http.HttpHandlers import HttpHandlers


class HttpAdapter:
    """Runs the local HTTP entry point without blocking the voice loop."""

    def __init__(
        self,
        flask_app: Flask,
        handlers: HttpHandlers,
        host: str = "127.0.0.1",
        port: int = 8765,
    ):
        self._flask_app = flask_app
        self._handlers = handlers
        self._host = host
        self._port = port
        self._server: BaseWSGIServer | None = None
        self._thread: Thread | None = None
        self._configure_cors()
        self._register_routes()

    def _configure_cors(self) -> None:
        allowed_origins = {
            "http://localhost:1420",
            "http://127.0.0.1:1420",
            "http://tauri.localhost",
            "https://tauri.localhost",
            "tauri://localhost",
        }

        @self._flask_app.after_request
        def add_cors_headers(response):
            origin = request.headers.get("Origin")
            if origin in allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Vary"] = "Origin"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
            return response

    def _register_routes(self) -> None:
        self._flask_app.add_url_rule(
            "/api/health", "health", self._handlers.health, methods=["GET"]
        )
        self._flask_app.add_url_rule(
            "/api/microphone",
            "microphone_state",
            self._handlers.microphone_state,
            methods=["GET"],
        )
        self._flask_app.add_url_rule(
            "/api/microphone",
            "toggle_microphone",
            lambda: self._handlers.toggle_microphone(request.get_json(silent=True)),
            methods=["PUT"],
        )
        self._flask_app.add_url_rule(
            "/api/commands",
            "command",
            lambda: self._handlers.command(request.get_json(silent=True)),
            methods=["POST"],
        )

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return

        self._server = make_server(
            self._host, self._port, self._flask_app, threaded=True
        )
        self._thread = Thread(
            target=self._server.serve_forever,
            name="whiskyhub-http",
            daemon=True,
        )
        self._thread.start()
        print(f"[HTTP] Сервер запущен: http://{self._host}:{self._port}")

    def stop(self) -> None:
        if self._server is None:
            return

        self._server.shutdown()
        if self._thread is not None:
            self._thread.join(timeout=2)
        self._server.server_close()
        self._server = None
        self._thread = None
        print("[HTTP] Сервер остановлен")
