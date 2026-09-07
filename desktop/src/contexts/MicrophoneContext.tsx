import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useRef,
    useState,
    type ReactNode,
} from "react";

const ENGINE_URL = "http://127.0.0.1:8765";

type MicrophoneContextValue = {
    microphoneEnabled: boolean;
    microphoneAvailable: boolean;
    microphoneLoading: boolean;
    microphoneError: string | null;
    refreshMicrophone: () => Promise<boolean>;
    setMicrophoneEnabled: (enabled: boolean) => Promise<void>;
    markMicrophoneUnavailable: () => void;
};

const MicrophoneContext = createContext<MicrophoneContextValue | null>(null);

export function MicrophoneProvider({
    children,
    engineRunning,
    onEngineUnavailable,
}: {
    children: ReactNode;
    engineRunning: boolean;
    onEngineUnavailable: () => void;
}) {
    const [microphoneEnabled, setEnabled] = useState(false);
    const [microphoneAvailable, setAvailable] = useState(false);
    const [microphoneLoading, setLoading] = useState(false);
    const [microphoneError, setError] = useState<string | null>(null);
    const requestGeneration = useRef(0);
    const consecutiveFailures = useRef(0);

    const refreshMicrophone = useCallback(async () => {
        const generation = requestGeneration.current;
        try {
            const response = await fetch(`${ENGINE_URL}/api/microphone`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = (await response.json()) as { enabled?: unknown };
            if (typeof data.enabled !== "boolean") {
                throw new Error("Некорректный ответ WhiskyHub Engine");
            }
            if (generation !== requestGeneration.current) return false;

            setEnabled(data.enabled);
            setAvailable(true);
            setError(null);
            consecutiveFailures.current = 0;
            return true;
        } catch {
            if (generation !== requestGeneration.current) return false;
            consecutiveFailures.current += 1;
            if (consecutiveFailures.current >= 3) {
                setAvailable(false);
                setEnabled(false);
                onEngineUnavailable();
            }
            return false;
        }
    }, [onEngineUnavailable]);

    const setMicrophoneEnabled = useCallback(
        async (enabled: boolean) => {
            if (microphoneLoading) return;
            setLoading(true);
            setError(null);

            try {
                const response = await fetch(`${ENGINE_URL}/api/microphone`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ enabled }),
                });
                if (!response.ok) {
                    const data = (await response.json().catch(() => null)) as
                        | { error?: string; message?: string }
                        | null;
                    throw new Error(data?.error ?? data?.message ?? `HTTP ${response.status}`);
                }

                if (!(await refreshMicrophone())) {
                    throw new Error("Не удалось получить состояние микрофона");
                }
            } catch (error) {
                setError(
                    error instanceof Error
                        ? error.message
                        : "Не удалось связаться с WhiskyHub Engine",
                );
                setAvailable(false);
                setEnabled(false);
            } finally {
                setLoading(false);
            }
        },
        [microphoneLoading, refreshMicrophone],
    );

    const markMicrophoneUnavailable = useCallback(() => {
        requestGeneration.current += 1;
        consecutiveFailures.current = 0;
        setEnabled(false);
        setAvailable(false);
        setError(null);
    }, []);

    useEffect(() => {
        if (!engineRunning) {
            markMicrophoneUnavailable();
            return;
        }

        void refreshMicrophone();
        const interval = window.setInterval(() => void refreshMicrophone(), 2000);
        return () => window.clearInterval(interval);
    }, [engineRunning, markMicrophoneUnavailable, refreshMicrophone]);

    const value = useMemo(
        () => ({
            microphoneEnabled,
            microphoneAvailable,
            microphoneLoading,
            microphoneError,
            refreshMicrophone,
            setMicrophoneEnabled,
            markMicrophoneUnavailable,
        }),
        [
            microphoneEnabled,
            microphoneAvailable,
            microphoneLoading,
            microphoneError,
            refreshMicrophone,
            setMicrophoneEnabled,
            markMicrophoneUnavailable,
        ],
    );

    return (
        <MicrophoneContext.Provider value={value}>
            {children}
        </MicrophoneContext.Provider>
    );
}

export function useMicrophone() {
    const context = useContext(MicrophoneContext);
    if (context === null) {
        throw new Error("useMicrophone должен использоваться внутри MicrophoneProvider");
    }
    return context;
}
