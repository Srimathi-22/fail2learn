from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.models import init_db, get_stats

# ─── Import routers ───────────────────────────────────────
from backend.routes.reaction  import router as reaction_router
from backend.routes.candidates import router as candidates_router
from backend.routes.feedback  import router as feedback_router
from backend.routes.history   import router as history_router

# ─── App setup ────────────────────────────────────────────
app = FastAPI(
    title       = "Fail2Learn API",
    description = "AI Platform for Molecular Discovery in Chemical Catalysis",
    version     = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # restrict in production
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ─── Register routers ─────────────────────────────────────
app.include_router(reaction_router,    prefix="/api", tags=["Reaction"])
app.include_router(candidates_router,  prefix="/api", tags=["Candidates"])
app.include_router(feedback_router,    prefix="/api", tags=["Feedback"])
app.include_router(history_router,     prefix="/api", tags=["History"])


# ─── Startup ──────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    init_db()
    print("✅ Fail2Learn API started — DB initialized")


# ─── Health check ─────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "Fail2Learn API is running"}


@app.get("/api/stats")
def stats():
    return get_stats()


# ─── Run ──────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
