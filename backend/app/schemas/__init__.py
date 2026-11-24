from backend.app.schemas.auth import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse
from backend.app.schemas.prediction import PredictionRequest, PredictionResponse, PredictionHistoryItem
from backend.app.schemas.traffic import TrafficFlowResponse, TrafficSegment
from backend.app.schemas.route import RouteCompareRequest, RouteCompareResponse, RouteSegment
from backend.app.schemas.report import CommunityReportCreate, CommunityReportResponse
from backend.app.schemas.location import SavedLocationCreate, SavedLocationResponse, LocationSearchItem

__all__ = [
    "UserRegisterRequest", "UserLoginRequest", "UserResponse", "TokenResponse",
    "PredictionRequest", "PredictionResponse", "PredictionHistoryItem",
    "TrafficFlowResponse", "TrafficSegment",
    "RouteCompareRequest", "RouteCompareResponse", "RouteSegment",
    "CommunityReportCreate", "CommunityReportResponse",
    "SavedLocationCreate", "SavedLocationResponse", "LocationSearchItem"
]
