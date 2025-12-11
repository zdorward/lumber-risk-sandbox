from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .etl import run_etl
from .analytics import compute_analytics

import os
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # if DB doesn’t exist, or is empty, run ETL once
    if not os.path.exists("lumber.db"):
        run_etl()
    yield

app = FastAPI(title="Lumber Risk Sandbox", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for a demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/etl/run")
def run_etl_endpoint():
    try:
        run_etl()
        return {"status": "ok", "message": "ETL completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
def analytics(symbol: str = "LBS=F",
              ma_short: int = 10,
              ma_long: int = 30,
              notional: float = 1_000_000.0):
    try:
        result = compute_analytics(symbol, ma_short, ma_long, notional)
        if not result:
            raise HTTPException(status_code=404, detail="No data / analytics available")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))