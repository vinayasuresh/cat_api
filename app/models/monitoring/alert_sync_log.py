from sqlalchemy import Column, Integer, DateTime, JSON
from sqlalchemy.sql import func
from app.db.session import Base

class AlertSyncLog(Base):
    """Model to track alert synchronization process results."""
    __tablename__ = "alert_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    total_alerts = Column(Integer, nullable=False)
    processed_count = Column(Integer, nullable=False, default=0)
    ignored_by_state = Column(Integer, nullable=False, default=0)
    ignored_by_missing_data = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    missing_states = Column(JSON, nullable=True)  # Store missing states as JSON array
    # Zipcode processing summary fields
    processed_same_codes = Column(Integer, nullable=False, default=0)
    skipped_same_codes = Column(Integer, nullable=False, default=0)
    found_zipcodes = Column(Integer, nullable=False, default=0)
    created_zipcode_mappings = Column(Integer, nullable=False, default=0)
    used_zipcode_mappings = Column(Integer, nullable=False, default=0)
    sync_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
