# Importación de librerías para seguridad (hashing), expresiones regulares y tipos
import logging  # Gestión de logs del sistema
import bcrypt   # Hashing de contraseñas de alta seguridad
import re       # Procesamiento de texto (dominios, correos)
from typing import Optional, List, Dict, Any # Tipado estático

# Importación de componentes del núcleo y servicios auxiliares
from src.core.database_interface import IDatabase
from src.repositories.repository import UserRepository, CompanyRepository, ContactRepository
from src.models.models import User, Company, Address, Phone, Email
from src.services.contact_normalization_service import ContactNormalizationService
from src.services.address_intelligence_service import AddressIntelligenceService
from src.services.identity_hygiene_service import IdentityHygieneService
from src.core.exceptions import ValidationError, XORRuleViolation, DatabaseError, AuthError, DuplicateError
import mysql.connector
from .rut_parsing_service import RUTParsingService

# Instancia del logger para trazas de depuración de lógica de negocio
logger = logging.getLogger(__name__)

class CRMService:
    """
    Servicio Orquestador del CRM.
    Centraliza la lógica de negocio y coordina repositorios y servicios de validación.
    """

    def __init__(self, db: IDatabase, hygiene_service: Optional[IdentityHygieneService] = None, address_service: Optional[AddressIntelligenceService] = None):
        # Inyección de dependencias: base de datos y repositorios
        self.db = db
        self.u_repo = UserRepository(db)
        self.c_repo = CompanyRepository(db)
        self.cont_repo = ContactRepository(db)
        # Servicios especializados para limpieza de datos e inteligencia geográfica
        self.normalizer = ContactNormalizationService(db)
        self.geo_intel = AddressIntelligenceService(db)
        self.identity_hygiene = hygiene_service or IdentityHygieneService()
        self.address_intelligence = address_service or AddressIntelligenceService(db)
        self.rut_parser = RUTParsingService()

    def _serialize_dates(self, data: Any) -> Any:
        """Convierte recursivamente objetos datetime a strings ISO."""
        if isinstance(data, list):
            return [self._serialize_dates(item) for item in data]
        if isinstance(data, dict):
            return {k: self._serialize_dates(v) for k, v in data.items()}
        if hasattr(data, 'isoformat'):
            return data.isoformat()
        return data

    def hash_password(self, password: str) -> str:
        """Genera un hash bcrypt seguro para una contraseña en texto plano."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str, hashed_password: str) -> bool:
        """Verifica si una contraseña coincide con el hash almacenado."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Proceso de autenticación de usuario.
        Retorna los datos serializados del usuario si es exitoso.
        """
        user_data = self.u_repo.find_by_username(username)
        # Verificamos si el usuario existe y su contraseña es válida
        if user_data and user_data.get('password_hash'):
            if self.check_password(password, user_data['password_hash']):
                logger.info(f"Login exitoso para usuario: {username}")
                # Eliminamos el hash de la contraseña de la respuesta por seguridad (aunque el serializador ya lo hace)
                user_data.pop('password_hash', None)
                return user_data
        
        logger.warning(f"Intento de login fallido: {username}")
        raise AuthError("Credenciales inválidas.")

    def register_user_secure(self, user: User, password_plain: str) -> int:
        """Registra un usuario aplicando hashing de contraseña inmediato."""
        user.password_hash = self.hash_password(password_plain)
        return self.u_repo.insert(user)

    def _validate_xor(self, user_id: Optional[int], company_id: Optional[int]):
        """Valida que un contacto pertenezca a un Usuario O a una Empresa, pero no a ambos."""
        if user_id and company_id:
            raise XORRuleViolation("No se puede asignar a un Usuario y una Empresa simultáneamente.")
        if not user_id and not company_id:
            raise XORRuleViolation("Debe asignar el contacto a un Usuario o a una Empresa.")

    def create_user_complete(self, 
                             user: User, 
                             phones: List[Phone] = None, 
                             emails: List[Email] = None, 
                             addresses: List[Address] = None,
                             global_user_id: int = None,
                             tag_ids: List[int] = None) -> int:
        """
        Crea un perfil de usuario completo (con contactos) de forma atómica.
        Utiliza una transacción para asegurar que no queda data huérfana.
        """
        try:
            with self.db.start_transaction() as cursor:
                # 0. Normalización de Identidad (RUT/NIT) y Nombres (Title Case)
                user.first_name = self.normalizer.normalize_name_title(user.first_name)
                user.middle_name = self.normalizer.normalize_name_title(user.middle_name)
                user.last_name = self.normalizer.normalize_name_title(user.last_name)

                if user.rut_nit:
                    user.rut_nit, dv = self.identity_hygiene.normalize_rut(user.rut_nit)
                    if dv is not None:
                        user.verification_digit = dv
                    user.is_natural_person = True 
                else:
                    user.is_natural_person = False 

                # 1. Inserción del registro maestro de Usuario
                sql_u = """
                INSERT INTO users (
                    global_user_id, agent_id, role_id, status_id, prefix, first_name, middle_name, 
                    last_name, suffix, nickname, file_as,
                    phonetic_first_name, phonetic_middle_name, phonetic_last_name,
                    rut_nit, verification_digit, birthday, gender_id, notes,
                    is_natural_person
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params_u = (
                    global_user_id, user.agent_id, user.role_id if user.role_id is not None else 1, user.status_id, user.prefix,
                    user.first_name, user.middle_name, user.last_name,
                    user.suffix, user.nickname, user.file_as,
                    user.phonetic_first_name, user.phonetic_middle_name, user.phonetic_last_name,
                    user.rut_nit, user.verification_digit, user.birthday, user.gender_id, user.notes,
                    1 if user.is_natural_person else 0
                )
                try:
                    cursor.execute(sql_u, params_u)
                except mysql.connector.Error as db_err:
                    if db_err.errno == 1062:
                        raise DuplicateError(f"Ya existe un usuario con el nombre '{user.first_name} {user.last_name}' o el RUT/NIT '{user.rut_nit}'")
                    raise DatabaseError(f"Error de base de datos al insertar usuario: {db_err.msg}")
                    
                u_id = cursor.lastrowid
                
                # 2. Inserción de Teléfonos con normalización proactiva
                if phones:
                    sql_t = "INSERT INTO phones (user_id, company_id, country_id, local_number, label_id) VALUES (%s, NULL, %s, %s, %s)"
                    for t in phones:
                        norm = self.normalizer.normalize_phone(t.local_number)
                        cursor.execute(sql_t, (u_id, norm['country_id'], norm['local_number'], t.label_id))
                
                # 3. Inserción de Correos Electrónicos normalizados
                if emails:
                    sql_c = "INSERT INTO emails (user_id, company_id, email_address, label_id) VALUES (%s, NULL, %s, %s)"
                    for c in emails:
                        if not self.normalizer.is_valid_email(c.email_address):
                            raise ValidationError(f"Estructura de correo inválida: {c.email_address}")
                        # Normalización proactiva a minúsculas
                        c.email_address = self.normalizer.normalize_email(c.email_address)
                        cursor.execute(sql_c, (u_id, c.email_address, c.label_id))
                
                # 4. Inserción de Direcciones Físicas
                if addresses:
                    sql_d = """
                    INSERT INTO addresses (
                        user_id, company_id, country_id, state_id, city_id,
                        address_line1, address_line2, postal_code
                    ) VALUES (%s, NULL, %s, %s, %s, %s, %s, %s)
                    """
                    for d in addresses:
                        cursor.execute(sql_d, (u_id, d.country_id, d.state_id, d.city_id, d.address_line1, d.address_line2, d.postal_code))

                # 5. Inserción de Etiquetas (Tags)
                if tag_ids:
                    sql_tags = "INSERT INTO user_tags (user_id, tag_id) VALUES (%s, %s)"
                    for tid in tag_ids:
                        # Verificar existencia si es necesario, o confiar en foreign key (fallará si no existe)
                        try:
                            cursor.execute(sql_tags, (u_id, tid))
                        except mysql.connector.Error as e:
                            logger.warn(f"Error asignando tag {tid}: {e}")
                            # No fallamos todo el proceso por un tag, pero lo logueamos

                
                logger.info(f"Usuario {u_id} creado satisfactoriamente con sus contactos.")
                
                # Registro en la bitácora de auditoría
                self._log_audit(None, 'CREATE', 'USER', u_id, f"Se creó el usuario ID {u_id} con rol {user.role_id}")
                
                return u_id
                
        except Exception as e:
            logger.error(f"Fallo al crear usuario completo: {e}")
            raise # La transacción se revertirá automáticamente gracias al contextmanager

    def delete_user_complete(self, user_id: int) -> bool:
        """Realiza el borrado suave de un usuario y registra la acción en auditoría."""
        try:
            # Verificación preventiva de existencia
            user_data = self.u_repo.get_by_id(user_id)
            if not user_data:
                raise ValidationError(f"No se encontró el usuario con ID {user_id}")

            # Borrado suave (cambia fecha deleted_at)
            res = self.u_repo.delete(user_id)
            
            # Auditoría
            self._log_audit(None, 'SOFT_DELETE', 'USER', user_id, f"Borrado suave del usuario {user_data.get('first_name')} {user_data.get('last_name')}")
            return res
        except Exception as e:
            logger.error(f"Error borrando usuario {user_id}: {e}")
            raise

    def delete_company_complete(self, company_id: int) -> bool:
        """Realiza el borrado suave de una empresa."""
        try:
            company_data = self.c_repo.get_by_id(company_id)
            if not company_data:
                raise ValidationError(f"No se encontró la empresa con ID {company_id}")

            res = self.c_repo.delete(company_id)
            
            # Auditoría
            self._log_audit(None, 'SOFT_DELETE', 'COMPANY', company_id, f"Borrado suave de la empresa {company_data.get('legal_name')}")
            return res
        except Exception as e:
            logger.error(f"Error borrando empresa {company_id}: {e}")
            raise

    def add_phone(self, phone: Phone):
        """Añade un teléfono validando la exclusividad (XOR)."""
        self._validate_xor(phone.user_id, phone.company_id)
        return self.cont_repo.insert_phone(phone)

    def add_email(self, email: Email):
        """Añade un email validando la exclusividad (XOR)."""
        self._validate_xor(email.user_id, email.company_id)
        return self.cont_repo.insert_email(email)

    def add_address(self, address: Address):
        """Añade una dirección validando la exclusividad (XOR)."""
        self._validate_xor(address.user_id, address.company_id)
        return self.cont_repo.insert_address(address)

    def update_user_basic(self, user_id: int, data: dict):
        """Actualiza datos básicos, protegiendo campos de sistema como 'id' o fechas de creación."""
        data.pop('id', None)
        data.pop('created_at', None)
        data.pop('updated_at', None)
        return self.u_repo.update(user_id, data)

    def update_company_basic(self, company_id: int, data: dict):
        """Actualiza datos de empresa de forma dinámica y con estandarización."""
        data.pop('id', None)
        data.pop('created_at', None)
        data.pop('updated_at', None)
        
        # Filtrar solo campos que existen en el modelo
        from src.models.models import Company # Importar aquí para evitar circular
        fields_to_update = {k: v for k, v in data.items() if k in {f.name for f in Company.__dataclass_fields__.values()}}
        
        if 'domain' in fields_to_update:
            fields_to_update['domain'] = self.standardize_domain(fields_to_update['domain'])
            
        if not fields_to_update:
            return False

        res = self.c_repo.update(company_id, fields_to_update)
        self._log_audit(None, 'UPDATE', 'COMPANY', company_id, f"Actualización dinámica: {list(fields_to_update.keys())}")
        return res


    def update_phone(self, phone_id: int, data: dict):
        """Actualización simple de campos de teléfono."""
        data.pop('id', None)
        data.pop('created_at', None)
        return self.cont_repo.update_phone(phone_id, data)

    def update_email(self, email_id: int, data: dict):
        """Actualización simple de campos de email."""
        data.pop('id', None)
        data.pop('created_at', None)
        return self.cont_repo.update_email(email_id, data)

    def update_address(self, address_id: int, data: dict):
        """Actualización simple de campos de dirección."""
        data.pop('id', None)
        data.pop('created_at', None)
        return self.cont_repo.update_address(address_id, data)

    @staticmethod
    def standardize_domain(domain: Optional[str]) -> Optional[str]:
        """Limpia dominios web: quita http/s, www, slashes finales y pasa a minúsculas."""
        if not domain or len(domain.strip()) < 3:
            return None
        clean = domain.lower().strip()
        clean = re.sub(r'^https?://', '', clean) # Elimina protocolo
        clean = re.sub(r'^www\.', '', clean)     # Elimina prefijo www
        clean = clean.rstrip('/')                # Elimina barra final
        
        if len(clean) < 3:
            return None
        return clean
    def create_company_complete(self, 
                                company: Company, 
                                phones: List[Phone] = None, 
                                emails: List[Email] = None, 
                                addresses: List[Address] = None,
                                tag_ids: List[int] = None) -> int:
        """
        Crea una empresa con toda su información de contacto en una sola transacción atómica.
        """
        try:
            # Normalización a NULL para evitar violaciones de constraints de longitud mínima
            company.legal_name = self.normalizer.normalize_company_name(company.legal_name)
            company.commercial_name = self.normalizer.normalize_company_name(company.commercial_name) if company.commercial_name and company.commercial_name.strip() else None
            company.description = company.description.strip() if company.description and company.description.strip() else None

            # Estandarizamos el dominio antes de guardar
            company.domain = self.standardize_domain(company.domain)
                
            with self.db.start_transaction() as cursor:
                # 0. Normalización de RUT/NIT empresarial (si no viene, queda cadena vacía para NOT NULL)
                company.rut_nit = company.rut_nit or ''
                company.rut_nit, dv = self.identity_hygiene.normalize_rut(company.rut_nit)
                if dv is not None:
                    company.verification_digit = dv

                # 1. Inserción del registro de Empresa
                sql_c = """
                INSERT INTO companies (
                    legal_name, commercial_name, rut_nit, verification_digit, 
                    status_id, domain, description, revenue, agent_id, company_department_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                try:
                    cursor.execute(sql_c, (
                        company.legal_name, company.commercial_name, company.rut_nit, 
                        company.verification_digit, company.status_id, company.domain,
                        company.description, company.revenue, company.agent_id, getattr(company, 'company_department_id', None)
                    ))
                except mysql.connector.Error as db_err:
                    if db_err.errno == 1062: # Duplicate entry
                        raise DuplicateError(f"Ya existe una empresa registrada con el RUT/NIT: {company.rut_nit}")
                    raise DatabaseError(f"Error de base de datos al insertar empresa: {db_err.msg}")
                
                c_id = cursor.lastrowid
                
                # 2. Inserción de Teléfonos (Nulos los user_id, pues es empresa)
                if phones:
                    sql_p = "INSERT INTO phones (user_id, company_id, country_id, local_number, label_id) VALUES (NULL, %s, %s, %s, %s)"
                    for p in phones:
                        norm = self.normalizer.normalize_phone(p.local_number)
                        cursor.execute(sql_p, (c_id, norm['country_id'], norm['local_number'], p.label_id))
                
                # 3. Inserción de Correos (Nulos los user_id)
                if emails:
                    sql_e = "INSERT INTO emails (user_id, company_id, email_address, label_id) VALUES (NULL, %s, %s, %s)"
                    for e in emails:
                        if not self.normalizer.is_valid_email(e.email_address):
                            raise ValidationError(f"Estructura de correo inválida: {e.email_address}")
                        # Normalización proactiva a minúsculas
                        e.email_address = self.normalizer.normalize_email(e.email_address)
                        cursor.execute(sql_e, (c_id, e.email_address, e.label_id))
                
                # 4. Inserción de Direcciones
                if addresses:
                    sql_a = """
                    INSERT INTO addresses (
                        user_id, company_id, country_id, state_id, city_id,
                        address_line1, address_line2, postal_code
                    ) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)
                    """
                    for a in addresses:
                        cursor.execute(sql_a, (c_id, a.country_id, a.state_id, a.city_id, a.address_line1, a.address_line2, a.postal_code))
                
                # 5. Inserción de Etiquetas (Tags)
                if tag_ids:
                    sql_tags = "INSERT INTO company_tags (company_id, tag_id) VALUES (%s, %s)"
                    for tid in tag_ids:
                        try:
                            cursor.execute(sql_tags, (c_id, tid))
                        except Exception as e:
                            logger.warn(f"Error asignando tag {tid} a la empresa: {e}")
                            # No fallamos todo el proceso por un tag, pero lo logueamos
                
                # Auditoría del evento
                self._log_audit(None, 'CREATE', 'COMPANY', c_id, f"Se creó la empresa {company.legal_name}")
                
                return c_id
        except Exception as e:
            logger.error(f"Error creando empresa completa: {e}")
            raise

    def link_user_to_company(self, user_id: int, company_id: int, position_id: int = 1, department_id: int = 1):
        """Asocia un usuario a una empresa con un cargo y departamento específico."""
        sql = """
        INSERT INTO user_companies (user_id, company_id, position_id, company_department_id)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            position_id = VALUES(position_id), 
            company_department_id = VALUES(company_department_id)
        """
        return self.db.execute_command(sql, (user_id, company_id, position_id, department_id), perform_commit=True, fetch_results=False)

    def sync_user_companies(self, user_id: int, links: List[Dict[str, Any]]):
        """Sincroniza los vínculos profesionales de un usuario (Delete-Or-Update)."""
        with self.db.transaction() as cursor:
            # Eliminar vínculos que ya no están en la lista
            keep_company_ids = [l['company_id'] for l in links if l.get('company_id')]
            if keep_company_ids:
                sql_del = "DELETE FROM user_companies WHERE user_id = %s AND company_id NOT IN (%s)" % (user_id, ",".join(["%s"]*len(keep_company_ids)))
                cursor.execute(sql_del, keep_company_ids)
            else:
                cursor.execute("DELETE FROM user_companies WHERE user_id = %s", (user_id,))
            
            # Insertar/Actualizar
            sql_ins = """
            INSERT INTO user_companies (user_id, company_id, position_id, company_department_id)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE position_id = VALUES(position_id), company_department_id = VALUES(company_department_id)
            """
            for l in links:
                cursor.execute(sql_ins, (user_id, l['company_id'], l.get('position_id', 1), l.get('company_department_id', 1)))

    def unlink_user_from_company(self, user_id: int, company_id: int):
        """Elimina el vínculo profesional entre un usuario y una empresa."""
        sql = "DELETE FROM user_companies WHERE user_id = %s AND company_id = %s"
        res = self.db.execute_command(sql, (user_id, company_id), perform_commit=True, fetch_results=False)
        
        # Auditoría del desvinculado
        self._log_audit(None, 'UNLINK', 'COMPANY', company_id, f"Se desvinculó al usuario {user_id}")
        return res


    def delete_user_relation_type(self, type_id: int):
        """Elimina un tipo de relación si no está en uso."""
        return self.db.execute_command("DELETE FROM user_relation_types WHERE id = %s", (type_id,), perform_commit=True, fetch_results=False)

    def get_tags(self) -> List[Dict[str, Any]]:
        """Obtiene todas las etiquetas (tags) de colores."""
        return self.db.execute_command("SELECT id, name, color FROM tags")

    def add_tag(self, name: str, color: str = '#808080'):
        """Crea una nueva etiqueta visual."""
        sql = "INSERT INTO tags (name, color) VALUES (%s, %s)"
        return self.db.execute_command(sql, (name, color), perform_commit=True, fetch_results=False)

    # --- Gestión Genérica de Lookups (Maestros) ---

    def get_lookup_data(self, table: str) -> List[Dict[str, Any]]:
        """Método genérico para consultar cualquier tabla de referencia (whitelist)."""
        allowed = ['cargos', 'departamentos_empresa', 'status_types', 'genders', 'tags', 'user_relation_types', 'company_relation_types']
        if table not in allowed: return []
        return self.db.execute_command(f"SELECT * FROM {table}")

    def add_lookup_item(self, table: str, data: Dict[str, Any]):
        """Método genérico para insertar en tablas maestro."""
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({fields}) VALUES ({placeholders})"
        return self.db.execute_command(sql, tuple(data.values()), perform_commit=True, fetch_results=False)

    def delete_lookup_item(self, table: str, item_id: int):
        """Borrado físico de registros maestro."""
        return self.db.execute_command(f"DELETE FROM {table} WHERE id = %s", (item_id,), perform_commit=True, fetch_results=False)

    def link_companies(self, source_id: int, target_id: int, relation_type_id: int, notes: str = None):
        """Vincula dos empresas (Holding, Alianza, etc)."""
        sql = """
        INSERT INTO company_relations (source_company_id, target_company_id, relation_type_id, notes)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE relation_type_id = VALUES(relation_type_id), notes = VALUES(notes)
        """
        return self.db.execute_command(sql, (source_id, target_id, relation_type_id, notes), perform_commit=True, fetch_results=False)

    def link_users(self, from_id: int, to_id: int, relation_type_id: int, custom_label: str = None):
        """Vincula dos usuarios con reciprocidad."""
        sql = """
        INSERT INTO user_user_relations (from_user_id, to_user_id, relation_type_id, custom_label)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE relation_type_id = VALUES(relation_type_id), custom_label = VALUES(custom_label)
        """
        return self.db.execute_command(sql, (from_id, to_id, relation_type_id, custom_label), perform_commit=True, fetch_results=False)

    def unlink_companies(self, source_id: int, target_id: int):
        """Elimina el vínculo entre dos empresas."""
        sql = "DELETE FROM company_relations WHERE source_company_id = %s AND target_company_id = %s"
        return self.db.execute_command(sql, (source_id, target_id), perform_commit=True, fetch_results=False)

    def unlink_users(self, from_id: int, to_id: int):
        """Elimina el vínculo entre dos usuarios."""
        sql = "DELETE FROM user_user_relations WHERE (from_user_id = %s AND to_user_id = %s) OR (from_user_id = %s AND to_user_id = %s)"
        return self.db.execute_command(sql, (from_id, to_id, to_id, from_id), perform_commit=True, fetch_results=False)

    def get_company_contacts(self, company_id: int) -> List[Dict[str, Any]]:
        """Lista todos los usuarios (empleados/contactos) vinculados a una empresa."""
        sql = """
        SELECT u.* FROM users u
        JOIN user_companies uc ON uc.user_id = u.id
        WHERE uc.company_id = %s
        """
        # Obtenemos los datos y los serializamos para JSON
        res = self.db.execute_command(sql, (company_id,))
        from src.core.serializers import UserSerializer
        return [UserSerializer.serialize(User.from_dict(row)) for row in res]

    def list_natural_persons(self) -> List[Dict[str, Any]]:
        """Lista usuarios marcados como personas naturales (B2C)."""
        sql = "SELECT * FROM users WHERE is_natural_person = TRUE"
        res = self.db.execute_command(sql)
        from src.core.serializers import UserSerializer
        return [UserSerializer.serialize(User.from_dict(row)) for row in res]

    def get_user_relation_types(self) -> List[Dict[str, Any]]:
        """Lista los tipos de relación entre personas (Cónyuge, Socio, etc)."""
        return self.db.execute_command("SELECT id, name FROM user_relation_types ORDER BY name")

    # --- Gestión Geográfica (Fase 13) ---

    def list_countries(self) -> List[Dict[str, Any]]:
        return self.db.execute_query("SELECT id, country_name, phone_code FROM countries ORDER BY country_name")

    def add_country(self, name: str, phone_code: str = None, area: float = 0, population: int = 0) -> int:
        """Añade un país e informa al normalizador para recargar prefijos."""
        sql = "INSERT INTO countries (country_name, phone_code, area_km2, population) VALUES (%s, %s, %s, %s)"
        c_id = self.db.execute_command(sql, (name, phone_code, area, population), perform_commit=True, fetch_results=False)
        if hasattr(self, 'normalizer'):
            self.normalizer.reload_codes()
        return c_id

    def list_states(self, country_id: int) -> List[Dict[str, Any]]:
        """Lista departamentos/estados por país."""
        return self.db.execute_command("SELECT id, state_name FROM states WHERE country_id = %s ORDER BY state_name", (country_id,))

    def add_state(self, name: str, country_id: int, area: float = 0, population: int = 0) -> int:
        sql = "INSERT INTO states (state_name, country_id, area_km2, population) VALUES (%s, %s, %s, %s)"
        return self.db.execute_command(sql, (name, country_id, area, population), perform_commit=True, fetch_results=False)

    def _log_audit(self, actor_id: Optional[int], action_type: str, entity_type: str, entity_id: int, details: str = None):
        """Insertar registros en la bitácora de auditoría sin commit (debe estar dentro de una transacción)."""
        try:
            self.db.execute_command(
                "INSERT INTO audit_logs (actor_id, action_type, entity_type, entity_id, details) VALUES (%s, %s, %s, %s, %s)",
                (actor_id, action_type, entity_type, entity_id, details),
                fetch_results=False,
                perform_commit=False
            )
        except Exception as e:
            logger.error(f"Fallo al registrar auditoría: {e}")

    def list_cities(self, state_id: int) -> List[Dict[str, Any]]:
        """Lista municipios/ciudades por departamento."""
        return self.db.execute_command("SELECT id, city_name FROM cities WHERE state_id = %s ORDER BY city_name", (state_id,))

    def add_city(self, name: str, state_id: int, area: float = 0, population: int = 0) -> int:
        sql = "INSERT INTO cities (city_name, state_id, area_km2, population) VALUES (%s, %s, %s, %s)"
        return self.db.execute_command(sql, (name, state_id, area, population), perform_commit=True, fetch_results=False)

    # --- Vistas de Resumen para Frontend (Fase 16) ---

    def get_users_summary(self) -> List[Dict[str, Any]]:
        """Obtiene un resumen de usuarios con datos de contacto primarios para la tabla del frontend."""
        sql = """
        SELECT 
            u.id, u.first_name, u.last_name, 
            CONCAT(u.rut_nit, IF(u.verification_digit IS NOT NULL, CONCAT('-', u.verification_digit), '')) as rut_nit,
            (SELECT email_address FROM emails WHERE user_id = u.id LIMIT 1) as email,
            (SELECT local_number FROM phones WHERE user_id = u.id LIMIT 1) as phone,
            (SELECT GROUP_CONCAT(c.legal_name SEPARATOR ', ') 
             FROM companies c 
             JOIN user_companies uc ON uc.company_id = c.id 
             WHERE uc.user_id = u.id) as company,
            (SELECT GROUP_CONCAT(t.name SEPARATOR ', ') 
             FROM tags t 
             LEFT JOIN user_tags ut ON ut.tag_id = t.id 
             WHERE ut.user_id = u.id) as labels
        FROM users u
        WHERE u.deleted_at IS NULL
        """
        return self.db.execute_command(sql)

    def get_companies_summary(self) -> List[Dict[str, Any]]:
        """Obtiene resumen de empresas para la tabla del frontend."""
        sql = """
        SELECT 
            c.id, c.legal_name, c.commercial_name, 
            CONCAT(c.rut_nit, IF(c.verification_digit IS NOT NULL, CONCAT('-', c.verification_digit), '')) as rut_nit,
            c.domain, c.revenue, c.employee_count as total_employees,
            (SELECT COUNT(*) FROM user_companies WHERE company_id = c.id) as linked_contacts_count,
            (SELECT email_address FROM emails WHERE company_id = c.id LIMIT 1) as email,
            (SELECT local_number FROM phones WHERE company_id = c.id LIMIT 1) as phone,
            (SELECT GROUP_CONCAT(t.name SEPARATOR ', ') 
             FROM tags t 
             LEFT JOIN company_tags ct ON ct.tag_id = t.id 
             WHERE ct.company_id = c.id) as labels
        FROM companies c
        WHERE c.deleted_at IS NULL
        """
        return self.db.execute_command(sql)

    # Removed get_user_complete and get_company_complete as they are redundant with get_user_detail_full and get_company_detail_full

    def update_user_complete(self, user_id: int, data: Dict[str, Any]) -> bool:
        """
        Sincroniza el perfil completo de un usuario y sus múltiples contactos en un bloque atómico.
        """
        try:
            with self.db.start_transaction() as cursor:
                # 1. Actualización de datos básicos (si existen en el payload)
                # Normalización de nombres (Title Case)
                from src.models.models import User
                for k in ['first_name', 'middle_name', 'last_name']:
                    if k in data and data[k]:
                        data[k] = self.normalizer.normalize_name_title(data[k])

                fields_to_update = {k: v for k, v in data.items() if k in {f.name for f in User.__dataclass_fields__.values()} and k not in ['id', 'created_at', 'updated_at']}
                
                # Manejo de credenciales si vienen en el payload (Roles Admin/Agente)
                if 'agent_id' in data:
                    fields_to_update['agent_id'] = data['agent_id']
                
                # Normalización antes de actualizar
                if 'rut_nit' in fields_to_update:
                    if fields_to_update['rut_nit']:
                        fields_to_update['rut_nit'], dv = self.identity_hygiene.normalize_rut(fields_to_update['rut_nit'])
                        if dv is not None:
                            fields_to_update['verification_digit'] = dv
                        fields_to_update['is_natural_person'] = True
                    else:
                        fields_to_update['is_natural_person'] = False
                        fields_to_update['rut_nit'] = None
                        fields_to_update['verification_digit'] = None

                if fields_to_update:
                    set_clause = ", ".join([f"{k} = %s" for k in fields_to_update.keys()])
                    sql_u = f"UPDATE users SET {set_clause} WHERE id = %s"
                    cursor.execute(sql_u, list(fields_to_update.values()) + [user_id])

                # 2. Sincronización de Teléfonos (Delete-Or-Update logic)
                if 'phones' in data:
                    incoming_phones = data['phones']
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

                # 3. Sincronización de Correos
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

                # 4. Sincronización de Direcciones
                if 'addresses' in data:
                    incoming_addresses = data['addresses']
                    keep_ids = [a['id'] for a in incoming_addresses if a.get('id')]
                    if keep_ids:
                        cursor.execute("DELETE FROM addresses WHERE user_id = %s AND id NOT IN (%s)" % (user_id, ",".join(["%s"]*len(keep_ids))), keep_ids)
                    else:
                        cursor.execute("DELETE FROM addresses WHERE user_id = %s", (user_id,))
                    
                    for a in incoming_addresses:
                        if a.get('id'):
                            cursor.execute("""
                                UPDATE addresses SET 
                                country_id = %s, state_id = %s, city_id = %s, 
                                address_line1 = %s, address_line2 = %s, postal_code = %s 
                                WHERE id = %s
                            """, (a.get('country_id'), a.get('state_id'), a.get('city_id'), 
                                 a.get('address_line1'), a.get('address_line2'), a.get('postal_code'), a['id']))
                        else:
                            cursor.execute("""
                                INSERT INTO addresses (user_id, country_id, state_id, city_id, address_line1, address_line2, postal_code) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (user_id, a.get('country_id'), a.get('state_id'), a.get('city_id'), 
                                 a.get('address_line1'), a.get('address_line2'), a.get('postal_code')))

                # 5. Sincronización de Etiquetas del Usuario
                if 'tags' in data:
                    cursor.execute("DELETE FROM user_tags WHERE user_id = %s", (user_id,))
                    for t in data['tags']:
                        t_id = t.get('id')
                        # Si es una etiqueta nueva (ID de JS timestamp)
                        if not t_id or t_id > 2000000000:
                            cursor.execute("SELECT id FROM tags WHERE name = %s", (t['name'],))
                            row = cursor.fetchone()
                            if row: t_id = row['id']
                            else:
                                cursor.execute("INSERT INTO tags (name, color) VALUES (%s, %s)", (t['name'], t.get('color', '#e0e0e0')))
                                t_id = cursor.lastrowid
                        cursor.execute("INSERT INTO user_tags (user_id, tag_id) VALUES (%s, %s)", (user_id, t_id))

                # Auditoría de actualización masiva
                self._log_audit(None, 'UPDATE', 'USER', user_id, f"Actualización profunda de perfil y etiquetas")
                
                return True
        except Exception as e:
            logger.error(f"Error sincronizando usuario {user_id}: {e}")
            raise

    def get_user_detail_full(self, user_id: int) -> Dict[str, Any]:
        """Carga profunda de un usuario con todas sus relaciones vinculadas."""
        user_data = self.u_repo.get_by_id(user_id)
        if not user_data: return None
        
        # Cargamos relaciones adicionales directamente mediante consultas
        user_data['phones'] = self.db.execute_command("SELECT * FROM phones WHERE user_id = %s", (user_id,))
        user_data['emails'] = self.db.execute_command("SELECT * FROM emails WHERE user_id = %s", (user_id,))
        user_data['addresses'] = self.db.execute_command("""
            SELECT a.*, c.country_name, s.state_name, ci.city_name 
            FROM addresses a
            LEFT JOIN countries c ON a.country_id = c.id
            LEFT JOIN states s ON a.state_id = s.id
            LEFT JOIN cities ci ON a.city_id = ci.id
            WHERE a.user_id = %s
        """, (user_id,))
        
        user_data['companies'] = self.db.execute_command("""
            SELECT c.id, c.legal_name, c.commercial_name, pos.position_name, dept.department_name
            FROM companies c
            JOIN user_companies uc ON uc.company_id = c.id
            LEFT JOIN positions pos ON uc.position_id = pos.id
            LEFT JOIN company_departments dept ON uc.company_department_id = dept.id
            WHERE uc.user_id = %s
        """, (user_id,))
        
        # Cargar etiquetas del usuario
        user_data['tags'] = self.db.execute_command("""
            SELECT t.id, t.name, t.color 
            FROM tags t
            JOIN user_tags ut ON ut.tag_id = t.id
            WHERE ut.user_id = %s
        """, (user_id,))

        # Cargar relaciones Personales/Profesionales entre Usuarios
        user_data['relationships'] = self.db.execute_command("""
            SELECT 
                r.to_user_id as related_user_id,
                u.first_name, u.last_name,
                rt.name as relation_type,
                r.custom_label,
                r.relation_type_id
            FROM user_user_relations r
            JOIN users u ON r.to_user_id = u.id
            JOIN user_relation_types rt ON r.relation_type_id = rt.id
            WHERE r.from_user_id = %s
            UNION
            SELECT 
                r.from_user_id as related_user_id,
                u.first_name, u.last_name,
                t2.name as relation_type,
                r.custom_label,
                t2.id as relation_type_id
            FROM user_user_relations r
            JOIN users u ON r.from_user_id = u.id
            JOIN user_relation_types t1 ON r.relation_type_id = t1.id
            LEFT JOIN user_relation_types t2 ON t1.inverse_type_id = t2.id
            WHERE r.to_user_id = %s
        """, (user_id, user_id))
        
        logger.debug(f"Deep detail for user {user_id} loaded successfully")
        
        return self._serialize_dates(user_data)

    def get_company_detail_full(self, company_id: int) -> Dict[str, Any]:
        """Carga profunda de una empresa y sus empleados/contactos vinculados."""
        company_data = self.c_repo.get_by_id(company_id)
        if not company_data: return None
        
        company_data['phones'] = self.db.execute_command("SELECT * FROM phones WHERE company_id = %s", (company_id,))
        company_data['emails'] = self.db.execute_command("SELECT * FROM emails WHERE company_id = %s", (company_id,))
        company_data['addresses'] = self.db.execute_command("""
            SELECT a.*, c.country_name, s.state_name, ci.city_name 
            FROM addresses a
            LEFT JOIN countries c ON a.country_id = c.id
            LEFT JOIN states s ON a.state_id = s.id
            LEFT JOIN cities ci ON a.city_id = ci.id
            WHERE a.company_id = %s
        """, (company_id,))
        
        # Listado de empleados vinculados con su cargo y contacto primario
        company_data['employees'] = self.db.execute_command("""
            SELECT u.id, u.first_name, u.last_name, pos.position_name, dept.department_name,
                   (SELECT email_address FROM emails WHERE user_id = u.id LIMIT 1) as email,
                   (SELECT local_number FROM phones WHERE user_id = u.id LIMIT 1) as phone
            FROM users u
            JOIN user_companies uc ON uc.user_id = u.id
            LEFT JOIN positions pos ON uc.position_id = pos.id
            LEFT JOIN company_departments dept ON uc.company_department_id = dept.id
            WHERE uc.company_id = %s
        """, (company_id,))

        # Listado de Relaciones Corporativas (B2B)
        # Traemos tanto las que 'parent_company_id' es la empresa actual como 'child_company_id'
        query_rels = """
            SELECT 
                cr.child_company_id as target_company_id,
                c.legal_name,
                crt.name as relation_type,
                cr.relation_type_id,
                0 as is_inverse
            FROM company_associations cr
            JOIN companies c ON c.id = cr.child_company_id
            JOIN company_relation_types crt ON cr.relation_type_id = crt.id
            WHERE cr.parent_company_id = %s
            UNION
            SELECT 
                cr.parent_company_id as target_company_id,
                c.legal_name,
                t2.name as relation_type,
                t2.id as relation_type_id,
                1 as is_inverse
            FROM company_associations cr
            JOIN companies c ON c.id = cr.parent_company_id
            JOIN company_relation_types t1 ON cr.relation_type_id = t1.id
            LEFT JOIN company_relation_types t2 ON t1.inverse_type_id = t2.id
            WHERE cr.child_company_id = %s
        """
        company_data['relationships'] = self.db.execute_command(query_rels, (company_id, company_id))
        
        return self._serialize_dates(company_data)


    def update_company_complete(self, company_id: int, data: Dict[str, Any]) -> bool:
        """
        Sincroniza el perfil completo de una empresa y sus múltiples contactos.
        """
        try:
            with self.db.start_transaction() as cursor:
                # 1. Actualización de datos básicos
                from src.models.models import Company
                # 1. Actualización de datos básicos de la empresa y normalización a NULL
                for k in ['legal_name', 'commercial_name']:
                    if k in data and data[k]:
                        data[k] = self.normalizer.normalize_company_name(data[k])
                    elif k == 'commercial_name':
                        data[k] = None # Normalizar vacío a NULL

                if 'description' in data and not (data['description'] and data['description'].strip()):
                    data[k] = None # Normalizar descripción vacía a NULL

                fields_to_update = {k: v for k, v in data.items() if k in {f.name for f in Company.__dataclass_fields__.values()} and k not in ['id', 'created_at', 'updated_at']}
                
                if 'domain' in fields_to_update:
                    fields_to_update['domain'] = self.standardize_domain(fields_to_update['domain'])

                if 'rut_nit' in fields_to_update and fields_to_update['rut_nit']:
                    fields_to_update['rut_nit'], dv = self.identity_hygiene.normalize_rut(fields_to_update['rut_nit'])
                    if dv is not None:
                        fields_to_update['verification_digit'] = dv

                if fields_to_update:
                    set_clause = ", ".join([f"{k} = %s" for k in fields_to_update.keys()])
                    sql_c = f"UPDATE companies SET {set_clause} WHERE id = %s"
                    cursor.execute(sql_c, list(fields_to_update.values()) + [company_id])

                # 2. Sincronización de Teléfonos
                if 'phones' in data:
                    incoming_phones = data['phones']
                    keep_ids = [p['id'] for p in incoming_phones if p.get('id')]
                    if keep_ids:
                        cursor.execute("DELETE FROM phones WHERE company_id = %s AND id NOT IN (%s)" % (company_id, ",".join(["%s"]*len(keep_ids))), keep_ids)
                    else:
                        cursor.execute("DELETE FROM phones WHERE company_id = %s", (company_id,))
                    
                    for p in incoming_phones:
                        norm = self.normalizer.normalize_phone(p.get('local_number', ''))
                        if p.get('id'):
                            cursor.execute("UPDATE phones SET local_number = %s, country_id = %s, label_id = %s WHERE id = %s", 
                                         (norm['local_number'], norm['country_id'], p.get('label_id', 1), p['id']))
                        else:
                            cursor.execute("INSERT INTO phones (company_id, country_id, local_number, label_id) VALUES (%s, %s, %s, %s)",
                                         (company_id, norm['country_id'], norm['local_number'], p.get('label_id', 1)))

                # 3. Sincronización de Correos
                if 'emails' in data:
                    incoming_emails = data['emails']
                    keep_ids = [e['id'] for e in incoming_emails if e.get('id')]
                    if keep_ids:
                        cursor.execute("DELETE FROM emails WHERE company_id = %s AND id NOT IN (%s)" % (company_id, ",".join(["%s"]*len(keep_ids))), keep_ids)
                    else:
                        cursor.execute("DELETE FROM emails WHERE company_id = %s", (company_id,))
                    
                    for e in incoming_emails:
                        clean = self.normalizer.normalize_email(e.get('email_address', ''))
                        if e.get('id'):
                            cursor.execute("UPDATE emails SET email_address = %s, label_id = %s WHERE id = %s", 
                                         (clean, e.get('label_id', 1), e['id']))
                        else:
                            cursor.execute("INSERT INTO emails (company_id, email_address, label_id) VALUES (%s, %s, %s)",
                                         (company_id, clean, e.get('label_id', 1)))

                # 4. Sincronización de Direcciones
                if 'addresses' in data:
                    incoming_addresses = data['addresses']
                    keep_ids = [a['id'] for a in incoming_addresses if a.get('id')]
                    if keep_ids:
                        cursor.execute("DELETE FROM addresses WHERE company_id = %s AND id NOT IN (%s)" % (company_id, ",".join(["%s"]*len(keep_ids))), keep_ids)
                    else:
                        cursor.execute("DELETE FROM addresses WHERE company_id = %s", (company_id,))
                    
                    for a in incoming_addresses:
                        if a.get('id'):
                            cursor.execute("""
                                UPDATE addresses SET 
                                country_id = %s, state_id = %s, city_id = %s, 
                                address_line1 = %s, address_line2 = %s, postal_code = %s 
                                WHERE id = %s
                            """, (a.get('country_id'), a.get('state_id'), a.get('city_id'), 
                                 a.get('address_line1'), a.get('address_line2'), a.get('postal_code'), a['id']))
                        else:
                            cursor.execute("""
                                INSERT INTO addresses (company_id, country_id, state_id, city_id, address_line1, address_line2, postal_code) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (company_id, a.get('country_id'), a.get('state_id'), a.get('city_id'), 
                                 a.get('address_line1'), a.get('address_line2'), a.get('postal_code')))

                # 5. Sincronización de Etiquetas (Tags)
                if 'tags' in data:
                    incoming_tag_ids = [t['id'] for t in data['tags'] if isinstance(t, dict) and t.get('id')]
                    # Remove all tags not in the new list
                    if incoming_tag_ids:
                        placeholders = ','.join(['%s'] * len(incoming_tag_ids))
                        cursor.execute(
                            f"DELETE FROM company_tags WHERE company_id = %s AND tag_id NOT IN ({placeholders})",
                            [company_id] + incoming_tag_ids
                        )
                    else:
                        cursor.execute("DELETE FROM company_tags WHERE company_id = %s", (company_id,))
                    # Insert new tags (ignore duplicates)
                    for tid in incoming_tag_ids:
                        cursor.execute(
                            "INSERT IGNORE INTO company_tags (company_id, tag_id) VALUES (%s, %s)",
                            (company_id, tid)
                        )

            self._log_audit(None, 'UPDATE', 'COMPANY', company_id, f"Sincronización completa de empresa y contactos")
            return True
        except Exception as e:
            logger.error(f"Error sincronizando empresa {company_id}: {e}")
            raise

    # Lookups para la CLI
    # --- MÉTODOS DE BÚSQUEDA (LOOKUPS) PARA CLI Y FRONTEND ---

    def create_tag(self, name: str, color: str = '#808080') -> int:
        """Crea una nueva etiqueta global."""
        try:
            sql = "INSERT INTO tags (name, color) VALUES (%s, %s)"
            try:
                tag_id = self.db.execute_command(sql, (name, color), perform_commit=True)
                return tag_id
            except mysql.connector.IntegrityError:
                res = self.db.fetch_one("SELECT id FROM tags WHERE name = %s", (name,))
                if res:
                    return res['id']
                raise
        except Exception as e:
            logger.error(f"Error creando tag {name}: {e}")
            raise

    def get_users(self) -> List[Dict[str, Any]]:
        """Lookup para usuarios (id y nombre completo)."""
        return self.db.execute_query("SELECT id, CONCAT(first_name, ' ', last_name) AS name FROM users WHERE deleted_at IS NULL")

    def get_companies(self) -> List[Dict[str, Any]]:
        return self.db.execute_query("SELECT id, legal_name AS name FROM companies WHERE status_id = 1")

    def get_countries(self) -> List[Dict[str, Any]]:
        return self.db.execute_query("SELECT id, country_name, phone_code FROM countries ORDER BY country_name")



    def get_states(self, country_id: int) -> List[Dict[str, Any]]:
        return self.db.execute_query("SELECT id, state_name FROM states WHERE country_id = %s ORDER BY state_name", (country_id,))

    def get_cities(self, state_id: int) -> List[Dict[str, Any]]:
        return self.db.execute_query("SELECT id, city_name FROM cities WHERE state_id = %s ORDER BY city_name", (state_id,))

    def get_genders(self) -> List[Dict[str, Any]]:
        # Return raw DB column 'name'
        return self.db.execute_query("SELECT id, name FROM genders ORDER BY id")

    def get_roles(self) -> List[Dict[str, Any]]:
        # Return raw DB column 'role_name'
        return self.db.execute_query("SELECT id, role_name FROM roles ORDER BY id")

    def get_statuses(self) -> List[Dict[str, Any]]:
        # Return raw DB column 'status_name'
        return self.db.execute_query("SELECT id, status_name FROM statuses ORDER BY id")

    def get_labels(self) -> List[Dict[str, Any]]:
        # Fix: la tabla labels usa 'label_name', no 'first_name'
        return self.db.execute_query("SELECT id, label_name FROM labels ORDER BY id")

    def get_positions(self) -> List[Dict[str, Any]]:
        return self.db.execute_query("SELECT id, position_name FROM positions ORDER BY position_name")

    def get_departments(self) -> List[Dict[str, Any]]:
        return self.db.execute_query("SELECT id, department_name FROM company_departments ORDER BY department_name")

    def get_company_relation_types(self) -> List[Dict[str, Any]]:
        query = """
        SELECT t1.id, t1.name, t1.inverse_type_id, t2.name as inverse_name 
        FROM company_relation_types t1
        LEFT JOIN company_relation_types t2 ON t1.inverse_type_id = t2.id
        """
        return self.db.execute_query(query)

    def get_user_relation_types(self) -> List[Dict[str, Any]]:
        query = """
        SELECT t1.id, t1.name, t1.inverse_type_id, t2.name as inverse_name 
        FROM user_relation_types t1
        LEFT JOIN user_relation_types t2 ON t1.inverse_type_id = t2.id
        """
        return self.db.execute_query(query)

    def get_tags(self) -> List[Dict[str, Any]]:
        return self.db.execute_query("SELECT id, name, color FROM tags ORDER BY name")

    def get_agents(self) -> List[Dict[str, Any]]:
        """Retorna usuarios que pueden ser asignados como responsables (Admin, Agente, Vendedor)."""
        return self.db.execute_query("""
            SELECT id, CONCAT(first_name, ' ', last_name) as name 
            FROM users 
            WHERE role_id IN (1, 2, 3) AND deleted_at IS NULL
            ORDER BY first_name
        """)

    def unlink_user_from_company(self, user_id: int, company_id: int) -> bool:
        """Elimina la relación profesional entre un usuario y una empresa."""
        try:
            # Check if exists
            exists = self.db.fetch_one("SELECT 1 FROM user_companies WHERE user_id = %s AND company_id = %s", (user_id, company_id))
            if not exists:
                return False
                
            sql = "DELETE FROM user_companies WHERE user_id = %s AND company_id = %s"
            self.db.execute_command(sql, (user_id, company_id), perform_commit=True, fetch_results=False)
            self._log_audit(None, 'UNLINK', 'USER_COMPANY', user_id, f"Usuario {user_id} desvinculado de empresa {company_id}")
            return True
        except Exception as e:
            logger.error(f"Error desvinculando usuario {user_id} de empresa {company_id}: {e}")
            raise

    def link_companies(self, source_id: int, target_id: int, relation_type_id: int, notes: str = None, is_inverse: bool = False) -> bool:
        """Crea una relación entre dos empresas."""
        try:
            # Handle Inverse Selection: Swap Source and Target
            s_id = target_id if is_inverse else source_id
            t_id = source_id if is_inverse else target_id
            
            # Check for existing link to avoid duplicates
            exists = self.db.fetch_one("SELECT 1 FROM company_relations WHERE source_company_id = %s AND target_company_id = %s", (s_id, t_id))
            if exists:
                return True # Already linked
                
            sql = """
                INSERT INTO company_relations (source_company_id, target_company_id, relation_type_id, notes)
                VALUES (%s, %s, %s, %s)
            """
            # Fix: Must set fetch_results=False to trigger commit logic in execute_query
            self.db.execute_command(sql, (s_id, t_id, relation_type_id, notes), perform_commit=True, fetch_results=False)
            
            self._log_audit(None, 'LINK', 'COMPANY_RELATION', s_id, f"Empresa {s_id} vinculada con {t_id} (Inverso: {is_inverse})")
            return True
        except Exception as e:
            logger.error(f"Error vinculando empresas {source_id} -> {target_id}: {e}")
            raise

    def update_company_relation(self, source_id: int, target_id: int, relation_type_id: int, notes: str = None, is_inverse: bool = False) -> bool:
        """Actualiza una relación existente entre dos empresas."""
        try:
            # Handle Inverse Selection: Swap Source and Target if needed
            # IMPORTANT: The primary key is (source, target), so we must ensure we are updating the CORRECT direction.
            # If the original link was A->B, and we want to update it to "Inverse", 
            # we might just be updating the TYPE ID on the A->B record, OR we might be logically swapping them.
            # For simplicity in this schema (single direction storage), we check if A->B exists.
            
            # 1. Check direct existence (Source -> Target)
            exists_direct = self.db.fetch_one("SELECT 1 FROM company_relations WHERE source_company_id = %s AND target_company_id = %s", (source_id, target_id))
            
            # 2. Check inverse existence (Target -> Source)
            exists_inverse = self.db.fetch_one("SELECT 1 FROM company_relations WHERE source_company_id = %s AND target_company_id = %s", (target_id, source_id))
            
            s_final, t_final = source_id, target_id
            
            if exists_direct:
                # We are updating the record A->B
                # If is_inverse is passed, it affects how we VIEW it, but here we just store the RelationTypeID and Notes.
                # However, if the user chose "Inverse" type, the UI sends the ID.
                # If the UI creates "A Linked to B" as "Deportista (Inverse)", it means "B is Deportista of A"? No.
                # It means "A is Deportista of B". So we store B->A.
                pass
            elif exists_inverse:
                s_final, t_final = target_id, source_id
            else:
                raise ValueError("No existe el vínculo para actualizar.")

            # If the user is CHANGING directions (e.g. was A->B, now wants B->A), that's a delete+insert.
            # But here we assume we just update the metadata (Type/Notes) of the EXISTING record found.
            
            # Wait, if is_inverse is True, the UI intends S->T to mean T->S.
            # If we update, we should respect that intention.
            # Complex Case: A->B exists (Provider). User edits to "Client (Inverse)".
            # Takes A, B. is_inverse=True. Target relation = Client. 
            # Logic: Client(Inverse) means A is Client of B. So B->A (Client).
            # But currently A->B (Provider) exists.
            # If we just update A->B to Client, A->B (Client). A is Client of B? No, A is Provider of B.
            # If A->B is Provider, A provides to B.
            # If A->B is Client, A is client of B. 
            # So just updating the Type ID is usually sufficient unless the Logical Direction flips.
            
            # Simplified Update: update criteria based on finding the record, update the fields.
            # We will NOT swap directions on update to avoid Primary Key collisions or complexity.
            # We strictly update Type and Notes.
            
            sql = "UPDATE company_relations SET relation_type_id = %s, notes = %s WHERE source_company_id = %s AND target_company_id = %s"
            self.db.execute_command(sql, (relation_type_id, notes, s_final, t_final), perform_commit=True, fetch_results=False)
            
            self._log_audit(None, 'UPDATE', 'COMPANY_RELATION', s_final, f"Vínculo actualizado {s_final}->{t_final}")
            return True
        except Exception as e:
            logger.error(f"Error actualizando vínculos {source_id} -> {target_id}: {e}")
            raise

    def unlink_companies(self, source_id: int, target_id: int) -> bool:
        """Elimina la relación entre dos empresas."""
        try:
            sql = "DELETE FROM company_relations WHERE source_company_id = %s AND target_company_id = %s"
            # Fix: fetch_results=False is required to trigger commit
            self.db.execute_command(sql, (source_id, target_id), perform_commit=True, fetch_results=False)
            self._log_audit(None, 'UNLINK', 'COMPANY_RELATION', source_id, f"Vínculo eliminado entre empresa {source_id} y {target_id}")
            return True
        except Exception as e:
            logger.error(f"Error desvinculando empresas {source_id} -> {target_id}: {e}")
            raise


    def create_user_relation_type(self, name: str, inverse_name: str, is_symmetric: bool = False) -> int:
        """Crea un nuevo par de tipos de relación (Bidireccional) o uno simétrico entre usuarios."""
        try:
            with self.db.start_transaction() as cursor:
                # 1. Crear Tipo A
                cursor.execute("INSERT INTO user_relation_types (name) VALUES (%s)", (name,))
                id_a = cursor.lastrowid
                
                if is_symmetric:
                     # Simétrico: Se apunta a sí mismo
                     cursor.execute("UPDATE user_relation_types SET inverse_type_id = %s WHERE id = %s", (id_a, id_a))
                     return id_a
                else:
                    # Asimétrico: Crear par inverso
                    cursor.execute("INSERT INTO user_relation_types (name, inverse_type_id) VALUES (%s, %s)", (inverse_name, id_a))
                    id_b = cursor.lastrowid
                    
                    # Actualizar Tipo A apuntando a B
                    cursor.execute("UPDATE user_relation_types SET inverse_type_id = %s WHERE id = %s", (id_b, id_a))
                    return id_a
        except Exception as e:
            logger.error(f"Error creando tipo de relación usuario {name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creando tipo de relación usuario {name}: {e}")
            raise

    def create_company_relation_type(self, name: str, inverse_name: str, is_symmetric: bool = False) -> int:
        """Crea un nuevo par de tipos de relación (Bidireccional) o uno simétrico entre empresas."""
        try:
            # Transacción manual para crear el par vinculado
            with self.db.start_transaction() as cursor:
                # 1. Crear Tipo A (Directo)
                cursor.execute("INSERT INTO company_relation_types (name) VALUES (%s)", (name,))
                id_a = cursor.lastrowid
                
                if is_symmetric:
                    # Simétrico: Se apunta a sí mismo
                    cursor.execute("UPDATE company_relation_types SET inverse_type_id = %s WHERE id = %s", (id_a, id_a))
                    self._log_audit(None, 'CREATE', 'CATALOG_COMPANY', id_a, f"Nuevo tipo simétrico creado: {name}")
                    return id_a
                else:
                    # Asimétrico: Crear par inverso
                    cursor.execute("INSERT INTO company_relation_types (name, inverse_type_id) VALUES (%s, %s)", (inverse_name, id_a))
                    id_b = cursor.lastrowid
                    
                    # 3. Actualizar Tipo A apuntando a B
                    cursor.execute("UPDATE company_relation_types SET inverse_type_id = %s WHERE id = %s", (id_b, id_a))
                    
                    self._log_audit(None, 'CREATE', 'CATALOG_COMPANY', id_a, f"Nuevo tipo de relación creado: {name} <-> {inverse_name}")
                    return id_a
        except Exception as e:
            logger.error(f"Error creando tipo de relación empresa {name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creando tipo de relación empresa {name}: {e}")
            raise

    def delete_company_relation_type(self, type_id: int) -> bool:
        """Elimina un tipo de relación corporativa y todos sus vínculos asociados."""
        try:
            # 1. Protected Types Check (Simple ID range for defaults)
            if type_id <= 5: 
                raise ValueError("No se pueden eliminar los tipos de relación protegidos del sistema (IDs 1-5).")

            # 2. Cascade Delete Links first
            # Get count for audit
            count_res = self.db.fetch_one("SELECT COUNT(*) as c FROM company_relations WHERE relation_type_id = %s", (type_id,))
            count = count_res['c'] if count_res else 0
            
            if count > 0:
                self.db.execute_command("DELETE FROM company_relations WHERE relation_type_id = %s", (type_id,), perform_commit=True, fetch_results=False)
            
            # 3. Delete Type
            self.db.execute_command("DELETE FROM company_relation_types WHERE id = %s", (type_id,), perform_commit=True, fetch_results=False)
            
            self._log_audit(None, 'DELETE', 'CATALOG_COMPANY', type_id, f"Tipo de relación {type_id} eliminado. {count} vínculos borrados en cascada.")
            return True
        except Exception as e:
            logger.error(f"Error eliminando tipo de relación empresa {type_id}: {e}")
            raise
    def get_economic_activities(self, query: str = None) -> List[Dict[str, Any]]:
        """Busca actividades económicas por código o descripción."""
        if query:
            sql = "SELECT isic_code as id, description FROM economic_activities WHERE isic_code LIKE %s OR description LIKE %s LIMIT 50"
            params = (f"%{query}%", f"%{query}%")
        else:
            sql = "SELECT isic_code as id, description FROM economic_activities LIMIT 50"
            params = ()
        
        return self.db.execute_query(sql, params)

    def parse_rut(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extrae datos procesables de un PDF del RUT."""
        return self.rut_parser.parse_rut(pdf_bytes)
