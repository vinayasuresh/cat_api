from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.common.zones_counties import ZoneCounty
from app.models.common.zipcodes import Zipcode
import enum

class RegionType(str, enum.Enum):
    ZONE = "ZONE"
    COUNTY = "COUNTY"
    ZIPCODE = "ZIPCODE"

class AlertAffectedArea(Base):
    __tablename__ = "alert_affected_areas"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    zone_county_id = Column(Integer, ForeignKey("zones_counties.id"), nullable=True)
    zipcode_id = Column(Integer, ForeignKey("zipcodes.id"), nullable=True)
    region_type = Column(Enum(RegionType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Define relationships with foreign_keys to avoid ambiguity
    alert = relationship("Alert", foreign_keys=[alert_id], back_populates="affected_areas")
    zone_county = relationship("ZoneCounty", foreign_keys=[zone_county_id])
    zipcode = relationship("Zipcode", foreign_keys=[zipcode_id])
