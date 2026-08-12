import { useState } from "react";
import IdeaForm from "./components/IdeaForm";

function App() {
  const [result, setResult] = useState(null);

  const handleGenerate = (idea) => {
    // TODO Wk2 Day2: wire to backend /generate stub
    setResult(`Received idea: ${idea}`);
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