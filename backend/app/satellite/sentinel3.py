import numpy as np
from typing import Dict, Any

class Sentinel3Analyzer:
    """
    Sentinel-3 OLCI wide-area ocean water-colour anomaly monitor.
    Used for macro coastal/ocean context (~300 m spatial sampling).
    """

    @staticmethod
    def analyze_wide_area_ocean(image_rgb: np.ndarray) -> Dict[str, Any]:
        """Provides wide-area ocean water-colour variance and macro context."""
        gray = np.mean(image_rgb, axis=2)
        variance = float(np.var(gray))
        mean_val = float(np.mean(gray))

        is_anomalous = variance > 600.0 or mean_val < 15.0 or mean_val > 210.0

        return {
            "detected": is_anomalous,
            "anomaly_class": "SURFACE_ANOMALY" if is_anomalous else "NORMAL",
            "confidence": 0.45 if is_anomalous else 0.0,
            "detection_method": "sentinel3_wide_area_olci",
            "mean_reflectance": round(mean_val, 2),
            "reflectance_variance": round(variance, 2),
            "reason": "Sentinel-3 wide-area ocean water-colour anomaly flagged." if is_anomalous else "Sentinel-3 ocean context normal."
        }
