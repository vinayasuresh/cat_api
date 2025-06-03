from sqlalchemy.orm import Session
from app.models.common.policyholders import Policyholder
from app.models.common.state import State
from app.models.common.zones_counties import ZoneCounty
from app.models.common.zipcodes import Zipcode
from app.models.auth.user import User

async def seed_policyholders(db: Session):
    print("Seeding policyholders...")
    
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        raise Exception("Admin user not found! Please run user seeder first.")

    # Sample policyholder data
    policyholders_data = [
        {
            "policy_id": "POL-001",
            "name": "John Doe",
            "zipcode": "75001",
            "state_code": "TX",
            "county_code": "TX_C1",
            "address": "123 Main St",
            "email": "john.doe@example.com",
            "phoneno": "555-0101",
            "premium": 1200.00,
            "claims": 0
        },
        {
            "policy_id": "POL-002",
            "name": "Jane Smith",
            "zipcode": "33101",
            "state_code": "FL",
            "county_code": "FL_C1",
            "address": "456 Ocean Dr",
            "email": "jane.smith@example.com",
            "phoneno": "555-0102",
            "premium": 2500.00,
            "claims": 1
        }
    ]
    
    for policyholder_data in policyholders_data:
        # Get required foreign keys
        state = db.query(State).filter(State.code == policyholder_data["state_code"]).first()
        county = db.query(ZoneCounty).filter(ZoneCounty.code == policyholder_data["county_code"]).first()
        zipcode = db.query(Zipcode).filter(Zipcode.code == policyholder_data["zipcode"]).first()
        
        if not all([state, county, zipcode]):
            continue

        existing_policyholder = db.query(Policyholder).filter(
            Policyholder.policy_id == policyholder_data["policy_id"]
        ).first()
        
        if not existing_policyholder:
            policyholder = Policyholder(
                policy_id=policyholder_data["policy_id"],
                name=policyholder_data["name"],
                zipcode_id=zipcode.id,
                state_id=state.id,
                county_id=county.id,
                address=policyholder_data["address"],
                email=policyholder_data["email"],
                phoneno=policyholder_data["phoneno"],
                premium=policyholder_data["premium"],
                claims=policyholder_data["claims"],
                created_by=admin_user.id,
                updated_by=admin_user.id
            )
            db.add(policyholder)
    
    db.commit()
    print("Policyholders seeded successfully!")
