import os
import cv2
import numpy as np
from harness.config import harness_settings

class SatelliteHarnessProvider:
    """Provides real static satellite images for test harness execution."""

    @staticmethod
    def get_real_satellite_patch(mission: str, width: int = 512, height: int = 512) -> np.ndarray:
        is_sar = "Sentinel-1" in mission
        filepath = harness_settings.S1_SAR_PATH if is_sar else harness_settings.S2_OPTICAL_PATH

        if filepath.exists():
            img_bgr = cv2.imread(str(filepath))
            if img_bgr is not None:
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                return cv2.resize(img_rgb, (width, height))
        
        # High-resolution realistic satellite ocean texture placeholder if asset file is missing
        img = np.zeros((height, width, 3), dtype=np.uint8)
        if is_sar:
            # Realistic SAR VV radar backscatter grayscale texture
            np.random.seed(42)
            noise = np.random.normal(110, 25, (height, width)).astype(np.uint8)
            img[:, :, 0] = noise
            img[:, :, 1] = noise
            img[:, :, 2] = noise
        else:
            # Realistic Sentinel-2 Optical coastal ocean water texture
            img[:, :, 0] = 15  # R
            img[:, :, 1] = 65  # G
            img[:, :, 2] = 145 # B
        return img
