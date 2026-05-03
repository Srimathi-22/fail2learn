# Fail2Learn: A Failure-Driven AI Platform for Catalyst and Synthetic Biology Discovery

**Hackathon:** AI for Bharat  
**Theme:** Theme 4 — AI Platform for Molecular Discovery in Chemical Catalysis and Synthetic Biology  
**Team:** Flamboyant  
**Submission Date:** May 2026

---

## 1. Understanding the Problem

Catalyst and enzyme discovery is one of the most resource-intensive processes in modern chemistry. A single screening campaign for a viable catalyst — say, for converting CO₂ to methanol — can consume months of bench time, significant reagents, and expert researcher hours, with no guarantee of a successful outcome.

The core inefficiency is not just the time taken per experiment, but the fact that **failed experiments are treated as dead ends rather than data**. When a catalyst underperforms, the insight — which structural features caused the failure, what conditions led to deactivation, which combinations showed unexpected side reactions — is rarely captured in a structured, reusable form. It lives in a lab notebook or a researcher's memory and is lost to the next iteration.

This platform addresses that gap directly. By treating failures as first-class data, Fail2Learn builds a continuously improving knowledge base that accelerates future discovery cycles.

---

## 2. Our Approach

### End-to-End Workflow

The platform follows a complete discovery workflow:

1. **Researcher inputs a target reaction** (e.g., CO₂ + green H₂ → methanol)
2. **Known catalysts are retrieved** from Materials Project and BRENDA databases
3. **Generative AI proposes novel candidates** — structural variants and entirely new designs
4. **Predictive models rank all candidates** by activity, selectivity, and stability
5. **Failure risk is estimated** for each candidate before lab testing
6. **Results are visualised** in an interactive dashboard
7. **Experimental outcomes are logged back** — successes and failures alike
8. **Models retrain** using the new data, improving future predictions

### Two Directions Covered

**Direction 1 — Chemical Catalysis:**  
The platform supports reactions including CO₂ to methanol, syngas to ethanol, and ethanol to jet fuel. Candidates are retrieved from Materials Project (structure-activity data) and ranked using composite scoring across activity, selectivity, and stability metrics.

**Direction 2 — Synthetic Biology:**  
Enzyme candidates are retrieved from BRENDA using EC number mappings. The generative module proposes novel enzyme mutations and pathway modifications. Failure patterns such as catalyst poisoning, sintering, and low stability are detected and annotated.

---

## 3. System Architecture

### Data Layer
- **Materials Project API** — crystal structures, formation energies, stability data
- **BRENDA** — enzyme kinetics, EC number mappings, organism data
- **SQLite database** — local storage for catalysts, candidates, predictions, experiments, failure patterns, retrain logs, and annotations
- **Fallback synthetic data** — ensures the platform works without real API keys, as required by hackathon rules

### AI / ML Layer
- **Generative module** — Claude API (Anthropic) generates novel catalyst and enzyme designs based on known candidates and reaction context
- **Prediction module** — composite scoring model weighing activity (40%), selectivity (35%), and stability (25%), with failure risk penalty
- **Failure analysis engine** — detects patterns across failed experiments (low activity, sintering, poisoning, low stability)
- **Retraining pipeline** — computes correction factors from predicted vs actual outcomes and applies bias adjustments to future predictions

### Backend Layer
- **FastAPI** — REST API serving all ML modules
- **Endpoints:** `/api/reaction`, `/api/candidates`, `/api/feedback`, `/api/history`, `/api/stats`
- **Uvicorn** — ASGI server for async request handling

### Frontend Layer
- **React** — interactive dashboard
- **Recharts** — performance plots, scoring charts
- **Views:** reaction input, ranked candidate table, failure analysis panel, feedback form, experiment history log

---

## 4. Data Feedback Loops

This is the core innovation of Fail2Learn.

**How researchers log outcomes:**  
After conducting experiments, researchers submit results via the `/api/feedback` endpoint or the dashboard feedback form. They provide actual yield, activity, and stability measurements, along with outcome classification (success / partial / failure) and free-text notes.

**How models retrain:**  
The retraining pipeline compares predicted vs actual values for each catalyst. It computes activity and stability bias factors — the average gap between what the model predicted and what actually happened. These correction factors are applied to all future predictions for that reaction. Every retraining event is logged with full attribution in the `retrain_log` table.

**Safeguards against data drift:**  
- Retraining is triggered only when new experimental data is logged, not on a fixed schedule
- Sample size is tracked — correction factors from fewer than 3 experiments are flagged as low-confidence
- All prediction and retrain history is versioned and auditable
- Discrepancies between predicted and actual values surface automatically, highlighting model weaknesses

**Data provenance:**  
Every record in the database carries a source tag (Materials Project, BRENDA, Claude AI, or researcher-logged), a timestamp, and a catalyst ID. This ensures full traceability from original retrieval through prediction to experimental outcome.

---

## 5. Failure Memory System

Unlike conventional platforms that only surface top-performing candidates, Fail2Learn systematically captures and analyses failures.

**Failure patterns detected:**
- Low activity — candidates with actual activity below 0.3
- Low stability — candidates with actual stability below 0.3  
- Catalyst poisoning — detected from researcher notes
- Sintering — high-temperature degradation, detected from notes

**For each pattern, the platform provides:**
- Which catalysts were affected
- How frequently the pattern appears
- A concrete actionable recommendation (e.g., "Use high surface area supports to prevent particle agglomeration")

**Prediction vs actual comparison:**  
For every logged experiment, the platform computes the gap between predicted and actual performance. If the gap exceeds 0.2 on any metric, it is flagged as a significant discrepancy and surfaced in the dashboard for researcher review.

---

## 6. Technology Choices and Justification

| Choice | Justification |
|--------|--------------|
| Claude API for generation | State-of-the-art reasoning for proposing chemically plausible candidates; no molecular ML model training required within hackathon scope |
| SQLite | Lightweight, zero-config, fully local — appropriate for prototype; easily migrated to PostgreSQL for production |
| FastAPI | Fast, async, auto-generates OpenAPI docs — ideal for ML serving |
| Materials Project + BRENDA | Gold-standard open databases for inorganic catalysts and enzyme data respectively |
| Composite scoring | Transparent, auditable, and adjustable — judges and researchers can see exactly how scores are computed |

**Key risks and mitigations:**

| Risk | Mitigation |
|------|-----------|
| API unavailability | Fallback synthetic data built in for both Materials Project and BRENDA |
| Model overfit to few experiments | Sample size tracked; low-confidence corrections flagged |
| False positives in failure detection | Pattern detection requires explicit keyword or threshold triggers — not probabilistic guessing |
| LLM hallucination in candidate generation | Candidates are ranked by a separate scoring model, not accepted blindly from the LLM |

---

## 7. Collaborative Features

- **Experiment logs** carry a `logged_by` field for researcher attribution
- **Annotations table** allows multiple researchers to add notes to any experiment
- **Version history** — every prediction and retrain event is timestamped and stored
- **Full audit trail** from original query through to follow-up hypothesis

---

## 8. Development Roadmap

### Hackathon Prototype (Current)
- ✅ Full pipeline: fetch → generate → predict → visualise → feedback → retrain
- ✅ Materials Project + BRENDA integration with fallback data
- ✅ Claude API generative module
- ✅ Failure analysis engine with pattern detection
- ✅ FastAPI backend with 5 endpoints
- ✅ SQLite database with full schema
- ✅ React dashboard (in progress)

### Longer-Term Pilot with GPS Renewables
- Replace composite scoring with trained ML models (GNN or XGBoost on molecular descriptors)
- Integrate real GPS Renewables reaction data (ethanol-to-jet conversion)
- Add molecular structure visualisation (3D viewer via RDKit or Mol*)
- Add metabolic flux modelling for synthetic biology direction
- Deploy on cloud infrastructure with multi-user authentication
- Connect to laboratory information management systems (LIMS) for automated result ingestion
- Expand to additional reactions relevant to GPS Renewables operations

---

## 9. Why Fail2Learn Wins

Most AI research tools are prediction machines — they generate candidates and stop there. Fail2Learn closes the loop. Every failed experiment makes the next prediction more accurate. Every logged result builds institutional knowledge that persists across researchers and projects.

For GPS Renewables, this means shorter discovery cycles for their ethanol-to-jet catalyst programme, reduced reagent waste from pursuing low-probability candidates, and a growing competitive advantage as the platform learns from their specific reaction conditions over time.

**We are willing to engage in a longer-term pilot with GPS Renewables** to develop this platform beyond the hackathon, integrating real production data and extending coverage to their full catalyst and bioprocess portfolio.