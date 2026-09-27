from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    alert_type = Column(String(50), nullable=False) # EMAIL, DASHBOARD, HIGH_PRIORITY
    recipient = Column(String(255), nullable=False)
    status = Column(String(50), default="QUEUED")  # QUEUED, SENT, FAILED, QUOTA_EXHAUSTED
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="alerts")
