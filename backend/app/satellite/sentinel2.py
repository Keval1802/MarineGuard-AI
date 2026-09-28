import numpy as np
import cv2
from typing import Dict, Any
from app.satellite.preprocessing import SatellitePreprocessor

class Sentinel2Analyzer:
    """
    Sentinel-2 optical multispectral analyzer for:
    - Floating debris / material candidates (NIR / SWIR band ratio over water)
    - High turbidity / sediment events (Red / NIR band ratio over water)
    """

    @staticmethod
    def analyze_floating_material(image_rgb: np.ndarray) -> Dict[str, Any]:
        """
        Detects FLOATING_MATERIAL_CANDIDATE in ocean water.
        Solid floating waste/debris reflects differently from open water in NIR/SWIR bands.
        """
        r = image_rgb[:, :, 0].astype(np.float32)
        g = image_rgb[:, :, 1].astype(np.float32)
        b = image_rgb[:, :, 2].astype(np.float32)

        # Floating material index (FMI) proxy (NIR/SWIR elevation over blue water)
        fmi = (r + g) / (b + 1.0)
        
        # Mask out land to compute clean ocean water baseline statistics
        water_mask = SatellitePreprocessor.create_water_mask(image_rgb)
        water_pixels = fmi[water_mask == 1]
        
        if len(water_pixels) == 0:
            water_pixels = fmi.ravel()

        water_bg_mean = float(np.mean(water_pixels))
        water_bg_std = float(np.std(water_pixels))
        thresh = water_bg_mean + 2.0 * water_bg_std

        # Cloud & sun glint filter (R, G, B all > 185)
        is_cloud = (r > 185) & (g > 185) & (b > 185)

        high_fmi_mask = ((fmi > max(1.1, thresh)) & (water_mask == 1) & (~is_cloud)).astype(np.uint8) * 255
        
        # Morphological closing to merge nearby floating candidate pixels
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        high_fmi_mask = cv2.morphologyEx(high_fmi_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(high_fmi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return {
                "detected": False,
                "anomaly_class": "NORMAL",
                "confidence": 0.0,
                "detection_method": "floating_debris_index"
            }

        total_pixels = float(np.count_nonzero(high_fmi_mask))
        largest_cnt = max(contours, key=cv2.contourArea)
        area_px = max(float(cv2.contourArea(largest_cnt)), total_pixels)

        if area_px < 15:
            return {
                "detected": False,
                "anomaly_class": "NORMAL",
                "confidence": 0.0,
                "detection_method": "floating_debris_index"
            }

        est_area_km2 = round(area_px * 0.0001, 3)
        confidence = min(0.78, 0.45 + (area_px / 800.0) * 0.25)

        return {
            "detected": True,
            "anomaly_class": "FLOATING_MATERIAL_CANDIDATE",
            "confidence": round(confidence, 2),
            "estimated_area_km2": est_area_km2,
            "detection_method": "floating_debris_index",
            "reason": f"Floating material spectral anomaly detected over {est_area_km2} km² area."
        }

    @staticmethod
    def analyze_turbidity(image_rgb: np.ndarray) -> Dict[str, Any]:
        """
        Detects HIGH_TURBIDITY_EVENT in ocean water.
        Turbidity plumes are caused by suspended sediment concentration (optical only).
        """
        r = image_rgb[:, :, 0].astype(np.float32)
        g = image_rgb[:, :, 1].astype(np.float32)

        turbidity_index = (r + 1.0) / (g + 1.0)
        water_mask = SatellitePreprocessor.create_water_mask(image_rgb)
        water_pixels = turbidity_index[water_mask == 1]
        
        if len(water_pixels) == 0:
            water_pixels = turbidity_index.ravel()

        mean_turb = float(np.mean(water_pixels))
        std_turb = float(np.std(water_pixels))
        
        turb_mask = ((turbidity_index > (mean_turb + 1.1 * std_turb)) & (water_mask == 1)).astype(np.uint8) * 255
        contours, _ = cv2.findContours(turb_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return {
                "detected": False,
                "anomaly_class": "NORMAL",
                "confidence": 0.0,
                "detection_method": "turbidity_index"
            }

        largest_cnt = max(contours, key=cv2.contourArea)
        area_px = float(cv2.contourArea(largest_cnt))

        if area_px < 15:
            return {
                "detected": False,
                "anomaly_class": "NORMAL",
                "confidence": 0.0,
                "detection_method": "turbidity_index"
            }

        est_area_km2 = round(area_px * 0.0001, 3)
        confidence = min(0.82, 0.50 + (area_px / 1200.0) * 0.25)

        return {
            "detected": True,
            "anomaly_class": "HIGH_TURBIDITY_EVENT",
            "confidence": round(confidence, 2),
            "estimated_area_km2": est_area_km2,
            "detection_method": "turbidity_index",
            "reason": f"High turbidity sediment plume detected over {est_area_km2} km² area."
        }
