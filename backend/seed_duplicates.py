
import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.database_manager import DatabaseManager
from src.services.services import CRMService
from src.models.models import User, Phone, Email

def seed_duplicates():
    load_dotenv()
    db = DatabaseManager()
    service = CRMService(db)
    
    print("\n" + "="*50)
    print(" [SEED] CREANDO ESCENARIOS DE DUPLICADOS ")
    print("="*50)
    
    try:
        # ESCENARIO ÚNICO: Duplicado por TELÉFONO (Formatos diferentes para probar Inteligencia)
        print("\n1. Creando par duplicado por TELÉFONO (Formato variable)...")
        
        # Usuario A: Elena Rivas (Formato limpio)
        u1 = User(first_name="Elena", last_name="Rivas", rut_nit="TEST-789", status_id=1, is_natural_person=True)
        p1 = [Phone(local_number="3009998877", country_id=1, label_id=1)]
        uid1 = service.create_user_complete(u1, phones=p1)
        
        # Usuario B: E. Rivas (Formato con ruidos e indicativos)
        # Nivel de inteligencia: El motor debe normalizar "+57 300-999-8877" a "3009998877"
        u2 = User(first_name="E. María", last_name="Rivas", rut_nit="TEST-000", status_id=1, is_natural_person=True)
        p2 = [Phone(local_number="+57 300-999-8877", country_id=1, label_id=1)]
        uid2 = service.create_user_complete(u2, phones=p2)
        
        print(f"   ✅ Usuario 1 creado (ID: {uid1})")
        print(f"   ✅ Usuario 2 creado (ID: {uid2})")
        print("\n🚀 LISTO. Los datos han burlado el UNIQUE KEY de la DB por formato,")
        print("   pero el motor 'Combinar y Corregir' los detectará como el mismo teléfono.")

        print("\n🚀 LISTO. Ahora vaya a la CLI y use 'Combinar y Corregir'.")

    except Exception as e:
        print(f"\n 🔴 ERROR AL SEEDER: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_duplicates()
