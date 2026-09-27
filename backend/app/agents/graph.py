from langgraph.graph import StateGraph, END
from app.agents.state import MarineIncidentState
from app.agents.router_agent import RouterAgent
from app.agents.evidence_agent import EvidenceAgent
from app.agents.source_agent import SourceInvestigationAgent
from app.agents.impact_agent import ImpactAgent
from app.agents.report_agent import ReportAgent

def route_next_node(state: MarineIncidentState) -> str:
    """Conditional routing function evaluating state['next_step']."""
    step = state.get("next_step", "generate_report")
    if step == "collect_evidence":
        return "evidence_node"
    elif step == "investigate_source":
        return "source_node"
    elif step == "assess_impact":
        return "impact_node"
    elif step == "generate_report":
        return "report_node"
    return END

async def run_evidence_node(state: MarineIncidentState) -> MarineIncidentState:
    return await EvidenceAgent.run(state)

async def run_source_node(state: MarineIncidentState) -> MarineIncidentState:
    return await SourceInvestigationAgent.run(state)

async def run_impact_node(state: MarineIncidentState) -> MarineIncidentState:
    return await ImpactAgent.run(state)

def run_report_node(state: MarineIncidentState) -> MarineIncidentState:
    return ReportAgent.run(state)

def build_marineguard_agent_graph():
    """
    Compiles LangGraph StateGraph linking multi-agent investigation workflow (Section 17).
    """
    builder = StateGraph(MarineIncidentState)

    # Add agent nodes
    builder.add_node("router_node", RouterAgent.run)
    builder.add_node("evidence_node", run_evidence_node)
    builder.add_node("source_node", run_source_node)
    builder.add_node("impact_node", run_impact_node)
    builder.add_node("report_node", run_report_node)

    # Set entry point
    builder.set_entry_point("router_node")

    # Add conditional routing edges
    builder.add_conditional_edges(
        "router_node",
        route_next_node,
        {
            "evidence_node": "evidence_node",
            "source_node": "source_node",
            "impact_node": "impact_node",
            "report_node": "report_node",
            END: END
        }
    )

    builder.add_edge("evidence_node", "source_node")
    builder.add_edge("source_node", "impact_node")
    builder.add_edge("impact_node", "report_node")
    builder.add_edge("report_node", END)

    return builder.compile()

marineguard_workflow = build_marineguard_agent_graph()
