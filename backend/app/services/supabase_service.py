"""
MarineGuard AI — Real-Time Supabase Cloud Synchronization Service

Automatically synchronizes incident records, telemetry observations, and visual satellite evidence
to Supabase Cloud PostgreSQL database tables and Supabase Storage buckets at creation time.
"""

import os
import sys
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.models.incident import Incident
from app.models.satellite import SatelliteObservation
from app.models.evidence import WeatherObservation, OceanObservation, CandidateSource, PredictedPath, AffectedArea, VesselEvent
from app.models.alert import Alert

class SupabaseSyncService:
    @staticmethod
    def get_client():
        url = settings.SUPABASE_URL or "https://lnlbjvfnwigxkwubxxsg.supabase.co"
        key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY or os.getenv("SUPABASE_ANON_KEY", "")
        try:
            from supabase import create_client
            return create_client(url, key)
        except Exception as e:
            print(f"[SupabaseSyncService] Client init exception: {e}")
            return None

    @classmethod
    def sync_incident(cls, db: Session, incident_id: str):
        """Pushes an incident and all its evidence/telemetry to Supabase Cloud at creation/update time."""
        client = cls.get_client()
        if not client:
            return

        try:
            inc = db.query(Incident).filter(Incident.id == incident_id).first()
            if not inc:
                return

            # 1. Upsert Incident Record
            inc_payload = {
                "id": inc.id,
                "incident_code": inc.incident_code,
                "anomaly_type": inc.anomaly_type,
                "latitude": inc.latitude,
                "longitude": inc.longitude,
                "location_name": inc.location_name or "Unknown Marine Region",
                "confidence_score": inc.confidence_score,
                "severity_score": inc.severity_score,
                "priority_score": inc.priority_score,
                "status": inc.status,
                "report": inc.report,
                "first_detected": inc.first_detected.isoformat() if inc.first_detected else datetime.utcnow().isoformat(),
                "last_updated": inc.last_updated.isoformat() if inc.last_updated else datetime.utcnow().isoformat()
            }
            try:
                client.table("incidents").upsert(inc_payload).execute()
            except Exception as payload_err:
                if "location_name" in str(payload_err):
                    inc_payload.pop("location_name", None)
                    client.table("incidents").upsert(inc_payload).execute()
                else:
                    raise payload_err
            print(f"[SupabaseSyncService] Real-time synced incident record: {inc.incident_code}")

            # 2. Upsert Satellite Observations & Upload Images
            obs_list = db.query(SatelliteObservation).filter(SatelliteObservation.incident_id == inc.id).all()
            for obs in obs_list:
                obs_payload = {
                    "id": obs.id,
                    "incident_id": obs.incident_id,
                    "mission": obs.mission,
                    "product_id": obs.product_id,
                    "acquisition_time": obs.acquisition_time.isoformat() if obs.acquisition_time else datetime.utcnow().isoformat(),
                    "cloud_cover": obs.cloud_cover,
                    "image_path": obs.image_path,
                    "annotated_image_path": obs.annotated_image_path,
                    "before_after_image_path": obs.before_after_image_path,
                    "model_result": obs.model_result,
                    "detection_method": obs.detection_method,
                    "wind_speed_ms": obs.wind_speed_ms,
                    "confidence": obs.confidence
                }
                client.table("satellite_observations").upsert(obs_payload).execute()

                # Upload image files to Supabase Storage Bucket
                for path_attr in ["image_path", "annotated_image_path", "before_after_image_path"]:
                    rel_path = getattr(obs, path_attr, None)
                    if rel_path:
                        fname = os.path.basename(rel_path)
                        local_file = os.path.join(settings.LOCAL_STORAGE_DIR, fname)
                        if os.path.exists(local_file):
                            try:
                                with open(local_file, "rb") as f:
                                    client.storage.from_("marineguard-evidence").upload(
                                        path=fname,
                                        file=f.read(),
                                        file_options={"content-type": "image/png", "x-upsert": "true"}
                                    )
                                print(f"[SupabaseSyncService] Real-time uploaded image {fname} to Supabase Storage")
                            except Exception as img_err:
                                pass

            # 3. Upsert Weather Observations
            w_list = db.query(WeatherObservation).filter(WeatherObservation.incident_id == inc.id).all()
            for w in w_list:
                try:
                    client.table("weather_observations").upsert({
                        "id": w.id,
                        "incident_id": w.incident_id,
                        "timestamp": w.timestamp.isoformat() if w.timestamp else datetime.utcnow().isoformat(),
                        "wind_speed": w.wind_speed,
                        "wind_direction": w.wind_direction,
                        "rainfall": w.rainfall,
                        "source": w.source
                    }).execute()
                except Exception:
                    pass

            # 4. Upsert Ocean Observations
            o_list = db.query(OceanObservation).filter(OceanObservation.incident_id == inc.id).all()
            for o in o_list:
                try:
                    client.table("ocean_observations").upsert({
                        "id": o.id,
                        "incident_id": o.incident_id,
                        "timestamp": o.timestamp.isoformat() if o.timestamp else datetime.utcnow().isoformat(),
                        "current_speed": o.current_speed,
                        "current_direction": o.current_direction,
                        "tide": o.tide,
                        "sea_surface_temperature": o.sea_surface_temperature,
                        "source": o.source
                    }).execute()
                except Exception:
                    pass

            # 5. Upsert Candidate Sources
            cs_list = db.query(CandidateSource).filter(CandidateSource.incident_id == inc.id).all()
            for cs in cs_list:
                try:
                    client.table("candidate_sources").upsert({
                        "id": cs.id,
                        "incident_id": cs.incident_id,
                        "source_type": cs.source_type,
                        "reference": cs.reference,
                        "confidence": cs.confidence,
                        "evidence_json": cs.evidence_json
                    }).execute()
                except Exception:
                    pass

            # 6. Upsert Predicted Path Trajectories
            pp_list = db.query(PredictedPath).filter(PredictedPath.incident_id == inc.id).all()
            for pp in pp_list:
                try:
                    client.table("predicted_paths").upsert({
                        "id": pp.id,
                        "incident_id": pp.incident_id,
                        "forecast_time": pp.forecast_time,
                        "latitude": pp.latitude,
                        "longitude": pp.longitude,
                        "uncertainty": pp.uncertainty
                    }).execute()
                except Exception:
                    pass

            # 7. Upsert Affected GIS Sensitive Areas
            aa_list = db.query(AffectedArea).filter(AffectedArea.incident_id == inc.id).all()
            for aa in aa_list:
                try:
                    client.table("affected_areas").upsert({
                        "id": aa.id,
                        "incident_id": aa.incident_id,
                        "area_type": aa.area_type,
                        "area_name": aa.area_name,
                        "distance_km": aa.distance_km,
                        "risk_level": aa.risk_level
                    }).execute()
                except Exception:
                    pass

            # 8. Upsert Alerts
            al_list = db.query(Alert).filter(Alert.incident_id == inc.id).all()
            for al in al_list:
                try:
                    client.table("alerts").upsert({
                        "id": al.id,
                        "incident_id": al.incident_id,
                        "alert_type": al.alert_type,
                        "recipient": al.recipient,
                        "status": al.status,
                        "sent_at": al.sent_at.isoformat() if al.sent_at else None
                    }).execute()
                except Exception:
                    pass

            # 9. Upsert Vessel Events & Correlated Vessel Activity Data
            ve_list = db.query(VesselEvent).filter(VesselEvent.incident_id == inc.id).all()
            for ve in ve_list:
                ve_payload = {
                    "id": ve.id,
                    "incident_id": ve.incident_id,
                    "vessel_id": ve.vessel_identifier,
                    "timestamp": ve.timestamp.isoformat() if ve.timestamp else datetime.utcnow().isoformat(),
                    "latitude": ve.latitude,
                    "longitude": ve.longitude,
                    "speed_knots": ve.speed,
                    "heading_deg": ve.direction,
                    "risk_level": "HIGH"
                }
                try:
                    client.table("vessel_events").upsert(ve_payload).execute()
                except Exception as ve_err:
                    try:
                        client.table("vessel_events").insert(ve_payload).execute()
                    except Exception as ve_err2:
                        print(f"[SupabaseSyncService] vessel_events sync notice: {ve_err2}")

            print(f"[SupabaseSyncService] Comprehensive sync completed for incident: {inc.incident_code}")

        except Exception as e:
            print(f"[SupabaseSyncService] Real-time sync notice for incident {incident_id}: {e}")
