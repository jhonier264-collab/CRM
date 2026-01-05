import logging
import bcrypt
import re
from typing import Optional, List, Dict, Any
from src.core.database_interface import IDatabase
from src.repositories.repository import UserRepository, CompanyRepository, ContactRepository
from src.models.models import User, Company, Address, Phone, Email
from src.services.contact_normalization_service import ContactNormalizationService
from src.services.address_intelligence_service import AddressIntelligenceService
from src.services.identity_hygiene_service import IdentityHygieneService
from src.core.exceptions import ValidationError, XORRuleViolation, DatabaseError, AuthError

logger = logging.getLogger(__name__)

class CRMService:
    """Service class to orchestrate business logic and persistence."""

    def __init__(self, db: IDatabase):
        self.db = db
        self.u_repo = UserRepository(db)
        self.c_repo = CompanyRepository(db)
        self.cont_repo = ContactRepository(db)
        self.normalizer = ContactNormalizationService(db)
        self.geo_intel = AddressIntelligenceService(db)
        self.identity_hygiene = IdentityHygieneService()

    def hash_password(self, password: str) -> str:
        """Generates a secure hash for the password."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str, hashed_password: str) -> bool:
        """Verifies if the password matches the hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def login(self, username: str, password: str) -> Optional[User]:
        """Authentication process."""
        user = self.u_repo.find_by_username(username)
        if user and user.password_hash:
            if self.check_password(password, user.password_hash):
                logger.info(f"Successful login for user: {username}")
                return user
        logger.warning(f"Failed login attempt for user: {username}")
        raise AuthError("Invalid credentials")

    def register_user_secure(self, user: User, password_plain: str) -> int:
        """Registers a user with a hashed password."""
        user.password_hash = self.hash_password(password_plain)
        return self.u_repo.insert(user)

    def _validate_xor(self, user_id: Optional[int], company_id: Optional[int]):
        """Validates that exactly one of the two IDs is present."""
        if user_id and company_id:
            raise XORRuleViolation("Cannot assign to both a User and a Company simultaneously.")
        if not user_id and not company_id:
            raise XORRuleViolation("Must assign the contact to either a User or a Company.")

    def create_user_complete(self, 
                             user: User, 
                             phones: List[Phone] = None, 
                             emails: List[Email] = None, 
                             addresses: List[Address] = None,
                             password: str = None) -> int:
        """Creates a user with their contact info in a single transaction."""
        try:
            with self.db.transaction() as cursor:
                # 0. Validation & Normalization
                if user.rut_nit:
                    user.rut_nit, dv = self.identity_hygiene.normalize_rut(user.rut_nit)
                    if dv is not None:
                        user.verification_digit = dv

                if user.is_natural_person and not user.rut_nit:
                    raise ValidationError("RUT/NIT is mandatory for Natural Persons.")

                # 0.1 Password Handling
                if password:
                    user.password_hash = self.hash_password(password)

                # 1. Insert User
                sql_u = """
                INSERT INTO users (
                    agent_id, role_id, status_id, prefix, first_name, middle_name, 
                    last_name, username, password_hash, suffix, rut_nit, verification_digit,
                    is_natural_person
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params_u = (
                    user.agent_id, user.role_id if user.role_id is not None else 1, user.status_id, user.prefix,
                    user.first_name, user.middle_name, user.last_name,
                    user.username, user.password_hash,
                    user.suffix, user.rut_nit, user.verification_digit,
                    1 if user.is_natural_person else 0
                )
                cursor.execute(sql_u, params_u)
                u_id = cursor.lastrowid
                
                # 2. Insert Phones (with Proactive Normalization)
                if phones:
                    sql_t = "INSERT INTO phones (user_id, company_id, country_id, local_number, label_id) VALUES (%s, NULL, %s, %s, %s)"
                    for t in phones:
                        # Clean the phone before saving
                        norm = self.normalizer.normalize_phone(t.local_number)
                        cursor.execute(sql_t, (u_id, norm['country_id'], norm['local_number'], t.label_id))
                
                # 3. Insert Emails
                if emails:
                    sql_c = "INSERT INTO emails (user_id, company_id, email_address, label_id) VALUES (%s, NULL, %s, %s)"
                    for c in emails:
                        clean_email = self.normalizer.normalize_email(c.email_address)
                        cursor.execute(sql_c, (u_id, clean_email, c.label_id))
                
                # 4. Insert Addresses
                if addresses:
                    sql_d = """
                    INSERT INTO addresses (
                        user_id, company_id, country_id, state_id, city_id,
                        address_line1, address_line2, postal_code
                    ) VALUES (%s, NULL, %s, %s, %s, %s, %s, %s)
                    """
                    for d in addresses:
                        cursor.execute(sql_d, (u_id, d.country_id, d.state_id, d.city_id, d.address_line1, d.address_line2, d.postal_code))
                
                logger.info(f"User {u_id} successfully created with contacts.")
                
                # Audit Log
                self._log_audit(None, 'CREATE', 'USER', u_id, f"Created user {user.username or u_id} with role {user.role_id}")
                
                return u_id
                
        except Exception as e:
            logger.error(f"Error creating complete user: {e}")
            raise

    def delete_user_complete(self, user_id: int):
        """Moves a user to the recycling bin (Soft Delete)."""
        try:
            # First verify if the user exists
            user = self.u_repo.get_by_id(user_id)
            if not user:
                raise ValidationError(f"User with ID {user_id} not found")

            # Simple soft delete of the user record
            res = self.u_repo.delete(user_id)
            
            # Audit Log
            self._log_audit(None, 'SOFT_DELETE', 'USER', user_id, f"Soft deleted user {user.first_name} {user.last_name}")
            return res
        except Exception as e:
            logger.error(f"Error soft-deleting complete user: {e}")
            raise

    def delete_company_complete(self, company_id: int):
        """Moves a company to the recycling bin (Soft Delete)."""
        try:
            # First verify if the company exists
            company = self.c_repo.get_by_id(company_id)
            if not company:
                raise ValidationError(f"Company with ID {company_id} not found")

            # Soft delete
            res = self.c_repo.delete(company_id)
            
            # Audit Log
            self._log_audit(None, 'SOFT_DELETE', 'COMPANY', company_id, f"Soft deleted company {company.legal_name}")
            return res
        except Exception as e:
            logger.error(f"Error soft-deleting company: {e}")
            raise

    def add_phone(self, phone: Phone):
        """Adds a phone validating the XOR rule."""
        self._validate_xor(phone.user_id, phone.company_id)
        return self.cont_repo.insert_phone(phone)

    def add_email(self, email: Email):
        """Adds an email validating the XOR rule."""
        self._validate_xor(email.user_id, email.company_id)
        return self.cont_repo.insert_email(email)

    def add_address(self, address: Address):
        """Adds an address validating the XOR rule."""
        self._validate_xor(address.user_id, address.company_id)
        return self.cont_repo.insert_address(address)

    def update_user_basic(self, user_id: int, data: dict):
        """Updates basic user data, protecting read-only fields."""
        data.pop('id', None)
        data.pop('created_at', None)
        data.pop('updated_at', None) # Let DB handle this
        return self.u_repo.update(user_id, data)

    def update_company_basic(self, company_id: int, data: dict):
        """Updates basic company data, protecting read-only fields."""
        data.pop('id', None)
        data.pop('created_at', None)
        data.pop('updated_at', None) # Let DB handle this
        
        if 'domain' in data:
            data['domain'] = self.standardize_domain(data['domain'])
            
        res = self.c_repo.update(company_id, data)
        # Audit Log
        self._log_audit(None, 'UPDATE', 'COMPANY', company_id, f"Updated company basic info: {list(data.keys())}")
        return res

    def update_phone(self, phone_id: int, data: dict):
        data.pop('id', None)
        data.pop('created_at', None)
        return self.cont_repo.update_phone(phone_id, data)

    def update_email(self, email_id: int, data: dict):
        data.pop('id', None)
        data.pop('created_at', None)
        return self.cont_repo.update_email(email_id, data)

    def update_address(self, address_id: int, data: dict):
        data.pop('id', None)
        data.pop('created_at', None)
        return self.cont_repo.update_address(address_id, data)

    @staticmethod
    def standardize_domain(domain: Optional[str]) -> Optional[str]:
        """Cleans domain: removes protocol (http/s), 'www.', trailing slashes and lowers it."""
        if not domain:
            return None
        # Lower and strip
        clean = domain.lower().strip()
        # Remove protocol
        clean = re.sub(r'^https?://', '', clean)
        # Remove www.
        clean = re.sub(r'^www\.', '', clean)
        # Remove trailing slash
        clean = clean.rstrip('/')
        return clean

    def create_company_complete(self, 
                                company: Company, 
                                phones: List[Phone] = None, 
                                emails: List[Email] = None, 
                                addresses: List[Address] = None) -> int:
        """Creates a company with its contact info in a single transaction."""
        try:
            if company.domain:
                company.domain = self.standardize_domain(company.domain)
                
            with self.db.transaction() as cursor:
                # 0. Normalization
                if company.rut_nit:
                    company.rut_nit, dv = self.identity_hygiene.normalize_rut(company.rut_nit)
                    if dv is not None:
                        company.verification_digit = dv

                # 1. Insert Company
                sql_c = "INSERT INTO companies (legal_name, rut_nit, verification_digit, status_id, domain) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql_c, (company.legal_name, company.rut_nit, company.verification_digit, company.status_id, company.domain))
                c_id = cursor.lastrowid
                
                # 2. Insert Phones (Normalized)
                if phones:
                    sql_p = "INSERT INTO phones (user_id, company_id, country_id, local_number, label_id) VALUES (NULL, %s, %s, %s, %s)"
                    for p in phones:
                        norm = self.normalizer.normalize_phone(p.local_number)
                        cursor.execute(sql_p, (c_id, norm['country_id'], norm['local_number'], p.label_id))
                
                # 3. Insert Emails (Normalized)
                if emails:
                    sql_e = "INSERT INTO emails (user_id, company_id, email_address, label_id) VALUES (NULL, %s, %s, %s)"
                    for e in emails:
                        clean_email = self.normalizer.normalize_email(e.email_address)
                        cursor.execute(sql_e, (c_id, clean_email, e.label_id))
                
                # 4. Insert Addresses
                if addresses:
                    sql_a = """
                    INSERT INTO addresses (
                        user_id, company_id, country_id, state_id, city_id,
                        address_line1, address_line2, postal_code
                    ) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)
                    """
                    for a in addresses:
                        cursor.execute(sql_a, (c_id, a.country_id, a.state_id, a.city_id, a.address_line1, a.address_line2, a.postal_code))
                
                # Audit Log
                self._log_audit(None, 'CREATE', 'COMPANY', c_id, f"Created company {company.legal_name}")
                
                return c_id
        except Exception as e:
            logger.error(f"Error creating company complete: {e}")
            raise

    def link_user_to_company(self, user_id: int, company_id: int, position_id: int = 1, department_id: int = 1):
        """Creates a professional link between a user and a company using Department and Position IDs."""
        sql = """
        INSERT INTO user_companies (user_id, company_id, position_id, company_department_id)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            position_id = VALUES(position_id), 
            company_department_id = VALUES(company_department_id)
        """
        return self.db.execute_query(sql, (user_id, company_id, position_id, department_id), commit=True, is_select=False)

    def unlink_user_from_company(self, user_id: int, company_id: int):
        """Removes the professional link between a user and a company."""
        sql = "DELETE FROM user_companies WHERE user_id = %s AND company_id = %s"
        res = self.db.execute_query(sql, (user_id, company_id), commit=True, is_select=False)
        
        # Audit Log
        self._log_audit(None, 'UNLINK', 'COMPANY', company_id, f"Unlinked User {user_id}")
        return res

    def get_cargos(self) -> List[Dict[str, Any]]:
        """Retrieves the list of available job titles (cargos)."""
        return self.db.execute_query("SELECT id, position_name FROM positions")

    def get_departments(self) -> List[Dict[str, Any]]:
        """Retrieves the list of company departments."""
        return self.db.execute_query("SELECT id, department_name FROM company_departments")

    # --- Hierarchy & Relations (Reciprocal Logic) ---
    def get_genders(self) -> List[Dict[str, Any]]:
        """Retrieves standardized genders."""
        return self.db.execute_query("SELECT id, gender_name FROM genders")

    def get_labels(self) -> List[Dict[str, Any]]:
        """Retrieves contact labels (Personal, Work, etc)."""
        return self.db.execute_query("SELECT id, label_name FROM labels")

    def get_company_relation_types(self) -> List[Dict[str, Any]]:
        """Retrieves relation types for COMPANIES."""
        return self.db.execute_query("SELECT id, name, inverse_name FROM company_relation_types")

    def get_user_relation_types(self) -> List[Dict[str, Any]]:
        """Retrieves relation types for USERS."""
        return self.db.execute_query("SELECT id, name, inverse_name FROM user_relation_types")

    def add_user_relation_type(self, name: str, inverse_name: str):
        """Adds a new human relation type."""
        sql = "INSERT INTO user_relation_types (name, inverse_name) VALUES (%s, %s)"
        return self.db.execute_query(sql, (name, inverse_name), commit=True, is_select=False)

    def delete_user_relation_type(self, type_id: int):
        """Deletes a relation type if not in use (simplified)."""
        return self.db.execute_query("DELETE FROM user_relation_types WHERE id = %s", (type_id,), commit=True, is_select=False)

    def get_tags(self) -> List[Dict[str, Any]]:
        """Retrieves all tags."""
        return self.db.execute_query("SELECT id, name, color FROM tags")

    def add_tag(self, name: str, color: str = '#808080'):
        """Adds a new tag."""
        sql = "INSERT INTO tags (name, color) VALUES (%s, %s)"
        return self.db.execute_query(sql, (name, color), commit=True, is_select=False)

    # --- Generic Lookup Management (Cargos, Deptos, Status, etc.) ---

    def get_lookup_data(self, table: str) -> List[Dict[str, Any]]:
        """Generic method to fetch list data from any lookup table."""
        # Simple whitelist for safety
        allowed = ['cargos', 'departamentos_empresa', 'status_types', 'genders', 'tags', 'user_relation_types', 'company_relation_types']
        if table not in allowed: return []
        return self.db.execute_query(f"SELECT * FROM {table}")

    def add_lookup_item(self, table: str, data: Dict[str, Any]):
        """Generic method to add an item to a lookup table."""
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({fields}) VALUES ({placeholders})"
        return self.db.execute_query(sql, tuple(data.values()), commit=True, is_select=False)

    def delete_lookup_item(self, table: str, item_id: int):
        """Generic method to delete an item."""
        return self.db.execute_query(f"DELETE FROM {table} WHERE id = %s", (item_id,), commit=True, is_select=False)

    def link_companies(self, parent_id: int, child_id: int, relation_type_id: int):
        """Creates a link between companies using company_relation_types."""
        sql = """
        INSERT INTO company_associations (parent_company_id, child_company_id, relation_type_id)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE relation_type_id = VALUES(relation_type_id)
        """
        return self.db.execute_query(sql, (parent_id, child_id, relation_type_id), commit=True, is_select=False)

    def link_users(self, from_id: int, to_id: int, relation_type_id: int, custom_label: str = None):
        """Creates a reciprocal link between two users using user_relation_types."""
        sql = """
        INSERT INTO user_user_relations (from_user_id, to_user_id, relation_type_id, custom_label)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE relation_type_id = VALUES(relation_type_id), custom_label = VALUES(custom_label)
        """
        return self.db.execute_query(sql, (from_id, to_id, relation_type_id, custom_label), commit=True, is_select=False)

    def get_company_contacts(self, company_id: int) -> List[User]:
        """Retrieves all users linked to a specific company."""
        sql = """
        SELECT u.* FROM users u
        JOIN user_companies uc ON uc.user_id = u.id
        WHERE uc.company_id = %s
        """
        res = self.db.execute_query(sql, (company_id,))
        return [User.from_dict(row) for row in res]

    def list_natural_persons(self) -> List[User]:
        """Lists users specifically marked as natural persons (B2C)."""
        sql = "SELECT * FROM users WHERE is_natural_person = TRUE"
        res = self.db.execute_query(sql)
        return [User.from_dict(row) for row in res]

    def unlink_user_from_company(self, user_id: int, company_id: int):
        """Removes the corporate relationship."""
        sql = "DELETE FROM user_companies WHERE user_id = %s AND company_id = %s"
        return self.db.execute_query(sql, (user_id, company_id), commit=True, is_select=False)

    # --- Geographical Management (Phase 13) ---

    def list_countries(self) -> List[Dict[str, Any]]:
        return self.db.execute_query("SELECT id, country_name, phone_code FROM countries ORDER BY country_name")

    def add_country(self, name: str, phone_code: str = None, area: float = 0, population: int = 0) -> int:
        sql = "INSERT INTO countries (country_name, phone_code, area_km2, population) VALUES (%s, %s, %s, %s)"
        c_id = self.db.execute_query(sql, (name, phone_code, area, population), commit=True, is_select=False)
        # Notify normalizer to reload codes
        if hasattr(self, 'normalizer'):
            self.normalizer.reload_codes()
        return c_id

    def list_states(self, country_id: int) -> List[Dict[str, Any]]:
        return self.db.execute_query("SELECT id, state_name FROM states WHERE country_id = %s ORDER BY state_name", (country_id,))

    def add_state(self, name: str, country_id: int, area: float = 0, population: int = 0) -> int:
        sql = "INSERT INTO states (state_name, country_id, area_km2, population) VALUES (%s, %s, %s, %s)"
        return self.db.execute_query(sql, (name, country_id, area, population), commit=True, is_select=False)

    def _log_audit(self, actor_id: Optional[int], action_type: str, entity_type: str, entity_id: int, details: str = None):
        """Helper to insert audit logs."""
        try:
            self.db.execute_query(
                "INSERT INTO audit_logs (actor_id, action_type, entity_type, entity_id, details) VALUES (%s, %s, %s, %s, %s)",
                (actor_id, action_type, entity_type, entity_id, details),
                is_select=False,
                commit=False
            )
        except Exception as e:
            logger.error(f"Failed to log audit: {e}")

    def list_cities(self, state_id: int) -> List[Dict[str, Any]]:
        return self.db.execute_query("SELECT id, city_name FROM cities WHERE state_id = %s ORDER BY city_name", (state_id,))

    def add_city(self, name: str, state_id: int, area: float = 0, population: int = 0) -> int:
        sql = "INSERT INTO cities (city_name, state_id, area_km2, population) VALUES (%s, %s, %s, %s)"
        return self.db.execute_query(sql, (name, state_id, area, population), commit=True, is_select=False)

    # --- Summary Views for Frontend (Phase 16) ---

    def get_users_summary(self) -> List[Dict[str, Any]]:
        """Retrieves users with primary email, phone and company for the list view."""
        sql = """
        SELECT 
            u.id, u.first_name, u.last_name, 
            CONCAT(u.rut_nit, IF(u.verification_digit IS NOT NULL, CONCAT('-', u.verification_digit), '')) as rut_nit,
            (SELECT email_address FROM emails WHERE user_id = u.id LIMIT 1) as email,
            (SELECT local_number FROM phones WHERE user_id = u.id LIMIT 1) as phone,
            (SELECT GROUP_CONCAT(c.legal_name SEPARATOR ', ') 
             FROM companies c 
             JOIN user_companies uc ON uc.company_id = c.id 
             WHERE uc.user_id = u.id) as company
        FROM users u
        WHERE u.deleted_at IS NULL
        """
        return self.db.execute_query(sql)

    def get_companies_summary(self) -> List[Dict[str, Any]]:
        """Retrieves companies with primary contact info and full tax ID."""
        sql = """
        SELECT 
            c.id, c.legal_name, c.commercial_name, 
            CONCAT(c.rut_nit, IF(c.verification_digit IS NOT NULL, CONCAT('-', c.verification_digit), '')) as rut_nit,
            c.domain, c.revenue,
            (SELECT email_address FROM emails WHERE company_id = c.id LIMIT 1) as email,
            (SELECT local_number FROM phones WHERE company_id = c.id LIMIT 1) as phone
        FROM companies c
        WHERE c.deleted_at IS NULL
        """
        return self.db.execute_query(sql)

    def update_user_complete(self, user_id: int, data: Dict[str, Any]):
        """Updates user basic info and its multiple contacts in one transaction."""
        try:
            with self.db.transaction() as cursor:
                # 1. Update basic info
                fields_to_update = {k: v for k, v in data.items() if k in {f.name for f in User.__dataclass_fields__.values()} and k not in ['id', 'created_at', 'updated_at']}
                
                # Normalization for user identity
                if 'rut_nit' in fields_to_update and fields_to_update['rut_nit']:
                    fields_to_update['rut_nit'], dv = self.identity_hygiene.normalize_rut(fields_to_update['rut_nit'])
                    if dv is not None:
                        fields_to_update['verification_digit'] = dv

                if fields_to_update:
                    set_clause = ", ".join([f"{k} = %s" for k in fields_to_update.keys()])
                    sql_u = f"UPDATE users SET {set_clause} WHERE id = %s"
                    cursor.execute(sql_u, list(fields_to_update.values()) + [user_id])

                # 2. Sync Phones
                if 'phones' in data:
                    incoming_phones = data['phones']
                    # Keep valid ones
                    keep_ids = [p['id'] for p in incoming_phones if p.get('id')]
                    if keep_ids:
                        cursor.execute("DELETE FROM phones WHERE user_id = %s AND id NOT IN (%s)" % (user_id, ",".join(["%s"]*len(keep_ids))), keep_ids)
                    else:
                        cursor.execute("DELETE FROM phones WHERE user_id = %s", (user_id,))
                    
                    for p in incoming_phones:
                        norm = self.normalizer.normalize_phone(p.get('local_number', ''))
                        if p.get('id'):
                            cursor.execute("UPDATE phones SET local_number = %s, country_id = %s, label_id = %s WHERE id = %s", 
                                         (norm['local_number'], norm['country_id'], p.get('label_id', 1), p['id']))
                        else:
                            cursor.execute("INSERT INTO phones (user_id, country_id, local_number, label_id) VALUES (%s, %s, %s, %s)",
                                         (user_id, norm['country_id'], norm['local_number'], p.get('label_id', 1)))

                # 3. Sync Emails
                if 'emails' in data:
                    incoming_emails = data['emails']
                    keep_ids = [e['id'] for e in incoming_emails if e.get('id')]
                    if keep_ids:
                        cursor.execute("DELETE FROM emails WHERE user_id = %s AND id NOT IN (%s)" % (user_id, ",".join(["%s"]*len(keep_ids))), keep_ids)
                    else:
                        cursor.execute("DELETE FROM emails WHERE user_id = %s", (user_id,))
                    
                    for e in incoming_emails:
                        clean = self.normalizer.normalize_email(e.get('email_address', ''))
                        if e.get('id'):
                            cursor.execute("UPDATE emails SET email_address = %s, label_id = %s WHERE id = %s", 
                                         (clean, e.get('label_id', 1), e['id']))
                        else:
                            cursor.execute("INSERT INTO emails (user_id, email_address, label_id) VALUES (%s, %s, %s)",
                                         (user_id, clean, e.get('label_id', 1)))

                # 4. Sync Addresses
                if 'addresses' in data:
                    incoming_addrs = data['addresses']
                    keep_ids = [a['id'] for a in incoming_addrs if a.get('id')]
                    if keep_ids:
                        cursor.execute("DELETE FROM addresses WHERE user_id = %s AND id NOT IN (%s)" % (user_id, ",".join(["%s"]*len(keep_ids))), keep_ids)
                    else:
                        cursor.execute("DELETE FROM addresses WHERE user_id = %s", (user_id,))
                    
                    for a in incoming_addrs:
                        if a.get('id'):
                            cursor.execute("UPDATE addresses SET address_line1 = %s, city_id = %s, label_id = %s WHERE id = %s", 
                                         (a.get('address_line1'), a.get('city_id'), a.get('label_id', 1), a['id']))
                        else:
                            cursor.execute("INSERT INTO addresses (user_id, address_line1, city_id, label_id) VALUES (%s, %s, %s, %s)",
                                         (user_id, a.get('address_line1'), a.get('city_id'), a.get('label_id', 1)))

                logger.info(f"User {user_id} and relations synced successfully")
                
                # Audit Log
                self._log_audit(None, 'UPDATE', 'USER', user_id, f"Updated user full data")
                
                return True
        except Exception as e:
            logger.error(f"Error syncing user {user_id}: {e}")
            raise

    def get_user_detail_full(self, user_id: int) -> Dict[str, Any]:
        """Deep loads a user with all relations (Modular version)."""
        import dataclasses
        user = self.u_repo.get_by_id(user_id)
        if not user: return None
        
        res = dataclasses.asdict(user)
        # Contact relations
        res['phones'] = self.db.execute_query("SELECT * FROM phones WHERE user_id = %s", (user_id,))
        res['emails'] = self.db.execute_query("SELECT * FROM emails WHERE user_id = %s", (user_id,))
        res['addresses'] = self.db.execute_query("""
            SELECT a.*, c.country_name, s.state_name, ci.city_name 
            FROM addresses a
            LEFT JOIN countries c ON a.country_id = c.id
            LEFT JOIN states s ON a.state_id = s.id
            LEFT JOIN cities ci ON a.city_id = ci.id
            WHERE a.user_id = %s
        """, (user_id,))
        
        # Professional relations
        res['companies'] = self.db.execute_query("""
            SELECT c.id, c.legal_name, c.commercial_name, 
                   pos.position_name, 
                   dept.department_name
            FROM companies c
            JOIN user_companies uc ON uc.company_id = c.id
            LEFT JOIN positions pos ON uc.position_id = pos.id
            LEFT JOIN company_departments dept ON uc.company_department_id = dept.id
            WHERE uc.user_id = %s
        """, (user_id,))
        
        # Ensure dates are stringified for JSON
        for key in ['birthday', 'created_at', 'updated_at']:
            if res.get(key) and hasattr(res[key], 'isoformat'):
                res[key] = res[key].isoformat()
                
        return res

    def update_company_complete(self, company_id: int, data: Dict[str, Any]):
        """Updates company info and its relations in one transaction."""
        try:
            with self.db.transaction() as cursor:
                # 1. Basic Info
                fields = {k: v for k, v in data.items() if k in {f.name for f in Company.__dataclass_fields__.values()} and k not in ['id', 'created_at', 'updated_at']}
                
                if 'rut_nit' in fields and fields['rut_nit']:
                    fields['rut_nit'], dv = self.identity_hygiene.normalize_rut(fields['rut_nit'])
                    if dv is not None:
                        fields['verification_digit'] = dv
                
                if 'domain' in fields:
                    fields['domain'] = self.standardize_domain(fields['domain'])

                if fields:
                    set_clause = ", ".join([f"{k} = %s" for k in fields.keys()])
                    cursor.execute(f"UPDATE companies SET {set_clause} WHERE id = %s", list(fields.values()) + [company_id])

                # 2. Phones
                if 'phones' in data:
                    incoming = data['phones']
                    keep_ids = [p['id'] for p in incoming if p.get('id')]
                    if keep_ids:
                        cursor.execute("DELETE FROM phones WHERE company_id = %s AND id NOT IN (%s)" % (company_id, ",".join(["%s"]*len(keep_ids))), keep_ids)
                    else:
                        cursor.execute("DELETE FROM phones WHERE company_id = %s", (company_id,))
                    
                    for p in incoming:
                        norm = self.normalizer.normalize_phone(p.get('local_number', ''))
                        if p.get('id'):
                            cursor.execute("UPDATE phones SET local_number = %s, country_id = %s, label_id = %s WHERE id = %s", 
                                         (norm['local_number'], norm['country_id'], p.get('label_id', 1), p['id']))
                        else:
                            cursor.execute("INSERT INTO phones (company_id, country_id, local_number, label_id) VALUES (%s, %s, %s, %s)",
                                         (company_id, norm['country_id'], norm['local_number'], p.get('label_id', 1)))

                # 3. Emails
                if 'emails' in data:
                    incoming = data['emails']
                    keep_ids = [e['id'] for e in incoming if e.get('id')]
                    if keep_ids:
                        cursor.execute("DELETE FROM emails WHERE company_id = %s AND id NOT IN (%s)" % (company_id, ",".join(["%s"]*len(keep_ids))), keep_ids)
                    else:
                        cursor.execute("DELETE FROM emails WHERE company_id = %s", (company_id,))
                    
                    for e in incoming:
                        clean = self.normalizer.normalize_email(e.get('email_address', ''))
                        if e.get('id'):
                            cursor.execute("UPDATE emails SET email_address = %s, label_id = %s WHERE id = %s", 
                                         (clean, e.get('label_id', 1), e['id']))
                        else:
                            cursor.execute("INSERT INTO emails (company_id, email_address, label_id) VALUES (%s, %s, %s)",
                                         (company_id, clean, e.get('label_id', 1)))

                return True
        except Exception as e:
            logger.error(f"Error syncing company {company_id}: {e}")
            raise

    def get_company_detail_full(self, company_id: int) -> Dict[str, Any]:
        """Deep loads a company with all relations (Modular version)."""
        import dataclasses
        company = self.c_repo.get_by_id(company_id)
        if not company: return None
        
        res = dataclasses.asdict(company)
        res['phones'] = self.db.execute_query("SELECT * FROM phones WHERE company_id = %s", (company_id,))
        res['emails'] = self.db.execute_query("SELECT * FROM emails WHERE company_id = %s", (company_id,))
        res['addresses'] = self.db.execute_query("""
            SELECT a.*, c.country_name, s.state_name, ci.city_name 
            FROM addresses a
            LEFT JOIN countries c ON a.country_id = c.id
            LEFT JOIN states s ON a.state_id = s.id
            LEFT JOIN cities ci ON a.city_id = ci.id
            WHERE a.company_id = %s
        """, (company_id,))
        
        # Employees list
        res['employees'] = self.db.execute_query("""
            SELECT u.id, u.first_name, u.last_name, 
                   pos.position_name, 
                   dept.department_name
            FROM users u
            JOIN user_companies uc ON uc.user_id = u.id
            LEFT JOIN positions pos ON uc.position_id = pos.id
            LEFT JOIN company_departments dept ON uc.company_department_id = dept.id
            WHERE uc.company_id = %s
        """, (company_id,))

        for key in ['created_at', 'updated_at']:
            if res.get(key) and hasattr(res[key], 'isoformat'):
                res[key] = res[key].isoformat()

        return res
