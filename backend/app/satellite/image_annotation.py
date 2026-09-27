import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Dict, Any, Optional

class ImageAnnotator:
    """
    Renders visual evidence overlays:
    - Bounding boxes & anomaly polygons
    - Metadata text overlays (mission, timestamp, confidence, area)
    - Scale bars & compass direction indicators
    - Side-by-side Sentinel-1 & Sentinel-2 comparative images
    """

    @staticmethod
    def draw_incident_annotation(
        image_rgb: np.ndarray,
        anomaly_type: str,
        confidence: float,
        area_km2: float,
        mission: str,
        timestamp_str: str,
        bbox_coords: Optional[Tuple[int, int, int, int]] = None
    ) -> np.ndarray:
        """Draws bounding polygon highlight, corner targets, scale bar, and metadata banner on evidence image."""
        img = image_rgb.copy()
        h, w = img.shape[:2]

        if not bbox_coords:
            min_x, min_y = int(w * 0.30), int(h * 0.38)
            max_x, max_y = int(w * 0.62), int(h * 0.64)
        else:
            min_x, min_y, max_x, max_y = bbox_coords

        # Color coding by anomaly class (RGB)
        color_map = {
            "OIL_LIKE_ANOMALY": (255, 60, 60),           # Crimson Red
            "FLOATING_MATERIAL_CANDIDATE": (255, 215, 0), # Gold Yellow
            "HIGH_TURBIDITY_EVENT": (230, 120, 40),      # Amber Orange
            "SURFACE_ANOMALY": (210, 80, 255)           # Neon Purple
        }
        color = color_map.get(anomaly_type, (0, 220, 255))

        # 1. Semi-transparent highlight overlay inside anomaly region
        overlay = img.copy()
        cv2.rectangle(overlay, (min_x, min_y), (max_x, max_y), color, -1)
        cv2.addWeighted(overlay, 0.18, img, 0.82, 0, img)

        # 2. Outer bounding box outline with dashed corner brackets
        cv2.rectangle(img, (min_x, min_y), (max_x, max_y), color, 2, cv2.LINE_AA)
        
        # Corner brackets for tactical targeting look
        corner_len = 14
        # Top-Left
        cv2.line(img, (min_x, min_y), (min_x + corner_len, min_y), (255, 255, 255), 2)
        cv2.line(img, (min_x, min_y), (min_x, min_y + corner_len), (255, 255, 255), 2)
        # Top-Right
        cv2.line(img, (max_x, min_y), (max_x - corner_len, min_y), (255, 255, 255), 2)
        cv2.line(img, (max_x, min_y), (max_x, min_y + corner_len), (255, 255, 255), 2)
        # Bottom-Left
        cv2.line(img, (min_x, max_y), (min_x + corner_len, max_y), (255, 255, 255), 2)
        cv2.line(img, (min_x, max_y), (min_x, max_y - corner_len), (255, 255, 255), 2)
        # Bottom-Right
        cv2.line(img, (max_x, max_y), (max_x - corner_len, max_y), (255, 255, 255), 2)
        cv2.line(img, (max_x, max_y), (max_x, max_y - corner_len), (255, 255, 255), 2)

        # 3. Anomaly Target Label Tag
        tag_text = f"TARGET: {anomaly_type.replace('_', ' ')} ({int(confidence * 100)}%)"
        cv2.rectangle(img, (min_x, min_y - 20), (min_x + len(tag_text) * 7 + 10, min_y), (15, 23, 42), -1)
        cv2.putText(img, tag_text, (min_x + 5, min_y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA)

        # 4. Scale Bar & Compass (Bottom Left / Bottom Right)
        # Scale Bar
        sb_x, sb_y = 15, h - 25
        cv2.line(img, (sb_x, sb_y), (sb_x + 60, sb_y), (255, 255, 255), 2)
        cv2.line(img, (sb_x, sb_y - 4), (sb_x, sb_y + 4), (255, 255, 255), 2)
        cv2.line(img, (sb_x + 60, sb_y - 4), (sb_x + 60, sb_y + 4), (255, 255, 255), 2)
        cv2.putText(img, "1.0 km", (sb_x + 12, sb_y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (240, 240, 240), 1, cv2.LINE_AA)

        # Compass Indicator
        cp_x, cp_y = w - 30, h - 30
        cv2.arrowedLine(img, (cp_x, cp_y), (cp_x, cp_y - 20), (56, 189, 248), 2, tipLength=0.35)
        cv2.putText(img, "N", (cp_x - 4, cp_y - 24), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (56, 189, 248), 1, cv2.LINE_AA)

        # 5. Header Metadata Banner
        banner_height = 45
        cv2.rectangle(img, (0, 0), (w, banner_height), (15, 23, 42), -1)

        text_line1 = f"{mission.upper()} | {anomaly_type} | Conf: {int(confidence * 100)}%"
        text_line2 = f"Est. Area: {area_km2:.2f} km² | Acquired: {timestamp_str}"

        cv2.putText(img, text_line1, (10, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img, text_line2, (10, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (200, 220, 240), 1, cv2.LINE_AA)

        return img

    @staticmethod
    def create_before_after_comparison(
        image_before: np.ndarray,
        image_after: np.ndarray,
        timestamp_before: str = "T1 (Historical)",
        timestamp_after: str = "T2 (Current Anomaly)"
    ) -> np.ndarray:
        """Generates a side-by-side comparative evidence image for before/after change review."""
        return ImageAnnotator.create_dual_sentinel_comparison(
            image_s1=image_before,
            image_s2=image_after,
            label_s1=f"BEFORE: {timestamp_before}",
            label_s2=f"AFTER: {timestamp_after}"
        )

    @staticmethod
    def create_dual_sentinel_comparison(
        image_s1: np.ndarray,
        image_s2: np.ndarray,
        label_s1: str = "SENTINEL-1 SAR (RADAR VV BACKSCATTER)",
        label_s2: str = "SENTINEL-2 OPTICAL (MULTISPECTRAL TRUE-COLOR)"
    ) -> np.ndarray:
        """
        Stitches Sentinel-1 SAR (Radar) image on the LEFT and Sentinel-2 Optical on the RIGHT.
        """
        h1, w1 = image_s1.shape[:2]
        h2, w2 = image_s2.shape[:2]

        target_h = max(h1, h2)
        target_w = max(w1, w2)

        img_s1_resized = cv2.resize(image_s1, (target_w, target_h))
        img_s2_resized = cv2.resize(image_s2, (target_w, target_h))

        separator_w = 6
        separator = np.full((target_h, separator_w, 3), (56, 189, 248), dtype=np.uint8)

        canvas = np.hstack([img_s1_resized, separator, img_s2_resized])
        c_h, c_w = canvas.shape[:2]

        # Top Banner
        banner_h = 45
        banner = np.zeros((banner_h, c_w, 3), dtype=np.uint8)
        banner[:] = (15, 23, 42)

        cv2.putText(banner, f"LEFT: {label_s1}", (15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (56, 189, 248), 1, cv2.LINE_AA)
        cv2.putText(banner, f"RIGHT: {label_s2}", (target_w + separator_w + 15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (250, 204, 21), 1, cv2.LINE_AA)

        final_comparison = np.vstack([banner, canvas])
        return final_comparison
