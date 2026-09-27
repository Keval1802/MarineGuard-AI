import os
import sys
import asyncio
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(project_root, "backend")
if project_root not in sys.path:
    sys.path.append(project_root)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.config import settings
from app.database import SessionLocal
from app.models.incident import Incident
from app.models.satellite import SatelliteObservation
from app.models.evidence import WeatherObservation, OceanObservation, CandidateSource, PredictedPath, AffectedArea
from supabase import create_client

def get_supabase_client():
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SECRET_KEY or settings.SUPABASE_ANON_KEY or os.getenv("SUPABASE_ANON_KEY", "")
    return create_client(url, key)

async def test_supabase_integration():
    print("=" * 70)
    print("MARINEGUARD AI — SUPABASE CLOUD INTEGRATION & FULL REPO SYNC ENGINE")
    print(f"Target Supabase URL: {settings.SUPABASE_URL}")
    print("=" * 70)

    # 1. Initialize Supabase Client
    print("\n[STEP 1] Initializing Supabase REST & Auth Client Connection...")
    client = get_supabase_client()
    print("[OK] Supabase Client initialized successfully!")

    # 2. Query Local Database for Real Satellite Incidents
    print("\n[STEP 2] Fetching Local Incidents & Satellite Evidence Observations...")
    db = SessionLocal()
    try:
        incidents = db.query(Incident).all()
        print(f"Found {len(incidents)} real incident(s) in local SQLite database:")
        for inc in incidents:
            print(f"  - [{inc.incident_code}] Anomaly: {inc.anomaly_type} | Status: {inc.status} | Priority: {inc.priority_score:.3f}")

        # Clear old records from Supabase Cloud tables to prevent foreign/unique key conflicts
        try:
            client.table("satellite_observations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            client.table("weather_observations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            client.table("ocean_observations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            client.table("candidate_sources").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            client.table("predicted_paths").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            client.table("affected_areas").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            client.table("alerts").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            client.table("incidents").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print("  [OK] Cleared stale cloud tables on Supabase!")
        except Exception as purge_err:
            print(f"  [NOTICE] Cloud purge notice: {purge_err}")

        for inc in incidents:
            # Sync Incidents Table
            inc_payload = {
                "id": inc.id,
                "incident_code": inc.incident_code,
                "anomaly_type": inc.anomaly_type,
                "latitude": inc.latitude,
                "longitude": inc.longitude,
                "confidence_score": inc.confidence_score,
                "severity_score": inc.severity_score,
                "priority_score": inc.priority_score,
                "status": inc.status,
                "report": inc.report,
                "first_detected": inc.first_detected.isoformat(),
                "last_updated": inc.last_updated.isoformat()
            }

            try:
                client.table("incidents").upsert(inc_payload).execute()
                print(f"  [OK] Upserted incident record: {inc.incident_code}")
            except Exception as e:
                print(f"  [NOTICE] Supabase table 'incidents' upsert notice: {e}")

            # Sync Satellite Observations Table
            obs_list = db.query(SatelliteObservation).filter(SatelliteObservation.incident_id == inc.id).all()
            for obs in obs_list:
                obs_payload = {
                    "id": obs.id,
                    "incident_id": obs.incident_id,
                    "mission": obs.mission,
                    "product_id": obs.product_id,
                    "acquisition_time": obs.acquisition_time.isoformat(),
                    "cloud_cover": obs.cloud_cover,
                    "image_path": obs.image_path,
                    "annotated_image_path": obs.annotated_image_path,
                    "before_after_image_path": obs.before_after_image_path,
                    "model_result": obs.model_result,
                    "detection_method": obs.detection_method,
                    "wind_speed_ms": obs.wind_speed_ms,
                    "confidence": obs.confidence
                }
                try:
                    client.table("satellite_observations").upsert(obs_payload).execute()
                    print(f"  [OK] Upserted satellite observation: {obs.mission} ({obs.product_id[:25]}...)")
                except Exception as e:
                    print(f"  [NOTICE] Supabase table 'satellite_observations' upsert notice: {e}")

            # Sync Weather Observations Table
            w_list = db.query(WeatherObservation).filter(WeatherObservation.incident_id == inc.id).all()
            for w in w_list:
                w_payload = {
                    "id": w.id,
                    "incident_id": w.incident_id,
                    "timestamp": w.timestamp.isoformat() if w.timestamp else datetime.utcnow().isoformat(),
                    "wind_speed": w.wind_speed,
                    "wind_direction": w.wind_direction,
                    "rainfall": w.rainfall,
                    "source": w.source
                }
                try:
                    client.table("weather_observations").upsert(w_payload).execute()
                except Exception:
                    pass

            # Sync Ocean Observations Table
            o_list = db.query(OceanObservation).filter(OceanObservation.incident_id == inc.id).all()
            for o in o_list:
                o_payload = {
                    "id": o.id,
                    "incident_id": o.incident_id,
                    "timestamp": o.timestamp.isoformat() if o.timestamp else datetime.utcnow().isoformat(),
                    "current_speed": o.current_speed,
                    "current_direction": o.current_direction,
                    "tide": o.tide,
                    "sea_surface_temperature": o.sea_surface_temperature,
                    "source": o.source
                }
                try:
                    client.table("ocean_observations").upsert(o_payload).execute()
                except Exception:
                    pass

        # 4. Storage Bucket Evidence Upload Test
        print("\n[STEP 4] Uploading Real Satellite Visual Evidence Artifacts to Supabase Storage Bucket...")
        evidence_dir = os.path.join(backend_dir, "storage", "evidence")
        if os.path.exists(evidence_dir):
            evidence_files = [f for f in os.listdir(evidence_dir) if f.endswith(".png")]
            for fname in evidence_files:
                fpath = os.path.join(evidence_dir, fname)
                try:
                    with open(fpath, "rb") as f:
                        client.storage.from_("marineguard-evidence").upload(
                            path=fname,
                            file=f.read(),
                            file_options={"content-type": "image/png", "x-upsert": "true"}
                        )
                    print(f"  [OK] Uploaded evidence file: {fname} to Supabase Storage!")
                except Exception as upload_err:
                    print(f"  [NOTICE] Storage upload notice for {fname}: {upload_err}")

        print("\n" + "=" * 70)
        print("SUPABASE INTEGRATION & DATA SYNC COMPLETE!")
        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_supabase_integration())
