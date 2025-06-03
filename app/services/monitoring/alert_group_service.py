from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.monitoring.alert import Alert, AlertSeverity
from app.models.common.category import Category
from app.models.common.category_event_mappings import CategoryEventMapping
from app.models.common.events import Event
from app.models.common.state import State
from app.models.common.zones_counties import ZoneCounty, RegionType
from app.models.monitoring.alert_affected_area import AlertAffectedArea, RegionType as AreaRegionType
from app.models.common.zipcodes import Zipcode
from app.models.common.policyholders import Policyholder

import logging

logger = logging.getLogger(__name__)

def alert_to_dict(alert: Alert, db: Session = None) -> Dict[str, Any]:
    """Convert Alert model to dictionary."""
    # Get state code if state is available
    state_code = None
    if hasattr(alert, 'state') and alert.state:
        state_code = alert.state.code

    # Initialize affected_areas structure
    alert_affected_areas = []
    
    if db:
        # Get affected areas for this alert
        affected_areas = (
            db.query(AlertAffectedArea)
            .filter(AlertAffectedArea.alert_id == alert.id)
            .all()
        )

        state_details = {}
        processed_zones = set()

        for area in affected_areas:
            if not area.zone_county_id or area.zone_county_id in processed_zones:
                continue

            processed_zones.add(area.zone_county_id)
            zone_county = db.query(ZoneCounty).filter(ZoneCounty.id == area.zone_county_id).first()
            if not zone_county:
                continue

            # Get all zipcodes for this zone/county
            zipcode_areas = (
                db.query(AlertAffectedArea)
                .filter(
                    and_(
                        AlertAffectedArea.alert_id == alert.id,
                        AlertAffectedArea.zone_county_id == zone_county.id,
                        AlertAffectedArea.region_type == AreaRegionType.ZIPCODE
                    )
                )
                .all()
            )

            zipcode_details = []
            policyholders_info = []
            for zip_area in zipcode_areas:
                if not zip_area.zipcode_id:
                    continue

                zipcode = db.query(Zipcode).filter(Zipcode.id == zip_area.zipcode_id).first()
                if zipcode:
                     # Get actual policyholder count for this zipcode
                        policyholder_count = db.query(Policyholder).filter(
                            Policyholder.zipcode_id == zip_area.zipcode_id,
                            Policyholder.status == True
                        ).count()
                        
                        if policyholder_count > 0:
                            zipcode_details.append(zipcode.code)
                            policyholders_info.append({
                                "zipcode": zipcode.code,
                                "policyholder_count": policyholder_count,
                                "policyholders": [
                                    {
                                        "id": p.id,
                                        "policy_id": p.policy_id,
                                        "name": p.name,
                                        "email": p.email,
                                        "phoneno": p.phoneno,
                                        "address": p.address,
                                        "state": db.query(State).filter(State.id == p.state_id).first().name if p.state_id else None,
                                        "county": db.query(ZoneCounty).filter(ZoneCounty.id == p.county_id).first().code if p.county_id else None,
                                        "claims": p.claims,
                                        "premium": p.premium
                                    }
                                    for p in db.query(Policyholder).filter(
                                        Policyholder.zipcode_id == zip_area.zipcode_id,
                                        Policyholder.status == True
                                    ).all()
                                ]
                            })

            if zipcode_details:  # Only add if there are zipcodes
                if state_code not in state_details:
                    state_details[state_code] = {
                        "state": state_code,
                        "county_zone": [],
                    }
                
                zone_info = {
                    "type": zone_county.type.value,
                    "name": zone_county.name,
                    "code": zone_county.code,
                    "zipcodes": zipcode_details,
                    "policyholders_info": policyholders_info
                }
                state_details[state_code]["county_zone"].append(zone_info)

        alert_affected_areas = list(state_details.values())

    return {
        "id": alert.id,
        "event_id": alert.external_id,
        "event_type": alert.event_type,
        "event_timestamp": alert.event_timestamp.isoformat() if alert.event_timestamp else None,
        "event_title": alert.title,
        "event_description": alert.description,
        "severity": alert.severity.value if alert.severity else None,
        "status": alert.status.value if alert.status else None,
        # "state": state_code,
        "source": alert.source,
        # "created_at": alert.created_at.isoformat() if alert.created_at else None,
        # "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
        "affected_areas": alert_affected_areas
    }

def get_alerts_grouped_by_category_with_zipcodes(
    db: Session,
    state: Optional[str] = None,
    severity: Optional[AlertSeverity] = None,
    category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Extended version of get_alerts_grouped_by_category that includes detailed zipcode information
    grouped by state and county/zone.
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

        event_names = [name[0] for name in event_names if name[0]]
        try:
            # Start with basic query and always join with State
            base_query = db.query(Alert).options(joinedload(Alert.state))
            
            # Add state filter if provided
            # # Add joins and filters
            # if state and state != "all":
            #     base_query = (
            #         base_query
            #         .join(State, Alert.state_id == State.id)
            #         .filter(State.code == state)
            #     )
            # if severity and severity != "all":
            #     base_query = base_query.filter(Alert.severity == severity)

            logger.info("Built basic query without filters")
                
        except Exception as e:
            logger.error(f"Error building alert query: {str(e)}")
            raise

        matched_alerts = []
        for event_name in event_names:
            alerts = base_query.filter(Alert.event_type.ilike(f"%{event_name}%")).all()
            matched_alerts.extend(alerts)

        active_count = len(matched_alerts)

        # Process affected areas with detailed information
        # state_details = {}
        # for alert in matched_alerts:
        #     if not alert.state_id:
        #         continue

        #     try:
        #         # Get state from database if it's not loaded
        #         if alert.state_id:
        #             if not alert.state:
        #                 state = db.query(State).filter(State.id == alert.state_id).first()
        #             else:
        #                 state = alert.state

        #             if not state:
        #                 logger.warning(f"No state found for alert {alert.id} with state_id {alert.state_id}")
        #                 continue

        #             state_code = state.code
        #             logger.debug(f"Processing state {state_code} for alert {alert.id}")
        #         else:
        #             logger.warning(f"No state_id for alert {alert.id}")
        #             continue
        #     except Exception as e:
        #         logger.error(f"Error processing state for alert {alert.id}: {str(e)}")
        #         continue
        #     if state_code not in state_details:
        #         state_details[state_code] = {
        #             "state": state_code,
        #             "county_zone": [],
        #         }

        #     # Get affected areas for this alert
        #     affected_areas = (
        #         db.query(AlertAffectedArea)
        #         .filter(AlertAffectedArea.alert_id == alert.id)
        #         .all()
        #     )

            # Process each affected area
            # processed_zones = set()  # Track processed zones to avoid duplicates
            # for area in affected_areas:
            #     if not area.zone_county_id or area.zone_county_id in processed_zones:
            #         continue

            #     processed_zones.add(area.zone_county_id)
            #     zone_county = db.query(ZoneCounty).filter(ZoneCounty.id == area.zone_county_id).first()
            #     if not zone_county:
            #         continue

            #     # Get all zipcodes for this zone/county
            #     zipcode_areas = (
            #         db.query(AlertAffectedArea)
            #         .filter(
            #             and_(
            #                 AlertAffectedArea.alert_id == alert.id,
            #                 AlertAffectedArea.zone_county_id == zone_county.id,
            #                 AlertAffectedArea.region_type == AreaRegionType.ZIPCODE
            #             )
            #         )
            #         .all()
            #     )

            #     zipcode_details = []
            #     policyholders_info = []
            #     for zip_area in zipcode_areas:
            #         if not zip_area.zipcode_id:
            #             continue

            #         zipcode = db.query(Zipcode).filter(Zipcode.id == zip_area.zipcode_id).first()
            #         if zipcode:
            #             # Get actual policyholder count for this zipcode
            #             policyholder_count = db.query(Policyholder).filter(
            #                 Policyholder.zipcode_id == zip_area.zipcode_id,
            #                 Policyholder.status == True
            #             ).count()
                        
            #             if policyholder_count > 0:
            #                 zipcode_details.append(zipcode.code)
            #                 policyholders_info.append({
            #                     "zipcode": zipcode.code,
            #                     "policyholder_count": policyholder_count,
            #                     "policyholders": [
            #                         {
            #                             "id": p.id,
            #                             "policy_id": p.policy_id,
            #                             "name": p.name,
            #                             "email": p.email,
            #                             "phoneno": p.phoneno,
            #                             "address": p.address,
            #                             "state": db.query(State).filter(State.id == p.state_id).first().name if p.state_id else None,
            #                             "county": db.query(ZoneCounty).filter(ZoneCounty.id == p.county_id).first().code if p.county_id else None,
            #                             "claims": p.claims,
            #                             "premium": p.premium
            #                         }
            #                         for p in db.query(Policyholder).filter(
            #                             Policyholder.zipcode_id == zip_area.zipcode_id,
            #                             Policyholder.status == True
            #                         ).all()
            #                     ]
            #                 })

            #     if zipcode_details:  # Only add if there are zipcodes with policyholders
            #         zone_info = {
            #             "type": zone_county.type.value,
            #             "name": zone_county.name,
            #             "code": zone_county.code,
            #             "zipcodes": zipcode_details,
            #             "policyholders_info": policyholders_info
            #         }
            #         state_details[state_code]["county_zone"].append(zone_info)

        # Convert state_details to list and calculate totals
        # affected_areas = list(state_details.values())

        # Assign dynamic class based on activeCount
        # active_class = (
        #     "bg-red-600" if active_count >= 100
        #     else "bg-orange-500" if active_count >= 50
        #     else "bg-yellow-400" if active_count >= 10
        #     else "bg-green-400"
        # )

        # Convert Alert objects to dictionaries
        serialized_alerts = [alert_to_dict(alert, db) for alert in matched_alerts]
        
        results.append({
            "cat_id": cat.id,
            # "imageUrl": cat.image_url,
            "cat_title": cat.name,
            "cat_description": cat.description,
            "activeCount": active_count,
            # "activeClass": active_class,
            # "affectedAreas": affected_areas,
            # "lastViewed": 'Just now',
            "cat_events": serialized_alerts
        })

    return results
