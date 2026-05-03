import { useState } from "react";
import API from "../api/api";

export default function Feedback({ reaction: propReaction }) {
  const [form, setForm] = useState({
    catalyst_id     : "",
    formula         : "",
    reaction        : propReaction || "",
    actual_yield    : "",
    actual_activity : "",
    actual_stability: "",
    outcome         : "success",
    notes           : "",
    logged_by       : "researcher",
  });
  const [submitted, setSubmitted] = useState(false);
  const [loading,   setLoading]   = useState(false);

  const update = (field, val) => setForm(f => ({ ...f, [field]: val }));

  const submit = async () => {
    if (!form.catalyst_id || !form.formula || !form.reaction) {
      return alert("Please fill in Catalyst ID, Formula and Reaction");
    }
    setLoading(true);
    try {
      await API.post("/feedback", {
        ...form,
        actual_yield    : parseFloat(form.actual_yield)    || 0,
        actual_activity : parseFloat(form.actual_activity) || 0,
        actual_stability: parseFloat(form.actual_stability)|| 0,
      });
      setSubmitted(true);
    } catch {
      alert("Error submitting feedback — check backend");
    }
    setLoading(false);
  };

  if (submitted) return (
    <div className="page">
      <div style={{ textAlign: "center", padding: "6rem 2rem" }}>
        <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>✅</div>
        <h2 style={{ fontSize: "1.5rem", marginBottom: "0.5rem", color: "var(--accent-green)" }}>
          Feedback Logged!
        </h2>
        <p style={{ color: "var(--text-secondary)", marginBottom: "2rem" }}>
          Models have been retrained with your experimental results.
        </p>
        <button className="submit-btn" style={{ maxWidth: 240, margin: "0 auto" }}
          onClick={() => setSubmitted(false)}>
          Log Another Result
        </button>
      </div>
    </div>
  );

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-label">Feedback Loop</div>
        <h1 className="page-title">Log <span>Experiment Result</span></h1>
        <p className="page-desc">
          Feed real lab results back into Fail2Learn. The platform compares predictions
          against actuals and retrains its models to improve future accuracy.
        </p>
      </div>

      <div className="card">
        <div className="card-title">Experiment Details</div>
        <div className="feedback-grid">

          <div>
            <label className="field-label">Catalyst ID</label>
            <input className="field-input" placeholder="e.g. ai-gen-co2-to-1"
              value={form.catalyst_id}
              onChange={e => update("catalyst_id", e.target.value)} />
          </div>

          <div>
            <label className="field-label">Formula</label>
            <input className="field-input" placeholder="e.g. Cu-Zn-Ga/Al2O3"
              value={form.formula}
              onChange={e => update("formula", e.target.value)} />
          </div>

          <div className="full">
            <label className="field-label">Reaction</label>
            <input className="field-input" placeholder="e.g. co2 to methanol"
              value={form.reaction}
              onChange={e => update("reaction", e.target.value)} />
          </div>

          <div>
            <label className="field-label">Actual Yield (0–1)</label>
            <input className="field-input" type="number" min="0" max="1" step="0.01"
              placeholder="0.72"
              value={form.actual_yield}
              onChange={e => update("actual_yield", e.target.value)} />
          </div>

          <div>
            <label className="field-label">Actual Activity (0–1)</label>
            <input className="field-input" type="number" min="0" max="1" step="0.01"
              placeholder="0.68"
              value={form.actual_activity}
              onChange={e => update("actual_activity", e.target.value)} />
          </div>

          <div>
            <label className="field-label">Actual Stability (0–1)</label>
            <input className="field-input" type="number" min="0" max="1" step="0.01"
              placeholder="0.55"
              value={form.actual_stability}
              onChange={e => update("actual_stability", e.target.value)} />
          </div>

          <div>
            <label className="field-label">Outcome</label>
            <select className="field-select"style={{ background: "#071428", color: "var(--text-primary)" }}
              value={form.outcome}
              onChange={e => update("outcome", e.target.value)}>
              <option value="success">✅ Success</option>
              <option value="partial">⚠️ Partial</option>
              <option value="failure">❌ Failure</option>
            </select>
          </div>

          <div className="full">
            <label className="field-label">Notes (optional)</label>
            <textarea className="field-textarea"
              placeholder="e.g. sintering observed at high temperature..."
              value={form.notes}
              onChange={e => update("notes", e.target.value)} />
          </div>

          <div className="full">
            <button className="submit-btn" onClick={submit} disabled={loading}>
              {loading ? "Submitting & Retraining..." : "Submit Feedback →"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
