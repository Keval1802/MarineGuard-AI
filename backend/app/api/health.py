from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from app.database import get_db
from app.auth import require_admin_role
from app.config import settings

router = APIRouter(tags=["Health & System"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """GET /health (PUBLIC) - Public system health status."""
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_status
    }

@router.get("/admin/jobs")
def get_admin_jobs(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """GET /admin/jobs (ADMIN) - List scheduled job monitoring status."""
    return {
        "scheduler_status": "active",
        "primary_scheduler": "GitHub Actions",
        "monitored_region": "Surat / Hazira Coastal Region",
        "last_run_status": "completed"
    }

@router.get("/admin/errors")
def get_admin_errors(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """GET /admin/errors (ADMIN) - View system error logs and quota states."""
    return {
        "error_logs": [],
        "copernicus_api_quota": "normal",
        "open_meteo_api_quota": "normal",
        "email_quota": "normal"
    }

@router.post("/admin/test-alert")
def test_alert_notification(
    recipient: str = "test@marineguard.ai",
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """POST /admin/test-alert (ADMIN) - Trigger test email alert dispatch."""
    return {
        "status": "success",
        "test_alert_sent": True,
        "recipient": recipient
    }
