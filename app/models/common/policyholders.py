from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.db.session import Base
from app.models.auth.user import User


class Policyholder(Base):
    __tablename__ = "policyholders"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)  # policyholder name
    zipcode_id = Column(Integer, ForeignKey("zipcodes.id"), nullable=False)
    claims = Column(Integer, default=0)
    premium = Column(Float, default=0.0)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    county_id = Column(Integer, ForeignKey("zones_counties.id"), nullable=True)  # for county or zone
    address = Column(String(255), nullable=True)
    email = Column(String(100), nullable=True)
    phoneno = Column(String(20), nullable=True)
    status = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
