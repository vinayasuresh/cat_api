from sqlalchemy.orm import Session
from app.models.monitoring.alert import Alert, AlertStatus, AlertSeverity
from app.models.common.state import State
from datetime import datetime, timezone

async def seed_alerts(db: Session):
    print("Seeding alerts...")

    # Sample alert data
    alerts_data = [
        {
            "title": "Severe Hurricane Warning",
            "description": "Category 4 hurricane approaching the coast",
            "status": AlertStatus.NEW,
            "severity": AlertSeverity.HIGH,
            "state_code": "FL",
            "source": "National Weather Service",
            "event_type": "Hurricane",
            "external_id": "HUR-2025-001"
        },
        {
            "title": "Tornado Watch",
            "description": "Conditions are favorable for tornado development",
            "status": AlertStatus.NEW,
            "severity": AlertSeverity.MEDIUM,
            "state_code": "TX",
            "source": "National Weather Service",
            "event_type": "Tornado",
            "external_id": "TOR-2025-001"
        },
        {
            "title": "Flash Flood Warning",
            "description": "Heavy rainfall causing flash flooding",
            "status": AlertStatus.NEW,
            "severity": AlertSeverity.HIGH,
            "state_code": "LA",
            "source": "National Weather Service",
            "event_type": "Flood",
            "external_id": "FLD-2025-001"
        }
    ]
    
    for alert_data in alerts_data:
        # Get state ID
        state = db.query(State).filter(State.code == alert_data["state_code"]).first()
        if not state:
            continue

        existing_alert = db.query(Alert).filter(Alert.external_id == alert_data["external_id"]).first()
        
        if not existing_alert:
            alert = Alert(
                title=alert_data["title"],
                description=alert_data["description"],
                status=alert_data["status"],
                severity=alert_data["severity"],
                state_id=state.id,
                source=alert_data["source"],
                event_type=alert_data["event_type"],
                external_id=alert_data["external_id"],
                event_timestamp=datetime.now(timezone.utc)
            )
            db.add(alert)
    
    db.commit()
    print("Alerts seeded successfully!")
