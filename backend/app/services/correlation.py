import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from app.ais.matcher import haversine_km

class SpillVesselCorrelator:
    """
    Oil Slick to Vessel Track Correlation Engine (Stages 12, 13, 14).
    Correlates satellite-detected oil slick polygons with candidate vessel AIS tracks.
    """

    @staticmethod
    def calculate_heading_difference(heading1: float, heading2: float) -> float:
        """Calculates minimum angular difference (0 to 180 degrees) between two headings."""
        diff = abs(heading1 - heading2) % 360.0
        return diff if diff <= 180.0 else 360.0 - diff

    @classmethod
    def correlate_vessel_track_to_slick(
        cls,
        slick: Dict[str, Any],
        vessel_identity: Dict[str, Any],
        vessel_track: List[Dict[str, Any]],
        lookback_hours: float = 6.0
    ) -> Dict[str, Any]:
        """
        Correlates a candidate vessel's historical AIS track against an oil slick polygon/centroid.

        slick: {
            "id": "OIL-0092",
            "centroid_lat": 21.349,
            "centroid_lon": 72.520,
            "area_km2": 2.8,
            "orientation": 201.0,  # slick long-axis orientation in degrees
            "acquisition_time": "2026-09-26T05:37:12Z"
        }
        """
        acq_time = datetime.fromisoformat(slick["acquisition_time"].replace("Z", "+00:00")).replace(tzinfo=None)
        start_time = acq_time - timedelta(hours=lookback_hours)

        slick_lat = slick["centroid_lat"]
        slick_lon = slick["centroid_lon"]
        slick_orient = slick.get("orientation", 0.0)

        min_dist_km = float("inf")
        best_point = None

        for pt in vessel_track:
            pt_time = datetime.fromisoformat(pt["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None)
            if start_time <= pt_time <= acq_time:
                dist = haversine_km(slick_lat, slick_lon, pt["latitude"], pt["longitude"])
                if dist < min_dist_km:
                    min_dist_km = dist
                    best_point = pt

        if not best_point:
            # Fallback to closest point regardless of strict window
            for pt in vessel_track:
                dist = haversine_km(slick_lat, slick_lon, pt["latitude"], pt["longitude"])
                if dist < min_dist_km:
                    min_dist_km = dist
                    best_point = pt

        # Calculate feature metrics (Stage 13)
        time_diff_min = 999.0
        heading_diff = 180.0
        vessel_cog = 0.0

        if best_point:
            best_time = datetime.fromisoformat(best_point["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None)
            time_diff_min = abs((acq_time - best_time).total_seconds()) / 60.0
            vessel_cog = best_point.get("cog") or best_point.get("heading") or 0.0
            heading_diff = cls.calculate_heading_difference(vessel_cog, slick_orient)

        vessel_type = (vessel_identity.get("ship_type") or "").upper()
        track_intersects = min_dist_km <= (math.sqrt(slick.get("area_km2", 1.0)) * 0.5 + 0.5)

        # Build correlation score (Stage 14)
        score = 0
        
        # Distance feature (< 2 km)
        if min_dist_km < 2.0:
            score += 30
        elif min_dist_km < 5.0:
            score += 15

        # Time feature (< 60 minutes prior to imagery capture)
        if time_diff_min < 60.0:
            score += 20
        elif time_diff_min < 180.0:
            score += 10

        # Orientation feature (Vessel COG vs slick long-axis orientation < 20 deg)
        if heading_diff < 20.0:
            score += 20
        elif heading_diff < 40.0:
            score += 10

        # Vessel type risk factor (Tankers / Bunkers / Cargo)
        if any(t in vessel_type for t in ["TANKER", "BUNKER", "CARGO"]):
            score += 10

        # Direct spatial intersection
        if track_intersects:
            score += 20

        final_score = min(100, score)

        return {
            "slick_id": slick.get("id", "OIL-SLICK-01"),
            "mmsi": str(vessel_identity.get("mmsi")),
            "ship_name": vessel_identity.get("ship_name"),
            "ship_type": vessel_type,
            "minimum_distance_km": round(float(min_dist_km), 3),
            "time_difference_minutes": round(float(time_diff_min), 1),
            "heading_difference_deg": round(float(heading_diff), 1),
            "vessel_cog_deg": round(float(vessel_cog), 1),
            "slick_orientation_deg": round(float(slick_orient), 1),
            "correlation_score": final_score,
            "label": "Vessel associated with spill candidate",
            "disclaimer": "Satellite/AIS correlation is evidence for investigation; it does not by itself establish legal responsibility."
        }
