import { useState } from "react";
import IdeaForm from "./components/IdeaForm";
import LiveLog from "./components/LiveLog";

function App() {
  const [result, setResult] = useState(null);
  const [activeIdea, setActiveIdea] = useState(null);

  const handleGenerate = async (idea) => {
    setActiveIdea(idea); // triggers LiveLog to start streaming

    const res = await fetch("http://localhost:8000/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idea }),
    });
    const data = await res.json();
    setResult(JSON.stringify(data));
  };

  return (
    <div>
      <h1>AutoStartup Simulator</h1>
      <IdeaForm onSubmit={handleGenerate} />
      <LiveLog idea={activeIdea} />
      {result && <p>{result}</p>}
    </div>
  );
}

export default App;