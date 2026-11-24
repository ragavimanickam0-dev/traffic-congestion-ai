from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict

class FeatureAttribution(BaseModel):
    name: str
    importance: float
    direction: Optional[str] = None

class DepartureRecommendation(BaseModel):
    suggested_departure: str
    delay_saved_minutes: int
    rationale: str

class PredictionRequest(BaseModel):
    location_name: str = Field(..., min_length=2)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    horizon_minutes: int = Field(default=30, description="15, 30, or 60 minutes")
    temperature_c: Optional[float] = None
    precipitation_mm: Optional[float] = None

class PredictionResponse(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    horizon_minutes: int
    predicted_category: str
    confidence_score: float
    class_probabilities: Dict[str, float]
    weather_condition: str
    temperature_c: float
    precipitation_mm: float
    feature_attributions: List[FeatureAttribution]
    horizon_trend: List[int]
    departure_recommendation: Optional[DepartureRecommendation] = None
    narrative: str
    evaluated_at: datetime
    data_source: str

class PredictionHistoryItem(BaseModel):
    id: int
    location_name: str
    latitude: float
    longitude: float
    horizon_minutes: int
    predicted_category: str
    confidence_score: float
    weather_condition: Optional[str]
    temperature_c: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True
