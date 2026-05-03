from fastapi import APIRouter
from ml.predict_performance import get_top_candidates
from ml.failure_analysis import get_failure_summary

router = APIRouter()

@router.get("/candidates")
def get_candidates(reaction: str, top_n: int = 10):
    """Return top ranked candidates + failure summary for a reaction."""
    candidates = get_top_candidates(reaction, top_n=top_n)
    failure    = get_failure_summary(reaction)
    return {
        "reaction"       : reaction,
        "candidates"     : candidates,
        "failure_summary": failure,
    }
