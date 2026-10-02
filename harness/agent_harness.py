import asyncio
from typing import Dict, Any

class AgentWorkflowHarness:
    """Executes and verifies LangGraph agentic reasoning workflows offline."""

    @staticmethod
    async def run_workflow_test(incident_payload: Dict[str, Any]) -> Dict[str, Any]:
        from app.agents.graph import marineguard_workflow
        
        final_state = await marineguard_workflow.ainvoke(incident_payload)
        
        conf = final_state.get("confidence_score", 0.0)
        pri = final_state.get("priority_score", 0.0)
        
        assert 0.0 <= conf <= 100.0, f"Invalid confidence score: {conf}"
        assert 0.0 <= pri <= 1.0, f"Invalid priority score: {pri}"
        assert final_state.get("report") is not None, "Report text missing"
        
        return {
            "passed": True,
            "confidence_score": conf,
            "priority_score": pri,
            "status": final_state.get("status")
        }

    @staticmethod
    async def run_all_pollutants_harness_test() -> Dict[str, Dict[str, Any]]:
        """
        Executes end-to-end analysis across ALL marine pollutant types:
        1. OIL_LIKE_ANOMALY (Petroleum / Fuel Hydrocarbons)
        2. FLOATING_MATERIAL_CANDIDATE (Plastic Debris / Algal Bloom / Chemical Sheen)
        3. SURFACE_ANOMALY (Unclassified Surface Film / Thermal Plume)
        4. HIGH_TURBIDITY_EVENT (Natural Estuarine Sediment / Mudflats)
        5. FALSE_POSITIVE (Cloud / Sensor Artifact / Coastal Land Crop)
        """
        from app.services.risk import RiskCalculator

        pollutant_types = [
            "OIL_LIKE_ANOMALY",
            "FLOATING_MATERIAL_CANDIDATE",
            "SURFACE_ANOMALY",
            "HIGH_TURBIDITY_EVENT",
            "FALSE_POSITIVE"
        ]

        results = {}
        for ptype in pollutant_types:
            res = RiskCalculator.calculate_risk(
                confidence_score=75.0,
                anomaly_type=ptype,
                estimated_area_km2=2.5,
                latitude=21.145,
                longitude=72.620,
                trajectory_points=[{"latitude": 21.145, "longitude": 72.620}]
            )
            results[ptype] = {
                "priority_score": res["priority_score"],
                "risk_level": res["risk_level"],
                "base_severity": res["base_severity"]
            }
        return results
