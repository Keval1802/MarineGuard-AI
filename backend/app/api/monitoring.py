from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import uuid

from app.database import get_db
from app.config import settings
from app.auth import require_admin_role
from app.models.incident import Incident, IncidentStatus, AnomalyType
from app.models.satellite import SatelliteObservation, ProcessedSourceItem
from app.models.evidence import (
    WeatherObservation, OceanObservation, VesselEvent,
    CandidateSource, PredictedPath, AffectedArea
)
from app.models.alert import Alert

from app.satellite.catalog import CopernicusCatalogService
from app.satellite.anomaly_detector import AnomalyDetector
from app.satellite.image_capture import SatelliteImageCaptureService
from app.environmental.weather import WeatherService
from app.environmental.ocean import OceanService
from app.environmental.gis import GISService
from app.services.confidence import ConfidenceCalculator
from app.services.trajectory import TrajectoryService
from app.services.risk import RiskCalculator
from app.services.email_service import EmailAlertService
from app.services.report_service import ReportService

router = APIRouter(prefix="/monitor", tags=["Scheduled Monitoring"])

@router.post("/run")
async def run_monitoring_cycle(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    force_anomaly: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    POST /monitor/run (SYSTEM / ADMIN).
    Executes near-real-time monitoring pipeline (Section 14):
    1. Polling new satellite & environmental data.
    2. Running deterministic anomaly detection.
    3. Applying Section 21 incident merge rule (5 km / 48 h).
    4. Aggregating multi-source evidence.
    5. Generating satellite visual evidence images.
    6. Computing trajectory, risk, priority, and alerts.
    """
    catalog = CopernicusCatalogService()
    image_service = SatelliteImageCaptureService()
    detector = AnomalyDetector()

    lat = latitude if latitude is not None else settings.DEFAULT_AOI_CENTER[0]
    lon = longitude if longitude is not None else settings.DEFAULT_AOI_CENTER[1]
    bbox = (lon - 0.08, lat - 0.08, lon + 0.08, lat + 0.08)

    # Search for observations in target bounding box
    scenes = await catalog.search_scenes(bbox=bbox)
    processed_count = 0
    new_incidents_count = 0
    updated_incidents_count = 0
    affected_incident_ids = set()
    affected_incidents_payload: Dict[str, Dict[str, Any]] = {}

    for scene in scenes:
        prod_id = scene["product_id"]
        
        # Section 14 Deduplication rule: check if product_id already processed
        existing = db.query(ProcessedSourceItem).filter(ProcessedSourceItem.source_item_id == prod_id).first()
        if existing and existing.processed and not force_anomaly:
            continue

        # Fetch real satellite observation scene
        target_anomaly = force_anomaly or ("OIL_LIKE_ANOMALY" if "S1" in prod_id else "HIGH_TURBIDITY_EVENT")
        real_scene = catalog.fetch_real_satellite_image(
            width=512, height=512, mission=scene["mission"], anomaly_type=target_anomaly, lat=lat, lon=lon
        )

        # Weather & Ocean context at acquisition
        weather_data = await WeatherService.get_weather(lat, lon)
        ocean_data = await OceanService.get_ocean_conditions(lat, lon)

        # Anomaly Detection (Section 16)
        detection = detector.process_scene(
            scene_rgb=real_scene,
            mission=scene["mission"],
            wind_speed_ms=weather_data["wind_speed_ms"],
            target_class=target_anomaly
        )

        # Record item as processed
        if not existing:
            from dateutil.parser import parse as parse_dt
            try:
                acq_dt = parse_dt(scene["acquisition_time"])
            except Exception:
                acq_dt = datetime.utcnow()

            processed_item = ProcessedSourceItem(
                source_name=scene["mission"],
                source_item_id=prod_id,
                acquisition_time=acq_dt,
                processed=True
            )
            db.add(processed_item)

        processed_count += 1

        if not detection["detected"]:
            db.commit()
            continue

        # Anomaly Detected -> Apply Section 21 Incident Merge Rule
        det_class = detection["anomaly_class"]
        det_conf = detection["confidence"]
        est_area = detection.get("estimated_area_km2", 1.5)

        # Section 21 Merge Check: Find open active incidents
        time_cutoff = datetime.utcnow() - timedelta(hours=settings.INCIDENT_MERGE_MAX_TIME_HOURS)
        active_incidents = db.query(Incident).filter(
            Incident.status.notin_([IncidentStatus.RESOLVED.value, IncidentStatus.CLOSED.value, IncidentStatus.FALSE_POSITIVE.value]),
            Incident.last_updated >= time_cutoff
        ).all()

        target_incident = None
        for inc in active_incidents:
            dist_km = GISService.haversine_distance(lat, lon, inc.latitude, inc.longitude)
            # Same class or SURFACE_ANOMALY/UNKNOWN, within 5 km, within 48h
            class_match = (inc.anomaly_type == det_class or 
                           inc.anomaly_type in ["SURFACE_ANOMALY", "UNKNOWN"] or 
                           det_class in ["SURFACE_ANOMALY", "UNKNOWN"])
            if class_match and dist_km <= settings.INCIDENT_MERGE_MAX_DISTANCE_KM:
                target_incident = inc
                break

        if target_incident:
            # Merge into existing incident: Update current known location (Section 21)
            target_incident.latitude = lat
            target_incident.longitude = lon
            target_incident.location_name = GISService.get_location_name(lat, lon)
            target_incident.last_updated = datetime.utcnow()
            target_incident.anomaly_type = det_class
            updated_incidents_count += 1
            inc_code = target_incident.incident_code
        else:
            # Create new incident
            code_num = db.query(Incident).count() + 1
            inc_code = f"MG-2026-{code_num:04d}"
            target_incident = Incident(
                incident_code=inc_code,
                anomaly_type=det_class,
                latitude=lat,
                longitude=lon,
                location_name=GISService.get_location_name(lat, lon),
                first_detected=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                status=IncidentStatus.DETECTED.value
            )
            db.add(target_incident)
            db.flush() # Populate target_incident.id
            new_incidents_count += 1

        # Capture satellite evidence images (Section 13)
        image_paths = image_service.capture_evidence_images(
            incident_code=inc_code,
            anomaly_type=det_class,
            confidence=det_conf,
            area_km2=est_area,
            mission=scene["mission"],
            latitude=lat,
            longitude=lon
        )

        # Record Satellite Observation (Deduplicated per product_id)
        existing_sat_obs = db.query(SatelliteObservation).filter_by(
            incident_id=target_incident.id, product_id=prod_id
        ).first()
        if not existing_sat_obs:
            sat_obs = SatelliteObservation(
                incident_id=target_incident.id,
                mission=scene["mission"],
                product_id=prod_id,
                acquisition_time=datetime.utcnow(),
                cloud_cover=scene["cloud_cover"],
                image_path=image_paths["raw_image_path"],
                annotated_image_path=image_paths["annotated_image_path"],
                before_after_image_path=image_paths["before_after_image_path"],
                model_result=det_class,
                detection_method=detection["detection_method"],
                wind_speed_ms=detection.get("wind_speed_ms"),
                confidence=det_conf
            )
            db.add(sat_obs)

        # Record Weather & Ocean Observations
        weather_obs = WeatherObservation(
            incident_id=target_incident.id,
            wind_speed=weather_data["wind_speed_ms"],
            wind_direction=weather_data["wind_direction_deg"],
            rainfall=weather_data["rainfall_mmh"],
            source=weather_data["source"]
        )
        db.add(weather_obs)

        ocean_obs = OceanObservation(
            incident_id=target_incident.id,
            current_speed=ocean_data["current_speed_ms"],
            current_direction=ocean_data["current_direction_deg"],
            tide=ocean_data["tide"],
            sea_surface_temperature=ocean_data["sea_surface_temperature_c"],
            source=ocean_data["source"]
        )
        db.add(ocean_obs)

        # Calculate Trajectory (Section 24) - Clear previous predicted paths to avoid duplicates
        db.query(PredictedPath).filter_by(incident_id=target_incident.id).delete()
        trajectory_pts = TrajectoryService.calculate_drift_trajectory(
            lat=lat, lon=lon, anomaly_type=det_class,
            current_speed_ms=ocean_data["current_speed_ms"],
            current_dir_deg=ocean_data["current_direction_deg"],
            wind_speed_ms=weather_data["wind_speed_ms"],
            wind_dir_deg=weather_data["wind_direction_deg"]
        )
        for pt in trajectory_pts:
            db.add(PredictedPath(
                incident_id=target_incident.id,
                forecast_time=pt["forecast_time"],
                latitude=pt["latitude"],
                longitude=pt["longitude"],
                uncertainty=pt["uncertainty_km"]
            ))

        # Calculate Origin Zone & Candidate Sources (Section 23) - Deduplicated by reference
        reverse_zone = TrajectoryService.calculate_reverse_origin_zone(
            lat=lat, lon=lon, anomaly_type=det_class,
            current_speed_ms=ocean_data["current_speed_ms"],
            current_dir_deg=ocean_data["current_direction_deg"],
            wind_speed_ms=weather_data["wind_speed_ms"],
            wind_dir_deg=weather_data["wind_direction_deg"]
        )
        nearby_gis = GISService.get_nearby_assets(reverse_zone["origin_latitude"], reverse_zone["origin_longitude"], max_distance_km=10.0)
        for gis_item in nearby_gis[:2]:
            existing_cs = db.query(CandidateSource).filter_by(
                incident_id=target_incident.id, reference=gis_item["name"]
            ).first()
            if not existing_cs:
                db.add(CandidateSource(
                    incident_id=target_incident.id,
                    source_type=gis_item["type"],
                    reference=gis_item["name"],
                    confidence="moderate",
                    evidence_json={"distance_km": gis_item["distance_km"]}
                ))

        # Calculate Confidence (Section 22)
        sat_obs_count = db.query(SatelliteObservation).filter_by(incident_id=target_incident.id).count()
        has_second_sat = (sat_obs_count >= 1) or (image_paths.get("before_after_image_path") is not None) or (len(scenes) > 1)

        conf_res = ConfidenceCalculator.calculate_confidence(
            has_satellite=True,
            satellite_model_conf=det_conf,
            has_second_satellite=has_second_sat,
            environmental_match=True
        )
        target_incident.confidence_score = conf_res["confidence_score"]

        # Calculate Risk and Priority Score (Section 26)
        risk_res = RiskCalculator.calculate_risk(
            confidence_score=target_incident.confidence_score,
            anomaly_type=det_class,
            estimated_area_km2=est_area,
            latitude=lat,
            longitude=lon,
            trajectory_points=trajectory_pts
        )
        target_incident.severity_score = risk_res["severity_score"]
        target_incident.priority_score = risk_res["priority_score"]

        # Save Affected GIS Areas (Section 25) - Clear previous affected areas to avoid duplicates
        db.query(AffectedArea).filter_by(incident_id=target_incident.id).delete()
        for aff in risk_res["affected_areas"]:
            db.add(AffectedArea(
                incident_id=target_incident.id,
                area_type=aff["area_type"],
                area_name=aff["area_name"],
                distance_km=aff["distance_km"],
                risk_level=aff["risk_level"]
            ))

        # Generate Deterministic Incident Report
        affected_str = ", ".join([a["area_name"] for a in risk_res["affected_areas"]]) or "None immediate"
        cand_sources_list = [{"source_type": g["type"], "reference": g["name"]} for g in nearby_gis[:2]]
        
        target_incident.report = ReportService.generate_deterministic_report(
            incident_code=inc_code,
            anomaly_type=det_class,
            latitude=lat,
            longitude=lon,
            confidence_score=target_incident.confidence_score,
            confidence_level=conf_res["confidence_level"],
            priority_score=target_incident.priority_score,
            risk_level=risk_res["risk_level"],
            estimated_area_km2=est_area,
            weather_data=weather_data,
            ocean_data=ocean_data,
            candidate_sources=cand_sources_list,
            predicted_path=trajectory_pts,
            affected_areas=risk_res["affected_areas"],
            confidence_breakdown=conf_res["breakdown_points"],
            risk_breakdown=risk_res
        )

        db.commit()
        img_attachment = image_paths.get("before_after_image_path") or image_paths.get("annotated_image_path") or image_paths.get("raw_image_path")
        affected_incidents_payload[target_incident.id] = {
            "incident": target_incident,
            "incident_code": inc_code,
            "anomaly_type": det_class,
            "risk_level": risk_res["risk_level"],
            "affected_areas_str": affected_str,
            "image_path": img_attachment
        }
        affected_incident_ids.add(target_incident.id)

    # Section 27 Alert Dispatch Deduplication: Send ONCE per affected incident per monitoring cycle
    for inc_id, payload in affected_incidents_payload.items():
        inc = payload["incident"]

        # Check if an email alert was already dispatched for this incident in the last 4 hours
        four_hours_ago = datetime.utcnow() - timedelta(hours=4)
        recent_alert = db.query(Alert).filter(
            Alert.incident_id == inc_id,
            Alert.alert_type.in_(["EMAIL_ALERT", "HIGH_PRIORITY_EMAIL"]),
            Alert.created_at >= four_hours_ago
        ).first()

        # Allow dispatch if no recent alert exists OR if priority score >= 0.85 (critical escalation)
        if recent_alert and inc.priority_score < 0.85 and not force_anomaly:
            continue

        alert_res = EmailAlertService.send_incident_alert(
            incident_code=payload["incident_code"],
            priority_score=inc.priority_score,
            risk_level=payload["risk_level"],
            anomaly_type=payload["anomaly_type"],
            confidence_score=inc.confidence_score,
            location_str=inc.location_name or f"Hazira Coast ({lat:.3f}, {lon:.3f})",
            affected_areas_str=payload["affected_areas_str"],
            report_text=inc.report,
            image_path=payload["image_path"]
        )
        if alert_res["triggered"]:
            db.add(Alert(
                incident_id=inc_id,
                alert_type=alert_res["alert_type"],
                recipient=alert_res["recipient"],
                status=alert_res["status"],
                sent_at=datetime.utcnow() if "SENT" in alert_res.get("status", "") else None
            ))
            db.commit()

    # Real-time Supabase Cloud Sync ONCE per affected incident after scan cycle finishes
    if affected_incident_ids:
        try:
            from app.services.supabase_service import SupabaseSyncService
            for inc_id in affected_incident_ids:
                SupabaseSyncService.sync_incident(db, inc_id)
        except Exception:
            pass

    return {
        "status": "success",
        "processed_sources_count": processed_count,
        "new_incidents_created": new_incidents_count,
        "existing_incidents_updated": updated_incidents_count
    }
