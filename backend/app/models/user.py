from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    saved_locations = relationship("SavedLocation", back_populates="user", cascade="all, delete-orphan")
    prediction_history = relationship("PredictionHistory", back_populates="user", cascade="all, delete-orphan")
    community_reports = relationship("CommunityReport", back_populates="user")
