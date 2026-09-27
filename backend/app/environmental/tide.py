from datetime import datetime
from typing import Dict, Any, Optional

class TideService:
    """
    Calculates semi-diurnal tide status for Surat / Gulf of Khambhat coastal waters.
    Gulf of Khambhat exhibits one of India's highest tidal ranges (~8-10 meters).
    """

    @staticmethod
    def get_tide_status(timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        if not timestamp:
            timestamp = datetime.utcnow()

        # Semi-diurnal cycle (~12.42 hours)
        hours = timestamp.hour + timestamp.minute / 60.0
        cycle_phase = (hours % 12.42) / 12.42

        if cycle_phase < 0.15 or cycle_phase > 0.85:
            state = "HIGH_TIDE"
            level_m = 8.5
        elif 0.15 <= cycle_phase < 0.50:
            state = "EBB_TIDE"      # Water receding outward
            level_m = 4.2
        elif 0.50 <= cycle_phase < 0.65:
            state = "LOW_TIDE"
            level_m = 1.1
        else:
            state = "FLOOD_TIDE"    # Water rushing inward toward Gulf
            level_m = 5.8

        return {
            "tide_state": state,
            "estimated_water_level_m": round(level_m, 1),
            "timestamp": timestamp.isoformat(),
            "region": "Gulf of Khambhat / Hazira Channel"
        }
