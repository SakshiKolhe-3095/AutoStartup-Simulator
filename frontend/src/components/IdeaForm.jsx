import { useState } from "react";

export default function IdeaForm({ onSubmit }) {
  const [idea, setIdea] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (idea.trim()) onSubmit(idea);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={idea}
        onChange={(e) => setIdea(e.target.value)}
        placeholder="e.g. AI-powered plant care app"
      />
      <button type="submit">Generate</button>
    </form>
  );
}