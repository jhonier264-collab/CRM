
import re
from typing import Tuple, Optional

class IdentityHygieneService:
    """Service to normalize and validate identification numbers (RUT/NIT)."""

    @staticmethod
    def normalize_rut(raw_rut: str) -> Tuple[str, Optional[int]]:
        """
        Cleans the RUT/NIT and extracts the verification digit (DV) if present.
        Example: "1.088.322.864-0" -> ("1088322864", 0)
        Example: "900.123.456 1" -> ("900123456", 1)
        """
        if not raw_rut:
            return "", None

        # Remove all special characters except alpha-numeric
        # We need to preserve the last digit if it's the DV
        
        # Step 1: Remove dots, commas, spaces
        clean = re.sub(r'[\.\,\s]', '', str(raw_rut))
        
        # Step 2: Check for hyphen as separator for DV
        if '-' in clean:
            parts = clean.split('-')
            main_rut = parts[0]
            dv_str = parts[1]
            try:
                dv = int(dv_str[0]) if dv_str else None
                return main_rut, dv
            except (ValueError, IndexError):
                return main_rut, None
        
        # Step 3: If no hyphen, check if the last digit could be a DV (common in systems)
        # But for NITs sometimes people just paste everything.
        # If it's more than 8 digits, maybe the last one is DV if it's separated or just the last digit of the string.
        # Actually, if there are no separators, we can't be 100% sure unless we calculate it.
        # For now, let's only split if there was a separator or if it's a known format.
        
        # fallback: just return the clean numeric string
        return clean, None

    @staticmethod
    def clean_numeric(text: str) -> str:
        """Removes all non-numeric characters."""
        return re.sub(r'\D', '', str(text))
