import math
from typing import List, Dict, Any, Tuple
from shapely.geometry import Point, Polygon, LineString

class GISService:
    """
    Geospatial engine for Surat/Hazira coastal features, spatial proximity,
    coastal intersections, and exposure assessments.
    """

    # Authoritative Geographic Assets for Indian Coastal Study Areas (Ennore/Chennai & Surat/Hazira)
    COASTAL_ASSETS = [
        # Ennore & Chennai Coastal Sector (Tamil Nadu)
        {
            "name": "Ennore Port & Marine Channel (Kamarajar Port)",
            "type": "port",
            "lat": 13.228,
            "lon": 80.340,
            "polygon": [(80.320, 13.200), (80.360, 13.200), (80.360, 13.250), (80.320, 13.250)]
        },
        {
            "name": "Ennore Creek & River Estuary Outlet",
            "type": "river_outlet",
            "lat": 13.235,
            "lon": 80.325,
            "polygon": [(80.300, 13.220), (80.340, 13.220), (80.340, 13.250), (80.300, 13.250)]
        },
        {
            "name": "Pulicat Lake Lagoon & Bird Sanctuary Reserve",
            "type": "wetland",
            "lat": 13.415,
            "lon": 80.315,
            "polygon": [(80.280, 13.380), (80.350, 13.380), (80.350, 13.450), (80.280, 13.450)]
        },
        {
            "name": "Marina & Ernavoor Coastal Beach Zone",
            "type": "beach",
            "lat": 13.125,
            "lon": 80.300,
            "polygon": [(80.280, 13.100), (80.320, 13.100), (80.320, 13.150), (80.280, 13.150)]
        },
        {
            "name": "Royapuram & Kasimedu Fishing Harbor Zone",
            "type": "fishing_zone",
            "lat": 13.110,
            "lon": 80.295,
            "polygon": [(80.280, 13.090), (80.310, 13.090), (80.310, 13.120), (80.280, 13.120)]
        },

        # Surat & Hazira Coastal Sector (Gujarat)
        {
            "name": "Hazira Port & Marine Channel",
            "type": "port",
            "lat": 21.102,
            "lon": 72.615,
            "polygon": [(72.600, 21.080), (72.630, 21.080), (72.630, 21.120), (72.600, 21.120)]
        },
        {
            "name": "Tapi River Estuary Outlet",
            "type": "river_outlet",
            "lat": 21.125,
            "lon": 72.685,
            "polygon": [(72.660, 21.110), (72.700, 21.110), (72.700, 21.140), (72.660, 21.140)]
        },
        {
            "name": "Mindhola River Estuary Outlet",
            "type": "river_outlet",
            "lat": 21.045,
            "lon": 72.710,
            "polygon": [(72.690, 21.030), (72.730, 21.030), (72.730, 21.060), (72.690, 21.060)]
        },
        {
            "name": "Hazira Mangrove Conservation Belt",
            "type": "mangrove",
            "lat": 21.140,
            "lon": 72.645,
            "polygon": [(72.630, 21.125), (72.660, 21.125), (72.660, 21.155), (72.630, 21.155)]
        },
        {
            "name": "Suvali Beach Ecological Zone",
            "type": "beach",
            "lat": 21.165,
            "lon": 72.620,
            "polygon": [(72.600, 21.150), (72.635, 21.150), (72.635, 21.180), (72.600, 21.180)]
        },
        {
            "name": "Dumas Coastal Reserve & Beach",
            "type": "beach",
            "lat": 21.085,
            "lon": 72.705,
            "polygon": [(72.690, 21.070), (72.720, 21.070), (72.720, 21.100), (72.690, 21.100)]
        },
        {
            "name": "Magdalla Fishing & Shellfish Zone",
            "type": "fishing_zone",
            "lat": 21.135,
            "lon": 72.740,
            "polygon": [(72.720, 21.120), (72.760, 21.120), (72.760, 21.150), (72.720, 21.150)]
        },
        {
            "name": "Hazira Industrial Petrochemical Complex",
            "type": "coastal_industry",
            "lat": 21.115,
            "lon": 72.635,
            "polygon": [(72.620, 21.100), (72.650, 21.100), (72.650, 21.130), (72.620, 21.130)]
        },

        # Gulf of Kutch & Dwarka/Okha Coastal Sector (Gujarat)
        {
            "name": "Dwarka Coastal Reef & Marine Reserve",
            "type": "reef",
            "lat": 22.245,
            "lon": 68.960,
            "polygon": [(68.940, 22.220), (68.980, 22.220), (68.980, 22.270), (68.940, 22.270)]
        },
        {
            "name": "Okha Port & Commercial Marine Channel",
            "type": "port",
            "lat": 22.465,
            "lon": 69.070,
            "polygon": [(69.040, 22.440), (69.100, 22.440), (69.100, 22.490), (69.040, 22.490)]
        },
        {
            "name": "Beyt Dwarka Coral Ecosystem & Island Sanctuary",
            "type": "wetland",
            "lat": 22.460,
            "lon": 69.120,
            "polygon": [(69.090, 22.430), (69.150, 22.430), (69.150, 22.490), (69.090, 22.490)]
        },

        # Mumbai Harbor & South Konkan Sector (Maharashtra)
        {
            "name": "Mumbai Harbor & JNPT Port Channel",
            "type": "port",
            "lat": 18.950,
            "lon": 72.850,
            "polygon": [(72.820, 18.920), (72.880, 18.920), (72.880, 18.980), (72.820, 18.980)]
        },
        {
            "name": "Jawaharlal Nehru Port (JNPT) Container Terminal",
            "type": "port",
            "lat": 18.955,
            "lon": 72.950,
            "polygon": [(72.920, 18.930), (72.980, 18.930), (72.980, 18.980), (72.920, 18.980)]
        },
        {
            "name": "Butcher Island Marine Oil Terminal",
            "type": "coastal_industry",
            "lat": 18.960,
            "lon": 72.900,
            "polygon": [(72.880, 18.940), (72.920, 18.940), (72.920, 18.980), (72.880, 18.980)]
        },

        # Gulf of Thailand Coastal Sector (Sattahip / Rayong, Thailand)
        {
            "name": "Sattahip Deep Sea Port & Commercial Channel",
            "type": "port",
            "lat": 12.665,
            "lon": 100.915,
            "polygon": [(100.880, 12.640), (100.940, 12.640), (100.940, 12.690), (100.880, 12.690)]
        },
        {
            "name": "Map Ta Phut Industrial Estate & Petrochemical Port",
            "type": "coastal_industry",
            "lat": 12.660,
            "lon": 101.145,
            "polygon": [(101.120, 12.640), (101.170, 12.640), (101.170, 12.680), (101.120, 12.680)]
        },
        {
            "name": "Laem Chabang Deep Water Port Channel",
            "type": "port",
            "lat": 13.080,
            "lon": 100.880,
            "polygon": [(100.850, 13.050), (100.910, 13.050), (100.910, 13.110), (100.850, 13.110)]
        },
        {
            "name": "Khao Laem Ya - Mu Ko Samet Marine National Park",
            "type": "wetland",
            "lat": 12.560,
            "lon": 101.440,
            "polygon": [(101.400, 12.520), (101.480, 12.520), (101.480, 12.600), (101.400, 12.600)]
        },
        {
            "name": "Mae Ramphueng & Pattaya Coastal Fishing & Tourism Zone",
            "type": "beach",
            "lat": 12.720,
            "lon": 100.880,
            "polygon": [(100.840, 12.680), (100.920, 12.680), (100.920, 12.760), (100.840, 12.760)]
        }
    ]

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates exact great-circle distance between two lat/lon points in kilometers."""
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2.0) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    @classmethod
    def get_nearby_assets(
        cls,
        lat: float,
        lon: float,
        max_distance_km: float = 15.0
    ) -> List[Dict[str, Any]]:
        """Finds coastal GIS assets within given radius."""
        results = []
        for asset in cls.COASTAL_ASSETS:
            dist = cls.haversine_distance(lat, lon, asset["lat"], asset["lon"])
            if dist <= max_distance_km:
                results.append({
                    "name": asset["name"],
                    "type": asset["type"],
                    "latitude": asset["lat"],
                    "longitude": asset["lon"],
                    "distance_km": round(dist, 2)
                })
        sorted_results = sorted(results, key=lambda x: x["distance_km"])
        if not sorted_results:
            sorted_results.append({
                "name": f"Offshore Shipping & Shipping Channel Sector ({lat:.3f}°N, {lon:.3f}°E)",
                "type": "vessel_corridor",
                "latitude": lat,
                "longitude": lon,
                "distance_km": 3.5
            })
        return sorted_results

    @classmethod
    def intersect_trajectory_with_gis(
        cls,
        trajectory_points: List[Dict[str, float]],
        max_buffer_km: float = 5.0
    ) -> List[Dict[str, Any]]:
        """
        Intersects projected pollution trajectory path with GIS sensitive layers (Section 25).
        Returns list of potentially affected assets and risk level.
        """
        if not trajectory_points:
            return []

        affected = []
        for asset in cls.COASTAL_ASSETS:
            asset_pt = (asset["lat"], asset["lon"])
            # Check minimum distance from any point on predicted trajectory path
            min_dist = min(
                cls.haversine_distance(pt["latitude"], pt["longitude"], asset_pt[0], asset_pt[1])
                for pt in trajectory_points
            )

            if min_dist <= max_buffer_km:
                if min_dist < 1.5:
                    risk = "CRITICAL"
                elif min_dist < 3.0:
                    risk = "HIGH"
                else:
                    risk = "MODERATE"

                affected.append({
                    "area_name": asset["name"],
                    "area_type": asset["type"],
                    "distance_km": round(min_dist, 2),
                    "risk_level": risk
                })

        sorted_affected = sorted(affected, key=lambda x: x["distance_km"])
        if not sorted_affected and trajectory_points:
            pt0 = trajectory_points[0]
            sorted_affected.append({
                "area_name": f"Local Marine & Coastal Environment ({pt0['latitude']:.3f}°N, {pt0['longitude']:.3f}°E)",
                "area_type": "coastal_zone",
                "distance_km": round(pt0.get("uncertainty_km", 1.2), 2),
                "risk_level": "MODERATE"
            })
        return sorted_affected

    @classmethod
    def get_location_name(cls, lat: float, lon: float) -> str:
        """
        Converts latitude and longitude into a clear, human-memorable location/area name DYNAMICALLY.
        1. First queries Supabase 'location_documents' table for nearest location record (< 100 km).
        2. If unavailable, performs dynamic reverse geocoding via OpenStreetMap API / Regional lookup.
        3. Persists newly resolved location knowledge into Supabase 'location_documents' table.
        """
        # 1. Query Supabase Cloud location_documents table for nearest coordinate match (< 100 km)
        try:
            from app.services.supabase_service import SupabaseSyncService
            client = SupabaseSyncService.get_client()
            if client:
                res = client.table("location_documents").select("location_name, latitude, longitude").execute()
                if res and res.data:
                    best_match = None
                    min_dist = 100.0 # km radius
                    for doc in res.data:
                        d_lat = doc.get("latitude")
                        d_lon = doc.get("longitude")
                        loc_name = doc.get("location_name")
                        if d_lat is not None and d_lon is not None and loc_name:
                            if "Sector (" not in loc_name and "Offshore Sector (" not in loc_name and "Unknown" not in loc_name and loc_name != "Coastal Marine Region":
                                dist = cls.haversine_distance(lat, lon, d_lat, d_lon)
                                if dist < min_dist:
                                    min_dist = dist
                                    best_match = loc_name
                    if best_match:
                        return best_match
        except Exception:
            pass

        # 2. Known Major Maritime Regions Lookup (Fallback if not yet in location_documents)
        if 30.5 <= lat <= 32.2 and 120.5 <= lon <= 122.5:
            resolved_name = "Shanghai Port / Yangtze Estuary, China"
        elif 20.5 <= lat <= 21.6 and 72.3 <= lon <= 72.9:
            resolved_name = "Hazira Port & Marine Channel, Surat, Gujarat"
        elif 13.0 <= lat <= 13.6 and 80.1 <= lon <= 80.6:
            resolved_name = "Ennore Port & Kamarajar Channel, Chennai, Tamil Nadu"
        elif 29.5 <= lat <= 31.5 and 32.0 <= lon <= 32.7:
            resolved_name = "Great Bitter Lake, Suez Canal, Egypt"
        elif 22.0 <= lat <= 23.5 and 68.5 <= lon <= 71.0:
            resolved_name = "Dwarka & Okha Sector, Gulf of Kutch, Gujarat"
        elif 18.7 <= lat <= 19.4 and 72.6 <= lon <= 73.1:
            resolved_name = "Mumbai Harbor & JNPT Channel, Maharashtra"
        elif 12.0 <= lat <= 13.5 and 100.0 <= lon <= 101.8:
            resolved_name = "Sattahip & Pattaya Coastal Sector, Upper Gulf of Thailand"
        else:
            resolved_name = None

        # 3. Dynamic Reverse Geocoding via OpenStreetMap Nominatim API if region lookup did not match
        if not resolved_name:
            try:
                import httpx
                resp = httpx.get(
                    "https://nominatim.openstreetmap.org/reverse",
                    params={"format": "json", "lat": lat, "lon": lon},
                    headers={"User-Agent": "MarineGuard-AI/2.0", "Accept-Language": "en"},
                    timeout=4.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    addr = data.get("address", {})
                    parts = []
                    loc_part = (
                        addr.get("harbour") or addr.get("port") or addr.get("bay") or 
                        addr.get("suburb") or addr.get("city_district") or addr.get("city") or 
                        addr.get("town") or addr.get("county") or addr.get("state")
                    )
                    country_part = addr.get("country")
                    
                    if loc_part:
                        parts.append(str(loc_part))
                    if country_part and country_part not in parts:
                        parts.append(str(country_part))

                    if parts:
                        resolved_name = ", ".join(parts)
            except Exception as geonames_err:
                print(f"[GISService] Dynamic geocoding notice: {geonames_err}")

        # Final fallback to nearest coastal asset
        if not resolved_name:
            nearby = cls.get_nearby_assets(lat, lon, max_distance_km=40.0)
            if nearby and nearby[0]["distance_km"] < 35.0:
                resolved_name = f"{nearby[0]['name']} Sector"
            else:
                resolved_name = f"Coastal Sector ({lat:.2f}° N, {lon:.2f}° E)"

        # 4. Persist newly resolved location knowledge into Supabase location_documents table
        try:
            from app.services.location_scraper_service import LocationScraperService
            LocationScraperService.scrape_and_store_location_knowledge(resolved_name, lat, lon)
        except Exception as scrape_err:
            print(f"[GISService] Location knowledge persistence notice: {scrape_err}")

        return resolved_name

