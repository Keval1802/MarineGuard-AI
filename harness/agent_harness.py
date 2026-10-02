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
