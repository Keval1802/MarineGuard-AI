from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class IncidentBase(BaseModel):
    anomaly_type: str
    latitude: float
    longitude: float
    location_name: Optional[str] = "Unknown Marine Region"
    status: str

class IncidentCreate(IncidentBase):
    incident_code: Optional[str] = None
    confidence_score: float = 0.0
    severity_score: float = 0.0
    priority_score: float = 0.0

class SatelliteObservationSchema(BaseModel):
    id: str
    mission: str
    product_id: str
    acquisition_time: datetime
    cloud_cover: Optional[float] = None
    image_path: Optional[str] = None
    annotated_image_path: Optional[str] = None
    before_after_image_path: Optional[str] = None
    model_result: Optional[str] = None
    detection_method: str
    wind_speed_ms: Optional[float] = None
    confidence: float

    model_config = ConfigDict(from_attributes=True)

class IncidentResponse(IncidentBase):
    id: str
    incident_code: str
    first_detected: datetime
    last_updated: datetime
    confidence_score: float
    severity_score: float
    priority_score: float
    report: Optional[str] = None
    satellite_observations: List[SatelliteObservationSchema] = []

    model_config = ConfigDict(from_attributes=True)

class IncidentDetailResponse(IncidentResponse):
    satellite_observations: List[SatelliteObservationSchema] = []
    weather_observations: List[Any] = []
    ocean_observations: List[Any] = []
    vessel_events: List[Any] = []
    citizen_reports: List[Any] = []
    candidate_sources: List[Any] = []
    predicted_paths: List[Any] = []
    affected_areas: List[Any] = []
    alerts: List[Any] = []

class CitizenReportCreate(BaseModel):
    description: str
    latitude: float
    longitude: float
    image_path: Optional[str] = None

class CitizenReportResponse(CitizenReportCreate):
    id: str
    submitted_at: datetime
    verification_status: str
    incident_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
