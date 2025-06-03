from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.db.session import get_db
from app.models.common.state import State
from app.schemas.common.state import StateCreate, StateUpdate, StateResponse
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/states", response_model=StateResponse, status_code=status.HTTP_201_CREATED)
def create_state(
    *,
    db: Session = Depends(get_db),
    state_in: StateCreate,
    current_user = Depends(get_current_user)
):
    """Create new state"""
    state = State(
        code=state_in.code,
        name=state_in.name,
        status=state_in.status,
        created_by=current_user.id
    )
    db.add(state)
    try:
        db.commit()
        db.refresh(state)
    except Exception as e:
        db.rollback()
        if "duplicate key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State with this code already exists"
            )
        raise
    return state

@router.get("/states", response_model=List[StateResponse])
def get_states(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[bool] = None,
    code: Optional[str] = None,
    name: Optional[str] = None,
):
    """Get list of states"""
    query = db.query(State)
    if status is not None:
        query = query.filter(State.status == status)
    if code:
        query = query.filter(State.code.ilike(f"%{code}%"))
    if name:
        query = query.filter(State.name.ilike(f"%{name}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/states/{state_id}", response_model=StateResponse)
def get_state(
    state_id: int,
    db: Session = Depends(get_db)
):
    """Get state by ID"""
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    return state

@router.put("/states/{state_id}", response_model=StateResponse)
def update_state(
    *,
    db: Session = Depends(get_db),
    state_id: int,
    state_in: StateUpdate,
    current_user = Depends(get_current_user)
):
    """Update state"""
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    
    update_data = state_in.dict(exclude_unset=True)
    update_data["updated_by"] = current_user.id
    
    for field, value in update_data.items():
        setattr(state, field, value)
    
    try:
        db.commit()
        db.refresh(state)
    except Exception as e:
        db.rollback()
        if "duplicate key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State with this code already exists"
            )
        raise
    return state

@router.delete("/states/{state_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_state(
    *,
    db: Session = Depends(get_db),
    state_id: int,
    current_user = Depends(get_current_user)
):
    """Delete state"""
    state = db.query(State).filter(State.id == state_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    
    # Soft delete by updating status
    state.status = False
    state.updated_by = current_user.id
    db.commit()
    return None
