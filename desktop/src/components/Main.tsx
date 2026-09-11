import { useState, type Dispatch, type SetStateAction } from "react";
import { invoke, isTauri } from "@tauri-apps/api/core";
import { Power } from "lucide-react";
import { useMicrophone } from "../contexts/MicrophoneContext";

type MainProps = {
    isEngineRunning: boolean;
    setIsEngineRunning: Dispatch<SetStateAction<boolean>>;
};

function Main({ isEngineRunning, setIsEngineRunning }: MainProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const {
        microphoneEnabled,
        microphoneAvailable,
        refreshMicrophone,
        markMicrophoneUnavailable,
    } = useMicrophone();

    async function toggleEngine() {
        if (isLoading) return;

        if (!isTauri()) {
            setError(
                "Запуск WhiskyHub Engine доступен только в окне Tauri. Запустите приложение командой pnpm tauri dev."
            );
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            if (isEngineRunning) {
                await invoke<boolean>("stop_engine");
                setIsEngineRunning(false);
                markMicrophoneUnavailable();
            } else {
                await invoke<boolean>("start_engine");
                setIsEngineRunning(true);
                await refreshMicrophone();
            }
        } catch (unknownError) {
            setError(String(unknownError));
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <div className="flex flex-col items-center mt-10 bg-gray-900 grow w-full">
            <div>
                <button
                    type="button"
                    onClick={toggleEngine}
                    disabled={isLoading}
                    className={`flex items-center border-3 rounded-[50%] p-20 transition-colors disabled:opacity-50 ${
                        isEngineRunning
                            ? "bg-green-950 border-green-500 text-green-400"
                            : "bg-gray-800 border-gray-600"
                    }`}
                >
                    <Power size={60} />
                </button>
            </div>
            <div className={`font-bold mt-10 ${isEngineRunning ? "text-green-500" : "text-gray-500"}`}>
                {isLoading ? "Подождите..." : isEngineRunning ? "Включено" : "Выключено"}
            </div>
            <div className="mt-4 flex items-center gap-2 text-sm text-gray-300">
                <span
                    className={`size-2.5 rounded-full ${
                        microphoneAvailable && microphoneEnabled
                            ? "bg-green-500"
                            : "bg-red-500"
                    }`}
                    aria-hidden="true"
                />
                <span>
                    Микрофон {microphoneAvailable && microphoneEnabled ? "включён" : "выключен"}
                </span>
            </div>
            {error && (
                <div className="text-red-400 text-center px-8 mt-4">{error}</div>
            )}
            {/*
            <div className="flex flex-col items-center mt-10">
                <div>Статус микрофона</div>
                <div>Статус камеры</div>
            </div>
            */}
            <div className="flex flex-col items-center text-gray-400 mt-10 mb-10">
                pre-alpha v0.0.4 by <a href="https://github.com/silentiasm" target="_blank" rel="noopener noreferrer">
                    silentias
                </a>
            </div>
        </div>
    )
}

export default Main;
