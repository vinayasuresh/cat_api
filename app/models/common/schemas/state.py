from pydantic import BaseModel, constr
from typing import Optional
from datetime import datetime

class StateBase(BaseModel):
    code: constr(max_length=10)
    name: constr(max_length=100)
    status: bool = True

class StateCreate(StateBase):
    pass

class StateUpdate(StateBase):
    code: Optional[constr(max_length=10)] = None
    name: Optional[constr(max_length=100)] = None
    status: Optional[bool] = None

class StateInDBBase(StateBase):
    id: int
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class State(StateInDBBase):
    pass

class StateResponse(State):
    pass
