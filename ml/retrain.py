import sqlite3
import json
from datetime import datetime

DB_PATH = "db/fail2learn.db"


def get_training_data(reaction: str) -> list[dict]:
    """
    Pull all experiments that have both a prediction and actual result.
    These become training examples for model improvement.
    """
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        SELECT e.catalyst_id, e.formula, e.reaction,
               e.actual_yield, e.actual_activity, e.actual_stability, e.outcome,
               p.predicted_activity, p.predicted_selectivity,
               p.predicted_stability, p.failure_risk
        FROM experiments e
        LEFT JOIN predictions p ON e.catalyst_id = p.catalyst_id
        WHERE e.reaction = ?
    """, (reaction,))
    rows = cur.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            "catalyst_id"          : row[0],
            "formula"              : row[1],
            "reaction"             : row[2],
            "actual_yield"         : row[3],
            "actual_activity"      : row[4],
            "actual_stability"     : row[5],
            "outcome"              : row[6],
            "predicted_activity"   : row[7],
            "predicted_selectivity": row[8],
            "predicted_stability"  : row[9],
            "failure_risk"         : row[10],
        })
    return data


def compute_correction_factors(training_data: list[dict]) -> dict:
    """
    Compare predicted vs actual values.
    Compute average correction factors to adjust future predictions.
    """
    if not training_data:
        return {}

    activity_errors  = []
    stability_errors = []

    for d in training_data:
        if d["predicted_activity"] and d["actual_activity"]:
            activity_errors.append(d["actual_activity"] - d["predicted_activity"])
        if d["predicted_stability"] and d["actual_stability"]:
            stability_errors.append(d["actual_stability"] - d["predicted_stability"])

    factors = {}
    if activity_errors:
        factors["activity_bias"]  = round(sum(activity_errors)  / len(activity_errors), 4)
    if stability_errors:
        factors["stability_bias"] = round(sum(stability_errors) / len(stability_errors), 4)

    # Outcome-based weight adjustment
    outcomes = [d["outcome"] for d in training_data]
    success_rate = outcomes.count("success") / len(outcomes)
    factors["success_rate"]        = round(success_rate, 3)
    factors["training_sample_size"] = len(training_data)

    return factors


def apply_corrections(reaction: str, factors: dict):
    """
    Apply correction factors to existing predictions for this reaction.
    This simulates model retraining by adjusting scores.
    """
    if not factors:
        print("[retrain] No correction factors — skipping update")
        return

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    activity_bias  = factors.get("activity_bias", 0)
    stability_bias = factors.get("stability_bias", 0)

    cur.execute("""
        UPDATE predictions
        SET predicted_activity  = MIN(1.0, MAX(0.0, predicted_activity  + ?)),
            predicted_stability = MIN(1.0, MAX(0.0, predicted_stability + ?)),
            final_score = MIN(1.0, MAX(0.0, final_score + ? * 0.4 + ? * 0.25))
        WHERE reaction = ?
    """, (activity_bias, stability_bias, activity_bias, stability_bias, reaction))

    conn.commit()
    conn.close()
    print(f"[retrain] Applied corrections — activity bias: {activity_bias}, stability bias: {stability_bias}")


def save_retrain_log(reaction: str, factors: dict):
    """Log every retraining event for auditability."""
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS retrain_log (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            reaction     TEXT,
            factors      TEXT,
            retrained_at TEXT
        )
    """)
    cur.execute("""
        INSERT INTO retrain_log (reaction, factors, retrained_at)
        VALUES (?, ?, ?)
    """, (reaction, json.dumps(factors), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    print(f"[retrain] Logged retraining event for '{reaction}'")


def retrain(reaction: str):
    """
    Full retraining pipeline:
    1. Pull training data (experiments + predictions)
    2. Compute correction factors
    3. Apply corrections to predictions
    4. Log the retraining event
    """
    print(f"\n[retrain] Starting retraining for '{reaction}'...")

    training_data = get_training_data(reaction)
    if not training_data:
        print(f"[retrain] No training data found for '{reaction}' — run experiments first")
        return

    print(f"[retrain] Found {len(training_data)} training samples")

    factors = compute_correction_factors(training_data)
    print(f"[retrain] Correction factors: {factors}")

    apply_corrections(reaction, factors)
    save_retrain_log(reaction, factors)

    print(f"[retrain] ✅ Retraining complete for '{reaction}'")
    return factors


def get_retrain_history(reaction: str) -> list[dict]:
    """Return all past retraining events for a reaction."""
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS retrain_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reaction TEXT, factors TEXT, retrained_at TEXT)
    """)
    cur.execute("""
        SELECT reaction, factors, retrained_at
        FROM retrain_log WHERE reaction=?
        ORDER BY retrained_at DESC
    """, (reaction,))
    rows = [{"reaction": r[0], "factors": json.loads(r[1]), "retrained_at": r[2]}
            for r in cur.fetchall()]
    conn.close()
    return rows


if __name__ == "__main__":
    factors = retrain("CO2 to methanol")
    history = get_retrain_history("CO2 to methanol")
    print(f"\nRetrain history: {len(history)} events")
    print("✅ retrain.py complete!")
