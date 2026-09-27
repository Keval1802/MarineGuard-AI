from typing import Dict, Any, List
from app.environmental.weather import WeatherService
from app.environmental.ocean import OceanService
from app.environmental.tide import TideService
from app.environmental.gis import GISService
from app.services.trajectory import TrajectoryService

class EnvironmentalMCPTools:
    """MCP Environmental, Meteorological, Oceanographic & GIS Tools."""

    @staticmethod
    async def get_weather(latitude: float, longitude: float) -> Dict[str, Any]:
        """MCP Tool: Retrieve weather data (wind speed, direction, rainfall)."""
        try:
            data = await WeatherService.get_weather(latitude, longitude)
            return {"status": "success", "weather": data}
        except Exception as e:
            return {"status": "error", "error_code": "source_unavailable", "message": str(e)}

    @staticmethod
    async def get_ocean_current(latitude: float, longitude: float) -> Dict[str, Any]:
        """MCP Tool: Retrieve ocean current vector and sea surface temperature."""
        try:
            data = await OceanService.get_ocean_conditions(latitude, longitude)
            return {"status": "success", "ocean": data}
        except Exception as e:
            return {"status": "error", "error_code": "source_unavailable", "message": str(e)}

    @staticmethod
    def get_tide() -> Dict[str, Any]:
        """MCP Tool: Retrieve current tide status for Hazira / Gulf of Khambhat."""
        try:
            data = TideService.get_tide_status()
            return {"status": "success", "tide": data}
        except Exception as e:
            return {"status": "error", "error_code": "source_unavailable", "message": str(e)}

    @staticmethod
    def get_nearby_ports(latitude: float, longitude: float) -> Dict[str, Any]:
        """MCP Tool: Retrieve nearby ports within 20 km."""
        assets = GISService.get_nearby_assets(latitude, longitude, max_distance_km=20.0)
        ports = [a for a in assets if a["type"] == "port"]
        return {"status": "success", "ports": ports}

    @staticmethod
    def get_nearby_rivers(latitude: float, longitude: float) -> Dict[str, Any]:
        """MCP Tool: Retrieve nearby river estuaries within 20 km."""
        assets = GISService.get_nearby_assets(latitude, longitude, max_distance_km=20.0)
        rivers = [a for a in assets if a["type"] == "river_outlet"]
        return {"status": "success", "rivers": rivers}

    @staticmethod
    def get_sensitive_areas(latitude: float, longitude: float) -> Dict[str, Any]:
        """MCP Tool: Retrieve sensitive coastal areas (mangroves, beaches, wetlands)."""
        assets = GISService.get_nearby_assets(latitude, longitude, max_distance_km=20.0)
        sensitive = [a for a in assets if a["type"] in ["mangrove", "beach", "wetland", "fishing_zone"]]
        return {"status": "success", "sensitive_areas": sensitive}

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> Dict[str, Any]:
        """MCP Tool: Calculate great-circle distance in km."""
        dist = GISService.haversine_distance(lat1, lon1, lat2, lon2)
        return {"status": "success", "distance_km": round(dist, 3)}

    @staticmethod
    def calculate_drift(
        latitude: float, longitude: float, anomaly_type: str,
        current_speed_ms: float, current_dir_deg: float,
        wind_speed_ms: float, wind_dir_deg: float
    ) -> Dict[str, Any]:
        """MCP Tool: Calculate pollutant-specific drift trajectory."""
        pts = TrajectoryService.calculate_drift_trajectory(
            lat=latitude, lon=longitude, anomaly_type=anomaly_type,
            current_speed_ms=current_speed_ms, current_dir_deg=current_dir_deg,
            wind_speed_ms=wind_speed_ms, wind_dir_deg=wind_dir_deg
        )
        return {"status": "success", "predicted_trajectory": pts}
