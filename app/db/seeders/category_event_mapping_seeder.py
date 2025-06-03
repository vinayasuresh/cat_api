from sqlalchemy.orm import Session
from app.models.common.category_event_mappings import CategoryEventMapping
from app.models.common.category import Category
from app.models.common.events import Event
import csv
import os

async def seed_category_event_mappings(db: Session):
    print("Seeding category-event mappings...")

    # Read mappings from CSV file
    csv_file = os.path.join(os.path.dirname(__file__), 'csv', 'category_event_mappings.csv')
    
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            category_id = int(row["category_id"])
            event_id = int(row["event_id"])
            
            # Check if mapping already exists
            existing_mapping = db.query(CategoryEventMapping).filter(
                CategoryEventMapping.category_id == category_id,
                CategoryEventMapping.event_id == event_id
            ).first()
            
            # Verify that both category and event exist
            category = db.query(Category).filter(Category.id == category_id).first()
            event = db.query(Event).filter(Event.id == event_id).first()
            
            if not existing_mapping and category and event:
                mapping = CategoryEventMapping(
                    category_id=category_id,
                    event_id=event_id
                )
                db.add(mapping)
    
    db.commit()
    print("Category-event mappings seeded successfully!")
