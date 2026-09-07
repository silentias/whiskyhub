from App.App import App
from Core.Actions.BaseActions import BaseActions
from Dispatcher.CentralDispatcher import CentralDispatcher
from Dispatcher.CommandCatalog import CommandCatalog
from Core.InnerActions.AssistantActions import AssistantActions
from App.RunTime import RunTime
from Adapters.Voice.VoiceAdapter import VoiceAdapter
from Adapters.Voice.VoiceCommandParser import VoiceCommandParser
from Adapters.Voice.VoiceListener import VoiceListener



def main():
    print("[MAIN] Программа запущена")

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

    listener = VoiceListener()
    command_catalog = CommandCatalog()
    voice_parser = VoiceCommandParser(command_catalog)
    voice_adapter = VoiceAdapter(
        listener=listener,
        assistant_name_provider=lambda: runtime.assistant_name,
        respond_with_voice=app.voice_enabled,
        parser=voice_parser,
    )
    actions = BaseActions(speech)
    inner_actions = AssistantActions(app.database, runtime, speech)
    dispatcher = CentralDispatcher(
        actions,
        inner_actions,
        runtime,
        command_catalog,
    )
    print(f"[MAIN] Скажите '{runtime.assistant_name}' для активации")

    try:
        while runtime.state_program == "running":
            request = voice_adapter.get_command_request()

            result = dispatcher.dispatch(request)
            voice_adapter.complete_session(
                keep_active=result.keep_session_active
            )

            if result.keep_session_active:
                print("[MAIN] Ожидаю продолжение голосовой сессии")
            else:
                print(
                    f"[MAIN] Скажите '{runtime.assistant_name}' "
                    "для новой команды"
                )

    except KeyboardInterrupt:
        print("\n[MAIN] Получен Ctrl+C")
    except Exception as error:
        print(f"[ERROR] {type(error).__name__}: {error}")
        raise
    finally:
        runtime.state_program = "stopped"
        print("[MAIN] Программа завершена")

if __name__ == "__main__":
    main()
