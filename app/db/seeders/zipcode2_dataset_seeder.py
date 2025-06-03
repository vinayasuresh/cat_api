from sqlalchemy.orm import Session
from app.models.common.zipcode2_dataset import ZipCode2Dataset
import csv
import os
import json

async def seed_zipcode2_dataset(db: Session):
    print("Seeding zipcode2 dataset...")
    
    # Read zipcode data from CSV
    csv_file = os.path.join(os.path.dirname(__file__), 'csv', 'zipcode2_dataset.csv')
    
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file, delimiter=';')  # Using semicolon delimiter
        # Skip header row
        headers = next(csv_reader)
        
        batch = []
        batch_size = 1000  # Process 1000 records at a time for better performance
        
        for row in csv_reader:
            # Check if zipcode already exists
            existing_zipcode = db.query(ZipCode2Dataset).filter(ZipCode2Dataset.zip_code == row[0]).first()
            
            if not existing_zipcode:
                # Handle the JSON field - ensure it's properly formatted
                county_weights_str = row[10].strip()
                try:
                    # Clean up any potential formatting issues
                    if county_weights_str:
                        county_weights = json.loads(county_weights_str.replace("'", '"'))
                    else:
                        county_weights = {}
                except json.JSONDecodeError:
                    print(f"Could not parse county weights for zip code {row[0]}: {county_weights_str}")
                    county_weights = {}
                
                zipcode = ZipCode2Dataset(
                    zip_code=row[0],
                    usps_city_name=row[1],
                    usps_state_code=row[2],
                    state_name=row[3],
                    zcta=row[4].upper() == 'TRUE',
                    zcta_parent=row[5] if row[5] else None,
                    population=float(row[6]) if row[6] else None,
                    density=float(row[7]) if row[7] else None,
                    primary_county_code=row[8],
                    primary_county_name=row[9],
                    county_weights=county_weights,
                    county_names=row[11],
                    county_codes=row[12],
                    imprecise=row[13].upper() == 'TRUE',
                    military=row[14].upper() == 'TRUE',
                    timezone=row[15],
                    geo_point=row[16] if len(row) > 16 else None
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
    
    print("Zipcode2 dataset seeded successfully!")
