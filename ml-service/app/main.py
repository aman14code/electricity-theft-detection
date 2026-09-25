"""
Electricity Theft Detection — ML Microservice
FastAPI server with /predict endpoint for anomaly detection.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import PredictRequest, PredictResponse, BatchPredictRequest, BatchPredictResponse
from .model import predict_with_model, predict_heuristic, _ensemble

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


@app.post("/predict/batch", response_model=BatchPredictResponse)
async def batch_predict(request: BatchPredictRequest):
    """
    Predict theft probabilities for a batch of consumers.
    Returns results and a prioritized risk queue sorted by probability.
    """
    results = []
    queue = []
    
    for consumer in request.consumers:
        result = predict_with_model(consumer.features, consumer.readings)
        if result is None:
            result = predict_heuristic(consumer.features, consumer.readings)
            
        results.append(result)
        
        if result.anomaly_flag or result.theft_probability > 0.15:
            queue.append({
                "meter_id": consumer.meter_id,
                "theft_probability": result.theft_probability,
                "risk_level": result.risk_level,
                "confidence": result.confidence
            })
            
    # Sort queue by probability descending
    queue.sort(key=lambda x: x["theft_probability"], reverse=True)
    
    summary = {
        "total_processed": len(request.consumers),
        "anomalies_detected": len([r for r in results if r.anomaly_flag]),
        "critical_risk": len([r for r in results if r.risk_level == "critical"]),
        "high_risk": len([r for r in results if r.risk_level == "high"])
    }
    
    return BatchPredictResponse(
        results=results,
        risk_queue=queue,
        summary=summary
    )


@app.get("/metrics")
async def get_metrics():
    """
    Return model evaluation metrics generated during training.
    Checks both results/ and app/ directories.
    """
    import os
    import json
    # Check the results directory first (where train_model.py saves them)
    results_path = os.path.join(os.path.dirname(__file__), "..", "results", "evaluation_results.json")
    app_path = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
    
    for metrics_path in [results_path, app_path]:
        if os.path.exists(metrics_path):
            with open(metrics_path, "r", encoding="utf-8") as f:
                return json.load(f)
    return {"message": "Metrics not found. Please train the model first."}


@app.get("/model-info")
async def get_model_info():
    """
    Return information about the loaded ensemble model.
    """
    if _ensemble is None:
        return {"loaded": False, "message": "No ensemble model loaded"}

    return {
        "loaded": True,
        "training_date": _ensemble.get("training_date", "unknown"),
        "n_features": _ensemble.get("n_features", 0),
        "feature_names": _ensemble.get("feature_names", []),
        "optimal_threshold": _ensemble.get("optimal_threshold", 0.5),
        "dataset_info": _ensemble.get("dataset_info", {}),
        "has_shap": _ensemble.get("shap_importance") is not None,
        "models": ["Random Forest", "XGBoost", "DNN", "Isolation Forest", "LSTM"],
        "ensemble_method": "stacking" if _ensemble.get("meta_model") else "soft_voting",
    }

