from typing import TypedDict, List, Dict, Any, Optional

class MarineIncidentState(TypedDict):
    """
    LangGraph Incident Investigation State (Section 21).
    Maintains persistent workflow state across agent execution nodes.
    """
    incident_id: str
    incident_code: str
    latitude: float
    longitude: float
    anomaly_type: str
    first_detected: str
    last_updated: str
    
    # Evidence Collections
    satellite_evidence: List[Dict[str, Any]]
    weather_evidence: List[Dict[str, Any]]
    ocean_evidence: List[Dict[str, Any]]
    vessel_evidence: List[Dict[str, Any]]
    citizen_reports: List[Dict[str, Any]]
    missing_sources: List[str]
    
    # Analysis Results
    possible_sources: List[Dict[str, Any]]
    predicted_path: List[Dict[str, Any]]
    affected_areas: List[Dict[str, Any]]
    rag_passages: List[Dict[str, Any]]
    
    # Scoring & Status
    confidence_score: float
    severity_score: float
    priority_score: float
    risk_level: str
    status: str
    
    # Synthesized Output Report
    report: Optional[str]
    next_step: str
