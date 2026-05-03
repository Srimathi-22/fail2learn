from fastapi import APIRouter
from pydantic import BaseModel
from ml.failure_analysis import log_experiment, compare_prediction_vs_actual, detect_failure_patterns
from ml.retrain import retrain

router = APIRouter()

class FeedbackRequest(BaseModel):
    catalyst_id     : str
    formula         : str
    reaction        : str
    actual_yield    : float
    actual_activity : float
    actual_stability: float
    outcome         : str   # 'success' | 'partial' | 'failure'
    notes           : str = ""
    logged_by       : str = "researcher"

@router.post("/feedback")
def log_feedback(req: FeedbackRequest):
    """
    Log real experimental result, compare with prediction,
    detect failure patterns, and retrain models.
    """
    exp_id = log_experiment(
        catalyst_id      = req.catalyst_id,
        formula          = req.formula,
        reaction         = req.reaction,
        actual_yield     = req.actual_yield,
        actual_activity  = req.actual_activity,
        actual_stability = req.actual_stability,
        outcome          = req.outcome,
        notes            = req.notes,
    )
    comparison = compare_prediction_vs_actual(req.catalyst_id)
    patterns   = detect_failure_patterns(req.reaction)
    factors    = retrain(req.reaction)

    return {
        "experiment_id"  : exp_id,
        "outcome"        : req.outcome,
        "comparison"     : comparison,
        "patterns_found" : len(patterns),
        "retrain_factors": factors,
        "message"        : "Feedback logged and models updated successfully",
    }
