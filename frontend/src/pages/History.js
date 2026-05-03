import { useEffect, useState } from "react";
import API from "../api/api";

export default function History({ reaction }) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!reaction) return;
    setLoading(true);
    API.get(`/history?reaction=${encodeURIComponent(reaction)}`)
      .then(res => setData(res))
      .catch(() => alert("Failed to fetch history"))
      .finally(() => setLoading(false));
  }, [reaction]);

  if (!reaction) return (
    <div className="page">
      <div className="empty-state">
        <div className="empty-state-icon">🔍</div>
        <p>Search a reaction first to view its history.</p>
      </div>
    </div>
  );

  if (loading) return (
    <div className="page">
      <div className="loader-wrap">
        <div className="loader-ring" />
        <span className="loader-text">LOADING HISTORY...</span>
      </div>
    </div>
  );

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-label">Experiment Log</div>
        <h1 className="page-title">
          History — <span>{reaction}</span>
        </h1>
        <p className="page-desc">
          Full audit trail of experiments, predictions, and model retraining events.
        </p>
      </div>

      {/* Summary cards */}
      <div className="stats-bar" style={{ marginBottom: "2rem" }}>
        <div className="stat-item">
          <div className="stat-value">{data?.total_runs ?? 0}</div>
          <div className="stat-label">Total Runs</div>
        </div>
        <div className="stat-item">
          <div className="stat-value" style={{ color: "var(--accent-green)" }}>
            {data?.experiments?.filter(e => e.outcome === "success").length ?? 0}
          </div>
          <div className="stat-label">Successes</div>
        </div>
        <div className="stat-item">
          <div className="stat-value" style={{ color: "var(--accent-red)" }}>
            {data?.experiments?.filter(e => e.outcome === "failure").length ?? 0}
          </div>
          <div className="stat-label">Failures</div>
        </div>
        <div className="stat-item">
          <div className="stat-value" style={{ color: "var(--accent-amber)" }}>
            {data?.retrain_log?.length ?? 0}
          </div>
          <div className="stat-label">Retrains</div>
        </div>
      </div>

      {/* Experiments table */}
      <div className="section">
        <div className="section-title">Experiments</div>
        {!data?.experiments?.length ? (
          <div className="empty-state">
            <div className="empty-state-icon">🧪</div>
            <p>No experiments logged yet.<br />Submit feedback after lab testing.</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Formula</th>
                  <th>Outcome</th>
                  <th>Yield</th>
                  <th>Activity</th>
                  <th>Stability</th>
                  <th>Notes</th>
                  <th>Logged At</th>
                </tr>
              </thead>
              <tbody>
                {data.experiments.map((exp, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text-primary)", fontWeight: 700 }}>
                      {exp.formula}
                    </td>
                    <td>
                      <span className={`outcome-pill ${exp.outcome}`}>
                        {exp.outcome === "success" ? "✅ " : exp.outcome === "failure" ? "❌ " : "⚠️ "}
                        {exp.outcome}
                      </span>
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>
                      {((exp.actual_yield ?? 0) * 100).toFixed(0)}%
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>
                      {((exp.actual_activity ?? 0) * 100).toFixed(0)}%
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>
                      {((exp.actual_stability ?? 0) * 100).toFixed(0)}%
                    </td>
                    <td style={{ fontSize: 12, color: "var(--text-muted)", maxWidth: 200 }}>
                      {exp.notes || "—"}
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-muted)", whiteSpace: "nowrap" }}>
                      {exp.logged_at?.slice(0, 16).replace("T", " ")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Retrain log */}
      <div className="section">
        <div className="section-title">Model Retrain Log</div>
        {!data?.retrain_log?.length ? (
          <div className="empty-state" style={{ padding: "2rem" }}>
            <p>No retraining events yet.</p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {data.retrain_log.map((log, i) => (
              <div key={i} className="card" style={{ padding: "1rem 1.25rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--accent-cyan)" }}>
                    Retrain #{i + 1}
                  </span>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-muted)" }}>
                    {log.retrained_at?.slice(0, 16).replace("T", " ")}
                  </span>
                </div>
                <div style={{ marginTop: 8, fontSize: 12, color: "var(--text-secondary)" }}>
                  Activity bias: <span style={{ color: "var(--accent-amber)" }}>{log.factors?.activity_bias ?? "—"}</span>
                  {" · "}
                  Stability bias: <span style={{ color: "var(--accent-amber)" }}>{log.factors?.stability_bias ?? "—"}</span>
                  {" · "}
                  Success rate: <span style={{ color: "var(--accent-green)" }}>
                    {log.factors?.success_rate !== undefined
                      ? `${(log.factors.success_rate * 100).toFixed(0)}%`
                      : "—"}
                  </span>
                  {" · "}
                  Samples: <span style={{ color: "var(--text-primary)" }}>{log.factors?.training_sample_size ?? "—"}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
