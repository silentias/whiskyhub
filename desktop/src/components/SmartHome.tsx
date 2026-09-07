import { Construction, HouseWifi } from "lucide-react";

function SmartHome() {
    return (
        <div className="flex w-full grow flex-col items-center justify-center px-8 pb-20 text-center">
            <div className="relative flex size-28 items-center justify-center rounded-[2rem] border border-gray-700 bg-gray-800 text-green-400 shadow-lg">
                <HouseWifi size={48} strokeWidth={1.8} />
                <div className="absolute -bottom-2 -right-2 flex size-10 items-center justify-center rounded-full border-4 border-gray-900 bg-amber-500 text-gray-950">
                    <Construction size={20} />
                </div>
            </div>
            <h1 className="mt-8 text-2xl font-bold">Умный дом</h1>
            <p className="mt-3 max-w-sm text-sm leading-6 text-gray-400">
                Управление устройствами и сценариями умного дома появится в следующих версиях WhiskyHub.
            </p>
            <span className="mt-5 rounded-full bg-amber-500/10 px-4 py-1.5 text-xs font-semibold text-amber-400">
                В разработке
            </span>
        </div>
    );
}

export default SmartHome;
