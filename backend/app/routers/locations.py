from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.search import SearchHistory
from backend.app.models.user import User
from backend.app.services.geocoding_service import search_locations, reverse_geocode
from backend.app.utils.security import get_current_user_optional

router = APIRouter(prefix="/locations", tags=["Locations & Geocoding"])

@router.get("/search")
def search(
    q: str = Query(..., min_length=2),
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    limit_val = int(limit) if isinstance(limit, (int, str)) and str(limit).isdigit() else 5
    results = search_locations(q, limit_val)

    try:
        first_lat = results[0]["lat"] if results else None
        first_lon = results[0]["lon"] if results else None
        record = SearchHistory(
            user_id=current_user.id if current_user else None,
            query_text=q[:250],
            latitude=first_lat,
            longitude=first_lon
        )
        db.add(record)
        db.commit()
    except Exception:
        db.rollback()

    return results

@router.get("/reverse")
def reverse(lat: float = Query(..., ge=-90, le=90), lon: float = Query(..., ge=-180, le=180)):
    return reverse_geocode(lat, lon)
