from fastapi import APIRouter
from backend.app.schemas.route import RouteCompareRequest, RouteCompareResponse
from backend.app.services.routing_service import compare_routes

router = APIRouter(prefix="/routes", tags=["Route Intelligence"])

@router.post("/compare", response_model=RouteCompareResponse)
def compare_available_routes(req: RouteCompareRequest):
    return compare_routes(
        origin_lat=req.origin_lat,
        origin_lon=req.origin_lon,
        dest_lat=req.dest_lat,
        dest_lon=req.dest_lon
    )
