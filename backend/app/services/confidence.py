from typing import Dict, Any, List

class ConfidenceCalculator:
    """
    Deterministic Evidence and Confidence Model (Section 22).
    Combines weighted points across evidence sources (0 - 100 total scale):
    - Satellite primary evidence: 0 - 30 pts
    - Second-source evidence (optical + SAR co-observation): 0 - 20 pts
    - Citizen evidence: 0 - 10 pts
    - Vessel / context match: 0 - 15 pts
    - Environmental match (wind/current consistency): 0 - 15 pts
    - Historical consistency: 0 - 10 pts
    """

    @staticmethod
    def calculate_confidence(
        has_satellite: bool = True,
        satellite_model_conf: float = 0.70,
        has_second_satellite: bool = False,
        has_citizen_report: bool = False,
        has_vessel_match: bool = False,
        environmental_match: bool = True,
        has_historical_match: bool = False
    ) -> Dict[str, Any]:
        
        points = 0.0
        breakdown = {}

        # 1. Primary Satellite Evidence (0-30 pts)
        if has_satellite:
            sat_pts = round(min(30.0, satellite_model_conf * 30.0), 1)
            points += sat_pts
            breakdown["satellite_primary"] = sat_pts

        # 2. Second Satellite Co-Observation (0-20 pts)
        if has_second_satellite:
            points += 20.0
            breakdown["satellite_secondary"] = 20.0
        else:
            breakdown["satellite_secondary"] = 0.0

        # 3. Citizen Report Evidence (0-10 pts)
        if has_citizen_report:
            points += 10.0
            breakdown["citizen_report"] = 10.0
        else:
            breakdown["citizen_report"] = 0.0

        # 4. Vessel / Activity Match (0-15 pts)
        if has_vessel_match:
            points += 15.0
            breakdown["vessel_context"] = 15.0
        else:
            breakdown["vessel_context"] = 0.0

        # 5. Environmental Match (0-15 pts)
        if environmental_match:
            points += 15.0
            breakdown["environmental_match"] = 15.0
        else:
            breakdown["environmental_match"] = 0.0

        # 6. Historical Consistency (0-10 pts)
        if has_historical_match:
            points += 10.0
            breakdown["historical_consistency"] = 10.0
        else:
            breakdown["historical_consistency"] = 0.0

        total_score = min(100.0, round(points, 1))

        # Thresholds (Section 22)
        if total_score < 30.0:
            level = "LOW"
        elif total_score < 50.0:
            level = "MODERATE"
        elif total_score < 75.0:
            level = "HIGH"
        else:
            level = "VERY HIGH"

        return {
            "confidence_score": total_score,
            "confidence_level": level,
            "breakdown_points": breakdown
        }
