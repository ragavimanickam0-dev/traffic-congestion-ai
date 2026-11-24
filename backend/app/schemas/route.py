from pydantic import BaseModel, Field
from typing import List, Optional

class RouteSegment(BaseModel):
    duration_minutes: float
    distance_km: float
    congestion_level: str
    summary: str
    geometry: List[List[float]]

class RouteCompareRequest(BaseModel):
    origin_lat: float = Field(..., ge=-90.0, le=90.0)
    origin_lon: float = Field(..., ge=-180.0, le=180.0)
    dest_lat: float = Field(..., ge=-90.0, le=90.0)
    dest_lon: float = Field(..., ge=-180.0, le=180.0)

class RouteCompareResponse(BaseModel):
    primary_route: RouteSegment
    alternative_route: Optional[RouteSegment] = None
    departure_guidance: str
    routing_engine: str
