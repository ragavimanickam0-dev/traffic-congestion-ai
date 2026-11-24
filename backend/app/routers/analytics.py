from fastapi import APIRouter, Query
from typing import Dict, Any
from backend.app.services.ml_service import get_model_metadata

router = APIRouter(prefix="/analytics", tags=["Analytics & Model Metrics"])

@router.get("/traffic")
def get_traffic_analytics(location: str = "All"):
    return {
        "location": location,
        "distribution": {
            "low": 35.0,
            "moderate": 42.0,
            "high": 23.0
        },
        "diurnal_speeds": [
            54, 56, 58, 57, 52, 42, 30, 18, 16, 26, 34, 38,
            36, 35, 33, 28, 20, 14, 16, 24, 35, 42, 48, 52
        ],
        "weekly_congestion_index": {
            "Mon": 78,
            "Tue": 82,
            "Wed": 85,
            "Thu": 84,
            "Fri": 91,
            "Sat": 54,
            "Sun": 42
        }
    }

@router.get("/model-metrics")
def get_evaluation_metrics():
    return get_model_metadata()
