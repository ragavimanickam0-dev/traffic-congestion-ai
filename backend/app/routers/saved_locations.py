from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models.location import SavedLocation
from backend.app.models.user import User
from backend.app.schemas.location import SavedLocationCreate, SavedLocationResponse
from backend.app.utils.security import get_current_user_optional

router = APIRouter(prefix="/saved-locations", tags=["Saved Locations"])

@router.get("", response_model=List[SavedLocationResponse])
def get_saved_locations(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    if not current_user:
        return [
            SavedLocation(
                id=1,
                user_id=1,
                label="Home",
                address="Indiranagar 100ft Road, Bangalore",
                category="Home",
                latitude=12.9784,
                longitude=77.6408
            ),
            SavedLocation(
                id=2,
                user_id=1,
                label="Tech Park Office",
                address="Manyata Tech Park, Nagavara",
                category="Work",
                latitude=13.0475,
                longitude=77.6212
            )
        ]

    return db.query(SavedLocation).filter(SavedLocation.user_id == current_user.id).all()

@router.post("", response_model=SavedLocationResponse, status_code=status.HTTP_201_CREATED)
def create_saved_location(
    req: SavedLocationCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else 1

    location = SavedLocation(
        user_id=user_id,
        label=req.label.strip(),
        address=req.address.strip(),
        category=req.category,
        latitude=req.latitude,
        longitude=req.longitude
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location

@router.delete("/{location_id}", status_code=status.HTTP_200_OK)
def delete_saved_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    location = db.query(SavedLocation).filter(SavedLocation.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved location not found."
        )

    if current_user and location.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this saved location."
        )

    db.delete(location)
    db.commit()
    return {"message": "Location removed successfully"}
