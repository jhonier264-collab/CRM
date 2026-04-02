"""
Encabezado Profesional: Servicio de Fachada de Autenticación
Propósito: Actúa como punto de entrada para todas las operaciones de seguridad, 
orquestando el núcleo de shared_auth con los repositorios locales.
Por qué: Mantener una interfaz limpia para el cliente (CLI/API) mientras se aplica DI.
"""

from typing import Dict, Any, Tuple
from ..lib.shared_auth.services import AuthCore
from ..repositories.auth_repository import AuthRepository
from ..lib.shared_auth.security import PasswordHasher
from ..core.database_interface import IDatabase
from .provisioning_service import ProvisioningService

class AuthService:
    def __init__(self, persistence: IDatabase):
        """
        Inyección de dependencia: Recibe el motor de persistencia global.
        Por qué: Permite que el servicio sea agnóstico a la DB y altamente testeable.
        """
        self.persistence = persistence
        self.repository = AuthRepository(persistence)
        self.auth_core = AuthCore(self.repository)
        self.provisioning_service = ProvisioningService(persistence)

    def login(self, identifier, password) -> Dict[str, Any]:
        """Autenticación agnóstica a través de la librería shared_auth."""
        return self.auth_core.authenticate(identifier, password)

    def request_recovery(self, identifier: str) -> Tuple[bool, str]:
        """Inicia el flujo de recuperación de contraseña."""
        return self.auth_core.request_password_recovery(identifier)

    def reset_password(self, identifier: str, token: str, new_password: str) -> Tuple[bool, str]:
        """Finaliza el flujo de recuperación reseteando la clave."""
        return self.auth_core.reset_password(identifier, token, new_password)

    def register_root_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registro de cliente raíz (SaaS).
        Valida los datos y ejecuta el aprovisionamiento de la instancia privada.
        """
        try:
            # Validación centralizada en AuthCore
            valid, msg = self.auth_core.validate_registration(user_data)
            if not valid:
                return {'success': False, 'message': msg}

            success = self.provisioning_service.create_tenant(user_data)
            if success:
                return {'success': True, 'message': 'Tenant y usuario creados exitosamente.'}
            else:
                return {'success': False, 'message': 'El aprovisionamiento falló.'}
        except ValueError as ve:
            return {'success': False, 'message': str(ve)}
        except Exception as e:
            return {'success': False, 'message': f"Error crítico: {str(e)}"}

    def register_staff_user(self, username, email, password, tenant_db):
        """Registra un miembro del staff en el directorio global."""
        hashed_pw = PasswordHasher.hash(password)
        data = {
            'username': username,
            'email': email,
            'password_hash': hashed_pw,
            'tenant_db': tenant_db,
            'account_type': 'INDIVIDUAL'
        }
        success, msg = self.repository.register_user(data)
        if success:
            return True, "Usuario de personal registrado globalmente."
        return False, msg
    def update_staff_user(self, old_username, new_username=None, password=None, email=None):
        """Actualiza las credenciales globales de un miembro de staff."""
        conn = self.db_manager.get_connection(db_name='master_db')
        cursor = conn.cursor()
        try:
            updates = []
            params = []
            if new_username:
                updates.append("username = %s")
                params.append(new_username)
            if password:
                hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                updates.append("password_hash = %s")
                params.append(hashed_pw)
            if email:
                updates.append("email = %s")
                params.append(email)
            
            if not updates: return True, "No hay cambios globales."
            
            sql = "UPDATE global_users SET " + ", ".join(updates) + " WHERE username = %s"
            params.append(old_username)
            cursor.execute(sql, params)
            conn.commit()
            return True, "Credenciales globales actualizadas exitosamente."
        except Exception as e:
            conn.rollback()
            logger.error(f"Error actualizando credenciales globales: {e}")
            return False, str(e)
        finally:
            cursor.close()
