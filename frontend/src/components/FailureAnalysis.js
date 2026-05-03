export default function FailureAnalysis({ data }) {
  const safeData = Array.isArray(data) ? data : [];
  const risky = safeData.filter(c => (c.failure_risk ?? 0) > 0.2);

  if (risky.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">✅</div>
        <p>No high-risk candidates detected.</p>
      </div>
    );
  }

  const getRec = (reason) => {
    if (!reason) return "Further investigation recommended.";
    if (reason.includes("sinter"))   return "Use high surface area supports (SBA-15, Al₂O₃) to prevent particle agglomeration.";
    if (reason.includes("poison"))   return "Pre-treat feed gas to remove sulphur/halide impurities before reaction.";
    if (reason.includes("oxidat"))   return "Consider reducing atmosphere or protective coating to prevent oxidation.";
    if (reason.includes("leach"))    return "Use stronger metal-support interactions or encapsulation techniques.";
    if (reason.includes("coke"))     return "Add steam or CO₂ to reaction feed; consider periodic regeneration cycles.";
    if (reason.includes("activat"))  return "Apply pre-reduction treatment at moderate temperature before use.";
    return "Monitor reaction conditions carefully and consider structural modifications.";
  };

  return (
    <div className="failure-grid">
      {risky.map((c, i) => (
        <div className="failure-card" key={i}>
          <div className="failure-formula">{c.formula}</div>
          <div className="failure-reason">
            ⚠ {c.failure_reason || "Unknown failure mode"}
          </div>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            marginBottom: 10,
          }}>
            <div style={{
              flex: 1,
              height: 4,
              background: "rgba(255,255,255,0.06)",
              borderRadius: 2,
              overflow: "hidden",
            }}>
              <div style={{
                width: `${Math.round((c.failure_risk ?? 0) * 100)}%`,
                height: "100%",
                background: "linear-gradient(90deg, #ffaa00, #ff4466)",
                borderRadius: 2,
              }} />
            </div>
            <span style={{
              fontFamily: "var(--font-mono)",
              fontSize: 11,
              color: "var(--accent-red)",
            }}>
              {((c.failure_risk ?? 0) * 100).toFixed(0)}% risk
            </span>
          </div>
          <div className="failure-rec">{getRec(c.failure_reason)}</div>
        </div>
      ))}
    </div>
  );
}
