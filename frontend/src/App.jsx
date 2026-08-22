import { useState } from "react";
import IdeaForm from "./components/IdeaForm";
import LiveLog from "./components/LiveLog";
import ResultsDisplay from "./components/ResultsDisplay";

function App() {
  const [result, setResult] = useState(null);
  const [activeIdea, setActiveIdea] = useState(null);

  const handleGenerate = async (idea) => {
    setActiveIdea(idea);
    setResult(null);

    const res = await fetch("http://localhost:8000/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idea }),
    });
    const data = await res.json();
    setResult(data);
  };

  return (
    <div>
      <h1>AutoStartup Simulator</h1>
      <IdeaForm onSubmit={handleGenerate} />
      <LiveLog idea={activeIdea} />
      <ResultsDisplay result={result} />
    </div>
  );
}

export default App;