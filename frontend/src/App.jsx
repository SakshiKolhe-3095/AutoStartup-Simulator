import { useState } from "react";
import IdeaForm from "./components/IdeaForm";

function App() {
  const [result, setResult] = useState(null);

  const handleGenerate = async (idea) => {
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
      {result && <p>{result}</p>}
    </div>
  );
}

export default App;