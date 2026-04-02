from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple

class IAuthRepository(ABC):
    """
    Interface for the Auth Repository.
    This allows the AuthCore service to remain decoupled from the specific database.
    """

    @abstractmethod
    def get_user_by_identifier(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Finds a user by username or email."""
        pass

    @abstractmethod
    def update_lockout(self, user_id: int, attempts: int, locked_until: Optional[str] = None) -> None:
        """Updates failed attempts and lockout timestamp."""
        pass

    @abstractmethod
    def get_recovery_token(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieves an active recovery token for the user."""
        pass

    @abstractmethod
    def save_recovery_token(self, user_id: int, token: str, expires_at: str) -> None:
        """Saves a new recovery token."""
        pass

    @abstractmethod
    def reset_password(self, user_id: int, new_password_hash: str) -> bool:
        """Resets the user's password and clears lockout/attempts."""
        pass

    @abstractmethod
    def register_user(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Registers a new user in the global directory."""
        pass
