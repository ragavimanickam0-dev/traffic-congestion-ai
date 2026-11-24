from fastapi import APIRouter, Query
from backend.app.schemas.traffic import TrafficFlowResponse
from backend.app.services.traffic_service import get_traffic_telemetry

router = APIRouter(prefix="/traffic", tags=["Traffic Telemetry"])

@router.get("", response_model=TrafficFlowResponse)
def get_traffic(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    zoom: int = 14
):
    zoom_val = int(zoom) if isinstance(zoom, (int, str)) and str(zoom).isdigit() else 14
    return get_traffic_telemetry(lat, lon, zoom_val)
