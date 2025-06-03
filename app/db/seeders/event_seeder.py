from sqlalchemy.orm import Session
from app.models.common.events import Event
from app.models.auth.user import User
import csv
import os

async def seed_events(db: Session):
    print("Seeding events...")
    
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        raise Exception("Admin user not found! Please run user seeder first.")

    # Read events from CSV file
    csv_file = os.path.join(os.path.dirname(__file__), 'csv', 'events.csv')
    
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Check if event already exists
            existing_event = db.query(Event).filter(Event.name == row["name"]).first()
            
            if not existing_event:
                event = Event(
                    name=row["name"],
                    description=row["description"],
                    status=row["status"].lower() == "true",
                    created_by=admin_user.id
                )
                db.add(event)
    
    db.commit()
    print("Events seeded successfully!")
