import numpy as np
import cv2
from typing import Dict, Any, Optional
from app.satellite.preprocessing import SatellitePreprocessor
from app.satellite.sentinel1 import Sentinel1Analyzer
from app.satellite.sentinel2 import Sentinel2Analyzer
from app.satellite.sentinel3 import Sentinel3Analyzer

class AnomalyDetector:
    """
    Unsupervised, deterministic Marine Anomaly Detector (Section 16).
    Builds a normal water appearance baseline from AOI clean scenes,
    compares new scenes against baseline, and routes signals to per-class algorithms.
    """

    def __init__(self, baseline_scene: Optional[np.ndarray] = None):
        self.baseline_scene = baseline_scene

    def set_baseline(self, clean_scene: np.ndarray):
        """Sets the clean water baseline for statistical comparison."""
        self.baseline_scene = clean_scene.copy()

    def process_scene(
        self,
        scene_rgb: np.ndarray,
        mission: str = "Sentinel-2",
        wind_speed_ms: Optional[float] = None,
        target_class: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes a satellite scene and evaluates potential pollution anomalies.
        """
        cloud_cover = SatellitePreprocessor.calculate_cloud_cover(scene_rgb)
        if cloud_cover > 30.0:
            return {
                "detected": False,
                "anomaly_class": "NORMAL",
                "confidence": 0.0,
                "cloud_cover": round(cloud_cover, 1),
                "reason": f"High cloud cover ({cloud_cover:.1f}%) obscures water surface."
            }

        water_mask = SatellitePreprocessor.create_water_mask(scene_rgb)

        # 1. Mission / Per-Class Algorithm Routing
        if mission == "Sentinel-1":
            # SAR dark-patch analysis with SAR wind-gate logic
            return Sentinel1Analyzer.evaluate_oil_candidate(scene_rgb, wind_speed_ms)

        elif mission == "Sentinel-3":
            return Sentinel3Analyzer.analyze_wide_area_ocean(scene_rgb)

        else: # Sentinel-2 Optical
            if target_class == "FLOATING_MATERIAL_CANDIDATE":
                return Sentinel2Analyzer.analyze_floating_material(scene_rgb)
            
            elif target_class == "HIGH_TURBIDITY_EVENT":
                return Sentinel2Analyzer.analyze_turbidity(scene_rgb)
            
            elif target_class == "OIL_LIKE_ANOMALY":
                # Optical oil sheen / glint candidate support check
                return Sentinel1Analyzer.evaluate_oil_candidate(scene_rgb, wind_speed_ms)

            # Standard comprehensive check: evaluate Floating Material, Turbidity, then Baseline Outlier
            floating_res = Sentinel2Analyzer.analyze_floating_material(scene_rgb)
            if floating_res["detected"]:
                floating_res["cloud_cover"] = round(cloud_cover, 1)
                return floating_res

            turbidity_res = Sentinel2Analyzer.analyze_turbidity(scene_rgb)
            if turbidity_res["detected"]:
                turbidity_res["cloud_cover"] = round(cloud_cover, 1)
                return turbidity_res

            # Statistical baseline outlier check (SURFACE_ANOMALY / UNKNOWN)
            if self.baseline_scene is not None:
                change_res = SatellitePreprocessor.validate_and_compute_change(
                    self.baseline_scene, scene_rgb
                )
                if change_res["valid"] and change_res["change_ratio"] > 0.03:
                    return {
                        "detected": True,
                        "anomaly_class": "SURFACE_ANOMALY",
                        "confidence": min(0.65, round(0.30 + change_res["change_ratio"] * 3.0, 2)),
                        "estimated_area_km2": round(change_res["change_ratio"] * 25.0, 3),
                        "detection_method": "statistical_outlier",
                        "cloud_cover": round(cloud_cover, 1),
                        "reason": f"Statistical outlier change ({change_res['change_ratio']*100:.1f}%) detected against clean baseline."
                    }

        return {
            "detected": False,
            "anomaly_class": "NORMAL",
            "confidence": 0.0,
            "cloud_cover": round(cloud_cover, 1),
            "detection_method": "multi_spectral_baseline",
            "reason": "Water appearance normal; no anomaly signature detected."
        }
