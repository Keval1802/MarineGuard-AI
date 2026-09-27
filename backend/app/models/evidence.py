from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    wind_speed = Column(Float, nullable=False)      # m/s
    wind_direction = Column(Float, nullable=False)  # degrees (0-360)
    rainfall = Column(Float, default=0.0)           # mm/h
    source = Column(String(100), default="Open-Meteo")

    incident = relationship("Incident", back_populates="weather_observations")

class OceanObservation(Base):
    __tablename__ = "ocean_observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    current_speed = Column(Float, nullable=False)      # m/s
    current_direction = Column(Float, nullable=False)  # degrees (0-360)
    tide = Column(String(50), default="EBB")           # FLOOD, EBB, HIGH, LOW
    sea_surface_temperature = Column(Float, nullable=True) # Celsius
    source = Column(String(100), default="Copernicus-Marine/Open-Meteo")

    incident = relationship("Incident", back_populates="ocean_observations")

class VesselEvent(Base):
    __tablename__ = "vessel_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    vessel_identifier = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=True)        # knots
    direction = Column(Float, nullable=True)    # degrees
    distance_from_incident = Column(Float, nullable=False) # km

    incident = relationship("Incident", back_populates="vessel_events")

class CitizenReport(Base):
    __tablename__ = "citizen_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    image_path = Column(String(500), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    verification_status = Column(String(50), default="UNVERIFIED")  # UNVERIFIED, VERIFIED, REJECTED

    incident = relationship("Incident", back_populates="citizen_reports")

class CandidateSource(Base):
    __tablename__ = "candidate_sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    source_type = Column(String(100), nullable=False)  # vessel_activity, river_outlet, port_discharge, coastal_industry
    reference = Column(String(255), nullable=False)
    confidence = Column(String(50), default="moderate")  # low, moderate, high
    evidence_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="candidate_sources")

class PredictedPath(Base):
    __tablename__ = "predicted_paths"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    forecast_time = Column(String(50), nullable=False)  # e.g., "+3h", "+6h", "+12h", "+24h"
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    uncertainty = Column(Float, default=0.5)  # radius in km

    incident = relationship("Incident", back_populates="predicted_paths")

class AffectedArea(Base):
    __tablename__ = "affected_areas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    area_type = Column(String(100), nullable=False)  # mangrove, beach, wetland, fishing_zone, port, settlement
    area_name = Column(String(255), nullable=False)
    distance_km = Column(Float, nullable=False)
    risk_level = Column(String(50), default="MODERATE") # LOW, MODERATE, HIGH, CRITICAL

    incident = relationship("Incident", back_populates="affected_areas")
