import { ChatWindow } from "./components/ChatWindow";
import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="app__header">
        <h1>Swiss Wealth RAG Assistant</h1>
        <p>Grounded answers over indexed Swiss wealth management documents.</p>
      </header>

      <main>
        <ChatWindow />
      </main>
    </div>
  );
}

export default App;