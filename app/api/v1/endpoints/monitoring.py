from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
from app.db.session import get_db, SessionLocal
from app.models.monitoring.alert import Alert, AlertStatus, AlertSeverity
from app.schemas.monitoring.alert import AlertResponse
from app.services.monitoring.alert_service import fetch_weather_alerts, process_weather_alerts, get_alerts_grouped_by_category
from app.services.monitoring.alert_group_service import get_alerts_grouped_by_category_with_zipcodes
from sqlalchemy import desc, distinct
from app.core.config import settings

router = APIRouter()
_background_task = None  # Global variable to track the background task

async def fetch_alerts_job():
    """Background task to fetch weather alerts periodically based on configured interval"""
    global _background_task
    while True:
        try:
            db = SessionLocal()
            alerts = await fetch_weather_alerts()
            process_weather_alerts(db, alerts)
        except Exception as e:
            print(f"Error in background task: {str(e)}")
        finally:
            if db:
                db.close()
        await asyncio.sleep(settings.ALERT_FETCH_INTERVAL_SECONDS)  # Sleep for configured interval

@router.on_event("startup")
async def start_background_tasks():
    global _background_task
    if _background_task is None:  # Only start if not already running
        _background_task = asyncio.create_task(fetch_alerts_job())
        print("Weather alerts background task started")

@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    search: Optional[str] = None,
    state: Optional[str] = None,
    severity: Optional[AlertSeverity] = None,
    sort_by: Optional[str] = Query(default="default", enum=["default", "pinned", "recent", "active", "alphabetical"])
):
    """
    Get list of alerts with filtering and sorting options
    - search: Search in title and description
    - state: Filter by state
    - severity: Filter by severity level
    - sort_by: Sort order (default, pinned, recent, active, alphabetical)
    """
    query = db.query(Alert)

    # Apply filters
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            (Alert.title.ilike(search_term)) | 
            (Alert.description.ilike(search_term))
        )
    
    if state and state != "all":
        query = query.filter(Alert.state == state)
    
    if severity and severity != "all":
        query = query.filter(Alert.severity == severity)

    # Apply sorting
    if sort_by == "recent":
        query = query.order_by(desc(Alert.event_timestamp))
    elif sort_by == "alphabetical":
        query = query.order_by(Alert.title)
    else:  # default sorting by severity and then timestamp
        query = query.order_by(
            desc(Alert.severity),
            desc(Alert.event_timestamp)
        )

    # Pagination
    total = query.count()
    alerts = query.offset(skip).limit(limit).all()

    return alerts

@router.get("/alerts/states", response_model=List[str])
def get_available_states(db: Session = Depends(get_db)):
    """Get list of all states that have alerts"""
    states = db.query(distinct(Alert.state)).filter(Alert.state.isnot(None)).all()
    return [state[0] for state in states if state[0]]

@router.get("/alerts/state/{state}", response_model=List[AlertResponse])
def get_alerts_by_state(
    state: str,
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    severity: Optional[AlertSeverity] = None
):
    """Get alerts for a specific state with optional severity filter"""
    query = db.query(Alert).filter(Alert.state == state)
    
    if severity and severity != "all":
        query = query.filter(Alert.severity == severity)
    
    query = query.order_by(
        desc(Alert.severity),
        desc(Alert.event_timestamp)
    )
    
    return query.offset(skip).limit(limit).all()

@router.post("/fetch-alerts")
async def trigger_alert_fetch(db: Session = Depends(get_db)):
    """Manually trigger weather alert fetch and return grouped alerts with zipcode details"""
    try:
        alerts = await fetch_weather_alerts()
        result = process_weather_alerts(db, alerts)
        if result:
            return result
        return {"message": "No new alerts to process"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/category-risk-with-zipcodes", response_model=List[Dict[str, Any]])
def fetch_category_risk_alerts_with_zipcodes(
    db: Session = Depends(get_db),
    state: Optional[str] = None,
    severity: Optional[AlertSeverity] = None,
    category: Optional[str] = None,
):
    """
    Fetch already synced alerts grouped by category with detailed zipcode information
    for policyholder data collection. Returns alerts with state->county/zone->zipcode hierarchy.
    """
    try:
        result = get_alerts_grouped_by_category_with_zipcodes(db=db, state=state, severity=severity, category=category)
        if not result:
            return []
        return result
    except Exception as e:
        print(f"Error in fetch_category_risk_alerts_with_zipcodes: {str(e)}")  # Add logging
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")
    
@router.get("/alerts/category-risk")
def fetch_category_risk_alerts(
    db: Session = Depends(get_db),
    state: Optional[str] = None,
    severity: Optional[AlertSeverity] = None,
    category: Optional[str] = None,
):
    """
    Fetch alerts grouped by category, with optional filters applied on each category match
    """
    return get_alerts_grouped_by_category(db=db, state=state, severity=severity, category=category)