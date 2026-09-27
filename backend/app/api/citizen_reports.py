from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models.evidence import CitizenReport
from app.schemas.incident import CitizenReportCreate, CitizenReportResponse
from app.auth import require_user

router = APIRouter(prefix="/citizen-reports", tags=["Citizen Reports"])

@router.post("", response_model=CitizenReportResponse, status_code=status.HTTP_201_CREATED)
def submit_citizen_report(
    report_data: CitizenReportCreate,
    db: Session = Depends(get_db)
):
    """POST /citizen-reports (PUBLIC) - Submit citizen pollution report."""
    report = CitizenReport(
        description=report_data.description,
        latitude=report_data.latitude,
        longitude=report_data.longitude,
        image_path=report_data.image_path,
        verification_status="UNVERIFIED"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.get("", response_model=List[CitizenReportResponse])
def get_citizen_reports(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_user)
):
    """GET /citizen-reports (AUTHENTICATED) - List submitted citizen reports."""
    reports = db.query(CitizenReport).order_by(CitizenReport.submitted_at.desc()).limit(100).all()
    return reports
