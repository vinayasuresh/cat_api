from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class AlertStatus(str, enum.Enum):
    NEW = "NEW"
    READ = "READ"
    ARCHIVED = "ARCHIVED"

class AlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(Enum(AlertStatus), default=AlertStatus.NEW)
    severity = Column(Enum(AlertSeverity), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    source = Column(String)
    event_type = Column(String, index=True, nullable=True)
    external_id = Column(String, unique=True, index=True)
    event_timestamp = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Define relationships
    affected_areas = relationship("AlertAffectedArea", cascade="all, delete-orphan")
    state = relationship("State", lazy="joined")
