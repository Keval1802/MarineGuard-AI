import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.vessel import AISPosition

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates Haversine distance in kilometers between two points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

class AISRepository:
    """
    AIS position storage & retrieval engine (Stage 9).
    """

    @classmethod
    def get_nearby_ais_positions(
        cls,
        db: Session,
        lat: float,
        lon: float,
        target_time: datetime,
        time_window_minutes: float = 30.0,
        max_distance_km: float = 10.0
    ) -> List[Dict[str, Any]]:
        """Queries database for AIS broadcasts within time window and spatial radius."""
        start_t = target_time - timedelta(minutes=time_window_minutes)
        end_t = target_time + timedelta(minutes=time_window_minutes)

        records = db.query(AISPosition).filter(
            AISPosition.timestamp >= start_t,
            AISPosition.timestamp <= end_t
        ).all()

        nearby = []
        for r in records:
            dist = haversine_km(lat, lon, r.latitude, r.longitude)
            if dist <= max_distance_km:
                dt_min = abs((r.timestamp - target_time).total_seconds()) / 60.0
                nearby.append({
                    "mmsi": r.mmsi,
                    "latitude": r.latitude,
                    "longitude": r.longitude,
                    "timestamp": r.timestamp.isoformat(),
                    "sog": r.sog,
                    "cog": r.cog,
                    "heading": r.heading,
                    "distance_km": round(dist, 3),
                    "time_diff_min": round(dt_min, 1)
                })

        return sorted(nearby, key=lambda x: x["distance_km"])

class SARToAISMatcher:
    """
    Spatio-temporal matcher linking SAR vessel detections to AIS broadcasts (Stage 10).
    Condition: time_difference <= 10 min AND distance <= 2.0 km.
    """

    @classmethod
    def match_sar_to_ais(
        cls,
        sar_detection: Dict[str, Any],
        ais_records: List[Dict[str, Any]],
        max_dist_km: float = 2.0,
        max_time_min: float = 10.0
    ) -> Optional[Dict[str, Any]]:
        """
        Matches a single SAR vessel detection target against nearby AIS broadcasts.
        """
        best_match = None
        min_dist = float("inf")

        for ais in ais_records:
            dist = ais.get("distance_km", haversine_km(
                sar_detection["latitude"], sar_detection["longitude"],
                ais["latitude"], ais["longitude"]
            ))
            time_diff = ais.get("time_diff_min", 0.0)

            if dist <= max_dist_km and time_diff <= max_time_min:
                if dist < min_dist:
                    min_dist = dist
                    best_match = {
                        "mmsi": ais["mmsi"],
                        "distance_km": round(dist, 3),
                        "time_difference_minutes": round(time_diff, 1),
                        "ais_latitude": ais["latitude"],
                        "ais_longitude": ais["longitude"],
                        "sog": ais.get("sog"),
                        "cog": ais.get("cog")
                    }

        return best_match
