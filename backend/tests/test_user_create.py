
import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.models.models import User, Phone, Email

def test_user_create():
    load_dotenv()
    db = DatabaseManager()
    service = CRMService(db)
    
    print("\n" + "="*50)
    print(" [ID: 3.1] [TEST] USER CREATE ")
    print("="*50)
    
    try:
        print("\n--- CREACIÓN INTERACTIVA DE USUARIO ---")
        fn = input("Primer Nombre: ")
        ln = input("Primer Apellido: ")
        tid = input("RUT/NIT: ")
        email = input("Correo electrónico (Opcional, Enter para omitir): ")
        
        user = User(
            first_name=fn,
            last_name=ln,
            rut_nit=tid,
            status_id=1
        )
        
        emails = []
        if email:
            emails.append(Email(email_address=email, label_id=1))

        user_id = service.create_user_complete(user, emails=emails)
        print(f"\n✅ ÉXITO: Usuario creado con ID: {user_id}")
        
    except Exception as e:
        print(f" >>> Error during user creation: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_user_create()
