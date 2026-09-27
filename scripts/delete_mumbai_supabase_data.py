"""
MarineGuard AI — Delete Mumbai Port & Juhu Incidents/Documents from Supabase Cloud & Local DB
"""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(project_root, "backend")
sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)

from app.config import settings
from app.database import SessionLocal
from app.models import Incident, SatelliteObservation
from supabase import create_client

def cleanup_mumbai_data():
    print("=" * 80)
    print("REMOVING ALL MUMBAI PORT & JUHU DATA FROM SUPABASE CLOUD & LOCAL DATABASE")
    print("=" * 80)

    url = settings.SUPABASE_URL
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY or os.getenv("SUPABASE_ANON_KEY", "")
    supabase = create_client(url, key)

    # 1. Query Mumbai / Juhu Incidents on Supabase Cloud
    print("\n[STEP 1] Querying Supabase Cloud 'incidents' table for Mumbai / Juhu entries...")
    inc_res = supabase.table("incidents").select("*").execute()
    all_incidents = inc_res.data or []
    
    mumbai_incidents = [
        inc for inc in all_incidents 
        if any(term in str(inc.get("location_name", "")).lower() for term in ["mumbai", "juhu", "jnpt", "bandra"])
        or any(term in str(inc.get("incident_code", "")).lower() for term in ["1895", "1910"])
    ]

    print(f"  Found {len(mumbai_incidents)} Mumbai incident(s) in Supabase Cloud:")
    for inc in mumbai_incidents:
        print(f"  -> Incident Code: {inc.get('incident_code')} | ID: {inc.get('id')} | Location: {inc.get('location_name')}")

    # 2. Delete Mumbai Satellite Observations & Evidence Images from Supabase Storage
    for inc in mumbai_incidents:
        inc_id = inc.get("id")
        code = inc.get("incident_code")

        # Delete satellite observations
        try:
            obs_res = supabase.table("satellite_observations").select("*").eq("incident_id", inc_id).execute()
            obs_items = obs_res.data or []
            print(f"\n  Deleting {len(obs_items)} satellite observation record(s) for {code}...")
            
            # Delete images from storage bucket
            for obs in obs_items:
                for img_key in ["image_path", "annotated_image_path", "before_after_image_path"]:
                    p = obs.get(img_key)
                    if p:
                        fname = os.path.basename(p)
                        try:
                            supabase.storage.from_("marineguard-evidence").remove([fname])
                            print(f"    [OK] Deleted Storage evidence file: {fname}")
                        except Exception as st_err:
                            print(f"    [NOTICE] Storage delete notice for {fname}: {st_err}")

            supabase.table("satellite_observations").delete().eq("incident_id", inc_id).execute()
        except Exception as err:
            print(f"  Notice deleting satellite observations for {code}: {err}")

        # Delete from incidents table
        try:
            supabase.table("incidents").delete().eq("id", inc_id).execute()
            print(f"  [OK] Deleted incident {code} ({inc_id}) from Supabase Cloud 'incidents' table.")
        except Exception as err:
            print(f"  Notice deleting incident {code}: {err}")

    # 3. Query & Delete Mumbai Location Documents from Supabase Cloud 'location_documents' table
    print("\n[STEP 2] Querying Supabase Cloud 'location_documents' table for Mumbai entries...")
    doc_res = supabase.table("location_documents").select("*").execute()
    all_docs = doc_res.data or []
    
    mumbai_docs = [
        doc for doc in all_docs
        if any(term in str(doc.get("location_name", "")).lower() for term in ["mumbai", "juhu", "jnpt", "bandra"])
    ]

    print(f"  Found {len(mumbai_docs)} Mumbai location document(s) in Supabase Cloud.")
    for doc in mumbai_docs:
        doc_id = doc.get("id")
        loc_name = doc.get("location_name")
        try:
            supabase.table("location_documents").delete().eq("id", doc_id).execute()
            print(f"  [OK] Deleted document ID: {doc_id} | Location: {loc_name}")
        except Exception as err:
            print(f"  Notice deleting location document {doc_id}: {err}")

    # 4. Clean local SQLite database
    print("\n[STEP 3] Cleaning local SQLite database...")
    db = SessionLocal()
    try:
        local_incs = db.query(Incident).all()
        to_del_incs = [
            inc for inc in local_incs 
            if any(term in str(inc.location_name or "").lower() for term in ["mumbai", "juhu", "jnpt", "bandra"])
            or any(term in str(inc.incident_code or "").lower() for term in ["1895", "1910"])
        ]
        for inc in to_del_incs:
            db.delete(inc)
            print(f"  [OK] Deleted local SQLite incident: {inc.incident_code}")
        
        db.commit()
    except Exception as db_err:
        print(f"  Local DB cleanup notice: {db_err}")
    finally:
        db.close()

    print("\n" + "=" * 80)
    print("MUMBAI PORT DATA CLEANUP COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    cleanup_mumbai_data()
