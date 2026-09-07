import { Mic } from "lucide-react";
import { useMicrophone } from "../contexts/MicrophoneContext";

function Settings() {
    const {
        microphoneEnabled,
        microphoneAvailable,
        microphoneLoading,
        microphoneError,
        setMicrophoneEnabled,
    } = useMicrophone();
    const isMicrophoneOn = microphoneAvailable && microphoneEnabled;

    return (
        <div className="flex w-full grow flex-col px-8 pb-8 pt-8">
            <h1 className="text-3xl font-bold">Настройки</h1>
            <p className="mt-2 text-sm text-gray-400">
                Настройте работу голосового ассистента
            </p>

            <div className="mt-8 overflow-hidden rounded-2xl border border-gray-700 bg-gray-800">
                <div className="flex items-center gap-4 p-4">
                    <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-green-500 text-white">
                        <Mic size={23} aria-hidden="true" />
                    </div>
                    <div className="min-w-0 grow">
                        <div className="font-semibold">Микрофон</div>
                        <div className="mt-0.5 text-sm text-gray-400">
                            {isMicrophoneOn ? "Включён" : "Выключен"}
                        </div>
                    </div>
                    <button
                        type="button"
                        role="switch"
                        aria-checked={isMicrophoneOn}
                        aria-label="Включить или выключить микрофон"
                        disabled={!microphoneAvailable || microphoneLoading}
                        onClick={() => void setMicrophoneEnabled(!microphoneEnabled)}
                        className={`relative h-7 w-12 shrink-0 rounded-full transition-colors duration-200 ${
                            isMicrophoneOn ? "bg-green-500" : "bg-gray-600"
                        } disabled:cursor-not-allowed disabled:opacity-50`}
                    >
                        <span
                            className={`absolute left-1 top-1 size-5 rounded-full bg-white shadow-md transition-transform duration-200 ${
                                isMicrophoneOn ? "translate-x-5" : "translate-x-0"
                            }`}
                        />
                    </button>
                </div>
            </div>

            {!microphoneAvailable && (
                <p className="mt-4 px-1 text-xs leading-5 text-gray-500">
                    Запустите WhiskyHub Engine, чтобы управлять микрофоном.
                </p>
            )}
            {microphoneError && (
                <p className="mt-2 px-1 text-xs text-red-400">{microphoneError}</p>
            )}
        </div>
    );
}

export default Settings;
