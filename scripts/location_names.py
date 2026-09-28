import os
import sys
from datetime import datetime

# Add project root and backend to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.database import SessionLocal
from app.models.incident import Incident
from app.environmental.gis import GISService
from app.services.supabase_service import SupabaseSyncService

def ensure_human_location_names():
    """
    Script to ensure all incidents in local DB and Supabase Cloud store human-memorable
    location names
    retrieved from Supabase 'location_documents' table / GIS service, rather than coordinates or generic strings.
    """
    print("=" * 80)
    print("      MARINEGUARD AI — ENSURE HUMAN MEMORABLE LOCATION NAMES SCRIPT")
    print("=" * 80)

    db = SessionLocal()
    supabase_client = SupabaseSyncService.get_client()

    # 1. Fetch location_documents from Supabase Cloud
    loc_docs = []
    if supabase_client:
        try:
            res = supabase_client.table("location_documents").select("location_name, latitude, longitude").execute()
            if res and res.data:
                loc_docs = res.data
                print(f"[+] Loaded {len(loc_docs)} reference location document(s) from Supabase Cloud.")
        except Exception as e:
            print(f"[!] Warning fetching location_documents from Supabase: {e}")

    # Helper function to find best location name
    def resolve_location(lat: float, lon: float, curr_name: str) -> str:
        # A. Check Supabase location_documents table for nearest match (< 50 km)
        best_name = None
        min_dist = 50.0 # km
        for doc in loc_docs:
            d_lat = doc.get("latitude")
            d_lon = doc.get("longitude")
            l_name = doc.get("location_name")
            if d_lat is not None and d_lon is not None and l_name:
                if "Sector (" not in l_name and "Offshore Sector" not in l_name and "Unknown" not in l_name:
                    dist = GISService.haversine_distance(lat, lon, d_lat, d_lon)
                    if dist < min_dist:
                        min_dist = dist
                        best_name = l_name
        if best_name:
            return best_name

        # B. GIS Service lookup
        gis_name = GISService.get_location_name(lat, lon)
        if gis_name and "Offshore Sector (" not in gis_name:
            return gis_name

        # C. Return cleaned current name if acceptable, else generic fallback
        if curr_name and curr_name != "Unknown Marine Region" and "Sector (" not in curr_name:
            return curr_name

        return gis_name

    # 2. Fetch and update local DB incidents
    incidents = db.query(Incident).all()
    print(f"\nScanning {len(incidents)} incident records in local database...\n")

    updated_count = 0
    for inc in incidents:
        old_name = inc.location_name
        resolved_name = resolve_location(inc.latitude, inc.longitude, old_name)

        is_invalid = (
            not old_name or 
            old_name == "Unknown Marine Region" or 
            "Coastal Sector (" in old_name or 
            "Offshore Sector (" in old_name or
            "°N" in old_name or
            "° N" in old_name
        )

        if is_invalid or old_name != resolved_name:
            inc.location_name = resolved_name
            updated_count += 1
            print(f"  [UPDATED] Incident {inc.incident_code} ({inc.latitude:.3f}° N, {inc.longitude:.3f}° E)")
            print(f"            Previous Name : {old_name}")
            print(f"            New Human Name: {resolved_name}\n")

            # 3. Sync update to Supabase Cloud if available
            if supabase_client:
                try:
                    SupabaseSyncService.sync_incident(db, inc.id)
                except Exception as sync_err:
                    print(f"            [!] Supabase sync error for {inc.incident_code}: {sync_err}")

    db.commit()
    db.close()

    print("=" * 80)
    print(f"SUCCESS: Finished processing. Updated {updated_count} incident location name(s).")
    print("=" * 80)

if __name__ == "__main__":
    ensure_human_location_names()
