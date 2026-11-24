from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class SavedLocationCreate(BaseModel):
    label: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=3, max_length=255)
    category: str = Field(default="Other")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

class SavedLocationResponse(BaseModel):
    id: int
    user_id: int
    label: str
    address: str
    category: str
    latitude: float
    longitude: float
    created_at: datetime

    class Config:
        from_attributes = True

class LocationSearchItem(BaseModel):
    display_name: str
    lat: float
    lon: float
    type: Optional[str] = None
