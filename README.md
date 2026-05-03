# Fail2Learn 
### AI Platform for Molecular Discovery in Chemical Catalysis & Synthetic Biology

> Built for **AI for Bharat Hackathon** — Theme 4
>By Flamboyant

---

##  What is Fail2Learn?

Fail2Learn accelerates catalyst and enzyme discovery by learning from **both successes AND failures**. Most AI tools only learn from what works  we learn from what doesn't.

A researcher enters a target reaction like **CO₂ → Methanol** or **Ethanol → Jet Fuel**. The platform fetches known catalysts from scientific databases, generates novel AI-designed candidates, ranks them by predicted performance, and continuously improves from real experimental feedback.

---

##  Key Features

- **Catalyst Retrieval** — fetches from Materials Project + BRENDA databases
- **AI Candidate Generation** — proposes novel catalyst designs
- **Performance Ranking** — scores by activity, selectivity, stability
- **Failure Risk Analysis** — predicts failure modes before lab testing
- **Feedback Loop** — log real results, retrain models automatically
- **Full Audit Trail** — version history, experiment logs, retrain events
- **Any Reaction** — works for any target reaction

---

## 🗂️ Project Structure

```
fail2learn/
├── ml/
│   ├── fetch_catalysts.py
│   ├── generate_candidates.py
│   ├── predict_performance.py
│   ├── failure_analysis.py
│   └── retrain.py
├── db/
│   └── models.py
├── backend/
│   ├── main.py
│   └── routes/
│       ├── reaction.py
│       ├── candidates.py
│       ├── feedback.py
│       └── history.py
├── frontend/
├── idea_submission.md
└── requirements.txt
```

---

##  Setup & Run

```bash
git clone https://github.com/Srimathi-22/fail2learn.git
cd fail2learn
pip install -r requirements.txt
python db/models.py
set PYTHONPATH=.
python ml/fetch_catalysts.py
python ml/generate_candidates.py
python ml/predict_performance.py
python ml/failure_analysis.py
python -m uvicorn backend.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm start
```

---

##  API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reaction` | Run full pipeline |
| GET | `/api/candidates?reaction=...` | Get ranked candidates |
| POST | `/api/feedback` | Log results + retrain |
| GET | `/api/history?reaction=...` | View experiment history |
| GET | `/api/stats` | Platform statistics |

---

##  Tech Stack

| Layer | Technology |
|-------|-----------|
| AI | Claude API (Anthropic) |
| Backend | FastAPI, Uvicorn |
| Database | SQLite |
| Frontend | React, Recharts |
| Data Sources | Materials Project, BRENDA |

---

##  Team

| Member | Role |
|--------|------|
| Srimathi S | ML + Backend |
| R Manolisha | Backend Support and debugging |
| Tiruvalarnayatty S| Frontend + UI designs |
