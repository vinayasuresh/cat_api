import csv
import json
import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.common.zipcode_dataset import ZipCodeDataset
from app.db.session import SessionLocal, engine

def import_zipcodes():
    session = SessionLocal()
    csv_file = Path(__file__).parent.parent / 'uszips.csv'
    batch_size = 1000
    batch = []
    
    try:
        print(f"Reading from {csv_file}")
        with open(csv_file, 'r') as f:
            csv_reader = csv.DictReader(f)
            total_rows = 0
            
            for row in csv_reader:
                total_rows += 1
                # Convert county_weights from string to JSON
                try:
                    county_weights = json.loads(row['county_weights']) if row['county_weights'] else None
                except json.JSONDecodeError:
                    print(f"Warning: Invalid JSON in county_weights for ZIP {row['zip']}")
                
                # Create ZipCodeDataset instance
                try:
                    zipcode = ZipCodeDataset(
                        zip=row['zip'],
                        lat=float(row['lat']) if row['lat'] else None,
                        lng=float(row['lng']) if row['lng'] else None,
                        city=row['city'],
                        state_id=row['state_id'],
                        state_name=row['state_name'],
                        zcta=row['zcta'].lower() == 'true',
                        parent_zcta=row['parent_zcta'] or None,
                        population=float(row['population']) if row['population'] else None,
                        density=float(row['density']) if row['density'] else None,
                        county_fips=row['county_fips'],
                        county_name=row['county_name'],
                        county_weights=county_weights,
                        county_names_all=row['county_names_all'],
                        county_fips_all=row['county_fips_all'],
                        imprecise=row['imprecise'].lower() == 'true',
                        military=row['military'].lower() == 'true',
                        timezone=row['timezone']
                    )
                    batch.append(zipcode)
                    
                    if len(batch) >= batch_size:
                        session.bulk_save_objects(batch)
                        session.commit()
                        print(f"Imported {total_rows} records...")
                        batch = []
                        
                except Exception as e:
                    print(f"Error processing ZIP {row['zip']}: {e}")
                    continue
            
            # Commit any remaining records
            if batch:
                session.bulk_save_objects(batch)
                session.commit()
            
            print(f"Successfully imported {total_rows} zipcode records!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    import_zipcodes()
