import { useState, memo } from "react";

function IdeaForm({ onSubmit, loading }) {
  const [idea, setIdea] = useState("");
  const handleSubmit = (e) => {
    e.preventDefault();
    if (idea.trim()) onSubmit(idea);
  };
  return (
    <form onSubmit={handleSubmit} className="idea-form">
      <input
        type="text"
        value={idea}
        onChange={(e) => setIdea(e.target.value)}
        placeholder="e.g. AI-powered plant care app"
        disabled={loading}
      />
      <button type="submit" disabled={loading}>
        {loading ? "Generating..." : "Generate"}
      </button>
    </form>
  );
}

export default memo(IdeaForm);