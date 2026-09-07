import { Code2, HardDrive, Mic, Monitor, Volume2 } from "lucide-react";

function Info() {
    return (
        <div className="flex w-full grow flex-col overflow-y-auto px-8 pb-8 pt-5">
            <div className="text-center">
                <h1 className="text-3xl font-bold text-white">WhiskyHub</h1>
                <p className="mt-2 text-sm text-gray-400">
                    Локальный голосовой ассистент для управления компьютером
                </p>
                <span className="mt-3 inline-block rounded-full bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-400">
                    pre-alpha v0.0.3
                </span>
            </div>

            <div className="mt-7 space-y-3">
                <InfoCard
                    Icon={Mic}
                    title="Локальное распознавание"
                    description="Речь распознаётся на устройстве с помощью Vosk и не отправляется в облако."
                />
                <InfoCard
                    Icon={Volume2}
                    title="Локальная озвучка"
                    description="Ответы генерируются локальной моделью Piper. Озвучку можно отключить."
                />
                <InfoCard
                    Icon={Monitor}
                    title="Управление Windows"
                    description="Ассистент открывает системные приложения, управляет звуком и выполняет голосовые команды."
                />
                <InfoCard
                    Icon={HardDrive}
                    title="Локальные данные"
                    description="Имя помощника и настройки хранятся только на компьютере пользователя."
                />
            </div>

            <div className="mt-7 rounded-2xl border border-gray-700 bg-gray-800/70 p-4 text-sm text-gray-400">
                <InfoRow label="Платформа" value="Windows" />
                <InfoRow label="Имя по умолчанию" value="Виски" />
                <InfoRow label="Статус" value="В разработке" accent />
            </div>

            <a
                href="https://github.com/silentiasm"
                target="_blank"
                rel="noopener noreferrer"
                className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-400 transition-colors hover:text-white"
            >
                <Code2 size={18} />
                GitHub проекта
            </a>
        </div>
    );
}

type InfoCardProps = {
    Icon: typeof Mic;
    title: string;
    description: string;
};

function InfoCard({ Icon, title, description }: InfoCardProps) {
    return (
        <div className="flex gap-4 rounded-2xl border border-gray-700 bg-gray-800 p-4">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-gray-700 text-green-400">
                <Icon size={21} aria-hidden="true" />
            </div>
            <div>
                <h2 className="font-semibold text-white">{title}</h2>
                <p className="mt-1 text-sm leading-5 text-gray-400">{description}</p>
            </div>
        </div>
    );
}

function InfoRow({ label, value, accent = false }: { label: string; value: string; accent?: boolean }) {
    return (
        <div className="flex justify-between border-b border-gray-700 py-2 last:border-0">
            <span>{label}</span>
            <span className={accent ? "font-medium text-amber-400" : "font-medium text-white"}>
                {value}
            </span>
        </div>
    );
}

export default Info;
