"""
Pydantic schemas for the ML prediction API.
Defines request/response models for the /predict endpoint.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class MeterReading(BaseModel):
    """Single smart meter reading with multi-dimensional telemetry."""
    timestamp: str
    consumption_kwh: float = Field(ge=0, description="Active energy in kWh")
    voltage: float = Field(ge=0, description="Line voltage in V")
    current: float = Field(ge=0, default=0.0, description="Line current in A")
    power_factor: float = Field(ge=0, le=1, default=1.0, description="Real/apparent power ratio")
    frequency: float = Field(ge=0, default=50.0, description="Grid frequency in Hz")
    tamper_flag: bool = Field(default=False, description="Hardware tamper indicator")


class ConsumptionStats(BaseModel):
    """Statistical summary of a measurement dimension."""
    mean: float = 0.0
    std: float = 0.0
    min: float = 0.0
    max: float = 0.0


class Features(BaseModel):
    """Pre-computed statistical features sent by the backend."""
    consumption_stats: ConsumptionStats = ConsumptionStats()
    voltage_stats: ConsumptionStats = ConsumptionStats()
    current_stats: ConsumptionStats = ConsumptionStats()
    power_factor_stats: ConsumptionStats = ConsumptionStats()
    frequency_stats: ConsumptionStats = ConsumptionStats()
    tamper_ratio: float = 0.0
    baseline_consumption: float = 0.0
    consumer_type: str = "residential"
    reading_count: int = 0


class PredictRequest(BaseModel):
    """Full prediction request payload."""
    meter_id: str
    features: Features
    readings: List[MeterReading]


class AnomalyBreakdown(BaseModel):
    """Per-measure anomaly scores (0–1)."""
    consumption_drop: float = Field(0.0, ge=0, le=1)
    voltage_anomaly: float = Field(0.0, ge=0, le=1)
    current_anomaly: float = Field(0.0, ge=0, le=1)
    power_factor_anomaly: float = Field(0.0, ge=0, le=1)
    frequency_deviation: float = Field(0.0, ge=0, le=1)
    tamper_detected: float = Field(0.0, ge=0, le=1)
    pattern_irregularity: float = Field(0.0, ge=0, le=1)
    flat_line_detection: float = Field(0.0, ge=0, le=1)


class PredictResponse(BaseModel):
    """Prediction result returned to the backend."""
    theft_probability: float = Field(ge=0, le=1)
    anomaly_flag: bool
    anomaly_breakdown: AnomalyBreakdown
    source: str = Field(description="'model' or 'heuristic'")
    confidence: float = Field(ge=0, le=1, default=0.0)
    risk_level: str = Field(default="low", description="low / medium / high / critical")
