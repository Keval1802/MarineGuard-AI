import os
import cv2
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
from app.config import settings
from app.satellite.catalog import CopernicusCatalogService
from app.satellite.preprocessing import SatellitePreprocessor
from app.satellite.image_annotation import ImageAnnotator

class SatelliteImageCaptureService:
    """
    Retrieves satellite observation scenes, crops AOI, generates raw evidence images,
    annotated anomaly images, and before/after comparison images (Section 13).
    """

    def __init__(self):
        self.catalog = CopernicusCatalogService()
        self.storage_dir = settings.LOCAL_STORAGE_DIR
        os.makedirs(self.storage_dir, exist_ok=True)

    def capture_evidence_images(
        self,
        incident_code: str,
        anomaly_type: str,
        confidence: float,
        area_km2: float,
        mission: str = "Sentinel-2",
        acquisition_time: Optional[datetime] = None,
        latitude: float = 21.145,
        longitude: float = 72.620
    ) -> Dict[str, str]:
        """
        Generates and saves visual evidence outputs:
        1. Raw cropped scene patch from Copernicus Data Space API
        2. Annotated incident image with bounding box / polygon & metadata
        3. Before/After side-by-side comparative image
        """
        if not acquisition_time:
            acquisition_time = datetime.utcnow()

        timestamp_str = acquisition_time.strftime("%Y-%m-%d %H:%M:%S UTC")

        # Fetch real Copernicus satellite image scene for Sentinel-1 SAR and Sentinel-2 Optical
        s1_scene = self.catalog.fetch_real_satellite_image(
            lat=latitude, lon=longitude, width=512, height=512, mission="Sentinel-1", anomaly_type="OIL_LIKE_ANOMALY"
        )
        s2_scene = self.catalog.fetch_real_satellite_image(
            lat=latitude, lon=longitude, width=512, height=512, mission="Sentinel-2", anomaly_type="FLOATING_MATERIAL_CANDIDATE"
        )

        current_scene = s1_scene if "Sentinel-1" in mission else s2_scene

        # 1. Raw image
        raw_filename = f"{incident_code}_{mission.lower()}_raw.png"
        raw_path = os.path.join(self.storage_dir, raw_filename)
        cv2.imwrite(raw_path, cv2.cvtColor(current_scene, cv2.COLOR_RGB2BGR))

        # 2. Annotated image
        annotated_img = ImageAnnotator.draw_incident_annotation(
            image_rgb=current_scene,
            anomaly_type=anomaly_type,
            confidence=confidence,
            area_km2=area_km2,
            mission=mission,
            timestamp_str=timestamp_str
        )
        annotated_filename = f"{incident_code}_{mission.lower()}_annotated.png"
        annotated_path = os.path.join(self.storage_dir, annotated_filename)
        cv2.imwrite(annotated_path, cv2.cvtColor(annotated_img, cv2.COLOR_RGB2BGR))

        # 3. Combined Dual-Satellite Comparison Image (Sentinel-1 SAR on LEFT, Sentinel-2 Optical on RIGHT)
        s1_annotated = ImageAnnotator.draw_incident_annotation(s1_scene, "OIL_LIKE_ANOMALY", confidence, area_km2, "Sentinel-1", timestamp_str)
        s2_annotated = ImageAnnotator.draw_incident_annotation(s2_scene, "FLOATING_MATERIAL_CANDIDATE", confidence, area_km2, "Sentinel-2", timestamp_str)
        
        comparison_img = ImageAnnotator.create_dual_sentinel_comparison(
            image_s1=s1_annotated,
            image_s2=s2_annotated,
            label_s1=f"SENTINEL-1 SAR RADAR ({timestamp_str})",
            label_s2=f"SENTINEL-2 OPTICAL MULTISPECTRAL ({timestamp_str})"
        )
        comparison_filename = f"{incident_code}_comparison.png"
        comparison_path = os.path.join(self.storage_dir, comparison_filename)
        cv2.imwrite(comparison_path, cv2.cvtColor(comparison_img, cv2.COLOR_RGB2BGR))

        return {
            "raw_image_path": f"/storage/evidence/{raw_filename}",
            "annotated_image_path": f"/storage/evidence/{annotated_filename}",
            "before_after_image_path": f"/storage/evidence/{comparison_filename}"
        }
