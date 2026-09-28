from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models.incident import Incident
from app.models.satellite import SatelliteObservation
from app.models.evidence import (
    WeatherObservation, OceanObservation, VesselEvent,
    CandidateSource, PredictedPath, AffectedArea
)
from app.schemas.incident import IncidentResponse, IncidentDetailResponse
from app.auth import require_user, require_admin_role

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentResponse])
def get_incidents(
    status_filter: Optional[str] = Query(None, alias="status"),
    anomaly_type: Optional[str] = None,
    min_priority: Optional[float] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_user)
):
    """GET /incidents (AUTHENTICATED) - List incidents querying Supabase Cloud database directly."""
    # 1. Primary: Query Supabase Cloud Database directly
    try:
        from app.services.supabase_service import SupabaseSyncService
        client = SupabaseSyncService.get_client()
        if client:
            query_builder = client.table("incidents").select("*")
            if status_filter:
                query_builder = query_builder.eq("status", status_filter)
            if anomaly_type:
                query_builder = query_builder.eq("anomaly_type", anomaly_type)
            if min_priority is not None:
                query_builder = query_builder.gte("priority_score", min_priority)
            
            res = query_builder.order("last_updated", desc=True).limit(limit).execute()
            if res.data and len(res.data) > 0:
                from app.environmental.gis import GISService
                for item in res.data:
                    if not item.get("location_name") or item.get("location_name") == "Unknown Marine Region" or "Coastal Sector (" in str(item.get("location_name")):
                        lat = item.get("latitude", 21.145)
                        lon = item.get("longitude", 72.620)
                        item["location_name"] = GISService.get_location_name(lat, lon)
                return res.data
    except Exception as sp_err:
        print(f"[Incidents API] Supabase Cloud query notice: {sp_err}")

    # 2. Secondary Fallback: Local database query
    query = db.query(Incident)
    if status_filter:
        query = query.filter(Incident.status == status_filter)
    if anomaly_type:
        query = query.filter(Incident.anomaly_type == anomaly_type)
    if min_priority is not None:
        query = query.filter(Incident.priority_score >= min_priority)

    incidents = query.order_by(Incident.last_updated.desc()).limit(limit).all()
    from app.environmental.gis import GISService
    for inc in incidents:
        if not inc.location_name or inc.location_name == "Unknown Marine Region" or "Coastal Sector (" in str(inc.location_name):
            inc.location_name = GISService.get_location_name(inc.latitude, inc.longitude)
    return incidents

@router.get("/{incident_id}", response_model=IncidentDetailResponse)
def get_incident_detail(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_user)
):
    """GET /incidents/{incident_id} (AUTHENTICATED) - Get detailed incident view from Supabase Cloud."""
    # 1. Primary: Query Supabase Cloud Database directly
    try:
        from app.services.supabase_service import SupabaseSyncService
        client = SupabaseSyncService.get_client()
        if client:
            res = client.table("incidents").select("*").eq("id", incident_id).execute()
            if not res.data:
                res = client.table("incidents").select("*").eq("incident_code", incident_id).execute()
            if res.data and len(res.data) > 0:
                item = res.data[0]
                if not item.get("location_name") or item.get("location_name") == "Unknown Marine Region" or "Coastal Sector (" in str(item.get("location_name")):
                    from app.environmental.gis import GISService
                    lat = item.get("latitude", 21.145)
                    lon = item.get("longitude", 72.620)
                    item["location_name"] = GISService.get_location_name(lat, lon)
                return item
    except Exception as sp_err:
        print(f"[Incidents API Detail] Supabase Cloud detail query notice: {sp_err}")

    # 2. Secondary Fallback: Local database query
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        incident = db.query(Incident).filter(Incident.incident_code == incident_id).first()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")

    if not incident.location_name or incident.location_name == "Unknown Marine Region" or "Coastal Sector (" in str(incident.location_name):
        from app.environmental.gis import GISService
        incident.location_name = GISService.get_location_name(incident.latitude, incident.longitude)

    return incident

@router.get("/{incident_id}/evidence")
def get_incident_evidence(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_user)
):
    """GET /incidents/{incident_id}/evidence (AUTHENTICATED) - Get evidence timeline."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "incident_id": incident.id,
        "incident_code": incident.incident_code,
        "satellite_observations": incident.satellite_observations,
        "weather_observations": incident.weather_observations,
        "ocean_observations": incident.ocean_observations,
        "citizen_reports": incident.citizen_reports
    }

@router.get("/{incident_id}/trajectory")
def get_incident_trajectory(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_user)
):
    """GET /incidents/{incident_id}/trajectory (AUTHENTICATED) - Get forecast trajectory points."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "incident_id": incident.id,
        "incident_code": incident.incident_code,
        "current_latitude": incident.latitude,
        "current_longitude": incident.longitude,
        "predicted_paths": incident.predicted_paths
    }

@router.get("/{incident_id}/sources")
def get_incident_sources(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_user)
):
    """GET /incidents/{incident_id}/sources (AUTHENTICATED) - Get candidate origin sources."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "incident_id": incident.id,
        "candidate_sources": incident.candidate_sources,
        "vessel_events": incident.vessel_events
    }

@router.get("/{incident_id}/impact")
def get_incident_impact(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_user)
):
    """GET /incidents/{incident_id}/impact (AUTHENTICATED) - Get coastal exposure impact."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "incident_id": incident.id,
        "affected_areas": incident.affected_areas,
        "priority_score": incident.priority_score,
        "severity_score": incident.severity_score
    }

@router.post("/{incident_id}/reanalyze")
async def reanalyze_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """POST /incidents/{incident_id}/reanalyze (ADMIN) - Trigger full Agentic AI reanalysis."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    from app.agents.graph import marineguard_workflow

    initial_state = {
        "incident_id": incident.id,
        "incident_code": incident.incident_code,
        "latitude": incident.latitude,
        "longitude": incident.longitude,
        "anomaly_type": incident.anomaly_type,
        "first_detected": incident.first_detected.isoformat(),
        "last_updated": incident.last_updated.isoformat(),
        "satellite_evidence": [],
        "weather_evidence": [],
        "ocean_evidence": [],
        "vessel_evidence": [],
        "citizen_reports": [],
        "missing_sources": [],
        "possible_sources": [],
        "predicted_path": [],
        "affected_areas": [],
        "rag_passages": [],
        "confidence_score": incident.confidence_score,
        "severity_score": incident.severity_score,
        "priority_score": incident.priority_score,
        "risk_level": "HIGH",
        "status": "UNDER_INVESTIGATION",
        "report": None,
        "next_step": "collect_evidence"
    }

    final_state = await marineguard_workflow.ainvoke(initial_state)

    if final_state.get("report"):
        incident.report = final_state["report"]
    incident.status = final_state.get("status", "UNDER_INVESTIGATION")
    db.commit()
    db.refresh(incident)

    # Sync complete updated incident data to Supabase Cloud
    try:
        from app.services.supabase_service import SupabaseSyncService
        SupabaseSyncService.sync_incident(db, incident.id)
    except Exception:
        pass

    return {
        "status": "reanalysis_completed",
        "incident_id": incident.id,
        "incident_code": incident.incident_code,
        "priority_score": incident.priority_score,
        "report": incident.report
    }

@router.post("/{incident_id}/email")
async def send_incident_report_email(
    incident_id: str,
    payload: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_user)
):
    """POST /incidents/{incident_id}/email (AUTHENTICATED) - Dispatches investigation report & evidence via Gmail SMTP."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        incident = db.query(Incident).filter(Incident.incident_code == incident_id).first()

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")

    recipient_email = None
    if payload and "recipient" in payload:
        recipient_email = payload["recipient"]

    from app.services.email_service import EmailAlertService
    
    img_path = incident.before_after_image_path or incident.annotated_image_path or incident.raw_image_path
    if not img_path and incident.satellite_observations:
        sat = incident.satellite_observations[0]
        img_path = sat.before_after_image_path or sat.annotated_image_path or sat.image_path

    res = EmailAlertService.send_report_email(
        incident_code=incident.incident_code,
        recipient=recipient_email,
        report_text=incident.report,
        image_path=img_path,
        location_name=incident.location_name,
        anomaly_type=incident.anomaly_type,
        priority_score=incident.priority_score
    )

    return res
