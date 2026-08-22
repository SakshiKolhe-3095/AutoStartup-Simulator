export default function InvestorScore({ score }) {
  if (score === undefined || score === null) return null;

  const pct = (score / 10) * 100;
  const color = score >= 7 ? "#4caf50" : score >= 4 ? "#ffb300" : "#e53935";

  return (
    <div style={{ margin: "1.5rem 0" }}>
      <h3>Investor Confidence Score</h3>
      <div
        style={{
          width: "100%",
          maxWidth: "400px",
          height: "24px",
          background: "#222",
          borderRadius: "12px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            height: "100%",
            background: color,
            transition: "width 0.6s ease",
          }}
        />
      </div>
      <p style={{ marginTop: "0.5rem", fontWeight: "bold", color }}>
        {score} / 10
      </p>
    </div>
  );
}