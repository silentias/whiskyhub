import { useEffect, useRef, useState } from "react";
import { ChevronDown, Terminal } from "lucide-react";

const LOGS_URL = "http://127.0.0.1:8765/api/logs?limit=200";

function LogViewer() {
    const [isOpen, setIsOpen] = useState(false);
    const [logs, setLogs] = useState<string[]>([]);
    const [error, setError] = useState<string | null>(null);
    const consoleRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!isOpen) return;

        let active = true;
        const loadLogs = async () => {
            try {
                const response = await fetch(LOGS_URL);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const data = (await response.json()) as { logs?: unknown };
                if (!Array.isArray(data.logs) || !data.logs.every((line) => typeof line === "string")) {
                    throw new Error("Некорректный ответ WhiskyHub Engine");
                }
                if (active) {
                    setLogs(data.logs);
                    setError(null);
                }
            } catch {
                if (active) setError("WhiskyHub Engine недоступен");
            }
        };

        void loadLogs();
        const interval = window.setInterval(() => void loadLogs(), 1000);
        return () => {
            active = false;
            window.clearInterval(interval);
        };
    }, [isOpen]);

    useEffect(() => {
        if (isOpen && consoleRef.current) {
            consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
        }
    }, [isOpen, logs]);

    return (
        <div className="mt-6 overflow-hidden rounded-2xl border border-gray-700 bg-gray-800">
            <button
                type="button"
                aria-expanded={isOpen}
                onClick={() => setIsOpen((open) => !open)}
                className="flex w-full items-center gap-3 p-4 text-left transition-colors hover:bg-gray-700/50"
            >
                <Terminal className="text-green-400" size={21} aria-hidden="true" />
                <span className="grow font-semibold">Журнал работы</span>
                <ChevronDown
                    size={20}
                    className={`text-gray-400 transition-transform ${isOpen ? "rotate-180" : ""}`}
                    aria-hidden="true"
                />
            </button>

            {isOpen && (
                <div className="border-t border-gray-700 bg-black p-3">
                    <div
                        ref={consoleRef}
                        className="h-56 overflow-y-auto whitespace-pre-wrap break-words font-mono text-[11px] leading-5 text-gray-300"
                    >
                        {logs.length > 0
                            ? logs.map((line, index) => (
                                  <div
                                      key={`${index}-${line}`}
                                      className={line.includes(" ERROR ") ? "text-red-400" : line.includes(" WARNING ") ? "text-yellow-400" : ""}
                                  >
                                      {line}
                                  </div>
                              ))
                            : !error && <div className="text-gray-600">Журнал пока пуст</div>}
                        {error && <div className="text-red-400">{error}</div>}
                    </div>
                </div>
            )}
        </div>
    );
}

export default LogViewer;
