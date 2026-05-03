import sqlite3
import json
from datetime import datetime

DB_PATH = "db/fail2learn.db"

# ─── Scoring weights ───────────────────────────────────────
WEIGHTS = {
    "activity"   : 0.40,
    "selectivity": 0.35,
    "stability"  : 0.25,
}

def _score(activity: float, selectivity: float, stability: float) -> float:
    return round(
        WEIGHTS["activity"]    * activity +
        WEIGHTS["selectivity"] * selectivity +
        WEIGHTS["stability"]   * stability, 4
    )

def _penalty(failure_risk: float) -> float:
    """Higher failure risk reduces final score."""
    return round(1.0 - (failure_risk * 0.3), 4)


def predict_and_rank(reaction: str) -> list[dict]:
    """
    Pull all candidates (known + novel) for a reaction,
    compute composite score, rank them, save results.
    """
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Pull novel AI candidates
    cur.execute("""
        SELECT catalyst_id, formula, source, rationale,
               predicted_activity, predicted_selectivity,
               predicted_stability, failure_risk, failure_reason, is_novel
        FROM candidates WHERE reaction=?
    """, (reaction,))
    novel_rows = cur.fetchall()

    # Pull known catalysts (assign default scores)
    cur.execute("""
        SELECT catalyst_id, formula, source, NULL, NULL, NULL, NULL, NULL, NULL, 0
        FROM catalysts WHERE reaction=? AND is_novel=0
    """, (reaction,))
    known_rows = cur.fetchall()

    conn.close()

    all_rows = novel_rows + known_rows
    if not all_rows:
        print(f"[predict] No candidates found for '{reaction}'. Run fetch + generate first.")
        return []

    ranked = []
    for row in all_rows:
        (cat_id, formula, source, rationale,
         activity, selectivity, stability,
         failure_risk, failure_reason, is_novel) = row

        # Known catalysts get estimated scores based on literature averages
        if activity is None:
            activity, selectivity, stability, failure_risk = 0.55, 0.50, 0.60, 0.30

        composite   = _score(activity, selectivity, stability)
        penalty     = _penalty(failure_risk or 0.3)
        final_score = round(composite * penalty, 4)

        ranked.append({
            "catalyst_id"          : cat_id,
            "formula"              : formula,
            "source"               : source,
            "reaction"             : reaction,
            "rationale"            : rationale or "Retrieved from scientific database",
            "predicted_activity"   : round(activity, 3),
            "predicted_selectivity": round(selectivity, 3),
            "predicted_stability"  : round(stability, 3),
            "failure_risk"         : round(failure_risk or 0.3, 3),
            "failure_reason"       : failure_reason or "Standard degradation",
            "composite_score"      : composite,
            "final_score"          : final_score,
            "is_novel"             : bool(is_novel),
            "rank"                 : 0,
            "predicted_at"         : datetime.now().isoformat(),
        })

    # Sort by final score descending
    ranked.sort(key=lambda x: x["final_score"], reverse=True)
    for i, r in enumerate(ranked):
        r["rank"] = i + 1

    _save_predictions(ranked)
    print(f"[predict] Ranked {len(ranked)} candidates for '{reaction}'")
    return ranked


def _save_predictions(ranked: list[dict]):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            catalyst_id           TEXT,
            formula               TEXT,
            source                TEXT,
            reaction              TEXT,
            rationale             TEXT,
            predicted_activity    REAL,
            predicted_selectivity REAL,
            predicted_stability   REAL,
            failure_risk          REAL,
            failure_reason        TEXT,
            composite_score       REAL,
            final_score           REAL,
            rank                  INTEGER,
            is_novel              INTEGER,
            predicted_at          TEXT
        )
    """)
    for r in ranked:
        cur.execute("""
            INSERT INTO predictions
            (catalyst_id,formula,source,reaction,rationale,
             predicted_activity,predicted_selectivity,predicted_stability,
             failure_risk,failure_reason,composite_score,final_score,rank,is_novel,predicted_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            r["catalyst_id"], r["formula"], r["source"], r["reaction"],
            r["rationale"], r["predicted_activity"], r["predicted_selectivity"],
            r["predicted_stability"], r["failure_risk"], r["failure_reason"],
            r["composite_score"], r["final_score"], r["rank"],
            int(r["is_novel"]), r["predicted_at"]
        ))
    conn.commit()
    conn.close()


def get_top_candidates(reaction: str, top_n: int = 5) -> list[dict]:
    """Return top N ranked candidates for a reaction."""
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        SELECT * FROM predictions
        WHERE reaction=?
        ORDER BY final_score DESC LIMIT ?
    """, (reaction, top_n))
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    conn.close()
    return rows


if __name__ == "__main__":
    reaction = "CO2 to methanol"
    results  = predict_and_rank(reaction)
    print(f"\nTop 5 candidates for '{reaction}':")
    for r in results[:5]:
        print(f"  #{r['rank']} {r['formula']} | score={r['final_score']} | novel={r['is_novel']}")
    print("\n✅ predict_performance.py complete!")
