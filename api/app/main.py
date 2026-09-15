"""FastAPI entrypoint. Phase 1 (H0-H6) scope only: prove the app boots,
can reach Postgres, and can load config/weights.yaml. Award/flag/score
routes land in the H6-H18 and H18-H30 blocks once the six flags exist."""
from fastapi import FastAPI, HTTPException

from app.config import get_weights
from app.db import get_cursor

app = FastAPI(title="Procurement Anomaly Detection API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    try:
        with get_cursor() as cur:
            cur.execute("SELECT 1 AS ok")
            row = cur.fetchone()
        return {"status": "ok", "db": row}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"database unreachable: {exc}")


@app.get("/config/weights")
def config_weights():
    """Exposes config/weights.yaml verbatim so the frontend/demo can show
    the real thresholds on camera without duplicating them."""
    return get_weights()
