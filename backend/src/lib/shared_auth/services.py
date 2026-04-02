from typing import Dict, Any, Optional, Tuple
import datetime
from .interfaces import IAuthRepository
from .security import PasswordHasher, SessionManager, validar_rut_colombia
from .recovery_provider import RecoveryProvider

class AuthCore:
    def __init__(self, repository: IAuthRepository):
        self.repository = repository
        self.max_attempts = 5
        self.lockout_minutes = 15

    def authenticate(self, identifier: str, password: str) -> Dict[str, Any]:
        """
        Authenticates a user by username or email.
        Handles lockout logic and returns a session token on success.
        """
        user = self.repository.get_user_by_identifier(identifier)
        if not user:
            return {'authenticated': False, 'error': 'Usuario no encontrado.'}

        # Check Lockout
        if user.get('locked_until'):
            locked_until = user['locked_until']
            if isinstance(locked_until, str):
                locked_until = datetime.datetime.fromisoformat(locked_until)
            
            if datetime.datetime.utcnow() < locked_until:
                return {
                    'authenticated': False, 
                    'error': f"Cuenta bloqueada temporalmente. Intente de nuevo después de {locked_until.strftime('%H:%M:%S')}."
                }

        # Verify Password
        if PasswordHasher.verify(password, user['password_hash']):
            # Success: Reset attempts
            self.repository.update_lockout(user['id'], 0, None)
            
            token = SessionManager.generate_token(user['id'], user['username'], tenant_db=user.get('tenant_db'))
            return {
                'authenticated': True,
                'token': token,
                'user_id': user['id'],
                'username': user['username'],
                'tenant_db': user.get('tenant_db')
            }
        else:
            # Failure: Increment attempts
            attempts = user.get('failed_attempts', 0) + 1
            locked_until = None
            
            if attempts >= self.max_attempts:
                locked_until = (datetime.datetime.utcnow() + datetime.timedelta(minutes=self.lockout_minutes)).isoformat()
                error_msg = f"Demasiados intentos fallidos. Cuenta bloqueada por {self.lockout_minutes} minutos."
            else:
                error_msg = f"Contraseña incorrecta. Intentos restantes: {self.max_attempts - attempts}."
            
            self.repository.update_lockout(user['id'], attempts, locked_until)
            return {'authenticated': False, 'error': error_msg}

    def request_password_recovery(self, identifier: str) -> Tuple[bool, str]:
        """Initiates the recovery process."""
        user = self.repository.get_user_by_identifier(identifier)
        if not user:
            return False, "Usuario no encontrado."

        token = RecoveryProvider.generate_token()
        expiry = RecoveryProvider.get_expiry_time().isoformat()
        
        self.repository.save_recovery_token(user['id'], token, expiry)
        
        # Enviar el correo usando SMTP
        email_to = user.get('email')
        if not email_to:
            return False, "El usuario no tiene un correo configurado para recibir la recuperación."
            
        from src.services.email_service import EmailService
        success = EmailService.send_recovery_email(email_to, token)
        
        if success:
            return True, "Código de recuperación enviado a su correo (Válido por 10 min)."
        else:
            return False, "No se pudo enviar el correo de recuperación. Verifique la configuración del servidor."

    def reset_password(self, identifier: str, token: str, new_password: str) -> Tuple[bool, str]:
        """Validates the recovery token and resets the password."""
        recovery_data = self.repository.get_recovery_token(identifier)
        if not recovery_data:
            return False, "No hay una solicitud de recuperación activa."

        if recovery_data['token'] != token:
            return False, "Código de recuperación inválido."

        expiry = recovery_data['expires_at']
        if isinstance(expiry, str):
            expiry = datetime.datetime.fromisoformat(expiry)
            
        if RecoveryProvider.is_expired(expiry):
            return False, "El código ha expirado. Solicite uno nuevo."

        # Reset Password
        hashed_pw = PasswordHasher.hash(new_password)
        success = self.repository.reset_password(recovery_data['user_id'], hashed_pw)
        
        if success:
            return True, "Contraseña actualizada exitosamente."
        return False, "Error al actualizar la contraseña."

    def validate_registration(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Common validations for registration."""
        if data.get('password') != data.get('password_confirm'):
            return False, "Las contraseñas no coinciden."
        
        if data.get('account_type') == 'COMPANY':
            rut = data.get('rut')
            if not rut or not validar_rut_colombia(rut):
                return False, "El RUT/NIT ingresado es inválido."
        
        return True, "Validación exitosa."

    def create_global_user(self, user_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Creates a new user in the global master_db.
        Handles password hashing.
        """
        # Hash password if provided in plain text
        if 'password' in user_data and 'password_hash' not in user_data:
            user_data['password_hash'] = PasswordHasher.hash(user_data['password'])
        
        return self.repository.register_user(user_data)

    def update_password(self, user_id: int, new_password: str) -> bool:
        """
        Directly updates a user's password (for logged-in profile updates).
        """
        hashed_pw = PasswordHasher.hash(new_password)
        # We reuse success/fail from repository
        return self.repository.reset_password(user_id, hashed_pw)

    def sync_global_user(self, global_user_id: int, data: Dict[str, Any]) -> bool:
        """
        Syncs profile data (email, rut, etc.) from Tenant to Master DB.
        """
        # Whitelist allowed fields to prevent arbitrary updates
        allowed = {'username', 'email', 'rut', 'is_active'}
        updates = {k: v for k, v in data.items() if k in allowed and v is not None}
        
        if not updates:
            return False
            
        return self.repository.update_user(global_user_id, updates)

    def revoke_access(self, global_user_id: int) -> bool:
        """
        Disables global login for a user (used when role is downgraded).
        """
        return self.repository.set_user_active_status(global_user_id, False)
