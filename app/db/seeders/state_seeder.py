from sqlalchemy.orm import Session
from app.models.common.state import State
from app.models.auth.user import User
import csv
import os

async def seed_states(db: Session):
    print("Seeding states...")
    
    # Get admin user for created_by
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        raise Exception("Admin user not found! Please run user seeder first.")

    # Read states from CSV file
    csv_file = os.path.join(os.path.dirname(__file__), 'csv', 'states.csv')
    
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Check if state already exists
            existing_state = db.query(State).filter(State.code == row["code"]).first()
            
            if not existing_state:
                state = State(
                    code=row["code"],
                    fips=row["fips"],
                    name=row["name"],
                    status=row["status"].lower() == "true",
                    created_by=admin_user.id
                )
                db.add(state)
    
    db.commit()
    print("States seeded successfully!")
