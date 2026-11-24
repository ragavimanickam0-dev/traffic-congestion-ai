import json
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models.prediction import PredictionHistory
from backend.app.models.user import User
from backend.app.schemas.prediction import PredictionRequest, PredictionResponse, PredictionHistoryItem
from backend.app.services.ml_service import predict_congestion
from backend.app.services.weather_service import get_current_weather
from backend.app.utils.security import get_current_user_optional

router = APIRouter(prefix="/predictions", tags=["Traffic Predictions"])

@router.post("", response_model=PredictionResponse)
def make_prediction(
    req: PredictionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    if req.horizon_minutes not in [15, 30, 60]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported prediction horizons are 15, 30, and 60 minutes."
        )

    temp = req.temperature_c
    precip = req.precipitation_mm
    if temp is None or precip is None:
        live_weather = get_current_weather(req.latitude, req.longitude)
        if temp is None:
            temp = live_weather.get("temperature_c", 24.5)
        if precip is None:
            precip = live_weather.get("precipitation_mm", 0.0)

    result = predict_congestion(
        location_name=req.location_name,
        latitude=req.latitude,
        longitude=req.longitude,
        horizon_minutes=req.horizon_minutes,
        temperature_c=temp,
        precipitation_mm=precip
    )

    try:
        history_record = PredictionHistory(
            user_id=current_user.id if current_user else None,
            location_name=req.location_name,
            latitude=req.latitude,
            longitude=req.longitude,
            horizon_minutes=req.horizon_minutes,
            predicted_category=result["predicted_category"],
            confidence_score=result["confidence_score"],
            weather_condition=result.get("weather_condition", "Clear"),
            temperature_c=temp,
            feature_attribution_json=json.dumps(result.get("feature_attributions", []))
        )
        db.add(history_record)
        db.commit()
    except Exception:
        db.rollback()

    return result

@router.get("/history", response_model=List[PredictionHistoryItem])
def get_prediction_history(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    limit_val = int(limit) if isinstance(limit, (int, str)) and str(limit).isdigit() else 10
    query = db.query(PredictionHistory)
    if current_user:
        user_records = query.filter(PredictionHistory.user_id == current_user.id).order_by(PredictionHistory.created_at.desc()).limit(limit_val).all()
        if user_records:
            return user_records

    return query.order_by(PredictionHistory.created_at.desc()).limit(limit_val).all()
