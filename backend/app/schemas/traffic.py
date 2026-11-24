from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TrafficSegment(BaseModel):
    segment_id: str
    road_name: str
    latitude: float
    longitude: float
    current_speed_kmh: float
    free_flow_speed_kmh: float
    congestion_level: str
    congestion_ratio: float

class TrafficFlowResponse(BaseModel):
    latitude: float
    longitude: float
    current_speed_kmh: float
    free_flow_speed_kmh: float
    congestion_level: str
    data_source: str
    is_live_provider: bool
    last_updated: datetime
    segments: List[TrafficSegment]
