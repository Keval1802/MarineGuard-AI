import math
from typing import List, Dict, Any, Tuple

class TrajectoryService:
    """
    Pollutant-specific drift and backward origin trajectory calculator (Sections 23 & 24).
    Enforces pollutant-specific windage factors.
    """

    @classmethod
    def calculate_drift_trajectory(
        cls,
        lat: float,
        lon: float,
        anomaly_type: str,
        current_speed_ms: float,
        current_dir_deg: float,
        wind_speed_ms: float,
        wind_dir_deg: float,
        hours_forecast: List[int] = [3, 6, 12, 24]
    ) -> List[Dict[str, Any]]:
        """
        Calculates forward drift trajectory for specified hours ahead.
        """
        # 1. Determine Pollutant-Specific Windage Coefficient (Section 24)
        if anomaly_type == "OIL_LIKE_ANOMALY":
            windage_factor = 0.03       # 3% of wind speed
            wind_deflection_deg = 15.0  # ~15 degree Coriolis/surface shear deflection
        elif anomaly_type == "FLOATING_MATERIAL_CANDIDATE":
            windage_factor = 0.045      # ~4.5% higher emergent windage for floating solid waste
            wind_deflection_deg = 5.0
        elif anomaly_type == "HIGH_TURBIDITY_EVENT":
            windage_factor = 0.005      # ~0% wind influence for suspended sediment plume
            wind_deflection_deg = 0.0
        else:
            windage_factor = 0.025
            wind_deflection_deg = 10.0

        # Current Vector (u_curr, v_curr) in m/s
        curr_rad = math.radians(current_dir_deg)
        u_curr = current_speed_ms * math.sin(curr_rad)
        v_curr = current_speed_ms * math.cos(curr_rad)

        # Wind Vector (u_wind, v_wind) in m/s with deflection
        effective_wind_dir = (wind_dir_deg + wind_deflection_deg) % 360.0
        wind_rad = math.radians(effective_wind_dir)
        u_wind = (wind_speed_ms * windage_factor) * math.sin(wind_rad)
        v_wind = (wind_speed_ms * windage_factor) * math.cos(wind_rad)

        # Net Combined Velocity Vector (m/s)
        u_net = u_curr + u_wind
        v_net = v_curr + v_wind

        # Convert m/s displacement to approx Lat/Lon degrees
        # 1 deg latitude ≈ 111,000 meters; 1 deg longitude ≈ 111,000 * cos(lat) meters
        lat_per_meter = 1.0 / 111000.0
        lon_per_meter = 1.0 / (111000.0 * math.cos(math.radians(lat)))

        forecast_points = []
        for hr in hours_forecast:
            dt_seconds = hr * 3600.0
            delta_y_m = v_net * dt_seconds  # Northward meters
            delta_x_m = u_net * dt_seconds  # Eastward meters

            next_lat = lat + (delta_y_m * lat_per_meter)
            next_lon = lon + (delta_x_m * lon_per_meter)

            # Dynamic uncertainty calculation incorporating wind turbulence, current velocity, and pollutant class
            wind_scale = (wind_speed_ms / 5.0) * 0.12
            current_scale = (current_speed_ms / 0.5) * 0.10
            pollutant_dispersion = 0.04 if anomaly_type == "HIGH_TURBIDITY_EVENT" else (0.07 if anomaly_type == "OIL_LIKE_ANOMALY" else 0.11)

            uncertainty_km = round(0.25 + hr * (wind_scale + current_scale + pollutant_dispersion), 2)

            forecast_points.append({
                "forecast_time": f"+{hr}h",
                "latitude": round(next_lat, 5),
                "longitude": round(next_lon, 5),
                "uncertainty": uncertainty_km,
                "uncertainty_km": uncertainty_km
            })

        return forecast_points

    @classmethod
    def calculate_reverse_origin_zone(
        cls,
        lat: float,
        lon: float,
        anomaly_type: str,
        current_speed_ms: float,
        current_dir_deg: float,
        wind_speed_ms: float,
        wind_dir_deg: float,
        hours_back: int = 12
    ) -> Dict[str, Any]:
        """
        Calculates backward drift trajectory to estimate probable origin region (Section 23).
        """
        # Reverse forward vectors
        reverse_curr_dir = (current_dir_deg + 180.0) % 360.0
        reverse_wind_dir = (wind_dir_deg + 180.0) % 360.0

        back_pts = cls.calculate_drift_trajectory(
            lat, lon, anomaly_type, current_speed_ms, reverse_curr_dir, wind_speed_ms, reverse_wind_dir, [hours_back]
        )

        origin_pt = back_pts[0]
        return {
            "origin_latitude": origin_pt["latitude"],
            "origin_longitude": origin_pt["longitude"],
            "estimated_hours_ago": hours_back,
            "origin_radius_km": round(origin_pt["uncertainty_km"] * 1.5, 2)
        }
