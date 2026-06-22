import { ChatWindow } from "./components/ChatWindow";
import { DeploymentBanner } from "./components/DeploymentBanner";
import { Footer } from "./components/Footer";
import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="app__header">
        <h1>Swiss Wealth RAG Assistant</h1>
        <p>Grounded answers over indexed Swiss wealth management documents.</p>
      </header>

      <DeploymentBanner />

      <main>
        <ChatWindow />
      </main>

      <Footer />
    </div>
  );
}

export default App;