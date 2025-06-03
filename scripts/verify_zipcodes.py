import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.models.common.zipcode_dataset import ZipCodeDataset

def verify_import():
    session = SessionLocal()
    try:
        # Get total count
        total_count = session.query(ZipCodeDataset).count()
        print(f"Total records in database: {total_count}")
        
        # Get a few sample records from different states
        samples = session.query(ZipCodeDataset).limit(5).all()
        
        if samples:
            print("\nSample records:")
            for sample in samples:
                print(f"\nZIP: {sample.zip}")
                print(f"City: {sample.city}")
                print(f"State: {sample.state_name}")
                print(f"County: {sample.county_name}")
                print(f"Population: {sample.population}")
                print(f"Timezone: {sample.timezone}")
        else:
            print("No records found in the database!")
    except Exception as e:
        print(f"Error occurred: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    verify_import()
