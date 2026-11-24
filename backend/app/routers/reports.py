from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models.report import CommunityReport
from backend.app.models.user import User
from backend.app.schemas.report import CommunityReportCreate, CommunityReportResponse
from backend.app.utils.security import get_current_user_optional

router = APIRouter(prefix="/reports", tags=["Community Incident Reports"])

@router.get("", response_model=List[CommunityReportResponse])
def get_reports(
    type: Optional[str] = None,
    status: Optional[str] = "active",
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(CommunityReport)
    if type and isinstance(type, str):
        query = query.filter(CommunityReport.report_type == type)
    if status and isinstance(status, str):
        query = query.filter(CommunityReport.status == status)

    limit_val = int(limit) if isinstance(limit, (int, str)) and str(limit).isdigit() else 50
    return query.order_by(CommunityReport.created_at.desc()).limit(limit_val).all()

@router.post("", response_model=CommunityReportResponse, status_code=status.HTTP_201_CREATED)
def submit_report(
    req: CommunityReportCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    report = CommunityReport(
        user_id=current_user.id if current_user else None,
        report_type=req.report_type,
        road_name=req.road_name or "Reported Segment",
        description=req.description.strip(),
        latitude=req.latitude,
        longitude=req.longitude,
        severity=req.severity,
        status="active",
        votes=1
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.post("/{report_id}/vote")
def vote_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(CommunityReport).filter(CommunityReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident report not found."
        )

    report.votes += 1
    if report.votes >= 3:
        report.status = "verified"
    db.commit()
    return {"message": "Vote recorded", "votes": report.votes, "status": report.status}
