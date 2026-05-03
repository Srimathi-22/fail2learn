export default function CandidateTable({ data }) {
  const safeData = Array.isArray(data) ? data : [];

  if (safeData.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🔬</div>
        <p>No candidates found.<br />Run a reaction pipeline to see results.</p>
      </div>
    );
  }

  const bar = (val, risk = false) => (
    <div className="score-bar">
      <div className="score-track">
        <div
          className={`score-fill${risk ? " risk" : ""}`}
          style={{ width: `${Math.round((val ?? 0) * 100)}%` }}
        />
      </div>
      <span className="score-num">{((val ?? 0) * 100).toFixed(0)}%</span>
    </div>
  );

  return (
    <div className="table-wrapper">
      <table className="candidate-table">
        <thead>
          <tr>
            <th>RANK</th>
            <th>Formula</th>
            <th>Activity</th>
            <th>Selectivity</th>
            <th>Stability</th>
            <th>Failure Risk</th>
            <th>Score</th>
            <th>Rationale</th>
          </tr>
        </thead>
        <tbody>
          {safeData.map((c, i) => (
            <tr key={c.id ?? i}>
              <td>
                <span className={`rank-badge${i < 3 ? " top" : ""}`}>
                  {c.rank ?? i + 1}
                </span>
              </td>
              <td>
                <span className="formula-cell">{c.formula}</span>
              </td>
              
              <td>{bar(c.predicted_activity)}</td>
              <td>{bar(c.predicted_selectivity)}</td>
              <td>{bar(c.predicted_stability)}</td>
              <td>{bar(c.failure_risk, true)}</td>
              <td>
                <span style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "13px",
                  color: "var(--accent-cyan)",
                  fontWeight: 700,
                }}>
                  {((c.final_score ?? 0) * 100).toFixed(1)}
                </span>
              </td>
              <td style={{ maxWidth: 220, fontSize: 12, color: "var(--text-muted)", lineHeight: 1.5 }}>
                {c.rationale}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
