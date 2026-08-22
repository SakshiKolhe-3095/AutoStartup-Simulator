export default function ResultsDisplay({ result }) {
  if (!result) return null;

  const {
    deck_url,
    landing_page_url,
    investor_transcript = [],
  } = result;

  return (
    <div style={{ padding: "1rem", marginTop: "1rem" }}>
      <h2>Results</h2>

      <div style={{ marginBottom: "1rem" }}>
        {deck_url ? (
          <a href={deck_url} target="_blank" rel="noreferrer">
            Download Pitch Deck
          </a>
        ) : (
          <p>Pitch deck not yet available.</p>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        {landing_page_url ? (
          <a href={landing_page_url} target="_blank" rel="noreferrer">
            View Landing Page
          </a>
        ) : (
          <p>Landing page not yet available.</p>
        )}
      </div>

      <div>
        <h3>Investor Q&A</h3>
        {investor_transcript.length === 0 && <p>No transcript yet.</p>}
        {investor_transcript.map((entry, i) => (
          <div key={i} style={{ marginBottom: "0.75rem" }}>
            <p><strong>Q:</strong> {entry.q}</p>
            <p><strong>A:</strong> {entry.a}</p>
            {entry.rebuttal && (
              <>
                <p><em>Investor pushback:</em> {entry.rebuttal}</p>
                <p><em>CEO defense:</em> {entry.defense}</p>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}