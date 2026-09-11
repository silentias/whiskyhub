import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

const COMMANDS_URL = "http://127.0.0.1:8765/api/commands";

type Command = {
    id: number;
    slug: string;
    voice_phrases: string[];
    voice_patterns: string[];
    requires_confirmation: boolean;
};

function Commands() {
    const [commands, setCommands] = useState<Command[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadCommands = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(COMMANDS_URL);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = (await response.json()) as { commands?: unknown };
            if (!Array.isArray(data.commands)) {
                throw new Error("Некорректный ответ WhiskyHub Engine");
            }
            setCommands(data.commands as Command[]);
        } catch {
            setCommands([]);
            setError("Запустите WhiskyHub Engine, чтобы получить список команд.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        void loadCommands();
    }, [loadCommands]);

    return (
        <div className="flex w-full grow flex-col overflow-y-auto px-8 pb-8 pt-6">
            <div className="flex items-start justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold">Команды</h1>
                    <p className="mt-2 text-sm text-gray-400">
                        Доступно: {commands.length}
                    </p>
                </div>
                <button
                    type="button"
                    onClick={() => void loadCommands()}
                    disabled={loading}
                    aria-label="Обновить команды"
                    className="rounded-xl bg-gray-800 p-3 text-gray-300 transition-colors hover:bg-gray-700 disabled:opacity-50"
                >
                    <RefreshCw size={19} className={loading ? "animate-spin" : ""} />
                </button>
            </div>

            {error && (
                <div className="mt-6 rounded-2xl border border-red-900/60 bg-red-950/30 p-4 text-sm text-red-300">
                    {error}
                </div>
            )}

            <div className="mt-6 space-y-3">
                {commands.map((command) => (
                    <article
                        key={command.id}
                        className="rounded-2xl border border-gray-700 bg-gray-800 p-4"
                    >
                        <div className="flex items-center justify-between gap-3">
                            <code className="text-sm font-semibold text-green-400">
                                {command.slug}
                            </code>
                            {command.requires_confirmation && (
                                <span className="flex items-center gap-1 text-xs text-amber-400">
                                    <AlertTriangle size={14} />
                                    Нужно подтверждение
                                </span>
                            )}
                        </div>

                        {command.voice_phrases.length > 0 ? (
                            <div className="mt-3 flex flex-wrap gap-2">
                                {command.voice_phrases.map((phrase) => (
                                    <span
                                        key={phrase}
                                        className="rounded-lg bg-gray-700 px-2.5 py-1 text-xs text-gray-200"
                                    >
                                        «{phrase}»
                                    </span>
                                ))}
                            </div>
                        ) : (
                            <p className="mt-3 text-xs text-gray-500">
                                {command.voice_patterns.length > 0
                                    ? "Команда принимает аргументы"
                                    : "Доступна через API"}
                            </p>
                        )}
                    </article>
                ))}
            </div>
        </div>
    );
}

export default Commands;
