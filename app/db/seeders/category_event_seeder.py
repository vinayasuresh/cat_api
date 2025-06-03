from sqlalchemy.orm import Session
from app.models.common.category_event_mappings import CategoryEventMapping
from app.models.common.category import Category
from app.models.common.events import Event

async def seed_category_events(db: Session):
    print("Seeding category-event mappings...")

    # Define the relationships between categories and events
    mappings = [
        {"category": "Weather", "events": ["Hurricane", "Tornado", "Winter Storm"]},
        {"category": "Natural Disasters", "events": ["Earthquake", "Hurricane", "Tornado", "Flood"]},
        {"category": "Fire", "events": ["Wildfire"]},
        {"category": "Infrastructure", "events": ["Earthquake"]}
    ]
    
    for mapping in mappings:
        category = db.query(Category).filter(Category.name == mapping["category"]).first()
        if not category:
            continue

        for event_name in mapping["events"]:
            event = db.query(Event).filter(Event.name == event_name).first()
            if not event:
                continue

            # Check if mapping already exists
            existing_mapping = db.query(CategoryEventMapping).filter(
                CategoryEventMapping.category_id == category.id,
                CategoryEventMapping.event_id == event.id
            ).first()

            if not existing_mapping:
                new_mapping = CategoryEventMapping(
                    category_id=category.id,
                    event_id=event.id
                )
                db.add(new_mapping)
    
    db.commit()
    print("Category-event mappings seeded successfully!")
