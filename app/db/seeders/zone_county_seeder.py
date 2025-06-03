from sqlalchemy.orm import Session
from app.models.common.zones_counties import ZoneCounty, RegionType
from app.models.common.state import State
from app.models.auth.user import User

async def seed_zones_counties(db: Session):
    print("Seeding zones and counties...")
    
    # Get admin user for created_by
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        raise Exception("Admin user not found! Please run user seeder first.")

    # Example data - you should replace this with your actual zones and counties
    sample_data = [
        {
            "state_code": "FL",
            "zones": [
                {"code": "FL_Z1", "name": "Florida Zone 1"},
                {"code": "FL_Z2", "name": "Florida Zone 2"}
            ],
            "counties": [
                {"code": "FL_C1", "name": "Miami-Dade County"},
                {"code": "FL_C2", "name": "Broward County"}
            ]
        },
        # Add more states with their zones and counties
    ]
    
    for state_data in sample_data:
        state = db.query(State).filter(State.code == state_data["state_code"]).first()
        if not state:
            continue

        # Add zones
        for zone in state_data["zones"]:
            existing_zone = db.query(ZoneCounty).filter(ZoneCounty.code == zone["code"]).first()
            if not existing_zone:
                new_zone = ZoneCounty(
                    code=zone["code"],
                    name=zone["name"],
                    type=RegionType.ZONE,
                    state_id=state.id,
                    created_by=admin_user.id,
                    updated_by=admin_user.id
                )
                db.add(new_zone)

        # Add counties
        for county in state_data["counties"]:
            existing_county = db.query(ZoneCounty).filter(ZoneCounty.code == county["code"]).first()
            if not existing_county:
                new_county = ZoneCounty(
                    code=county["code"],
                    name=county["name"],
                    type=RegionType.COUNTY,
                    state_id=state.id,
                    created_by=admin_user.id,
                    updated_by=admin_user.id
                )
                db.add(new_county)

    db.commit()
    print("Zones and counties seeded successfully!")
