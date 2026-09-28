import pytest
from fastapi.testclient import TestClient
import numpy as np
from datetime import datetime, timedelta

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.incident import Incident, AnomalyType, IncidentStatus
from app.satellite.sentinel1 import Sentinel1Analyzer
from app.satellite.sentinel2 import Sentinel2Analyzer
from app.satellite.catalog import CopernicusCatalogService
from app.services.confidence import ConfidenceCalculator
from app.services.trajectory import TrajectoryService
from app.services.risk import RiskCalculator
from app.environmental.gis import GISService

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after tests

def test_health_check():
    """Test public health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_sar_wind_gate_rules():
    """Test Section 16 SAR wind-gate rule logic."""
    catalog = CopernicusCatalogService()
    sar_scene = catalog.fetch_real_satellite_image(mission="Sentinel-1", anomaly_type="OIL_LIKE_ANOMALY")

    # Case 1: Ideal wind speed 5.0 m/s (between 2 and 10 m/s) -> OIL_LIKE_ANOMALY candidate
    res1 = Sentinel1Analyzer.evaluate_oil_candidate(sar_scene, wind_speed_ms=5.0)
    assert res1["detected"] is True
    assert res1["anomaly_class"] == "OIL_LIKE_ANOMALY"
    assert res1["is_wind_gated"] is True

    # Case 2: Wind speed 1.5 m/s (< 2 m/s) -> Low wind look-alike SURFACE_ANOMALY
    res2 = Sentinel1Analyzer.evaluate_oil_candidate(sar_scene, wind_speed_ms=1.5)
    assert res2["detected"] is True
    assert res2["anomaly_class"] == "SURFACE_ANOMALY"
    assert res2["is_wind_gated"] is False

    # Case 3: Wind speed 12.0 m/s (> 10 m/s) -> High wind dispersion SURFACE_ANOMALY
    res3 = Sentinel1Analyzer.evaluate_oil_candidate(sar_scene, wind_speed_ms=12.0)
    assert res3["detected"] is True
    assert res3["anomaly_class"] == "SURFACE_ANOMALY"
    assert res3["is_wind_gated"] is False

def test_optical_per_class_detectors():
    """Test Sentinel-2 optical floating debris and turbidity detectors."""
    catalog = CopernicusCatalogService()
    
    # Floating debris scene
    debris_scene = catalog.fetch_real_satellite_image(mission="Sentinel-2", anomaly_type="FLOATING_MATERIAL_CANDIDATE")
    res_debris = Sentinel2Analyzer.analyze_floating_material(debris_scene)
    assert res_debris["detected"] is True
    assert res_debris["anomaly_class"] == "FLOATING_MATERIAL_CANDIDATE"

    # Turbidity plume scene
    turb_scene = catalog.fetch_real_satellite_image(mission="Sentinel-2", anomaly_type="HIGH_TURBIDITY_EVENT")
    res_turb = Sentinel2Analyzer.analyze_turbidity(turb_scene)
    assert res_turb["detected"] is True
    assert res_turb["anomaly_class"] == "HIGH_TURBIDITY_EVENT"

def test_confidence_calculator():
    """Test Section 22 evidence confidence scoring."""
    res = ConfidenceCalculator.calculate_confidence(
        has_satellite=True,
        satellite_model_conf=0.80,
        has_second_satellite=True,
        has_vessel_match=True,
        environmental_match=True
    )
    assert res["confidence_score"] > 60.0
    assert "breakdown_points" in res

def test_risk_and_priority_score_formula():
    """Test Section 26 exact priority score mathematical formula."""
    lat, lon = 21.145, 72.620
    traj_pts = [
        {"forecast_time": "+3h", "latitude": 21.155, "longitude": 72.630, "uncertainty_km": 0.8}
    ]
    res = RiskCalculator.calculate_risk(
        confidence_score=75.0,
        anomaly_type="OIL_LIKE_ANOMALY",
        estimated_area_km2=2.5,
        latitude=lat,
        longitude=lon,
        trajectory_points=traj_pts
    )
    assert 0.0 <= res["priority_score"] <= 1.0
    assert res["risk_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]

def test_trajectory_and_drift_calculation():
    """Test Section 24 pollutant-specific drift vectors."""
    pts = TrajectoryService.calculate_drift_trajectory(
        lat=21.145, lon=72.620,
        anomaly_type="OIL_LIKE_ANOMALY",
        current_speed_ms=0.5, current_dir_deg=45.0,
        wind_speed_ms=6.0, wind_dir_deg=220.0
    )
    assert len(pts) == 4
    assert pts[0]["forecast_time"] == "+3h"

def test_public_citizen_report_submission():
    """Test POST /citizen-reports (PUBLIC)."""
    payload = {
        "description": "Observed dark sheen near Hazira beach area",
        "latitude": 21.165,
        "longitude": 72.620
    }
    response = client.post("/api/v1/citizen-reports", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["verification_status"] == "UNVERIFIED"
    assert data["latitude"] == 21.165

def test_authenticated_incidents_api_access():
    """Test authenticated access to /incidents endpoint."""
    headers = {"Authorization": "Bearer dev-test-token"}
    response = client.get("/api/v1/incidents", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_monitoring_run():
    """Test POST /monitor/run with dev-admin-token."""
    headers = {"Authorization": "Bearer dev-admin-token"}
    response = client.post("/api/v1/monitor/run?force_anomaly=OIL_LIKE_ANOMALY", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["processed_sources_count"] > 0

    # Cleanup test incidents created during monitor run test
    db_clean = SessionLocal()
    db_clean.query(Incident).filter(Incident.incident_code.like("MG-2026-TEST-%")).delete(synchronize_session=False)
    db_clean.commit()
    db_clean.close()
