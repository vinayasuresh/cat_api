from app.db.seeders.user_seeder import seed_users
from app.db.seeders.state_seeder import seed_states
from app.db.seeders.zone_county_seeder import seed_zones_counties
from app.db.seeders.category_seeder import seed_categories
from app.db.seeders.event_seeder import seed_events
from app.db.seeders.category_event_seeder import seed_category_events
from app.db.seeders.zipcode_dataset_seeder import seed_zipcode_dataset
from app.db.seeders.zipcode2_dataset_seeder import seed_zipcode2_dataset
from app.db.seeders.policyholder_seeder import seed_policyholders
from app.db.seeders.alert_seeder import seed_alerts
from app.db.seeders.alert_affected_area_seeder import seed_alert_affected_areas
from app.db.seeders.category_event_mapping_seeder import seed_category_event_mappings

async def run_all_seeders(db):
    print("Starting database seeding...")
    
    # Seed in order of dependencies
    await seed_users(db)
    await seed_states(db)
    await seed_categories(db)
    await seed_events(db)
    await seed_category_event_mappings(db)
    await seed_zipcode_dataset(db)
    await seed_zipcode2_dataset(db)
    
    print("Database seeding completed successfully!")
