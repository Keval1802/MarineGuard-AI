import numpy as np
from scipy.ndimage import uniform_filter
import cv2
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import math

# Known Fixed Infrastructure Coordinates (Ports, Oil Terminals, Offshore Platforms, Bridges)
FIXED_INFRASTRUCTURE = [
    {"name": "Sattahip Deep Port Jetty", "lat": 12.665, "lon": 100.915, "radius_m": 800},
    {"name": "Map Ta Phut Petrochemical Terminal Pier", "lat": 12.660, "lon": 101.145, "radius_m": 1000},
    {"name": "Kamarajar Ennore Port Breakwater Jetty", "lat": 13.228, "lon": 80.340, "radius_m": 900},
    {"name": "Hazira Port Platform & Loading Dock", "lat": 21.102, "lon": 72.615, "radius_m": 850},
    {"name": "Tapi Estuary Bridge & Jetty Structure", "lat": 21.125, "lon": 72.685, "radius_m": 700}
]

def cfar_detect(
    image: np.ndarray,
    guard_size: int = 3,
    training_size: int = 15,
    alpha: float = 4.0
) -> np.ndarray:
    """
    Cell-Averaging Constant False Alarm Rate (CA-CFAR) Vessel Detection Algorithm (Stage 2).
    Operates on linear VV backscatter rasters.
    """
    image = np.asarray(image, dtype=np.float32)
    outer_size = training_size * 2 + 1
    guard_window = guard_size * 2 + 1

    # scipy uniform_filter calculates local sliding window means
    outer_mean = uniform_filter(image, size=outer_size, mode="reflect")
    guard_mean = uniform_filter(image, size=guard_window, mode="reflect")

    outer_n = outer_size ** 2
    guard_n = guard_window ** 2

    training_sum = (outer_mean * outer_n - guard_mean * guard_n)
    training_n = outer_n - guard_n

    # Estimate ocean background noise level excluding guard window
    background = np.maximum(training_sum / training_n, 1e-6)
    threshold = background * alpha

    # Bright pixels exceeding adaptive local background threshold are candidate vessel pixels
    detection = image > threshold
    return detection

def convert_mask_to_targets(
    detection_mask: np.ndarray,
    image_vv: np.ndarray,
    min_area: int = 2,
    max_area: int = 500
) -> List[Dict[str, Any]]:
    """
    Groups neighboring detected pixels into vessel candidate target objects (Stage 3).
    Filters out single pixel noise (< 2) and huge non-vessel objects (> 500).
    """
    mask = detection_mask.astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)

    targets = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if min_area <= area <= max_area:
            cx, cy = centroids[i][0], centroids[i][1]
            
            # Calculate mean VV backscatter intensity for vessel object
            obj_mask = (labels == i)
            mean_backscatter = float(np.mean(image_vv[obj_mask])) if np.any(obj_mask) else 0.5
            
            targets.append({
                "pixel_x": float(cx),
                "pixel_y": float(cy),
                "pixel_area": int(area),
                "backscatter": mean_backscatter
            })
    return targets

def georeference_pixels(
    targets: List[Dict[str, Any]],
    image_width: int,
    image_height: int,
    bbox: Tuple[float, float, float, float]
) -> List[Dict[str, Any]]:
    """
    Converts pixel (x, y) coordinates into WGS84 (latitude, longitude) (Stage 4).
    bbox: (min_lon, min_lat, max_lon, max_lat)
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    georeferenced = []

    for t in targets:
        px, py = t["pixel_x"], t["pixel_y"]
        
        # Linear affine interpolation across image bounding box
        lon = min_lon + (px / float(image_width)) * (max_lon - min_lon)
        lat = max_lat - (py / float(image_height)) * (max_lat - min_lat)
        
        t_copy = dict(t)
        t_copy["longitude"] = round(float(lon), 6)
        t_copy["latitude"] = round(float(lat), 6)
        georeferenced.append(t_copy)

    return georeferenced

def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates distance in meters between two coordinates."""
    R = 6371000.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

def filter_fixed_infrastructure(
    targets: List[Dict[str, Any]],
    fixed_targets: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Filters out fixed infrastructure targets (ports, platforms, jetties) from vessel candidates (Stage 5).
    """
    infrastructure_list = fixed_targets or FIXED_INFRASTRUCTURE
    valid_vessels = []

    for t in targets:
        t_lat, t_lon = t["latitude"], t["longitude"]
        is_fixed = False

        for fix in infrastructure_list:
            dist = haversine_m(t_lat, t_lon, fix["lat"], fix["lon"])
            if dist <= fix["radius_m"]:
                is_fixed = True
                break

        if not is_fixed:
            valid_vessels.append(t)

    return valid_vessels

class SARVesselDetector:
    """
    Sentinel-1 SAR VV CA-CFAR vessel detector service.
    """

    @classmethod
    def detect_vessels(
        cls,
        image_vv: np.ndarray,
        acquisition_time: datetime,
        scene_id: str,
        bbox: Tuple[float, float, float, float] = (100.80, 12.60, 100.95, 12.80),
        alpha: float = 4.0
    ) -> List[Dict[str, Any]]:
        """
        Executes complete SAR vessel detection pipeline (Stages 1 through 6).
        """
        # 1. CA-CFAR detection on linear backscatter raster
        mask = cfar_detect(image_vv, guard_size=3, training_size=15, alpha=alpha)

        # 2. Extract connected components vessel objects
        raw_targets = convert_mask_to_targets(mask, image_vv, min_area=2, max_area=500)

        # 3. Georeference pixel coordinates to lat/lon
        h, w = image_vv.shape[:2]
        geo_targets = georeference_pixels(raw_targets, image_width=w, image_height=h, bbox=bbox)

        # 4. Filter land & fixed infrastructure
        vessels = filter_fixed_infrastructure(geo_targets)

        # 5. Form final SAR vessel detection objects with timestamp
        formatted_vessels = []
        for idx, v in enumerate(vessels, 1):
            formatted_vessels.append({
                "id": f"SAR-{scene_id[:12]}-{idx:03d}",
                "scene_id": scene_id,
                "latitude": v["latitude"],
                "longitude": v["longitude"],
                "acquisition_time": acquisition_time.isoformat(),
                "sar_strength": round(float(v["backscatter"]), 4),
                "pixel_area": v["pixel_area"],
                "confidence": min(0.95, 0.70 + (v["backscatter"] * 0.2))
            })

        return formatted_vessels
