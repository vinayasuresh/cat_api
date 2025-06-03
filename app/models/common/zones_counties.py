from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.session import Base
from app.models.auth.user import User
import enum

class RegionType(enum.Enum):
    ZONE = "ZONE"
    COUNTY = "COUNTY"

class ZoneCounty(Base):
    __tablename__ = "zones_counties"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    fips = Column(String(5), nullable=False)
    type = Column(Enum(RegionType), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    status = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
