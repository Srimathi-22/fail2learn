from fastapi import APIRouter
from pydantic import BaseModel
from ml.fetch_catalysts import fetch_all
from ml.generate_candidates import generate_candidates
from ml.predict_performance import predict_and_rank

router = APIRouter()

class ReactionRequest(BaseModel):
    reaction: str
    n_candidates: int = 5

@router.post("/reaction")
def run_reaction_pipeline(req: ReactionRequest):
    known  = fetch_all(req.reaction)
    novel  = generate_candidates(req.reaction, n=req.n_candidates)
    ranked = predict_and_rank(req.reaction)
    return {
        "reaction"        : req.reaction,
        "known_catalysts" : len(known),
        "novel_candidates": len(novel),
        "ranked_results"  : ranked[:10],
    }