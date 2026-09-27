from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class SatelliteObservation(Base):
    __tablename__ = "satellite_observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    mission = Column(String(50), nullable=False)  # e.g., Sentinel-1, Sentinel-2, Sentinel-3
    product_id = Column(String(255), nullable=False)
    acquisition_time = Column(DateTime, nullable=False)
    cloud_cover = Column(Float, nullable=True)  # Percentage 0-100
    
    image_path = Column(String(500), nullable=True)  # Raw scene or AOI crop path
    annotated_image_path = Column(String(500), nullable=True)
    before_after_image_path = Column(String(500), nullable=True)
    
    model_result = Column(String(100), nullable=True)
    detection_method = Column(String(100), nullable=False)  # sar_dark_patch, floating_debris_index, turbidity_index, statistical_outlier
    wind_speed_ms = Column(Float, nullable=True)  # Populated for oil/SAR wind gate audits
    confidence = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="satellite_observations")

class ProcessedSourceItem(Base):
    __tablename__ = "processed_source_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_name = Column(String(100), nullable=False, index=True)  # e.g. sentinel1, sentinel2, weather_feed
    source_item_id = Column(String(255), unique=True, nullable=False, index=True)
    acquisition_time = Column(DateTime, nullable=True)
    processed = Column(Boolean, default=True)
    processed_at = Column(DateTime, default=datetime.utcnow)
    checksum = Column(String(64), nullable=True)
