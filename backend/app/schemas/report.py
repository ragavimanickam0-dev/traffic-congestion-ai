from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CommunityReportCreate(BaseModel):
    report_type: str = Field(..., pattern="^(Accident|Road Closure|Waterlogging|Construction|Congestion)$")
    road_name: Optional[str] = None
    description: str = Field(..., min_length=5, max_length=1000)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    severity: str = Field(default="Medium", pattern="^(Low|Medium|Critical)$")

class CommunityReportResponse(BaseModel):
    id: int
    user_id: Optional[int]
    report_type: str
    road_name: Optional[str]
    description: str
    latitude: float
    longitude: float
    severity: str
    status: str
    votes: int
    created_at: datetime

    class Config:
        from_attributes = True
