import { House, HouseWifi, Info, ListChecks, Settings } from "lucide-react";

export type Tab = "commands" | "smart-home" | "main" | "settings" | "info";

type HeaderProps = {
    activeTab: Tab;
    onTabChange: (tab: Tab) => void;
};

const buttons = [
    { id: "commands", label: "Команды", Icon: ListChecks },
    { id: "smart-home", label: "Умный дом", Icon: HouseWifi },
    { id: "main", label: "Главная", Icon: House },
    { id: "settings", label: "Настройки", Icon: Settings },
    { id: "info", label: "Информация", Icon: Info },
] satisfies { id: Tab; label: string; Icon: typeof House }[];

function Header({ activeTab, onTabChange }: HeaderProps) {
    const activeIndex = buttons.findIndex(({ id }) => id === activeTab);

    return (
        <div className="w-full px-4 pt-4">
            <header className="relative flex w-full items-center overflow-hidden rounded-3xl bg-gray-800 p-1 text-white shadow-md">
                <div
                    aria-hidden="true"
                    className="absolute inset-y-1 left-1 w-[calc((100%-0.5rem)/5)] rounded-[1.25rem] bg-gray-700 shadow-sm transition-transform duration-300 ease-out"
                    style={{ transform: `translateX(${activeIndex * 100}%)` }}
                />

                {buttons.map(({ id, label, Icon }) => (
                    <button
                        key={id}
                        type="button"
                        className="relative z-10 flex w-1/5 items-center justify-center rounded-3xl p-4 transition-colors duration-300"
                        aria-label={label}
                        aria-pressed={activeTab === id}
                        onClick={() => onTabChange(id)}
                    >
                        <Icon aria-hidden="true" size={24} strokeWidth={2.25} />
                    </button>
                ))}
            </header>
        </div>
    );
}

export default Header;
