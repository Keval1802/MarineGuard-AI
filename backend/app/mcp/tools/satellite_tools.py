from typing import Dict, Any, List, Optional
from datetime import datetime
from app.satellite.catalog import CopernicusCatalogService
from app.database import SessionLocal
from app.models.incident import Incident
from app.models.satellite import SatelliteObservation

class SatelliteMCPTools:
    """MCP Satellite Data & Image Tools."""

    @staticmethod
    async def search_satellite_observations(
        min_lon: float = 72.50, min_lat: float = 21.00,
        max_lon: float = 72.85, max_lat: float = 21.30
    ) -> Dict[str, Any]:
        """MCP Tool: Search for satellite observations over bounding box."""
        try:
            catalog = CopernicusCatalogService()
            scenes = await catalog.search_scenes(bbox=(min_lon, min_lat, max_lon, max_lat))
            return {"status": "success", "scenes": scenes}
        except Exception as e:
            return {"status": "error", "error_code": "source_unavailable", "message": str(e)}

    @staticmethod
    def get_latest_sentinel1_scene(incident_id: str) -> Dict[str, Any]:
        """MCP Tool: Retrieve latest Sentinel-1 SAR scene metadata for incident."""
        db = SessionLocal()
        try:
            obs = db.query(SatelliteObservation).filter(
                SatelliteObservation.incident_id == incident_id,
                SatelliteObservation.mission == "Sentinel-1"
            ).order_by(SatelliteObservation.acquisition_time.desc()).first()
            if not obs:
                return {"status": "error", "error_code": "data_not_available", "message": "No Sentinel-1 observation for this incident"}
            return {
                "status": "success",
                "product_id": obs.product_id,
                "acquisition_time": obs.acquisition_time.isoformat(),
                "detection_method": obs.detection_method,
                "wind_speed_ms": obs.wind_speed_ms,
                "confidence": obs.confidence,
                "image_path": obs.image_path
            }
        finally:
            db.close()

    @staticmethod
    def get_latest_sentinel2_scene(incident_id: str) -> Dict[str, Any]:
        """MCP Tool: Retrieve latest Sentinel-2 MSI optical scene metadata for incident."""
        db = SessionLocal()
        try:
            obs = db.query(SatelliteObservation).filter(
                SatelliteObservation.incident_id == incident_id,
                SatelliteObservation.mission == "Sentinel-2"
            ).order_by(SatelliteObservation.acquisition_time.desc()).first()
            if not obs:
                return {"status": "error", "error_code": "data_not_available", "message": "No Sentinel-2 observation for this incident"}
            return {
                "status": "success",
                "product_id": obs.product_id,
                "acquisition_time": obs.acquisition_time.isoformat(),
                "cloud_cover": obs.cloud_cover,
                "detection_method": obs.detection_method,
                "confidence": obs.confidence,
                "image_path": obs.image_path
            }
        finally:
            db.close()

    @staticmethod
    def get_satellite_evidence_image(incident_id: str) -> Dict[str, Any]:
        """MCP Tool: Fetch raw satellite evidence image path."""
        db = SessionLocal()
        try:
            obs = db.query(SatelliteObservation).filter(SatelliteObservation.incident_id == incident_id).first()
            if not obs or not obs.image_path:
                return {"status": "error", "error_code": "data_not_available", "message": "Raw satellite evidence image unavailable"}
            return {"status": "success", "image_path": obs.image_path}
        finally:
            db.close()

    @staticmethod
    def get_annotated_incident_image(incident_id: str) -> Dict[str, Any]:
        """MCP Tool: Fetch annotated mask overlay evidence image path."""
        db = SessionLocal()
        try:
            obs = db.query(SatelliteObservation).filter(SatelliteObservation.incident_id == incident_id).first()
            if not obs or not obs.annotated_image_path:
                return {"status": "error", "error_code": "data_not_available", "message": "Annotated incident image unavailable"}
            return {"status": "success", "annotated_image_path": obs.annotated_image_path}
        finally:
            db.close()

    @staticmethod
    def get_before_after_comparison_image(incident_id: str) -> Dict[str, Any]:
        """MCP Tool: Fetch side-by-side before/after comparative image path."""
        db = SessionLocal()
        try:
            obs = db.query(SatelliteObservation).filter(SatelliteObservation.incident_id == incident_id).first()
            if not obs or not obs.before_after_image_path:
                return {"status": "error", "error_code": "data_not_available", "message": "Before/after comparison image unavailable"}
            return {"status": "success", "before_after_image_path": obs.before_after_image_path}
        finally:
            db.close()
