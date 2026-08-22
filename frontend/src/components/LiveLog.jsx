import { useState, useEffect } from "react";

export default function LiveLog({ idea }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    if (!idea) return;
    setLogs([]);
    const source = new EventSource(
      `http://localhost:8000/generate/stream?idea=${encodeURIComponent(idea)}`
    );
    source.onmessage = (event) => {
      setLogs((prev) => [...prev, event.data]);
      if (event.data === "Done.") source.close();
    };
    source.onerror = () => source.close();
    return () => source.close();
  }, [idea]);

  if (!idea) return null;

  return (
      <div className="live-log">
      {logs.map((log, i) => (
        <div key={i}>{log}</div>
      ))}
    </div>
  );
}