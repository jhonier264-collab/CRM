
import re
import logging
from typing import Dict, Any, List, Optional
from src.core.database_interface import IDatabase

logger = logging.getLogger(__name__)

class ContactNormalizationService:
    """Service to clean and standardize contact information before database insertion."""
    
    def __init__(self, db: IDatabase):
        self.db = db
        self._phone_codes = self._load_phone_codes()

    def reload_codes(self):
        """Refreshes the internal cache of phone codes from the DB."""
        self._phone_codes = self._load_phone_codes()
        logger.info("Phone codes cache reloaded.")

    def _load_phone_codes(self) -> List[Dict[str, Any]]:
        """Loads available phone codes from the countries table."""
        try:
            # Sort by length descending to match longest prefixes first (e.g. +1 340 before +1)
            sql = "SELECT id, phone_code FROM countries WHERE phone_code IS NOT NULL"
            codes = self.db.execute_query(sql)
            # Normalize codes for matching (remove +)
            for c in codes:
                c['clean_code'] = re.sub(r'\D', '', str(c['phone_code']))
            return sorted(codes, key=lambda x: len(x['clean_code']), reverse=True)
        except Exception as e:
            logger.error(f"Error loading phone codes: {e}")
            return []

    def normalize_phone(self, raw_phone: str) -> Dict[str, Any]:
        """
        Parses a raw phone string, detects country code, and returns clean local number.
        Example: '+57 300 123 4567' -> {'country_id': 1, 'local_number': '3001234567'}
        """
        if not raw_phone:
            return {'country_id': 1, 'local_number': ''} # Default to ID 1 (e.g. Local)
            
        # 1. Basic Cleaning: Keep only digits and '+'
        clean = re.sub(r'[^\d+]', '', raw_phone)
        
        # 2. Detect Prefix
        detected_country_id = 1 # Default
        local_number = clean
        
        if clean.startswith('+'):
            digits_only = clean[1:]
            for code in self._phone_codes:
                if digits_only.startswith(code['clean_code']):
                    detected_country_id = code['id']
                    local_number = digits_only[len(code['clean_code']):]
                    break
        else:
            # Try matching without + if it's long enough
            for code in self._phone_codes:
                if clean.startswith(code['clean_code']) and len(clean) > len(code['clean_code']) + 5:
                    detected_country_id = code['id']
                    local_number = clean[len(code['clean_code']):]
                    break
        
        return {
            'country_id': detected_country_id,
            'local_number': local_number
        }

    def normalize_email(self, raw_email: str) -> str:
        """Standardizes email to lowercase and trims whitespace."""
        if not raw_email: return ""
        return raw_email.strip().lower()
