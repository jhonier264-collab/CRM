
import logging
from typing import Dict, Any, Optional
from src.core.database_interface import IDatabase

logger = logging.getLogger(__name__)

class AddressIntelligenceService:
    """Service to handle smart address resolution and geocoding logic."""
    
    def __init__(self, db: IDatabase):
        self.db = db

    def resolve_geography_ids(self, city_name: str, state_name: str, country_name: str) -> Dict[str, Any]:
        """
        Takes human-readable names and returns the corresponding DB IDs.
        If a level doesn't exist, it can potentially trigger creation logic.
        """
        result = {
            'country_id': None,
            'state_id': None,
            'city_id': None
        }
        
        # 1. Resolve Country
        country = self.db.execute_query(
            "SELECT id FROM countries WHERE country_name LIKE %s LIMIT 1", 
            (f"%{country_name}%",)
        )
        if country:
            result['country_id'] = country[0]['id']
            
            # 2. Resolve State within Country
            state = self.db.execute_query(
                "SELECT id FROM states WHERE country_id = %s AND state_name LIKE %s LIMIT 1",
                (result['country_id'], f"%{state_name}%")
            )
            if state:
                result['state_id'] = state[0]['id']
                
                # 3. Resolve City within State
                city = self.db.execute_query(
                    "SELECT id FROM cities WHERE state_id = %s AND city_name LIKE %s LIMIT 1",
                    (result['state_id'], f"%{city_name}%")
                )
                if city:
                    result['city_id'] = city[0]['id']
                    
        return result

    def parse_google_address(self, google_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardizes a payload coming from a front-end Google Places autocomplete.
        Expects keys like: 'street', 'city', 'state', 'country', 'postal_code'.
        """
        # This is a bridge method. It extracts data and then resolves IDs.
        city = google_payload.get('city', '')
        state = google_payload.get('state', '')
        country = google_payload.get('country', '')
        
        geo_ids = self.resolve_geography_ids(city, state, country)
        
        return {
            **geo_ids,
            'address_line1': google_payload.get('street', ''),
            'postal_code': google_payload.get('postal_code', '')
        }
