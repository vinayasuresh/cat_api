from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.common.events import Event
from app.schemas.common.event import EventCreate, EventUpdate, EventResponse
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    *,
    db: Session = Depends(get_db),
    event_in: EventCreate,
    current_user = Depends(get_current_user)
):
    """Create new event"""
    event = Event(
        name=event_in.name,
        description=event_in.description,
        status=event_in.status,
        created_by=current_user.id
    )
    db.add(event)
    try:
        db.commit()
        db.refresh(event)
    except Exception as e:
        db.rollback()
        if "duplicate key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event with this name already exists"
            )
        raise
    return event

@router.get("/events", response_model=List[EventResponse])
def get_events(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[bool] = None,
    name: Optional[str] = None,
):
    """Get list of events"""
    query = db.query(Event)
    if status is not None:
        query = query.filter(Event.status == status)
    if name:
        query = query.filter(Event.name.ilike(f"%{name}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Get event by ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/events/{event_id}", response_model=EventResponse)
def update_event(
    *,
    db: Session = Depends(get_db),
    event_id: int,
    event_in: EventUpdate,
    current_user = Depends(get_current_user)
):
    """Update event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event_in.dict(exclude_unset=True)
    update_data["updated_by"] = current_user.id
    
    for field, value in update_data.items():
        setattr(event, field, value)
    
    try:
        db.commit()
        db.refresh(event)
    except Exception as e:
        db.rollback()
        if "duplicate key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event with this name already exists"
            )
        raise
    return event

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    *,
    db: Session = Depends(get_db),
    event_id: int,
    current_user = Depends(get_current_user)
):
    """Delete event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Soft delete by updating status
    event.status = False
    event.updated_by = current_user.id
    db.commit()
    return None
