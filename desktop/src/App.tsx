import { useState } from "react";
import "./App.css";
import Header, { type Tab } from "./components/Header";
import Commands from "./components/Commands";
import Info from "./components/Info";
import Main from "./components/Main";
import Settings from "./components/Settings";
import SmartHome from "./components/SmartHome";
import { MicrophoneProvider } from "./contexts/MicrophoneContext";

function App() {
  const [activeTab, setActiveTab] = useState<Tab>("main");
  const [isEngineRunning, setIsEngineRunning] = useState(false);

  return (
    <MicrophoneProvider
      engineRunning={isEngineRunning}
      onEngineUnavailable={() => setIsEngineRunning(false)}
    >
      <div className="bg-gray-900 text-white h-[100vh] w-[100vw] flex flex-col items-center">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === "commands" && <Commands />}
      {activeTab === "smart-home" && <SmartHome />}
      {activeTab === "main" && (
        <Main
          isEngineRunning={isEngineRunning}
          setIsEngineRunning={setIsEngineRunning}
        />
      )}
      {activeTab === "settings" && <Settings />}
      {activeTab === "info" && <Info />}
      </div>
    </MicrophoneProvider>
  );
}

export default App;
