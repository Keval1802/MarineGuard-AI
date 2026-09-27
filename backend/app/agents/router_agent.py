from app.agents.state import MarineIncidentState

class RouterAgent:
    """
    Router / Incident Agent (Section 18.1).
    Determines investigation workflow steps and routes graph execution.
    """

    @staticmethod
    def run(state: MarineIncidentState) -> MarineIncidentState:
        """Determines next workflow step based on incident status and missing evidence."""
        state["last_updated"] = state.get("last_updated", "")
        
        # If incident has no weather or ocean evidence, route to Evidence Agent
        if not state.get("weather_evidence") or not state.get("ocean_evidence"):
            state["next_step"] = "collect_evidence"
        # Next route to Source Investigation Agent
        elif not state.get("possible_sources"):
            state["next_step"] = "investigate_source"
        # Next route to Impact & Trajectory Agent
        elif not state.get("predicted_path"):
            state["next_step"] = "assess_impact"
        # Finally route to Risk & Report Agent
        else:
            state["next_step"] = "generate_report"

        return state
