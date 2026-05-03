from fastapi import APIRouter
from db.models import get_db
from ml.retrain import get_retrain_history

router = APIRouter()

@router.get("/history")
def get_history(reaction: str):
    """Return all past experiments and retraining events for a reaction."""
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        SELECT catalyst_id, formula, outcome, actual_yield,
               actual_activity, actual_stability, notes, logged_at
        FROM experiments WHERE reaction=?
        ORDER BY logged_at DESC
    """, (reaction,))
    cols = ["catalyst_id","formula","outcome","actual_yield",
            "actual_activity","actual_stability","notes","logged_at"]
    experiments = [dict(zip(cols, row)) for row in cur.fetchall()]
    conn.close()

    retrain_log = get_retrain_history(reaction)

    return {
        "reaction"    : reaction,
        "experiments" : experiments,
        "retrain_log" : retrain_log,
        "total_runs"  : len(experiments),
    }
