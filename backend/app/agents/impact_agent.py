from app.agents.state import MarineIncidentState
from app.mcp.server import mcp_server
from app.services.risk import RiskCalculator

class ImpactAgent:
    """
    Impact and Trajectory Agent (Section 18.4).
    Calculates multi-hour pollutant drift trajectory and intersects path with sensitive GIS layers.
    """

    @staticmethod
    async def run(state: MarineIncidentState) -> MarineIncidentState:
        lat = state["latitude"]
        lon = state["longitude"]
        anom_type = state["anomaly_type"]

        w_data = state.get("weather_evidence", [{}])[0]
        o_data = state.get("ocean_evidence", [{}])[0]

        curr_speed = o_data.get("current_speed_ms", 0.5)
        curr_dir = o_data.get("current_direction_deg", 45.0)
        wind_speed = w_data.get("wind_speed_ms", 5.0)
        wind_dir = w_data.get("wind_direction_deg", 215.0)

        # MCP Tool: calculate drift
        drift_res = await mcp_server.call_tool("calculate_drift", {
            "latitude": lat, "longitude": lon, "anomaly_type": anom_type,
            "current_speed_ms": curr_speed, "current_dir_deg": curr_dir,
            "wind_speed_ms": wind_speed, "wind_dir_deg": wind_dir
        })

        if drift_res.get("status") == "success":
            state["predicted_path"] = drift_res["predicted_trajectory"]
        else:
            state["predicted_path"] = []

        # Risk & Priority Score Math
        risk_res = RiskCalculator.calculate_risk(
            confidence_score=state.get("confidence_score", 65.0),
            anomaly_type=anom_type,
            estimated_area_km2=1.8,
            latitude=lat,
            longitude=lon,
            trajectory_points=state["predicted_path"]
        )

        state["priority_score"] = risk_res["priority_score"]
        state["severity_score"] = risk_res["severity_score"]
        state["risk_level"] = risk_res["risk_level"]
        state["affected_areas"] = risk_res["affected_areas"]
        state["next_step"] = "generate_report"

        return state
