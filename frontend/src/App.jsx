import { useState } from "react";
import IdeaForm from "./components/IdeaForm";
import LiveLog from "./components/LiveLog";
import ResultsDisplay from "./components/ResultsDisplay";
import "./App.css";

function App() {
  const [result, setResult] = useState(null);
  const [activeIdea, setActiveIdea] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (idea) => {
    setActiveIdea(idea);
    setResult(null);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idea }),
      });
      const data = await res.json();
      setResult(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <h1>AutoStartup Simulator</h1>
      <IdeaForm onSubmit={handleGenerate} loading={loading} />
      <LiveLog idea={activeIdea} />
      <ResultsDisplay result={result} />
    </div>
  );
}

export default App;