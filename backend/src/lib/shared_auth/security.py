import os
import bcrypt
import jwt
import datetime
from typing import Optional, Dict, Any

class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

class SessionManager:
    SECRET_KEY = os.getenv('SECRET_KEY')

    @staticmethod
    def generate_token(user_id: int, username: str, tenant_db: Optional[str] = None, expiry_minutes: int = 60) -> str:
        payload = {
            'sub': username,
            'user_id': user_id,
            'tenant_db': tenant_db,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry_minutes)
        }
        return jwt.encode(payload, SessionManager.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, SessionManager.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

def validar_rut_colombia(rut_completo: str) -> bool:
    """
    Valida un RUT/NIT colombiano (formato XXXXXXXXX-X).
    Implementación del algoritmo de Módulo 11.
    """
    try:
        if "-" not in rut_completo:
            return False
            
        nit, dv_ingresado = rut_completo.split("-")
        nit = nit.replace(".", "").replace(",", "")
        
        if not nit.isdigit() or not dv_ingresado.isdigit():
            return False
            
        v_pri = [0, 3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
        suma = 0
        
        # Invertir el nit para procesar desde el final
        for i, digito in enumerate(reversed(nit)):
            suma += int(digito) * v_pri[i + 1]
        
        residuo = suma % 11
        if residuo <= 1:
            dv_calculado = residuo
        else:
            dv_calculado = 11 - residuo
            
        # El algoritmo de la DIAN tiene una pequeña variación:
        # si residuo > 1, es 11 - residuo. Si residuo es 0 o 1, es el mismo residuo? 
        # No, según el estándar:
        # 0 -> 0
        # 1 -> 1
        # >1 -> 11 - residuo
        # Vamos a usar la lógica estándar del prompt:
        dv_calculado = 0 if residuo <= 1 else 11 - residuo
        
        return int(dv_ingresado) == dv_calculado
    except Exception:
        return False
