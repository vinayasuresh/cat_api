from sqlalchemy.orm import Session
from app.models.common.zipcode_dataset import ZipCodeDataset
import csv
import os
import json

async def seed_zipcode_dataset(db: Session):
    print("Seeding zipcode dataset...")
    
    # Read zipcode data from CSV
    csv_file = os.path.join(os.path.dirname(__file__), 'csv', 'zipcode_dataset.csv')
    
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        batch = []
        batch_size = 1000  # Process 1000 records at a time for better performance
        
        for row in csv_reader:
            # Check if zipcode already exists
            existing_zipcode = db.query(ZipCodeDataset).filter(ZipCodeDataset.zip == row["zip"]).first()
            
            if not existing_zipcode:
                # Convert county_weights from string to JSON
                county_weights = json.loads(row["county_weights"]) if row["county_weights"] else {}
                
                zipcode = ZipCodeDataset(
                    zip=row["zip"],
                    lat=float(row["lat"]) if row["lat"] else None,
                    lng=float(row["lng"]) if row["lng"] else None,
                    city=row["city"],
                    state_id=row["state_id"],
                    state_name=row["state_name"],
                    zcta=row["zcta"].lower() == "true",
                    parent_zcta=row["parent_zcta"] if row["parent_zcta"] != "NULL" else None,
                    population=float(row["population"]) if row["population"] and row["population"] != "NULL" else None,
                    density=float(row["density"]) if row["density"] and row["density"] != "NULL" else None,
                    county_fips=row["county_fips"],
                    county_name=row["county_name"],
                    county_weights=county_weights,
                    county_names_all=row["county_names_all"],
                    county_fips_all=row["county_fips_all"],
                    imprecise=row["imprecise"].lower() == "true",
                    military=row["military"].lower() == "true",
                    timezone=row["timezone"]
                )
                batch.append(zipcode)

            if len(batch) >= batch_size:
                db.bulk_save_objects(batch)
                db.commit()
                batch = []

        # Save any remaining records
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
    
    print("Zipcode dataset seeded successfully!")
