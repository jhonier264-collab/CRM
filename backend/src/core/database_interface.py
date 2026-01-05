
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Any, Dict, List, Optional

class IDatabase(ABC):
    """Minimum interface for the database manager used by repositories.
    
    Defines methods that a concrete implementation must offer to allow
    dependency inversion and simplify testing.
    """

    @abstractmethod
    def connect(self) -> Any:
        """Connect to the database."""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Optional[tuple] = None, commit: bool = False, is_select: bool = True) -> Any:
        """Execute a SQL query."""
        pass

    @abstractmethod
    def transaction(self) -> AbstractContextManager:
        """Handle transactions."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the connection."""
        pass
