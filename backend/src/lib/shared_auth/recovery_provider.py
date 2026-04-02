import random
import datetime
from typing import Optional

class RecoveryProvider:
    """
    Handles generation and validation of 6-digit recovery tokens.
    """
    
    @staticmethod
    def generate_token() -> str:
        """Generates a random 6-digit string."""
        return str(random.randint(100000, 999999))

    @staticmethod
    def is_expired(expires_at: datetime.datetime) -> bool:
        """Checks if the token has expired."""
        return datetime.datetime.utcnow() > expires_at

    @staticmethod
    def get_expiry_time(minutes: int = 10) -> datetime.datetime:
        """Returns the timestamp for expiry."""
        return datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)
