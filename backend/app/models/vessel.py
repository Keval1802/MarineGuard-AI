from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class SarVesselDetection(Base):
    """
    Sentinel-1 SAR VV CA-CFAR vessel target detection object (Stage 3 & 4).
    """
    __tablename__ = "sar_vessel_detections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scene_id = Column(String(255), nullable=False, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    acquisition_time = Column(DateTime, nullable=False, index=True)
    
    backscatter = Column(Float, nullable=True)  # SAR VV gamma0 / sigma0 strength
    pixel_area = Column(Integer, default=1)     # Number of connected pixels
    confidence = Column(Float, default=0.85)    # CFAR signal-to-noise / confidence score
    created_at = Column(DateTime, default=datetime.utcnow)

class AISPosition(Base):
    """
    Continuous historical & live AIS broadcast position record (Stage 9 & 10).
    """
    __tablename__ = "ais_positions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mmsi = Column(String(32), nullable=False, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    sog = Column(Float, nullable=True)  # Speed Over Ground (knots)
    cog = Column(Float, nullable=True)  # Course Over Ground (degrees)
    heading = Column(Float, nullable=True)
    source = Column(String(100), default="AISStream/GFW")
    created_at = Column(DateTime, default=datetime.utcnow)

class Vessel(Base):
    """
    Vessel identity dataset record resolved via GFW Vessels API / MMSI (Stage 8 & 11).
    """
    __tablename__ = "vessels"

    mmsi = Column(String(32), primary_key=True)
    imo = Column(String(32), nullable=True, index=True)
    gfw_id = Column(String(255), nullable=True, index=True)
    
    ship_name = Column(String(255), nullable=True)
    ship_type = Column(String(100), nullable=True)
    flag = Column(String(10), nullable=True)
    callsign = Column(String(50), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OilSlick(Base):
    """
    Dark oil slick polygon & centroid detected from satellite imagery (Stage 12).
    """
    __tablename__ = "oil_slicks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scene_id = Column(String(255), nullable=False, index=True)
    centroid_lat = Column(Float, nullable=False, index=True)
    centroid_lon = Column(Float, nullable=False, index=True)
    area_km2 = Column(Float, nullable=False)
    orientation = Column(Float, default=0.0)  # Slick long-axis angle in degrees (0-360)
    
    polygon_json = Column(JSON, nullable=True)
    confidence = Column(Float, default=0.85)
    acquisition_time = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SpillVesselMatch(Base):
    """
    Correlation result linking an oil slick polygon to candidate vessel AIS tracks (Stage 14 & 15).
    """
    __tablename__ = "spill_vessel_matches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slick_id = Column(String(36), ForeignKey("oil_slicks.id", ondelete="CASCADE"), nullable=False, index=True)
    mmsi = Column(String(32), ForeignKey("vessels.mmsi", ondelete="CASCADE"), nullable=False, index=True)
    
    minimum_distance_km = Column(Float, nullable=False)
    time_difference_minutes = Column(Float, nullable=False)
    heading_difference_deg = Column(Float, nullable=False)
    correlation_score = Column(Float, nullable=False)  # 0 to 100
    
    label = Column(String(100), default="Vessel associated with spill candidate")
    details_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
