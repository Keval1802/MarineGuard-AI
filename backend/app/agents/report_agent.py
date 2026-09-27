from app.agents.state import MarineIncidentState
from app.rag.retriever import MarineRAGRetriever
from app.services.report_service import ReportService

class ReportAgent:
    """
    Risk and Report Agent (Section 18.5).
    Queries RAG retriever for response procedures and coastal guidelines,
    synthesizes evidence, respects Section 40 Output Guardrails, and generates structured report.
    """

    @staticmethod
    def run(state: MarineIncidentState) -> MarineIncidentState:
        retriever = MarineRAGRetriever()
        
        # Query RAG knowledge store for relevant response procedures
        query_str = f"Response guidelines for {state['anomaly_type']} in Gujarat mangroves and ports"
        rag_chunks = retriever.retrieve_guidelines(query_str, top_k=2)
        state["rag_passages"] = rag_chunks

        rag_summary = ""
        if rag_chunks:
            rag_summary = "RAG Knowledge Base Guidelines:\n" + "\n".join([f"- ({c['source']}): {c['text'][:150]}..." for c in rag_chunks])

        # Generate deterministic report
        w_data = state.get("weather_evidence", [{}])[0]
        o_data = state.get("ocean_evidence", [{}])[0]

        report_text = ReportService.generate_deterministic_report(
            incident_code=state["incident_code"],
            anomaly_type=state["anomaly_type"],
            latitude=state["latitude"],
            longitude=state["longitude"],
            confidence_score=state.get("confidence_score", 65.0),
            confidence_level="HIGH" if state.get("confidence_score", 65.0) >= 50.0 else "MODERATE",
            priority_score=state.get("priority_score", 0.65),
            risk_level=state.get("risk_level", "HIGH"),
            estimated_area_km2=1.8,
            weather_data=w_data,
            ocean_data=o_data,
            candidate_sources=state.get("possible_sources", []),
            predicted_path=state.get("predicted_path", []),
            affected_areas=state.get("affected_areas", []),
            agent_synthesis=rag_summary
        )

        state["report"] = report_text
        state["status"] = "UNDER_INVESTIGATION"
        state["next_step"] = "END"
        return state
