import numpy as np
import cv2
from typing import Dict, Any, Optional

class Sentinel1Analyzer:
    """
    Sentinel-1 SAR processing engine for dark-patch / surface-roughness anomaly detection.
    Enforces strict SAR wind-gating rules (Section 16).
    """

    @staticmethod
    def detect_sar_dark_patches(sar_image: np.ndarray) -> Dict[str, Any]:
        """
        Scans SAR backscatter image (VV intensity or decibel) for low-backscatter dark patches.
        """
        if len(sar_image.shape) == 3:
            gray = cv2.cvtColor(sar_image, cv2.COLOR_RGB2GRAY)
        else:
            gray = sar_image.copy()

        from app.satellite.preprocessing import SatellitePreprocessor
        water_mask = SatellitePreprocessor.create_water_mask(sar_image)

        # Smooth SAR speckle noise using Lee/Bilateral filtering simulation
        smoothed = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

        # Statistical adaptive dark-spot thresholding on ocean water pixels only
        water_pixels = smoothed[water_mask == 1]
        if len(water_pixels) == 0:
            water_pixels = smoothed.ravel()

        mean_val = np.mean(water_pixels)
        std_val = np.std(water_pixels)
        
        # Dark patches are 1.8 std below water mean, restricted to ocean water mask
        dark_thresh = max(10, mean_val - 1.8 * std_val)
        dark_mask = ((smoothed < dark_thresh) & (water_mask == 1)).astype(np.uint8)

        # Find dark region contours
        contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        candidates = []
        for cnt in contours:
            area_px = cv2.contourArea(cnt)
            if area_px >= 20:  # Ignore tiny noise artifacts
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    candidates.append({
                        "center_pixel": (cx, cy),
                        "area_pixels": float(area_px),
                        "contour": cnt
                    })

        return {
            "dark_mask": dark_mask,
            "candidates": candidates,
            "mean_backscatter": float(mean_val)
        }

    @classmethod
    def evaluate_oil_candidate(
        cls,
        sar_image: np.ndarray,
        wind_speed_ms: Optional[float]
    ) -> Dict[str, Any]:
        """
        Evaluates SAR dark patches against wind gate rule:
        - Wind speed 2 - 10 m/s: Valid OIL_LIKE_ANOMALY candidate
        - Wind speed < 2 m/s or > 10 m/s: Flagged as lower-confidence look-alike candidate
        """
        sar_results = cls.detect_sar_dark_patches(sar_image)
        candidates = sar_results["candidates"]

        if not candidates:
            return {
                "detected": False,
                "anomaly_class": "NORMAL",
                "confidence": 0.0,
                "wind_speed_ms": wind_speed_ms,
                "detection_method": "sar_dark_patch",
                "reason": "No SAR dark patch detected in ocean water."
            }

        largest_candidate = max(candidates, key=lambda c: c["area_pixels"])
        area_px = largest_candidate["area_pixels"]
        # Approximate conversion: 1 pixel ~ 10m x 10m = 100 m2 = 0.0001 km2
        est_area_km2 = round(area_px * 0.0001, 3)

        # Wind-gate evaluation (Section 16)
        if wind_speed_ms is None:
            # Missing wind data fallback -> low confidence candidate
            return {
                "detected": True,
                "anomaly_class": "SURFACE_ANOMALY",
                "confidence": 0.35,
                "wind_speed_ms": None,
                "estimated_area_km2": est_area_km2,
                "detection_method": "sar_dark_patch",
                "is_wind_gated": False,
                "reason": "SAR dark patch found, but wind data unavailable for verification."
            }

        if 2.0 <= wind_speed_ms <= 10.0:
            # Ideal wind window for SAR oil detection
            confidence = min(0.85, 0.55 + (area_px / 1000.0) * 0.2)
            return {
                "detected": True,
                "anomaly_class": "OIL_LIKE_ANOMALY",
                "confidence": round(confidence, 2),
                "wind_speed_ms": wind_speed_ms,
                "estimated_area_km2": est_area_km2,
                "detection_method": "sar_dark_patch",
                "is_wind_gated": True,
                "reason": f"SAR dark patch detected within valid wind window ({wind_speed_ms:.1f} m/s)."
            }
        elif wind_speed_ms < 2.0:
            # Low wind look-alike (biogenic film / calm sea)
            return {
                "detected": True,
                "anomaly_class": "SURFACE_ANOMALY",
                "confidence": 0.30,
                "wind_speed_ms": wind_speed_ms,
                "estimated_area_km2": est_area_km2,
                "detection_method": "sar_dark_patch",
                "is_wind_gated": False,
                "reason": f"Wind speed ({wind_speed_ms:.1f} m/s < 2.0 m/s) too low; high likelihood of natural biogenic slick look-alike."
            }
        else:
            # High wind dispersion (> 10 m/s)
            return {
                "detected": True,
                "anomaly_class": "SURFACE_ANOMALY",
                "confidence": 0.25,
                "wind_speed_ms": wind_speed_ms,
                "estimated_area_km2": est_area_km2,
                "detection_method": "sar_dark_patch",
                "is_wind_gated": False,
                "reason": f"Wind speed ({wind_speed_ms:.1f} m/s > 10.0 m/s) high; oil dispersed or wave clutter masking signal."
            }
