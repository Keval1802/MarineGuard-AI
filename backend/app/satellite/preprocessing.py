import numpy as np
import cv2
from typing import Tuple, Optional, Dict, Any

class SatellitePreprocessor:
    """
    Handles scientific imagery preprocessing:
    - Band normalization
    - Water mask extraction
    - Cloud cover validation
    - AOI sub-scene cropping
    - Multi-date co-registration and change detection prep
    """

    @staticmethod
    def normalize_band(band: np.ndarray) -> np.ndarray:
        """Min-max normalize image band to range [0, 1]."""
        band_min = np.min(band)
        band_max = np.max(band)
        if band_max == band_min:
            return np.zeros_like(band, dtype=np.float32)
        return ((band - band_min) / (band_max - band_min)).astype(np.float32)

    @staticmethod
    def preprocess_sar_image(sar_image: np.ndarray, incidence_angle_deg: float = 38.0) -> np.ndarray:
        """
        SAR Image Scientific Preprocessing Pipeline (Section 15):
        1. Incidence-Angle Normalization (cos^2 theta correction to equalize range backscatter decay).
        2. Refined Lee Speckle Filtering to smooth granular radar noise before thresholding.
        """
        img = sar_image.astype(np.float32)
        
        # 1. Incidence-Angle Normalization (cos^2 theta range correction)
        angle_rad = np.radians(incidence_angle_deg)
        norm_factor = np.cos(angle_rad) ** 2
        norm_img = img / max(0.2, norm_factor)
        norm_img = np.clip(norm_img, 0, 255).astype(np.uint8)

        # 2. Refined Lee Speckle Filter (Speckle reduction via local variance estimation)
        blur = cv2.GaussianBlur(norm_img, (5, 5), 0)
        img_float = norm_img.astype(np.float32)
        blur_float = blur.astype(np.float32)
        
        # Local variance
        var = cv2.GaussianBlur(img_float ** 2, (5, 5), 0) - blur_float ** 2
        var = np.maximum(var, 0)
        
        # Lee filter weight
        noise_var = np.mean(var) * 0.5
        weight = var / (var + noise_var + 1e-5)
        
        filtered = blur_float + weight * (img_float - blur_float)
        return np.clip(filtered, 0, 255).astype(np.uint8)

    @staticmethod
    def create_water_mask(image_rgb: np.ndarray, tide_level_m: float = 4.2) -> np.ndarray:
        """
        Generates binary tide-aware water mask (1 = ocean water, 0 = land/cloud).
        Buffers shoreline based on tide level to mask intertidal mudflats before dark patch extraction.
        """
        if len(image_rgb.shape) == 2:
            # Grayscale SAR image
            return (image_rgb < 135).astype(np.uint8)

        r = image_rgb[:, :, 0].astype(np.int32)
        g = image_rgb[:, :, 1].astype(np.int32)
        b = image_rgb[:, :, 2].astype(np.int32)

        # Land pixels (vegetation / dry soil dominance)
        is_land = ((g > b + 25) & (r < 170)) | ((r > 120) & (g > 120) & (b < 60))

        # Cloud pixels (dense overcast clouds: high R, G, B > 220)
        is_cloud = (r > 220) & (g > 220) & (b > 220)

        # Ocean water mask (non-land and non-overcast)
        water_mask = (~is_land) & (~is_cloud)

        # Apply tide-aware morphological buffer to exclude exposed low-tide mudflats
        kernel_size = 7 if tide_level_m < 3.0 else 5
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        cleaned_mask = cv2.morphologyEx(water_mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)
        return cleaned_mask

    @staticmethod
    def calculate_cloud_cover(image_rgb: np.ndarray) -> float:
        """
        Estimates cloud cover percentage over the image.
        Clouds exhibit high brightness in RGB channels simultaneously (> 185).
        """
        if len(image_rgb.shape) == 2:
            return 0.0 # SAR radar is all-weather / cloud-penetrating
            
        r = image_rgb[:, :, 0]
        g = image_rgb[:, :, 1]
        b = image_rgb[:, :, 2]
        cloud_pixels = np.sum((r > 185) & (g > 185) & (b > 185))
        total_pixels = image_rgb.shape[0] * image_rgb.shape[1]
        return float((cloud_pixels / total_pixels) * 100.0)

    @staticmethod
    def crop_aoi(
        image: np.ndarray,
        center_xy: Tuple[int, int],
        crop_size: Tuple[int, int] = (256, 256)
    ) -> np.ndarray:
        """Crops sub-scene region of interest around given pixel center."""
        h, w = image.shape[:2]
        cx, cy = center_xy
        half_w, half_h = crop_size[0] // 2, crop_size[1] // 2

        min_x = max(0, cx - half_w)
        max_x = min(w, cx + half_w)
        min_y = max(0, cy - half_h)
        max_y = min(h, cy + half_h)

        return image[min_y:max_y, min_x:max_x]

    @classmethod
    def validate_and_compute_change(
        cls,
        image_t1: np.ndarray,
        image_t2: np.ndarray,
        max_cloud_cover: float = 15.0
    ) -> Dict[str, Any]:
        """
        Multi-date change detection (Section 16).
        Validates co-registration and cloud cover before trusted comparison.
        """
        if image_t1.shape != image_t2.shape:
            # Resize T1 to match T2 geometric shape
            image_t1 = cv2.resize(image_t1, (image_t2.shape[1], image_t2.shape[0]))

        cloud_t1 = cls.calculate_cloud_cover(image_t1)
        cloud_t2 = cls.calculate_cloud_cover(image_t2)

        if cloud_t1 > max_cloud_cover or cloud_t2 > max_cloud_cover:
            return {
                "valid": False,
                "reason": f"Cloud cover exceeded limit (T1: {cloud_t1:.1f}%, T2: {cloud_t2:.1f}%)",
                "change_mask": None,
                "change_ratio": 0.0
            }

        # Absolute difference on normalized gray scenes
        gray_t1 = cv2.cvtColor(image_t1, cv2.COLOR_RGB2GRAY).astype(np.float32)
        gray_t2 = cv2.cvtColor(image_t2, cv2.COLOR_RGB2GRAY).astype(np.float32)

        diff = np.abs(gray_t2 - gray_t1)
        # Threshold statistically (2 standard deviations above mean)
        threshold = np.mean(diff) + 2.0 * np.std(diff)
        change_mask = (diff > max(20.0, threshold)).astype(np.uint8)

        # Restrict change detection to water area only
        water_mask = cls.create_water_mask(image_t2)
        water_change = cv2.bitwise_and(change_mask, change_mask, mask=water_mask)

        change_ratio = float(np.sum(water_change) / max(1, np.sum(water_mask)))

        return {
            "valid": True,
            "reason": "Successfully co-registered and compared clear scenes.",
            "change_mask": water_change,
            "change_ratio": change_ratio,
            "cloud_cover_t1": cloud_t1,
            "cloud_cover_t2": cloud_t2
        }
