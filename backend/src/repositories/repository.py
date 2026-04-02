# Importación de módulos para logueo, tipado y acceso a base de datos
import logging  # Registro de eventos y errores
from typing import List, Dict, Any, Optional, Type, TypeVar  # Soporte para tipado estático
from src.core.database_interface import IDatabase  # Interfaz de la base de datos
from src.models.models import User, Company, Address, Phone, Email  # Modelos de datos
from src.core.serializers import UserSerializer, CompanySerializer, AddressSerializer, PhoneSerializer, EmailSerializer # Serializadores para limpieza de datos

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

# Definición de un tipo genérico para métodos que puedan retornar distintos modelos
T = TypeVar('T')

class BaseRepository:
    """
    Clase base para todos los repositorios.
    Centraliza la instancia de la base de datos para todas las sub-clases.
    """
    def __init__(self, db: IDatabase):
        # Asignamos la instancia de BD inyectada
        self.db = db

class UserRepository(BaseRepository):
    """
    Repositorio especializado en la entidad Usuario.
    Maneja toda la interacción directa con la tabla 'users'.
    """

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca un usuario por su ID y retorna un diccionario JSON limpio.
        """
        # Sentencia SQL para buscar por llave primaria
        query = "SELECT * FROM users WHERE id = %s"
        # Ejecutamos la consulta
        res = self.db.execute_command(query, (user_id,))
        if res:
            # Convertimos el registro de BD a Modelo y luego lo serializamos como JSON limpio
            user_obj = User.from_dict(res[0])
            return UserSerializer.serialize(user_obj)
        return None

    def list(self) -> List[Dict[str, Any]]:
        """
        Lista todos los usuarios activos (que no han sido borrados de forma suave).
        Retorna una lista de diccionarios serializados.
        """
        # Filtramos por deleted_at IS NULL para respetar la papelera de reciclaje
        query = "SELECT * FROM users WHERE deleted_at IS NULL"
        res = self.db.execute_query(query)
        # Serializamos cada fila antes de retornarla
        return [UserSerializer.serialize(User.from_dict(row)) for row in res]

    def insert(self, user_data: Dict[str, Any]) -> int:
        """
        Inserta un nuevo usuario validando los datos de entrada previamente.
        Debe recibir un diccionario o un objeto User.
        """
        # Si recibimos un objeto, lo convertimos a diccionario para validar
        if isinstance(user_data, User):
            user_data = UserSerializer.serialize(user_data)
        
        # Validación de tipos básica (Input validation)
        if not isinstance(user_data.get('first_name'), str):
            raise TypeError("El campo 'first_name' debe ser una cadena de texto.")

        # Preparación de la consulta de inserción con todos los campos del modelo
        query = """
        INSERT INTO users (
            agent_id, role_id, status_id, prefix, first_name, middle_name, 
            last_name, username, password_hash, suffix, nickname,
            phonetic_first_name, phonetic_middle_name, phonetic_last_name,
            file_as, rut_nit, verification_digit, birthday, gender_id, notes,
            is_natural_person
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Mapeo manual de parámetros para asegurar limpieza
        params = (
            user_data.get('agent_id'), user_data.get('role_id'), user_data.get('status_id'), user_data.get('prefix'),
            user_data.get('first_name'), user_data.get('middle_name'), user_data.get('last_name'),
            user_data.get('username'), user_data.get('password_hash'), user_data.get('suffix'), user_data.get('nickname'),
            user_data.get('phonetic_first_name'), user_data.get('phonetic_middle_name'), user_data.get('phonetic_last_name'),
            user_data.get('file_as'), user_data.get('rut_nit'), user_data.get('verification_digit'), user_data.get('birthday'),
            user_data.get('gender_id'), user_data.get('notes'), 1 if user_data.get('is_natural_person') else 0
        )
        # Ejecutamos con perform_commit=True por ser una operación de escritura
        return self.db.execute_command(query, params, perform_commit=True, fetch_results=False)

    def update(self, user_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza datos de un usuario de forma dinámica.
        Valida que existan campos a actualizar.
        """
        if not data:
            return False
        
        # Limpieza de campos internos (Output filtering en el input para seguridad)
        data.pop('id', None)
        
        # Construcción dinámica de la cláusula SET
        fields = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE users SET {fields} WHERE id = %s"
        # Los parámetros son los valores del diccionario seguido del ID del usuario
        params = list(data.values()) + [user_id]
        return self.db.execute_command(query, params, perform_commit=True, fetch_results=False)

    def delete(self, user_id: int) -> bool:
        """
        Realiza un 'Soft Delete' marcando la fecha de eliminación.
        El registro permanece en la BD pero no se lista normalmente.
        """
        query = "UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s"
        return self.db.execute_command(query, (user_id,), perform_commit=True, fetch_results=False)

    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Busca un usuario por su nombre de usuario (usado principalmente en Login).
        """
        query = "SELECT * FROM users WHERE username = %s"
        res = self.db.execute_command(query, (username,))
        if res:
            return UserSerializer.serialize(User.from_dict(res[0]))
        return None

    def get_role(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene el rol asociado a un usuario específico mediante un Join.
        """
        query = """
        SELECT r.id, r.role_name 
        FROM roles r 
        JOIN users u ON u.role_id = r.id 
        WHERE u.id = %s
        """
        data = self.db.execute_command(query, (user_id,))
        return data[0] if data else None

class CompanyRepository(BaseRepository):
    """
    Repositorio para la entidad Empresa.
    Maneja la persistencia en la tabla 'companies'.
    """

    def get_by_id(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Busca una empresa por ID."""
        query = "SELECT * FROM companies WHERE id = %s"
        res = self.db.execute_command(query, (company_id,))
        if res:
            return CompanySerializer.serialize(Company.from_dict(res[0]))
        return None

    def list(self) -> List[Dict[str, Any]]:
        """Lista empresas activas."""
        query = "SELECT * FROM companies WHERE deleted_at IS NULL"
        res = self.db.execute_query(query)
        return [CompanySerializer.serialize(Company.from_dict(row)) for row in res]

    def insert(self, company_data: Dict[str, Any]) -> int:
        """Inserta una empresa con limpieza previa."""
        if isinstance(company_data, Company):
            company_data = CompanySerializer.serialize(company_data)

        query = """
        INSERT INTO companies (
            agent_id, status_id, rut_nit, verification_digit, legal_name,
            commercial_name, description, domain, revenue
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            company_data.get('agent_id'), company_data.get('status_id'), company_data.get('rut_nit'), company_data.get('verification_digit'),
            company_data.get('legal_name'), company_data.get('commercial_name'), company_data.get('description'),
            company_data.get('domain'), company_data.get('revenue')
        )
        return self.db.execute_query(query, params, commit=True, is_select=False)

    def update(self, company_id: int, data: Dict[str, Any]) -> bool:
        """Actualización dinámica de empresas."""
        if not data:
            return False
        fields = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE companies SET {fields} WHERE id = %s"
        params = list(data.values()) + [company_id]
        return self.db.execute_query(query, params, commit=True, is_select=False)

    def delete(self, company_id: int) -> bool:
        """Borrado suave de empresas."""
        query = "UPDATE companies SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s"
        return self.db.execute_command(query, (company_id,), perform_commit=True, fetch_results=False)

class ContactRepository(BaseRepository):
    """
    Repositorio unificado para Direcciones, Teléfonos y Correos.
    Permite centralizar el manejo de datos de contacto.
    """

    def insert_address(self, d: Address) -> int:
        """Inserta dirección validando tipos mediante el serializador."""
        data = AddressSerializer.serialize(d)
        query = """
        INSERT INTO addresses (
            user_id, company_id, country_id, state_id, city_id,
            address_line1, address_line2, postal_code
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data.get('user_id'), data.get('company_id'), data.get('country_id'), data.get('state_id'),
            data.get('city_id'), data.get('address_line1'), data.get('address_line2'), data.get('postal_code')
        )
        return self.db.execute_query(query, params, commit=True, is_select=False)

    def insert_phone(self, t: Phone) -> int:
        """Inserta teléfono con serialización."""
        data = PhoneSerializer.serialize(t)
        query = """
        INSERT INTO phones (user_id, company_id, country_id, local_number, label_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (data.get('user_id'), data.get('company_id'), data.get('country_id'), data.get('local_number'), data.get('label_id'))
        return self.db.execute_query(query, params, commit=True, is_select=False)

    def insert_email(self, e: Email) -> int:
        """Inserta email con serialización."""
        data = EmailSerializer.serialize(e)
        query = """
        INSERT INTO emails (user_id, company_id, email_address, label_id)
        VALUES (%s, %s, %s, %s)
        """
        params = (data.get('user_id'), data.get('company_id'), data.get('email_address'), data.get('label_id'))
        return self.db.execute_query(query, params, commit=True, is_select=False)

    def update_address(self, address_id: int, data: Dict[str, Any]) -> bool:
        """Actualiza dirección."""
        fields = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE addresses SET {fields} WHERE id = %s"
        return self.db.execute_command(query, list(data.values()) + [address_id], perform_commit=True, fetch_results=False)

    def update_phone(self, phone_id: int, data: Dict[str, Any]) -> bool:
        """Actualiza teléfono."""
        fields = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE phones SET {fields} WHERE id = %s"
        return self.db.execute_command(query, list(data.values()) + [phone_id], perform_commit=True, fetch_results=False)

    def update_email(self, email_id: int, data: Dict[str, Any]) -> bool:
        """Actualiza email."""
        fields = ", ".join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE emails SET {fields} WHERE id = %s"
        return self.db.execute_command(query, list(data.values()) + [email_id], perform_commit=True, fetch_results=False)

    def delete_contacts_by_user(self, user_id: int):
        """Elimina físicamente todos los contactos de un usuario."""
        queries = [
            "DELETE FROM phones WHERE user_id = %s",
            "DELETE FROM emails WHERE user_id = %s",
            "DELETE FROM addresses WHERE user_id = %s"
        ]
        for q in queries:
            self.db.execute_command(q, (user_id,), perform_commit=True, fetch_results=False)

    def delete_contacts_by_company(self, company_id: int):
        """Elimina físicamente todos los contactos de una empresa."""
        queries = [
            "DELETE FROM phones WHERE company_id = %s",
            "DELETE FROM emails WHERE company_id = %s",
            "DELETE FROM addresses WHERE company_id = %s"
        ]
        for q in queries:
            self.db.execute_command(q, (company_id,), perform_commit=True, fetch_results=False)
