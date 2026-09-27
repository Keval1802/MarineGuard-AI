import pytest
import os
import asyncio
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.incident import Incident
from app.mcp.server import mcp_server
from app.rag.retriever import MarineRAGRetriever
from app.agents.graph import marineguard_workflow

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield

def test_mcp_environmental_tools():
    """Test MCP Weather, Ocean, Tide, and GIS tools."""
    async def run_test():
        w_res = await mcp_server.call_tool("get_weather", {"latitude": 21.145, "longitude": 72.620})
        assert w_res["status"] == "success"
        assert "wind_speed_ms" in w_res["weather"]

        o_res = await mcp_server.call_tool("get_ocean_current", {"latitude": 21.145, "longitude": 72.620})
        assert o_res["status"] == "success"
        assert "current_speed_ms" in o_res["ocean"]

        t_res = await mcp_server.call_tool("get_tide", {})
        assert t_res["status"] == "success"
        assert t_res["tide"]["tide_state"] in ["HIGH_TIDE", "EBB_TIDE", "LOW_TIDE", "FLOOD_TIDE"]

        ports_res = await mcp_server.call_tool("get_nearby_ports", {"latitude": 21.145, "longitude": 72.620})
        assert ports_res["status"] == "success"
        assert len(ports_res["ports"]) > 0

        rivers_res = await mcp_server.call_tool("get_nearby_rivers", {"latitude": 21.145, "longitude": 72.620})
        assert rivers_res["status"] == "success"
        assert len(rivers_res["rivers"]) > 0

    asyncio.run(run_test())

def test_mcp_drift_calculator_tool():
    """Test MCP calculate_drift tool."""
    async def run_test():
        res = await mcp_server.call_tool("calculate_drift", {
            "latitude": 21.145, "longitude": 72.620,
            "anomaly_type": "OIL_LIKE_ANOMALY",
            "current_speed_ms": 0.5, "current_dir_deg": 45.0,
            "wind_speed_ms": 6.0, "wind_dir_deg": 215.0
        })
        assert res["status"] == "success"
        assert len(res["predicted_trajectory"]) == 4

    asyncio.run(run_test())

def test_rag_knowledge_retriever():
    """Test RAG document ingestion and similarity retrieval."""
    retriever = MarineRAGRetriever()
    results = retriever.retrieve_guidelines("oil spill response procedure for mangroves", top_k=2)
    assert len(results) > 0
    assert "text" in results[0]
    assert "score" in results[0]

def test_langgraph_agent_workflow():
    """Test LangGraph multi-agent stateful workflow execution."""
    import uuid
    test_code = f"MG-TEST-{uuid.uuid4().hex[:6]}"
    async def run_test():
        db = SessionLocal()
        inc = Incident(
            incident_code=test_code,
            anomaly_type="OIL_LIKE_ANOMALY",
            latitude=21.145,
            longitude=72.620,
            confidence_score=70.0,
            priority_score=0.65,
            status="DETECTED"
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)
        inc_id = inc.id
        db.close()

        initial_state = {
            "incident_id": inc_id,
            "incident_code": test_code,
            "latitude": 21.145,
            "longitude": 72.620,
            "anomaly_type": "OIL_LIKE_ANOMALY",
            "first_detected": "2026-09-25T08:00:00Z",
            "last_updated": "2026-09-25T08:00:00Z",
            "satellite_evidence": [],
            "weather_evidence": [],
            "ocean_evidence": [],
            "vessel_evidence": [],
            "citizen_reports": [],
            "missing_sources": [],
            "possible_sources": [],
            "predicted_path": [],
            "affected_areas": [],
            "rag_passages": [],
            "confidence_score": 70.0,
            "severity_score": 0.65,
            "priority_score": 0.65,
            "risk_level": "HIGH",
            "status": "DETECTED",
            "report": None,
            "next_step": "collect_evidence"
        }

        final_state = await marineguard_workflow.ainvoke(initial_state)
        assert final_state["next_step"] == "END"
        assert final_state["report"] is not None
        assert "MARINEGUARD AI" in final_state["report"]
        assert len(final_state["possible_sources"]) > 0

        # Clean up temporary test incident
        db_clean = SessionLocal()
        db_clean.query(Incident).filter(Incident.id == inc_id).delete()
        db_clean.commit()
        db_clean.close()

    asyncio.run(run_test())

def test_reanalyze_api_with_langgraph():
    """Test POST /incidents/{incident_id}/reanalyze with admin token."""
    db = SessionLocal()
    inc = db.query(Incident).first()
    assert inc is not None
    inc_id = inc.id
    db.close()

    headers = {"Authorization": "Bearer dev-admin-token"}
    response = client.post(f"/api/v1/incidents/{inc_id}/reanalyze", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reanalysis_completed"
    assert "MARINEGUARD AI" in data["report"]

def test_rag_api_endpoints():
    """Test GET /api/v1/rag/documents and POST /api/v1/rag/query REST endpoints."""
    headers = {"Authorization": "Bearer dev-admin-token"}
    
    # Test GET documents
    doc_res = client.get("/api/v1/rag/documents", headers=headers)
    assert doc_res.status_code == 200
    doc_data = doc_res.json()
    assert doc_data["status"] == "success"
    assert doc_data["total_chunks"] > 0
    assert len(doc_data["documents"]) > 0

    # Test POST query
    query_res = client.post("/api/v1/rag/query", json={"query": "MARPOL oil discharge limit eez", "top_k": 2}, headers=headers)
    assert query_res.status_code == 200
    query_data = query_res.json()
    assert query_data["status"] == "success"
    assert len(query_data["passages"]) > 0

    # Test POST scrape
    scrape_res = client.post("/api/v1/rag/scrape", json={
        "url": "https://en.wikipedia.org/wiki/2017_Ennore_oil_spill",
        "doc_identifier": "ennore_oil_spill_history",
        "auto_reindex": True
    }, headers=headers)
    assert scrape_res.status_code == 200
    scrape_data = scrape_res.json()
    assert scrape_data["status"] == "success"
    assert "web_ennore_oil_spill_history.txt" in scrape_data["filename"]
    assert scrape_data["total_rag_chunks"] > 0

def test_mcp_api_endpoints():
    """Test GET /api/v1/mcp/tools and POST /api/v1/mcp/call REST endpoints."""
    headers = {"Authorization": "Bearer dev-admin-token"}
    
    # Test GET tools
    tools_res = client.get("/api/v1/mcp/tools", headers=headers)
    assert tools_res.status_code == 200
    tools_data = tools_res.json()
    assert tools_data["status"] == "success"
    assert tools_data["total_tools"] > 0

    # Test POST call get_weather
    call_res = client.post("/api/v1/mcp/call", json={
        "tool_name": "get_weather",
        "arguments": {"latitude": 21.145, "longitude": 72.620}
    }, headers=headers)
    assert call_res.status_code == 200
    call_data = call_res.json()
    assert call_data["status"] == "success"
    assert "wind_speed_ms" in call_data["weather"]

    # Test POST call web_search_maritime
    web_res = client.post("/api/v1/mcp/call", json={
        "tool_name": "web_search_maritime",
        "arguments": {"query": "Gulf of Khambhat oil spill advisory", "max_results": 2}
    }, headers=headers)
    assert web_res.status_code == 200
    web_data = web_res.json()
    assert web_data["status"] in ["success", "error"]


