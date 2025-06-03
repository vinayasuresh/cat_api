from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: bool = True

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None

class EventResponse(EventBase):
    id: int
    created_by: int
    created_at: datetime
    updated_by: Optional[int] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
