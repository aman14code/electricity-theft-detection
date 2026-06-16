"""
Electricity Theft Detection — ML Microservice
FastAPI server with /predict endpoint for anomaly detection.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import PredictRequest, PredictResponse
from .model import predict_with_model, predict_heuristic

app = FastAPI(
    title="Electricity Theft Detection — ML Service",
    description="Multi-measure anomaly detection engine for smart meter data",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "ml-service"}


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Predict theft probability from smart meter readings.

    Accepts an array of time-series meter readings with multi-dimensional
    telemetry (consumption, voltage, current, power factor, frequency,
    tamper flag).

    Returns theft probability (0–1), anomaly flag, per-measure breakdown,
    confidence score, and risk level.

    Pipeline:
      1. Try trained ML model (.pkl) if available
      2. Fall back to 8-measure deterministic heuristic engine
    """
    if not request.readings:
        raise HTTPException(status_code=400, detail="No readings provided")

    # 1. Try trained model first
    result = predict_with_model(request.features, request.readings)

    # 2. Fall back to heuristic
    if result is None:
        result = predict_heuristic(request.features, request.readings)

    return result
