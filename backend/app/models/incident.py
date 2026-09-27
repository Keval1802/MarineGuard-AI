from sqlalchemy import Column, String, Float, DateTime, Text, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
import uuid
from app.database import Base

class AnomalyType(str, enum.Enum):
    NORMAL = "NORMAL"
    SURFACE_ANOMALY = "SURFACE_ANOMALY"
    OIL_LIKE_ANOMALY = "OIL_LIKE_ANOMALY"
    FLOATING_MATERIAL_CANDIDATE = "FLOATING_MATERIAL_CANDIDATE"
    HIGH_TURBIDITY_EVENT = "HIGH_TURBIDITY_EVENT"
    UNKNOWN = "UNKNOWN"

class IncidentStatus(str, enum.Enum):
    DETECTED = "DETECTED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    POSSIBLE = "POSSIBLE"
    LIKELY = "LIKELY"
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    MONITORING = "MONITORING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    FALSE_POSITIVE = "FALSE_POSITIVE"

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_code = Column(String(32), unique=True, nullable=False, index=True)
    anomaly_type = Column(String(50), default=AnomalyType.UNKNOWN.value, nullable=False)
    
    # Current known location (Section 21 - updated when new evidence or drift occurs)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    location_name = Column(String(255), default="Unknown Marine Region", nullable=True)
    
    first_detected = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    
    confidence_score = Column(Float, default=0.0)  # 0 to 100
    severity_score = Column(Float, default=0.0)    # 0 to 1
    priority_score = Column(Float, default=0.0)    # 0 to 1
    
    status = Column(String(50), default=IncidentStatus.DETECTED.value, nullable=False)
    report = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    satellite_observations = relationship("SatelliteObservation", back_populates="incident", cascade="all, delete-orphan")
    weather_observations = relationship("WeatherObservation", back_populates="incident", cascade="all, delete-orphan")
    ocean_observations = relationship("OceanObservation", back_populates="incident", cascade="all, delete-orphan")
    vessel_events = relationship("VesselEvent", back_populates="incident", cascade="all, delete-orphan")
    citizen_reports = relationship("CitizenReport", back_populates="incident")
    candidate_sources = relationship("CandidateSource", back_populates="incident", cascade="all, delete-orphan")
    predicted_paths = relationship("PredictedPath", back_populates="incident", cascade="all, delete-orphan")
    affected_areas = relationship("AffectedArea", back_populates="incident", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="incident", cascade="all, delete-orphan")
