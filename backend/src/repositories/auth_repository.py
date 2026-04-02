"""
Encabezado Profesional: Repositorio de Autenticación
Propósito: Gestiona la persistencia de datos relacionados con la seguridad y el directorio global.
Por qué: Seguir Clean Architecture desacoplando la lógica de negocio de la infraestructura.
"""

from typing import Optional, Dict, Any, Tuple
from ..lib.shared_auth.interfaces import IAuthRepository
from ..core.database_interface import IDatabase

class AuthRepository(IAuthRepository):
    def __init__(self, persistence: IDatabase):
        """
        Inyección de dependencia: Recibe cualquier motor de persistencia que cumpla con IDatabase.
        """
        self.persistence = persistence

    def get_user_by_identifier(self, identifier: str) -> Optional[Dict[str, Any]]:
        command = """
            SELECT id, username, email, password_hash, tenant_db, failed_attempts, locked_until 
            FROM global_users 
            WHERE (username = %s OR email = %s) AND is_active = TRUE
        """
        results = self.persistence.execute_command(command, (identifier, identifier))
        return results[0] if results else None

    def update_lockout(self, user_id: int, attempts: int, locked_until: Optional[str] = None) -> None:
        command = "UPDATE global_users SET failed_attempts = %s, locked_until = %s WHERE id = %s"
        self.persistence.execute_command(command, (attempts, locked_until, user_id), perform_commit=True, fetch_results=False)

    def get_recovery_token(self, identifier: str) -> Optional[Dict[str, Any]]:
        command = """
            SELECT rt.user_id, rt.token, rt.expires_at 
            FROM recovery_tokens rt
            JOIN global_users gu ON rt.user_id = gu.id
            WHERE (gu.username = %s OR gu.email = %s) AND rt.used = FALSE
            ORDER BY rt.created_at DESC LIMIT 1
        """
        results = self.persistence.execute_command(command, (identifier, identifier))
        return results[0] if results else None

    def save_recovery_token(self, user_id: int, token: str, expires_at: str) -> None:
        command = "INSERT INTO recovery_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)"
        self.persistence.execute_command(command, (user_id, token, expires_at), perform_commit=True, fetch_results=False)

    def reset_password(self, user_id: int, new_password_hash: str) -> bool:
        # Usamos una transacción para asegurar que la actualización de clave y la anulación de tokens sean atómicas.
        with self.persistence.start_transaction() as cursor:
            try:
                # Reset password and clear lockout
                command_update = """
                    UPDATE global_users 
                    SET password_hash = %s, failed_attempts = 0, locked_until = NULL 
                    WHERE id = %s
                """
                cursor.execute(command_update, (new_password_hash, user_id))
                
                # Mark tokens as used
                cursor.execute("UPDATE recovery_tokens SET used = TRUE WHERE user_id = %s", (user_id,))
                return True
            except Exception:
                # El contextmanager realizará el rollback automáticamente si hay excepción
                return False

    def register_user(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        command = """
            INSERT INTO global_users (username, email, password_hash, tenant_db, account_type, rut)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            user_id = self.persistence.execute_command(
                command, 
                (
                    user_data['username'], 
                    user_data['email'], 
                    user_data['password_hash'], 
                    user_data.get('tenant_db'),
                    user_data.get('account_type', 'INDIVIDUAL'),
                    user_data.get('rut')
                ),
                perform_commit=True,
                fetch_results=False
            )
            return True, str(user_id)
        except Exception as e:
            return False, str(e)

    def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        if not updates:
            return False
        fields = ", ".join([f"{k} = %s" for k in updates.keys()])
        command = f"UPDATE global_users SET {fields} WHERE id = %s"
        params = list(updates.values()) + [user_id]
        try:
            self.persistence.execute_command(command, params, perform_commit=True, fetch_results=False)
            return True
        except Exception as e:
            print(f"Error updating global user {user_id}: {e}")
            return False

    def set_user_active_status(self, user_id: int, is_active: bool) -> bool:
        command = "UPDATE global_users SET is_active = %s WHERE id = %s"
        try:
            self.persistence.execute_command(command, (is_active, user_id), perform_commit=True, fetch_results=False)
            return True
        except Exception as e:
            print(f"Error setting active status for global user {user_id}: {e}")
            return False
