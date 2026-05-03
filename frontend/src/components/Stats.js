import { useEffect, useState } from "react";
import API from "../api/api";

export default function Stats() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    API.get("/stats").then(res => setStats(res)).catch(() => {});
  }, []);

  if (!stats) return null;

  const items = [
    { label: "Catalysts",    value: stats.total_catalysts   ?? 0 },
    { label: "AI Candidates", value: stats.novel_candidates  ?? 0 },
    { label: "Experiments",  value: stats.total_experiments ?? 0 },
    { label: "Success Rate", value: stats.total_experiments
        ? `${Math.round((stats.successful_runs / stats.total_experiments) * 100)}%`
        : "—" },
    { label: "Failures",     value: stats.failed_runs       ?? 0 },
    { label: "Retrains",     value: stats.retrain_events    ?? 0 },
  ];

  return (
    <div className="stats-bar">
      {items.map(({ label, value }) => (
        <div className="stat-item" key={label}>
          <div className="stat-value">{value}</div>
          <div className="stat-label">{label}</div>
        </div>
      ))}
    </div>
  );
}
