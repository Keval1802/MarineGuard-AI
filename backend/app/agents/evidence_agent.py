from app.agents.state import MarineIncidentState
from app.mcp.server import mcp_server

class EvidenceAgent:
    """
    Evidence Agent (Section 18.2).
    Gathers multi-source evidence via MCP tools (weather, ocean, vessel activity, satellite images).
    Tracks missing evidence sources without inventing data (Section 19).
    """

    @staticmethod
    async def run(state: MarineIncidentState) -> MarineIncidentState:
        lat = state["latitude"]
        lon = state["longitude"]
        inc_id = state["incident_id"]
        missing = []

        # 1. Weather evidence
        w_res = await mcp_server.call_tool("get_weather", {"latitude": lat, "longitude": lon})
        if w_res["status"] == "success":
            state["weather_evidence"] = [w_res["weather"]]
        else:
            missing.append("weather")

        # 2. Ocean current evidence
        o_res = await mcp_server.call_tool("get_ocean_current", {"latitude": lat, "longitude": lon})
        if o_res["status"] == "success":
            state["ocean_evidence"] = [o_res["ocean"]]
        else:
            missing.append("ocean_current")

        # 3. Vessel activity evidence
        v_res = await mcp_server.call_tool("get_vessel_tracks", {"latitude": lat, "longitude": lon, "radius_km": 10.0})
        if v_res["status"] == "success":
            state["vessel_evidence"] = v_res["candidate_vessels"]
        else:
            missing.append("vessel_tracks")

        # 4. Satellite visual evidence image paths
        raw_res = await mcp_server.call_tool("get_satellite_evidence_image", {"incident_id": inc_id})
        ann_res = await mcp_server.call_tool("get_annotated_incident_image", {"incident_id": inc_id})
        comp_res = await mcp_server.call_tool("get_before_after_comparison_image", {"incident_id": inc_id})

        sat_ev = {
            "raw_image": raw_res.get("image_path"),
            "annotated_image": ann_res.get("annotated_image_path"),
            "comparison_image": comp_res.get("before_after_image_path")
        }
        state["satellite_evidence"] = [sat_ev]

        # 5. Multimodal Vision Verifier (reclassifies estuarine mudflats & sediment turbidity)
        try:
            from app.agents.vision_verifier import LLMVisionVerifier
            img_for_verification = ann_res.get("annotated_image_path") or raw_res.get("image_path")
            if img_for_verification:
                verification_res = await LLMVisionVerifier.verify_anomaly_with_llm(
                    image=img_for_verification,
                    sensor="Sentinel-1 SAR / Sentinel-2 Optical",
                    candidate_class=state.get("anomaly_type", "OIL_LIKE_ANOMALY"),
                    confidence=state.get("confidence_score", 65.0) / 100.0,
                    area_km2=1.8
                )
                if verification_res:
                    verified_cls = verification_res.get("verified_class")
                    if verified_cls and verified_cls != state.get("anomaly_type"):
                        state["anomaly_type"] = verified_cls
                    if "verified_confidence" in verification_res:
                        state["confidence_score"] = round(verification_res["verified_confidence"] * 100.0, 1)
        except Exception as v_err:
            print(f"[EvidenceAgent] Vision verification notice: {v_err}")

        state["missing_sources"] = missing
        state["next_step"] = "investigate_source"

        return state
