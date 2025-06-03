from sqlalchemy.orm import Session
from app.models.monitoring.alert_affected_area import AlertAffectedArea, RegionType
from app.models.monitoring.alert import Alert
from app.models.common.zones_counties import ZoneCounty
from app.models.common.zipcodes import Zipcode

async def seed_alert_affected_areas(db: Session):
    print("Seeding alert affected areas...")
    
    affected_areas_data = [
        {
            "alert_external_id": "HUR-2025-001",
            "areas": [
                {"type": RegionType.ZONE, "code": "FL_Z1"},
                {"type": RegionType.ZONE, "code": "FL_Z2"},
                {"type": RegionType.COUNTY, "code": "FL_C1"}
            ]
        },
        {
            "alert_external_id": "TOR-2025-001",
            "areas": [
                {"type": RegionType.COUNTY, "code": "TX_C1"},
                {"type": RegionType.ZIPCODE, "code": "75001"}
            ]
        }
    ]
    
    for area_data in affected_areas_data:
        # Get alert
        alert = db.query(Alert).filter(Alert.external_id == area_data["alert_external_id"]).first()
        if not alert:
            continue

        for area in area_data["areas"]:
            if area["type"] in [RegionType.ZONE, RegionType.COUNTY]:
                region = db.query(ZoneCounty).filter(ZoneCounty.code == area["code"]).first()
                if region:
                    affected_area = AlertAffectedArea(
                        alert_id=alert.id,
                        zone_county_id=region.id,
                        region_type=area["type"]
                    )
                    db.add(affected_area)
            elif area["type"] == RegionType.ZIPCODE:
                zipcode = db.query(Zipcode).filter(Zipcode.code == area["code"]).first()
                if zipcode:
                    affected_area = AlertAffectedArea(
                        alert_id=alert.id,
                        zipcode_id=zipcode.id,
                        region_type=area["type"]
                    )
                    db.add(affected_area)
    
    db.commit()
    print("Alert affected areas seeded successfully!")
