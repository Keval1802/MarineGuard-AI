from typing import Dict, Any, List
from app.environmental.gis import GISService

class RiskCalculator:
    """
    Deterministic Risk and Priority Scoring Model (Section 26).
    Enforces normalized 0-1 inputs and exact weighted priority formula:
    priority_score = (
        confidence_norm * 0.25
        + severity_score * 0.25
        + coastal_impact_score * 0.20
        + ecosystem_score * 0.20
        + human_exposure_score * 0.10
    )
    """

    @classmethod
    def calculate_risk(
        cls,
        confidence_score: float,
        anomaly_type: str,
        estimated_area_km2: float,
        latitude: float,
        longitude: float,
        trajectory_points: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        
        # 1. Normalized Confidence (0 - 1)
        confidence_norm = max(0.0, min(1.0, confidence_score / 100.0))

        # 2. Severity Score (0 - 1)
        base_severity_map = {
            "OIL_LIKE_ANOMALY": 0.65,
            "HIGH_TURBIDITY_EVENT": 0.20,
            "FLOATING_MATERIAL_CANDIDATE": 0.45,
            "SURFACE_ANOMALY": 0.35,
            "FALSE_POSITIVE": 0.05,
            "UNKNOWN": 0.25
        }
        base_sev = base_severity_map.get(anomaly_type, 0.25)
        # Scale up severity with estimated area (up to max 10 km2 area factor)
        area_factor = min(0.35, (estimated_area_km2 / 10.0) * 0.35)
        severity_score = min(1.0, round(base_sev + area_factor, 2))

        # 3. GIS Nearby Asset Intersections & Biodiversity Sites
        nearby_assets = GISService.get_nearby_assets(latitude, longitude, max_distance_km=20.0)
        trajectory_intersections = GISService.intersect_trajectory_with_gis(trajectory_points, max_buffer_km=15.0)

        # Distance to coast calculation
        nearest_dist_km = nearby_assets[0]["distance_km"] if nearby_assets else 15.0
        max_dist_km = 20.0
        coastal_impact_score = max(0.0, min(1.0, round(1.0 - (nearest_dist_km / max_dist_km), 2)))

        # Fetch biodiversity protected sites
        from app.services.biodiversity_service import BiodiversityService
        bio_data = BiodiversityService.get_biodiversity_exposure(latitude, longitude, trajectory_points)
        bio_sites = bio_data.get("protected_sites", [])

        # Ecosystem score (mangroves, beaches, wetlands, protected reserves)
        eco_distances = []
        for a in trajectory_intersections + nearby_assets:
            if a.get("area_type") in ["mangrove", "beach", "wetland", "estuary", "river_outlet"]:
                eco_distances.append(a["distance_km"])
        for st in bio_sites:
            if "distance_km" in st:
                eco_distances.append(st["distance_km"])

        if eco_distances:
            closest_eco = min(eco_distances)
            ecosystem_score = max(0.10, min(1.0, round(1.0 - (closest_eco / 15.0), 2)))
        else:
            ecosystem_score = 0.10

        # Human exposure score (ports, fishing zones, coastal settlements, industrial channels)
        human_distances = []
        for a in trajectory_intersections + nearby_assets:
            if a.get("area_type") in ["port", "fishing_zone", "coastal_industry", "channel", "river_outlet"]:
                human_distances.append(a["distance_km"])

        if human_distances:
            closest_human = min(human_distances)
            human_exposure_score = max(0.10, min(1.0, round(1.0 - (closest_human / 15.0), 2)))
        else:
            human_exposure_score = 0.10

        # 4. Weighted Priority Score Formula (Section 26)
        priority_score = (
            confidence_norm * 0.25 +
            severity_score * 0.25 +
            coastal_impact_score * 0.20 +
            ecosystem_score * 0.20 +
            human_exposure_score * 0.10
        )
        priority_score = round(max(0.0, min(1.0, priority_score)), 3)

        # Risk Classification & Non-Hazardous Event Priority Capping
        if anomaly_type in ["HIGH_TURBIDITY_EVENT", "FALSE_POSITIVE", "NORMAL"]:
            priority_score = min(priority_score, 0.350)
            level = "LOW" if anomaly_type == "FALSE_POSITIVE" else "MODERATE"
        else:
            if priority_score < 0.30:
                level = "LOW"
            elif priority_score < 0.50:
                level = "MODERATE"
            elif priority_score < 0.75:
                level = "HIGH"
            else:
                level = "CRITICAL"

        return {
            "priority_score": priority_score,
            "risk_level": level,
            "confidence_norm": confidence_norm,
            "severity_score": severity_score,
            "base_severity": base_sev,
            "area_factor": area_factor,
            "coastal_impact_score": coastal_impact_score,
            "ecosystem_score": ecosystem_score,
            "human_exposure_score": human_exposure_score,
            "nearest_coast_distance_km": nearest_dist_km,
            "affected_areas": trajectory_intersections
        }
