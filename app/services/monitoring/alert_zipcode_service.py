from sqlalchemy.orm import Session
from app.models.common.zones_counties import ZoneCounty
from app.models.common.zipcodes import Zipcode
from app.models.common.zipcode_dataset import ZipCodeDataset
from app.models.common.zipcode2_dataset import ZipCode2Dataset
from typing import List, Set
import logging
from sqlalchemy.exc import IntegrityError


logger = logging.getLogger(__name__)

def get_zipcodes_by_region_fips(db: Session, region_fips_codes: List[str]) -> Set[str]:
    """
    Get zipcodes from zipcode_dataset table using region FIPS codes (state FIPS + region code)
    """
    try:
        if not region_fips_codes:
            return set()
        
        print(f"Fetching zipcodes for region FIPS codes: {region_fips_codes}")
            
        # Single query for all region FIPS codes
        zipcodes = db.query(ZipCodeDataset.zip).filter(
            ZipCodeDataset.county_fips.in_(region_fips_codes)
        ).all()

        # Alternative query for zipcode2_dataset if needed
        # zipcodes = db.query(ZipCode2Dataset.zip_code).filter(
        #     ZipCode2Dataset.primary_county_code.in_(region_fips_codes)
        # ).all()
        
        return {z[0] for z in zipcodes}
    except Exception as e:
        logger.error(f"Error getting zipcodes for region FIPS codes {region_fips_codes}: {str(e)}")
        return set()

def process_zipcodes_with_dataset(
    db: Session, 
    properties: dict,
    zone_counties: List[ZoneCounty],
    region_fips_codes: List[str] = None
) -> tuple[List[Zipcode], dict]:
    """
    Process and create/update zipcodes for multiple zones/counties using region_fips codes.
    Returns tuple of (list of associated zipcodes, summary dict).
    """
    result_zipcodes = []
    summary = {
        "processed_region_fips_codes": 0,
        "skipped_region_fips_codes": 0,
        "found_zipcodes": 0,
        "created_mappings": 0,
        "existing_mappings": 0
    }
    
    try:
        # Use the provided region_fips_codes directly
        if not region_fips_codes:
            print("No region FIPS codes provided")
            return result_zipcodes, summary

        print(f"Processing region FIPS codes: {region_fips_codes}")
        
        summary["processed_region_fips_codes"] = len(region_fips_codes)
            
        # Get zipcodes from dataset for all region FIPS codes
        dataset_zipcodes = get_zipcodes_by_region_fips(db, region_fips_codes)
        
        if not dataset_zipcodes:
            print(f"No zipcodes found in dataset for region FIPS codes: {region_fips_codes}")
            summary["skipped_region_fips_codes"] = len(region_fips_codes)
            return result_zipcodes, summary
            
        summary["found_zipcodes"] = len(dataset_zipcodes)
        
        # Get all existing zipcodes in one query for efficiency
        existing_zipcodes = {
            z.code: z for z in db.query(Zipcode).filter(
                Zipcode.code.in_(dataset_zipcodes)
            ).all()
        }
        
        # Track processed zip-zone combinations to avoid duplicates
        processed_combinations = set()
        new_zipcodes = []
        
        # Process zipcodes in batch
        for zip_code in dataset_zipcodes:
            for zone_county in zone_counties:
                # Skip if we've already processed this combination
                combo = (zip_code, zone_county.id)
                if combo in processed_combinations:
                    continue
                    
                processed_combinations.add(combo)
                existing = existing_zipcodes.get(zip_code)
                
                if existing:
                    # Always reuse the existing mapping
                    result_zipcodes.append(existing)
                    summary["existing_mappings"] += 1
                else:
                    # Create new zipcode
                    new_zipcode = Zipcode(
                        code=zip_code,
                        name=f"ZIP {zip_code}",
                        zone_county_id=zone_county.id,
                        status=True
                    )
                    new_zipcodes.append(new_zipcode)
                    summary["created_mappings"] += 1
        
        # Bulk insert new zipcodes
        if new_zipcodes:
            try:
                # Instead of bulk_save_objects, use add_all to get IDs back
                for zipcode in new_zipcodes:
                    db.add(zipcode)
                db.flush()
                print(f"Successfully created {len(new_zipcodes)} new zipcode mappings")
                result_zipcodes.extend(new_zipcodes)
            except Exception as e:
                logger.error(f"Error inserting zipcodes: {str(e)}")
                raise
                
        # Log summary
        print(
            f"Processing summary: "
            f"Processed {summary['processed_region_fips_codes']} region FIPS codes, "
            f"Skipped {summary['skipped_region_fips_codes']} region FIPS codes, "
            f"Found {summary['found_zipcodes']} zipcodes in dataset, "
            f"Created {summary['created_mappings']} new mappings, "
            f"Used {summary['existing_mappings']} existing mappings"
        )
        
    except Exception as e:
        logger.error(f"Error in process_zipcodes_with_dataset: {str(e)}")
        raise
        
    return result_zipcodes, summary
