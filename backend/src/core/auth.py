
import logging
from typing import Set, Optional
from src.repositories.repository import UserRepository
from .exceptions import AuthError

logger = logging.getLogger(__name__)

class AccessControl:
    """Class to check permissions based on roles.
    
    Allows defining which roles have permission for specific actions.
    """

    def __init__(self, user_repo: UserRepository, allowed_roles: Optional[Set[int]] = None):
        """
        Args:
            user_repo: Repository to query the user's role.
            allowed_roles: Set of authorized role IDs.
                          Default: 1 (Admin), 2 (Agent), 3 (Special Agent).
        """
        self.repo = user_repo
        # Authorized roles per requirement: Admin, Agent, Special Agent
        self.allowed_roles = allowed_roles or {1, 2, 3}

    def has_permission(self, user_id: int, action: str) -> bool:
        """Checks if the user has permission for an action.
        
        Currently actions are validated against the set of allowed_roles.
        """
        role = self.repo.get_role(user_id)
        if not role:
            logger.warning(f"User {user_id} attempted access without an assigned role.")
            return False

        role_id = role.get('id')
        return role_id in self.allowed_roles

    def validate_permission(self, user_id: int, action: str):
        """Throws an exception if the user does not have permission."""
        if not self.has_permission(user_id, action):
            logger.error(f"Access denied: User {user_id} for action '{action}'")
            raise AuthError(f"User {user_id} does not have permissions to perform this action.")

    def update_allowed_roles(self, roles: Set[int]):
        """Allows dynamically changing authorized roles."""
        self.allowed_roles = roles