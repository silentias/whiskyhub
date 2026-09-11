import logging
import time

from Core.Logging import configure_logging

configure_logging()
logger = logging.getLogger("whiskyhub")

from App.App import App
from Core.Actions.BaseActions import BaseActions
from Dispatcher.CentralDispatcher import CentralDispatcher
from Dispatcher.CommandCatalog import CommandCatalog
from Core.InnerActions.AssistantActions import AssistantActions
from App.RunTime import RunTime
from Adapters.Voice.VoiceAdapter import VoiceAdapter
from Adapters.Voice.VoiceCommandParser import VoiceCommandParser
from Adapters.Voice.VoiceListener import VoiceListener
from Adapters.Http.HttpAdapter import HttpAdapter
from Adapters.Http.HttpHandlers import HttpHandlers



def main():
    logger.info("Программа запущена")

    app = App()
    runtime = RunTime()
    runtime.assistant_name = (
        app.database.get_active_assistant_name()
        or runtime.assistant_name
    )

    speech = None
    if app.voice_enabled:
        from Core.VoiceOutManager.SpeechSynthesizer import speech_synthesizer

        speech = speech_synthesizer

    listener = VoiceListener(runtime)
    command_catalog = CommandCatalog()
    voice_parser = VoiceCommandParser(command_catalog)
    voice_adapter = VoiceAdapter(
        listener=listener,
        assistant_name_provider=lambda: runtime.assistant_name,
        respond_with_voice=app.voice_enabled,
        parser=voice_parser,
    )
    actions = BaseActions(speech, runtime)
    inner_actions = AssistantActions(app.database, runtime, speech)
    dispatcher = CentralDispatcher(
        actions,
        inner_actions,
        runtime,
        command_catalog,
    )
    http_handlers = HttpHandlers(dispatcher, runtime)
    http_adapter = HttpAdapter(app.flask_app, http_handlers)
    http_adapter.start()
    logger.info("Скажите '%s' для активации", runtime.assistant_name)

    try:
        while runtime.state_program == "running":
            try:
                request = voice_adapter.get_command_request()

                result = dispatcher.dispatch(request)
                voice_adapter.complete_session(
                    keep_active=result.keep_session_active
                )

                if result.keep_session_active:
                    logger.info("Ожидаю продолжение голосовой сессии")
                else:
                    logger.info(
                        "Скажите '%s' для новой команды", runtime.assistant_name
                    )
            except Exception as error:
                logger.exception("Ошибка голосового цикла")
                voice_adapter.complete_session(keep_active=False)
                listener.recover()
                time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Получен Ctrl+C")
    finally:
        runtime.state_program = "stopped"
        listener.close()
        http_adapter.stop()
        logger.info("Программа завершена")

if __name__ == "__main__":
    main()
