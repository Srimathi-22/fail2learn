import sqlite3
import json
from datetime import datetime
from collections import defaultdict

DB_PATH = "db/fail2learn.db"


def _ensure_tables():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            catalyst_id      TEXT,
            formula          TEXT,
            reaction         TEXT,
            actual_yield     REAL,
            actual_activity  REAL,
            actual_stability REAL,
            outcome          TEXT,   -- 'success' | 'partial' | 'failure'
            notes            TEXT,
            logged_at        TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS failure_patterns (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            reaction         TEXT,
            pattern_type     TEXT,
            description      TEXT,
            affected_formulas TEXT,
            frequency        INTEGER,
            recommendation   TEXT,
            detected_at      TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_experiment(catalyst_id: str, formula: str, reaction: str,
                   actual_yield: float, actual_activity: float,
                   actual_stability: float, outcome: str, notes: str = "") -> int:
    """
    Log a real experimental result back into the platform.
    outcome: 'success' | 'partial' | 'failure'
    Returns the experiment id.
    """
    _ensure_tables()
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO experiments
        (catalyst_id, formula, reaction, actual_yield,
         actual_activity, actual_stability, outcome, notes, logged_at)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (catalyst_id, formula, reaction, actual_yield,
          actual_activity, actual_stability, outcome, notes,
          datetime.now().isoformat()))
    exp_id = cur.lastrowid
    conn.commit()
    conn.close()
    print(f"[failure_analysis] Logged experiment #{exp_id} — outcome: {outcome}")
    return exp_id


def compare_prediction_vs_actual(catalyst_id: str) -> dict:
    """
    Compare what the model predicted vs what actually happened.
    Surfaces discrepancies that may reveal model weaknesses.
    """
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    cur.execute("""
        SELECT predicted_activity, predicted_stability, final_score
        FROM predictions WHERE catalyst_id=? ORDER BY id DESC LIMIT 1
    """, (catalyst_id,))
    pred = cur.fetchone()

    cur.execute("""
        SELECT actual_activity, actual_stability, actual_yield, outcome
        FROM experiments WHERE catalyst_id=? ORDER BY id DESC LIMIT 1
    """, (catalyst_id,))
    actual = cur.fetchone()
    conn.close()

    if not pred or not actual:
        return {"error": "Missing prediction or experiment data"}

    activity_gap  = round(actual[0] - pred[0], 3)
    stability_gap = round(actual[1] - pred[1], 3)

    discrepancies = []
    if abs(activity_gap) > 0.2:
        discrepancies.append({
            "field"    : "activity",
            "predicted": pred[0],
            "actual"   : actual[0],
            "gap"      : activity_gap,
            "severity" : "high" if abs(activity_gap) > 0.35 else "medium",
        })
    if abs(stability_gap) > 0.2:
        discrepancies.append({
            "field"    : "stability",
            "predicted": pred[1],
            "actual"   : actual[1],
            "gap"      : stability_gap,
            "severity" : "high" if abs(stability_gap) > 0.35 else "medium",
        })

    return {
        "catalyst_id"   : catalyst_id,
        "outcome"       : actual[3],
        "actual_yield"  : actual[2],
        "discrepancies" : discrepancies,
        "model_accurate": len(discrepancies) == 0,
    }


def detect_failure_patterns(reaction: str) -> list[dict]:
    """
    Analyse all failed experiments for a reaction.
    Find common structural or condition patterns in failures.
    """
    _ensure_tables()
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        SELECT catalyst_id, formula, actual_activity, actual_stability, outcome, notes
        FROM experiments
        WHERE reaction=? AND outcome IN ('failure','partial')
    """, (reaction,))
    failures = cur.fetchall()
    conn.close()

    if not failures:
        print(f"[failure_analysis] No failures logged yet for '{reaction}'")
        return []

    # Group by formula patterns
    pattern_counts = defaultdict(list)
    for (cat_id, formula, activity, stability, outcome, notes) in failures:
        if activity is not None and activity < 0.3:
            pattern_counts["low_activity"].append(formula)
        if stability is not None and stability < 0.3:
            pattern_counts["low_stability"].append(formula)
        if notes and "poison" in notes.lower():
            pattern_counts["catalyst_poisoning"].append(formula)
        if notes and "sinter" in notes.lower():
            pattern_counts["sintering"].append(formula)

    patterns = []
    recommendations = {
        "low_activity"       : "Consider promoters or support modification to improve active site density.",
        "low_stability"      : "Explore bimetallic formulations or coating with stabilising oxide.",
        "catalyst_poisoning" : "Pre-treat feed gas to remove sulphur/halide impurities before reaction.",
        "sintering"          : "Use high surface area supports (SBA-15, Al2O3) to prevent particle agglomeration.",
    }

    for pattern_type, formulas in pattern_counts.items():
        entry = {
            "reaction"         : reaction,
            "pattern_type"     : pattern_type,
            "description"      : f"{len(formulas)} catalysts failed due to {pattern_type.replace('_',' ')}",
            "affected_formulas": json.dumps(list(set(formulas))),
            "frequency"        : len(formulas),
            "recommendation"   : recommendations.get(pattern_type, "Further investigation needed."),
            "detected_at"      : datetime.now().isoformat(),
        }
        patterns.append(entry)
        _save_pattern(entry)

    print(f"[failure_analysis] Detected {len(patterns)} failure patterns for '{reaction}'")
    return patterns


def _save_pattern(pattern: dict):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO failure_patterns
        (reaction,pattern_type,description,affected_formulas,frequency,recommendation,detected_at)
        VALUES (?,?,?,?,?,?,?)
    """, (
        pattern["reaction"], pattern["pattern_type"], pattern["description"],
        pattern["affected_formulas"], pattern["frequency"],
        pattern["recommendation"], pattern["detected_at"]
    ))
    conn.commit()
    conn.close()


def get_failure_summary(reaction: str) -> dict:
    """Return a summary of failure patterns for the frontend."""
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM experiments WHERE reaction=?", (reaction,))
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM experiments WHERE reaction=? AND outcome='failure'", (reaction,))
    failures = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM experiments WHERE reaction=? AND outcome='success'", (reaction,))
    successes = cur.fetchone()[0]
    cur.execute("""
        SELECT pattern_type, frequency, recommendation
        FROM failure_patterns WHERE reaction=?
        ORDER BY frequency DESC
    """, (reaction,))
    patterns = [{"type": r[0], "frequency": r[1], "recommendation": r[2]}
                for r in cur.fetchall()]
    conn.close()

    return {
        "reaction"       : reaction,
        "total_experiments": total,
        "failures"       : failures,
        "successes"      : successes,
        "failure_rate"   : round(failures / total, 2) if total else 0,
        "top_patterns"   : patterns[:3],
    }


if __name__ == "__main__":
    _ensure_tables()

    # Simulate some experiment logs
    log_experiment("ai-gen-CO2 to-1", "Cu-Zn-Ga/Al2O3", "CO2 to methanol",
                   actual_yield=0.72, actual_activity=0.68,
                   actual_stability=0.55, outcome="success")

    log_experiment("ai-gen-CO2 to-2", "In2O3-ZrO2", "CO2 to methanol",
                   actual_yield=0.30, actual_activity=0.25,
                   actual_stability=0.20, outcome="failure",
                   notes="catalyst poisoning observed, rapid deactivation")

    log_experiment("mp-fallback-1", "Cu/ZnO/Al2O3", "CO2 to methanol",
                   actual_yield=0.50, actual_activity=0.48,
                   actual_stability=0.35, outcome="partial",
                   notes="sintering detected at high temperature")

    patterns = detect_failure_patterns("CO2 to methanol")
    summary  = get_failure_summary("CO2 to methanol")

    print(f"\nFailure summary: {summary}")
    print("\n✅ failure_analysis.py complete!")
