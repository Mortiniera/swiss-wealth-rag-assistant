import { ChatWindow } from "./components/ChatWindow";
import { DeploymentBanner } from "./components/DeploymentBanner";
import { Footer } from "./components/Footer";
import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="app__header">
        <p className="app__eyebrow">Swiss Wealth Intelligence</p>
        <h1>Swiss Wealth Intelligence Assistant</h1>
        <p className="app__subtitle">
          RAG assistant for Swiss private banking, wealth management, sustainable investing and
          family governance documents.
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
