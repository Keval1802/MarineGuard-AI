from app.agents.state import MarineIncidentState
from app.mcp.server import mcp_server

class SourceInvestigationAgent:
    """
    Source Investigation Agent (Section 18.3).
    Estimates backward origin zones, queries nearby ports, river outlets, and vessel tracks.
    Strictly uses terms such as 'candidate source' or 'possible origin', never establishing legal guilt (Section 42).
    """

    @staticmethod
    async def run(state: MarineIncidentState) -> MarineIncidentState:
        lat = state["latitude"]
        lon = state["longitude"]
        anom_type = state["anomaly_type"]

        # Fetch environmental vectors for backward drift
        w_data = state.get("weather_evidence", [{}])[0]
        o_data = state.get("ocean_evidence", [{}])[0]

        curr_speed = o_data.get("current_speed_ms", 0.5)
        curr_dir = o_data.get("current_direction_deg", 45.0)
        wind_speed = w_data.get("wind_speed_ms", 5.0)
        wind_dir = w_data.get("wind_direction_deg", 215.0)

        # Query MCP tools for rivers, ports, SAR vessel detection & GFW slick-vessel correlation
        r_res = await mcp_server.call_tool("get_nearby_rivers", {"latitude": lat, "longitude": lon})
        p_res = await mcp_server.call_tool("get_nearby_ports", {"latitude": lat, "longitude": lon})
        sar_res = await mcp_server.call_tool("detect_sar_vessels", {"latitude": lat, "longitude": lon})
        corr_res = await mcp_server.call_tool("correlate_spill_vessels", {"latitude": lat, "longitude": lon})

        candidates = []

        # 1. SAR CA-CFAR Vessel Detections & GFW Correlation Match
        if corr_res.get("status") == "success":
            spill_corr = corr_res.get("spill_vessel_correlation", {})
            candidates.append({
                "source_type": "candidate_vessel_track",
                "reference": f"{spill_corr.get('ship_name', 'MMSI ' + str(spill_corr.get('mmsi')))} ({spill_corr.get('ship_type', 'TANKER')})",
                "confidence": "high" if spill_corr.get("correlation_score", 0) >= 70 else "moderate",
                "distance_km": spill_corr.get("minimum_distance_km", 1.8),
                "correlation_score": spill_corr.get("correlation_score", 85),
                "disclaimer": spill_corr.get("disclaimer", "Vessel associated with spill candidate; responsibility not established.")
            })

        if sar_res.get("status") == "success":
            for det in sar_res.get("detected_vessels", [])[:2]:
                candidates.append({
                    "source_type": "sar_vessel_detection",
                    "reference": f"SAR Bright Target {det['id']} (Strength: {det['sar_strength']})",
                    "confidence": "high" if det["confidence"] >= 0.85 else "moderate",
                    "distance_km": round(abs(det["latitude"] - lat) * 111.0, 2),
                    "disclaimer": "Sentinel-1 SAR VV CA-CFAR detection target candidate."
                })

        # 2. Nearby vessel traffic candidate fallback
        for vessel in state.get("vessel_evidence", []):
            candidates.append({
                "source_type": "candidate_vessel_track",
                "reference": vessel.get("lane_name", "Local Shipping Channel"),
                "confidence": "moderate",
                "distance_km": vessel.get("distance_km", 2.5),
                "disclaimer": "Candidate for investigation only; responsibility not established."
            })

        # 3. Nearby estuarine river outlets
        if r_res.get("status") == "success":
            for river in r_res.get("rivers", []):
                candidates.append({
                    "source_type": "candidate_estuary_outlet",
                    "reference": river["name"],
                    "confidence": "moderate" if river["distance_km"] < 5.0 else "low",
                    "distance_km": river["distance_km"],
                    "disclaimer": "Possible river-borne runoff candidate."
                })

        # 4. Nearby ports
        if p_res.get("status") == "success":
            for port in p_res.get("ports", []):
                candidates.append({
                    "source_type": "candidate_port_discharge",
                    "reference": port["name"],
                    "confidence": "moderate" if port["distance_km"] < 6.0 else "low",
                    "distance_km": port["distance_km"],
                    "disclaimer": "Possible port approach candidate."
                })

        state["possible_sources"] = candidates
        state["next_step"] = "assess_impact"

        return state
