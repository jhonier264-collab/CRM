
import logging
from typing import List, Dict, Any, Optional, Type, TypeVar
from src.core.database_interface import IDatabase
from src.models.models import User, Company, Address, Phone, Email

logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseRepository:
    """Base class for repositories with common methods."""
    def __init__(self, db: IDatabase):
        self.db = db

class UserRepository(BaseRepository):
    """Repository for the Users entity."""

    def get_by_id(self, user_id: int) -> Optional[User]:
        query = "SELECT * FROM users WHERE id = %s"
        res = self.db.execute_query(query, (user_id,))
        if res:
            return User.from_dict(res[0])
        return None

    def list(self) -> List[User]:
        query = "SELECT * FROM users WHERE deleted_at IS NULL"
        res = self.db.execute_query(query)
        return [User.from_dict(row) for row in res]

    def insert(self, user: User) -> int:
        query = """
        INSERT INTO users (
            agent_id, role_id, status_id, prefix, first_name, middle_name, 
            last_name, username, password_hash, suffix, nickname,
            phonetic_first_name, phonetic_middle_name, phonetic_last_name,
            file_as, rut_nit, verification_digit, birthday, gender_id, notes,
            is_natural_person
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            user.agent_id, user.role_id, user.status_id, user.prefix,
            user.first_name, user.middle_name, user.last_name,
            user.username, user.password_hash, user.suffix, user.nickname,
            user.phonetic_first_name, user.phonetic_middle_name, user.phonetic_last_name,
            user.file_as, user.rut_nit, user.verification_digit, user.birthday,
            user.gender_id, user.notes, 1 if user.is_natural_person else 0
        )
        return self.db.execute_query(query, params, commit=True, is_select=False)

    def update(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Updates user data dynamically."""
        if not data:
            return False
        fields = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE users SET {fields} WHERE id = %s"
        params = list(data.values()) + [user_id]
        return self.db.execute_query(query, params, commit=True, is_select=False)

    def delete(self, user_id: int) -> bool:
        """Moves a user to the recycling bin (Soft Delete)."""
        query = "UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s"
        return self.db.execute_query(query, (user_id,), commit=True, is_select=False)

    def find_by_username(self, username: str) -> Optional[User]:
        """Finds a user by their username for login purposes."""
        query = "SELECT * FROM users WHERE username = %s"
        res = self.db.execute_query(query, (username,))
        if res:
            return User.from_dict(res[0])
        return None

    def get_role(self, user_id: int) -> Optional[Dict[str, Any]]:
        query = """
        SELECT r.id, r.role_name 
        FROM roles r 
        JOIN users u ON u.role_id = r.id 
        WHERE u.id = %s
        """
        data = self.db.execute_query(query, (user_id,))
        return data[0] if data else None

class CompanyRepository(BaseRepository):
    """Repository for the Companies entity."""

    def get_by_id(self, company_id: int) -> Optional[Company]:
        query = "SELECT * FROM companies WHERE id = %s"
        res = self.db.execute_query(query, (company_id,))
        if res:
            return Company.from_dict(res[0])
        return None

    def list(self) -> List[Company]:
        query = "SELECT * FROM companies WHERE deleted_at IS NULL"
        res = self.db.execute_query(query)
        return [Company.from_dict(row) for row in res]

    def insert(self, company: Company) -> int:
        query = """
        INSERT INTO companies (
            agent_id, status_id, rut_nit, verification_digit, legal_name,
            commercial_name, description, domain, revenue
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            company.agent_id, company.status_id, company.rut_nit, company.verification_digit,
            company.legal_name, company.commercial_name, company.description,
            company.domain, company.revenue
        )
        return self.db.execute_query(query, params, commit=True, is_select=False)

    def update(self, company_id: int, data: Dict[str, Any]) -> bool:
        """Updates company data dynamically."""
        if not data:
            return False
        fields = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE companies SET {fields} WHERE id = %s"
        params = list(data.values()) + [company_id]
        return self.db.execute_query(query, params, commit=True, is_select=False)

    def delete(self, company_id: int) -> bool:
        """Moves a company to the recycling bin (Soft Delete)."""
        query = "UPDATE companies SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s"
        return self.db.execute_query(query, (company_id,), commit=True, is_select=False)

class ContactRepository(BaseRepository):
    """Unified repository for Addresses, Phones, and Emails."""

    def insert_address(self, d: Address) -> int:
        query = """
        INSERT INTO addresses (
            user_id, company_id, country_id, state_id, city_id,
            address_line1, address_line2, postal_code
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            d.user_id, d.company_id, d.country_id, d.state_id,
            d.city_id, d.address_line1, d.address_line2, d.postal_code
        )
        return self.db.execute_query(query, params, commit=True, is_select=False)

    def insert_phone(self, t: Phone) -> int:
        query = """
        INSERT INTO phones (user_id, company_id, country_id, local_number, label_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (t.user_id, t.company_id, t.country_id, t.local_number, t.label_id)
        return self.db.execute_query(query, params, commit=True, is_select=False)

    def insert_email(self, e: Email) -> int:
        query = """
        INSERT INTO emails (user_id, company_id, email_address, label_id)
        VALUES (%s, %s, %s, %s)
        """
        params = (e.user_id, e.company_id, e.email_address, e.label_id)
        return self.db.execute_query(query, params, commit=True, is_select=False)

    def update_address(self, address_id: int, data: Dict[str, Any]) -> bool:
        fields = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE addresses SET {fields} WHERE id = %s"
        return self.db.execute_query(query, list(data.values()) + [address_id], commit=True, is_select=False)

    def update_phone(self, phone_id: int, data: Dict[str, Any]) -> bool:
        fields = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE phones SET {fields} WHERE id = %s"
        return self.db.execute_query(query, list(data.values()) + [phone_id], commit=True, is_select=False)

    def update_email(self, email_id: int, data: Dict[str, Any]) -> bool:
        fields = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE emails SET {fields} WHERE id = %s"
        return self.db.execute_query(query, list(data.values()) + [email_id], commit=True, is_select=False)

    def delete_contacts_by_user(self, user_id: int):
        """Deletes all contacts associated with a user."""
        queries = [
            "DELETE FROM phones WHERE user_id = %s",
            "DELETE FROM emails WHERE user_id = %s",
            "DELETE FROM addresses WHERE user_id = %s"
        ]
        for q in queries:
            self.db.execute_query(q, (user_id,), commit=True, is_select=False)

    def delete_contacts_by_company(self, company_id: int):
        """Deletes all contacts associated with a company."""
        queries = [
            "DELETE FROM phones WHERE company_id = %s",
            "DELETE FROM emails WHERE company_id = %s",
            "DELETE FROM addresses WHERE company_id = %s"
        ]
        for q in queries:
            self.db.execute_query(q, (company_id,), commit=True, is_select=False)
