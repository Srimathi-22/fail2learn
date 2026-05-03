# Fail2Learn 🧪
### AI Platform for Molecular Discovery in Chemical Catalysis & Synthetic Biology

Built for **AI for Bharat Hackathon** — Theme 4  
Team: [Your Team Name]

---

## 🚀 What It Does

Fail2Learn accelerates catalyst and enzyme discovery by learning from **both successes and failures**. Researchers enter a target reaction, the platform fetches known catalysts, generates novel AI candidates, predicts performance, and continuously improves from experimental feedback.

---

## 🗂️ Project Structure

```
fail2learn/
├── ml/
│   ├── fetch_catalysts.py       # Fetch from Materials Project + BRENDA
│   ├── generate_candidates.py   # Claude AI → novel catalyst designs
│   ├── predict_performance.py   # Score + rank all candidates
│   ├── failure_analysis.py      # Detect failure patterns
│   └── retrain.py               # Retrain models from feedback
├── db/
│   └── models.py                # SQLite schema + helpers
├── backend/
│   ├── main.py                  # FastAPI app
│   └── routes/
│       ├── reaction.py          # POST /api/reaction
│       ├── candidates.py        # GET  /api/candidates
│       ├── feedback.py          # POST /api/feedback
│       └── history.py           # GET  /api/history
├── frontend/                    # React dashboard
├── video/                       # 5-min walkthrough
└── requirements.txt
```

---

## ⚙️ Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
**Windows:**
```bash
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```
**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Initialize the database
```bash
python db/models.py
```

### 4. Run the ML pipeline
```bash
python ml/fetch_catalysts.py
python ml/generate_candidates.py
python ml/predict_performance.py
python ml/failure_analysis.py
```

### 5. Start the backend
```bash
uvicorn backend.main:app --reload
```
API runs at: `http://localhost:8000`  
Docs at: `http://localhost:8000/docs`

### 6. Start the frontend
```bash
cd frontend
npm install
npm start
```
Dashboard at: `http://localhost:3000`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reaction` | Run full pipeline for a target reaction |
| GET | `/api/candidates?reaction=...` | Get ranked candidates + failure summary |
| POST | `/api/feedback` | Log experimental results + retrain |
| GET | `/api/history?reaction=...` | View past experiments + retrain log |
| GET | `/api/stats` | Overall platform statistics |

---

## 🧬 Example Workflow

1. Researcher enters: `CO2 + green H2 → methanol`
2. Platform fetches 5 known catalysts from Materials Project + BRENDA
3. Claude AI generates 5 novel candidate designs
4. All 10 ranked by predicted activity, selectivity, stability
5. Researcher exports top 3 for lab testing
6. After experiments, logs results via `/api/feedback`
7. Platform detects failure patterns + retrains models

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| ML / AI | Python, Claude API (Anthropic) |
| Database | SQLite |
| Backend | FastAPI, Uvicorn |
| Frontend | React, Recharts |
| Data Sources | Materials Project, BRENDA |

---


