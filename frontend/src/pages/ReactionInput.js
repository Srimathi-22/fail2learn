import { useState } from "react";
import API from "../api/api";
import { useNavigate } from "react-router-dom";

const PRESETS = [
  "CO2 to methanol",
  "syngas to ethanol",
  "ethanol to jet fuel",
  "cellulose to hydrocarbons",
  "biomass to fuels",
  "CO2 to ethanol",
  "methane to hydrogen",
  "glucose to ethanol",
  "lignin to aromatics",
  "glycerol to propanol",
];

export default function ReactionInput({ setReaction }) {
  const [reaction, setLocalReaction] = useState("");
  const [loading, setLoading]         = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (!reaction.trim()) return alert("Please enter a target reaction");
    setLoading(true);
    try {
      await API.post("/reaction", { reaction });
      setReaction(reaction);
      navigate("/candidates", { state: { reaction } });
    } catch {
      alert("Error running pipeline — is the backend running?");
    }
    setLoading(false);
  };

  return (
    <div className="reaction-hero">
      <div className="reaction-card">
       

        <h1 className="reaction-title">
          Discover Better !<br />
          <span>Catalysts Faster ~ </span>
        </h1>
        <p className="reaction-subtitle">
          Enter a target reaction. Fail2Learn retrieves known catalysts,
          generates novel AI designs, and learns from every failure.
        </p>

        <div className="reaction-presets">
          {PRESETS.map(p => (
            <button
              key={p}
              className="preset-btn"
              onClick={() => setLocalReaction(p)}
            >
              {p}
            </button>
          ))}
        </div>

        <div className="input-group">
          <label className="input-label">Target Reaction</label>
          <input
            className="reaction-input"
            value={reaction}
            onChange={e => setLocalReaction(e.target.value)}
            placeholder="e.g. CO2 to methanol"
            onKeyDown={e => e.key === "Enter" && handleSubmit()}
          />
        </div>

        <button
          className="submit-btn"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Checking..." : "Check the discovery →"}
        </button>
      </div>
    </div>
  );
}
