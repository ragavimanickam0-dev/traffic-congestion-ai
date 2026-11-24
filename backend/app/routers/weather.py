from fastapi import APIRouter, Query
from backend.app.services.weather_service import get_current_weather

router = APIRouter(prefix="/weather", tags=["Meteorology"])

@router.get("")
def get_weather(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0)
):
    return get_current_weather(lat, lon)
