from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.monitoring.alert import AlertStatus, AlertSeverity

class AlertBase(BaseModel):
    title: str
    description: str
    status: AlertStatus = AlertStatus.NEW
    severity: AlertSeverity
    state_id: Optional[int] = None  # Changed from state: str to state_id: Optional[int]
    source: str
    external_id: str
    event_timestamp: datetime
    event_type: str

class AlertCreate(AlertBase):
    pass

class AlertUpdate(AlertBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AlertStatus] = None
    severity: Optional[AlertSeverity] = None
    state_id: Optional[int] = None  # Changed from state to state_id
    source: Optional[str] = None
    external_id: Optional[str] = None
    event_timestamp: Optional[datetime] = None

class AlertInDBBase(AlertBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class Alert(AlertInDBBase):
    pass

class AlertResponse(Alert):
    pass
