from datetime import datetime
import httpx
from sqlalchemy.orm import Session
from app.models.monitoring.alert import Alert, AlertSeverity, AlertStatus
from app.models.common.category import Category
from app.schemas.monitoring.alert import AlertCreate
from typing import List, Optional, Tuple, Set, Dict, Any
from app.models.common.category_event_mappings import CategoryEventMapping
from app.models.common.events import Event
from app.models.common.state import State
from app.models.common.zones_counties import ZoneCounty, RegionType
from app.models.monitoring.alert_affected_area import AlertAffectedArea, RegionType as AreaRegionType
from app.models.common.zipcodes import Zipcode
from app.models.monitoring.alert_sync_log import AlertSyncLog
from app.services.monitoring.alert_zipcode_service import process_zipcodes_with_dataset
import random
from collections import defaultdict
import logging
from app.models.common.policyholders import Policyholder
import string
import uuid

logger = logging.getLogger(__name__)

def map_severity(cap_severity: str) -> AlertSeverity:
    """Map weather.gov severity to AlertSeverity enum.
    Normalizes input to uppercase to ensure consistent behavior across environments."""
    severity_map = {
        "EXTREME": AlertSeverity.HIGH,
        "SEVERE": AlertSeverity.HIGH,
        "MODERATE": AlertSeverity.MEDIUM,
        "MINOR": AlertSeverity.LOW,
    }
    # Convert input to uppercase to ensure consistent matching
    normalized_severity = cap_severity.upper() if cap_severity else "MINOR"
    return severity_map.get(normalized_severity, AlertSeverity.LOW)

async def fetch_weather_alerts() -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://api.weather.gov/alerts/active",
                headers={"Accept": "application/geo+json"}
            )
            response.raise_for_status()
            data = response.json()
            features = data.get("features", [])
            print(f"Fetched {len(features)} alerts from weather.gov")
            return features
    except Exception as e:
        print(f"Error fetching weather alerts: {str(e)}")
        return []

def process_weather_alerts(db: Session, alerts: List[dict]) -> Optional[List[dict]]:
    """Process incoming weather alerts and create/update database records."""
    # Counters for tracking
    processed_count = 0
    ignored_by_state = 0
    ignored_by_missing_data = 0
    error_count = 0
    total_alerts = len(alerts) if alerts else 0
    
    # Zipcodes summary tracking
    zipcode_summary = {
        "processed_same_codes": 0,
        "skipped_same_codes": 0,
        "found_zipcodes": 0,
        "created_mappings": 0,
        "existing_mappings": 0
    }
    
    if total_alerts == 0:
        print("No alerts to process")
        return None

    print(f"Starting to process {total_alerts} alerts...")
    
    try:
        # Pre-load all states into memory with their FIPS codes
        print("Loading states data...")
        valid_states = {
            state.code: state for state in db.query(State).all()
        }
        if not valid_states:
            print("❌ No states found in database")
            return None
        
        # Ensure all states have FIPS codes
        states_without_fips = [state.code for state in valid_states.values() if not state.fips]
        if states_without_fips:
            print(f"⚠️ Warning: Some states are missing FIPS codes: {', '.join(states_without_fips)}")
        
        # Pre-load existing zone/county data
        print("Loading zones/counties data...")
        existing_zones = {
            zone.code: zone for zone in db.query(ZoneCounty).all()
        }
        
        # Track unique states for reporting
        unique_states = set()
        
        # First pass - quick validation and statistics
        print("Performing initial validation...")
        valid_alerts = []
        for feature in alerts:
            try:
                properties = feature.get("properties", {})
                external_id = feature.get("id")
                geocode = properties.get("geocode", {})
                ugc_codes = geocode.get("UGC", [])
                
                # Basic data validation
                if not external_id:
                    print("Missing external_id")
                    ignored_by_missing_data += 1
                    continue
                    
                if not properties:
                    print(f"Missing properties for alert {external_id}")
                    ignored_by_missing_data += 1
                    continue
                    
                if not ugc_codes:
                    print(f"Missing UGC codes for alert {external_id}")
                    ignored_by_missing_data += 1
                    continue
                
                # Check state validity
                state_code = ugc_codes[0][:2].upper()
                unique_states.add(state_code)
                
                if state_code not in valid_states:
                    # print(f"Invalid state code: {state_code}")
                    ignored_by_state += 1
                    continue
                
                # Validate required fields
                title = properties.get("headline") or properties.get("event")
                if not title:
                    print(f"Missing title for alert {external_id}")
                    ignored_by_missing_data += 1
                    continue
                
                valid_alerts.append((feature, properties, external_id, ugc_codes, state_code))
                
            except Exception as e:
                print(f"Error validating alert: {str(e)}")
                error_count += 1
                continue
        
        missing_states = unique_states - valid_states.keys()
        print(f"\nFound {len(valid_alerts)} valid alerts to process")
        
        if missing_states:
            print("\n🔍 State Validation Report:")
            print(f"Found {len(unique_states)} unique states in alerts")
            print(f"Missing {len(missing_states)} states from database: {', '.join(sorted(missing_states))}")
        
        # Batch check existing alerts for efficiency
        print("Checking for existing alerts...")
        existing_alert_ids = {
            id[0] for id in db.query(Alert.external_id).all()
        }
        
        # Main processing loop with transaction management
        print("\nProcessing alerts...")
        for feature, properties, external_id, ugc_codes, state_code in valid_alerts:
            if external_id in existing_alert_ids:
                print(f"⏩ Skipping existing alert: {external_id}")
                ignored_by_missing_data += 1
                continue
                
            try:
                # Extract alert data
                title = properties.get("headline") or properties.get("event")
                desc = properties.get("description") or properties.get("text") or ""
                event = properties.get("event") or "Unknown Event"
                
                # Parse event timestamp
                try:
                    event_time = properties.get("sent") or properties.get("effective") or datetime.utcnow().isoformat()
                    if isinstance(event_time, str):
                        event_time = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
                except Exception as e:
                    print(f"Error parsing event time for {external_id}: {str(e)}")
                    event_time = datetime.utcnow()
                
                # Create alert with proper status
                alert_data = AlertCreate(
                    title=title,
                    description=desc,
                    severity=map_severity(properties.get("severity", "Minor")),
                    state_id=valid_states[state_code].id,
                    source="weather.gov",
                    external_id=external_id,
                    event_timestamp=event_time,
                    event_type=event,
                    status=AlertStatus.NEW
                )
                
                # Use nested transaction for atomic alert creation
                with db.begin_nested() as alert_savepoint:
                    try:
                        db_alert = Alert(**alert_data.dict())
                        db.add(db_alert)
                        db.flush()
                        
                        # Process all zones in batch with validation
                        successful_zones = []
                        region_fips_codes = []  # To store state_fips + region_code values
                        
                        for ugc_code in ugc_codes:
                            state_code, region_type, region_code = process_ugc_code(ugc_code)
                            if not all([state_code, region_type, region_code]):
                                print(f"Invalid UGC code: {ugc_code}")
                                continue
                            
                            # Get state FIPS code for this region
                            state = valid_states.get(state_code)
                            if not state or not state.fips:
                                print(f"Missing state FIPS for {state_code}")
                                continue
                            
                            # Create region_fips (state_fips + region_code)
                            region_fips = f"{state.fips}{region_code}"
                            print(f"Created region_fips: {region_fips} from state FIPS {state.fips} and region code {region_code}")
                            region_fips_codes.append(region_fips)
                            
                            # Get or create zone/county using cached data
                            zone_county = existing_zones.get(ugc_code)
                            if not zone_county:
                                try:
                                    zone_county = ZoneCounty(
                                        code=ugc_code,
                                        name=f"{state_code} {region_type.name} {region_code}",
                                        fips=region_fips,
                                        type=region_type,
                                        state_id=state.id,
                                        status=True
                                    )
                                    db.add(zone_county)
                                    existing_zones[ugc_code] = zone_county
                                except Exception as e:
                                    print(f"Error creating zone/county {ugc_code}: {str(e)}")
                                    continue
                            
                            successful_zones.append((zone_county, region_type))
                        
                        # Process zipcodes one zone at a time if we have valid zones
                        if successful_zones:
                            db.flush()  # Ensure all zones have IDs
                            
                            all_zipcodes = []  # Collect all zipcodes from all zones
                            affected_areas = []  # For storing all affected areas
                            
                            # Process each zone individually
                            for zone_county, region_type in successful_zones:
                                try:
                                    # Each zone has its own FIPS code that can be used to fetch zipcodes
                                    if zone_county.fips:
                                        print(f"Processing zone {zone_county.code} with FIPS {zone_county.fips}")
                                        # Pass only the one zone and its FIPS code
                                        zipcodes, zip_summary = process_zipcodes_with_dataset(
                                            db, 
                                            properties, 
                                            [zone_county],  # Pass just this one zone
                                            [zone_county.fips]  # Pass just this zone's FIPS code
                                        )
                                        
                                        # Update zipcode summary totals for this zone
                                        for key in zipcode_summary:
                                            # Map old keys to new keys for backward compatibility
                                            if key == "processed_same_codes":
                                                zipcode_summary[key] += zip_summary.get("processed_region_fips_codes", 0)
                                            elif key == "skipped_same_codes":
                                                zipcode_summary[key] += zip_summary.get("skipped_region_fips_codes", 0)
                                            else:
                                                zipcode_summary[key] += zip_summary.get(key, 0)
                                        
                                        # Add zipcodes for this zone to the overall list
                                        all_zipcodes.extend(zipcodes)
                                        
                                        # Create affected areas and mock policyholders for this zone and its zipcodes
                                        
                                        for zipcode in zipcodes:
                                            print(f"Processing zipcode {zipcode.code} in zone/county {zone_county.code}")
                                            
                                            # Generate 1-2 mock policyholders for this zipcode
                                            for _ in range(random.randint(1, 2)):
                                                # Generate random mock data
                                                name = f"Test Policy {random.choice(string.ascii_uppercase)}{random.randint(1000, 9999)}"
                                                policy_id = f"POL-{str(uuid.uuid4())[:8].upper()}"
                                                claims = random.randint(0, 5)
                                                premium = round(random.uniform(500.0, 5000.0), 2)

                                                addresses = [
                                                    {"address": f"{data['address']}, {data['state']}, {data['zipcode']}, {data['county']}"}
                                                    for data in [
                                                        {"address": "1600 Amphitheatre Parkway", "state": "California", "zipcode": "94043", "county": "Santa Clara"},
                                                        {"address": "350 Fifth Avenue", "state": "New York", "zipcode": "10118", "county": "New York"},
                                                    ]
                                                ]

                                                email_phone_map = {
                                                    "mohan@pionedata.com": "8940026533",
                                                    "mouli@pionedata.com": "9003274650",
                                                    "roshini@pionedata.com": "9363793428",
                                                    "sarala@pionedata.com": "9345012271",
                                                    "deepak@pionedata.com": "6379453546"
                                                }

                                                # Pick a random email and its corresponding phone
                                                selected_email = random.choice(list(email_phone_map.keys()))
                                                selected_phoneno = email_phone_map[selected_email]

                                                selected = random.choice(addresses)
                                                
                                                # Create policyholder record
                                                policyholder = Policyholder(
                                                    policy_id=policy_id,
                                                    name=name,
                                                    zipcode_id=zipcode.id,
                                                    claims=claims,
                                                    premium=premium,
                                                    status=True,
                                                    state_id=zone_county.state_id,
                                                    county_id=zone_county.id,
                                                    address=selected["address"],
                                                    email=selected_email,
                                                    phoneno=selected_phoneno
                                                )
                                                db.add(policyholder)
                                            
                                            print(f"Printed Zipcode Id: {zipcode.id}")
                                            print(f"Adding affected area for zipcode {zipcode.code} in zone/county {zone_county.code}")
                                            affected_areas.append(
                                                AlertAffectedArea(
                                                    alert_id=db_alert.id,
                                                    zipcode_id=zipcode.id,
                                                    zone_county_id=zone_county.id,
                                                    region_type=AreaRegionType.ZIPCODE
                                                )
                                            )
                                    else:
                                        print(f"Zone {zone_county.code} has no FIPS code, skipping")
                                        
                                except Exception as e:
                                    print(f"Error processing zipcodes for zone {zone_county.code}: {str(e)}")
                                    # Continue to next zone even if one fails
                                    continue
                            
                            # Save all affected areas in one bulk operation
                            if affected_areas:
                                db.bulk_save_objects(affected_areas)
                                db.flush()
                            
                            # If no zipcodes were found at all, add zone/county areas
                            if not all_zipcodes:
                                print("No zipcodes found for any zone, adding zone/county areas")
                                zone_areas = []
                                for zone_county, region_type in successful_zones:
                                    area_type = AreaRegionType.ZONE if region_type == RegionType.ZONE else AreaRegionType.COUNTY
                                    zone_areas.append(
                                        AlertAffectedArea(
                                            alert_id=db_alert.id,
                                            zone_county_id=zone_county.id,
                                            region_type=area_type
                                        )
                                    )
                                    
                                if zone_areas:
                                    db.bulk_save_objects(zone_areas)
                                    db.flush()
                            
                            alert_savepoint.commit()
                            processed_count += 1
                            print(f"✅ Successfully processed alert: {title}")
                        else:
                            print(f"❌ No valid zones for alert: {title}")
                            alert_savepoint.rollback()
                            error_count += 1
                            
                    except Exception as e:
                        print(f"❌ Error processing alert {external_id}: {str(e)}")
                        alert_savepoint.rollback()
                        error_count += 1
                        continue
                        
            except Exception as e:
                print(f"❌ Error creating alert data: {str(e)}")
                error_count += 1
                continue

        # Create single sync log entry and commit all changes together
        sync_log = AlertSyncLog(
            total_alerts=total_alerts,
            processed_count=processed_count,
            ignored_by_state=ignored_by_state,
            ignored_by_missing_data=ignored_by_missing_data,
            error_count=error_count,
            missing_states=list(missing_states) if missing_states else [],
            # Add zipcode processing summary (using existing field names for DB compatibility)
            processed_same_codes=zipcode_summary["processed_same_codes"],
            skipped_same_codes=zipcode_summary["skipped_same_codes"],
            found_zipcodes=zipcode_summary["found_zipcodes"],
            created_zipcode_mappings=zipcode_summary["created_mappings"],
            used_zipcode_mappings=zipcode_summary["existing_mappings"]
        )
        db.add(sync_log)

        # Single commit for both alerts and sync log
        db.commit()

        # Print summary
        print("\n📊 Alert Processing Summary:")
        if processed_count > 0:
            print(f"Total Alerts: {total_alerts}")
            print(f"Processed: {processed_count} ✅")
        else:
            print(f"No new alerts processed")
            print(f"Total Alerts: {total_alerts}")
        
        print(f"Ignored Alerts:")
        print(f"  - By State ({len(missing_states)} missing states): {ignored_by_state} 🌎")
        print(f"  - By Missing/Invalid Data: {ignored_by_missing_data} ⏩")
        print(f"Errors: {error_count} ❌")
        
        # Print zipcode processing summary
        print("\n📊 Zipcode Processing Summary:")
        print(f"Processed region FIPS codes: {zipcode_summary['processed_same_codes']}")
        print(f"Skipped region FIPS codes: {zipcode_summary['skipped_same_codes']}")
        print(f"Found zipcodes in dataset: {zipcode_summary['found_zipcodes']}")
        print(f"Created new zipcode mappings: {zipcode_summary['created_mappings']}")
        print(f"Used existing zipcode mappings: {zipcode_summary['existing_mappings']}")

        # Return categorized alerts and zipcode summary only if some were processed
        if processed_count > 0:
            from app.services.monitoring.alert_group_service import get_alerts_grouped_by_category_with_zipcodes
            grouped_alerts = get_alerts_grouped_by_category_with_zipcodes(db)
            
            # Add zipcode summary to the response
            result = {
                "alerts": grouped_alerts,
                "zipcode_summary": {
                    "processed_region_fips_codes": zipcode_summary["processed_same_codes"],
                    "skipped_region_fips_codes": zipcode_summary["skipped_same_codes"],
                    "found_zipcodes": zipcode_summary["found_zipcodes"],
                    "created_mappings": zipcode_summary["created_mappings"],
                    "existing_mappings": zipcode_summary["existing_mappings"]
                }
            }
            return result

    except Exception as e:
        print(f"❌ Critical error in alert processing: {str(e)}")
        db.rollback()
        raise
    
    return None

def get_alerts_grouped_by_category(
    db: Session,
    state: Optional[str] = None,
    severity: Optional[AlertSeverity] = None,
    category: Optional[str] = None,
):
    """
    Group alerts by active categories and apply optional state, severity, and category (event_type) filters
    """
    results = []
    categories = db.query(Category).filter(Category.status == True).all()

    for cat in categories:
        # Get all event names mapped to this category
        event_names = (
            db.query(Event.name)
            .join(CategoryEventMapping, CategoryEventMapping.event_id == Event.id)
            .filter(CategoryEventMapping.category_id == cat.id)
            .all()
        )

        # Flatten and lowercase names
        event_names = [name[0] for name in event_names if name[0]]

        # Create base query for alerts
        base_query = db.query(Alert)

        # Apply state filter if provided
        if state and state != "all":
            base_query = base_query.join(State).filter(State.code == state)

        # Apply severity filter if provided
        if severity and severity != "all":
            base_query = base_query.filter(Alert.severity == severity)

        matched_alerts = []
        for event_name in event_names:
            alerts = base_query.filter(Alert.event_type.ilike(f"%{event_name}%")).all()
            matched_alerts.extend(alerts)

        active_count = len(matched_alerts)

        # Extract unique states and get their codes from the states table
        state_ids = list({alert.state_id for alert in matched_alerts if alert.state_id})
        state_codes = []
        if state_ids:
            states = db.query(State).filter(State.id.in_(state_ids)).all()
            state_codes = [state.code for state in states]

        # Build affected_areas as JSON array with random policyholder counts
        affected_areas = [
            {
                "state": state_code,
                "policyholders": random.randint(500, 1000)  # Simple random value per state
            }
            for state_code in state_codes
        ]

        # Assign dynamic class based on activeCount
        if active_count >= 100:
            active_class = "bg-red-600"
        elif active_count >= 50:
            active_class = "bg-orange-500"
        elif active_count >= 10:
            active_class = "bg-yellow-400"
        else:
            active_class = "bg-green-400"

        results.append({
            "id": cat.id,
            "imageUrl": cat.image_url,
            "title": cat.name,
            "description": cat.description,
            "activeCount": active_count,
            "activeClass": active_class,  # dynamic class here
            "affectedAreas": affected_areas,
            "moreStates": 'And 6 more states...',
            "lastViewed": 'Just now',
            "alerts": matched_alerts,
        })

    return results

def process_ugc_code(code: str) -> Tuple[str, RegionType, str]:
    """Process a UGC code into state code, region type, and region code.
    UGC format: SS[CZ]nnn where SS=state, C=county, Z=zone, nnn=number.
    
    The region_code can be combined with state FIPS to create a region_fips code
    that can be used to lookup zipcodes in the zipcode dataset.
    """
    
    if not code or len(code) < 6:
        return None, None, None
        
    try:
        state_code = code[:2].upper()
        type_code = code[2].upper()
        region_code = code[3:]
        
        # Validate state code format (two uppercase letters)
        if not state_code.isalpha() or len(state_code) != 2:
            print(f"Invalid state code in UGC: {code}")
            return None, None, None
            
        # Validate type code
        if type_code not in ['C', 'Z']:
            print(f"Invalid region type in UGC: {code}")
            return None, None, None
            
        # Validate region code (should be numeric)
        if not region_code.isdigit():
            print(f"Invalid region code in UGC: {code}")
            return None, None, None
            
        region_type = RegionType.COUNTY if type_code == "C" else RegionType.ZONE
        return state_code, region_type, region_code
        
    except Exception as e:
        print(f"Error processing UGC code {code}: {str(e)}")
        return None, None, None

def process_zipcodes(
    db: Session, 
    properties: dict,
    zone_county: ZoneCounty
) -> List[Zipcode]:
    """Process and create/update zipcodes for a zone/county from alert properties.
    Returns list of associated zipcodes."""
    
    # Get zipcodes from geocode.SAME if available, otherwise from geocode.UGC
    geocode = properties.get("geocode", {})
    zip_codes = set(geocode.get("SAME", []))  # SAME codes often contain zipcode info
    
    # If no SAME codes, try to get from other sources
    if not zip_codes:
        area_desc = properties.get("areaDesc", "")
        # Extract any 5-digit numbers that might be zipcodes
        import re
        zip_matches = re.findall(r"\b\d{5}\b", area_desc)
        zip_codes.update(zip_matches)
    
    result_zipcodes = []
    
    for zip_code in zip_codes:
        try:
            # Check if zipcode already exists
            zipcode = db.query(Zipcode).filter(Zipcode.code == zip_code).first()
            
            if zipcode:
                # If zipcode exists but with different zone_county_id, create new mapping
                if zipcode.zone_county_id != zone_county.id:
                    new_zipcode = Zipcode(
                        code=zip_code,
                        name=f"ZIP {zip_code}",
                        zone_county_id=zone_county.id,
                        status=True
                    )
                    db.add(new_zipcode)
                    db.flush()
                    result_zipcodes.append(new_zipcode)
                else:
                    result_zipcodes.append(zipcode)
            else:
                # Create new zipcode
                new_zipcode = Zipcode(
                    code=zip_code,
                    name=f"ZIP {zip_code}",
                    zone_county_id=zone_county.id,
                    status=True
                )
                db.add(new_zipcode)
                db.flush()
                result_zipcodes.append(new_zipcode)
            
        except Exception as e:
            print(f"Error processing zipcode {zip_code}: {str(e)}")
            # Don't rollback here, let the outer transaction handle it
            raise  # Re-raise the error to be handled by the outer transaction
    
    return result_zipcodes
