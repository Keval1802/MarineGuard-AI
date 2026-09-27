import pytest
import numpy as np
from datetime import datetime
from app.satellite.vessel_detector import SARVesselDetector, cfar_detect, convert_mask_to_targets, georeference_pixels
from app.gfw.vessels import GFWVesselClient
from app.ais.matcher import SARToAISMatcher, haversine_km
from app.services.correlation import SpillVesselCorrelator

def test_ca_cfar_vessel_detector():
    """Test Stages 1 - 5: CA-CFAR detection, connected components, georeferencing, & fixed target filtering."""
    np.random.seed(42)
    image_vv = np.random.normal(loc=0.03, scale=0.005, size=(100, 100)).astype(np.float32)
    image_vv = np.clip(image_vv, 0.001, 1.0)
    
    # Inject bright vessel targets
    image_vv[40:43, 50:53] = 0.85

    detection_mask = cfar_detect(image_vv, guard_size=3, training_size=15, alpha=4.0)
    assert detection_mask[41, 51] == True

    targets = convert_mask_to_targets(detection_mask, image_vv, min_area=2, max_area=500)
    assert len(targets) >= 1

    bbox = (100.80, 12.60, 100.95, 12.80)
    geo_targets = georeference_pixels(targets, image_width=100, image_height=100, bbox=bbox)
    assert "latitude" in geo_targets[0]
    assert "longitude" in geo_targets[0]

    now = datetime.utcnow()
    detected_vessels = SARVesselDetector.detect_vessels(
        image_vv=image_vv,
        acquisition_time=now,
        scene_id="S1A_TEST_SCENE",
        bbox=bbox,
        alpha=4.0
    )
    assert len(detected_vessels) >= 1
    assert "sar_strength" in detected_vessels[0]

def test_gfw_vessel_client():
    """Test Stages 7 - 8 & 11: GFW Vessels V3 API client lookup."""
    client = GFWVesselClient()
    identity = client.search_vessel_by_identifier("419123456")
    
    assert identity["mmsi"] == "419123456"
    assert "gfw_vessel_id" in identity
    assert "ship_name" in identity
    assert "ship_type" in identity

def test_sar_to_ais_matcher():
    """Test Stage 10: SAR detection to AIS broadcast spatial-temporal matching."""
    sar_det = {"latitude": 21.34219, "longitude": 72.51481, "acquisition_time": "2026-09-26T05:37:12Z"}
    ais_records = [
        {"mmsi": "419111111", "latitude": 21.34000, "longitude": 72.51700, "time_diff_min": 1.0, "sog": 11.2, "cog": 196.0},
        {"mmsi": "419222222", "latitude": 21.41000, "longitude": 72.60000, "time_diff_min": 0.0, "sog": 14.5, "cog": 120.0}
    ]

    matched = SARToAISMatcher.match_sar_to_ais(sar_det, ais_records, max_dist_km=2.0, max_time_min=10.0)
    assert matched is not None
    assert matched["mmsi"] == "419111111"
    assert matched["distance_km"] <= 2.0

def test_spill_vessel_correlation_engine():
    """Test Stage 12 - 14: Slick-to-vessel track correlation scoring."""
    now_iso = datetime.utcnow().isoformat()
    slick = {
        "id": "OIL-0092",
        "centroid_lat": 21.349,
        "centroid_lon": 72.520,
        "area_km2": 2.8,
        "orientation": 201.0,
        "acquisition_time": now_iso
    }

    vessel_identity = {
        "gfw_vessel_id": "GFW-987",
        "mmsi": "419111111",
        "ship_name": "EXAMPLE TANKER",
        "ship_type": "OIL TANKER"
    }

    vessel_track = [
        {"latitude": 21.342, "longitude": 72.515, "timestamp": now_iso, "sog": 11.5, "cog": 196.0}
    ]

    correlation = SpillVesselCorrelator.correlate_vessel_track_to_slick(
        slick=slick,
        vessel_identity=vessel_identity,
        vessel_track=vessel_track,
        lookback_hours=6.0
    )

    assert correlation["correlation_score"] >= 80
    assert correlation["label"] == "Vessel associated with spill candidate"
    assert "disclaimer" in correlation
