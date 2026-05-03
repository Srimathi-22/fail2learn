import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import API from "../api/api";
import CandidateTable from "../components/CandidateTable";
import FailureAnalysis from "../components/FailureAnalysis";
import Stats from "../components/Stats";
import Loader from "../components/Loader";

export default function Candidates({ reaction: propReaction }) {
  const { state } = useLocation();
  const reaction = state?.reaction || propReaction;

  const [data,    setData]    = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!reaction) return;
    setLoading(true);
    API.get(`/candidates?reaction=${encodeURIComponent(reaction)}`)
      .then(res => setData(res.candidates || []))
      .catch(() => alert("Failed to fetch candidates"))
      .finally(() => setLoading(false));
  }, [reaction]);

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-label">Discovery Results</div>
        <h1 className="page-title">
          {reaction
            ? <><span>{reaction}</span> — Ranked Candidates</>
            : "Candidate Results"}
        </h1>
        <p className="page-desc">
          Known catalysts from scientific databases combined with AI-generated novel designs,
          ranked by predicted performance and failure risk.
        </p>
      </div>

      <Stats />

      {loading ? <Loader /> : (
        <>
          <div className="section">
            <div className="section-title">Ranked Candidates ({data.length})</div>
            <CandidateTable data={data} />
          </div>

          <div className="section">
            <div className="section-title">Failure Risk Analysis</div>
            <FailureAnalysis data={data} />
          </div>
        </>
      )}
    </div>
  );
}
