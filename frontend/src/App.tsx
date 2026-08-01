import { ChatWindow } from "./components/ChatWindow";
import { DeploymentBanner } from "./components/DeploymentBanner";
import { Footer } from "./components/Footer";
import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="app__header">
        <p className="app__eyebrow">Helvetia Private Bank</p>
        <h1>Helvetia Operations Assistant</h1>
        <p className="app__subtitle">
          Internal policy Q&amp;A for Helvetia Private Bank : KYC, AML, transfers, restrictions,
          complaints and related procedures, with grounded sources.
        </p>
      </header>

      <main>
        <ChatWindow />
      </main>

      <DeploymentBanner />

      <Footer />
    </div>
  );
}

export default App;
